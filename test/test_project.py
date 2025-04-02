# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for projects content generation."""

import pytest
import logging

from config import Project
from project import ProjectPage, ProjectSection


PROJ_ID = "test-prj"
BAD_ID = "bad-prj"
INVALID_ID = "invalid-prj"
ID_KEY = "id"


@pytest.fixture
def sample_project_config(mocker):
    """Fixture providing a mocked Project configuration."""
    mock_project = mocker.Mock(spec=Project)
    mock_project.id = PROJ_ID
    mock_project.model_dump.return_value = {
        ID_KEY: PROJ_ID,
        "weight": 1,
        "tags": ["test"]
    }

    mock_manifest = mocker.Mock()
    mock_manifest.model_dump.return_value = {
        "title": "Test Project",
        "description": "Test description"
    }
    mock_manifest.description.text = "# Test Project\n\nProject description"
    mock_project.manifest = mock_manifest

    return mock_project


@pytest.fixture
def sample_project_configs(sample_project_config, mocker):
    """Fixture providing multiple project configs."""
    bad_project = mocker.Mock(spec=Project)
    bad_project.id = BAD_ID
    bad_project.model_dump.return_value = {ID_KEY: BAD_ID}

    bad_manifest = mocker.Mock()
    bad_manifest.model_dump.side_effect = ValueError("Config error")
    bad_project.manifest = bad_manifest

    return [sample_project_config, bad_project]


class TestProjectPage:
    """Tests for ProjectPage class."""

    def test_from_config_success(self, sample_project_config):
        """Test successful project page creation from config."""
        page = ProjectPage.from_config(sample_project_config)

        assert isinstance(page, ProjectPage)
        assert page.front_matter[ID_KEY] == PROJ_ID
        assert "title" in page.front_matter
        assert page.markdown.startswith("# Test Project")

        sample_project_config.model_dump.assert_called_once_with(
            exclude_none=True
        )
        sample_project_config.manifest.model_dump.assert_called_once_with(
            exclude_none=True,
            by_alias=True
        )

    def test_from_config_validation_error(self, mocker):
        """Test handling of validation errors during page creation."""
        mock_project = mocker.Mock(spec=Project)
        mock_project.id = INVALID_ID
        mock_project.model_dump.return_value = {ID_KEY: INVALID_ID}

        mock_manifest = mocker.Mock()
        mock_manifest.model_dump.side_effect = ValueError("Validation failed")
        mock_project.manifest = mock_manifest

        with pytest.raises(ValueError, match="Validation failed"):
            ProjectPage.from_config(mock_project)


class TestProjectSection:
    """Tests for ProjectSection class."""

    def test_from_config_success(self, sample_project_configs, caplog):
        """Test successful section creation from configs."""
        with caplog.at_level(logging.INFO):
            section = ProjectSection.from_config(sample_project_configs)

        log_msg = caplog.text
        expected_logs = (
            f"Generating '{PROJ_ID}' page",
            f"Failed to generate '{BAD_ID}' page",
            "Config error"
        )

        assert len(section) == 1
        assert PROJ_ID in section
        assert BAD_ID not in section
        assert all(msg in log_msg for msg in expected_logs)
