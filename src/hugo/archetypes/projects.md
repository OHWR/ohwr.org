---
# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

{{ with (index .Site.Data.projects .Name) }}
{{ with .name }}
title: {{ . }}
{{ end }}
{{ with .images }}
images:
{{ range . }}
  - {{ . }}
{{ end }}
{{ end }}
{{ with .featured }}
featured: {{ . }}
{{ end }}
{{ with .tags }}
tags:
{{ range . }}
  - {{ . }}
{{ end }}
{{ end }}
{{ with .categories }}
categories:
{{ range . }}
  - {{ . }}
{{ end }}
{{ end }}
{{ end }}
date: {{ .Date }}
---

{{< project {{ .Name }} >}}
{{< latest-news project="{{ .Name }}" >}}
