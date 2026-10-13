---
id: CR-1029
title: Push from the devcontainer through gh and shared volumes
status: To Do
assignee: []
created_date: '2026-10-13 13:54'
updated_date: '2026-10-13 20:38'
labels: []
dependencies:
  - CR-1027
  - CR-1031
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng-demo
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Nobody can push from inside plcc-ng-demo's devcontainer, so every push happens on the host, and agents can't push a branch or open a PR. The devcontainer's initializeCommand also runs POSIX shell on the host and bind-mounts a host folder, which rules out Windows hosts and Codespaces. plcc-ng-demo does not release, so its rulesets come with this CR instead of a separate protections CR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block every push
- [ ] #2 The devcontainer applies the spec's 'How the credential reaches the container' and 'Where the shared clones live', as plcc-ng's does
- [ ] #3 bin/install/shared-clones.bash clones dev and change-requests idempotently under flock
- [ ] #4 .claude/settings.json denies the commands the spec lists
- [ ] #5 .gitattributes starts with * text=auto eol=lf
- [ ] #6 CONTRIBUTING.md describes the volumes in place of the ../dev clone
- [ ] #7 In a rebuilt local container, a smoke test passes: push a branch and open a PR with gh, list CRs with backlog task list, push a tracker change with bin/push.bash, and see a direct push to main rejected. The full Verification checklist runs only for plcc-ng, in CR-1027, since this repo's devcontainer changes copy plcc-ng's.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-13: AC 7 narrowed from the full Verification checklist on three hosts to a smoke test, by the maintainer's decision; CR-1027 runs the full checklist.

AC 1 met by CR-1031's work (2026-10-13): plcc-ng-demo's main ruleset requires a PR and blocks force-push and deletion, and its tags ruleset blocks creation, update, and deletion; an org owner's direct push to main and tag push were both rejected.
<!-- SECTION:NOTES:END -->
