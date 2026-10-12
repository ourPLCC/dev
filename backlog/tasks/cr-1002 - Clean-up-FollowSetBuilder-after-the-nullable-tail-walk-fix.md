---
id: CR-1002
title: Clean up FollowSetBuilder after the nullable-tail walk fix
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 11:31'
updated_date: '2026-10-12 21:39'
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
- [x] #1 `_isLastOccuranceInRule` and its if/else split are removed; the method is just the forward walk
- [x] #2 The FIRST-of-symbol helper is renamed to reflect any later symbol (e.g. `_addFirstOfSymbol(symbol, nonterminal)`)
- [x] #3 A single-symbol nullable check (e.g. `_isNullable(symbol)`) replaces the list-wrapped `_canDeriveEmpty` call
- [x] #4 Existing `build_follow_sets_test.py` passes unchanged
- [x] #5 No behavior change: all existing LL(1) unit tests pass unchanged, including the CR-1003 parse-table test
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Merged in plcc-ng PR #336 (commit 8b845fc3). FollowSetBuilder's occurrence update is now just the forward walk: _isLastOccuranceInRule and its if/else are gone (an empty tail falls through to the loop's else and adds FOLLOW(lhs)). _addFirstOfNextSymbol is renamed _addFirstOfSymbol, the list-wrapped _canDeriveEmpty is replaced by single-symbol _isNullable, and the rules parameter is renamed production. No tests changed. Unit tests: 1265 passed, 1 skipped, the same before and after; that run includes build_follow_sets_test.py and the CR-1003 parse-table test. bin/test/functional.bash exits 0.
<!-- SECTION:FINAL_SUMMARY:END -->
