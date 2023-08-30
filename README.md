<!--
SPDX-FileCopyrightText: 2023 CERN (home.cern)

SPDX-License-Identifier: CC-BY-SA-4.0+
-->

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-yellow.svg)](https://creativecommons.org/licenses/by-sa/4.0/) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) [![Build](https://github.com/OHWR/ohwr.org/actions/workflows/build.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/build.yaml) [![Deploy to GitHub Pages](https://github.com/OHWR/ohwr.org/actions/workflows/deploy.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/deploy.yaml) [![REUSE Compliance Check](https://github.com/OHWR/ohwr.org/actions/workflows/reuse.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/reuse.yaml) [![YAML Lint](https://github.com/OHWR/ohwr.org/actions/workflows/yaml.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/yaml.yaml) [![Makefile Lint](https://github.com/OHWR/ohwr.org/actions/workflows/makefile.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/makefile.yaml) [![Python Lint](https://github.com/OHWR/ohwr.org/actions/workflows/python.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/python.yaml)

# Open Hardware Repository :penguin:

A new website proposal for the Open Hardware Repository - https://ohwr.github.io/ohwr.org/

If approved, this website will be deployed to https://ohwr.org, replacing the current OHWR website.

The website is built with [Hugo](https://gohugo.io) using the [Bigspring Light](https://github.com/gethugothemes/bigspring-light) theme.

## Build :hammer:

### Requirements :clipboard:

* [Go](https://go.dev/doc/install) >= go1.20.3
* [Hugo](https://gohugo.io/installation) (the extended edition) >= v0.110.0+extended
* [Python](https://www.python.org/downloads) >= 3.11.4
* [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation) >= 6.0.1
* [Pydantic](https://docs.pydantic.dev/latest/install) >= 2.1.1

### Steps :footprints:

1. Clone the project
```
git clone https://github.com/OHWR/ohwr.org.git
```
2. Go to the project directory
```
cd ohwr.org
```
3. Build the website
```
make build
```
4. Serve the website
```
make run
```

To view the website, open the URL displayed in your terminal.

## Deployment :satellite:

The website is deployed to [GitHub Pages](https://pages.github.com/) with the [GitHub Actions](https://github.com/features/actions) workflow defined in `.github/workflows/deploy.yaml`.

The workflow builds and deploys the website whenever a change is pushed to the `master` branch.
