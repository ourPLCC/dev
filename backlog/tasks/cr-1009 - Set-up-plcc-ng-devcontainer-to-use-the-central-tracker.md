---
id: CR-1009
title: Set up plcc-ng-devcontainer to use the central tracker
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-09 12:36'
updated_date: '2026-10-11 19:42'
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
- [x] #1 The devcontainer clones ../dev if missing, mounts it at /workspaces/dev, sets BACKLOG_CWD, installs the backlog version pinned in .backlog-version, adds Claude Code with a plcc-ng-devcontainer-claude volume, and approves AGENTS.md's imports
- [x] #2 Creating the container fails loudly if git refuses the repo or the tracker (dubious ownership); safe.directory entries name only /workspaces/dev and this repo's own path
- [x] #3 After a rebuild in local VS Code, backlog task list --project plcc-ng-devcontainer --plain works inside the container and /memory lists the three imported files
- [x] #4 AGENTS.md imports the org agent rules, the org developer guide, and CONTRIBUTING.md; CONTRIBUTING.md opens with the link to the org developer guide, and the README's Contributing section points to it
- [x] #5 No document says this repo's own devcontainer works in Codespaces
- [x] #6 .gitignore ignores .plans/, .claude/settings.json allows backlog, and bash scripts/reuse.sh lint passes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered during plan execution (final review, all shared with plcc-ng-demo's setup; triage at close): (1) bin/install/claude-imports.bash leaves ~/.claude.json.XXXXXX behind if ~/.claude.json is malformed - add trap 'rm -f "$tmp"' EXIT in both repos or neither. (2) ${containerWorkspaceFolder} is unquoted in postCreateCommand; a host folder name with a space breaks container creation. (3) Opening a git worktree in the devcontainer may fail at git -C status (host .git path) and clone a second ../dev beside the worktree. (4) Unverified until host rebuild: jq present in base:ubuntu; claude-code feature installs after node.

Triage at close (with the human): notes 1-2 filed as a cross-repo draft for devcontainer hardening; note 3 (git worktrees) dropped, nobody uses worktrees in these devcontainers; note 4 resolved by the host rebuild (container built, so jq is present and the claude-code feature installed).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Set up plcc-ng-devcontainer's own devcontainer for the central tracker (PR #17, merged as c32b82d): it clones and mounts ../dev, sets BACKLOG_CWD and exact safe.directory entries, installs the pinned backlog, adds Claude Code with a plcc-ng-devcontainer-claude volume, and approves AGENTS.md's imports via bin/install/claude-imports.bash. Added AGENTS.md, CONTRIBUTING.md on the org guide (README's Contributing section now points to it), .claude/settings.json, .plans/ in .gitignore, and GFDL licensing for the new docs. The repo's own devcontainer is documented as local VS Code only; client-facing images are unchanged and no release was triggered. Verified by scripted checks on the resolved config, the import-approval script and the docs (links, Codespaces wording, REUSE lint), a fresh whole-branch review, CI on the PR, and a host rebuild where backlog task list worked and /memory listed ORG-AGENTS.md and both CONTRIBUTING.md files. Spec: plcc-ng-devcontainer dev-docs/specs/2026-10-11-central-tracker-setup-design.md.
<!-- SECTION:FINAL_SUMMARY:END -->
