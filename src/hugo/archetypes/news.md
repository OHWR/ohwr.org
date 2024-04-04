---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

{{ with (index .Site.Data.news .Name) }}
{{ with .title }}
title: {{ . }}
{{ end }}
{{ with .date }}
date: {{ . }}
{{ end }}
{{ with .images }}
images:
{{ range . }}
  - {{ . }}
{{ end }}
{{ end }}
{{ with .topics }}
topics:
{{ range . }}
  - {{ . }}
{{ end }}
{{ end }}
---

{{ with .content}}
{{ . }}
{{ end }}
{{ end }}
