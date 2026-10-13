---
id: CR-1026
title: Apply GitHub-side protections for container push access
status: To Do
assignee: []
created_date: '2026-10-13 13:54'
updated_date: '2026-10-13 19:10'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng-devcontainer
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers are getting push access through a fine-grained token that any agent in the container can use, so GitHub must stop direct pushes to main and to tags. plcc-ng-devcontainer releases with its own App (APP_ID), not the release App the other repos use, so the rulesets must either name that App as a bypass actor or the repo must switch to the shared one.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block every push; the repo's release App is the only bypass actor
- [x] #2 The CR records whether the repo keeps its own App or adopts the shared release App, and why
- [ ] #3 The App's secrets live in a release environment limited to main and release tags
- [ ] #4 A release run after the change publishes its images and feature
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
From CR-1023's triage (2026-10-13): the shared ourPLCC Release Bot App is installed on plcc-ng and plcc-ng-devcontainer, so the spec's 'own App (APP_ID)' may be this App under another secret name; AC #2 settles which. If it is the shared App, any of its private keys this repo holds in repository secrets mints installation tokens for plcc-ng too, and so bypasses plcc-ng's rulesets (the App is their bypass actor). AC #3 closes that, which is why CR-1027 depends on this CR.

AC 2 (2026-10-13): plcc-ng-devcontainer adopts the shared ourPLCC Release Bot. It already uses it: the Release Bot is the only GitHub App installed on the repo, so its APP_ID and APP_PRIVATE_KEY secrets are the Release Bot's. Keeping one App means one bypass actor for every repo's rulesets. The secret names stay APP_ID and APP_PRIVATE_KEY, to keep the workflow change to adding environment: release.
<!-- SECTION:NOTES:END -->
