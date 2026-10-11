---
id: CR-1001
title: Migrate plcc-ng-demo's issue tracker to ourPLCC/dev
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 01:55'
updated_date: '2026-10-11 18:11'
labels: []
milestone: m-0
dependencies:
  - CR-1016
references:
  - ../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md
  - ../../dev-docs/specs/2026-10-11-plcc-ng-demo-migration-design.md
type: chore
project: plcc-ng-demo
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
plcc-ng-demo keeps a 5-issue copy of the old plcc-ng tracker. Design: plcc-ng dev-docs/specs/2026-10-08-199-central-tracker-design.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Legacy issues converted at offset +800 (CR-8xx)
- [ ] #2 plcc-ng-demo's devcontainer, AGENTS.md, and CONTRIBUTING.md follow plcc-ng's layout: the devcontainer clones and mounts ../dev at /workspaces/dev with BACKLOG_CWD set, AGENTS.md imports ../dev/ORG-AGENTS.md, ../dev/CONTRIBUTING.md, then CONTRIBUTING.md, and CONTRIBUTING.md opens with the link to the org developer guide; its old tracker is removed
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
From CR-1005: assign_ids now takes dup_offset and dup_range. The ID table reserves no duplicate-number range for plcc-ng-demo; if its legacy numbers repeat, pick a range inside CR-801..CR-899 and record it in dev-docs/tracker.md.

From CR-1000: after the switch-over, scan the code repo for broken relative Markdown links. migrate.repo_links only unlinks the tracker's own files, so links to other files the switch-over deletes (languages-ng's CLAUDE.md and its bin/tests/issues-*.bats) were left dangling until review caught them.

From PR #6 review (Copilot): containerEnv's safe.directory for the repo itself was hard-coded (/workspaces/plcc-ng-demo) while postCreateCommand uses ${containerWorkspaceFolder}; a renamed checkout would fail the git status assertion. Fixed here. plcc-ng and languages-ng hard-code the same value (/workspaces/plcc-ng, /workspaces/languages-ng) and could take the same fix.
<!-- SECTION:NOTES:END -->
