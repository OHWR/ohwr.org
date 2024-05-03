# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import datetime
import logging
import re
from collections import UserList
from urllib import request
from urllib.error import URLError

import yaml
from common import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    ReachableUrlList,
)
from pydantic import (
    HttpUrl,
    NewPath,
    TypeAdapter,
    ValidationError,
    computed_field,
    validate_call,
)


class News(BaseModelForbidExtra):
    """Project news."""

    md: AnnotatedStr
    newsfeed: AnnotatedStrList

    @computed_field
    def title(self) -> str:
        """
        Get title from Markdown.

        Returns:
            str: title.

        Raises:
            ValueError: If the title cannot be parsed from the Markdown.
        """
        try:
            return re.search('^## (.+)', self.md).group(1).strip()
        except (re.error, TypeError, IndexError) as title_error:
            raise ValueError('Failed to parse title:\n{0}'.format(title_error))

    @computed_field
    def date(self) -> datetime.date:
        """
        Get date from Markdown.

        Returns:
            datetime.date: date.

        Raises:
            ValueError: If the date cannot be parsed from the Markdown.
        """
        try:
            date = re.search(
                r'^\d{4}-\d{2}-\d{2}', self.md, re.MULTILINE,
            ).group(0)
        except (re.error, TypeError, IndexError) as error:
            raise ValueError('Failed to fetch date:\n{0}'.format(error))
        return datetime.date.fromisoformat(date)

    @computed_field
    def images(self) -> list[str]:
        """
        Get images from Markdown.

        Returns:
            list[str]: images.

        Raises:
            ValueError: If the images cannot be parsed from the Markdown.
        """
        try:
            images = re.findall(r'!\[.*?\]\((.*?)\)', self.md)
        except re.error as error:
            raise ValueError('Failed to parse images:\n{0}'.format(error))
        if images:
            ta = TypeAdapter(ReachableUrlList)
            try:
                ta.validate_python(images)
            except ValidationError as url_error:
                raise ValueError('Failed to validate images:\n{0}'.format(
                    url_error,
                ))
            return images

    @computed_field
    def description(self) -> str:
        """
        Get description from Markdown.

        Returns:
            str: description.

        Raises:
            ValueError: If the description cannot be parsed from the Markdown.
        """
        try:
            description = re.search(
                r'\d{4}-\d{2}-\d{2}(.*)', self.md, re.DOTALL,
            ).group(1)
        except (re.error, TypeError, IndexError) as description_error:
            raise ValueError('Failed to parse description:\n{0}'.format(
                description_error,
            ))
        try:
            description = re.sub(
                r'!\[.*?\]\(.*?\)', '', description, flags=re.DOTALL,
            )
        except (re.error, TypeError) as cleanup_error:
            raise ValueError('Failed to cleanup description:\n{0}'.format(
                cleanup_error,
            ))
        return description.strip()

    @validate_call
    def hugo(self) -> str:
        """
        Generate Hugo content.

        Returns:
            str: Hugo content string.

        Raises:
            ValueError: If generating the Hugo content fails.
        """
        try:
            front_matter = yaml.safe_dump(self.model_dump(
                exclude_none=True, exclude={'md', 'description'},
            ))
        except yaml.YAMLError as yaml_error:
            raise ValueError('Failed to dump YAML front matter:\n{0}'.format(
                yaml_error,
            ))
        return '---\n{0}---\n{1}'.format(front_matter, self.description)

    @validate_call
    def dump(self, path: NewPath):
        """
        Dump Hugo content.

        Parameters:
            path: Hugo content file path for news.

        Raises:
            ValueError: if dumping the Hugo content fails.
        """
        logging.info("{0} - Writing news page to '{1}'...".format(
            self.newsfeed[0], path,
        ))
        hugo_content = self.hugo()
        try:
            with open(path, 'w') as news_file:
                news_file.write(hugo_content)
        except OSError as error:
            raise ValueError("Failed to write file '{0}':\n{1}".format(
                path, error,
            ))


class Newsfeed(UserList):
    """Project newsfeed."""

    @classmethod
    def from_url(cls, url: HttpUrl, project: str):
        """
        Load newsfeed from a URL.

        Parameters:
            url: Newsfeed URL.
            project: project identifier string.

        Returns:
            Newsfeed object.

        Raises:
            ValueError: if loading the newsfeed fails.
        """
        try:
            with request.urlopen(str(url), timeout=5) as res:  # noqa: S310
                return cls.from_md(res.read().decode('utf-8'), project)
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError("Failed to load newsfeed from '{0}':\n{1}".format(
                url, urlopen_error,
            ))

    @classmethod
    def from_md(cls, md: str, project: str):
        """
        Get news from the Markdown.

        Parameters:
            md: Newsfeed Markdown string.
            project: project identifier string.

        Returns:
            Newsfeed object.

        Raises:
            ValueError: If the news cannot be parsed from the Markdown.
        """
        try:
            matches = re.findall(r'(## .+?)(?=\n## |$)', md, re.DOTALL)
        except (re.error, TypeError) as re_error:
            raise ValueError('Failed to process Markdown:\n{0}'.format(
                re_error,
            ))
        newsfeed = []
        for match in matches:
            try:
                newsfeed.append(News(md=match, newsfeed=[project]))
            except (ValidationError, ValueError) as news_error:
                raise ValueError('Failed to load news:\n{0}'.format(
                    news_error,
                ))
        return cls(newsfeed)
