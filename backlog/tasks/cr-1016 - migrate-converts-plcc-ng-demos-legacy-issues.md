---
id: CR-1016
title: migrate converts plcc-ng-demo's legacy issues
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-11 16:08'
updated_date: '2026-10-11 16:08'
labels: []
dependencies:
  - CR-1013
type: chore
project: dev
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CR-1001 needs plcc-ng-demo's five legacy issues converted at offset +800 (CR-801..CR-805). Its issues use plcc-ng's file format, but migrate/plcc_ng.py is hard-coded to the plcc-ng project and offset 0, and the backlog CLI cannot create CRs with chosen IDs. Three of the five (001, 002, 005) were hand-copied into plcc-ng as CR-159, CR-160, CR-161 and must become Done + wontdo duplicates, which the plcc-ng driver cannot express for closed issues.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 migrate converts plcc-ng-demo's dev-docs/issues/ into CR-801..CR-805 with project, provenance, and links set for plcc-ng-demo
- [ ] #2 A triage entry marks a legacy issue as a duplicate of a plcc-ng CR: Done + wontdo, project plcc-ng, final summary naming the CR
- [ ] #3 verify, citations, and repo_links run with --driver plcc-ng-demo / --project plcc-ng-demo
- [ ] #4 plcc-ng and languages-ng migrate tests still pass; new behavior has tests
<!-- AC:END -->
