---
id: CR-527
title: 'use `plcc-rep -s` instead of copying `src/` into each test tmpdir'
status: To Do
assignee: []
created_date: '2026-08-05'
labels: []
dependencies: []
type: test
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
### Summary

`plcc-rep -s <abs spec path>` resolves `%include` from the spec's real
location while writing build output to the current directory, so the 39
migrated test files need no copied tree at all — isolation becomes
structural rather than a filtered copy. The 3 legacy `plccmk` languages
still need `relocate`, so both mechanisms coexist until they migrate.

### Description

`plcc-rep -s <absolute path to spec>` resolves `%include` relative to the
spec's real location while still writing build output to the **current
directory**. So a test needs no copied tree at all:

    cd "$BATS_TEST_TMPDIR"
    plcc-rep -s "$REPO/src/REF/java/spec.plcc" < input

This gets isolation structurally rather than by filtering a copy: nothing
is copied, so nothing stale can be copied. It supersedes the
`git ls-files`-driven copy added for issue CR-525 — for migrated languages.

**Verified** during the issue CR-525 design across all three Env flavors and
all three targets: V1/envRN, V6/envVal, REF/envRef in python, java, and
javascript. 6 of 6 produced their expected output with nothing copied, and
`git status --ignored` confirmed `src/` was left clean afterwards.

### Scope

39 test files / 117 tests use plcc-ng and can convert. Each becomes roughly:

    @test "SET counter (java)" {
      cd "$BATS_TEST_TMPDIR"
      RESULT="$(plcc-rep -s "$BATS_TEST_DIRNAME/../../java/spec.plcc" \
                  < "$BATS_TEST_DIRNAME/SET.input")"
      expected_output=$(< "$BATS_TEST_DIRNAME/SET.expected")
      [[ "$RESULT" == "$expected_output" ]]
    }

3 test files / 3 tests (OBJ, TYPE0, TYPE1) **cannot**: they run
`plccmk -c grammar` / `rep -n`, which build in place with no `-s`
equivalent. `relocate` and `relocate_copy_tree` must stay until those three
migrate, at which point both can be deleted outright.

NAME and NEED were in that cannot-convert list when this issue was filed.
Both have since migrated to plcc-ng and are now convertible; the counts
above reflect that.

Best sequenced with the remaining migration work, which is actively
editing these same test files.

### Notes

Any ideas, hunches, or related context.

**`-s` shrinks the footprint; it does not bound it.** Measured while
designing issue CR-531:
`-s` removes the 1.5 MB tree copy, but each test's build output still lands
in `BATS_TEST_TMPDIR` and still accumulates across the run (V4 seq: python
488K, java 588K, javascript 372K). For the suite as it stands that is a drop
from roughly 312 MB peak to roughly 65 MB — about 5x, and still growing with
every language added.

The bound comes from `bin/bats-tmpdir.bash` (issue CR-531), which empties each
passing test's tmpdir and holds peak at the cost of a single test regardless
of suite size. That also covers OBJ, TYPE0 and TYPE1, which can never
convert. So this issue is a speed and cleanliness win, not the disk fix it
was once thought to be.

**The "3 test files / 3 tests (OBJ, TYPE0, TYPE1) cannot [convert]" count
above is now zero** — OBJ migrated to plcc-ng in issue CR-535, following
TYPE0 and TYPE1. `relocate` need not coexist with `plcc-rep -s` any
longer: `relocate` and `relocate_copy_tree` are deletable outright rather
than convertible, since nothing left needs them. `plccmk` still appears
in `bin/relocate.bash` and `bin/clean.bash`, which is the remaining
surface.

Also stale as of issue CR-535: `bin/relocate.bash:41`'s comment — "the
not-yet-migrated languages (OBJ, TYPE1) run plccmk, which builds in place
and has no way to be pointed at a spec elsewhere" — is now factually
false, since both have migrated. Issue CR-535's completion note cites this
same file as "the remaining surface" without flagging that the comment
itself is stale; worth fixing both together when this issue is picked
up.

Migrated from languages-ng #027.
<!-- SECTION:DESCRIPTION:END -->
