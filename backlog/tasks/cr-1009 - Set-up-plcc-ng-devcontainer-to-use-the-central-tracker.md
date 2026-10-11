---
id: CR-1009
title: Set up plcc-ng-devcontainer to use the central tracker
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 12:36'
updated_date: '2026-10-11 19:21'
labels: []
milestone: m-0
dependencies:
  - CR-1013
  - CR-1014
references:
  - ../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md
  - >-
    ../../../plcc-ng-devcontainer/dev-docs/specs/2026-10-11-central-tracker-setup-design.md
type: chore
project: plcc-ng-devcontainer
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
plcc-ng-devcontainer has no legacy issues, but work in it is tracked here, and its contributors and agents cannot reach the tracker from its container. It needs the same setup as the other code repos (design: plcc-ng dev-docs/specs/2026-10-08-199-central-tracker-design.md, "Setup in each code repo").

Carry over from plcc-ng: give the ~/.claude named volume a per-repo name (not plcc-ng-claude), and make any containerEnv GIT_CONFIG_* safe.directory entries name this repo's own path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The devcontainer clones ../dev if missing, mounts it at /workspaces/dev, sets BACKLOG_CWD, installs the backlog version pinned in .backlog-version, adds Claude Code with a plcc-ng-devcontainer-claude volume, and approves AGENTS.md's imports
- [ ] #2 Creating the container fails loudly if git refuses the repo or the tracker (dubious ownership); safe.directory entries name only /workspaces/dev and this repo's own path
- [ ] #3 After a rebuild in local VS Code, backlog task list --project plcc-ng-devcontainer --plain works inside the container and /memory lists the three imported files
- [ ] #4 AGENTS.md imports the org agent rules, the org developer guide, and CONTRIBUTING.md; CONTRIBUTING.md opens with the link to the org developer guide, and the README's Contributing section points to it
- [ ] #5 No document says this repo's own devcontainer works in Codespaces
- [ ] #6 .gitignore ignores .plans/, .claude/settings.json allows backlog, and bash scripts/reuse.sh lint passes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during plan execution (final review, all shared with plcc-ng-demo's setup; triage at close): (1) bin/install/claude-imports.bash leaves ~/.claude.json.XXXXXX behind if ~/.claude.json is malformed - add trap 'rm -f "$tmp"' EXIT in both repos or neither. (2) ${containerWorkspaceFolder} is unquoted in postCreateCommand; a host folder name with a space breaks container creation. (3) Opening a git worktree in the devcontainer may fail at git -C status (host .git path) and clone a second ../dev beside the worktree. (4) Unverified until host rebuild: jq present in base:ubuntu; claude-code feature installs after node.
<!-- SECTION:NOTES:END -->
