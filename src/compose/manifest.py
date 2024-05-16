# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


from typing import Annotated, Literal, Optional

from pydantic import Field, HttpUrl, validate_call
from repository import Repository
from schema import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    ReachableUrl,
    ReachableUrlList,
    Schema,
)


class Link(BaseModelForbidExtra):
    """Link configuration."""

    name: AnnotatedStr
    url: ReachableUrl


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(Schema):
    """Manifest schema."""

    version: Literal['1.0.0'] = Field(exclude=True)
    name: AnnotatedStr = Field(serialization_alias='title')
    description: HttpUrl = Field(exclude=True)
    website: ReachableUrl
    licenses: AnnotatedStrList = Field(exclude=True)
    images: Optional[ReachableUrlList] = None
    documentation: Optional[ReachableUrl] = None
    issues: Optional[ReachableUrl] = None
    latest_release: Optional[ReachableUrl] = None
    forum: Optional[ReachableUrl] = None
    newsfeed: Optional[HttpUrl] = Field(default=None, exclude=True)
    links: Optional[LinkList] = None

    @classmethod
    @validate_call
    def from_repository(cls, url: HttpUrl):
        """
        Load the manifest from Git repository.

        Parameters:
            url: Git repository url.

        Returns:
            Manifest: The manifest object.

        Raises:
            ValueError: If loading the manifest fails.
        """
        try:
            repository = Repository.create(str(url))
        except ValueError as repository_error:
            raise ValueError(
                "Failed to load repository from '{0}':\n{1}".format(
                    url, repository_error,
                ))
        try:
            manifest_yaml = repository.read('.ohwr.yaml')
        except ValueError as manifest_error:
            raise ValueError(
                "Failed to fetch '.ohwr.yaml' from '{0}':\n{1}".format(
                    url, manifest_error,
                ),
            )
        return cls.from_yaml(manifest_yaml)
