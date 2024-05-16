# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


import datetime
import re
from functools import cached_property
from typing import Annotated, Optional
from urllib import request
from urllib.error import URLError

from license import License, SpdxLicenseList
from manifest import Manifest
from pydantic import (
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    ValidationError,
    computed_field,
    model_validator,
    validate_call,
)
from schema import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    ReachableUrlList,
    Schema,
    SerializableUrl,
)


class Category(BaseModelForbidExtra):
    """Project category."""

    name: AnnotatedStr
    description: AnnotatedStr


class Contact(BaseModelForbidExtra):
    """Contact configuration."""

    name: AnnotatedStr
    email: EmailStr


class News(BaseModelForbidExtra):
    """News configuration."""

    title: AnnotatedStr
    date: datetime.date
    images: Optional[ReachableUrlList] = None
    description: Optional[AnnotatedStr] = Field(default=None, exclude=True)

    @classmethod
    @validate_call
    def from_markdown(cls, md: AnnotatedStr):
        """
        Load news from a markdown string.

        Parameters:
            md: The markdown content to parse.

        Returns:
            News: An instance of the News class.
        """
        news_data = {
            'title': cls._parse_title(md), 'date': cls._parse_date(md),
        }
        images = cls._parse_images(md)
        if images:
            news_data['images'] = images
        description = cls._parse_description(md)
        if description:
            news_data['description'] = description
        return cls(**news_data)

    @classmethod
    @validate_call
    def _parse_title(cls, md: str) -> str:
        """
        Get title from Markdown.

        Parameters:
            md: The markdown content.

        Returns:
            str: title.

        Raises:
            ValueError: If the title cannot be parsed from the Markdown.
        """
        try:
            return re.search('^## (.+)', md).group(1)
        except (re.error, TypeError, IndexError) as title_error:
            raise ValueError('Failed to parse title:\n{0}'.format(title_error))

    @classmethod
    @validate_call
    def _parse_date(cls, md: str) -> datetime.date:
        """
        Get date from Markdown.

        Parameters:
            md: The markdown content.

        Returns:
            datetime.date: date.

        Raises:
            ValueError: If the date cannot be parsed from the Markdown.
        """
        try:
            date = re.search(
                r'^\d{4}-\d{2}-\d{2}', md, re.MULTILINE,
            ).group(0)
        except (re.error, TypeError, IndexError) as error:
            raise ValueError('Failed to fetch date:\n{0}'.format(error))
        return datetime.date.fromisoformat(date)

    @classmethod
    @validate_call
    def _parse_images(cls, md: str) -> list[str]:
        """
        Get images from Markdown.

        Parameters:
            md: The markdown content.

        Returns:
            list[str]: images.

        Raises:
            ValueError: If the images cannot be parsed from the Markdown.
        """
        try:
            return re.findall(r'!\[.*?\]\((.*?)\)', md)
        except re.error as error:
            raise ValueError('Failed to parse images:\n{0}'.format(error))

    @classmethod
    @validate_call
    def _parse_description(cls, md: str) -> str:
        """
        Get description from Markdown.

        Parameters:
            md: The markdown content.

        Returns:
            str: description.

        Raises:
            ValueError: If the description cannot be parsed from the Markdown.
        """
        try:
            description = re.search(
                r'\d{4}-\d{2}-\d{2}(.*)', md, re.DOTALL,
            ).group(1)
        except (re.error, TypeError, IndexError) as description_error:
            raise ValueError('Failed to parse description:\n{0}'.format(
                description_error,
            ))
        try:
            return re.sub(r'!\[.*?\]\(.*?\)', '', description, flags=re.DOTALL)
        except (re.error, TypeError) as cleanup_error:
            raise ValueError('Failed to cleanup description:\n{0}'.format(
                cleanup_error,
            ))


