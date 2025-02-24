---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

outputs:
  - 'html'
  - 'json'

search:
  keys:
    - name: 'title'
      weight: 3
    - name: 'project'
      weight: 2
    - name: 'content'
      weight: 1
  filter: 'project'
  placeholder: 'Search for a news article'
---
