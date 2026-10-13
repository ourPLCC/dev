---
id: CR-1022
title: Split tracker data into ourPLCC/change-requests
status: To Do
assignee: []
created_date: '2026-10-13 13:53'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: dev
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Containers are getting push access, and tracker changes are pushed straight to dev's main. But dev's main also holds what every container loads or runs: ORG-AGENTS.md, the git hooks, bin/check.py, and .backlog-version. So one direct push — from a prompt-injected agent, say — could rewrite every agent's instructions and run code in every container. GitHub can only restrict direct pushes by path with push rulesets, which ourPLCC's plan lacks. So the tracker data has to live in a repo of its own that takes direct pushes and holds nothing that runs or instructs, while dev takes changes only through pull requests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A spec in dev-docs/specs/ defines the split: what moves, how backlog/ history moves, how CR references whose relative depth changes are rewritten, and which old links break when the change-requests name stops redirecting to dev
- [ ] #2 ourPLCC/change-requests holds backlog/ with its history and no hooks, scripts, or agent instructions
- [ ] #3 dev no longer holds backlog/, and bin/check.py and dev's CI check change-requests
- [ ] #4 Rulesets: dev's main requires a pull request and blocks force-push and deletion; change-requests' main blocks force-push and deletion; all tags are blocked in both
- [ ] #5 change-requests' README says it holds work we committed to, while GitHub Issues hold conversations
- [ ] #6 The tracker stays usable from every repo's container throughout the transition, before and after that repo's devcontainer CR
<!-- AC:END -->
