# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Handle git repositories."""

import os
import subprocess  # noqa: S404
from abc import ABC, abstractmethod
from collections import UserString
from tempfile import TemporaryDirectory
from urllib import request
from urllib.error import URLError
from urllib.parse import urlparse


class Repository(UserString, ABC):
    """Abstract base class representing a repository."""

    @abstractmethod
    def read(self, path: str):
        """
        Abstract method to read a file from the repository.

        Args:
            path: The path of the file to retrieve.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """

    @classmethod
    def create(cls, url: str):
        """
        Create a repository object based on the provided URL.

        Parameters:
            url: Repository URL.

        Returns:
            Union[GitHubRepository, GenericRepository]: Repository object.
        """
        if urlparse(url).hostname == 'github.com':
            return GitHubRepository(url)
        return GenericRepository(url)


class GitHubRepository(Repository):
    """Represents a GitHub repository."""

    def read(self, path: str) -> str:
        """
        Read a file from the repository.

        Parameters:
            path: The path of the file to read.

        Returns:
            str: The file content.

        Raises:
            ValueError: If reading the file fails.
        """
        split = urlparse(self.data).path.split('/')
        try:
            project = split[-1].removesuffix('.git')
        except IndexError as project_error:
            raise ValueError(
                "Failed to parse project name from '{0}':\n{1}".format(
                    self.data, project_error,
                ),
            )
        try:
            owner = split[-2]
        except IndexError as owner_error:
            raise ValueError("Failed to parse owner from '{0}':\n{1}".format(
                self.data, owner_error,
            ))
        req = request.Request(
            'https://api.github.com/repos/{0}/{1}/contents/{2}'.format(
                owner, project, path,
            ),
            headers={'Accept': 'application/vnd.github.v3.raw'},
        )
        try:
            with request.urlopen(req, timeout=5) as response:  # noqa: S310
                return response.read().decode()
        except (URLError, ValueError, TimeoutError) as url_error:
            raise ValueError("Failed to request '{0}':\n{1}".format(
                req.full_url, url_error,
            ))


class GenericRepository(Repository):
    """Represents a generic repository."""

    def read(self, path: str) -> str:
        """
        Read a file from the repository.

        Args:
            path: The path of the file to read.

        Returns:
            str: The file content.

        Raises:
            ValueError: If reading the file fails.
        """
        tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(
                'git clone --depth 1 {0} {1}'.format(self.data, tmpdir),
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: S602
            )
        except subprocess.CalledProcessError as clone_error:
            raise ValueError("Failed to clone '{0}':\n{1}".format(
                self.data, clone_error,
            ))
        try:
            with open(os.path.join(tmpdir, path), 'r') as repository_file:
                return repository_file.read()
        except FileNotFoundError as file_error:
            raise ValueError("File '{0}' not found in '{1}':\n{2}".format(
                path, self.data, file_error,
            ))
