---
id: CR-1000
title: Migrate languages-ng's issue tracker to ourPLCC/dev
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 01:55'
updated_date: '2026-10-11 01:41'
labels: []
milestone: m-0
dependencies:
  - CR-1005
  - CR-1006
  - CR-1007
  - CR-1008
  - CR-1013
  - CR-1014
  - CR-1015
references:
  - ../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md
  - ../../dev-docs/specs/2026-10-11-languages-ng-migration-design.md
type: chore
project: languages-ng
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
languages-ng still keeps its own dev-docs/issues/ tracker (53 issues, frontmatter with closed: and target:). Moving it here puts all ourPLCC work in one tracker. Design: plcc-ng dev-docs/specs/2026-10-08-199-central-tracker-design.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Legacy issues converted at offset +500 per the languages-ng migration spec: completed/ 42, tasks/ 10, drafts/ 1; verify.py, backlog doctor, and bin/check.py are clean
- [ ] #2 The issues copied into plcc-ng by hand become Done + wontdo with project plcc-ng and a final summary naming the plcc-ng CR: 003->CR-162, 004->CR-163, 006->CR-164, 010->CR-174, 022->CR-185, 036->CR-186, 037->CR-187, 038->CR-188
- [ ] #3 Open issues 020, 043, 050, 051, 053 become Done + wontdo as obsolete; 046 is In Progress; 042 is a draft; the other open issues are To Do; every N>53 bare #N reference has a triage decision
- [ ] #4 languages-ng's devcontainer, AGENTS.md, and CONTRIBUTING.md follow plcc-ng's layout: the devcontainer clones and mounts ../dev at /workspaces/dev with BACKLOG_CWD set and mounts a languages-ng-claude volume at ~/.claude, AGENTS.md imports ../dev/ORG-AGENTS.md, ../dev/CONTRIBUTING.md, then CONTRIBUTING.md, and CONTRIBUTING.md opens with the link to the org developer guide; its old tracker is removed and grep finds no dev-docs/issues reference outside .git
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Notes for whoever migrates languages-ng:
- The devcontainer named volume for ~/.claude is called plcc-ng-claude; use a per-repo name (e.g. languages-ng-claude) when copying the devcontainer setup.
- The containerEnv GIT_CONFIG_* safe.directory entries must name that repo's own path.
- migrate/ caveats before reuse: plcc_ng.assign_ids hardcodes the 400-499 range guard although offset is a parameter (generalize per repo); _remove_previous matches the provenance prefix anywhere in a file (anchor it to the last line); verify crashes with AttributeError if a migrated file lacks id:; type_overrides keyed by legacy number applies to both files of a duplicate-number pair.

Correction to the _remove_previous caveat above: the provenance line ends the description section (before SECTION:DESCRIPTION:END), not the file. Tracked as CR-1006.

From CR-1005: assign_ids now takes dup_offset and dup_range. The ID table reserves no duplicate-number range for languages-ng; if its legacy numbers repeat, pick a range inside CR-501..CR-699 and record it in dev-docs/tracker.md.
<!-- SECTION:NOTES:END -->
