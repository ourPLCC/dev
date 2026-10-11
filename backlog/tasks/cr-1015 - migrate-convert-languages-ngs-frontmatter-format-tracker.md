---
id: CR-1015
title: 'migrate: convert languages-ng''s frontmatter-format tracker'
status: To Do
assignee: []
created_date: '2026-10-11 00:49'
updated_date: '2026-10-11 01:41'
labels: []
milestone: m-0
dependencies: []
references:
  - ../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md
  - ../../dev-docs/specs/2026-10-11-languages-ng-migration-design.md
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
- [ ] #1 migrate converts a languages-ng checkout's dev-docs/issues/ into Backlog.md files at offset +500, taking status from closed:, the date from opened:, and the project from target: (this repo -> languages-ng, ourPLCC/plcc-ng -> plcc-ng); unknown frontmatter keys or targets stop the run
- [ ] #2 Bare #N is resolved by context: PR #N -> the languages-ng PR URL; plcc-ng-qualified -> CR-N; unqualified N<=53 -> CR-<N+500>, listed in the report as defaulted; unqualified N>53 left as text and listed with its surrounding text, never guessed
- [ ] #3 The triage file records duplicates (emitted Done + wontdo, project plcc-ng, the plcc-ng issue's type, final summary naming its CR), N>53 reference decisions, open-issue triage, and type overrides; a re-run applies them, and verify.py fails while any N>53 reference has no entry
- [ ] #4 verify.py and citations.py take the repo's driver as a parameter; migrate/tests cover the new parser, loader, #N rules, and triage application, and the existing plcc-ng tests still pass
<!-- AC:END -->
