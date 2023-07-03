# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

PROJECTS_FILE		= ${CURDIR}/projects.txt
override PROJECT_URLS	+= $(shell [ -f ${PROJECTS_FILE} ] && cat ${PROJECTS_FILE})
PROJECTS		= $(basename $(notdir ${PROJECT_URLS}))
SOURCE			= ${CURDIR}/src
PROJECT_DATA_DIR	= ${SOURCE}/data/projects
PROJECT_CONTENT_DIR	= ${SOURCE}/content/projects
PROJECT_CONTENT		= $(foreach PROJECT,${PROJECTS},${PROJECT_CONTENT_DIR}/${PROJECT}.md)

all: lint build

###############################################################################
# Build
###############################################################################

.PHONY: build
build: build-hugo

.PHONY: build-hugo
build-hugo: ${PROJECT_CONTENT}
	hugo --gc --minify --source ${SOURCE} $${BASE_URL:+--baseURL ${BASE_URL}}

${PROJECT_CONTENT_DIR}/%.md: ${PROJECT_DATA_DIR}/%.yaml
	hugo new --source ${SOURCE} content/projects/${@F}

.PRECIOUS: ${PROJECT_DATA_DIR}/%.yaml
${PROJECT_DATA_DIR}/%.yaml:
	@mkdir -p ${@D}
	$(eval TMP := $(shell mktemp -d))
	git clone --depth 1 $(filter %/$*.git, ${PROJECT_URLS}) ${TMP}
	cp ${TMP}/.ohwr.yaml $@
	rm -rf ${TMP}

###############################################################################
# Run
###############################################################################

.PHONY: run
run: run-hugo

.PHONY: run-hugo
run-hugo:
	hugo serve --source ${SOURCE}

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
	yamllint ${CURDIR}

###############################################################################
# Clean
###############################################################################

.PHONY: clean
clean: clean-hugo clean-project-data clean-project-content

.PHONY: clean-hugo
clean-hugo:
	rm -rf ${SOURCE}/public ${SOURCE}/resources/_gen ${SOURCE}/.hugo_build.lock

.PHONY: clean-project-data
clean-project-data:
	rm -rf ${PROJECT_DATA_DIR}

.PHONY: clean-project-content
clean-project-content:
	rm -rf ${PROJECT_CONTENT_DIR}
