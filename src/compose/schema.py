# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Pydantic schema for YAML validation."""

from http import HTTPMethod, HTTPStatus
from typing import Annotated
from urllib import request
from urllib.error import URLError

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    HttpUrl,
    PlainSerializer,
    StringConstraints,
    ValidationError,
    validate_call,
)


class BaseModelForbidExtra(BaseModel, extra='forbid'):
    """Custom base class for Pydantic models with extra='forbid'."""


AnnotatedStr = Annotated[str, StringConstraints(
    strip_whitespace=True, min_length=1,
)]
AnnotatedStrList = Annotated[list[AnnotatedStr], Field(min_length=1)]


class Schema(BaseModelForbidExtra):
    """Model validation schema."""

    @classmethod
    @validate_call
    def from_yaml(cls, yaml_str: AnnotatedStr):
        """
        Load model from YAML.

        Parameters:
            yaml_str: YAML string.

        Returns:
            Schema: The schema object.

        Raises:
            ValueError: If loading the model from YAML fails.
        """
        try:
            yaml_dict = yaml.safe_load(yaml_str)
        except yaml.YAMLError as yaml_error:
            raise ValueError('Failed to load YAML:\n{0}'.format(yaml_error))
        try:
            return cls(**yaml_dict)
        except (ValidationError, TypeError) as cls_error:
            raise ValueError('Failed to initialize model:\n{0}'.format(
                cls_error,
            ))


def serialize(url: HttpUrl) -> str:
    """
    Serialize an HttpUrl into a string.

    Parameters:
        url: HTTP URL.

    Returns:
        URL string.
    """
    return str(url)


SerializableUrl = Annotated[HttpUrl, PlainSerializer(serialize)]


def is_reachable(url: HttpUrl) -> HttpUrl:
    """
    Check if the URL is reachable.

    Parameters:
        url: HTTP URL.

    Returns:
        HTTP URL.

    Raises:
        ValueError: if the URL is not reachable.
    """
    req = request.Request(url, method=HTTPMethod.HEAD)
    try:
        with request.urlopen(req, timeout=5) as res:  # noqa: S310
            if res.status != HTTPStatus.OK:
                raise ValueError("Status code: '{0}'.".format(res.status))
    except (URLError, ValueError, TimeoutError) as urlopen_error:
        raise ValueError("Failed to access URL '{0}':\n{1}".format(
            url, urlopen_error,
        ))
    return url


ReachableUrl = Annotated[SerializableUrl, AfterValidator(is_reachable)]
ReachableUrlList = Annotated[list[ReachableUrl], Field(min_length=1)]
