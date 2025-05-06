# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


from typing import Annotated, Literal, Optional

from pydantic import Field
from schema import AnnotatedStr, AnnotatedStrList, BaseModelForbidExtra, Schema
from url import Url, UrlContent, UrlList


class Link(BaseModelForbidExtra):
    """Link configuration."""

    name: AnnotatedStr
    url: Url


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(Schema):
    """Manifest schema."""

    version: Literal['1.0.0'] = Field(exclude=True)
    name: AnnotatedStr = Field(serialization_alias='title')
    description: UrlContent = Field(exclude=True)
    website: Url
    licenses: Optional[AnnotatedStrList] = Field(default=None, exclude=True)
    images: Optional[UrlList] = None
    documentation: Optional[Url] = None
    issues: Optional[Url] = None
    latest_release: Optional[Url] = None
    forum: Optional[Url] = None
    newsfeed: Optional[UrlContent] = Field(default=None, exclude=True)
    links: Optional[LinkList] = None
