# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

HUGO	= ${CURDIR}/src/hugo
COMPOSE	= ${CURDIR}/src/compose
PUBLIC	= ${CURDIR}/public
TEST	= ${CURDIR}/test

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
test: lint-reuse lint-yaml lint-makefile lint-python lint-markdown test-pytest

.PHONY: lint-reuse
lint-reuse:
	reuse lint

.PHONY: lint-yaml
lint-yaml:
	yamllint -d '{extends: default, ignore-from-file: .gitignore}' .

.PHONY: lint-makefile
lint-makefile:
	checkmake ${CURDIR}/Makefile

.PHONY: lint-python
lint-python:
	flake8

.PHONY: lint-markdown
lint-markdown:
	markdownlint-cli2 '${CURDIR}/**/*.md' '#${CURDIR}/.venv'

test-pytest:
	pytest ${TEST}

###############################################################################
# Clean
###############################################################################

.PHONY: clean
clean:
	rm -rf ${HUGO}/resources ${HUGO}/.hugo_build.lock ${COMPOSE}/__pycache__ \
		${PUBLIC} ${TEST}/__pycache__ ${TEST}/.pytest_cache
	find ${HUGO}/content/projects ! -name _index.md -type f -exec rm -f {} +
	find ${HUGO}/content/news ! -name _index.md -type f -exec rm -f {} +
	find ${HUGO}/content/redirects ! -name _index.md -type f -exec rm -f {} +
