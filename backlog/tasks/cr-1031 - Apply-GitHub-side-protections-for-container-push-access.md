---
id: CR-1031
title: Apply GitHub-side protections for container push access
status: Done
assignee: []
created_date: '2026-10-13 17:35'
updated_date: '2026-10-13 19:10'
labels: []
dependencies: []
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng-demo
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Devcontainers are getting push access through a fine-grained token that any agent in the container can use, so GitHub must stop direct pushes to main and to tags in every ourPLCC repo except dev and change-requests. plcc-ng-demo has no workflows, no gh-pages, and no tags today, so it needs only the rulesets; with no release App, nobody bypasses them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rulesets: main requires a pull request and blocks force-push and deletion; all tags block creation, update, and deletion; no bypass actors
- [x] #2 A direct push to main and a tag push are both rejected
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evidence (2026-10-13): ruleset 19468874 'default branch' on main applies deletion, non_fast_forward, and pull_request (0 approvals); ruleset 25021808 'tags' (all tags) applies creation, update, deletion, non_fast_forward. Both active, no bypass actors. From the host, as an org owner: a direct push to main was rejected (GH013, 'Changes must be made through a pull request') and pushing tag ruleset-check was rejected (GH013, 'creations being restricted').
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
plcc-ng-demo has no workflows and no release App, so its protections are settings only. The existing main ruleset already required a pull request and blocked force-push and deletion; a new tag ruleset blocks creating, updating, and deleting every tag. Neither has bypass actors. An org owner's direct push to main and tag push were both rejected.
<!-- SECTION:FINAL_SUMMARY:END -->
