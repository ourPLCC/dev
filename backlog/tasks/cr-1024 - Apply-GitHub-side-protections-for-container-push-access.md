---
id: CR-1024
title: Apply GitHub-side protections for container push access
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-13 13:53'
updated_date: '2026-10-13 19:58'
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
- [x] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block every push; the release App is the only bypass actor
- [x] #2 release.yaml creates tags and releases with a release App's token in a release environment limited to main
- [x] #3 test-languages.yaml declares an explicit, minimal permissions block, like every other workflow
- [ ] #4 A release run after the change creates its tag and GitHub Release
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-13: the ourPLCC Release Bot App's installation now covers this repo (installation: plcc-ng, plcc-ng-devcontainer, languages-ng, course-materials-ng). Its private key for this repo must go only into a release environment, never repository secrets: any of the App's keys mints tokens for every repo in the installation.

AC 2 and 3 evidence (2026-10-13): PR #22 (merge 41497ba). release.yaml runs in the release environment (limited to main; RELEASE_APP_ID and RELEASE_APP_PRIVATE_KEY as environment secrets, no repository secrets), mints the release App's token, checks out with persist-credentials: false, and gives semantic-release the App token; its permissions drop to contents: read. test-languages.yaml declares contents: read. Post-merge Release run 38457923209 minted the token in the release environment and succeeded (chore commit, no release). Remaining: rulesets (AC 1); the next real release (AC 4).

AC 1 evidence (2026-10-13, public rules API): ruleset 20773088 'default branch' on main applies deletion, non_fast_forward, pull_request (0 approvals), and the Test Languages status check; ruleset 25024737 'tags' (all tags) applies creation, update, deletion, non_fast_forward. Both active; the ourPLCC Release Bot is the only bypass actor (set in the UI). Only AC 4 remains: the next real release, which also proves the App's tag bypass.
<!-- SECTION:NOTES:END -->
