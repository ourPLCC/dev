---
id: CR-1024
title: Apply GitHub-side protections for container push access
status: To Do
assignee: []
created_date: '2026-10-13 13:53'
updated_date: '2026-10-13 19:35'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: languages-ng
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers are getting push access through a fine-grained token that any agent in the container can use, so GitHub must stop direct pushes to main and to tags. languages-ng's semantic-release creates tags and releases with GITHUB_TOKEN. A tag ruleset would block it unless it pushes as a release App, which the ruleset can name as its only bypass.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block every push; the release App is the only bypass actor
- [ ] #2 release.yaml creates tags and releases with a release App's token in a release environment limited to main
- [ ] #3 test-languages.yaml declares an explicit, minimal permissions block, like every other workflow
- [ ] #4 A release run after the change creates its tag and GitHub Release
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-13: the ourPLCC Release Bot App's installation now covers this repo (installation: plcc-ng, plcc-ng-devcontainer, languages-ng, course-materials-ng). Its private key for this repo must go only into a release environment, never repository secrets: any of the App's keys mints tokens for every repo in the installation.
<!-- SECTION:NOTES:END -->
