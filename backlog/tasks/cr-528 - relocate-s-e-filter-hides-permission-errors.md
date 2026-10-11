---
id: CR-528
title: 'relocate''s `[[ -e ]]` filter hides permission errors'
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

`relocate_copy_tree`'s existence filter can't tell "deleted with `rm`" from
"exists but unreadable" (`chmod 000` on a tracked file's parent directory
reproduces it), so an `EACCES` path is silently dropped from the copy
instead of failing loudly — the same silent-corruption class as issue CR-525,
reintroduced one layer down. Dormant: nothing in this repo `chmod`s a spec
directory today.

### Description

`relocate_copy_tree` in [bin/relocate.bash](../../../languages-ng/bin/relocate.bash)
filters the path list from `git ls-files` with a plain existence check:

```bash
if [[ -e "${f}" ]]; then printf '%s\0' "${f}"; fi
```

`[[ -e ]]` cannot distinguish "path was deleted with `rm`" (the case it
was added for — see issue CR-525)
from "path exists but is unreadable" (`EACCES`). Both read as "does not
exist" to `[[ -e ]]`, so both are silently dropped from the list handed
to `tar`.

This matters for the same reason issue CR-525 mattered: a test can run
against an incomplete tree while every layer reports success. Here the
mechanism is different — a permission error masquerading as a deletion —
but the shape of the failure is identical.

### Steps to Reproduce

Reproduced by the final reviewer of the issue CR-525 branch:

1. `chmod 000` the **parent directory** of a tracked file (not the file
   itself).
2. Run `relocate_copy_tree` against that tree. `git ls-files --others`
   warns on stderr (`could not open directory '...': Permission denied`)
   but still emits the file's path, since that comes from the index
   (`--cached`), not from walking the directory.
3. `[[ -e "${f}" ]]` evaluates that path and fails — not because the file
   is gone, but because `stat` on it returns `EACCES` through the
   unreadable parent directory.
4. The entry is filtered out exactly as if it had been `rm`-ed.
   `relocate_copy_tree` returns 0, and the destination never receives
   that path at all — no error, no warning, nothing in the copied tree.

A `chmod 000` on a tracked *file* (as opposed to its parent directory) is
already handled correctly today: `tar` itself fails to read the file, the
`pipefail` subshell (added for issue CR-525) propagates that failure, and
`relocate_copy_tree` returns non-zero. There is an existing regression
test for that case in `bin/tests/relocate.bats`
("`relocate_copy_tree` fails when a listed file cannot be read"). This
issue is specifically about the parent-directory variant, which the
`[[ -e ]]` filter intercepts before tar ever gets a chance to fail loudly.

### Notes

**A second condition the same filter swallows: dangling symlinks.**
`[[ -e ]]` follows a symlink to its target, so a link whose target is
missing reads as "does not exist" and is dropped. The previous `cp -R`
preserved such a link as a link, regardless of whether its target
resolved. This is a genuine behavior change introduced by the issue CR-525
fix, and it is inert today only because the repository contains no tracked
symlinks at all (`git ls-files -s | awk '$1 == "120000"'` is empty). It is
recorded here rather than as its own issue because it shares both the root
cause and the single line of code with the permission case above — the
proposed fix below resolves both, since `git ls-files --deleted` reports a
dangling symlink as present (the link itself exists) rather than deleted.

**Why this is not urgent.** Nothing in this repository `chmod`s a spec
directory during normal use, so the defect is dormant. It was triaged
during the issue CR-525 review as confirmed but non-blocking for that
branch — worth recording precisely so it isn't rediscovered from
scratch, not worth holding up a ready-to-merge fix.

**Proposed fix.** Replace the blanket `[[ -e ]]` filter with a set
subtraction: compute the list from `git ls-files -z --cached --others
--exclude-standard` and remove exactly the paths `git ls-files -z
--deleted` reports as gone from the working tree. That distinguishes
"legitimately gone from git's perspective" (the `rm`-deleted case this
filter exists for) from "exists but unreadable," and stops swallowing the
latter. With no filter standing in front of it, tar's own read failure
surfaces the permission problem loudly — the same propagation path the
issue CR-525 fix already built via `set -o pipefail`.

Related: issue CR-525, whose
fix added both the `[[ -e ]]` filter (for the legitimate `rm`-deleted
case) and the `pipefail` propagation that makes tar's own read failures
visible — this issue is about the filter hiding a different failure mode
from that same propagation.

Migrated from languages-ng #028.
<!-- SECTION:DESCRIPTION:END -->
