---
id: CR-505
title: 'migrate-v1-to-plcc-ng'
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
Port V1's grammar and Java semantics (today under old PLCC) to plcc-ng
syntax, and add Python and JavaScript semantics alongside it. V1 is the
first kept language that depends on `Env`, so this issue also ports the
`envRN` variant into the shared `src/Env/envRN/<target>/` location V2
will later reuse via `%include`. V2–V6 are explicitly out of scope for
this issue.

### Notes

See [dev-docs/specs/2026-07-22-plcc-ng-migration-design.md](../../../languages-ng/dev-docs/specs/2026-07-22-plcc-ng-migration-design.md)
and [dev-docs/plans/2026-07-22-plcc-ng-phase2-v1.md](../../../languages-ng/dev-docs/plans/2026-07-22-plcc-ng-phase2-v1.md).

Migrated from languages-ng #005.
<!-- SECTION:DESCRIPTION:END -->
