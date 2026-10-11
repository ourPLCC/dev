---
id: CR-521
title: 'migrate-v6-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-08-03'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port V6's grammar and Java semantics (today under old PLCC) to plcc-ng
syntax, and add Python and JavaScript semantics alongside it. V6 is
V5 + top-level define: it adds the DEFINE token and splits <Program>
into Define and Eval alternatives. A define mutates a single Program-level
environment node that persists across every program in one plcc-rep run,
so a redefinition is visible through closures that already captured that
node. It reuses the envVal Env variant and every other V5 class without
modification.

This is the last language in Phase 2.

### Notes

See [dev-docs/specs/2026-08-03-plcc-ng-v6-design.md](../../../languages-ng/dev-docs/specs/2026-08-03-plcc-ng-v6-design.md)
and [dev-docs/plans/2026-08-03-plcc-ng-phase2-v6.md](../../../languages-ng/dev-docs/plans/2026-08-03-plcc-ng-phase2-v6.md).

Migrated from languages-ng #021.
<!-- SECTION:DESCRIPTION:END -->
