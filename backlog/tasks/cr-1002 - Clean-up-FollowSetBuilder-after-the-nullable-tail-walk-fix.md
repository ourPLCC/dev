---
id: CR-1002
title: Clean up FollowSetBuilder after the nullable-tail walk fix
status: To Do
assignee: []
created_date: '2026-10-09 11:31'
updated_date: '2026-10-12 18:24'
labels: []
dependencies:
  - CR-1003
type: refactor
project: plcc-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CR-188 replaced a single-symbol lookahead in [FollowSetBuilder](../../../plcc-ng/src/plcc/spec/syntax/validations/ll1/build_follow_sets.py) with a forward walk. The fix was deliberately minimal and left three stale pieces: `_isLastOccuranceInRule` and the if/else around it are now dead branching (the loop's else clause already covers the last-occurrence case); `_addFirstOfNextSymbol` is now called for symbols arbitrarily far past "next", so its name misleads; `_canDeriveEmpty([rules[j]])` wraps a single symbol in a list at its only call site. Pure cleanup, no behavior change. Flagged in the final review of the CR-188 fix. Originally filed as plcc-ng #190 on the unmerged branch worktree-follow-set-fix-followups (59e60012), never merged; that number now belongs to CR-190.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `_isLastOccuranceInRule` and its if/else split are removed; the method is just the forward walk
- [ ] #2 The FIRST-of-symbol helper is renamed to reflect any later symbol (e.g. `_addFirstOfSymbol(symbol, nonterminal)`)
- [ ] #3 A single-symbol nullable check (e.g. `_isNullable(symbol)`) replaces the list-wrapped `_canDeriveEmpty` call
- [ ] #4 Existing `build_follow_sets_test.py` passes unchanged
- [ ] #5 _isLastOccuranceInRule and its if/else are removed; the forward walk alone handles a symbol at the end of a production
- [ ] #6 The FIRST-adding helper and the nullability check are named for what they do, and the nullability check takes a single symbol
- [ ] #7 No behavior change: all existing LL(1) unit tests pass unchanged, including the CR-1003 parse-table test
<!-- AC:END -->
