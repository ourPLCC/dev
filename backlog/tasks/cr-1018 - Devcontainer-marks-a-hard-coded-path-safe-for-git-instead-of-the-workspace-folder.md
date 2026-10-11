---
id: CR-1018
title: >-
  Devcontainer marks a hard-coded path safe for git instead of the workspace
  folder
status: To Do
assignee: []
created_date: '2026-10-11 18:31'
labels: []
dependencies: []
type: chore
project: languages-ng
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The devcontainer's containerEnv sets safe.directory for this repo to the literal /workspaces/languages-ng, while postCreateCommand runs git status in ${containerWorkspaceFolder}. If the checkout is renamed or the workspace folder is customized, git does not trust the real repo and the post-create git status assertion fails. Found by review of the same setup in plcc-ng-demo (CR-1001).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 containerEnv's safe.directory entry for this repo uses ${containerWorkspaceFolder}, not a literal path
- [ ] #2 A rebuilt container starts and its post-create git status assertion passes
<!-- AC:END -->
