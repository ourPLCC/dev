---
id: CR-540
title: 'OBJ test coverage gaps, and the 59-example sweep is not in the harness'
status: To Do
assignee: []
created_date: '2026-08-12'
labels: []
dependencies: []
type: test
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
### Summary

OBJ's seven committed test cases never exercise `/`, `add1`, `sub1`,
`zero?`, `exit`, the six comparison prims, `!@`, `@@`, `letrec`, `if`, or
any prim arity/type error path — verified correct by hand, so a
regression-detection gap rather than a known bug. Separately, the
migration's strongest evidence of fidelity, a 59-example × 3-target
byte-identity sweep, ran from a `/tmp` throwaway script and is not wired
into `bin/test.bash`.

### Description

Two related gaps in OBJ's test coverage, filed together since closing
either one touches the same seven-case suite under `src/OBJ/tests/`.

**Coverage gaps in the seven committed cases.** The seven cases
(`class/`, `objects/`, `inheritance/`, `lists/`, `strings-chars/`,
`env-ops/`, `errors/` — 47 program lines total) never exercise `/`,
`add1`, `sub1`, `zero?`, `exit`, the six comparison prims (`<? <=? >?
>=? <>? =?`), `!@`, `@@`, `letrec`, `if`, or any prim arity/type error
path. A reviewer verified these correct by hand during the final
branch review, so this is a regression-detection gap rather than a
known bug. Cheap to close: a handful more `.input`/`.expected` lines,
either extending existing cases or adding a new one.

**The 59-example cross-target sweep is not wired into the harness.**
The strongest evidence that this port is faithful to old PLCC is Task
5's byte-identity sweep across all 59 of OBJ's original example
programs, run on all three targets — but it ran from a throwaway
script in `/tmp`. Nothing in `bin/test.bash` re-runs it, so the
migration's best regression net currently exists nowhere durable.
Decide whether it becomes a committed, opt-in script (the suite's
runtime argues against making it part of the default run).

### Notes

The `.expected` files that already exist are genuinely load-bearing,
not filler — this issue is about widening coverage, not distrusting
what's there:

- `class/` pins static-vs-top-level shadowing.
- `strings-chars/` pins the output interleaving that breaks if anyone
  reverts a buffered output expression to printing (see the buffering
  entry in `dev-docs/course-material-impact.md`, `## OBJ`).
- `errors/` pins all three reserved-ID sites.

Found during the final whole-branch review of the OBJ migration
(issue CR-535).

Migrated from languages-ng #040.
<!-- SECTION:DESCRIPTION:END -->
