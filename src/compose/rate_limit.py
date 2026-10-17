# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Helpers to cope with rate-limited HTTP APIs."""

import logging
import math
import os
import time
from http import HTTPStatus
from urllib.parse import urlparse

import requests

MAX_RETRY_DELAY = 120

RATE_LIMIT_CODES = frozenset((429, 503))

# Client errors that will not change by retrying (all 4xx except 408 and 429).
PERMANENT_ERROR_CODES = frozenset(
    range(HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR),
) - {HTTPStatus.REQUEST_TIMEOUT, HTTPStatus.TOO_MANY_REQUESTS}

# Some servers reject HEAD requests: check those URLs with GET instead.
HEAD_FALLBACK_CODES = frozenset((405,))

# Minimum time between two requests to the same host, in seconds. This keeps
# the build under GitLab's limit of 500 unauthenticated requests per minute.
MIN_REQUEST_INTERVAL = 0.15

_last_request: dict[str, float] = {}


class RequestFailed(ValueError):
    """All attempts of an HTTP request failed."""

    def __init__(
        self, method: str, url: str, error: Exception | None,
    ) -> None:
        """
        Build the error message and keep the last HTTP status code.

        Parameters:
            method: HTTP method name.
            url: Requested URL.
            error: Last error raised by requests.
        """
        super().__init__("{0} request to '{1}' failed:\n{2}".format(
            method.upper(), url, error,
        ))
        res = getattr(error, 'response', None)
        self.status_code = None if res is None else res.status_code
        self.rate_limited = RateLimited.matches(res)

    @classmethod
    def create(
        cls, method: str, url: str, error: Exception | None,
        waited_on_rate_limit: bool,
    ) -> 'RequestFailed':
        """
        Return a RateLimited error if the request was rate-limited.

        Parameters:
            method: HTTP method name.
            url: Requested URL.
            error: Last error raised by requests.
            waited_on_rate_limit: Whether the request waited when it was
                rate-limited; if not, the skipped request is logged.

        Returns:
            A RequestFailed or RateLimited instance.
        """
        failure = cls(method, url, error)
        if not failure.rate_limited:
            return failure
        if not waited_on_rate_limit:
            logging.info("Not checked, rate-limited: '{0}'".format(url))
        return RateLimited(method, url, error)


class RateLimited(RequestFailed):
    """The last attempt of an HTTP request was rate-limited."""

    @classmethod
    def matches(cls, res: requests.Response | None) -> bool:
        """
        Tell whether a response means the request was rate-limited.

        Parameters:
            res: HTTP response, or None if no response was received.

        Returns:
            True if the server rate-limited the request.
        """
        if res is None:
            return False
        if res.status_code in RATE_LIMIT_CODES:
            return True
        # GitHub reports rate limits as 403 with one of these headers.
        return res.status_code == HTTPStatus.FORBIDDEN and (
            res.headers.get('X-RateLimit-Remaining') == '0' or
            'Retry-After' in res.headers
        )


def request(
    method: str, url: str, max_retries: int = 5,
    wait_on_rate_limit: bool = True, **kwargs,
) -> requests.Response:
    """
    Send an HTTP request, retrying on errors and honouring rate limits.

    Parameters:
        method: HTTP method name of the requests module ('get', 'head').
        url: URL to request.
        max_retries: Maximum number of attempts.
        wait_on_rate_limit: Wait and retry when rate-limited; if False, give
            up at the first rate-limited response.
        kwargs: Extra keyword arguments passed to the requests function.

    Returns:
        A successful response.

    Raises:
        RateLimited: If the last attempt was rate-limited.
        RequestFailed: If all attempts fail for another reason.
    """
    requests_error = None
    for attempt in range(max_retries):
        try:
            return _send(method, url, kwargs)
        except requests.exceptions.RequestException as request_error:
            requests_error = request_error
        delay = _error_delay(requests_error, attempt, wait_on_rate_limit)
        if delay > MAX_RETRY_DELAY or attempt == max_retries - 1:
            break
        time.sleep(delay)
    raise RequestFailed.create(method, url, requests_error, wait_on_rate_limit)


def _send(method: str, url: str, kwargs: dict) -> requests.Response:
    # Space out requests to the same host.
    host = urlparse(url).hostname or ''
    wait = _last_request.get(host, 0) + MIN_REQUEST_INTERVAL - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request[host] = time.monotonic()
    res = getattr(requests, method)(url, **kwargs)
    try:
        res.raise_for_status()
    except requests.exceptions.RequestException:
        # Release the connection: streamed responses keep it open.
        res.close()
        raise
    return res


def _error_delay(
    error: Exception, attempt: int, wait_on_rate_limit: bool,
) -> float:
    res = getattr(error, 'response', None)
    if res is None:
        return attempt + 1
    if RateLimited.matches(res):
        if not wait_on_rate_limit:
            return math.inf
        return retry_delay(res, attempt)
    if res.status_code in PERMANENT_ERROR_CODES:
        return math.inf
    return attempt + 1


def retry_delay(res: requests.Response, attempt: int) -> float:
    """
    Compute how long to wait before retrying a rate-limited request.

    Parameters:
        res: Response with a rate-limit status code.
        attempt: Zero-based index of the failed attempt.

    Returns:
        Delay in seconds requested by the server, or an exponential backoff.
    """
    delay = 2 ** (attempt + 1)
    retry_after = str(res.headers.get('Retry-After', ''))
    reset = str(res.headers.get(
        'RateLimit-Reset', res.headers.get('X-RateLimit-Reset', ''),
    ))
    if retry_after.isdigit():
        delay = int(retry_after)
    elif reset.isdigit():
        delay = int(reset) - time.time()
    return max(delay, 1)


def gitlab_headers(host: str) -> dict:
    """
    Return authentication headers for a GitLab instance.

    The token is read from GITLAB_TOKEN (gitlab.com) or GITLAB_CERN_TOKEN
    (gitlab.cern.ch). Authenticated requests get much higher rate limits.

    Parameters:
        host: GitLab host name.

    Returns:
        Headers dictionary, empty if no token is configured.
    """
    env_vars = {
        'gitlab.com': 'GITLAB_TOKEN',
        'gitlab.cern.ch': 'GITLAB_CERN_TOKEN',
    }
    token = os.environ.get(env_vars.get(host, ''))
    if token:
        return {'PRIVATE-TOKEN': token}
    return {}
