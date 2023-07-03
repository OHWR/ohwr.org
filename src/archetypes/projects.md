---
# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

{{ with (index .Site.Data.projects .Name).project }}
title: {{ .name }}
image: {{ .image }}
{{ end }}
date: {{ .Date }}
---

{{< project {{ .Name }} >}}
