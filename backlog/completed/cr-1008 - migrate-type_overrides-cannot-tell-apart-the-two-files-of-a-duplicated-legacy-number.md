---
id: CR-1008
title: >-
  migrate type_overrides cannot tell apart the two files of a duplicated legacy
  number
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 12:35'
updated_date: '2026-10-10 23:44'
labels: []
milestone: m-0
dependencies: []
type: chore
project: dev
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`type_overrides` in the triage file is keyed by legacy issue number ([plcc_ng.py](../../migrate/plcc_ng.py), `_validate` and `convert`). When two legacy issues share a number (plcc-ng had three such pairs), an override meant for one file is also applied to the other, so the wrong type can be assigned silently.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A type override can target one file of a duplicated legacy number without affecting the other
- [x] #2 Overrides keyed by a plain number keep working for numbers that are not duplicated
- [x] #3 A test covers an override applied to only one file of a duplicate pair
- [x] #4 An open-issue triage entry can target one file of a duplicated legacy number
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Triage entries (open and type_overrides) are now looked up by file stem first, falling back to the plain number only when it is not duplicated; plain-number keys that name a duplicated number are rejected (PR #8). Verified by tests in migrate/tests/test_plcc_ng.py: test_type_override_by_stem_targets_one_duplicate (AC1, AC3), test_unmapped_type_needs_override (AC2), test_open_entry_by_stem_targets_one_duplicate (AC4), plus the ambiguous-key and unpadded-stem tests; re-running the plcc-ng migration gave byte-identical output.
<!-- SECTION:FINAL_SUMMARY:END -->
