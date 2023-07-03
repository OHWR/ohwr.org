# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

SOURCE = $(CURDIR)/src

all: lint build

###############################################################################
# Build
###############################################################################

.PHONY: build
build: build-hugo

.PHONY: build-hugo
build-hugo:
	hugo --gc --minify --source $(SOURCE)

###############################################################################
# Run
###############################################################################

.PHONY: run
run: run-hugo

.PHONY: run-hugo
run-hugo:
	hugo serve --source $(SOURCE)

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
	rm -rf $(SOURCE)/public $(SOURCE)/resources/_gen $(SOURCE)/.hugo_build.lock
