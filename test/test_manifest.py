# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest
from pydantic import ValidationError
from typing import Dict, Any
from manifest import Manifest, Link


VERSION = "1.0.0"
PROJ_NAME = "Test Project"
DESC_URL = "https://example.com/description.md"
SITE_URL = "https://example.com"
REPO_NAME = "GitHub"
REPO_URL = "https://github.com/example"


@pytest.fixture
def minimal_manifest_data() -> Dict[str, Any]:
    """Fixture providing minimal manifest data."""
    return {
        "version": VERSION,
        "name": PROJ_NAME,
        "description": DESC_URL,
        "website": SITE_URL,
    }


@pytest.fixture
def valid_manifest_data(minimal_manifest_data) -> Dict[str, Any]:
    """Fixture providing valid manifest data."""
    return {
        **minimal_manifest_data,
        "licenses": ("BSD-3-Clause",),
        "images": ("https://example.com/image1.png",),
        "documentation": "https://example.com/docs",
        "issues": "https://example.com/issues",
        "latest_release": "https://example.com/release",
        "forum": "https://example.com/forum",
        "newsfeed": "https://example.com/news.rss",
        "links": ({"name": REPO_NAME, "url": REPO_URL},),
    }


@pytest.fixture
def mock_requests(mocker):
    """Fixture to mock all requests."""
    mock_head = mocker.patch("manifest.Url._head")
    mock_head.return_value.status_code = 200
    mock_head.return_value.raise_for_status.return_value = None

    mock_get = mocker.patch("manifest.Url._get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Sample content"
    mock_get.return_value.json.return_value = {"content": "Wiki content"}
    mock_get.return_value.headers = {"Content-Type": "text/plain"}
    mock_get.return_value.raise_for_status.return_value = None

    return mock_head, mock_get


class TestManifest:
    """Tests for manifest model."""
    def test_version_and_name(self, minimal_manifest_data, mock_requests):
        manifest = Manifest(**minimal_manifest_data)
        assert manifest.version == VERSION
        assert manifest.name == PROJ_NAME

    def test_licenses_and_links(self, valid_manifest_data, mock_requests):
        manifest = Manifest(**valid_manifest_data)
        assert manifest.licenses[0] == "BSD-3-Clause"
        assert len(manifest.links) == 1
        assert manifest.links[0].name == REPO_NAME
        assert manifest.links[0].url.url == REPO_URL

    def test_images(self, valid_manifest_data, mock_requests):
        manifest = Manifest(**valid_manifest_data)
        assert len(manifest.images) == 1

    def test_invalid_version(self, valid_manifest_data, mock_requests):
        test_data = dict(valid_manifest_data, version="2.0.0")
        with pytest.raises(ValidationError):
            Manifest(**test_data)

    def test_missing_required_fields(
            self, minimal_manifest_data, mock_requests
    ):
        fields = ("version", "name", "description", "website")
        for field in fields:
            test_data = dict(minimal_manifest_data)
            test_data.pop(field)
            with pytest.raises(ValidationError):
                Manifest(**test_data)

    def test_failed_url_validation(self, valid_manifest_data, mock_requests):
        mock_head, _ = mock_requests
        mock_head.side_effect = ValueError(
            "URL validation failed: 404 Not Found"
        )
        try:
            Manifest(**valid_manifest_data)
        except ValidationError as err:
            msgs = [str(msg["msg"]) for msg in err.errors()]
            assert any("URL validation failed" in msg for msg in msgs)
        else:
            pytest.fail("Expected ValidationError not raised")

    def test_serialization(self, valid_manifest_data, mock_requests):
        manifest = Manifest(**valid_manifest_data)
        serialized = manifest.model_dump(by_alias=True)
        missing = ["version", "description", "licenses"]

        assert serialized["title"] == PROJ_NAME
        assert serialized["website"] == SITE_URL
        for field in missing:
            assert field not in serialized


class TestLink:
    """Tests for Link model."""

    def test_valid_link(self, mock_requests):
        link = Link(name=REPO_NAME, url="https://github.com")
        assert link.name == REPO_NAME
        assert link.url.url == "https://github.com"

    def test_missing_fields(self, mock_requests):
        with pytest.raises(ValidationError):
            Link(name="Missing URL")
        with pytest.raises(ValidationError):
            Link(url="https://example.com")

    def test_failed_url_validation(self, mock_requests):
        mock_head, _ = mock_requests
        mock_head.side_effect = ValueError(
            "URL validation failed: 404 Not Found"
        )
        try:
            Link(name="Bad URL", url="https://invalid-url.com")
        except ValidationError as err:
            msgs = [str(msg["msg"]) for msg in err.errors()]
            assert any("URL validation failed" in msg for msg in msgs)
        else:
            pytest.fail("Expected ValidationError not raised")
