# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Project utilities."""


import logging
import re
from functools import cached_property
from typing import Optional
from urllib import request
from urllib.error import URLError

import yaml
from common import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    SerializableUrl,
)
from license import License, SpdxLicenseList
from manifest import Manifest
from pydantic import (
    EmailStr,
    NewPath,
    ValidationError,
    computed_field,
    validate_call,
)
from repository import Repository


class Contact(BaseModelForbidExtra):
    """Contact configuration schema."""

    name: AnnotatedStr
    email: EmailStr


class Project(BaseModelForbidExtra):
    """Project configuration schema."""

    repository: SerializableUrl
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None

    @computed_field
    @cached_property
    def id(self) -> str:
        """
        Get project identifier.

        Returns:
            str: project identifier.

        Raises:
            ValueError: If defining the project identifier fails.
        """
        try:
            return Repository.create(self.repository).project
        except (ValidationError, ValueError) as repository_error:
            raise ValueError(
                "Failed to define project id from '{0}':\n{1}".format(
                    self.repository, repository_error,
                ),
            )

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
            repository = Repository.create(self.repository)
        except (ValidationError, ValueError) as repository_error:
            raise ValueError(
                "Failed to load repository from '{0}':\n{1}".format(
                    self.repository, repository_error,
                ),
            )
        try:
            return Manifest.from_repository(repository)
        except (ValidationError, ValueError) as manifest_error:
            raise ValueError("Failed to load manifest from '{0}':\n{1}".format(
                repository.url, manifest_error,
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
        try:
            for license_id in self.manifest.licenses:
                licenses.append(SpdxLicenseList.get_license(license_id))
        except (ValidationError, ValueError) as error:
            raise ValueError('Failed to load licenses:\n{0}'.format(error))
        return licenses

    @validate_call
    def hugo(self) -> str:
        """
        Generate Hugo content.

        Returns:
            str: Hugo content string.

        Raises:
            ValueError: If generating the Hugo content fails.
        """
        front_matter = self.model_dump(exclude_none=True, exclude={
            'id', 'manifest', 'description',
        })
        front_matter.update(self.manifest.model_dump(
            exclude_none=True,
            by_alias=True,
            exclude={'version', 'description', 'licenses', 'newsfeed'},
        ))
        try:
            return (
                '---\n{0}---\n{{{{< project >}}}}\n' +
                '{1}\n{{{{< /project >}}}}\n{{{{< latest-news >}}}}'
            ).format(yaml.safe_dump(front_matter), self.description)
        except yaml.YAMLError as error:
            raise ValueError('Failed to dump YAML:\n{0}'.format(error))

    @validate_call
    def dump(self, path: NewPath):
        """
        Dump Hugo content.

        Parameters:
            path: Hugo content file path for projects.

        Raises:
            ValueError: if dumping the Hugo content fails.
        """
        logging.info("{0} - Writing project page to '{1}'...".format(
            self.id, path,
        ))
        hugo_content = self.hugo()
        try:
            with open(path, 'w') as project_file:
                project_file.write(hugo_content)
        except OSError as error:
            raise ValueError("Failed to write file '{0}':\n{1}".format(
                path, error,
            ))
