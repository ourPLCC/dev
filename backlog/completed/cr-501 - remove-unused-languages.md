---
id: CR-501
title: 'remove-unused-languages'
status: Done
assignee: []
created_date: '2026-07-22'
labels: []
dependencies: []
type: chore
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove all `src/` languages not used in current course materials, so the
repository only contains the 14 languages being migrated to `plcc-ng`
(V0–V6, SET, REF, NAME, NEED, TYPE0, TYPE1, OBJ) plus the `Env` library.
Also removes the two `Env` variants (`envSimple`, `envRefCD`) that none
of the kept languages use.

### Notes

See [dev-docs/specs/2026-07-22-plcc-ng-migration-design.md](../../../languages-ng/dev-docs/specs/2026-07-22-plcc-ng-migration-design.md)
for the full migration design and phase order. Removed languages remain
recoverable from the original `ourPLCC/languages` repository's history if
ever needed.

Migrated from languages-ng #001.
<!-- SECTION:DESCRIPTION:END -->
