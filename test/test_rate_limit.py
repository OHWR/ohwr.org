# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest
from requests.exceptions import HTTPError

from rate_limit import (
    MIN_REQUEST_INTERVAL,
    RateLimited,
    RequestFailed,
    gitlab_headers,
    request,
    retry_delay,
)

EXAMPLE_URL = "http://example.com"
OTHER_URL = "http://example.org"
REQUESTS_GET = "requests.get"
GET = "get"
HTTP_OK = 200
HTTP_ERROR = 400
TOO_MANY = 429
NOT_FOUND = 404
RETRY_AFTER = 30
RETRY_AFTER_HEADER = "Retry-After"
NOW = 1000
RESET_IN = 45
LONG_WAIT = 1649
TOKEN_VAR = "GITLAB_TOKEN"
TOKEN = "secret"


def make_response(mocker, status_code, headers=None):
    response = mocker.Mock()
    response.status_code = status_code
    response.headers = headers or {}
    if status_code >= HTTP_ERROR:
        response.raise_for_status.side_effect = HTTPError(
            str(status_code), response=response,
        )
    else:
        response.raise_for_status.return_value = None
    return response


class TestRequest:
    """Test retrying requests."""

    def test_retry_after_rate_limit(self, mocker, mock_sleep):
        limited = make_response(mocker, TOO_MANY, {RETRY_AFTER_HEADER: "7"})
        ok = make_response(mocker, HTTP_OK)
        mock_get = mocker.patch(REQUESTS_GET, side_effect=[limited, ok])

        assert request(GET, EXAMPLE_URL, timeout=10) == ok
        assert mock_get.call_count == 2
        mock_sleep.assert_any_call(7)

    def test_gives_up_after_max_retries(self, mocker):
        limited = make_response(mocker, TOO_MANY)
        mock_get = mocker.patch(REQUESTS_GET, return_value=limited)

        with pytest.raises(ValueError, match="GET request"):
            request(GET, EXAMPLE_URL, max_retries=3)
        assert mock_get.call_count == 3

    def test_no_retry_on_client_error(self, mocker, mock_sleep):
        missing = make_response(mocker, NOT_FOUND)
        mock_get = mocker.patch(REQUESTS_GET, return_value=missing)

        with pytest.raises(RequestFailed) as excinfo:
            request(GET, EXAMPLE_URL)
        assert excinfo.value.status_code == NOT_FOUND
        assert mock_get.call_count == 1

    def test_no_wait_on_rate_limit(self, mocker, mock_sleep):
        limited = make_response(mocker, TOO_MANY, {RETRY_AFTER_HEADER: "7"})
        mock_get = mocker.patch(REQUESTS_GET, return_value=limited)

        with pytest.raises(RateLimited):
            request(GET, EXAMPLE_URL, wait_on_rate_limit=False)
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()

    def test_closes_failed_response(self, mocker):
        limited = make_response(mocker, TOO_MANY)
        mocker.patch(REQUESTS_GET, return_value=limited)

        with pytest.raises(RequestFailed):
            request(GET, EXAMPLE_URL, max_retries=1, stream=True)
        limited.close.assert_called_once()

    def test_gives_up_when_wait_too_long(self, mocker, mock_sleep):
        headers = {RETRY_AFTER_HEADER: str(LONG_WAIT)}
        limited = make_response(mocker, TOO_MANY, headers)
        mock_get = mocker.patch(REQUESTS_GET, return_value=limited)

        with pytest.raises(RequestFailed) as excinfo:
            request(GET, EXAMPLE_URL)
        assert excinfo.value.status_code == TOO_MANY
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()


class TestThrottle:
    """Test spacing out requests to the same host."""

    def test_waits_between_requests_to_same_host(self, mocker, mock_sleep):
        ok = make_response(mocker, HTTP_OK)
        mocker.patch(REQUESTS_GET, return_value=ok)

        request(GET, EXAMPLE_URL)
        mock_sleep.assert_not_called()
        request(GET, EXAMPLE_URL)
        mock_sleep.assert_called_once()
        assert 0 < mock_sleep.call_args.args[0] <= MIN_REQUEST_INTERVAL

    def test_no_wait_for_different_hosts(self, mocker, mock_sleep):
        ok = make_response(mocker, HTTP_OK)
        mocker.patch(REQUESTS_GET, return_value=ok)

        request(GET, EXAMPLE_URL)
        request(GET, OTHER_URL)
        mock_sleep.assert_not_called()


class TestRetryDelay:
    """Test computing the retry delay."""

    def test_retry_after(self, mocker):
        headers = {RETRY_AFTER_HEADER: str(RETRY_AFTER)}
        res = make_response(mocker, TOO_MANY, headers)
        assert retry_delay(res, 0) == RETRY_AFTER

    def test_rate_limit_reset(self, mocker):
        mocker.patch("time.time", return_value=NOW)
        headers = {"RateLimit-Reset": str(NOW + RESET_IN)}
        res = make_response(mocker, TOO_MANY, headers)
        assert retry_delay(res, 0) == RESET_IN

    def test_exponential_backoff(self, mocker):
        res = make_response(mocker, TOO_MANY)
        assert retry_delay(res, 0) == 2
        assert retry_delay(res, 2) == 8


class TestGitLabHeaders:
    """Test GitLab authentication headers."""

    def test_no_token(self, monkeypatch):
        monkeypatch.delenv(TOKEN_VAR, raising=False)
        assert gitlab_headers("gitlab.com") == {}

    def test_gitlab_com_token(self, monkeypatch):
        monkeypatch.setenv(TOKEN_VAR, TOKEN)
        assert gitlab_headers("gitlab.com") == {"PRIVATE-TOKEN": TOKEN}

    def test_cern_token(self, monkeypatch):
        monkeypatch.setenv(TOKEN_VAR, TOKEN)
        monkeypatch.setenv("GITLAB_CERN_TOKEN", "cern")
        assert gitlab_headers("gitlab.cern.ch") == {"PRIVATE-TOKEN": "cern"}

    def test_unknown_host(self, monkeypatch):
        monkeypatch.setenv(TOKEN_VAR, TOKEN)
        assert gitlab_headers("example.com") == {}
