# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""CLI to generate content for ohwr.org."""

import argparse
import json
import logging
from urllib.request import urlopen

import yaml
from config import CatConfig, ConfigError, ProjConfig
from sources import CatSources, ProjSources

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()

config = yaml.safe_load(args.config)

logging.basicConfig(
    level=getattr(logging, config['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

with urlopen(config['license_list']) as response:  # noqa: S310
    spdx_license_list = json.load(response)

for cat in config['categories']:
    try:
        cat_config = CatConfig(**cat)
    except ConfigError as cat_error:
        msg = 'Could not configure the {0} category:\n↳ {1}'
        logging.error(msg.format(cat['name'], cat_error))
        continue
    cat_sources = CatSources.from_config(cat_config)
    cat_sources.dump(config['source'])

for proj in config['projects']:
    try:
        proj_config = ProjConfig.from_url(
            spdx_license_list=spdx_license_list,
            **proj,
        )
    except ConfigError as proj_error:
        msg = 'Could not configure the {0} project:\n↳ {1}'
        logging.error(msg.format(proj['id'], proj_error))
        continue
    proj_sources = ProjSources.from_config(proj_config)
    proj_sources.dump(config['source'])
