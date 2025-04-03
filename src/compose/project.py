# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate projects content."""


import logging

from config import Project
from hugo import Page, Section


class ProjectPage(Page):
    """Project Hugo page."""

    @classmethod
    def from_config(cls, config: Project) -> 'Project':
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


class ProjectSection(Section):
    """Projects Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Project]) -> 'ProjectSection':
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
                project = ProjectPage.from_config(config)
            except ValueError as project_error:
                logging.error("Failed to generate '{0}' page:\n{1}".format(
                    config.id, project_error,
                ))
                continue
            projects[config.id] = project
        return cls(projects)
