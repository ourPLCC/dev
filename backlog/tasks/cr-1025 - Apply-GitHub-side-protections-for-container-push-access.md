---
id: CR-1025
title: Apply GitHub-side protections for container push access
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-13 13:54'
updated_date: '2026-10-13 20:26'
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
- [x] #2 deploy.yml and release.yml push gh-pages with a release App's token in a release environment limited to main
- [x] #3 A deploy run after the change publishes the dev docs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-13: the ourPLCC Release Bot App's installation now covers this repo (installation: plcc-ng, plcc-ng-devcontainer, languages-ng, course-materials-ng). Its private key for this repo must go only into a release environment, never repository secrets: any of the App's keys mints tokens for every repo in the installation.

AC 2 and 3 evidence (2026-10-13): PR #68 (merge d56ab3d) runs deploy.yml and release.yml in the release environment (limited to main; RELEASE_APP_ID and RELEASE_APP_PRIVATE_KEY as environment secrets), mints the release App's token, and checks out with it, so mike's --push goes out as the App; permissions drop to contents: read. Deploy run 38461443178 failed on attempt 1 because the ID secret was saved as APP_ID; after it was re-added as RELEASE_APP_ID, attempt 2 succeeded and pushed gh-pages ('Deployed d56ab3d to dev'). release.yml's edition path is not exercised until the next edition is cut. Remaining: rulesets (AC 1).

Found while here: checks.yml's External links job (lychee) fails on PR #68 because some linked sites block bots. Unrelated to this CR. Triage at close.

Deviation (2026-10-13, maintainer's decision): Alain (alainkaegi) pushes to main directly, and that workflow stays. So ruleset 17903860 'default branch', now active on main (deletion, non_fast_forward, pull_request with 0 approvals, Strict build status check), has two bypass actors: the ourPLCC Release Bot and alainkaegi, both Always allow. Everyone else, including agents holding other contributors' tokens, must use a PR. Why main still needs protecting here: deploy.yml runs on push to main in the release environment and mints the release App's token, which reaches every repo in the App's installation; an open main would let any token holder run code with it. Residual risk: Alain's own token. The permissions spec says the release Apps are the only bypass actors; it needs a sentence recording this exception. Remaining for AC 1: the gh-pages and tag rulesets.
<!-- SECTION:NOTES:END -->
