# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import logging
import os

from config import Redirect

from hugo import Page, Section


class RedirectPage(Page):
    """Redirect Hugo page."""

    @classmethod
    def from_config(cls, config: Redirect) -> 'RedirectPage':
        """
        Create a redirect page from a configuration.

        Parameters:
            config: Redirect configuration.

        Returns:
            RedirectPage: Instance of RedirectPage class.
        """
        front_matter = config.model_dump(exclude_none=True)
        front_matter['type'] = 'redirect'
        return cls(front_matter=front_matter, markdown='')


class RedirectSection(Section):
    """Redirect Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Redirect]) -> 'RedirectSection':
        """
        Create a redirect section from a list of configurations.

        Parameters:
            configs: Redirect configurations.

        Returns:
            RedirectSection: Instance of RedirectSection class.
        """
        redirect_section = {}
        for config in configs:
            page = config.source.split('/')[-1]
            logging.info("Generating '{0}' page...".format(page))
            try:
                redirect = RedirectPage.from_config(config)
            except ValueError as redirect_error:
                logging.error("Failed to generate '{0}' page:\n{1}".format(
                    page, redirect_error,
                ))
                continue
            redirect_section[config.source] = redirect
        return cls(redirect_section)

    def _page_path(self, path: str, name: str) -> str:
        """
        Get page path.

        Parameters:
            path: Base path.
            name: Page name.

        Returns:
            Page path.

        Raises:
            ValueError: If creating the directory fails.
        """
        redirect_dir = os.path.join(path, name)
        try:
            os.makedirs(redirect_dir)
        except OSError as makedirs_error:
            raise ValueError("Failed to create '{0}' directory:\n{1}".format(
                redirect_dir, makedirs_error,
            ))
        return os.path.join(redirect_dir, 'index.md')
