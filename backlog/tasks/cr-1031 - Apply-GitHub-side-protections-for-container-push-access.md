---
id: CR-1031
title: Apply GitHub-side protections for container push access
status: To Do
assignee: []
created_date: '2026-10-13 17:35'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng-demo
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers are getting push access through a fine-grained token that any agent in the container can use, so GitHub must stop direct pushes to main and to tags in every ourPLCC repo except dev and change-requests. plcc-ng-demo has no workflows, no gh-pages, and no tags today, so it needs only the rulesets; with no release App, nobody bypasses them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block creation, update, and deletion; no bypass actors
- [ ] #2 A direct push to main and a tag push are both rejected
<!-- AC:END -->
