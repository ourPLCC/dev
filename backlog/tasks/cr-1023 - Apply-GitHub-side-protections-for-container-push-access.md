---
id: CR-1023
title: Apply GitHub-side protections for container push access
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-13 13:53'
updated_date: '2026-10-13 18:52'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers are getting push access through a fine-grained token that any agent in the container can use. Merging to main is plcc-ng's release, and today a branch's code can reach the release App's credentials: workflows used to get read/write tokens by default, and the App's secrets are repository secrets any workflow can use. Before any container can push, GitHub must stop pushes to main, gh-pages, and tags, and keep release credentials away from unreviewed code. This CR also carries the org-wide token settings, which belong to no repo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Org settings: fine-grained tokens need an owner's approval and last 90 days at most; classic tokens are blocked
- [x] #2 Rulesets: main requires a pull request and blocks force-push and deletion; gh-pages and all tags block every push; the release App is the only bypass actor
- [x] #3 The release App's secrets live in a release environment limited to main and v* tags; the pypi environment is limited to main and v* tags and requires the maintainer's approval
- [x] #4 docs.yml pushes gh-pages with the release App's token instead of GITHUB_TOKEN
- [x] #5 Every workflow declares an explicit, minimal permissions block
- [ ] #6 A release run after the change publishes to PyPI and deploys docs
- [x] #7 plcc-devcontainer is archived, so the release App key in its secrets can no longer run in a workflow
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
dev's .github/workflows/check.yml has no permissions block (found 2026-10-13 while correcting the permissions spec). Out of scope here: CR-1023 covers plcc-ng only, and no existing CR covers dev's workflows. Triage at close.

Cross-repo gap (found 2026-10-13): the ourPLCC Release Bot App is installed on plcc-ng and plcc-ng-devcontainer, each holding its own private key in repository secrets. Any of the App's keys mints installation tokens for every repo in the installation, so a branch workflow in plcc-ng-devcontainer that can read its repository-level key can get Contents write on plcc-ng and bypass plcc-ng's rulesets (the App is their bypass actor). The spec says plcc-ng-devcontainer uses its own App (APP_ID); that may be this App under another secret name. plcc-devcontainer (retired) was removed from the installation on 2026-10-13, but its key still works for the remaining repos until the repo is archived or its key and secrets are deleted. Container push access (CR-1027 and dependents) should wait until plcc-ng-devcontainer's key sits in a release environment limited to main and v* tags, and plcc-devcontainer's key is unreachable. Triage at close.

AC 4 and 5 evidence: PR #337 (merge b0442e50) adds explicit permissions blocks to ci.yml, docs-tests.yml, docs.yml, and release.yml. Post-merge Docs run 38446530069 pushed gh-pages (da91bfc) with the release App's token from the release environment; Release run 38446530070 ran semantic-release in the release environment, cut no version, and skipped publish and create-release.

AC 2 evidence (2026-10-13, public rules API): ruleset 3590717 'default' on main applies deletion, non_fast_forward, and pull_request (0 approvals); ruleset 25020471 'gh-pages' applies creation, update, deletion, non_fast_forward; ruleset 25020571 'All tags' (tag target) applies creation, update, deletion, non_fast_forward. All active. The ourPLCC Release Bot is the only bypass actor (set in the UI; the bypass list is not public). The next release exercises the bypass on main, tags, and gh-pages (AC 6).

AC 1 evidence (2026-10-13, org settings UI): fine-grained tokens allowed with administrator approval required and a 90-day maximum lifetime; classic tokens restricted.

AC 3 evidence (2026-10-13): plcc-ng's release environment allows main and v* and holds RELEASE_APP_ID and RELEASE_APP_PRIVATE_KEY; the repository-level copies are deleted. The pypi environment allows main and v*.*.* (narrower than the spec's v*, matching all 127 release tags), requires the maintainer's approval, allows self-review, and disallows admin bypass. Release run 38446530070 and Docs run 38446530069 drew the App's secrets from the release environment.

Triage (2026-10-13): the check.yml gap is folded into CR-1022 as a new AC. The plcc-ng-devcontainer half of the cross-repo key gap belongs to CR-1026 (AC #3), noted there; CR-1027 now depends on CR-1026. The plcc-devcontainer half is AC #7 here.

AC 7 evidence: ourPLCC/plcc-devcontainer is archived (public API, 2026-10-13).
<!-- SECTION:NOTES:END -->
