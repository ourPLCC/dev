---
id: CR-523
title: 'migrate-set-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-08-04'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port SET (`V6 + references/set`) to plcc-ng syntax: one shared
`grammar.plcc` plus three target `spec.plcc`s (Python, Java, JavaScript).
SET opens Phase 3 and does two jobs rather than one:

- Ports SET itself. The grammar is V6's plus one token (`SET`) and one
  production (`<Exp:SetExp> ::= SET <SYMBOL> EQUALS <Exp>`), each in the
  position the original grammar put it. Every V6 semantic class is reused;
  the delta is `Ref`/`ValRef` as free-standing per-language classes,
  `ProcVal.apply`/`LetDecls`/`Define._run` binding `Ref`s instead of `Val`s,
  and the new `SetExp.eval`.
- Ports **`envRef`** — the Env variant shared by all four Phase 3 languages
  (SET, REF, NAME, NEED) and, in extended form, by TYPE0, TYPE1, and OBJ.
  `envRef` is `envVal` with one level of indirection: a `Binding` holds a
  `Ref` rather than a `Val`, so a binding's value can be mutated in place
  (`Binding.ref`, `applyEnvRef`, `extendEnvRef`, `Bindings(idList,
  refList)`). It lives at `src/Env/envRef/<target>/env.plcc` and is
  `%include`d unchanged by REF, NAME, and NEED.

Four value-only test cases, each measured against a real spike run before
being written down (see the design doc): `let/` (`set` on a `let`-bound
variable, → `43`), `counter/` (`set` on a closure-captured binding, from
`Prog/g`, → `3`), `formal-is-a-copy/` (`set` on a formal does not reach the
caller, → `3`), and `define-then-set/` (`set` on a persistent top-level
`define` binding, and the only case where `set` returns its assigned
value, → `x` / `2` / `2`).

`formal-is-a-copy/` deliberately ships the same program REF will use, where
REF's expected output is `4` instead of `3` — the SET→REF contrast is the
entire point of REF, so it should not be dropped from SET as redundant.

Two convergence decisions, settled before this phase so they don't drift
across REF/NAME/NEED behind it: `Val.apply`/`ProcVal.apply` keep the
`Env` parameter added in V4-V6 even though nothing reads it yet — it is the
seam for a homework assignment (reimplementing `proc` with dynamic
scoping) and must not be removed as dead code. And Java's `Prim.apply`
takes `Val[] va` (not `List<Val> args`), matching how Python and
JavaScript already index operands; V1-V6's Java specs are retro-fixed to
this shape in the same phase, ahead of SET's own `spec.plcc`, since this
is the last checkpoint before the shape fans out across seven more
languages.

Baseline measured today with a full `bin/test.bash` run: 70 tests, 63
passing, 7 failing (NAME, NEED, OBJ, REF, SET, TYPE0, TYPE1 — all `plccmk:
command not found`). After this phase: 81 tests (70, minus SET's 1 old
test, plus 12 new — 4 cases × 3 targets), 75 passing, 6 failing — the same
`command not found` set minus SET.

### Notes

See
[dev-docs/specs/2026-08-04-plcc-ng-set-design.md](../../../languages-ng/dev-docs/specs/2026-08-04-plcc-ng-set-design.md),
which extends
[dev-docs/specs/2026-07-22-plcc-ng-migration-design.md](../../../languages-ng/dev-docs/specs/2026-07-22-plcc-ng-migration-design.md)
and builds on
[dev-docs/specs/2026-08-03-plcc-ng-v6-design.md](../../../languages-ng/dev-docs/specs/2026-08-03-plcc-ng-v6-design.md).

Out of scope for this issue: REF, NAME, and NEED and the
`evalRef`/`ThunkRef`/`ValRORef` work they add; TYPE0, TYPE1, and OBJ;
error-path and diagnostic tests; issue
CR-516 (cross-target integer
divergence) and issue CR-519 (Python
recursion ceiling), both repo-wide and inherited from V0; and any
unification of the Env variants or the per-language
`Val`/`IntVal`/`Prim`/`Ref` duplication.

Migrated from languages-ng #023.
<!-- SECTION:DESCRIPTION:END -->
