---
id: DRAFT-2
title: 'test.bash''s 75-minute run, and two implementers lost mid-task'
status: To Do
assignee: []
created_date: '2026-08-12'
labels: []
dependencies: []
type: chore
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
### Summary

A `bin/test.bash` run reached a correct `EXIT=0, 186/186, ok 186` but took
~75 minutes against a normal ~2 minutes, with no root cause established;
separately, two OBJ-migration implementer subagents were killed by
infrastructure mid-task (an API spend limit, a stall watchdog) but both
landed clean on verification. An observation, not a diagnosis — filed so the
record survives the worktree being deleted, in case it recurs.

### Description

**This is an observation, not a diagnosis.** Filed so the record
survives the OBJ-migration worktree being deleted (that ledger is
git-ignored), in case the slow-suite behavior recurs.

`bin/test.bash` ran to a correct, complete `EXIT=0, 186/186, ok 186`
but took **~75 minutes**, where every prior run of the same suite in
the same worktree took roughly two minutes. Observed 2026-08-12.
During the slow run it was progressing normally but slowly through
tests in alphabetical order; a single `plcc-rep` invocation timed at
1.4s, disk was 87% full with 7.8G free, load average was ~1.3, memory
4.2G/7.7G used, and no stray or runaway processes were found. **No
root cause was established. Ruled out: nothing conclusively.**

Separately, two of the OBJ-migration plan's six implementer subagents
were killed by infrastructure mid-task after committing but before
reporting: Task 3 by an API spend limit, Task 6 by a 600s stall
watchdog waiting on that slow suite run. Both were verified after the
fact by the controller and both landed clean, so this is not a finding
against the code — but it means two tasks have no independent
implementer attestation.

### Notes

Found during the final whole-branch review of the OBJ migration
(issue CR-535). If this recurs on a future language's suite run, this
issue is where to add the next data point. If it never recurs, close
it.

Migrated from languages-ng #042.
<!-- SECTION:DESCRIPTION:END -->
