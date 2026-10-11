---
id: CR-507
title: 'migrate-v2-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-07-23'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port V2's grammar and Java semantics (today under old PLCC) to plcc-ng
syntax, and add Python and JavaScript semantics alongside it. V2 is
V1 + IfExp: it reuses the envRN Env variant and V1's Prim/Val unchanged,
adding only the IfExp grammar production and its semantics. V3–V6 are
explicitly out of scope for this issue.

### Notes

See [dev-docs/specs/2026-07-22-plcc-ng-migration-design.md](../../../languages-ng/dev-docs/specs/2026-07-22-plcc-ng-migration-design.md),
[dev-docs/plans/2026-07-23-plcc-ng-phase2-v2.md](../../../languages-ng/dev-docs/plans/2026-07-23-plcc-ng-phase2-v2.md),
and CR-506 (IfExp's
repeated-capture alt-names must be all-lowercase).

Migrated from languages-ng #007.
<!-- SECTION:DESCRIPTION:END -->
