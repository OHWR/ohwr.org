---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

{{ with (index .Site.Data.categories .Name) }}
{{ with .name }}
title: {{ . }}
{{ end }}
---

{{ with .description }}
{{ . }}
{{ end }}
{{ end }}
