---
id: CR-801
title: 'Migration documentation gaps: plcc-parse and plcc-scan behavior changes'
status: Done
assignee: []
created_date: '2026-07-21'
labels:
  - wontdo
dependencies: []
type: docs
project: plcc-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two tool behavior changes from old PLCC to plcc-ng are not prominently called
out in the migration guide, causing confusion for instructors migrating
workshop materials.

---

### Change 1: `plcc-parse` no longer prints `OK`; no `-t` flag

In old PLCC, `parse` printed `OK` on success and `parse -t` printed a parse
trace. In plcc-ng, `plcc-parse` always prints the parse tree — there is no
`-t` flag and no `OK` output.

The migration guide notes this in a table (`| parse [-t] [-n] [file...] |
plcc-parse [file...] | Always shows parse tree; no -t flag needed |`) but the
change is easy to miss. Instructors expect `-t` and `OK` from muscle memory
and will be confused when neither works.

**Suggested migration doc addition:**

> **Breaking behavior change:** `plcc-parse` always prints the full parse
> tree. There is no `-t` flag for tracing and no `OK` output. The parse tree
> is the output.

---

### Change 2: `plcc-scan` output format changed

In old PLCC, `scan` output was:
```
TOKEN_NAME(lexeme)
```

In plcc-ng, `plcc-scan` output is:
```
source:line:col TOKEN_NAME 'lexeme'
```

Where `source` is the filename (or `-` for stdin), `line` and `col` are
1-indexed positions, and `lexeme` is quoted with single quotes.

Example — old output:
```
INTEGER(3)
ADDOP(+)
```

Example — new output:
```
-:1:1 INTEGER '3'
-:2:1 ADDOP '+'
```

This change is not mentioned in the migration guide at all. Any documentation,
tests, or example output that shows the old `TOKEN(lexeme)` format will be
wrong.

**Suggested migration doc addition:**

> **Breaking output format change:** `plcc-scan` output format has changed
> from `TOKEN_NAME(lexeme)` to `source:line:col TOKEN_NAME 'lexeme'`. Update
> any expected output in documentation, tests, or course materials.

---

### Notes

Both of these changes affected the CCSCNE-2026 workshop materials when
migrating to plcc-ng. Instructors are likely to encounter both when converting
existing course materials.

**Target repo:** `ourPLCC/plcc-ng` (docs) — the migration guide should add a
"Breaking behavior changes" callout section that covers both of these
prominently, rather than burying them in a comparison table or omitting them
entirely.

Migrated from plcc-ng-demo #001.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Duplicate of CR-159, filed upstream by hand.
<!-- SECTION:FINAL_SUMMARY:END -->
