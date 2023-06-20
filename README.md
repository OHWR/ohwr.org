<!--
SPDX-FileCopyrightText: 2023 CERN (home.cern)

SPDX-License-Identifier: CC-BY-SA-4.0+
-->

[![Deploy to GitHub Pages](https://github.com/OHWR/ohwr.org/actions/workflows/hugo.yaml/badge.svg)](https://github.com/OHWR/ohwr.org/actions/workflows/hugo.yaml)

# Open Hardware Repository :globe_with_meridians:

The Open Hardware Repository website - https://ohwr.org.

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
cd ohwr.org
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

The website is deployed to [GitHub Pages](https://pages.github.com/) with the [GitHub Actions](https://github.com/features/actions) workflow defined in `.github/workflows/deploy.yml`.

The workflow builds and deploys the website whenever a change is pushed to the `master` branch.
