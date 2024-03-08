# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load, parse and validate configuration."""

from http import HTTPMethod, HTTPStatus
from logging import debug
from typing import Any, Type
from urllib import request
from urllib.error import URLError

from pydantic import GetCoreSchemaHandler, ValidationInfo
from pydantic_core import core_schema


class URL(object):
    """Data type that checks if a string is a reachable URL."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], schema_handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Generate CoreSchema for URL custom type.

        Parameters:
            source: target class.
            schema_handler: callable that calls into schema generation logic.

        Returns:
            CoreSchema object.
        """
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )

    @classmethod
    def validate(cls, url: str, validation_info: ValidationInfo) -> str:
        """
        Check if a string is a reachable URL.

        Parameters:
            url: URL string.
            validation_info: validation information.

        Returns:
            URL string.

        Raises:
            ValueError: if the URL is not reachable.
        """
        req = request.Request(url, method=HTTPMethod.HEAD)
        debug('Checking if URL is reachable: {0}.'.format(url))
        try:
            with request.urlopen(req) as response:  # noqa: S310
                if response.status != HTTPStatus.OK:
                    msg = 'URL is unreachable: {0}:\n↳ Status Code: {1}'
                    raise ValueError(msg.format(url, response.status))
        except URLError as error:
            msg = 'URL is unreachable: {0}:\n↳ {1}'
            raise ValueError(msg.format(url, error))
        return url
