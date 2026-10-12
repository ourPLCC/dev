---
id: CR-1003
title: Add a parse-table-level regression test for the FOLLOW-set nullable-tail fix
status: To Do
assignee: []
created_date: '2026-10-09 11:31'
updated_date: '2026-10-12 18:24'
labels: []
dependencies: []
type: test
project: plcc-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CR-188's regression test guards the FOLLOW-set computation directly (`test_follow_set_walks_past_nullable_symbol_to_next_non_nullable` in `build_follow_sets_test.py`). The harm CR-188 described was one layer up: a dropped parse-table entry for an empty alternative, silently accepted by `plcc-ll1` as `is_ll1: true`. A test at the parse-table layer ([build_parsing_table_test.py](../../../plcc-ng/src/plcc/spec/syntax/validations/ll1/build_parsing_table_test.py), which already has `createGrammar` and `getCell` helpers) would catch a regression where a spec author would notice it, without the cost of a full end-to-end test. Flagged as a Minor suggestion in the final review of the CR-188 fix. Originally filed as plcc-ng #191 on the unmerged branch worktree-follow-set-fix-followups (59e60012), never merged; that number now belongs to CR-191.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A test in build_parsing_table_test.py uses a grammar shaped like S -> A B C, A -> a | ε, B -> b | ε, C -> c
- [ ] #2 It asserts that each empty alternative has a parse-table cell for every token in its FOLLOW set
- [ ] #3 The test fails if the pre-CR-188 single-symbol lookahead is restored
<!-- AC:END -->
