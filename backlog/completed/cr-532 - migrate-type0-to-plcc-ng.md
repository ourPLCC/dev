---
id: CR-532
title: 'migrate-type0-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-08-10'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port TYPE0 (`REF + type declarations, but no type checking`) to plcc-ng: one
shared `src/TYPE0/grammar.plcc` plus three target `spec.plcc`s (Python, Java,
JavaScript). TYPE0 forks from REF, not NEED — it has no `ThunkRef` and no
`ValRORef`.

The grammar delta over REF's shipped `grammar.plcc` is fourteen new tokens
and thirteen new productions (six relational operators, four type-syntax
tokens, four type keywords; five new type productions, `<Proc>`/`<Formals>`
gaining type annotations, two new literal expressions, six new `<Prim>`
alternatives), plus the standing `VAR` → `SYMBOL` rename and one typo fix:
`BoolPrimtype` → `BoolPrimType`, matching TYPE1's existing spelling.

The semantics are a four-hunk delta over REF, all following from TYPE0
having a real boolean type where REF does not: a new free-standing `BoolVal`
`Val` subclass; strict booleans (`Val.isTrue()` now throws
`boolean expression expected`, `Val.boolVal()` is added, `IntVal` loses its
`isTrue()` override); `ZeropPrim` returns a `BoolVal` instead of an `IntVal`;
and `TrueExp`/`FalseExp` plus six new relational prims (`<?`, `<=?`, `>?`,
`>=?`, `=?`, `<>?`). A fifth, unrelated change adds `LetDecls:init` (TYPE0's
pre-migration source is missing the duplicate-ID check every other ported
language has).

Three targets, four value-only test cases (`relational-prims/`,
`boolean-literals/`, `type-annotations-ignored/`,
`declared-type-not-checked/`), and — matching pre-migration TYPE0 — no
`Prog/` directory.

### Notes

See
[dev-docs/specs/2026-08-06-plcc-ng-type0-design.md](../../../languages-ng/dev-docs/specs/2026-08-06-plcc-ng-type0-design.md),
which extends
[dev-docs/specs/2026-07-22-plcc-ng-migration-design.md](../../../languages-ng/dev-docs/specs/2026-07-22-plcc-ng-migration-design.md)
and builds directly on
[dev-docs/specs/2026-08-04-plcc-ng-ref-design.md](../../../languages-ng/dev-docs/specs/2026-08-04-plcc-ng-ref-design.md).

The type nonterminals — `TypeExp`, `PrimTypeExp`, `ProcTypeExp`, `PrimType`,
`BoolPrimType`, `IntPrimType`, `TypeExps` — deliberately carry **no
semantics at all**: zero `%%%` blocks in all three `spec.plcc`s. They are
generated, populated by the parser, and never read by the evaluator. That is
TYPE0's whole thesis stated structurally, not a gap to fill in.

Out of scope: TYPE1 and OBJ; any type checking whatsoever; any `toString`,
`equals`, or other method on the type nonterminals; error-path and
diagnostic tests (strict `isTrue`'s `boolean expression expected`,
`boolVal`'s `not a Bool`, and `LetDecls:init`'s duplicate-ID message); any
`Prog/` directory for TYPE0; reordering the lexical section; and issue
CR-516 (cross-target integer
divergence), issue CR-519 (Python recursion
ceiling), issue
CR-522 (plcc-rep parses
each SOURCE argument independently), and issue
CR-531 (suite
exhausts disk and reports a spurious failure) — all repo-wide and
inherited.

Migrated from languages-ng #032.
<!-- SECTION:DESCRIPTION:END -->
