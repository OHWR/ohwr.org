# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import logging

from requests.exceptions import HTTPError

from url import Url

EXAMPLE_URL = "http://example.com"
REQUESTS_HEAD = "requests.head"
NOT_FOUND = 404
TOO_MANY_REQUESTS = 429


def error_response(mocker, status_code):
    response = mocker.Mock()
    response.status_code = status_code
    response.headers = {"Retry-After": "60"}
    response.raise_for_status.side_effect = HTTPError(
        str(status_code), response=response,
    )
    return response


class TestUrlCheck:
    """Test the lenient Url link check."""

    def test_rate_limited_link_is_not_a_warning(
        self, mocker, recwarn, caplog,
    ):
        limited = error_response(mocker, TOO_MANY_REQUESTS)
        mock_head = mocker.patch(REQUESTS_HEAD, return_value=limited)

        with caplog.at_level(logging.INFO):
            assert Url._validate(EXAMPLE_URL) == Url(EXAMPLE_URL)
        assert mock_head.call_count == 1
        assert not recwarn.list
        assert "Not checked, rate-limited: '{0}'".format(
            EXAMPLE_URL,
        ) in caplog.text

    def test_broken_link_is_a_warning(self, mocker, recwarn):
        missing = error_response(mocker, NOT_FOUND)
        mocker.patch(REQUESTS_HEAD, return_value=missing)

        assert Url._validate(EXAMPLE_URL) == Url(EXAMPLE_URL)
        assert len(recwarn.list) == 1
        assert "404" in str(recwarn.list[0].message)
