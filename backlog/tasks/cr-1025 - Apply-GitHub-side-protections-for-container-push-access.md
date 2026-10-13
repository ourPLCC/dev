---
id: CR-1025
title: Apply GitHub-side protections for container push access
status: To Do
assignee: []
created_date: '2026-10-13 13:54'
updated_date: '2026-10-13 19:35'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: course-materials-ng
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers in ourPLCC are getting push access through a fine-grained token scoped to every ourPLCC repo, this one included, so GitHub must stop direct pushes to main, gh-pages, and tags. course-materials-ng's deploy.yml and release.yml push gh-pages with GITHUB_TOKEN. A gh-pages ruleset would block them unless they push as a release App, which the ruleset can name as its only bypass.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rulesets: main requires a pull request and blocks force-push and deletion; gh-pages and all tags block every push; the release App is the only bypass actor
- [ ] #2 deploy.yml and release.yml push gh-pages with a release App's token in a release environment limited to main
- [ ] #3 A deploy run after the change publishes the dev docs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-13: the ourPLCC Release Bot App's installation now covers this repo (installation: plcc-ng, plcc-ng-devcontainer, languages-ng, course-materials-ng). Its private key for this repo must go only into a release environment, never repository secrets: any of the App's keys mints tokens for every repo in the installation.
<!-- SECTION:NOTES:END -->
