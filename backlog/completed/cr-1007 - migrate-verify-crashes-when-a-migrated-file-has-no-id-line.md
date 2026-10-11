---
id: CR-1007
title: 'migrate verify crashes when a migrated file has no id: line'
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 12:35'
updated_date: '2026-10-10 19:14'
labels: []
milestone: m-0
dependencies: []
type: chore
project: dev
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
[verify.py](../../migrate/verify.py) calls `ID_RE.search(...).group(1)` on every task and draft file. A file without an `id:` line makes `search` return `None`, and verify dies with `AttributeError` instead of reporting which file is broken, which is the case it most needs to explain.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A file without an id: line in its frontmatter is reported as a verification failure that names the file
- [x] #2 verify exits non-zero in that case and still checks the remaining files
- [x] #3 A test covers a task file and a draft file without an id: line
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Changed migrate/verify.py to read each migrated task's and draft's id from its frontmatter only; a file without one is reported as "<folder>/<file>: no id: line in frontmatter", the remaining files are still checked, and main() exits 1. Verified by migrate/tests/test_verify.py: test_verify_reports_files_without_id (task + draft, both reported), test_verify_ignores_id_line_outside_frontmatter, test_main_exits_nonzero_on_missing_id; all pass on merged main (PR ourPLCC/change-requests#1).
<!-- SECTION:FINAL_SUMMARY:END -->
