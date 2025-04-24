# SPDX-FileCopyrightText: 2025 CERN (home.cern)
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
        front_matter = config.model_dump()
        front_matter['url'] = os.path.join(config.url, 'index.html')
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
        for index, config in enumerate(configs):
            logging.info("Generating '{0}' page...".format(config.url))
            try:
                redirect = RedirectPage.from_config(config)
            except ValueError as redirect_error:
                logging.error("Failed to generate '{0}' page:\n{1}".format(
                    config.url, redirect_error,
                ))
                continue
            redirect_section[str(index)] = redirect
        return cls(redirect_section)
