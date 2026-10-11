---
id: CR-1019
title: Commit the devcontainer lock file to pin feature versions
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-11 18:43'
updated_date: '2026-10-11 18:45'
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
- [x] #1 .devcontainer/devcontainer-lock.json is committed and pins every feature in devcontainer.json
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Committed .devcontainer/devcontainer-lock.json, pinning the Claude Code feature (the only feature in devcontainer.json) at 1.0.5 by digest, as the sibling repos do. Verified by the lock file on main after PR #7 merged (cf5d6f1), identical to the branch commit 52537de.
<!-- SECTION:FINAL_SUMMARY:END -->
