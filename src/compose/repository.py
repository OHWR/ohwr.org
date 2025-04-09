# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Represent Git Repositories."""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from url import Url


@dataclass
class Repository(Url, ABC):
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
        gitlab = (
            r'^https://(?:gitlab\.com|ohwr\.org|gitlab\.cern\.ch)/.+?\.git$'
        )
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
        exp = (r'^https://((?:gitlab\.com|gitlab\.cern\.ch))/(.+?)\.git')
        match = re.search(exp, self.url)
        url = 'https://{0}/api/v4/projects/{1}'.format(
            match.group(1),
            quote(match.group(2), safe=''),
        )
        try:
            default_branch = self._get(url).json()['default_branch']
        except (TypeError, json.JSONDecodeError, KeyError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))
        url = 'https://{0}/{1}/-/raw/{2}/{3}'.format(
            match.group(1), match.group(2), default_branch, path,
        )
        return self._get(url).text
