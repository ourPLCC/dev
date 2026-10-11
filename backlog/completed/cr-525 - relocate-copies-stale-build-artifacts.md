---
id: CR-525
title: 'relocate-copies-stale-build-artifacts'
status: Done
assignee: []
created_date: '2026-08-05'
labels: []
dependencies: []
type: test
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
[bin/relocate.bash](../../../languages-ng/bin/relocate.bash) copies the **whole `src/`
tree** into each bats test's isolated tmpdir:

```bash
cp -R "${src_dir}/"* .
```

The wide copy is deliberate and load-bearing — every migrated language
`%include`s a sibling top-level directory (`../../Env/envRef/<target>/env.plcc`),
so a narrower copy would leave those includes unresolvable. But the glob
also sweeps up the gitignored build directories `plcc-rep` leaves behind:
`plcc-ng/`, `__pycache__/`, and `*.class`.

So **running `plcc-rep` by hand inside any `src/<lang>/<target>/`
directory silently corrupts the next `bin/test.bash` run**, and
`git status` stays clean throughout because every one of those artifacts
is ignored.

Three properties make this worse than an ordinary flake:

- **It accuses the wrong language.** The failure surfaces in whichever
  language holds the stale artifacts, which is typically *not* the one
  being worked on. During the REF migration it presented as
  `SET formal-is-a-copy (java)` failing — SET having been finished and
  untouched for a day.
- **It looks like flakiness.** Re-running after the artifacts happen to
  be cleared makes it pass, so the natural conclusion is "flaky test,"
  and the real cause goes unrecorded. This happened twice in one session,
  and was diagnosed as flakiness both times before being run down.
- **It corrupts the baseline, not just a run.** Migration work checks a
  measured before/after test count. A contaminated baseline reads
  77 passing / 7 failing instead of 78 / 6, which makes every downstream
  expectation in a phase plan wrong.

### Steps to Reproduce

1. Start from a clean tree with a green suite (`bin/test.bash` →
   84 tests, 78 passing, 6 failing as of 2026-08-04).
2. Run any spec by hand so it writes build output:
   `cd src/SET/java && plcc-rep < ../tests/let/SET.input`
3. Return to the repo root and run `bin/test.bash` again.
4. `SET formal-is-a-copy (java)` fails, while `git status` reports a
   clean tree.
5. `find src -name plcc-ng -type d -prune -exec rm -rf {} +` and re-run —
   it passes again.

### Notes

Observed during the REF migration (issue
CR-524); the workaround used there was to
clear artifacts immediately before every suite run:

```bash
find src -name plcc-ng -type d -prune -exec rm -rf {} +
find src -name __pycache__ -type d -prune -exec rm -rf {} +
find src -name '*.class' -delete
```

That is a workaround, not a fix — it relies on every contributor
remembering it, and the failure is invisible when they don't.

Possible directions, not yet evaluated against each other:

- Have `relocate` exclude build artifacts while still copying the tree —
  e.g. `rsync -a --exclude=plcc-ng --exclude=__pycache__ --exclude='*.class'`,
  or `git ls-files`-driven copy so only tracked files are relocated. The
  `git`-driven variant has the appealing property that what the tests see
  is exactly what is committed.
- Have `relocate` clear artifacts in the tmpdir copy after copying.
- Teach `bin/test.bash` to refuse to run, or warn loudly, when build
  artifacts exist under `src/`.

Related: issue CR-515
also concerned build output being confused with source, though its cause
(case-insensitive `.gitignore` matching) is unrelated.

Migrated from languages-ng #025.
<!-- SECTION:DESCRIPTION:END -->
