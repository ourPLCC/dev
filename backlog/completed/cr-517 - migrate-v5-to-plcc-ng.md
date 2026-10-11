---
id: CR-517
title: 'migrate-v5-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-07-31'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port V5's grammar and Java semantics (today under old PLCC) to plcc-ng
syntax, and add Python and JavaScript semantics alongside it. V5 is
V4 + letrec: it adds the LETREC token, the <Exp:LetrecExp> production,
and LetDecls.addLetrecBindings, which builds a recursive scope by
extending the environment with an empty Bindings and then mutating that
node as each right-hand side is evaluated. It reuses the envVal Env
variant and every other V4 class without modification. V6 is explicitly
out of scope.

### Notes

See [dev-docs/specs/2026-07-31-plcc-ng-v5-design.md](../../../languages-ng/dev-docs/specs/2026-07-31-plcc-ng-v5-design.md)
and [dev-docs/plans/2026-07-31-plcc-ng-phase2-v5.md](../../../languages-ng/dev-docs/plans/2026-07-31-plcc-ng-phase2-v5.md).

Migrated from languages-ng #017.
<!-- SECTION:DESCRIPTION:END -->
