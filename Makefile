# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

SOURCE		= ${CURDIR}/src
CONFIG		= ${CURDIR}/config.yaml
MAKEFILE	= ${CURDIR}/Makefile
DATA		= ${SOURCE}/data/projects
CONTENT		= ${SOURCE}/content/projects

PARSE_CONFIG	= $(shell yq '.projects.[] | ${1}' ${CONFIG})
HOST		= $(shell echo ${1} | cut -d'/' -f3)
OWNER		= $(shell echo ${1} | cut -d'/' -f4)
REPO		= $(shell echo ${1} | cut -d'/' -f5 | cut -d'.' -f1)
URL_GH		= https://api.github.com/repos/$(call OWNER, ${1})/$(call REPO, ${1})/contents/.ohwr.yaml
IMPORT_GH	= curl -H 'Accept: application/vnd.github.v3.raw' $(call URL_GH, ${1}) -L -o ${2}

define IMPORT
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
build: $(foreach ID, $(call PARSE_CONFIG, '.id'), ${CONTENT}/${ID}.md)
	hugo --gc --minify --source ${SOURCE} $${BASE_URL:+--baseURL ${BASE_URL}}

${CONTENT}/%.md: ${DATA}/%.yaml
	hugo new --source ${SOURCE} $${BASE_URL:+--baseURL ${BASE_URL}} content/projects/${@F}

.PRECIOUS: ${DATA}/%.yaml
${DATA}/%.yaml:
	@mkdir -p ${@D}
	$(eval URL = $(call PARSE_CONFIG, select(.id == "$*") | .url))
	$(if $(filter github.com, $(call HOST, ${URL})), $(call IMPORT_GH, ${URL}, $@), $(call IMPORT, ${URL}, $@))

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
