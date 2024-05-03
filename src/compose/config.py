# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from category import Category
from common import YamlSchema
from project import Project
from pydantic import DirectoryPath, Field, FilePath, model_validator
from typing_extensions import Annotated


class Config(YamlSchema):
    """Configuration schema."""

    sources: DirectoryPath
    licenses: FilePath
    categories: Annotated[list[Category], Field(min_length=1)]
    projects: Annotated[list[Project], Field(min_length=1)]

    @model_validator(mode='after')
    def check_categories_match(self):
        """
        Check if categories in projects match the available categories.

        Returns:
            Config: The configuration object with validated category names.

        Raises:
            ValueError: If an unknown category is found in a project.
        """
        categories = []
        if self.categories:
            for category in self.categories:
                categories.append(category.name)

        for project in self.projects:
            if project.categories:
                unknown = set(project.categories) - set(categories)
                if unknown:
                    raise ValueError(
                        "Project '{0}' with unknown categories: '{1}'.".format(
                            project.repository, unknown,
                        ),
                    )
        return self
