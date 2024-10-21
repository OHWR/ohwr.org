# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Fetch Git repository files."""

import json
import os
import re
import subprocess  # noqa: S404
from abc import ABC, abstractmethod
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from urllib.parse import quote

import requests


@dataclass
class Repository(ABC):
    """Abstract repository class to fetch files from a Git repository."""

    url: str

    @abstractmethod
    def fetch(self, path: str) -> str:
        """
        Abstract method to fetch files from a Git repository.

        Parameters:
            path: Path to the file to fetch from the Git repository.
        """

    @classmethod
    def from_url(cls, url: str) -> 'Repository':
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
        generic = r'^https://.+?\.git$'
        if re.search(github, url):
            return GitHubRepository(url)
        elif re.search(gitlab, url):
            return GitLabRepository(url)
        elif re.search(generic, url):
            return GenericRepository(url)
        raise ValueError("Failed to create repository from '{0}'".format(url))

    def _get(self, url: str, headers: str = '', timeout: float = 10) -> str:
        res = requests.get(url, headers=headers, timeout=timeout)
        res.raise_for_status()
        return res


class GitHubRepository(Repository):
    """GitHub repository."""

    def fetch(self, path: str) -> str:
        """
        Fetch a file from the GitHub repository.

        Parameters:
            path: Path to the file to fetch from the GitHub repository.

        Returns:
            File contents.

        Raises:
            ValueError: If requesting the file fails.
        """
        url = 'https://api.github.com/repos/{0}/contents/{1}'.format(
            re.search(r'^https://github\.com/(.+?)\.git', self.url).group(1),
            path,
        )
        headers = {'Accept': 'application/vnd.github.v3.raw'}
        try:
            res = self._get(url, headers=headers)
        except requests.exceptions.RequestException as get_error:
            raise ValueError("Failed to request '{0}':\n{1}".format(
                url, get_error,
            ))
        return res.text


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
        exp = (
            r'^https://((?:gitlab\.com|ohwr\.org|gitlab\.cern\.ch))/(.+?)\.git'
        )
        match = re.search(exp, self.url)
        url = 'https://{0}/api/v4/projects/{1}'.format(
            match.group(1),
            quote(match.group(2), safe=''),
        )
        try:
            res = self._get(url)
        except requests.exceptions.RequestException as get_project_error:
            raise ValueError("Failed to request '{0}':\n{1}".format(
                url, get_project_error,
            ))
        try:
            default_branch = res.json()['default_branch']
        except (TypeError, json.JSONDecodeError, KeyError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))
        url = 'https://{0}/{1}/-/raw/{2}/{3}'.format(
            match.group(1), match.group(2), default_branch, path,
        )
        try:
            res = self._get(url)
        except requests.exceptions.RequestException as get_error:
            raise ValueError("Failed to request '{0}':\n{1}".format(
                url, get_error,
            ))
        return res.text


class GenericRepository(Repository):
    """Generic repository."""

    def fetch(self, path: str) -> str:
        """
        Fetch a file from the Git repository.

        Parameters:
            path: Path to the file to fetch from the GitLab repository.

        Returns:
            File contents.

        Raises:
            ValueError: If repo cannot be cloned or file not found.
        """
        tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(  # noqa: S603, S607
                ['git', 'clone', '--depth', '1', self.url, tmpdir],
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as clone_error:
            raise ValueError("Failed to clone '{0}':\n{1}".format(
                self.url, clone_error,
            ))
        try:
            with open(os.path.join(tmpdir, path), 'r') as repository_file:
                return repository_file.read()
        except FileNotFoundError as file_error:
            raise ValueError("File '{0}' not found in '{1}':\n{2}".format(
                path, self.url, file_error,
            ))
