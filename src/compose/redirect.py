# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import logging
import os
from collections import UserDict

from config import Redirect as Config

from hugo import Page


class Redirect(Page):
    """Redirect Hugo page."""

    @classmethod
    def from_config(cls, config: Config) -> 'Redirect':
        """
        Create a redirect page from a configuration.

        Parameters:
            config: Redirect configuration.

        Returns:
            Redirect: Instance of Redirect class.
        """
        front_matter = config.model_dump(exclude_none=True)
        front_matter['type'] = 'redirect'
        return cls(front_matter=front_matter, markdown='')


class RedirectSection(UserDict[str, Redirect]):
    """Redirect Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Config]) -> 'RedirectSection':
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
                redirect = Redirect.from_config(config)
            except ValueError as redirect_error:
                logging.error("Failed to generate '{0}' page:\n{1}".format(
                    page, redirect_error,
                ))
                continue
            redirect_section[config.source] = redirect
        return cls(redirect_section)

    def write(self, path: str) -> None:
        """
        Write the redirect section to files.

        Parameters:
            path: Redirects content directory path.
        """
        for section, redirect in self.data.items():
            page = section.split('/')[-1]
            logging.info("Writing '{0}' page...".format(page))
            redirect_dir = os.path.join(path, section)
            try:
                os.makedirs(redirect_dir)
            except OSError as makedirs_error:
                logging.error("Failed to create '{0}' directory:\n{1}".format(
                    redirect_dir, makedirs_error,
                ))
                continue
            try:
                redirect.write(os.path.join(redirect_dir, 'index.md'))
            except ValueError as write_error:
                logging.error("Failed to write '{0}' page:\n{1}".format(
                    page, write_error,
                ))
