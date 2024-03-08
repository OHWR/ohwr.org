<!--
SPDX-FileCopyrightText: 2023 CERN (home.cern)

SPDX-License-Identifier: CC-BY-SA-4.0+
-->

# Contributing to ohwr.org 🚀

Thank you for considering contributing to
[ohwr.org](https://github.com/OHWR/ohwr.org). We appreciate your time and effort
in helping us improve and maintain our website. To ensure a smooth and
collaborative process, please follow the guidelines outlined below.

> **Note**: Please note that by contributing to this project, you agree to abide
> by our [Code of Conduct](CODE_OF_CONDUCT.md). Ensure you have read and
> understood the expectations outlined in the Code of Conduct before
> participating in the community.

To contribute, you can help us in the following ways:

1. [Create an Issue](#create-an-issue)
2. [Create a Pull Request](#create-a-pull-request)

## Create an Issue

> **Important:** Do not create security-related issues. To report security
> issues please refer to our [Security Policy](SECURITY.md).

To create an issue, please follow these steps:

1. **Navigate to Issues:**

   Visit the [Issues section](https://github.com/OHWR/ohwr.org/issues) of the
   repository.

2. **Create a New Issue:**

   Click on the "New Issue" button.

3. **Choose the Appropriate Template:**

   Select the template that best suits the nature of your issue:

   * Report a bug 🐛
   * Request content 📝
   * Request documentation 📘
   * Request a feature 🌟
   * Request layout improvement 🎨
   * Submit a project 🚀
   * Ask a question ❓

4. **Fill in the Details:**

   Complete the template with relevant information, providing as much detail as
   possible.

5. **Submit the Issue:**

   Click on "Submit new issue" to create the issue.

## Create a Pull Request

To create a pull request, please follow these steps:

1. **Fork the Repository:**

   Click on the "Fork" button at the top right of the
   [ohwr.org repository](https://github.com/OHWR/ohwr.org) to create a copy in
   your GitHub account.

2. **Enable GitHub Actions:**

   * Go to the "Actions" tab in your forked repository.
   * If Actions are not already enabled, click the "I understand my workflows,
     go ahead and enable them" button.

3. **Enable GitHub Pages:**

   * Go to the "Settings" tab in your forked repository.
   * On the sidebar of the settings page, click on "Pages".
   * Under the "Source" section, select "GitHub Actions".

4. **Find the Issue:**

   * Go to the "Issues" tab of the upstream
     [ohwr.org repository](https://github.com/OHWR/ohwr.org).
   * Click on the issue you want to address. If the issue doesn't exist yet,
     consider [creating one](#create-an-issue) first.

5. **Create a Branch:**

   * On the right side of the issue page, under "Development", click on
     "Create a branch".
   * Under the "Repository destination" section, select your forked repository.
   * Click on the "Create branch" button.

6. **Make Changes:**

   Clone your forked repository locally, checkout your new branch, make your
   changes to the code, commit and push them.

7. **Preview the Changes:**

   * Copy your changes to the "master" branch of your forked repository:

     ```bash
     git checkout master
     git reset --hard your-feature-branch
     git push
     ```

   * Wait for GitHub Actions to generate and publish the website to GitHub
     Pages. To observe the progress, go to the "Actions" tab in your forked
     repository.
   * Access the preview at <https://YOUR_USERNAME.github.io/ohwr.org>.

8. **Open a Pull Request:**

   * Go to the "Pull request" tab in your forked repository.
   * Click on the "New pull request" button.
   * On the pull request page, set:
      * "base repository" to "OHWR/ohwr.org".
      * "base" to "master".
      * "head repository" to "YOUR_USERNAME/ohwr.org".
      * "compare" to "your-feature-branch".
   * Click on the "Create pull request" button.
   * Complete the template with relevant information, providing as much detail
     as possible and referencing the related issue using the
     "Closes #ISSUE-NUMBER" syntax.
   * Click on the "Create pull request" button.
