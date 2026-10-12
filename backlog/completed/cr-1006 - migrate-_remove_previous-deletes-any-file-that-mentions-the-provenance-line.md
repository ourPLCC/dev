---
id: CR-1006
title: migrate _remove_previous deletes any file that contains the provenance text
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 12:35'
updated_date: '2026-10-10 22:53'
labels: []
milestone: m-0
dependencies: []
type: chore
project: dev
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`_remove_previous` in [plcc_ng.py](../../migrate/plcc_ng.py) deletes every tracker file whose text contains `Migrated from <project> #` anywhere. Migrated CRs carry that line as the last line of their description (just before the description end marker), but nothing stops a later CR or a hand-edited note from quoting it, and a re-run of the migration would then delete a CR it never created. No file is affected today; the risk grows once more repos are migrated and their CRs are discussed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Only files whose description ends with the provenance line are removed on a re-run
- [x] #2 A test shows a CR that quotes the provenance line elsewhere in its text survives a re-run
- [x] #3 A test shows a previously migrated CR is still removed on a re-run
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Cleanup (_remove_previous) and migrate.verify now share one is_migrated predicate: a file counts as migrated only when its description ends with the provenance line, just before the description end marker. Verified by test_rerun_keeps_cr_that_quotes_provenance_line and test_rerun_removes_previously_migrated_cr (test_plcc_ng.py), test_verify_ignores_cr_that_quotes_provenance_line (test_verify.py), and by checking that the old and new predicates select the same 197 files in the live tracker. Merged in PRs #6 and #7.
<!-- SECTION:FINAL_SUMMARY:END -->
