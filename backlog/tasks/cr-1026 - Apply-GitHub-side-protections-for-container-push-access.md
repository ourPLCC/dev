---
id: CR-1026
title: Apply GitHub-side protections for container push access
status: To Do
assignee: []
created_date: '2026-10-13 13:54'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng-devcontainer
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers are getting push access through a fine-grained token that any agent in the container can use, so GitHub must stop direct pushes to main and to tags. plcc-ng-devcontainer releases with its own App (APP_ID), not the release App the other repos use, so the rulesets must either name that App as a bypass actor or the repo must switch to the shared one.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block every push; the repo's release App is the only bypass actor
- [ ] #2 The CR records whether the repo keeps its own App or adopts the shared release App, and why
- [ ] #3 The App's secrets live in a release environment limited to main and release tags
- [ ] #4 A release run after the change publishes its images and feature
<!-- AC:END -->
