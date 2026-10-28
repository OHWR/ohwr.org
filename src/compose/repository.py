# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Represent Git Repositories."""

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from rate_limit import gitlab_headers
from url import StrictUrl


@dataclass
class Repository(StrictUrl, ABC):
    """Abstract repository class to fetch files from a Git repository."""

    @classmethod
    def create(cls, url: str) -> 'Repository':
        """
        Return a specific repository based on the URL.

        Parameters:
            url: The Git repository URL.

        Returns:
            A Repository instance.

        Raises:
            ValueError: If creating a repository from the provided URL fails.
        """
        github = r'^https://github\.com/.+?\.git$'
        gitlab = r'^https://(?:gitlab\.com|gitlab\.cern\.ch)/.+?\.git$'
        if re.search(github, url):
            return GitHubRepository(url)
        elif re.search(gitlab, url):
            return GitLabRepository(url)
        raise ValueError("Unsupported repository URL '{0}'".format(url))

    @abstractmethod
    def fetch(self, path: str) -> str:
        """
        Abstract method to fetch files from a Git repository.

        Parameters:
            path: Path to the file to fetch from the Git repository.
        """

    @classmethod
    def _validate(cls, input_value: Any) -> 'Repository':
        """
        Validate input value.

        Parameters:
            input_value: Value to validate.

        Returns:
            A Repository instance.

        Raises:
            ValueError: If the provided value is not valid.
        """
        if isinstance(input_value, cls):
            return input_value
        if isinstance(input_value, str):
            return cls.create(input_value)
        raise ValueError("Invalid value: '{0}'".format(input_value))


class GitHubRepository(Repository):
    """GitHub repository."""

    def fetch(self, path: str) -> str:
        """
        Fetch a file from the GitHub repository.

        Parameters:
            path: Path to the file to fetch from the GitHub repository.

        Returns:
            File contents.
        """
        url = 'https://api.github.com/repos/{0}/contents/{1}'.format(
            re.search(r'^https://github\.com/(.+?)\.git', self.url).group(1),
            path,
        )
        headers = {'Accept': 'application/vnd.github.v3.raw'}
        # Anonymous API requests are limited to 60 per hour per IP, which
        # is often used up on shared CI runners.
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = 'Bearer {0}'.format(token)
        return self._get(url, headers=headers).text


class GitLabRepository(Repository):
    """GitLab repository."""

    def fetch(self, path: str) -> str:
        """
        Fetch a file from the GitLab repository.

        Parameters:
            path: Path to the file to fetch from the GitLab repository.

        Returns:
            File contents.

        Raises:
            ValueError: If requesting the file fails.
        """
        match = re.search(
            r'^https://((?:gitlab\.com|gitlab\.cern\.ch))/(.+?)\.git',
            self.url,
        )
        headers = gitlab_headers(match.group(1))
        if not headers:
            # Without a token the API is heavily rate-limited: use the web
            # route instead, where 'HEAD' resolves to the default branch.
            url = 'https://{0}/{1}/-/raw/HEAD/{2}'.format(
                match.group(1), match.group(2), path,
            )
            return self._get(url).text
        url = 'https://{0}/api/v4/projects/{1}'.format(
            match.group(1),
            quote(match.group(2), safe=''),
        )
        try:
            default_branch = self._get(
                url, headers=headers,
            ).json()['default_branch']
        except (TypeError, json.JSONDecodeError, KeyError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))
        url = '{0}/repository/files/{1}/raw?ref={2}'.format(
            url, quote(path, safe=''), quote(default_branch, safe=''),
        )
        return self._get(url, headers=headers).text
