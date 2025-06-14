# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import os
import sys
import warnings

from config import Config
from license import SpdxLicenseList
from news import NewsSection
from project import ProjectSection
from pydantic import ValidationError
from redirect import RedirectSection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

parser = argparse.ArgumentParser()
parser.add_argument('config', type=str)
args = parser.parse_args()

logging.info("Loading configuration from '{0}'...".format(args.config))
try:
    with open(args.config, 'r') as config_file:
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter('always')
            config = Config.from_yaml(config_file.read())
            if warns:
                for warn in warns:
                    logging.warning('Warning: {0}'.format(warn.message))
except (ValidationError, ValueError) as config_error:
    logging.error('Failed to load configuration:\n{0}'.format(config_error))
    sys.exit(1)

logging.info("Loading SPDX license list from '{0}'...".format(config.licenses))
try:
    SpdxLicenseList.from_file(config.licenses)
except (ValidationError, ValueError) as spdx_error:
    logging.error('Failed to load SPDX license list:\n{0}'.format(spdx_error))
    sys.exit(1)

logging.info("Generating 'redirects' section...")
redirects = RedirectSection.from_config(config.redirects)

logging.info("Writing 'redirects' section...")
redirects.write(os.path.join(config.sources, 'content/redirects'))

logging.info("Generating 'projects' section...")
with warnings.catch_warnings(record=True) as warns:
    warnings.simplefilter('always')
    projects = ProjectSection.from_config(config.projects)
    if warns:
        for warn in warns:
            logging.warning('Warning: {0}'.format(
                warn.message,
            ))

logging.info("Writing 'projects' section...")
projects.write(os.path.join(config.sources, 'content/projects'))

logging.info("Generating 'news' section...")
with warnings.catch_warnings(record=True) as warns:
    warnings.simplefilter('always')
    news = NewsSection.from_config(config.projects)
    if warns:
        for warn in warns:
            logging.warning('Warning: {0}'.format(warn.message))

logging.info("Writing 'news' section...")
news.write(os.path.join(config.sources, 'content/news'))
