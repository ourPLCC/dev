# Splitting the tracker data into ourPLCC/change-requests — design

Date: 2026-10-13

## Problem

[2026-10-13-devcontainer-permissions-design.md](2026-10-13-devcontainer-permissions-design.md)
gives containers push access and moves the tracker data out of `dev`, so that
`dev`'s `main` takes changes only through pull requests while the tracker
takes direct pushes. It leaves the mechanics of that split to this spec: what
moves, how `backlog/`'s history moves, how CR references whose relative depth
changes are rewritten, how `dev`'s checks reach the new repo, and which old
links break when the name `ourPLCC/change-requests` stops redirecting to
`dev`.

## Supersedes

- [2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md):
  in "`bin/check.py`", that the hooks run through `core.hooksPath .githooks`
  in the repo that holds `backlog/`, and that CI runs on every push to the
  tracker's `main` (see "Checks").

## Decision summary

- `ourPLCC/change-requests` is a new public repo holding `backlog/`, a
  `README.md`, and a `.gitattributes`, and nothing else.
- `backlog/`'s history moves with `git filter-repo --path backlog/`: commit
  hashes change, authors, dates, and messages do not.
- A tested script in `dev`'s `migrate/` rewrites the relative references that
  pointed into `dev`, by rule.
- `dev` deletes `backlog/` in an ordinary pull request; its history is not
  rewritten.
- `bin/check.py` requires `--root`; the hooks check whichever repo runs them;
  `dev`'s CI checks out `change-requests` and checks it.
- The split is a **coordinated cutover** in one sitting. The tracker is
  unavailable from the freeze until the first rebuilt devcontainer lists CRs
  from `change-requests`.

## What moves

| Path | Goes to |
| --- | --- |
| `backlog/` (config, `tasks/`, `completed/`, `drafts/`, `docs/`, `decisions/`, `milestones/`, `archive/`) | `change-requests` |
| `README.md` | stays in `dev`, rewritten; `change-requests` gets its own |
| `.githooks/`, `bin/`, `tests/`, `migrate/`, `upstream/`, `.backlog-version`, `.github/`, `.claude/` | stay in `dev` |
| `AGENTS.md`, `ORG-AGENTS.md`, `CONTRIBUTING.md`, `dev-docs/` | stay in `dev` |

`change-requests` holds no hooks, scripts, workflows, version pins, or agent
instructions: everything in it is data an agent reads, with no more authority
than an issue. Its `.gitattributes` is the permissions spec's:

```gitattributes
* text=auto eol=lf
```

### Its README

A few lines, for visitors who arrive from a CR link:

- This repo holds ourPLCC's change requests: work we have committed to.
- To report a problem or suggest an idea, open a GitHub issue on the relevant
  code repo; GitHub Issues hold conversations with people.
