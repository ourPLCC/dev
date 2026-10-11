---
id: CR-1013
title: Rename the tracker repo to ourPLCC/dev
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-10 18:33'
updated_date: '2026-10-10 19:21'
labels: []
milestone: m-0
dependencies:
  - CR-1012
references:
  - ../../dev-docs/specs/2026-10-10-org-developer-docs-design.md
type: chore
project: dev
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once this repo holds the org developer guide, specs, and agent rules as well as the tracker, its name describes only half of it, and a newcomer would not look in a repo called change-requests for how we work. The name appears in every devcontainer path, so it changes before the remaining repos are set up against it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The GitHub repository is ourPLCC/dev
- [x] #2 backlog/config.yml lists the project value dev in place of change-requests, every CR that had project change-requests has project dev, and bin/check.py passes
- [x] #3 The repo's current docs, tooling, and CI refer to it as dev; records of past work (closed CRs, migration reports) are left as written
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CR-1009 AC #4 still says CLAUDE.md and contributing docs point to the tracker README; since CR-1012 the layout is AGENTS.md importing the org CONTRIBUTING.md, so that criterion needs rewriting to match CR-1014's.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Renamed the GitHub repository to ourPLCC/dev (verified: the GitHub API returns full_name ourPLCC/dev and the old URL 301-redirects to it). Replaced the project value change-requests with dev in backlog/config.yml and moved all nine CRs that had it (CR-1004-1008, CR-1010-1013) to dev; bin/check.py, both unittest suites, and backlog doctor pass. Updated dev-docs/tracker.md (host folder, /workspaces/dev mount, BACKLOG_CWD, project list) and open work naming the repo (CR-1000, CR-1001 titles; CR-1009 AC #1; CR-1010 AC #4; the one draft). Left as written: the merged spec, migrate/reports/, closed CR text, and CR-1014 AC #6. Notes triaged: the stale CR-1009 AC #4 was rewritten for the AGENTS.md layout. Merged in PR #3.
<!-- SECTION:FINAL_SUMMARY:END -->
