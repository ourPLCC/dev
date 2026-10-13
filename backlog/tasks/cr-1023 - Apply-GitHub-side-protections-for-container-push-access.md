---
id: CR-1023
title: Apply GitHub-side protections for container push access
status: To Do
assignee: []
created_date: '2026-10-13 13:53'
updated_date: '2026-10-13 17:45'
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
- [ ] #1 Org settings: fine-grained tokens need an owner's approval and last 90 days at most; classic tokens are blocked
- [ ] #2 Rulesets: main requires a pull request and blocks force-push and deletion; gh-pages and all tags block every push; the release App is the only bypass actor
- [ ] #3 The release App's secrets live in a release environment limited to main and v* tags; the pypi environment is limited to main and v* tags and requires the maintainer's approval
- [ ] #4 docs.yml pushes gh-pages with the release App's token instead of GITHUB_TOKEN
- [ ] #5 Every workflow declares an explicit, minimal permissions block
- [ ] #6 A release run after the change publishes to PyPI and deploys docs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
dev's .github/workflows/check.yml has no permissions block (found 2026-10-13 while correcting the permissions spec). Out of scope here: CR-1023 covers plcc-ng only, and no existing CR covers dev's workflows. Triage at close.
<!-- SECTION:NOTES:END -->
