# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test cases for license functionality."""

import json
import pytest
from pydantic import ValidationError
from license import License, SpdxLicenseList


class TestLicense:
    """Test cases for License class."""

    def test_license_creation(self):
        """Test creating a valid License."""
        license_data = License(
            id="BSD-3-Clause",
            name="BSD 3-Clause License",
            url="https://opensource.org/licenses/BSD-3-Clause"
        )
        assert license_data.id == "BSD-3-Clause"
        assert license_data.name == "BSD 3-Clause License"
        url = "https://opensource.org/licenses/BSD-3-Clause"
        assert license_data.url == url

    @pytest.mark.parametrize("license_id,name,url", [
        ("", "Sample", "https://sample.com"),
        ("SAMPLE", "", "https://sample.com"),
        ("SAMPLE", "Sample", ""),
        (" ", "Sample", "https://sample.com"),
    ])
    def test_invalid_license_creation(self, license_id, name, url):
        """Test creating invalid License objects."""
        with pytest.raises(ValidationError):
            License(id=license_id, name=name, url=url)


class TestSpdxLicenseList:
    """Test cases for SpdxLicenseList class."""

    @pytest.fixture(autouse=True)
    def clear_license_list(self):
        """Clear the license list before each test."""
        SpdxLicenseList._spdx_license_list = []

    @pytest.mark.parametrize("json_input,expected_count,expected_id", [
        (
            json.dumps({
                "licenses": [{
                    "licenseId": "GPL-3.0",
                    "name": "GPL 3.0",
                    "reference": "https://gnu.org/licenses/gpl-3.0"
                }]
            }),
            1,
            "GPL-3.0"
        ),
        (
            json.dumps({
                "licenses": [{
                    "licenseId": "MIT",
                    "name": "MIT License",
                    "reference": "https://opensource.org/licenses/MIT"
                }]
            }),
            1,
            "MIT"
        ),
    ])
    def test_from_json(self, json_input, expected_count, expected_id):
        """Test loading licenses from JSON."""
        SpdxLicenseList.from_json(json_input)
        assert len(SpdxLicenseList._spdx_license_list) == expected_count
        assert SpdxLicenseList._spdx_license_list[0].id == expected_id

    @pytest.mark.parametrize("json_input,expected_exception", [
        ("invalid json", ValueError),
        ('{"licenses": "not array"}', TypeError),
    ])
    def test_from_json_errors(self, json_input, expected_exception):
        """Test JSON loading error cases."""
        with pytest.raises(expected_exception):
            SpdxLicenseList.from_json(json_input)

    def test_from_file(self, tmp_path):
        """Test loading licenses from file."""
        file_path = tmp_path / "licenses.json"
        file_path.write_text(json.dumps({
            "licenses": [{
                "licenseId": "Apache-2.0",
                "name": "Apache License",
                "reference": "https://opensource.org/licenses/Apache-2.0"
            }]
        }))
        SpdxLicenseList.from_file(str(file_path))
        assert len(SpdxLicenseList._spdx_license_list) == 1

    @pytest.mark.parametrize("license_id,should_exist", [
        ("Apache-2.0", True),
        ("MISSING", False),
    ])
    def test_get_license(self, license_id, should_exist):
        """Test license retrieval."""
        SpdxLicenseList._spdx_license_list = [
            self._create_license("Apache-2.0")
        ]
        if should_exist:
            license_data = SpdxLicenseList.get_license(license_id)
            assert license_data.id == license_id
        else:
            with pytest.raises(ValueError) as excinfo:
                SpdxLicenseList.get_license(license_id)
            assert "Unknown SPDX identifier" in str(excinfo.value)

    def _create_license(self, license_id):
        """Helper to create test license."""
        return License(
            id=license_id,
            name="{0} License".format(license_id),
            url="https://opensource.org/licenses/{0}".format(license_id)
        )
