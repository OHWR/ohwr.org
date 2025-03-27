# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test cases for repository module."""

import json
import re
import pytest
from urllib.parse import quote
from repository import Repository, GitHubRepository, GitLabRepository

TEST_GITHUB_URL = "https://github.com/owner/repo.git"
TEST_GITLAB_URL = "https://gitlab.com/group/subgroup/repo.git"
TEST_OHWR_URL = "https://ohwr.org/project/repo.git"
TEST_CERN_URL = "https://gitlab.cern.ch/group/repo.git"
TEST_INVALID_URL = "https://unsupported.com/repo.git"
TEST_FILE_PATH = "path/to/file.txt"
TEST_FILE_CONTENT = "file content"
TEST_DEFAULT_BRANCH = "main"
MOCK_GET_PATH = "repository.Repository._get"


class TestRepository:
    """Test the base Repository class functionality."""

    @pytest.mark.parametrize(
        "url,expected_type",
        [
            (TEST_GITHUB_URL, GitHubRepository),
            (TEST_GITLAB_URL, GitLabRepository),
            (TEST_OHWR_URL, GitLabRepository),
            (TEST_CERN_URL, GitLabRepository),
        ],
    )
    def test_create_valid_repositories(self, url, expected_type):
        """Test repository creation with valid URLs."""
        repository = Repository.create(url)
        assert isinstance(repository, expected_type)
        assert repository.url == url

    def test_create_invalid_repository(self):
        """Test repository creation with invalid URL."""
        with pytest.raises(ValueError) as excinfo:
            Repository.create(TEST_INVALID_URL)
        assert "Unsupported repository URL" in str(excinfo.value)

    @pytest.mark.parametrize(
        "input_value",
        [TEST_GITHUB_URL, GitHubRepository(TEST_GITHUB_URL)],
    )
    def test_validate_valid_input(self, input_value):
        """Test _validate with valid input."""
        validated = Repository._validate(input_value)
        assert isinstance(validated, GitHubRepository)
        assert validated.url == TEST_GITHUB_URL

    def test_validate_invalid_input(self):
        """Test _validate with invalid input."""
        invalid_input = 123
        with pytest.raises(ValueError) as excinfo:
            Repository._validate(invalid_input)
        assert "Invalid value" in str(excinfo.value)


class TestGitHubRepository:
    """Test GitHubRepository functionality."""

    def test_fetch_file(self, mocker):
        """Test fetching a file from GitHub."""
        mock_get = mocker.patch(MOCK_GET_PATH)
        mock_response = mocker.Mock()
        mock_response.text = TEST_FILE_CONTENT
        mock_get.return_value = mock_response

        repo = GitHubRepository(TEST_GITHUB_URL)
        file_content = repo.fetch(TEST_FILE_PATH)

        expected_url = "https://api.github.com/repos/owner/repo/contents/{0}" \
            .format(TEST_FILE_PATH)
        mock_get.assert_called_once_with(
            expected_url,
            headers={"Accept": "application/vnd.github.v3.raw"},
        )
        assert file_content == TEST_FILE_CONTENT


class TestGitLabRepository:
    """Test GitLabRepository functionality."""
    @pytest.mark.parametrize(
        "repo_url",
        [TEST_GITLAB_URL, TEST_OHWR_URL, TEST_CERN_URL],
    )
    def test_fetch_file(self, mocker, repo_url):
        """Test fetching a file from GitLab instances."""
        mock_get = self._setup_mocks(mocker)
        repository = GitLabRepository(repo_url)
        project_url, file_url = self._get_expected_urls(repo_url)
        file_content = repository.fetch(TEST_FILE_PATH)

        assert mock_get.call_count == 2
        mock_get.assert_any_call(project_url)
        mock_get.assert_any_call(file_url)
        assert file_content == TEST_FILE_CONTENT

    def test_fetch_file_json_error(self, mocker):
        """Test handling of JSON decode errors."""
        mock_get = mocker.patch(MOCK_GET_PATH)
        mock_response = mocker.Mock()
        mock_response.json.side_effect = json.JSONDecodeError(
            "Error", "doc", 0
        )
        mock_get.return_value = mock_response

        repository = GitLabRepository(TEST_GITLAB_URL)
        with pytest.raises(ValueError) as excinfo:
            repository.fetch(TEST_FILE_PATH)
        assert "Failed to load JSON" in str(excinfo.value)

    def test_fetch_file_missing_branch(self, mocker):
        """Test handling of missing default branch."""
        mock_get = mocker.patch(MOCK_GET_PATH)
        mock_response = mocker.Mock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        repository = GitLabRepository(TEST_GITLAB_URL)
        with pytest.raises(ValueError) as excinfo:
            repository.fetch(TEST_FILE_PATH)
        assert "Failed to load JSON" in str(excinfo.value)

    def _get_expected_urls(self, repo_url):
        """Generate expected URLs for GitLab API calls."""
        match = re.search(r"^https://([^/]+)/(.+?)\.git", repo_url)
        base_url = "https://{0}".format(match.group(1))
        path = match.group(2)

        return (
            "{0}/api/v4/projects/{1}".format(base_url, quote(path, safe="")),
            "{0}/{1}/-/raw/{2}/{3}".format(
                base_url, path, TEST_DEFAULT_BRANCH, TEST_FILE_PATH
            )
        )

    def _setup_mocks(self, mocker):
        """Setup common mock objects for GitLab tests."""
        mock_get = mocker.patch(MOCK_GET_PATH)
        project_response = mocker.Mock()
        project_response.json.return_value = {
            "default_branch": TEST_DEFAULT_BRANCH
        }
        file_response = mocker.Mock()
        file_response.text = TEST_FILE_CONTENT
        mock_get.side_effect = [project_response, file_response]
        return mock_get
