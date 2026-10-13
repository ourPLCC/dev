---
id: CR-1021
title: Design a permissions model for local devcontainers
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-12 18:38'
updated_date: '2026-10-13 13:54'
labels: []
dependencies:
  - CR-1022
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: dev
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Contributors cannot push from inside a local ourPLCC devcontainer, so every push happens on the host. The tracker guide makes "push from the host" the rule, and Backlog.md auto-commits tracker changes inside the container, so every CR edit and every code branch needs a manual host-side step. Agents working in the container can commit but cannot push a branch or open a PR, which stalls the "Branch → PR" step of the workflow.

The container has nothing set up for this: the plcc-ng remote is HTTPS, there is no `gh` CLI, and there is no git credential helper. VS Code does forward an SSH agent, but nothing uses it.

What a container may do, with which credentials, and what an agent in it may do on the human's behalf is one decision that binds every repo's devcontainer. So it needs a design before any repo changes its devcontainer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A spec in dev-docs/specs/ defines which GitHub operations (at least push and opening a PR) a local devcontainer can perform, separately for a human contributor and for an agent working in it
- [ ] #2 The spec says how credentials reach the container without being committed to a repo or baked into an image, and how they survive a container rebuild
- [ ] #3 The tracker guide's "push from the host" rule matches the spec
- [ ] #4 ORG-AGENTS.md's Limits on autonomy forbids agents merging PRs, running gh auth login/refresh/token, and pushing change-requests other than through bin/push.bash
- [ ] #5 dev's CONTRIBUTING.md explains working in a devcontainer: creating and approving the token, gh auth login --with-token, what the container cannot do and where to do it, approving PyPI deployments, the Codespaces grant, and the per-contributor migration
- [ ] #6 dev's bin/push.bash pushes change-requests under flock after fetching, rebasing, and passing bin/check.py --pre-push
- [ ] #7 dev's .gitattributes starts with * text=auto eol=lf
<!-- AC:END -->
