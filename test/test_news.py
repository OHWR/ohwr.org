# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for news content generation."""

import pytest
import logging

from config import News, Project
from news import NewsPage, NewsSection


NEWS_ID = "test-news"
BAD_NEWS_ID = "bad-news"
PROJ_ID = "test-prj"
BAD_PROJ_ID = "bad-prj"
NEWS_PAGE_FORMAT = "{0}-1"


@pytest.fixture
def sample_news_config(mocker):
    """Fixture providing a mocked News configuration."""
    mock_news = mocker.Mock(spec=News)
    mock_news.model_dump.return_value = {
        "title": "Test News",
        "date": "2024-01-01",
        "description": "Test news description"
    }

    mock_news.description = "Test news description"
    mock_project = mocker.Mock()
    mock_project.id = PROJ_ID
    mock_project.manifest.name = "Test Project"
    mock_news.project = mock_project

    return mock_news


@pytest.fixture
def sample_project_configs(mocker, sample_news_config):
    """Fixture providing multiple project configs with news."""
    good_project = mocker.Mock(spec=Project)
    good_project.id = PROJ_ID
    good_project.news = [sample_news_config]

    bad_news_project = mocker.Mock(spec=Project)
    bad_news_project.id = BAD_PROJ_ID

    bad_news = mocker.Mock(spec=News)
    bad_news.description = "Bad news description"
    bad_project_mock = mocker.Mock()
    bad_project_mock.id = BAD_PROJ_ID
    bad_news.project = bad_project_mock
    bad_news.model_dump.side_effect = ValueError("News dump error")
    bad_news_project.news = [bad_news]

    bad_project = mocker.Mock(spec=Project)
    bad_project.id = "no-news-prj"
    type(bad_project).news = mocker.PropertyMock(
        side_effect=ValueError("Failed to get news")
    )

    return [good_project, bad_news_project, bad_project]


class TestNewsPage:
    """Tests for NewsPage class."""

    def test_from_config_success(self, sample_news_config):
        """Test successful news page creation from config."""
        page = NewsPage.from_config(sample_news_config)

        assert isinstance(page, NewsPage)
        assert page.front_matter["title"] == "Test News"
        assert page.front_matter["project"] == "Test Project"
        assert page.markdown == "Test news description"

        sample_news_config.model_dump.assert_called_once_with(
            exclude_none=True
        )

    def test_from_config_validation_error(self, mocker):
        """Test handling of validation errors during page creation."""
        mock_news = mocker.Mock(spec=News)
        mock_news.description = "Test description"
        mock_news.project = mocker.Mock()
        mock_news.model_dump.side_effect = ValueError("Validation failed")

        with pytest.raises(ValueError, match="Validation failed"):
            NewsPage.from_config(mock_news)


class TestNewsSection:
    """Tests for NewsSection class."""

    def test_from_config_success(self, sample_project_configs, caplog):
        """Test successful section creation from configs."""
        with caplog.at_level(logging.INFO):
            section = NewsSection.from_config(sample_project_configs)

        log_msg = caplog.text
        expected_logs = (
            "Generating '{0}' page".format(NEWS_PAGE_FORMAT.format(PROJ_ID)),
            "Failed to generate '{0}' page".format(
                NEWS_PAGE_FORMAT.format(BAD_PROJ_ID)
            ),
            "News dump error",
            "Failed to get news from 'no-news-prj'"
        )

        assert len(section) == 1
        assert NEWS_PAGE_FORMAT.format(PROJ_ID) in section
        assert NEWS_PAGE_FORMAT.format(BAD_PROJ_ID) not in section
        assert all(msg in log_msg for msg in expected_logs)

    def test_from_config_success_internal(self, sample_news_config):
        """Test successful _from_config method."""
        news_list = [sample_news_config]
        section = NewsSection._from_config(news_list)

        assert len(section) == 1
        assert NEWS_PAGE_FORMAT.format(PROJ_ID) in section
        assert isinstance(section[NEWS_PAGE_FORMAT.format(PROJ_ID)], NewsPage)
