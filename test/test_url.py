# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest
import json
from requests.exceptions import RequestException
from pydantic import BaseModel, ValidationError
from url import (
    StrictUrl,
    UrlContent,
    GitLabWikiPage,
    GenericUrlContent,
    StrictUrlList
)


EXAMPLE_URL = "http://example.com"
EXAMPLE_ORG_URL = "http://example.org"
GITLAB_URL = "https://gitlab.com/project/wiki/page"
GITLAB_DOMAIN = "gitlab.com"
PAGE_NAME = "page"
PROJECT_NAME = "project"
CONTENT_TEXT = "content"
REQUESTS_HEAD = "requests.head"
REQUESTS_GET = "requests.get"
RE_SEARCH = "re.search"


class StrictUrlListTestModel(BaseModel):
    """Test model for StrictUrlList validation."""
    urls: StrictUrlList


class TestStrictUrl:
    """Test the StrictUrl class functionality."""

    def test_url_validation_success(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mocker.patch(REQUESTS_HEAD, return_value=mock_response)

        url = StrictUrl._validate(EXAMPLE_URL)
        assert url.url == EXAMPLE_URL

    def test_url_validation_failure(self, mocker):
        mocker.patch(
            REQUESTS_HEAD,
            side_effect=RequestException("Connection error")
        )

        with pytest.raises(ValueError):
            StrictUrl._validate("http://invalid.com")

    def test_url_serialization(self):
        url_obj = StrictUrl(EXAMPLE_URL)
        assert StrictUrl._serialize(url_obj) == EXAMPLE_URL

    def test_url_get_success(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mocker.patch(REQUESTS_GET, return_value=mock_response)

        response = StrictUrl._get(EXAMPLE_URL)
        assert response == mock_response

    def test_url_get_failure(self, mocker):
        mocker.patch(REQUESTS_GET, side_effect=RequestException("GET error"))

        with pytest.raises(ValueError):
            StrictUrl._get("http://invalid.com")


class TestUrlContent:
    """Test the UrlContent abstract class and its implementations."""

    def test_generic_url_content(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "Sample content"
        mocker.patch(REQUESTS_GET, return_value=mock_response)

        content_obj = GenericUrlContent.from_url(EXAMPLE_URL)
        assert content_obj.url == EXAMPLE_URL
        assert content_obj.text == "Sample content"

    def test_gitlab_wiki_content(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"content": "Wiki content"}
        mocker.patch(REQUESTS_GET, return_value=mock_response)

        mock_match = mocker.Mock()
        mock_match.group.side_effect = [GITLAB_DOMAIN, PROJECT_NAME, PAGE_NAME]
        mocker.patch(RE_SEARCH, return_value=mock_match)

        wiki_content = GitLabWikiPage.from_url(GITLAB_URL)
        assert "api/v4/projects" in wiki_content.url
        assert wiki_content.text == "Wiki content"

    def test_gitlab_wiki_invalid_json(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError(
            "Invalid", "doc", 1
        )
        mocker.patch(REQUESTS_GET, return_value=mock_response)

        mock_match = mocker.Mock()
        mock_match.group.side_effect = [GITLAB_DOMAIN, PROJECT_NAME, PAGE_NAME]
        mocker.patch(RE_SEARCH, return_value=mock_match)

        with pytest.raises(ValueError):
            GitLabWikiPage.from_url(GITLAB_URL)

    def test_url_content_create_generic(self, mocker):
        mock_content = GenericUrlContent(EXAMPLE_URL, CONTENT_TEXT)
        mocker.patch.object(
            GenericUrlContent,
            'from_url',
            return_value=mock_content
        )

        result_obj = UrlContent.create(EXAMPLE_URL)
        assert result_obj == mock_content

    def test_url_content_create_gitlab(self, mocker):
        expected_url = "https://gitlab.com/api/v4/projects/project/wikis/page"

        mock_match = mocker.Mock()
        mock_match.group.side_effect = [GITLAB_DOMAIN, PROJECT_NAME, PAGE_NAME]
        mocker.patch(RE_SEARCH, return_value=mock_match)

        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"content": "wiki content"}
        mocker.patch(REQUESTS_GET, return_value=mock_response)

        mocker.patch('url.StrictUrl._get', return_value=mock_response)

        result_obj = UrlContent.create(GITLAB_URL)

        assert isinstance(result_obj, GitLabWikiPage)
        assert result_obj.url == expected_url
        assert result_obj.text == "wiki content"

    def test_url_content_validation(self, mocker):
        mock_content = GenericUrlContent(EXAMPLE_URL, CONTENT_TEXT)
        mocker.patch.object(UrlContent, 'create', return_value=mock_content)

        assert UrlContent._validate(EXAMPLE_URL) == mock_content
        assert UrlContent._validate(mock_content) == mock_content

        invalid_value = 123
        with pytest.raises(ValueError):
            UrlContent._validate(invalid_value)


class TestStrictUrlList:
    """Test the StrictUrlList type."""

    def test_urllist_validation_success(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mocker.patch(REQUESTS_HEAD, return_value=mock_response)

        model = StrictUrlListTestModel(urls=[EXAMPLE_URL])
        assert len(model.urls) == 1
        assert isinstance(model.urls[0], StrictUrl)
        assert model.urls[0].url == EXAMPLE_URL

        model = StrictUrlListTestModel(urls=[EXAMPLE_URL, EXAMPLE_ORG_URL])
        assert len(model.urls) == 2
        assert all(isinstance(url, StrictUrl) for url in model.urls)

    def test_urllist_validation_failure(self, mocker):
        with pytest.raises(ValidationError) as exc_info:
            StrictUrlListTestModel(urls=[])
        assert "too_short" in str(exc_info.value)

        mocker.patch(
            REQUESTS_HEAD,
            side_effect=RequestException("Connection error")
        )
        with pytest.raises(ValidationError) as exc_info:
            StrictUrlListTestModel(urls=["http://invalid.com"])
        assert "validation" in str(exc_info.value)

    def test_urllist_with_existing_url_objects(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mocker.patch(REQUESTS_HEAD, return_value=mock_response)

        url1 = StrictUrl(EXAMPLE_URL).url
        url2 = StrictUrl(EXAMPLE_ORG_URL).url

        model = StrictUrlListTestModel(urls=[url1, url2])
        assert len(model.urls) == 2
        assert all(isinstance(url, StrictUrl) for url in model.urls)

    def test_urllist_serialization(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mocker.patch(REQUESTS_HEAD, return_value=mock_response)

        model = StrictUrlListTestModel(urls=[EXAMPLE_URL, EXAMPLE_ORG_URL])
        json_data = model.model_dump_json()
        loaded_model = StrictUrlListTestModel.model_validate_json(json_data)

        assert len(loaded_model.urls) == 2
        assert loaded_model.urls[0].url == EXAMPLE_URL
        assert loaded_model.urls[1].url == EXAMPLE_ORG_URL


@pytest.mark.parametrize("test_url,expected_type", [
    (EXAMPLE_URL, GenericUrlContent),
    (GITLAB_URL, GitLabWikiPage),
])
def test_url_content_factory(test_url, expected_type, mocker):
    """Test the URL content factory creates the right type."""
    if expected_type == GitLabWikiPage:
        mock_return = GitLabWikiPage(test_url, "wiki content")
        mock_match = mocker.Mock()
        mock_match.group.side_effect = [GITLAB_DOMAIN, "proj", PAGE_NAME]
        mocker.patch(RE_SEARCH, return_value=mock_match)
    else:
        mock_return = GenericUrlContent(test_url, CONTENT_TEXT)

    mocker.patch.object(expected_type, 'from_url', return_value=mock_return)
    mocker.patch(REQUESTS_GET, return_value=mocker.Mock(text=CONTENT_TEXT))

    result_obj = UrlContent.create(test_url)
    assert isinstance(result_obj, expected_type)
