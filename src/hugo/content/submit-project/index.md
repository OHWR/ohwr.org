---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

title: Submit a Project to OHWR
---

Thank you for your interest in submitting your project to the Open Hardware
Repository. Please follow the steps bellow to submit your project.

### Configure your OHWR project page

Add an `.ohwr.yaml` file to the root directory of your project's repository.
This file should follow the following schema:

```yaml
# The version of the .ohwr.yaml schema.
version: '1.0.0'
# The name of your project.
name: 'Project Name'
# Link to the Markdown description of your project. The
# description is read from the first section of the file.
description: 'https://raw.githubusercontent.com/wiki/user/project/Home.md'
# The website of your project. Use the web page of your git repository if
# your project doesn't have website (e.g. 'https://github.com/user/project').
website: 'https://your.project.com'
# (optional) The licenses of your project. SPDX IDs: https://spdx.org/licenses.
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
# (optional) Link to the Markdown newsfeed of your project.
newsfeed: 'https://raw.githubusercontent.com/wiki/user/project/news.md'
# (optional) Addtional links.
links:
  - name: 'Link text here'
    url: 'https://foo.com/bar1'
  - name: 'Link text here'
    url: 'https://foo.com/bar2'
```

### Write a newsfeed (**optional**)

To post news about your project, create a Markdown file (e.g. a `News.md` file
in the Wiki of your project) and fill in the `newsfeed` field of your
`.ohwr.yaml` file with the link to your Markdown file.

For each news:

  1. Write the title in a heading level 2: `## News Title`.
  2. Add the date using the following format: `YYYY-MM-DD`.
  3. (**optional**) Include image(s) using the following syntax:
     `![Image Description](Image URL)`.
  4. Write the content of the news.

Here is an example of a Markdown newsfeed file:

```markdown
## Important Update on Website

2024-04-03

![Homepage Screenshot](https://example.com/homepage.png)
![New Feature Preview](https://example.com/feature.png)

This is the content of the first news item. It can contain any relevant
information or updates.

## Special Event Coming Up!

2024-04-02

![Event Poster](https://example.com/event.png)

This is the content of the second news item. It can contain any relevant
information or updates.

## Meet Our Team

2024-04-01

This is the content of the third news item. It can contain any relevant
information or updates.
```

### Create an issue

Open an [issue on the OHWR GitHub repository](https://github.com/OHWR/ohwr.org/issues/new?assignees=vascoguita&labels=project&projects=&template=project.md&title=%5BPROJ%5D+)
specifying:

* The URL of the project's git repository.
* The name and email address of the project maintainer.
* A list of tags (optional).
* A list of projects that are compatible with your project (optional).

Our team will review your submission and add your project to the OHWR website.

Thank you for contributing to the open-source hardware community through OHWR!
