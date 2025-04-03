# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for Hugo content generation."""

import pytest
import yaml
from hugo import Page, Section


@pytest.fixture
def sample_page():
    """Fixture providing a sample Page instance."""
    return Page(
        front_matter={"title": "Test Page", "date": "2025-01-01"},
        markdown="# Test Page\n\nThis is a test page."
    )


@pytest.fixture
def sample_section(sample_page):
    """Fixture providing a sample Section instance with pages."""
    section = Section()
    section["page1"] = sample_page
    section["page2"] = Page(
        front_matter={"title": "Another Page"},
        markdown="## Another Page\n\nMore content."
    )
    return section


class TestPage:
    """Tests for the Page class."""

    def test_write_success(self, sample_page, mocker):
        """Test successful page writing with mocked file operations."""
        mock_file = mocker.patch("builtins.open", mocker.mock_open())
        mock_yaml_dump = mocker.patch(
            "yaml.safe_dump",
            return_value="yaml_output"
        )

        sample_page.write("test_path.md")

        mock_yaml_dump.assert_called_once_with(sample_page.front_matter)
        mock_file.assert_called_once_with("test_path.md", 'w')
        file_handle = mock_file()
        expected_content = (
            "---\nyaml_output---\n# Test Page\n\nThis is a test page."
        )
        file_handle.write.assert_called_once_with(expected_content)

    def test_write_invalid_front_matter(self, mocker):
        """Test writing with invalid front matter."""
        page = Page(
            front_matter={"invalid": object()},
            markdown="content"
        )
        mocker.patch(
            "yaml.safe_dump",
            side_effect=yaml.YAMLError("YAML error")
        )

        with pytest.raises(ValueError, match="Failed to create YAML"):
            page.write("dummy_path.md")

    def test_write_io_error(self, sample_page, mocker):
        """Test handling of IO errors during file writing."""
        mocker.patch("builtins.open", side_effect=OSError("Disk error"))

        with pytest.raises(ValueError, match="Failed to write Hugo page"):
            sample_page.write("/invalid/path/test.md")


class TestSection:
    """Tests for the Section class."""

    def test_write_success(self, sample_section, mocker):
        """Test successful section writing with mocked page writes."""
        mock_write = mocker.patch.object(Page, 'write')
        sample_section.write("/content/dir")

        assert mock_write.call_count == 2
        mock_write.assert_any_call("/content/dir/page1.md")
        mock_write.assert_any_call("/content/dir/page2.md")

    def test_write_with_failing_page(self, sample_section, mocker, caplog):
        """Test section writing when one page fails."""
        sample_section["bad_page"] = Page(
            front_matter={"title": "Bad Page"},
            markdown="content"
        )
        mocker.patch.object(Page, 'write', side_effect=ValueError("Disk full"))
        sample_section.write("/content/dir")

        assert "Failed to write 'bad_page' page" in caplog.text
        assert "Disk full" in caplog.text

    def test_page_path(self, sample_section):
        """Test the _page_path helper method."""
        path = sample_section._page_path("/content/dir", "test_page")
        assert path == "/content/dir/test_page.md"
