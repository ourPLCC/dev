---
id: CR-1015
title: 'migrate: convert languages-ng''s frontmatter-format tracker'
status: To Do
assignee: []
created_date: '2026-10-11 00:49'
labels: []
milestone: m-0
dependencies: []
references:
  - ../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md
type: chore
project: dev
ordinal: 4500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
migrate/ reads only plcc-ng's legacy issue format (**Type:**/**Date:** lines, closure by moving to done/). languages-ng's 53 issues use YAML frontmatter (type, target, upstream, opened, closed), mark closure with closed:, and add a ## Summary section, so CR-1000 cannot convert them. Converting by hand would mean about 380 link and #N rewrites across 48 files. The existing link rewriting, emitting, and verification code can be reused; only parsing and loading are new.

languages-ng prose also mixes three meanings of a bare #N: its own issues, its GitHub PRs, and plcc-ng issues (its issue 053 is about this). The plcc-ng rule (a legacy number means that issue, anything else is a GitHub URL) would guess wrong, so ambiguous references need a human decision rather than a heuristic.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 migrate converts a languages-ng checkout's dev-docs/issues/ into Backlog.md files at offset +500, taking status from closed:, the date from opened:, and the project from target: (this repo -> languages-ng, ourPLCC/plcc-ng -> plcc-ng)
- [ ] #2 A bare #N whose meaning is not certain is left as text and listed in the report with its surrounding text; it is never guessed
- [ ] #3 The triage file can record how each ambiguous #N resolves, which issues are duplicates of a plcc-ng CR (emitted Done + wontdo with a final summary naming that CR), open-issue triage, and type overrides; a re-run applies them
- [ ] #4 migrate/tests cover the new parser and loader, and the existing plcc-ng tests still pass
<!-- AC:END -->
