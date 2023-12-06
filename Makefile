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
build: content
	hugo --gc --minify --source ${HUGO} --destination ${PUBLIC}
	

.PHONY: content
content:
	python ${COMPOSE} ${CURDIR}/config.yaml

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
test: lint-reuse lint-yaml lint-makefile lint-python lint-markdown

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
	flake8 ${COMPOSE}

.PHONY: lint-markdown
lint-markdown:
	markdownlint-cli2 ${CURDIR}/**/*.md !${HUGO}/content/projects \
		!${HUGO}/content/news -c

###############################################################################
# Clean
###############################################################################

.PHONY: clean
clean:
	rm -rf ${PUBLIC} ${HUGO}/resources ${HUGO}/.hugo_build.lock \
		${HUGO}/data ${HUGO}/content/projects ${HUGO}/content/news
