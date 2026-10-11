---
id: CR-536
title: 'plcc-rep deadlocks on a partial stdout line'
status: Done
assignee: []
created_date: '2026-08-11'
labels:
  - wontdo
dependencies: []
type: fix
project: plcc-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
### Summary

A semantic action that writes a partial line (no trailing newline) to stdout
deadlocks `plcc-rep` with no diagnostic: the merged partial+result line is
unparseable JSON, destroying the result record before `readline()` blocks
forever. Measured in Python and JavaScript, via stdin and via a SOURCE file:
exit 124, no output, no error.

### Description

A semantic action that writes a partial line (no trailing newline) to
stdout deadlocks `plcc-rep` with no diagnostic.

Mechanism, from reading the installed package's
`plcc/cmd/rep.py::_read_response`: `plcc-rep` runs the generated program
as a subprocess and treats its stdout as a private, line-oriented JSON
channel. A line that fails to parse as JSON is printed verbatim and the
read loop continues. That works for a line ending in a newline — the
result record arrives on the next `readline()` intact. It does not work
for a partial line: the unterminated text merges with the following JSON
result line into one unparseable line, which is printed (destroying the
result record), and `readline()` then blocks forever waiting for a result
that will never come.

Measured in both Python and JavaScript targets, via stdin and via a
SOURCE file: `timeout` reports exit 124, with no stdout and no stderr —
the worst available failure mode, since nothing tells the caller what
happened.

A newline-terminated write survives, but only via the unparseable-line
fallback, which is an accident of the implementation rather than a
supported output channel: it happens to print the raw line before the
real result, faking the interleaving a language's `display` would want.

### Steps to Reproduce

1. A spec whose semantic action for some expression writes a partial
   line, e.g. `sys.stdout.write("7")` with no trailing `\n`.
2. `echo '<partial-write expression>' | timeout 5 plcc-rep`
3. Actual: exit 124, no output. Expected: either the partial write is
   surfaced, or `plcc-rep` reports the malformed channel rather than
   hanging silently.

### Notes

Impact: a student who puts a `print` (or the target-language equivalent)
in a semantic action, without remembering to add a trailing newline, gets
a hang with no message — nothing distinguishes it from an infinite loop
in their own program.

Found while designing OBJ's port
([dev-docs/specs/2026-08-11-plcc-ng-obj-design.md](../../../languages-ng/dev-docs/specs/2026-08-11-plcc-ng-obj-design.md),
"The stdout Protocol Finding"), where OBJ's `display`, `display#`,
`putc`, `puts`, and `newline` are partial-line writers by design — a
trailing newline is what the separate `newline` expression is for. OBJ
works around this by buffering all output into `Program.out` and
returning it as part of `_run()`'s result rather than writing it
directly. That workaround is not this issue's to remove, though — see the
closing note below.

Related: issue CR-537
sketches the missing-record-kind fix that would let a semantic action emit
output through a supported channel instead of raw stdout.

Per issue-conventions.md, upstream-targeted issues stay in this repo and
are reported upstream manually, with explicit go-ahead.

**Filed upstream 2026-08-11** as `ourPLCC/plcc-ng` issue CR-186
(`dev-docs/issues/186-rep-deadlocks-on-partial-stdout-line.md`), typed
`fix`. The mechanism above was re-verified against plcc-ng's current
`src/plcc/cmd/rep.py` rather than the installed CLI, and holds. Upstream
splits the work: `_read_response` must stop treating an unbounded
`readline()` as acceptable regardless, since user code can always write to
stdout directly, while the wider fix is upstream CR-187's output record kind.

**Upstream status, checked 2026-08-13** against `ourPLCC/plcc-ng` at
`48fb1a5` (v2.0.2): CR-186 is still open — in `dev-docs/issues/`, not
`done/` — and no branch is working it. Note that upstream split the report:
CR-186 (the bounded-read fix) does not depend on CR-187 (the record kinds) and
is much the smaller change, so it can land first. If it does, the failure
mode improves from a silent hang to a diagnostic, which is most of the
classroom benefit — but it would **not** let OBJ drop its buffering
workaround. Only CR-187 does that. Treat the two as separate arrivals.

**Closed 2026-08-14 with upstream still open.** This issue was recorded as
staying open while OBJ's `Program.out` buffering lives in `src/`, but that
condition belongs to CR-537,
not here. Removing the buffering needs an output record kind, which is
upstream CR-187; a bounded read fixing *this* defect would turn the deadlock
into a diagnostic and leave OBJ with nowhere to emit output. So nothing in
`src/` waits on this issue.

Upstream's own CR-186 says as much: it describes its narrow fix as making a
partial-line write "produce a message rather than a hang", and attributes
the buffering workaround to CR-187.

The defect is real and is reported upstream — see `upstream:` above. Per
"Upstream defects" in issue-conventions.md, an
upstream defect with no local consequence closes here rather than tracking
someone else's tracker. If a fix arrives and OBJ later wants to emit
output directly, that is CR-537's revert, not a reopening of this issue.

Migrated from languages-ng #036.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Duplicate of CR-186, filed upstream by hand.
<!-- SECTION:FINAL_SUMMARY:END -->
