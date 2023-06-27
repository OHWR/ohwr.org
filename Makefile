# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

HUGO_SRC = $(CURDIR)/site

all: lint build

###############################################################################
# Build
###############################################################################

.PHONY: build
build: build-hugo

.PHONY: build-hugo
build-hugo:
	hugo --gc --minify --source $(HUGO_SRC)

###############################################################################
# Run
###############################################################################

.PHONY: run
run: run-hugo

.PHONY: run-hugo
run-hugo:
	hugo serve --source $(HUGO_SRC)

###############################################################################
# Lint
###############################################################################

.PHONY: lint
lint: lint-reuse lint-yaml

.PHONY: lint-reuse
lint-reuse:
	reuse lint

.PHONY: lint-yaml
lint-yaml:
	yamllint $(CURDIR)

###############################################################################
# Clean
###############################################################################

.PHONY: clean
clean: clean-hugo

.PHONY: clean-hugo
clean-hugo:
	rm -rf $(HUGO_SRC)/public $(HUGO_SRC)/resources/_gen $(HUGO_SRC)/.hugo_build.lock
