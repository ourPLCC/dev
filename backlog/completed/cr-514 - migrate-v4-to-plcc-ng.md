---
id: CR-514
title: 'migrate-v4-to-plcc-ng'
status: Done
assignee: []
created_date: '2026-07-30'
labels: []
dependencies: []
type: feat
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port V4's grammar and Java semantics (today under old PLCC) to plcc-ng
syntax, and add Python and JavaScript semantics alongside it. V4 is
V3 + procedures and the sequence operator: it adds the ProcExp/AppExp/
SeqExp productions, the Proc/Formals/SeqExps nonterminals, and the
ProcVal closure class, reusing the envVal Env variant V3 introduced
without modification. It is also the first migrated language with a
Prog/ directory of example programs, so this issue also verifies those
against all three targets. V5-V6 are explicitly out of scope.

### Notes

See [dev-docs/specs/2026-07-30-plcc-ng-v4-design.md](../../../languages-ng/dev-docs/specs/2026-07-30-plcc-ng-v4-design.md)
and [dev-docs/plans/2026-07-30-plcc-ng-phase2-v4.md](../../../languages-ng/dev-docs/plans/2026-07-30-plcc-ng-phase2-v4.md).

Migrated from languages-ng #014.
<!-- SECTION:DESCRIPTION:END -->
