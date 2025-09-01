<!--
SPDX-FileCopyrightText: 2025 CERN (home.cern)

SPDX-License-Identifier: CC-BY-SA-4.0+
-->

# Open Hardware Repository :penguin:

[![License CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-yellow.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![License BSD 3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](.github/CODE_OF_CONDUCT.md)
[![Build](https://github.com/OHWR/ohwr.org/actions/workflows/build.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/build.yaml)
[![Test](https://github.com/OHWR/ohwr.org/actions/workflows/test.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/test.yaml)
[![Deploy to GitHub Pages](https://github.com/OHWR/ohwr.org/actions/workflows/deploy.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/deploy.yaml)
[![REUSE Compliance Check](https://github.com/OHWR/ohwr.org/actions/workflows/reuse.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/reuse.yaml)
[![YAML Lint](https://github.com/OHWR/ohwr.org/actions/workflows/yaml.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/yaml.yaml)
[![Makefile Lint](https://github.com/OHWR/ohwr.org/actions/workflows/makefile.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/makefile.yaml)
[![Python Lint](https://github.com/OHWR/ohwr.org/actions/workflows/python.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/python.yaml)
[![Markdown Lint](https://github.com/OHWR/ohwr.org/actions/workflows/markdown.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/markdown.yaml)
[![CodeQL](https://github.com/OHWR/ohwr.org/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/github-code-scanning/codeql)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/bb599887cc7542e1afd97cdd9f66c1f0)](https://app.codacy.com/gh/OHWR/ohwr.org/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Mattermost](https://img.shields.io/badge/Mattermost-Join_Channel-blue?logo=mattermost)](https://mattermost.web.cern.ch/ohr/channels/ohwrorg)

This repository hosts the sources of [Open Hardware Repository website](https://ohwr.org).

The website is built with [Hugo](https://gohugo.io) using the [Bigspring Light](https://github.com/gethugothemes/bigspring-light)
theme.

## Build :hammer:

### Requirements :clipboard:

* [Go](https://go.dev/doc/install) >= 1.24.2
* [Hugo](https://gohugo.io/installation) (the extended edition) >= 0.147.2
* [Python](https://www.python.org/downloads) >= 3.12.3
* [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation) >= 6.0.2
* [Pydantic](https://docs.pydantic.dev/latest/install) >= 2.11.7
* [email-validator](https://github.com/JoshData/python-email-validator?tab=readme-ov-file#installation)
  \>= 2.3.0
* [Requests](https://requests.readthedocs.io/en/latest/user/install) >= 2.32.5

### Steps :footprints:

1. Clone the project

   ```bash
   git clone https://github.com/OHWR/ohwr.org.git
   ```

2. Go to the project directory

   ```bash
   cd ohwr.org
   ```

3. Build the website

   ```bash
   make build
   ```

   The website is stored in the `public` directory.

4. Serve the website

   ```bash
   make run
   ```

   To view the website, open the URL displayed in your terminal.

## Test :test_tube:

### Requirements :clipboard: <!-- markdownlint-disable-line MD024 -->

* [reuse](https://reuse.readthedocs.io/en/v1.0.0/readme.html#install)
  \>= 5.0.2
* [wemake-python-styleguide](https://wemake-python-styleguide.readthedocs.io/en/latest/#quickstart)
  \>= 1.0.0
* [yamllint](https://yamllint.readthedocs.io/en/stable/quickstart.html#installing-yamllint)
  \>= 1.37.1
* [checkmake](https://github.com/mrtazz/checkmake#installation)
  \>= 0.2.2
* [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2#install)
  \>= 0.10.0
* [pytest](https://docs.pytest.org/en/stable/getting-started.html#install-pytest)
  \>= 8.4.1
* [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/#install)
  \>=3.14.1

### Steps :footprints: <!-- markdownlint-disable-line MD024 -->

1. Clone the project

   ```bash
   git clone https://github.com/OHWR/ohwr.org.git
   ```

2. Go to the project directory

   ```bash
   cd ohwr.org
   ```

3. Run the tests

   ```bash
   make test
   ```

## Deployment :satellite:

The website is deployed to [GitHub Pages](https://pages.github.com/) with the
[GitHub Actions](https://github.com/features/actions) workflow defined in
`.github/workflows/deploy.yaml`.

The workflow builds and deploys the website whenever a change is pushed to the
`master` branch.

If errors are encountered while building the website, a warning is sent to the
[ohwr.org Mattermost channel](https://mattermost.web.cern.ch/ohr/channels/ohwrorg).

## Code of Conduct :scroll:

Please review our [Code of Conduct](.github/CODE_OF_CONDUCT.md) to understand
the expectations for behavior within the project community.

## Security Policy :lock:

For information on our security policy and reporting vulnerabilities, please
check our [Security Policy](.github/SECURITY.md).

## Contributing Guidelines :rocket:

We welcome contributions! Before getting started, please read our
[Contributing Guidelines](.github/CONTRIBUTING.md) for information on how to
contribute to the project.
