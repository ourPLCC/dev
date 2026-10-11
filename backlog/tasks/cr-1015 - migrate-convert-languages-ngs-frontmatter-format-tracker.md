---
id: CR-1015
title: 'migrate: convert languages-ng''s frontmatter-format tracker'
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-11 00:49'
updated_date: '2026-10-11 13:28'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Smoke run against languages-ng main (26da95e) with the agreed triage: 53 files -> 42 completed / 10 tasks / 1 draft; 92 defaulted #N; 16 unresolved #N, all plcc-ng issue numbers written as 'upstream #N' or 'upstream's own #N' in 022, 036, 038, 048, 052 (185, 186, 187, 170, 189). For CR-1000: those 16 need references entries (likely all CR-N at +0). The run also found that a converted draft took a number an existing tracker draft already had; fixed on this branch (drafts now number after the highest existing one). plcc_ng.py has the same scheme but is not re-run.
<!-- SECTION:NOTES:END -->
