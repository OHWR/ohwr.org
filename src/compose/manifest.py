# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


from typing import Annotated, Literal, Optional

from pydantic import Field
from schema import AnnotatedStr, AnnotatedStrList, BaseModelForbidExtra, Schema
from url import StrictUrl, UrlContent, StrictUrlList


class Link(BaseModelForbidExtra):
    """Link configuration."""

    name: AnnotatedStr
    url: StrictUrl


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(Schema):
    """Manifest schema."""

    version: Literal['1.0.0'] = Field(exclude=True)
    name: AnnotatedStr = Field(serialization_alias='title')
    description: UrlContent = Field(exclude=True)
    website: StrictUrl
    licenses: Optional[AnnotatedStrList] = Field(default=None, exclude=True)
    images: Optional[StrictUrlList] = None
    documentation: Optional[StrictUrl] = None
    issues: Optional[StrictUrl] = None
    latest_release: Optional[StrictUrl] = None
    forum: Optional[StrictUrl] = None
    newsfeed: Optional[UrlContent] = Field(default=None, exclude=True)
    links: Optional[LinkList] = None
