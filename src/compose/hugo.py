# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate Hugo content."""

from dataclasses import dataclass

import yaml


@dataclass
class Page():
    """Hugo page."""

    front_matter: dict
    markdown: str

    def write(self, path: str):
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
