# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Project category utilities."""


import logging
import os

from common import AnnotatedStr, BaseModelForbidExtra
from pydantic import DirectoryPath, validate_call


class Category(BaseModelForbidExtra):
    """Project category."""

    name: AnnotatedStr
    description: AnnotatedStr

    @validate_call
    def hugo(self) -> str:
        """
        Generate Hugo content.

        Returns:
            str: Hugo content string.
        """
        return '---\ntitle: {0}\n---\n{1}'.format(self.name, self.description)

    @validate_call
    def dump(self, sources: DirectoryPath):
        """
        Dump Hugo content.

        Parameters:
            sources: Hugo sources directory path.

        Raises:
            ValueError: if dumping the Hugo content fails.
        """
        category_dir = os.path.join(
            sources, 'content/categories', self.name.lower().replace(' ', '-'),
        )
        try:
            os.makedirs(category_dir)
        except OSError as makedirs_error:
            raise ValueError("Failed to create '{0}' directory:\n{1}".format(
                category_dir, makedirs_error,
            ))
        path = os.path.join(category_dir, '_index.md')
        logging.info("{0} - Writing category page to '{1}'...".format(
            self.name, path,
        ))
        hugo_content = self.hugo()
        try:
            with open(path, 'w') as category_file:
                category_file.write(hugo_content)
        except OSError as open_error:
            raise ValueError("Failed to write file '{0}':\n{1}".format(
                path, open_error,
            ))
