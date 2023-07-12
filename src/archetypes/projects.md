---
# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

{{ with (index .Site.Data.projects .Name).project }}
title: {{ .name }}
image: {{ .image }}
{{ if .tags }}
tags:
{{ range .tags }}
  - {{ . }}
{{ end }}
{{ end }}
{{ if .categories }}
categories:
{{ range .categories }}
  - {{ . }}
{{ end }}
{{ end }}
{{ end }}
date: {{ .Date }}
---

{{< project {{ .Name }} >}}
