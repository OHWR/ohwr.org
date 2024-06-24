# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load licenses."""


import json

from pydantic import Field, FilePath, ValidationError, validate_call
from schema import AnnotatedStr, BaseModelForbidExtra, SerializableUrl


class License(BaseModelForbidExtra):
    """License data."""

    id: AnnotatedStr = Field(exclude=True)
    name: AnnotatedStr
    url: SerializableUrl


class SpdxLicenseList:
    """SPDX license list data."""

    _spdx_license_list: list[License] = []

    @classmethod
    @validate_call
    def from_json(cls, licenses_json: AnnotatedStr):
        """
        Load SPDX license list data from JSON.

        Parameters:
            licenses_json: SPDX license list data JSON string.

        Raises:
            ValueError: if JSON is not valid.
        """
        try:
            licenses_data = json.loads(licenses_json)
        except (TypeError, json.JSONDecodeError) as json_error:
            raise ValueError('Failed to load JSON:\n{0}'.format(json_error))
        for license_data in licenses_data['licenses']:
            try:
                license = License(
                    id=license_data['licenseId'],
                    name=license_data['name'],
                    url=license_data['reference'],
                )
            except (ValidationError, KeyError) as license_error:
                raise ValueError('Failed to load license data:\n{0}'.format(
                    license_error,
                ))
            cls._spdx_license_list.append(license)

    @classmethod
    @validate_call
    def from_file(cls, path: FilePath):
        """
        Load SPDX license list data from JSON file.

        Parameters:
            path: SPDX license list data JSON file path.

        Raises:
            ValueError: if file is not valid.
        """
        try:
            with open(path, 'r') as licenses_file:
                cls.from_json(licenses_file.read())
        except (ValueError, FileNotFoundError) as file_error:
            raise ValueError("Failed to load file '{0}':\n{1}".format(
                path, file_error,
            ))

    @classmethod
    @validate_call
    def get_license(cls, license_id: AnnotatedStr) -> License:
        """
        Find license data for an SPDX license identifier.

        Parameters:
            license_id: license identifier string.

        Returns:
            License: The License object.

        Raises:
            ValueError: if no data was found for an SPDX license identifier.
        """
        for license in cls._spdx_license_list:
            if license.id == license_id:
                return license
        raise ValueError("Unknown SPDX identifier '{0}'.".format(license_id))
