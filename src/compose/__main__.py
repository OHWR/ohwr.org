# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import os
import sys

from category import CategorySection
from config import Config
from license import SpdxLicenseList
from news import NewsSection
from project import ProjectSection
from pydantic import ValidationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()

logging.info("Loading configuration from '{0}'...".format(args.config.name))
try:
    config = Config.from_yaml(args.config.read())
except (ValidationError, ValueError) as config_error:
    logging.error('Failed to load configuration:\n{0}'.format(config_error))
    sys.exit(1)

logging.info("Loading SPDX license list from '{0}'...".format(config.licenses))
try:
    SpdxLicenseList.from_file(config.licenses)
except (ValidationError, ValueError) as spdx_error:
    logging.error('Failed to load SPDX license list:\n{0}'.format(spdx_error))
    sys.exit(1)

logging.info("Generating 'categories' section...")
try:
    categories = CategorySection.from_config(config.categories)
except ValueError as categories_error:
    logging.error("Failed to generate 'categories' section:\n{0}".format(
        categories_error,
    ))
    sys.exit(1)

logging.info("Writing 'categories' section...")
try:
    categories.write(os.path.join(config.sources, 'content/categories'))
except ValueError as categories_write_error:
    logging.error("Failed to write 'categories' section:\n{0}".format(
        categories_write_error,
    ))
    sys.exit(1)

logging.info("Generating 'projects' section...")
projects = ProjectSection.from_config(config.projects)

logging.info("Writing 'projects' section...")
try:
    projects.write(os.path.join(config.sources, 'content/projects'))
except ValueError as projects_write_error:
    logging.error("Failed to write 'projects' section:\n{0}".format(
        projects_write_error,
    ))
    sys.exit(1)

logging.info("Generating 'news' section...")
news = NewsSection.from_config(config.projects)
logging.info("Writing 'news' section...")
try:
    news.write(os.path.join(config.sources, 'content/news'))
except ValueError as news_write_error:
    logging.error("Failed to write 'news' section:\n{0}".format(
        news_write_error,
    ))
    sys.exit(1)
