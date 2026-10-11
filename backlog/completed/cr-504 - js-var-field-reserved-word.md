---
id: CR-504
title: 'js-var-field-reserved-word'
status: Done
assignee: []
created_date: '2026-07-22'
labels:
  - wontdo
dependencies: []
type: docs
project: plcc-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A grammar token captured with its auto-generated field name colliding
with a JavaScript reserved word produces JavaScript that fails to load.
Specifically, `<VAR>` (no explicit `:fieldname`) auto-names its field
`var`, and the JavaScript target's generated constructor uses that name
as a parameter (`constructor(var) { ... }`), which is a `SyntaxError` in
JavaScript (`var` is reserved).

### Steps to Reproduce

1. Grammar with `token VAR '[A-Za-z]\w*'` and `<Exp:VarExp> ::= <VAR>`
   (no explicit field name), targeting `javascript`.
2. `echo "x" | plcc-rep`
3. Actual: `SyntaxError: Unexpected token 'var'` while loading the
   generated `VarExp.js`. Expected: it runs, same as the Python/Java
   targets do with the same grammar.

Renaming the capture (e.g. `<VAR:name>`) works around it. Since `VAR` is
the conventional token name for identifiers across all of this repo's
languages, this repo now renames it everywhere a grammar is shared across
targets, rather than special-casing JavaScript.

### Notes

Found while validating [dev-docs/plans/2026-07-22-plcc-ng-phase0-phase1.md](../../../languages-ng/dev-docs/plans/2026-07-22-plcc-ng-phase0-phase1.md).
`plcc-ng` might reasonably want to either reject/rename reserved-word
field names at generation time, or document the restriction. Not filed
upstream yet — needs the repo owner's go-ahead first.

**Resolved in plcc-ng 2.0.0:** the tool now reports a reserved-word field
collision as a specification error. Repo renamed the token `VAR` → `SYMBOL`
so the field is `symbol` (never `var`) across all targets. Upstream shipped
the detection, so filing upstream is moot.

Migrated from languages-ng #004.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Duplicate of CR-163, filed upstream by hand.
<!-- SECTION:FINAL_SUMMARY:END -->
