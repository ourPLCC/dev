---
id: CR-1027
title: Push from the devcontainer through gh and shared volumes
status: In Progress
assignee:
  - '@stoney'
created_date: '2026-10-13 13:54'
updated_date: '2026-10-26 18:08'
labels: []
dependencies:
  - CR-1021
  - CR-1022
  - CR-1023
  - CR-1024
  - CR-1025
  - CR-1026
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Nobody can push from inside plcc-ng's devcontainer, so every push happens on the host, and agents can't push a branch or open a PR. The devcontainer's initializeCommand also runs POSIX shell on the host and bind-mounts a host folder, which rules out Windows hosts and Codespaces. As the first repo to adopt the shared setup, plcc-ng also settles the spec's open checks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The devcontainer applies the spec's 'How the credential reaches the container': the gh feature, gh as the only github.com credential helper, no askpass fallback, no SSH agent, remoteUser vscode with UID 1000
- [ ] #2 The devcontainer applies the spec's 'Where the shared clones live': the ourplcc-gh, ourplcc-dev, and ourplcc-change-requests volumes, BACKLOG_CWD, no initializeCommand, and bin/install/shared-clones.bash
- [ ] #3 .claude/settings.json denies the commands the spec lists
- [ ] #4 .gitattributes starts with * text=auto eol=lf
- [ ] #5 CONTRIBUTING.md describes the volumes in place of the ../dev clone and drops the ../change-requests rename paragraph
- [ ] #6 The spec's Verification checklist passes on a Linux or macOS host, a Windows host, and a new Codespace
- [ ] #7 The spec's open checks are settled, and the spec is updated where a result contradicts it
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
From CR-1021's final review: bin/install/shared-clones.bash must take the shared lock as flock -o -w 120 /workspaces/dev <command>, never by opening a descriptor in its own shell, or a child that outlives it (git maintenance detached by fetch) keeps the lock. dev's bin/push.bash (dev PR #15) shows the pattern. The spec's new open check, that the lock in one container blocks another container on the same volume, is settled here.

2026-10-13: the maintainer narrowed CR-1028-CR-1030's verification to a smoke test; this CR alone runs the full Verification checklist on all three hosts. The permissions spec's Verification section still says each code repo's CR passes the checklist in all three; amend it in the same dev PR as the open-check results (AC 7).

2026-10-26: started on plcc-ng branch cr-1027-push-from-devcontainer; plan in .plans/2026-10-26-cr-1027-push-from-devcontainer.md. Next: Part A Task 1 (bin/install/backlog.bash).

2026-10-26: Part A (Tasks 1-5) done on plcc-ng branch cr-1027-push-from-devcontainer, 6 commits, unpushed; final review clean after one fix; commands tier 332/332, units and docs green. Deferred minors from the review: clone killed mid-checkout passes as complete; CONTRIBUTING offline recovery should also say rerun bin/install/backlog.bash; backlog.bash --check can exit non-zero if backlog --version fails; CONTRIBUTING 'token of your own' untrue in a Codespace; install-helpers row should say 'clean checkout of main'; a hanging fetch holds the shared lock until TCP timeout. devcontainer-lock.json lacks the github-cli entry until the first rebuild (Part B1): commit it then. Next: Task 6 (human, on the host): push the branch and open a draft PR.

2026-10-26: Task 6 done: branch pushed, draft PR https://github.com/ourPLCC/plcc-ng/pull/338 (merge only in CR-1022 cutover step 6). Next: Part B (open checks, human) in a separate test container, B1 first; no tracker edits or pushes there.
<!-- SECTION:NOTES:END -->
