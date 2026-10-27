---
id: CR-1022
title: Split tracker data into ourPLCC/change-requests
status: In Progress
assignee:
  - '@stoney'
created_date: '2026-10-13 13:53'
updated_date: '2026-10-27 17:43'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
  - ../../dev-docs/specs/2026-10-13-change-requests-split-design.md
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
- [x] #1 A spec in dev-docs/specs/ defines the split: what moves, how backlog/ history moves, how CR references whose relative depth changes are rewritten, and which old links break when the change-requests name stops redirecting to dev
- [ ] #2 ourPLCC/change-requests holds backlog/ with its history, a README, and a .gitattributes, and no hooks, scripts, workflows, or agent instructions; every relative reference that pointed into dev resolves
- [ ] #3 dev no longer holds backlog/; bin/check.py requires --root, the hooks check the repo that runs them, and dev's CI checks change-requests on every push and pull request
- [ ] #4 Rulesets: dev's main requires a pull request and blocks force-push and deletion; change-requests' main blocks force-push and deletion; all tags are blocked in both
- [ ] #5 change-requests' README says it holds work we committed to, while GitHub Issues hold conversations
- [ ] #6 The cutover follows the spec's sequence, and the tracker is unavailable only between the freeze and the first rebuilt devcontainer listing CRs from change-requests
- [ ] #7 Every workflow in dev declares an explicit, minimal permissions block
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during implementation (final review): (1) migrate/verify.py:65 runs tracker_root/bin/check.py, which change-requests lacks; a future migration needs it to call dev's check.py with --root. (2) PR 2's CI can pass before ourPLCC/change-requests exists, because the name still redirects to dev; a green run before cutover step 2 proves nothing about the real data. (3) Cutover step 3 must run split_links with --dev pointing at a dev main that has pulled PR 1, or CR-1022's own spec reference is skipped; expect 24 changed, 2 skipped, 4 unmatched (prose in code spans) plus any CRs filed since 2026-10-13.

Cutover step 6 merges dev PR #15 (CR-1021: bin/push.bash and the docs). It is based on cr-1022-check-change-requests, so once the split's PR merges, its diff against main shrinks to CR-1021's own commits; merge it only after that.

Folded in from CR-1023's triage (2026-10-13): dev's .github/workflows/check.yml has no permissions block, though the devcontainer permissions spec requires one in every ourPLCC workflow. This CR already reworks dev's CI.

2026-10-27: cutover prerequisite 3 (link search) run. GitHub search of the org (code, issues, PRs) and a local search of dev and plcc-ng found no URL under the old name into dev's own content. Gap in the split spec's 'Old links': it covers URLs, not short references like ourPLCC/change-requests#N, which after the split point at change-requests' issue or PR N instead of dev's. One found and fixed: CR-1007's final summary now says ourPLCC/dev#1. Before the freeze, rerun the search including short references (grep -rn 'change-requests#' backlog/ in dev, and GitHub search), and consider amending the spec's 'Old links' to name them.

Correction: CR-1007 is not fixed yet. It is in backlog/completed/, and the backlog CLI cannot edit completed CRs (task edit says 'Task not found'). Options: the maintainer edits that one line by hand, or split_links rewrites ourPLCC/change-requests#N to ourPLCC/dev#N during cutover step 3.

CR-1007 fixed by the maintainer by hand (dev commit e4084d4); its final summary now references ourPLCC/dev#1. No other short reference to the old name remains in backlog/.
<!-- SECTION:NOTES:END -->
