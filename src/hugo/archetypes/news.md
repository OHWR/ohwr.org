---
# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

{{ $project := path.BaseName .Dir }}
{{ with (index (index .Site.Data.news $project) .Name) }}
{{ with .title }}
title: {{ . }}
{{ end }}
{{ with .date }}
date: {{ . }}
{{ end }}
{{ with (.image | default (index (index site.Data.projects $project).images 0)) }}
image: {{ . }}
{{ end }}
{{ end }}
project: {{ $project }}
---

{{ if (ne .Name $project) }}
{{< news {{ $project }} {{ .Name }} >}}
{{ end }}