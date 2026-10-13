---
id: CR-1016
title: migrate converts plcc-ng-demo's legacy issues
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-11 16:08'
updated_date: '2026-10-11 18:24'
labels: []
dependencies:
  - CR-1013
references:
  - ../../dev-docs/specs/2026-10-11-plcc-ng-demo-migration-design.md
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
- [x] #1 migrate converts plcc-ng-demo's dev-docs/issues/ into CR-801..CR-805 with project, provenance, and links set for plcc-ng-demo
- [x] #2 A triage entry marks a legacy issue as a duplicate of a plcc-ng CR: Done + wontdo, project plcc-ng, final summary naming the CR
- [x] #3 verify, citations, and repo_links run with --driver plcc-ng-demo / --project plcc-ng-demo
- [x] #4 plcc-ng and languages-ng migrate tests still pass; new behavior has tests
- [x] #5 migrate/plcc-ng-demo-triage.json records the spec's triage, and the converted CRs match its expected counts (completed/ 5)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Changed migrate/plcc_ng.py to take a Profile (project, offsets, GitHub URL, provenance) defaulting to plcc-ng, added an optional duplicates triage table (Done + wontdo, project plcc-ng, the upstream CR's type), and added the migrate.plcc_ng_demo driver at offset +800 with migrate/plcc-ng-demo-triage.json; spec dev-docs/specs/2026-10-11-plcc-ng-demo-migration-design.md. Verified by 122 passing migrate tests (13 new; plcc-ng and languages-ng unchanged), CI and Copilot review on PR #11, the real conversion from plcc-ng-demo af68048 producing CR-801..CR-805 in completed/ (5, as expected) with migrate.verify ok, and citations/repo_links running with the plcc-ng-demo driver.
<!-- SECTION:FINAL_SUMMARY:END -->
