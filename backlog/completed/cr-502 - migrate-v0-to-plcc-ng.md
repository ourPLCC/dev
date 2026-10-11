---
id: CR-502
title: 'migrate-v0-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-07-22'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port V0's grammar to `plcc-ng` syntax and add Python, Java, and
JavaScript semantics (today only Java exists, under old PLCC). V0 is the
migration's syntax pathfinder: it has no semantics beyond printing the
parsed expression and no `Env` dependency, so it's the cheapest place to
validate the per-language directory layout (shared `grammar.plcc` plus
`python/`, `java/`, `javascript/` subdirectories) and the `.bats` test
convention (one shared expected-output fixture per test case, asserted
against by all three targets) before they fan out to 13 more languages.

### Notes

See [dev-docs/specs/2026-07-22-plcc-ng-migration-design.md](../../../languages-ng/dev-docs/specs/2026-07-22-plcc-ng-migration-design.md),
including its "Addendum: Validated Syntax Facts" section, for concrete
syntax rules this migration must follow (the `_run()` print-vs-return
split between targets, and the `VAR` field-rename rule for JavaScript
compatibility).

Migrated from languages-ng #002.
<!-- SECTION:DESCRIPTION:END -->
