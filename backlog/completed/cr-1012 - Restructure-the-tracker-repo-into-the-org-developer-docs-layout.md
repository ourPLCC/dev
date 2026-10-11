---
id: CR-1012
title: Restructure the tracker repo into the org developer-docs layout
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-10 18:33'
updated_date: '2026-10-10 19:14'
labels: []
milestone: m-0
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-10-org-developer-docs-design.md
type: docs
project: dev
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Material that applies to every ourPLCC repo has no home. Workflow rules are restated in each repo's CONTRIBUTING.md and CLAUDE.md and in this repo's README, and the copies drift; a decision binding several repos has nowhere to go; a new repo starts by copying another's docs. This repo is already cloned beside every code repo and mounted in every devcontainer, and its README already carries workflow policy beyond tracker mechanics, so it becomes the home of the org developer guide, org-wide specs, and agent rules, alongside the tracker.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.md says what the repo is and sends readers to CONTRIBUTING.md
- [x] #2 CONTRIBUTING.md is the org developer guide: how work flows from issue to merged PR, branch naming, commit style, the precedence rule (repos deviate only explicitly and with a reason), and a short summary of tracking that links to dev-docs/tracker.md
- [x] #3 ORG-AGENTS.md holds only agent-specific rules for every ourPLCC repo, opening with the test for what belongs there versus CONTRIBUTING.md or dev-docs/, then agent mechanics and limits on autonomy; AGENTS.md loads ORG-AGENTS.md, CONTRIBUTING.md, and dev-docs/tracker.md
- [x] #4 dev-docs/tracker.md holds the tracker-specific content of the old README, including notes on working on the tracker tooling; nothing in the old README is lost
- [x] #5 dev-docs/specs/ holds the org developer docs design spec
- [x] #6 bin/check.py and CI pass
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Split the README into README.md, CONTRIBUTING.md (org guide), ORG-AGENTS.md, AGENTS.md, and dev-docs/tracker.md, and added the org developer docs spec, amended to keep org agent rules in ORG-AGENTS.md. Verified by a sentence-by-sentence no-loss check against the old README, a link check, the unit tests, bin/check.py, backlog doctor, CI on the merge commit, and a Claude Code import test.
<!-- SECTION:FINAL_SUMMARY:END -->
