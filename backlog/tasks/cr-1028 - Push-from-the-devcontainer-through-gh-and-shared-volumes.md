---
id: CR-1028
title: Push from the devcontainer through gh and shared volumes
status: To Do
assignee: []
created_date: '2026-10-13 13:54'
updated_date: '2026-10-13 20:37'
labels: []
dependencies:
  - CR-1024
  - CR-1027
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: languages-ng
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Nobody can push from inside languages-ng's devcontainer, so every push happens on the host, and agents can't push a branch or open a PR. The devcontainer's initializeCommand also runs POSIX shell on the host and bind-mounts a host folder, which rules out Windows hosts and Codespaces.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The devcontainer applies the spec's 'How the credential reaches the container' and 'Where the shared clones live', as plcc-ng's does
- [ ] #2 bin/install/shared-clones.bash clones dev and change-requests idempotently under flock
- [ ] #3 .claude/settings.json denies the commands the spec lists
- [ ] #4 .gitattributes starts with * text=auto eol=lf
- [ ] #5 CONTRIBUTING.md describes the volumes in place of the ../dev clone
- [ ] #6 In a rebuilt local container, a smoke test passes: push a branch and open a PR with gh, list CRs with backlog task list, push a tracker change with bin/push.bash, and see a direct push to main rejected. The full Verification checklist runs only for plcc-ng, in CR-1027, since this repo's devcontainer changes copy plcc-ng's.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-13: AC 6 narrowed from the full Verification checklist on three hosts to a smoke test, by the maintainer's decision; CR-1027 runs the full checklist.
<!-- SECTION:NOTES:END -->