class Project(BaseModelForbidExtra):
    """Project configuration."""

    repository: SerializableUrl
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None

    @computed_field
    @cached_property
    def id(self) -> str:
        """
        Get id.

        Returns:
            str: identifier string.
        """
        split = str(self.repository).split('/')
        return split[-1].replace('.git', '')

    @computed_field
    @cached_property
    def manifest(self) -> Manifest:
        """
        Get manifest.

        Returns:
            Manifest: project manifest.

        Raises:
            ValueError: If loading the manifest fails.
        """
        try:
            return Manifest.from_repository(self.repository)
        except (ValidationError, ValueError) as manifest_error:
            raise ValueError("Failed to load manifest from '{0}':\n{1}".format(
                self.repository, manifest_error,
            ))

    @computed_field
    @cached_property
    def description(self) -> str:
        """
        Get description.

        Returns:
            str: description string.

        Raises:
            ValueError: If loading the description fails.
        """
        url = str(self.manifest.description)
        try:
            with request.urlopen(url, timeout=5) as res:  # noqa: S310
                md = res.read().decode('utf-8')
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError(
                "Failed to load description from '{0}':\n{1}".format(
                    url, urlopen_error,
                ),
            )
        try:
            sections = re.split('(^#.*$)', md, flags=re.MULTILINE)
        except (re.error, TypeError) as split_error:
            raise ValueError('Failed to split sections:\n{0}'.format(
                split_error,
            ))
        for section in sections:
            md = re.sub('<!--(.*?)-->', '', section, flags=re.DOTALL).strip()
            if not md.startswith('#') and md:
                return md
        raise ValueError('Failed to parse Markdown description.')

    @computed_field
    @cached_property
    def licenses(self) -> list[License]:
        """
        Get licenses.

        Returns:
            list[License]: license list.

        Raises:
            ValueError: If loading the licenses fails.
        """
        licenses = []
        for license_id in self.manifest.licenses:
            try:
                licenses.append(SpdxLicenseList.get_license(license_id))
            except (ValidationError, ValueError) as license_error:
                raise ValueError('Failed to load licenses:\n{0}'.format(
                    license_error,
                ))
        return licenses

    @computed_field
    @cached_property
    def news(self) -> list[News]:
        """
        Get news.

        Returns:
            list[News]: news list.

        Raises:
            ValueError: If loading the news fails.
        """
        if not self.manifest.newsfeed:
            return []
        try:
            with request.urlopen(  # noqa: S310
                str(self.manifest.newsfeed), timeout=5,
            ) as res:
                md = res.read().decode('utf-8')
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError("Failed to load newsfeed from '{0}':\n{1}".format(
                str(self.manifest.newsfeed), urlopen_error,
            ))
        try:
            matches = re.findall(r'(## .+?)(?=\n## |$)', md, re.DOTALL)
        except (re.error, TypeError) as re_error:
            raise ValueError('Failed to process Markdown:\n{0}'.format(
                re_error,
            ))
        news = []
        for match in matches:
            try:
                news.append(News.from_markdown(match))
            except (ValidationError, ValueError) as news_error:
                raise ValueError('Failed to load news:\n{0}'.format(
                    news_error,
                ))
        return news


class Config(Schema):
    """Configuration schema."""

    sources: DirectoryPath
    licenses: FilePath
    categories: Annotated[list[Category], Field(min_length=1)]
    projects: Annotated[list[Project], Field(min_length=1)]

    @model_validator(mode='after')
    def check_categories_match(self) -> 'Config':
        """
        Check if categories in projects match the available categories.

        Returns:
            Config: The configuration object with validated category names.

        Raises:
            ValueError: If an unknown category is found in a project.
        """
        categories = []
        for category in self.categories:
            categories.append(category.name)

        for project in self.projects:
            if project.categories:
                unknown = set(project.categories) - set(categories)
                if unknown:
                    raise ValueError(
                        "Project '{0}' with unknown categories: '{1}'.".format(
                            project.repository, unknown,
                        ),
                    )
        return self
