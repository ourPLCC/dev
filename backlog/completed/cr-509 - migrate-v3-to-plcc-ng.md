---
id: CR-509
title: 'migrate-v3-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-07-28'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port V3's grammar and Java semantics (today under old PLCC) to plcc-ng
syntax, and add Python and JavaScript semantics alongside it. V3 is
V2 + let: it introduces the envVal Env variant (ported once here and
reused by V4-V6), keeping checkDuplicates and the two-list Bindings
constructor that envRN dropped, and adds the LetExp/LetDecls productions
and their semantics. V4-V6 are explicitly out of scope for this issue.

### Notes

See [dev-docs/specs/2026-07-28-plcc-ng-v3-design.md](../../../languages-ng/dev-docs/specs/2026-07-28-plcc-ng-v3-design.md)
and [dev-docs/plans/2026-07-28-plcc-ng-phase2-v3.md](../../../languages-ng/dev-docs/plans/2026-07-28-plcc-ng-phase2-v3.md).

Migrated from languages-ng #009.
<!-- SECTION:DESCRIPTION:END -->
