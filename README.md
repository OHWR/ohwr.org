<!--
SPDX-FileCopyrightText: 2023 CERN (home.cern)

SPDX-License-Identifier: CC-BY-SA-4.0+
-->

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-yellow.svg)](https://creativecommons.org/licenses/by-sa/4.0/) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) [![Deploy to GitHub Pages](https://github.com/OHWR/ohwr.org/actions/workflows/hugo.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/hugo.yaml) [![REUSE Compliance Check ](https://github.com/OHWR/ohwr.org/actions/workflows/reuse.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/reuse.yaml)

# Open Hardware Repository :penguin:

<!--
The Open Hardware Repository website - https://ohwr.org.
-->

A new website proposal for the Open Hardware Repository - https://ohwr.github.io/ohwr.org/

If approved, this website will be deployed to https://ohwr.org, replacing the current OHWR website.

The website is built with [Hugo](https://gohugo.io) using the [Bigspring Light](https://github.com/gethugothemes/bigspring-light) theme.

## Build :hammer:

Before building the website, make sure to have [Go](https://go.dev/doc/install) and [Hugo](https://gohugo.io/installation) (the extended edition) installed.

To build the website:
1. Clone the project
```
git clone https://github.com/OHWR/ohwr.org.git
```
2. Go to the project directory
```
cd ohwr.org/site
```
3. Build the website
```
hugo --gc --minify
```
4. Serve the website
```
hugo server
```

To view the website, open the URL displayed in your terminal.

## Deployment :satellite:

The website is deployed to [GitHub Pages](https://pages.github.com/) with the [GitHub Actions](https://github.com/features/actions) workflow defined in `.github/workflows/hugo.yaml`.

The workflow builds and deploys the website whenever a change is pushed to the `master` branch.
