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
    - name: 'tags'
      weight: 2
    - name: 'content'
      weight: 1
  filter: 'tags'
  placeholder: 'Search for a project'
---
