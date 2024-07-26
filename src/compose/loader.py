# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load content from various types of URLs."""

import json
import os
import re
import subprocess  # noqa: S404
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from urllib import request
from urllib.error import URLError


@dataclass
class Loader:
    """Loads content from a URL or path."""

    req: request.Request

    def load(self, path: str = '') -> str:
        """
        Load content from the URL or path.

        Parameters:
            path: Path to append to the URL. Default is ''.

        Returns:
            Content from the URL.

        Raises:
            ValueError: If loading content fails.
        """
        req = self.req
        if path:
            req.full_url = '{0}/{1}'.format(req.full_url, path)
        try:
            with request.urlopen(req, timeout=5) as res:  # noqa: S310
                return res.read().decode('utf-8')
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError("Failed to load from '{0}':\n{1}".format(
                req.full_url, urlopen_error,
            ))

    @classmethod
    def from_url(cls, url: str) -> 'Loader':
        """
        Create a Loader based on the URL.

        Parameters:
            url: The URL to load from.

        Returns:
            A Loader instance.
        """
        github_repo = r'^https://github\.com/.+?\.git$'
        gitlab_repo = r'^https://(?:gitlab\.com|ohwr\.org)/.+?\.git$'
        gitlab_wiki = r'^https://(?:gitlab\.com|ohwr\.org)/.+?/wikis/.+'
        git_repo = r'^https://.+?\.git$'
        req = request.Request(url)
        if re.search(github_repo, url):
            return GitHubRepositoryLoader(req)
        elif re.search(gitlab_repo, url):
            return GitLabRepositoryLoader(req)
        elif re.search(gitlab_wiki, url):
            return GitLabWikiLoader(req)
        elif re.search(git_repo, url):
            return GitRepositoryLoader(req)
        return cls(req)


class GitHubRepositoryLoader(Loader):
    """Loader for GitHub repository URLs."""

    def __init__(self, req: request.Request) -> 'GitHubRepositoryLoader':
        """
        Initialize with a request object.

        Parameters:
            req: Request for the GitHub URL.
        """
        exp = r'^https://github\.com/(.+?)\.git'
        repo = re.search(exp, req.full_url).group(1)
        super().__init__(request.Request(
            'https://api.github.com/repos/{0}/contents'.format(repo),
            headers={'Accept': 'application/vnd.github.v3.raw'},
        ))


class GitLabRepositoryLoader(Loader):
    """Loader for GitLab repository URLs."""

    def __init__(self, req: request.Request) -> 'GitLabRepositoryLoader':
        """
        Initialize with a request object.

        Parameters:
            req: Request for the GitLab URL.

        Raises:
            ValueError: If info or branch cannot be retrieved.
        """
        exp = r'^https://((?:gitlab\.com|ohwr\.org))/(.+?)\.git'
        match = re.search(exp, req.full_url)
        try:
            project = Loader.from_url('https://{0}/api/v4/projects/{1}'.format(
                match.group(1),
                match.group(2).replace('/', '%2F'),  # noqa: WPS323
            )).load()
        except ValueError as info_error:
            raise ValueError('Failed to repository info:\n{0}'.format(
                info_error,
            ))
        try:
            default_branch = json.loads(project)['default_branch']
        except (TypeError, json.JSONDecodeError, KeyError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))
        super().__init__(
            request.Request('https://{0}/{1}/-/raw/{2}'.format(
                match.group(1), match.group(2), default_branch,
            )),
        )


class GitLabWikiLoader(Loader):
    """Loader for GitLab wiki URLs."""

    def __init__(self, req: request.Request) -> 'GitLabWikiLoader':
        """
        Initialize with a request object.

        Parameters:
            req: Request for the GitLab wiki URL.
        """
        exp = r'^https://((?:gitlab\.com|ohwr\.org))/(.+?)(?:/-)?/wikis/(.+)'
        match = re.search(exp, req.full_url)
        super().__init__(request.Request(
            'https://{0}/api/v4/projects/{1}/wikis/{2}'.format(
                match.group(1),
                match.group(2).replace('/', '%2F'),  # noqa: WPS323
                match.group(3).replace('/', '%2F'),  # noqa: WPS323
            ),
        ))

    def load(self, path: str = '') -> str:
        """
        Load content from the GitLab wiki URL or path.

        Parameters:
            path: Path to append to the URL. Default is ''.

        Returns:
            Content from the URL.

        Raises:
            ValueError: If JSON content cannot be parsed.
        """
        res = super().load(path)
        try:
            return json.loads(res)['content']
        except (TypeError, json.JSONDecodeError, KeyError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))


class GitRepositoryLoader(Loader):
    """Loader for generic Git repository URLs."""

    def load(self, path: str = '') -> str:
        """
        Load content from a Git repo by cloning and reading the file.

        Parameters:
            path: Path of the file to read in the repo. Default is ''.

        Returns:
            Content of the file.

        Raises:
            ValueError: If repo cannot be cloned or file not found.
        """
        tmpdir = TemporaryDirectory().name
        cmd = ['git', 'clone', '--depth', '1', self.req.full_url, tmpdir]
        try:
            subprocess.check_output(  # noqa: S603
                cmd, stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as clone_error:
            raise ValueError("Failed to clone '{0}':\n{1}".format(
                self.req.full_url, clone_error,
            ))
        try:
            with open(os.path.join(tmpdir, path), 'r') as repository_file:
                return repository_file.read()
        except FileNotFoundError as file_error:
            raise ValueError("File '{0}' not found in '{1}':\n{2}".format(
                path, self.req.full_url, file_error,
            ))
