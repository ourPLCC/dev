---
id: CR-804
title: '.gitignore doesn''t exclude the plcc-ng/ build directory'
status: Done
assignee: []
created_date: '2026-07-21'
labels: []
dependencies: []
type: chore
project: plcc-ng-demo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every plcc-ng CLI invocation (`plcc-scan`, `plcc-parse`, `plcc-rep`, ...)
creates a `plcc-ng/` build directory (containing `.spec`, `.spec-hash`,
`spec.json`) in the current working directory. This repo's `.gitignore`
only excludes `__pycache__/`, `*.pyc`, and `.DS_Store` — it doesn't exclude
`plcc-ng/`.

Working through the three activities as a student/instructor would (running
`plcc-scan`/`plcc-parse`/`plcc-rep` from `01-lexical/`, `02-syntactic/`,
`03-semantic/`, and `03-semantic/solution/`) leaves four untracked
`plcc-ng/` directories showing up in `git status`, e.g.:

```
?? 01-lexical/plcc-ng/
?? 02-syntactic/plcc-ng/
?? 03-semantic/plcc-ng/
?? 03-semantic/solution/plcc-ng/
```

This is pure generated build output (a spec hash + compiled JSON), not
anything a student would want to commit or even look at, but nothing tells
git to ignore it — so every student following the README ends up with a
dirty working tree and has to figure out on their own whether `plcc-ng/` is
safe to ignore/delete.

### Steps to Reproduce

1. `cd 01-lexical && plcc-scan -s activity/spec.plcc < activity/testprog.txt`
2. `git status` from repo root
3. Observe `01-lexical/plcc-ng/` listed as untracked

### Notes

- Target: this repo's `.gitignore` — add a `plcc-ng/` (or `**/plcc-ng/`)
  entry.
- Possibly also worth raising upstream in `ourPLCC/plcc-ng`: consider
  whether the default build-dir name is distinctive enough to recommend a
  single documented `.gitignore` line in the tool's own quickstart/docs, so
  every course repo built on plcc-ng doesn't have to rediscover this.

Migrated from plcc-ng-demo #004.
<!-- SECTION:DESCRIPTION:END -->
