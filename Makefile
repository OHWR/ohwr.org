# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

HUGO	= ${CURDIR}/src/hugo
COMPOSE	= ${CURDIR}/src/compose
PUBLIC	= ${CURDIR}/public

.PHONY: all
all: test build

###############################################################################
# Build
###############################################################################

.PHONY: build
build:
	python ${COMPOSE} ${CURDIR}/config.yaml
	hugo --gc --minify --source ${HUGO} --destination ${PUBLIC}

###############################################################################
# Run
###############################################################################

.PHONY: run
run: 
	hugo serve --source ${HUGO} --destination ${PUBLIC}

###############################################################################
# Test
###############################################################################

.PHONY: test
test: lint-reuse lint-yaml lint-makefile lint-python

.PHONY: lint-reuse
lint-reuse:
	reuse lint

.PHONY: lint-yaml
lint-yaml:
	yamllint ${CURDIR}

.PHONY: lint-makefile
lint-makefile:
	checkmake ${CURDIR}/Makefile

.PHONY: lint-python
lint-python:
	flake8 ${COMPOSE}

###############################################################################
# Clean
###############################################################################

.PHONY: clean
clean:
	rm -rf ${PUBLIC} ${HUGO}/resources ${HUGO}/.hugo_build.lock \
		${HUGO}/data ${HUGO}/content/projects ${HUGO}/content/news