- How to use the tracker: `dev`'s
  [dev-docs/tracker.md](https://github.com/ourPLCC/dev/blob/main/dev-docs/tracker.md).
- No code lives here; the tracker's tooling and checks are in `ourPLCC/dev`.

## How the history moves

On a fresh clone of `dev`, never on a working clone:

```bash
git clone https://github.com/ourPLCC/dev split
git -C split filter-repo --path backlog/
```

The result's history holds only the commits that touched `backlog/`, each with
its original author, date, and message. Commit hashes change. Nothing cites a
tracker commit by hash; the hashes CRs cite (for example "merged as
c32b82d") are code-repo commits and are unaffected.

`dev`'s own history keeps every `backlog/` commit; only its tree loses the
folder.

Rejected:

| Alternative | Why not |
| --- | --- |
| Push `dev`'s full history, then delete everything but `backlog/` | Keeps hashes, but every clone carries the old hooks, scripts, and agent rules in its history |
| Fresh import without history | Loses the record of who changed what, and when |

## Rewriting references

CRs link to files with relative paths written as if the CR is in
`backlog/tasks/` (see `dev-docs/tracker.md`, "References and links").
`../../../<repo>/…` still resolves after the split, because `change-requests`
is a sibling of the code repos, as `dev` is. `../../X` pointed into `dev` and
now points into `change-requests`.

`migrate/split_links.py`, with tests in `migrate/tests/`, standard library
only, run against the filtered clone with `dev`'s working tree as reference:

- It scans every `*.md` under `backlog/`: Markdown link targets
  (`](…)`) and `references:` entries in frontmatter.
- For each relative target, it resolves it as if the file is in
  `backlog/tasks/`. If the result lies inside `dev` but outside `backlog/`, and
  the target exists in `dev`, `../../X` becomes `../../../dev/X`.
- It leaves every other target alone: ones in sibling repos, ones inside
  `backlog/`, ones that do not exist (already broken, and completed CRs are
  history), and absolute URLs.
- It prints each change and each skipped `../../` target, and exits non-zero
  if it would change a file outside `backlog/`.

A `#fragment` is kept but ignored when checking that the target exists.

On `dev` as of 2026-10-13 it changes 23 targets: 18 spec references
(`../../dev-docs/specs/…`), 4 links to `../../migrate/…`, and 1 to
`../../.github/workflows/check.yml`. It skips two
links to `../../TEMPLATE.md`, which came from plcc-ng's old in-repo tracker and
were already broken. A different count at cutover means the tree changed;
check the report before committing.

The rewrite is one ordinary commit on `change-requests`, so history before it
is not touched. The scratch clone has no hooks, so the cutover runs the checks
by hand.

## Checks

### `bin/check.py`

- `--root` becomes required. It defaults today to `dev`'s own root, which no
  longer holds a tracker, and a missing root should fail rather than check
  the wrong directory.
- The checks are otherwise unchanged. The docstring no longer says they run on
  hosts.
- `tests/test_check.py` gains a test that it exits non-zero without `--root`.

### Hooks

`.githooks/pre-commit` and `pre-push` find `check.py` from their own location
and check the repo that runs them:

```sh
#!/bin/sh
exec python3 "$(dirname "$0")/../bin/check.py" --root "$(git rev-parse --show-toplevel)"
```

(`pre-push` adds `--pre-push`.) The permissions spec sets `change-requests`'
`core.hooksPath` to `/workspaces/dev/.githooks`, so the hooks come from
reviewed code. Nothing sets `dev`'s own `core.hooksPath`: a commit to `dev` has
no tracker to check. Today's devcontainers do set it, in `initializeCommand`,
and would then fail every `dev` commit; they are replaced in the cutover.

### CI

`dev`'s `check.yml`, on every push and pull request to `dev`:

1. Runs the unit tests (`tests/`, `migrate/tests/`), as now.
2. Checks out `ourPLCC/change-requests` (public, no token) into
   `change-requests/`.
3. Installs the `backlog` version in `dev`'s `.backlog-version`.
4. Runs `python3 bin/check.py --pre-push --root change-requests` and, in
   `change-requests/`, `backlog doctor`.

So a tooling change that breaks against the real data fails before it merges.

`change-requests` has no workflows: a workflow is code that runs. Nothing on
GitHub's side checks a direct push to it. `bin/push.bash` runs
`check.py --pre-push` over the whole tracker after rebasing onto
`origin/main`, so a bad push that skipped the hooks makes the next ordinary
push fail and names the problem. Fix by revert, as before. A scheduled run of
`check.yml` was considered and dropped: with one active contributor pushing
several times a day, the next push comes sooner, and a bad tracker push can
damage data but not run code.

## Old links

Creating `ourPLCC/change-requests` ends GitHub's redirect from that name to
`dev`.

- **Still resolve:** URLs to tracker content under the old name
  (`github.com/ourPLCC/change-requests/blob/main/backlog/…`), since the new
  repo has the same paths; and bare mentions of the name, such as the frozen
  2026-10-08 central-tracker spec's, which name the right repo again.
- **Break:** URLs under the old name to `dev`'s own content (`dev-docs/`,
  `bin/`, `README.md`, `CONTRIBUTING.md`, `migrate/`). The migration tools
  never posted the old name in issue comments, but people may have. Before
  creating the repo, search GitHub for `ourPLCC/change-requests` across the
  org's code, issues, and pull requests, and repoint each hit at
  `ourPLCC/dev`.
- **Point at the wrong thing:** short references under the old name,
  `ourPLCC/change-requests#N`, which today mean `dev`'s issue or pull request
  `N` and afterwards mean `change-requests`'. They hide in the tracker data
  too, which moves to the new repo. Search for them with the URLs, and with
  `grep -rn 'change-requests#[0-9]' backlog/` in `dev`, and rewrite each to
  `ourPLCC/dev#N`. The CLI cannot edit a CR in `backlog/completed/`, so a
  hit there is the one tracker edit made by hand.
- **Clones whose `origin` uses the old name** (a host `../dev` cloned before
  the rename) would fetch the new repo. The rewritten hashes make a pull there
  fail on unrelated histories rather than delete `dev`'s files; the cutover
  checks and fixes the remote first anyway.

## Documentation in `dev`

In the split pull request, only the facts about where the tracker lives:

- `README.md`: `dev` holds the developer guide, org-wide specs, agent rules,
  and the tracker's tooling; the tracker itself is
  [ourPLCC/change-requests](https://github.com/ourPLCC/change-requests).
- `CONTRIBUTING.md`, "Tracking work": CRs are "tracked centrally in
  `ourPLCC/change-requests`".
- `dev-docs/tracker.md`:
  - the intro: where the data lives;
  - "Working a CR": a `dev` spec's reference is
    `../../../dev/dev-docs/specs/<file>.md`;
  - "Drafts": the demote `grep` searches `/workspaces/change-requests/backlog`;
  - "Types and projects": `dev` is the org docs and specs and the tracker's
    tooling (checks, CI, migration); the config lives in `change-requests`;
  - "Checks": `bin/check.py` takes `--root`;
  - "Working on the tracker tooling": the commands CI runs, with `--root`.

"Setup", "Pushing and collisions", and "Upgrading Backlog.md" are rewritten by
the permissions spec's step 3 (`bin/push.bash`), which merges in the same
cutover.

## The cutover

The permissions spec's step 1 must not apply `dev`'s `main` ruleset before
this split: nobody bypasses it, so tracker pushes from the host to `dev`
would stop. `dev`'s rulesets are applied here instead (step 5 below).

### Before (no outage)

- Merge `migrate/split_links.py` and its tests into `dev` in their own pull
  request; nothing uses them yet.
- Have the `bin/push.bash` pull request and each code repo's devcontainer
  pull request ready, unmerged.
- Prepare the split pull request in `dev` (deleting `backlog/`, "Checks", and
  "Documentation in `dev`"), unmerged. Its CI fails until step 3.
- Search GitHub for links under the old name (see "Old links").

### In one sitting

1. **Freeze.** On the host, `git -C ../dev remote get-url origin` names
   `ourPLCC/dev` (fix it if not), and `git status`, `git log --branches --not
   --remotes`, and `git stash list` in `../dev` are clean. Push what they show.
   No tracker edits until step 7.
2. **Create `ourPLCC/change-requests`**, public, empty. Apply its rulesets at
   once: on `main`, block force-pushes and deletion; on all tags, block
   creation, update, and deletion. No bypass actors.
3. **Fill it.** In a scratch directory on the host: clone `dev`, run
   `filter-repo` ("How the history moves"), run `migrate/split_links.py` and
   commit, add `README.md` and `.gitattributes` and commit. Run
   `bin/check.py --pre-push --root` against it and `backlog doctor` in it, then
   push `main`.
4. **Merge `dev`'s split pull request** once its CI, which now checks the
   pushed `change-requests`, passes.
5. **Apply `dev`'s rulesets:** on `main`, require a pull request, block
   force-pushes and deletion; on all tags, block creation, update, and
   deletion. No bypass actors.
6. **Merge `bin/push.bash`**, then each code repo's devcontainer pull request,
   rebuilding that repo's container as it merges.
7. **Thaw.** The outage ends when the first rebuilt container runs
   `backlog task list` against `/workspaces/change-requests`. Record the
   cutover's results in the tracker from there.

### Failure

Until step 4 merges, `dev` is untouched: delete `ourPLCC/change-requests` and
start again from step 2. The redirect, gone since step 2, does not come back,
so a failed attempt still breaks the links in "Old links". After step 4, fix
forward with a pull request to `dev` or a commit to `change-requests`.

## Verification

- `change-requests`' tree holds exactly `backlog/`, `README.md`, and
  `.gitattributes`. Before the rewrite commit, the filtered clone's
  `git rev-parse HEAD:backlog` equals `dev`'s at the freeze, so the data
  arrived byte for byte.
- `bin/check.py --pre-push --root` and `backlog doctor` pass against it.
- Every relative target under `change-requests/backlog/` that resolved before
  the split resolves after it, from `/workspaces/change-requests` beside
  `/workspaces/dev` and the code repos.
- `dev`'s tree has no `backlog/`; its CI run on `main` after step 4 checked
  `change-requests` and passed.
- `bin/check.py` without `--root` exits non-zero.
- A push to `dev`'s `main` without a pull request is rejected; a force-push to
  `change-requests`' `main` is rejected; pushing a tag to either is rejected.
- A rebuilt container lists CRs with `backlog task list` and, with
  `bin/push.bash`, pushes a tracker change.

## Out of scope

- `bin/push.bash`, the shared volumes, and the devcontainer changes (the
  permissions spec and its CRs).
- A transition that keeps the tracker available throughout: with one active
  contributor on one machine, a planned outage costs less than temporary
  bridge changes in every code repo.
- Rewriting `dev`'s history to drop `backlog/`.
- Workflows in `change-requests`.
