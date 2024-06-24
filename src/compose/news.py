# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import logging
import os
from collections import UserDict

from config import News as Config
from config import Project

from hugo import Page


class News(Page):
    """News Hugo page."""

    @classmethod
    def from_config(cls, config: Config, project_id: str) -> 'News':
        """
        Create a news page from a configuration.

        Parameters:
            config: News configuration.
            project_id: Project identifier.

        Returns:
            News: Instance of News class.
        """
        front_matter = config.model_dump(exclude_none=True)
        front_matter['newsfeeds'] = [project_id]
        return cls(front_matter=front_matter, markdown=config.description)


class NewsSection(UserDict[str, News]):
    """News Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Project]) -> 'NewsSection':
        """
        Create a news section from a list of configurations.

        Parameters:
            configs: Project configurations.

        Returns:
            NewsSection: Instance of NewsSection class.
        """
        news_section = {}
        for project in configs:
            for index, config in enumerate(project.news):
                page = '{0}-{1}'.format(project.id, index + 1)
                logging.info("Generating '{0}' page...".format(page))
                try:
                    news_section[page] = News.from_config(config, project.id)
                except ValueError as news_error:
                    logging.error("Failed to generate '{0}' page:\n{1}".format(
                        page, news_error,
                    ))
        return cls(news_section)

    def write(self, path: str) -> None:
        """
        Write the news section to files.

        Parameters:
            path: news content directory path.

        Raises:
            ValueError: If writing the news section to files fails.
        """
        try:
            os.makedirs(path)
        except OSError as makedirs_error:
            raise ValueError("Failed to create '{0}' directory:\n{1}".format(
                path, makedirs_error,
            ))
        for page, news in self.data.items():
            logging.info("Writing '{0}' page...".format(page))
            try:
                news.write(os.path.join(path, '{0}.md'.format(page)))
            except ValueError as write_error:
                logging.error("Failed to write '{0}' page:\n{1}".format(
                    page, write_error,
                ))
