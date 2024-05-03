# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Handle git repositories."""

import os
import subprocess  # noqa: S404
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib import request
from urllib.error import URLError

from common import BaseModelForbidExtra
from pydantic import HttpUrl, ValidationError, computed_field, validate_call


class Repository(BaseModelForbidExtra, ABC):
    """Abstract base class representing a repository."""

    url: HttpUrl

    @abstractmethod
    def read(self, filepath: Path):
        """
        Abstract method to read a file from the repository.

        Args:
            filepath: The path of the file to retrieve.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """

    @classmethod
    @validate_call
    def create(cls, url: HttpUrl):
        """
        Create a repository object based on the provided URL.

        Parameters:
            url: Repository URL.

        Returns:
            Union[GitHubRepository, GenericRepository]: Repository object.

        Raises:
            ValueError: If parsing url or creating repository fails.
        """
        if url.host == 'github.com':
            try:
                return GitHubRepository(url=url)
            except ValidationError as github_error:
                raise ValueError(
                    "GitHub repository '{0}' is not valid:\n{1}".format(
                        url, github_error,
                    ),
                )
        else:
            try:
                return GenericRepository(url=url)
            except ValidationError as generic_error:
                raise ValueError(
                    "Generic repository '{0}' is not valid:\n{1}".format(
                        url, generic_error,
                    ),
                )

    @computed_field
    @cached_property
    def owner(self) -> str:
        """
        Retrieve the owner from the repository URL.

        Returns:
            str: owner.

        Raises:
            ValueError: If the owner cannot be parsed from the URL.
        """
        try:
            return self._split()[0]
        except IndexError as owner_error:
            raise ValueError("Failed to parse owner from '{0}':\n{1}".format(
                self.url, owner_error,
            ))

    @computed_field
    @cached_property
    def project(self) -> str:
        """
        Retrieve the project name from the repository URL.

        Returns:
            str: project name.

        Raises:
            ValueError: If the project name cannot be parsed from the URL.
        """
        try:
            return self._split()[1].removesuffix('.git')
        except IndexError as project_error:
            raise ValueError(
                "Failed to parse project name from '{0}':\n{1}".format(
                    self.url, project_error,
                ),
            )

    def _split(self) -> list[str]:
        path = self.url.path.removeprefix('/')
        return list(filter(None, path.split('/', 1)))


class GitHubRepository(Repository):
    """Represents a GitHub repository."""

    @validate_call
    def read(self, filepath: Path) -> str:
        """
        Read a file from the repository.

        Parameters:
            filepath: The path of the file to read.

        Returns:
            str: The file content.

        Raises:
            ConnectionError: If reading the file fails.
        """
        req = request.Request(
            'https://api.github.com/repos/{0}/{1}/contents/{2}'.format(
                self.owner, self.project, filepath,
            ),
            headers={'Accept': 'application/vnd.github.v3.raw'},
        )
        try:
            with request.urlopen(req, timeout=5) as response:  # noqa: S310
                return response.read().decode()
        except (URLError, ValueError, TimeoutError) as url_error:
            raise ConnectionError("Failed to request '{0}':\n{1}".format(
                req.full_url, url_error,
            ))


class GenericRepository(Repository):
    """Represents a generic repository."""

    @validate_call
    def read(self, filepath: Path) -> str:
        """
        Read a file from the repository.

        Args:
            filepath: The path of the file to read.

        Returns:
            str: The file content.

        Raises:
            RuntimeError: If cloning the repository fails.
            ValueError: If the specified file is not found in the repository.
        """
        tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(
                'git clone --depth 1 {0} {1}'.format(self.url, tmpdir),
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: S602
            )
        except subprocess.CalledProcessError as clone_error:
            raise RuntimeError("Failed to clone '{0}':\n{1}".format(
                self.url, clone_error,
            ))
        try:
            with open(os.path.join(tmpdir, filepath), 'r') as repository_file:
                return repository_file.read()
        except FileNotFoundError as file_error:
            raise ValueError("File '{0}' not found in '{1}':\n{2}".format(
                filepath, self.url, file_error,
            ))
