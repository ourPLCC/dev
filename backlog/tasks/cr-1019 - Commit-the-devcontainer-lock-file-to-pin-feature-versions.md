---
id: CR-1019
title: Commit the devcontainer lock file to pin feature versions
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-11 18:43'
updated_date: '2026-10-11 18:43'
labels: []
dependencies: []
type: chore
project: plcc-ng-demo
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CR-1001 added the Claude Code devcontainer feature (claude-code:1.0), but the devcontainer-lock.json the devcontainer CLI generated was left untracked. Without it, each rebuild may resolve a different 1.0.x feature version. plcc-ng, languages-ng, and plcc-ng-devcontainer all commit their lock files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 .devcontainer/devcontainer-lock.json is committed and pins every feature in devcontainer.json
<!-- AC:END -->
