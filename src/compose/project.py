# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate projects content."""


import logging
import os
from collections import UserDict

from config import Project as Config

from hugo import Page


class Project(Page):
    """Project Hugo page."""

    @classmethod
    def from_config(cls, config: Config) -> 'Project':
        """
        Create a project page from a configuration.

        Parameters:
            config: Project configuration.

        Returns:
            Project: Instance of Project class.
        """
        front_matter = config.model_dump(exclude_none=True)
        front_matter.update(config.manifest.model_dump(
            exclude_none=True,
            by_alias=True,
        ))
        return cls(front_matter=front_matter, markdown=config.description)


class ProjectSection(UserDict[str, Project]):
    """Projects Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Config]) -> 'ProjectSection':
        """
        Create a projects section from a list of configurations.

        Parameters:
            configs: Project configurations.

        Returns:
            ProjectSection: Instance of ProjectSection class.
        """
        projects = {}
        for config in configs:
            logging.info("Generating '{0}' page...".format(config.id))
            try:
                project = Project.from_config(config)
            except ValueError as project_error:
                logging.error("Failed to generate '{0}' page:\n{1}".format(
                    config.id, project_error,
                ))
                continue
            projects[config.id] = project
        return cls(projects)

    def write(self, path: str) -> None:
        """
        Write the projects section to files.

        Parameters:
            path: Projects content directory path.
        """
        for page, project in self.data.items():
            logging.info("Writing '{0}' page...".format(page))
            try:
                project.write(os.path.join(path, '{0}.md'.format(page)))
            except ValueError as write_error:
                logging.error("Failed to write '{0}' page:\n{1}".format(
                    page, write_error,
                ))
