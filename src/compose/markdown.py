# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Parse Markdown into a tree of sections."""


class Markdown(object):
    """
    Parses Markdown into a tree of sections.

    Attributes:
        markdown (str): The Markdown content.
        sections (list): A list of sections (instances of Markdown).

    Methods:
        find(heading: str): Searches for a section with the specified heading.
    """

    def __init__(self, markdown: str):
        """
        Initialize a Markdown object.

        Args:
            markdown (str): The Markdown content to be parsed.
        """
        self.markdown = markdown.strip()
        self.sections = []
        current_level = None
        lines = []
        for line in self.markdown.splitlines(keepends=True):
            if line.startswith('#'):
                if not current_level:
                    current_level = line.count('#')
                    lines = []
                elif current_level >= line.count('#'):
                    self.sections.append(Section(''.join(lines)))
                    current_level = line.count('#')
                    lines = []
            lines.append(line)
        if current_level:
            self.sections.append(Section(''.join(lines)))

    def find(self, heading: str):
        """
        Recursively searches for a section with the specified heading.

        Args:
            heading (str): The heading to search for.

        Returns:
            The section with the specified heading, or None if not found.
        """
        for section in self.sections:
            found_section = section.find(heading)
            if found_section:
                return found_section
        return None


class Section(Markdown):
    """
    Represents a section of a Markdown document.

    Attributes:
        level (int): The level of the section (determined by the number of
        '#' symbols in the heading).
        heading (str): The heading of the section.

    Methods:
        find(heading: str): Searches for a section with the specified heading.
    """

    def __init__(self, markdown: str):
        """
        Initialize a Section object.

        Args:
            markdown (str): The Markdown content to be parsed.
        """
        partition = markdown.partition('\n')
        self.level = partition[0].count('#')
        self.heading = partition[0].lstrip('#').strip()
        super().__init__(partition[2])

    def find(self, heading: str):
        """
        Recursively searches for a section with the specified heading.

        Args:
            heading (str): The heading to search for.

        Returns:
            The section with the specified heading, or None if not found.
        """
        if self.heading == heading:
            return self
        return super().find(heading)
