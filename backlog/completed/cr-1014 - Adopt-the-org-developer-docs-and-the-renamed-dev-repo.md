---
id: CR-1014
title: Adopt the org developer docs and the renamed dev repo
status: Done
assignee:
  - '@StoneyJackson'
created_date: '2026-10-10 18:34'
updated_date: '2026-10-10 20:47'
labels: []
milestone: m-0
dependencies:
  - CR-1013
references:
  - ../../dev-docs/specs/2026-10-10-org-developer-docs-design.md
type: chore
project: plcc-ng
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
plcc-ng's CONTRIBUTING.md and CLAUDE.md restate workflow rules that now live in the org developer guide in ourPLCC/dev, and the copies will drift. CLAUDE.md also mixes rules every developer needs with rules only agents need, and loads only for Claude. The devcontainer still clones and mounts the tracker under its old name.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The devcontainer clones ../dev if missing, mounts it at /workspaces/dev, and sets BACKLOG_CWD and safe.directory to match; after a rebuild, backlog commands work
- [x] #2 AGENTS.md replaces CLAUDE.md: it imports ../dev/ORG-AGENTS.md, ../dev/CONTRIBUTING.md, then CONTRIBUTING.md, and holds only agent rules specific to plcc-ng
- [x] #3 In a fresh Claude Code session, the imported files are loaded; any approval prompt for imports outside the repo is described in the setup instructions
- [x] #4 CONTRIBUTING.md opens by pointing to the org developer guide, holds only plcc-ng-specific material, and states each deviation from the org guide with its reason
- [x] #5 The PR template and other docs refer to the tracker as ourPLCC/dev
- [x] #6 The PR description tells maintainers to rename their host ../change-requests folder to ../dev before rebuilding
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Found during implementation: in a worktree under .worktrees/<name>/, AGENTS.md's @../dev/ imports resolve to .worktrees/dev and are skipped. Sessions started in a worktree still get the org files through the main checkout's AGENTS.md (Claude Code also loads parent directories' instruction files), so nothing breaks today, but a session that doesn't load parent directories would miss them. Also: external @imports are skipped silently in claude -p until the project has been approved interactively once.

Triage (with Stoney): both notes dropped. The worktree import gap has no effect today; the claude -p behavior is documented in CONTRIBUTING.md.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced CLAUDE.md with AGENTS.md importing the org guide, rewrote CONTRIBUTING.md to build on it, and moved the devcontainer to ../dev (plcc-ng#333). Fixed the AGENTS.md imports, which never loaded because of trailing commas and a missing approval for outside imports, and made the devcontainer approve them on creation via bin/install/claude-imports.bash (plcc-ng#334). Corrected the org design spec and dev's own AGENTS.md to match (dev#4). Verified by a rebuild: backlog works, /memory lists both org files, and a fresh VS Code session quoted ORG-AGENTS.md without reading it.
<!-- SECTION:FINAL_SUMMARY:END -->
