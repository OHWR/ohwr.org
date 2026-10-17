# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Represent URLs."""

from functools import partial
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Annotated, Any
from urllib.parse import quote, urljoin
import warnings

import requests
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from rate_limit import (
    HEAD_FALLBACK_CODES,
    RateLimited,
    RequestFailed,
    gitlab_headers,
    request,
)


@dataclass
class Url:
    """Represent a URL."""

    url: str

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, core_schema_handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """
        Define a custom Pydantic core schema for validation.

        Parameters:
            source_type: Pydantic source type.
            core_schema_handler: Pydantic core schema handler.

        Returns:
            A Pydantic CoreSchema instance.
        """
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
            ),
        )

    @classmethod
    def _validate(cls, input_value: Any) -> 'Url':
        """
        Validate input value.

        Parameters:
            input_value: Value to validate.

        Returns:
            A Url instance.
        """
        if isinstance(input_value, cls):
            return input_value
        if isinstance(input_value, str):
            try:
                cls._head(input_value, wait_on_rate_limit=False)
            except RateLimited:
                # Rate limiting says nothing about whether the link works,
                # and waiting for it is not worth it for a lenient check.
                return cls(input_value)
            except ValueError as head_error:
                warnings.warn(head_error)
            return cls(input_value)
        warnings.warn("Invalid value: '{0}'".format(input_value))

    @classmethod
    def _serialize(cls, url: 'Url') -> str:
        return url.url

    @classmethod
    def _head(
        cls, url: str, max_retries: int = 5, wait_on_rate_limit: bool = True,
    ) -> requests.Response:
        try:
            return request(
                'head', url, max_retries, wait_on_rate_limit,
                timeout=10, allow_redirects=True,
            )
        except RequestFailed as head_error:
            if head_error.status_code not in HEAD_FALLBACK_CODES:
                raise
        # Fetch only the headers: the body is not downloaded.
        res = request(
            'get', url, max_retries, wait_on_rate_limit,
            timeout=10, stream=True,
        )
        res.close()
        return res

    @classmethod
    def _get(
        cls, url: str, headers: dict | None = None, max_retries: int = 5,
    ) -> requests.Response:
        return request('get', url, max_retries, headers=headers, timeout=10)


UrlList = Annotated[list[Url], Field(min_length=1)]


@dataclass
class StrictUrl(Url):
    """Represent a reachable URL."""

    @classmethod
    def _validate(cls, input_value: Any) -> 'StrictUrl':
        """
        Validate input value.

        Parameters:
            input_value: Value to validate.

        Returns:
            A StrictUrl instance.

        Raises:
            ValueError: If the provided value is not valid.
        """
        if isinstance(input_value, cls):
            return input_value
        if isinstance(input_value, str):
            cls._head(input_value)
            return cls(input_value)
        raise ValueError("Invalid value: '{0}'".format(input_value))


StrictUrlList = Annotated[list[StrictUrl], Field(min_length=1)]


@dataclass
class UrlContent(StrictUrl, ABC):
    """Abstract class to fetch URL content."""

    text: str

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> 'UrlContent':
        """
        Abstract constructor method to fetch content from a URL.

        Parameters:
            url: URL to fetch content from.

        Returns:
            A UrlContent instance.
        """

    @classmethod
    def create(cls, url: str) -> 'UrlContent':
        """
        Return a specific UrlContent instance based on the URL.

        Parameters:
            url: URL to fetch content from.

        Returns:
            A UrlContent instance.
        """
        gitlab = r'^https://(?:gitlab\.com|gitlab\.cern\.ch)/.+?/{0}/.+'
        if re.search(gitlab.format('wikis'), url):
            return GitLabWikiPage.from_url(url)
        if re.search(gitlab.format('-/raw'), url):
            return GitLabRawFile.from_url(url)
        return GenericUrlContent.from_url(url)

    @classmethod
    def _validate(cls, input_value: Any) -> 'UrlContent':
        """
        Validate input value.

        Parameters:
            input_value: Value to validate.

        Returns:
            A UrlContent instance.

        Raises:
            ValueError: If the provided value is not valid.
        """
        if isinstance(input_value, cls):
            return input_value
        if isinstance(input_value, str):
            return cls.create(input_value)
        raise ValueError("Invalid value: '{0}'".format(input_value))


class GitLabWikiPage(UrlContent):
    """GitLab Wiki page."""

    @classmethod
    def from_url(cls, url: str) -> 'GitLabWikiPage':
        """
        Fetch a GitLab Wiki page from a URL.

        Parameters:
            url: Wiki page URL.

        Returns:
            A GitLabWikiPage instance.

        Raises:
            ValueError: If fetching the wiki page fails.
        """
        exp = (
            r'^https://((?:gitlab\.com|gitlab\.cern\.ch))/' +
            '(.+?)(?:/-)?/wikis/(.+)'
        )
        match = re.search(exp, url)
        api_url = 'https://{0}/api/v4/projects/{1}/wikis/{2}'.format(
            match.group(1),
            quote(match.group(2), safe=''),
            quote(match.group(3), safe=''),
        )
        try:
            text = cls._get(
                api_url, headers=gitlab_headers(api_url.split('/')[2]),
            ).json()['content']
        except (TypeError, json.JSONDecodeError, KeyError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))
        replacer = partial(cls._rel_to_abs, url=url)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', replacer, text)
        return cls(api_url, text)

    @classmethod
    def _rel_to_abs(cls, match, url):
        text = match.group(1)
        link = match.group(2)
        if not re.match(r'^[a-zA-Z]+://', link):
            link = urljoin(url, link)
        return "[{}]({})".format(text, link)


class GitLabRawFile(UrlContent):
    """Raw file from a GitLab repository."""

    @classmethod
    def from_url(cls, url: str) -> 'GitLabRawFile':
        """
        Fetch a raw GitLab file from a URL.

        The '/-/raw/' web route does not accept access tokens, so when a
        token is configured the file is fetched through the repository files
        API instead. Without a token the API is heavily rate-limited, so the
        web route is used.

        Parameters:
            url: Raw file URL ('https://<host>/<project>/-/raw/<ref>/<path>').

        Returns:
            A GitLabRawFile instance.
        """
        exp = (
            r'^https://((?:gitlab\.com|gitlab\.cern\.ch))/' +
            r'(.+?)/-/raw/([^/]+)/([^?#]+)'
        )
        match = re.search(exp, url)
        headers = gitlab_headers(match.group(1))
        if not headers:
            return cls(url, cls._get(url).text)
        api_url = (
            'https://{0}/api/v4/projects/{1}/repository/files/{2}/raw' +
            '?ref={3}'
        ).format(
            match.group(1),
            quote(match.group(2), safe=''),
            quote(match.group(4), safe=''),
            quote(match.group(3), safe=''),
        )
        return cls(url, cls._get(api_url, headers=headers).text)


class GenericUrlContent(UrlContent):
    """Generic URL content."""

    @classmethod
    def from_url(cls, url: str) -> 'GenericUrlContent':
        """
        Fetch content from a URL.

        Parameters:
            url: URL to fetch content from.

        Returns:
            A GenericUrlContent instance.
        """
        return cls(url, cls._get(url).text)
