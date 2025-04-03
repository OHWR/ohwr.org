# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate Hugo content."""

from collections import UserDict
from dataclasses import dataclass
import logging
import os

import yaml


@dataclass
class Page:
    """Hugo page."""

    front_matter: dict
    markdown: str

    def write(self, path: str) -> None:
        """
        Write Hugo page to a file.

        Parameters:
            path: File path.

        Raises:
            ValueError: If writing the Hugo page to a file fails.
        """
        try:
            front_matter = yaml.safe_dump(self.front_matter)
        except yaml.YAMLError as yaml_error:
            raise ValueError(
                'Failed to create YAML front matter:\n{0}'.format(yaml_error),
            )
        page = '---\n{0}---\n{1}'.format(front_matter, self.markdown)
        try:
            with open(path, 'w') as hugo_file:
                hugo_file.write(page)
        except OSError as write_error:
            raise ValueError("Failed to write Hugo page to '{0}':\n{1}".format(
                path, write_error,
            ))


class Section(UserDict[str, Page]):
    """Hugo section."""

    def write(self, path: str) -> None:
        """
        Write the section to files.

        Parameters:
            path: Content directory path.
        """
        for name, page in self.data.items():
            logging.info("Writing '{0}' page...".format(name))
            try:
                page.write(self._page_path(path, name))
            except ValueError as write_error:
                logging.error("Failed to write '{0}' page:\n{1}".format(
                    name, write_error,
                ))

    def _page_path(self, path: str, name: str) -> str:
        """
        Get page path.

        Parameters:
            path: Base path.
            name: Page name.

        Returns:
            Page path.
        """
        return os.path.join(path, '{0}.md'.format(name))
