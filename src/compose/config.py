# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


import datetime
import re
from functools import cached_property
from typing import Annotated, Optional

from license import License, SpdxLicenseList
from loader import Loader
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
    topics: Optional[AnnotatedStrList] = None
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
        try:
            return re.search('^## (.+)', md).group(1)
        except (re.error, TypeError, IndexError) as title_error:
            raise ValueError('Failed to parse title:\n{0}'.format(title_error))

    @classmethod
    @validate_call
    def _parse_date(cls, md: str) -> datetime.date:
        try:
            date = re.search(r'\d{4}-\d{2}-\d{2}', md, re.MULTILINE).group()
        except (re.error, TypeError, IndexError, AttributeError) as error:
            raise ValueError('Failed to fetch date:\n{0}'.format(error))
        return datetime.date.fromisoformat(date)

    @classmethod
    @validate_call
    def _parse_images(cls, md: str) -> list[str]:
        try:
            return re.findall(r'!\[.*?\]\((.*?)\)', md)
        except re.error as error:
            raise ValueError('Failed to parse images:\n{0}'.format(error))

    @classmethod
    @validate_call
    def _parse_description(cls, md: str) -> str:
        exp = r'\d{4}-\d{2}-\d{2}.*?\n(.*)'
        try:
            description = re.search(exp, md, re.DOTALL).group(1)
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

    id: AnnotatedStr
    repository: SerializableUrl
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None
    parents: Optional[AnnotatedStrList] = None
    compatibles: Optional[AnnotatedStrList] = None

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
            return Manifest.from_url(self.repository)
        except (ValidationError, ValueError) as manifest_error:
            raise ValueError("Failed to load manifest from '{0}':\n{1}".format(
                self.repository, manifest_error,
            ))

    @cached_property
    def description(self) -> str:
        """
        Get description.

        Returns:
            str: description string.

        Raises:
            ValueError: If loading the description fails.
        """
        try:
            md = Loader.from_url(str(self.manifest.description)).load()
        except ValueError as load_error:
            raise ValueError('Failed to load {0}:\n{1}'.format(
                str(self.manifest.description), load_error,
            ))
        try:
            sections = re.split('(^#.*$)', md, flags=re.MULTILINE)
        except (re.error, TypeError) as split_error:
            raise ValueError('Failed to split sections:\n{0}'.format(
                split_error,
            ))
        for section in sections:
            md = re.sub('<!--(.*?)-->', '', section, flags=re.DOTALL).strip()
            md = re.sub(r'^\s*-{3,}\s*$', '', md, flags=re.MULTILINE).strip()
            md = re.sub(r'!\[.*?\]\(.*?\)', '', md, flags=re.DOTALL)
            if not md.startswith('#') and md:
                return md
        raise ValueError('Failed to parse the Markdown description.')

    @computed_field
    @cached_property
    def summary(self) -> str:
        """
        Get summary.

        Returns:
            str: summary string.

        Raises:
            ValueError: If parsing the summary from the description fails.
        """
        exp = r'^.*?(?=\.\s|\.\r?\n|:\r?\n|\r?\n\r?\n|\.$|$)'
        match = re.search(exp, self.description, re.DOTALL)
        if match:
            return match.group()
        raise ValueError('Failed to parse the summary from the description.')

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
        if self.manifest.licenses:
            licenses = []
            for license_id in self.manifest.licenses:
                try:
                    licenses.append(SpdxLicenseList.get_license(license_id))
                except (ValidationError, ValueError) as license_error:
                    raise ValueError('Failed to load licenses:\n{0}'.format(
                        license_error,
                    ))
            return licenses

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
            md = Loader.from_url(str(self.manifest.newsfeed)).load()
        except ValueError as load_error:
            raise ValueError('Failed to load {0}:\n{1}'.format(
                str(self.manifest.newsfeed), load_error,
            ))
        try:
            matches = re.findall(r'(## .+?)(?=\n## |$)', md, re.DOTALL)
        except (re.error, TypeError) as re_error:
            raise ValueError('Failed to process Markdown:\n{0}'.format(
                re_error,
            ))
        news_list = []
        for match in matches:
            try:
                news = News.from_markdown(match)
            except (ValidationError, ValueError) as news_error:
                raise ValueError('Failed to load news:\n{0}'.format(
                    news_error,
                ))
            news.topics = [self.id]
            news_list.insert(0, news)
        return news_list


class Redirect(BaseModelForbidExtra):
    """Redirect configuration."""

    source: AnnotatedStr = Field(exclude=True)
    target: SerializableUrl


class Config(Schema):
    """Configuration schema."""

    sources: DirectoryPath
    licenses: FilePath
    redirects: Annotated[list[Redirect], Field(min_length=1)]
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
                            project.id, unknown,
                        ),
                    )
        return self

    @model_validator(mode='after')
    def check_parents_match(self) -> 'Config':
        """
        Check if parents in projects match the available projects.

        Returns:
            Config: The configuration object with validated parents.

        Raises:
            ValueError: If an unknown parent is found in a project.
        """
        parent_ids = []
        for parent in self.projects:
            parent_ids.append(parent.id)

        for child in self.projects:
            if child.parents:
                unknown = set(child.parents) - set(parent_ids)
                if unknown:
                    raise ValueError(
                        "Project '{0}' with unknown parents: '{1}'.".format(
                            child.id, unknown,
                        ),
                    )
        return self

    @model_validator(mode='after')
    def check_compatibles_match(self) -> 'Config':
        """
        Check if compatibles in projects match the available projects.

        Returns:
            Config: The configuration object with validated compatibles.

        Raises:
            ValueError: If an unknown compatible is found in a project.
        """
        compatible_ids = []
        for compatible in self.projects:
            compatible_ids.append(compatible.id)

        for project in self.projects:
            if project.compatibles:
                unknown = set(project.compatibles) - set(compatible_ids)
                if unknown:
                    raise ValueError(
                        (
                            "Project '{0}' with unknown compatibles: '{1}'."
                        ).format(project.id, unknown),
                    )
        return self
