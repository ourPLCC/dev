---
id: CR-1027
title: Push from the devcontainer through gh and shared volumes
status: To Do
assignee: []
created_date: '2026-10-13 13:54'
updated_date: '2026-10-13 19:24'
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
<!-- SECTION:NOTES:END -->
