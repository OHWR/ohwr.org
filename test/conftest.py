# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from config import Contact, Project
from repository import Repository
from url import StrictUrl


@pytest.fixture(autouse=True)
def mock_requests(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "# Description\n\nExample description"
    mocker.patch('requests.head', return_value=mock_response)
    mocker.patch('requests.get', return_value=mock_response)
    return mock_response


@pytest.fixture
def sample_contact():
    return Contact(name="John Doe", email="john@example.com")


@pytest.fixture
def mock_repository(mocker):
    mock = mocker.Mock(spec=Repository)
    mock.url = StrictUrl("https://github.com/example/repo.git")
    return mock


@pytest.fixture
def sample_project(mocker, sample_contact, mock_repository):
    mocker.patch('repository.Repository.create', return_value=mock_repository)
    return Project(
        id="test-project",
        repository="https://github.com/example/repo.git",
        contact=sample_contact
    )
