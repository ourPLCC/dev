---
id: DRAFT-3
title: Harden devcontainer setup across code repos
status: Draft
assignee: []
created_date: '2026-10-11 19:42'
labels: []
dependencies: []
project: dev
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found in the final review of the plcc-ng-devcontainer tracker setup. Two edge cases are shared by every code repo whose devcontainer copies the same setup (at least plcc-ng-devcontainer and plcc-ng-demo; probably plcc-ng and languages-ng). Both already fail loudly; neither has been seen in practice.

1. bin/install/claude-imports.bash leaves a ~/.claude.json.XXXXXX temp file behind when ~/.claude.json holds malformed JSON (jq fails, set -e aborts before mv). Possible fix: trap that removes the temp file on exit.
2. postCreateCommand uses ${containerWorkspaceFolder} unquoted, so a host folder name containing a space splits the git -C and script paths and container creation fails.

Fix in every repo or none, so the copies do not drift. Committing to it means one CR per repo.
<!-- SECTION:DESCRIPTION:END -->
