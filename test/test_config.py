# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from datetime import date
from pydantic import ValidationError

from config import Contact, News, Redirect, Config
from manifest import Manifest
from repository import Repository


@pytest.fixture
def valid_markdown():
    return "## Sample News\n2023-01-15\n\nThis is a sample news description."


@pytest.fixture
def dummy_licenses_file(tmp_path):
    """Create a dummy licenses file for testing"""
    licenses_file = tmp_path / "licenses.txt"
    licenses_file.write_text("MIT License")
    return licenses_file


@pytest.fixture
def sample_projects(sample_project):
    return [sample_project]


class TestContact:
    def test_valid_contact(self, sample_contact):
        assert sample_contact.name == "John Doe"
        assert sample_contact.email == "john@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            Contact(name="John Doe", email="invalid-email")


class TestNews:
    def test_from_markdown_valid(self, mocker, valid_markdown):
        mocker.patch('url.StrictUrl._validate', return_value=True)
        news = News.from_markdown(valid_markdown)
        assert news.title == "Sample News"
        assert news.date == date.fromisoformat('2023-01-15')

    def test_missing_date(self):
        md = "## Missing Date\nNo date here"
        with pytest.raises(ValueError) as excinfo:
            News.from_markdown(md)
        assert "Failed to fetch date" in str(excinfo.value)


class TestProject:
    def test_manifest_loading(self, sample_project, mock_repository):
        mock_repository.fetch.return_value = (
            "version: 1.0.0\n"
            "name: Test Project\n"
            "description: https://example/wikis/home\n"
            "licenses: [MIT]\n"
            "website: https://example.com"
        )

        manifest = sample_project.manifest
        assert isinstance(manifest, Manifest)
        assert manifest.name == "Test Project"
        assert manifest.licenses == ["MIT"]
        assert "Example description" in manifest.description.text


class TestConfig:
    def test_valid_config(
        self, mocker, sample_projects, tmp_path, dummy_licenses_file
    ):
        mocker.patch('url.StrictUrl._validate', return_value=True)
        mock_repo = mocker.Mock(spec=Repository)
        mocker.patch('repository.Repository.create', return_value=mock_repo)

        config = Config(
            sources=tmp_path,
            licenses=dummy_licenses_file,
            redirects=[Redirect(
                url="/old",
                target="https://github.com/new"
            )],
            tags=["test-tag"],
            projects=sample_projects
        )

        assert len(config.projects) == 1
        assert config.projects[0].id == "test-project"
        assert config.licenses == dummy_licenses_file
        assert config.redirects[0].url == "/old"
