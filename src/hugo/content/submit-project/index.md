---
# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

title: Submit a Project to OHWR
---

Thank you for your interest in submitting your project to the Open Hardware
Repository. It takes only two steps to submit your project:

## Step 1: Configure your OHWR project page

Add a `.ohwr.yaml` file to the root directory of your project's repository. This
file should follow the following schema:

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
  # The website of your project.
  # Use the web page of your git repository if your project doesn't have
  # dedicated website (e.g. 'https://github.com/user/project').
  website: 'https://your.project.com'
  # The licenses of your project.
  # Use SPDX identifiers - https://spdx.org/licenses/.
  licenses: ['CERN-OHL-W-2.0+', 'CC-BY-SA-4.0+', 'BSD-3-Clause']
  # (optional) Images of your project (maximum 5 images).
  # The main image should be the first in the list.
  # (e.g. a photo of the latest prototype).
  images:
    - 'https://your.project.com/img1.png'
    - 'https://your.project.com/img2.png'
    - 'https://your.project.com/img3.png'
  # (optional) Link to the documentation of your project.
  documentation: 'https://github.com/user/project/wiki'
  # (optional) Link to the issue/bug tracker of your project.
  issues: 'https://github.com/user/project/issues'
  # (optional) Link to the latest release of your project.
  latest_release: 'https://github.com/user/project/releases/latest'
  # (optional) Link to the forum where your community has conversations, asks
  # questions and posts answers.
  forum: 'https://forums.ohwr.org/c/project'
  # (optional) News feed of your project.
  news:
    - title: 'News title here'
      date: 2020-07-30
      # (optional) Image of the news.
      image: 'https://your.news.com/img.png'
      # (optional) The Markdown content of the news.
      content: |
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
        sollicitudin velit ac luctus [dignissim](https://foo.com/bar).
    - title: 'News title here'
      date: 2018-01-11
    - title: 'News title here'
      date: 2010-06-22
  # (optional) Addtional links.
  links:
    - name: 'Link text here'
      url: 'https://foo.com/bar1'
    - name: 'Link text here'
      url: 'https://foo.com/bar2'
    - name: 'Link text here'
      url: 'https://foo.com/bar3'
  # (optional) Categories to which your project belongs (e.g. 'FMC Carriers').
  categories: ['Category X', 'Category Y', 'Category Z']
  # (optional) Tags that characterize your project (e.g. 'ethernet').
  tags: ['Tag1', 'Tag2', 'Tag3']
```

## Step 2: Create an issue

Once you have added the .ohwr.yaml file to your project's repository, create an
issue on the OHWR GitHub repository. In the issue, please provide the following
information:

* The URL to your project's Git repository.

* An email address of the person responsible for the project.

Our team will review your submission, and if everything is in order, your
project will be added to the Open Hardware Repository.

Thank you for contributing to the open-source hardware community through OHWR!

{{< button link="https://github.com/OHWR/ohwr.org/issues/new" label="Create an issue" >}} <!-- markdownlint-disable-line MD013 MD034 -->
