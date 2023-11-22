# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Write Hugo data and content files."""

import os
import subprocess  # noqa: S404
from dataclasses import dataclass, field
from logging import info

import yaml
from config import NewsConfig, ProjConfig


@dataclass
class Sources(object):
    """Base class to write Hugo data and content file."""

    data_path: str
    content_path: str
    data_dict: dict
    sources: list = field(default_factory=list)

    def dump(self, source: str):
        """
        Write Hugo data file and generate the corresponding content file.

        Parameters:
            source: Hugo source directory.
        """
        data_dir = os.path.dirname(self.data_path)
        os.makedirs(os.path.join(source, data_dir), exist_ok=True)
        data_full_path = os.path.abspath(os.path.join(source, self.data_path))
        with open(data_full_path, 'w') as data_file:
            yaml.safe_dump(self.data_dict, data_file)
        info('Data "{0}" created'.format(data_full_path))
        output = subprocess.check_output(
            'hugo new {0} -s {1} -f'.format(self.content_path, source),
            shell=True,  # noqa: S602
        )
        info(output.decode().strip())
        for sources in self.sources:
            sources.dump(source)


class ProjSources(Sources):
    """Writes Hugo data and content file for a project page."""

    @classmethod
    def from_config(cls, config: ProjConfig):
        """
        Construct a ProjSources object from the configuration.

        Parameters:
            config: project configuration.

        Returns:
            ProjSources object.
        """
        sources = []
        for index, news in enumerate(config.news):
            news.topics.insert(0, config.name)
            sources.append(
                NewsSources.from_config(
                    news,
                    '{0}-{1}'.format(config.id, index + 1),
                ),
            )
        return cls(
            '{0}.yaml'.format(os.path.join('data/projects', config.id)),
            '{0}.md'.format(os.path.join('content/projects', config.id)),
            config.model_dump(exclude_none=True, exclude='news'),
            sources,
        )


class NewsSources(Sources):
    """Writes Hugo data and content file for a news page."""

    @classmethod
    def from_config(cls, config: NewsConfig, news_id: str):
        """
        Construct a NewsSources object from the configuration.

        Parameters:
            config: news page configuration.
            news_id: news page identifier.

        Returns:
            NewsSources object.
        """
        return cls(
            '{0}.yaml'.format(os.path.join('data/news', news_id)),
            '{0}.md'.format(os.path.join('content/news', news_id)),
            config.model_dump(exclude_none=True),
        )
