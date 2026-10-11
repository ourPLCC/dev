---
id: CR-803
title: 'Activity 3 doesn''t specify integer (floor) division semantics for Div'
status: Done
assignee: []
created_date: '2026-07-21'
labels: []
dependencies: []
type: docs
project: plcc-ng-demo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`03-semantic/README.md` asks students to implement `Sub`, `Mul`, and `Div`
"following the `Add` pattern," e.g.:

```python
Add
%%%
def evaluate(self):
    return self.opnd1.evaluate() + self.opnd2.evaluate()
%%%
```

For `Div`, the naive/literal reading of "follow the pattern" is:

```python
def evaluate(self):
    return self.opnd1.evaluate() / self.opnd2.evaluate()
```

This is what I wrote first, and it "works" — `plcc-rep` runs, produces
plausible-looking numbers, and doesn't error. But Python's `/` is true
division, so results like `* / 45 5 - 3 10` come out as `-63.0` instead of
`-63`. The solution (`03-semantic/solution/python/spec.plcc`) uses `//`
(floor division), and the solution README explicitly states "All three
[Python, Java, JavaScript] should produce the same output," listing integer
results (`6`, `90`, `-63`, `63`, no decimals).

Since the activity's own dummy `evaluate()` returns `999` (an int) and the
`Const.evaluate()` uses `int(...)`, the whole interpreter is implicitly
integer-typed — but nothing in the activity instructions says division
should truncate/floor rather than produce a float. A student comparing
their own output informally (without diffing against
`solution/python/spec.plcc`) could easily miss this, since the output looks
correct at a glance (`6.0` reads as "basically 6").

### Steps to Reproduce

1. `cd 03-semantic`
2. Implement `Div.evaluate` as
   `return self.opnd1.evaluate() / self.opnd2.evaluate()` (the literal
   "follow the Add pattern" translation).
3. `plcc-rep -s activity/spec.plcc < activity/testprog2.txt`
4. Observe outputs like `6.0`, `-63.0`, `63.0` instead of the solution's
   `6`, `-63`, `63`.

### Notes

- Target: `03-semantic/README.md` (this demo repo) — add a line noting that
  arithmetic is integer-only, so `Div` should use floor/integer division
  (`//` in Python) to match the Java/JavaScript backends' integer semantics
  and the solution's expected output.
- Not a plcc-ng tool bug — it's an activity-instructions gap. Cross-language
  parity (Python/Java/JS all producing `6` not `6.0`) is a design goal of
  this specific demo, so the instructions should say so rather than leaving
  division semantics to be inferred.

Migrated from plcc-ng-demo #003.
<!-- SECTION:DESCRIPTION:END -->
