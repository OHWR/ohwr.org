# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load, parse and validate project description."""

import re
from urllib import request
from urllib.error import URLError

from base import BaseModelForbidExtra
from pydantic import ValidationError


class DescriptionError(Exception):
    """Failed to load, parse or validate description."""


class Description(BaseModelForbidExtra):
    """Loads, parses and validates project description."""

    md: str

    @classmethod
    def from_url(cls, url: str):
        """
        Load a Markdown description from a URL.

        Parameters:
            url: Markdown description URL.

        Returns:
            Description object.

        Raises:
            DescriptionError: if loading the description fails.
        """
        try:
            with request.urlopen(url) as response:  # noqa: S310
                return cls.load(response.read().decode('utf-8'))
        except URLError as error:
            msg = 'Failed to request {0}:\n↳ {1}'
            raise DescriptionError(msg.format(url, error))

    @classmethod
    def load(cls, md: str):
        """
        Parse and validate project Markdown description.

        Parameters:
            md: Markdown description.

        Returns:
            Description object.

        Raises:
            DescriptionError: if parsing or validating the description fails.
        """
        try:
            md = re.sub('<!--(.*?)-->', '', md, flags=re.DOTALL).strip()
        except ValueError as re_error:
            msg = 'Failed to process Markdown content:\n↳ {0}'
            raise DescriptionError(msg.format(re_error))
        while md.startswith('#'):
            try:
                md = md.split('\n', 1)[1].strip()
            except IndexError as split_error:
                msg = 'Failed to fetch Markdown after headings:\n↳ {0}'
                raise DescriptionError(msg.format(split_error))
        try:
            return cls(md=md.split('\n#')[0].strip())
        except ValidationError as validation_error:
            msg = 'Description is not valid:\n↳ {0}'
            raise DescriptionError(msg.format(validation_error))
