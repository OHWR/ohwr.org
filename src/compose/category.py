# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate categories content."""

import logging
import os
from collections import UserDict

from config import Category as Config

from hugo import Page


class Category(Page):
    """Category Hugo page."""

    @classmethod
    def from_config(cls, config: Config) -> 'Category':
        """
        Create a category page from a configuration.

        Parameters:
            config: Category configuration.

        Returns:
            Category: Instance of Category class.
        """
        front_matter = {'title': config.name}
        return cls(front_matter=front_matter, markdown=config.description)


class CategorySection(UserDict[str, Category]):
    """Category Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Config]) -> 'CategorySection':
        """
        Create a categories section from a list of configurations.

        Parameters:
            configs: Category configurations.

        Returns:
            CategorySection: Instance of CategorySection class.

        Raises:
            ValueError: If creating the categories section fails.
        """
        categories = {}
        for config in configs:
            section = config.name.lower().replace(' ', '-')
            logging.info("Generating '{0}' page...".format(section))
            try:
                category = Category.from_config(config)
            except ValueError as category_error:
                raise ValueError("Failed to generate '{0}' page:\n{1}".format(
                    section, category_error,
                ))
            categories[section] = category
        return cls(categories)

    def write(self, path: str) -> None:
        """
        Write the categories section to files.

        Parameters:
            path: Categories content directory path.

        Raises:
            ValueError: If writing the categories section to files fails.
        """
        for section, category in self.data.items():
            logging.info("Writing '{0}' page...".format(section))
            category_dir = os.path.join(path, section)
            try:
                os.makedirs(category_dir)
            except OSError as makedirs_error:
                raise ValueError(
                    "Failed to create '{0}' directory:\n{1}".format(
                        category_dir, makedirs_error,
                    ),
                )
            try:
                category.write(os.path.join(category_dir, '_index.md'))
            except ValueError as write_error:
                raise ValueError("Failed to write '{0}' page:\n{1}".format(
                    section, write_error,
                ))
