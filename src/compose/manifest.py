# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


from typing import Annotated, Literal, Optional

from common import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    ReachableUrl,
    ReachableUrlList,
    YamlSchema,
)
from pydantic import Field, HttpUrl, ValidationError, validate_call
from repository import Repository


class Link(BaseModelForbidExtra):
    """Link schema."""

    name: AnnotatedStr
    url: ReachableUrl


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(YamlSchema):
    """Manifest schema."""

    version: Literal['1.0.0']
    name: AnnotatedStr = Field(serialization_alias='title')
    description: HttpUrl
    website: ReachableUrl
    licenses: AnnotatedStrList
    images: Optional[ReachableUrlList] = None
    documentation: Optional[ReachableUrl] = None
    issues: Optional[ReachableUrl] = None
    latest_release: Optional[ReachableUrl] = None
    forum: Optional[ReachableUrl] = None
    newsfeed: Optional[HttpUrl] = None
    links: Optional[LinkList] = None

    @classmethod
    @validate_call
    def from_repository(cls, repository: Repository):
        """
        Load the manifest from Git repository.

        Parameters:
            repository: Git repository.

        Returns:
            Manifest: The manifest object.

        Raises:
            ValueError: If loading the manifest fails.
        """
        try:
            manifest_yaml = repository.read('.ohwr.yaml')
        except (
            ValidationError, ValueError, ConnectionError, RuntimeError,
        ) as manifest_error:
            raise ValueError(
                "Failed to fetch '.ohwr.yaml' from '{0}':\n{1}".format(
                    repository.url, manifest_error,
                ),
            )
        try:
            return cls.from_yaml(manifest_yaml)
        except (ValidationError, ValueError) as yaml_error:
            raise ValueError(
                "Failed to parse '.ohwr.yaml' from '{0}':\n{1}".format(
                    repository.url, yaml_error,
                ),
            )
