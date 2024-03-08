---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

title: Submit a Project to OHWR
---

Thank you for your interest in submitting your project to the Open Hardware
Repository. It takes only two steps to submit your project.

### Step 1: Configure your OHWR project page

Add an `.ohwr.yaml` file to the root directory of your project's repository.
This file should follow the following schema:

```yaml
# The version of the .ohwr.yaml template.
version: '1.0.0'

project:
  # The name of your project.
  name: 'Project Name'
  # The Markdown description of your project (minimum 30 words).
  description: |
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
    sollicitudin velit ac luctus [dignissim](https://foo.com/bar).

    Ut in nulla at velit dictum rutrum pretium eu metus. Etiam rhoncus suscipit
    leo at varius.
  # The website of your project. Use the web page of your git repository if
  # your project doesn't have website (e.g. 'https://github.com/user/project').
  website: 'https://your.project.com'
  # The licenses of your project (SPDX IDs - https://spdx.org/licenses/).
  licenses: ['CERN-OHL-W-2.0+', 'CC-BY-SA-4.0+', 'BSD-3-Clause']
  # (optional) Images of your project (maximum 5 images). The main image should
  # be the first in the list (e.g. a photo of the latest prototype).
  images:
    - 'https://your.project.com/img1.png'
    - 'https://your.project.com/img2.png'
  # (optional) Link to the documentation of your project.
  documentation: 'https://github.com/user/project/wiki'
  # (optional) Link to the issue/bug tracker of your project.
  issues: 'https://github.com/user/project/issues'
  # (optional) Link to the latest release of your project.
  latest_release: 'https://github.com/user/project/releases/latest'
  # (optional) Link to the forum where your community has conversations.
  forum: 'https://forums.ohwr.org/c/project'
  # (optional) News feed of your project.
  news:
    - title: 'News title here'
      date: 2020-07-30
      # (optional) Images of the news.
      images:
        - 'https://your.news.com/img1.png'
        - 'https://your.news.com/img2.png'
      # (optional) The Markdown content of the news.
      content: 'Quisque sollicitudin velit ac [luctus](https://foo.com/bar).'
    - title: 'News title here'
      date: 2018-01-11
  # (optional) Addtional links.
  links:
    - name: 'Link text here'
      url: 'https://foo.com/bar1'
    - name: 'Link text here'
      url: 'https://foo.com/bar2'
  # (optional) Categories to which your project belongs (e.g. 'FMC Carriers').
  categories: ['Category X', 'Category Y', 'Category Z']
  # (optional) Tags that characterize your project (e.g. 'ethernet').
  tags: ['Tag1', 'Tag2', 'Tag3']
```

### Step 2: Create an issue

Open an issue on the OHWR GitHub repository specifying:

* The URL of the project's git repository.
* The name and email address of the responsible for the project.

Our team will review your submission, and if everything is in order, your
project will be added to the Open Hardware Repository.

Thank you for contributing to the open-source hardware community through OHWR!

{{< button link="https://github.com/OHWR/ohwr.org/issues/new?assignees=vascoguita&labels=project&projects=&template=project.md&title=%5BPROJ%5D+" label="New Issue" >}} <!-- markdownlint-disable-line MD013 MD034 -->
