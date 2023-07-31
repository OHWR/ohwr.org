# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

SOURCE		= ${CURDIR}/src
CONFIG		= ${CURDIR}/config.yaml
MAKEFILE	= ${CURDIR}/Makefile
SCHEMA		= ${CURDIR}/schema.yaml
DATA		= ${SOURCE}/data/projects
CONTENT		= ${SOURCE}/content/projects

HOST		= $(shell echo ${1} | cut -d'/' -f3)
OWNER		= $(shell echo ${1} | cut -d'/' -f4)
REPO		= $(shell echo ${1} | cut -d'/' -f5 | cut -d'.' -f1)
URL_GH		= https://api.github.com/repos/$(call OWNER, ${1})/$(call REPO, ${1})/contents/.ohwr.yaml
IS_GH		= $(filter github.com, $(call HOST, ${1}))
IMPORT_GH	= curl --silent -H 'Accept: application/vnd.github.v3.raw' $(call URL_GH, ${1}) -L -o ${2}

define IMPORT_GIT
$(eval TMP := $(shell mktemp -d))
git clone --depth 1 ${1} ${TMP}
cp ${TMP}/.ohwr.yaml ${2}
rm -rf ${TMP}
endef

.PHONY: all
all: test build

###############################################################################
# Build
###############################################################################

.PHONY: build
build: $(foreach ID, $(shell yq '.projects.[] | .id' ${CONFIG}), ${CONTENT}/${ID}.md)
	hugo --gc --minify --source ${SOURCE} $${BASE_URL:+--baseURL $${BASE_URL}}

${CONTENT}/%.md: ${DATA}/%.yaml
	hugo new --source ${SOURCE} $${BASE_URL:+--baseURL $${BASE_URL}} content/projects/${@F}

.PRECIOUS: ${DATA}/%.yaml
${DATA}/%.yaml:
	@mkdir -p ${@D}
	$(eval URL := $(shell yq '.projects.[] | select(.id == "$*") | .url' ${CONFIG}))
	$(if $(call IS_GH, ${URL}), $(call IMPORT_GH, ${URL}, $@), $(call IMPORT_GIT, ${URL}, $@))
	yamale -s ${SCHEMA} $@
	yq -i '.project.repository = "${URL}"' $@
	$(eval TYPE = $(shell yq '.projects.[] | select(.id == "$*") | .type' ${CONFIG}))
	$(if $(filter-out null, ${TYPE}), yq -i '.project.type = "${TYPE}"' $@)

###############################################################################
# Run
###############################################################################

.PHONY: run
run: 
	hugo serve --source ${SOURCE}

###############################################################################
# Test
###############################################################################

.PHONY: test
test: lint-reuse lint-yaml lint-makefile

.PHONY: lint-reuse
lint-reuse:
	reuse lint

.PHONY: lint-yaml
lint-yaml:
	yamllint ${CURDIR}

.PHONY: lint-makefile
lint-makefile:
	checkmake ${MAKEFILE}

###############################################################################
# Clean
###############################################################################

.PHONY: clean
clean: clean-hugo clean-data clean-content

.PHONY: clean-hugo
clean-hugo:
	rm -rf ${SOURCE}/public ${SOURCE}/resources/_gen ${SOURCE}/.hugo_build.lock

.PHONY: clean-data
clean-data:
	rm -rf ${DATA}

.PHONY: clean-content
clean-content:
	rm -rf ${CONTENT}
