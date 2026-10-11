---
id: CR-522
title: 'plcc-rep-parses-each-source-independently'
status: Done
assignee: []
created_date: '2026-08-03'
labels:
  - wontdo
dependencies: []
type: docs
project: plcc-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
plcc-rep parses each SOURCE argument as an independent token stream, so
a program split across two files no longer parses. Old PLCC's `rep`
joined its file arguments into one stream. V6's Prog/p1 (`+(3`) and
Prog/p2 (`,4)`) are a course example that relies on the old behavior.

Not a defect in this repo's src/ — per-source parsing is arguably the
more sensible design — but it is a migration hazard worth documenting
upstream, and it silently changes what a course demonstration does.

### Steps to Reproduce

1. From `src/V6/python/`, with p1 containing `+(3` and p2 containing `,4)`:

   ```
   $ plcc-rep ../Prog/p1 ../Prog/p2
   plcc-parser-table: -:1:3: error: expected 'RPAREN', got end of file
   plcc-parser-table: -:1:1: error: unexpected 'COMMA', no production for 'Program'
   ```

2. Concatenating first works as expected:

   ```
   $ cat ../Prog/p1 ../Prog/p2 | plcc-rep
   7
   ```

### Notes

Found while porting V6. See
[dev-docs/specs/2026-08-03-plcc-ng-v6-design.md](../../../languages-ng/dev-docs/specs/2026-08-03-plcc-ng-v6-design.md).

Per issue-conventions.md, upstream-targeted issues stay in this repo and
are reported upstream manually, with explicit go-ahead.

**Filed upstream 2026-08-11** as `ourPLCC/plcc-ng` issue CR-185
(`dev-docs/issues/185-rep-parses-each-source-independently.md`), typed
`docs`. Upstream's reading: per-source parsing is the design its issue CR-8
settled on and `SourceRunner` applies it to `plcc-scan`, `plcc-parse`, and
`plcc-rep` alike, so the fix there is a migration-guide entry rather than a
behavior change — with the question of whether `plcc-rep` specifically
should join its sources left open on top of that.

**Closed 2026-08-13 with upstream CR-185 still open.** The condition written
above was that this issue stays open until upstream lands *and* V6's
two-file `Prog/p1` + `Prog/p2` example either works or is documented as
needing `cat`. The second half is already satisfied — the entry is in
[course-material-impact.md](../../../languages-ng/dev-docs/course-material-impact.md) under `## V6`,
naming this issue — and the first half is not work in this repository. No
change to `src/` is pending, no workaround is carried, and the one course
example affected reads correctly today with `cat Prog/p1 Prog/p2 |
plcc-rep`, which still yields `7`. What remains is a documentation task in
someone else's tracker, so tracking it as an open issue here overstated
what was outstanding.

Upstream status verified 2026-08-13 against `ourPLCC/plcc-ng` at `48fb1a5`
(v2.0.2): CR-185 is still in `dev-docs/issues/` rather than
`dev-docs/issues/done/`, still listed under Open Issues in that repo's
roadmap, with no branch working it. If upstream later decides `plcc-rep`
*should* join its sources after all, that is a behavior change arriving
through a plcc-ng release, and the V6 entry in the impact log is what needs
revisiting — file a fresh issue then rather than reopening this one.

Migrated from languages-ng #022.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Duplicate of CR-185, filed upstream by hand.
<!-- SECTION:FINAL_SUMMARY:END -->
