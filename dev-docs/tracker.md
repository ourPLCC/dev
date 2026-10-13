# The change-request tracker

The central tracker for work on the ourPLCC code repositories: plcc-ng,
languages-ng, plcc-ng-demo, plcc-ng-devcontainer, and course-materials-ng. It
is managed with [Backlog.md](https://github.com/MrLesk/Backlog.md). Its data
lives in [ourPLCC/change-requests](https://github.com/ourPLCC/change-requests);
its checks and tooling live here, in `dev`. This is
the full guide to using it; the [developer guide](../CONTRIBUTING.md) gives
the short version and the workflow around it.

Checked against Backlog.md **1.53.0** (see `.backlog-version`). Its built-in
`backlog instructions` differ from this guide on plans, cleanup, and drafts;
this guide wins.

## Setup

- Each code repo's devcontainer clones this repo into the shared volume
  `ourplcc-dev`, mounted at `/workspaces/dev`, and the tracker data,
  [ourPLCC/change-requests](https://github.com/ourPLCC/change-requests),
  into `ourplcc-change-requests`, mounted at `/workspaces/change-requests`.
  Every ourPLCC container on a machine shares both. It sets
  `BACKLOG_CWD=/workspaces/change-requests` and installs the pinned `backlog`
  CLI, and on start fast-forwards `dev`'s `main` when it is checked out and
  clean.
- Commit and push inside the container, with `/workspaces/dev/bin/push.bash`,
  after every tracker change. Backlog.md commits every change automatically
  (`auto_commit: true`); the volume is not a backup.
- Hooks in `.githooks/` run `bin/check.py` (Python 3, standard library) on
  commit and push; the devcontainer sets `change-requests`' `core.hooksPath`
  to `/workspaces/dev/.githooks`, so the hooks come from reviewed code.
- Hosts: Linux, macOS, or Windows; or a Codespace.

## Vocabulary

- **Change request (CR):** committed work in exactly one repo — a feature, a
  fix, or an infrastructure change — with testable acceptance criteria. ID
  `CR-N`. Backlog.md stores them in `backlog/tasks/` ("tasks" is the tool's
  fixed folder name; we call them change requests).
- **Draft:** an idea we have not committed to. ID `DRAFT-N` (a separate,
  recycled sequence). Not on the board or in `task list`.
- **GitHub issue:** a conversation with a human on a code repo. Not tracked
  work.

## Filing

1. Search first, across all projects — duplicates and root causes often live
   in another repo: `backlog search "<words>" --plain`.
2. Can you write testable acceptance criteria? **Yes → CR** (even if *how* is
   still open). **No** (it is unclear *whether* we want it) **→ draft.**
3. Create it (only with the human's approval):

   ```bash
   backlog task create "<title>" --project plcc-ng --type fix \
     -d 'Why this exists: the problem or need.' --ac 'Testable criterion'
   backlog task create "<title>" --draft --project plcc-ng -d 'The idea.'
   ```

   Description = *why*. No implementation plan at filing time.

## Working a CR (superpowers flow)

1. **Brainstorm:** `backlog task edit CR-N -s "In Progress" -a @<name>`.
   Promote a draft (`backlog draft promote DRAFT-N`) once *what* is settled.
   The spec goes in the code repo's `dev-docs/specs/` (or this repo's, for a
   decision that binds more than one repo); update the CR's acceptance
   criteria to match and add the spec as a reference:
   `backlog task edit CR-N --add-ref ../../../plcc-ng/dev-docs/specs/<file>.md`
   (for this repo: `../../../dev/dev-docs/specs/<file>.md`). Specs do not cite
   CRs.
2. **Plan and execute:** the plan lives in `.plans/` inside the worktree
   (gitignored) and is deleted with it. Plans are not kept. During automated
   execution, record discovered work in the CR's notes —
   `backlog task edit CR-N --append-notes "…"` — never as new CRs.
3. **Branch** `cr-N-short-slug`; the PR names the CR.
4. **Close after merge:** triage the CR's notes with the human (new draft,
   new CR, fold into an existing CR, or drop); check each acceptance criterion
   against evidence (`--check-ac 1`); write `--final-summary "Changed X,
   verified by Y."`; set `-s Done`.

**Close on verification:** when only a later event can prove the fix (e.g. a
real release run), leave the CR `In Progress` after merge and close it once
verified.

## Statuses

`To Do` → `In Progress` → `Done`. `Done` CRs move to `completed/` when a human
runs `backlog cleanup` (interactive) or `backlog task complete CR-N`; they stay
viewable by ID (`backlog task view N`) and greppable, but tool search and edit
no longer reach them. To reopen, file a new CR that cites the old one.

## Won't do, duplicate, obsolete

```bash
backlog task edit CR-N -s Done --add-label wontdo --final-summary 'Why not (for a duplicate: name the surviving CR).'
backlog task complete CR-N
```

**Never `backlog task archive`.** Archived CRs drop out of ID lookup, and
archiving the highest-numbered CR lets its number be reallocated.
`bin/check.py` fails if anything is in `archive/`. `--ready` treats a won't-do
dependency as satisfied, so review the CRs that depended on it.

## Drafts

- **Never cite a draft** — not in CRs, specs, commits, or branch names. If
  something must refer to a draft's content, copy the content. Promotion gives
  a new `CR-N` and does not rewrite old `DRAFT-N` mentions; draft numbers are
  reused. `bin/check.py` fails on any `DRAFT-N` outside its own file.
- **Demote** (`backlog task demote CR-N`) only when nothing cites the CR:

  ```bash
  grep -rn 'CR-N\b' /workspaces/change-requests/backlog /workspaces/<repo> --include='*.md'
  git -C /workspaces/<repo> log --all --oneline -i --grep 'cr-N\b'
  ```

  If it is cited, rewrite its acceptance criteria instead.

## Types and projects

| Type | Use for |
|---|---|
| `fix` | A defect in a shipped package (bumps the patch version) |
| `feat` | New behavior in a shipped package (bumps the minor version) |
| `docs` | Documentation content |
| `test` | Tests only |
| `refactor` | Structure changes without behavior change |
| `chore` | Everything else: tooling, CI, build, devcontainer, this tracker, upkeep |

A CR's type is the conventional-commit type of the change that decides its
version impact; its branch may carry other commit types too.

Every CR has exactly one `project`: `plcc-ng`, `languages-ng`, `plcc-ng-demo`,
`plcc-ng-devcontainer`, `course-materials-ng`, or `dev` (this repo: the org
docs and specs, and the tracker's checks, CI, and migration tooling; the
config is `change-requests`' `backlog/config.yml`). Work spanning repos is one
CR per repo linked with `--dep` (no umbrella CRs); `backlog task list --ready`
hides a CR until its dependencies are done.

## IDs

| Range | Meaning |
|---|---|
| `CR-1`–`CR-399` | plcc-ng legacy issues, same number: plcc-ng `#160` is `CR-160` |
| `CR-400`–`CR-499` | plcc-ng legacy numbers used twice (035, 039, 043): the second at +400 |
| `CR-501`–`CR-699` | languages-ng legacy issues (+500): languages-ng `#12` is `CR-512` |
| `CR-801`–`CR-899` | plcc-ng-demo legacy issues (+800) |
| `CR-999` | Seed — do not touch |
| `CR-1000`+ | New CRs |

Lookups are numeric: `backlog task view 160` finds `CR-160`. Each migrated CR
ends with `Migrated from <repo> #NNN.`.

## References and links

- **Between CRs:** bare IDs (`CR-160`), never paths.
- **To code:** relative links written as if the CR is in `backlog/tasks/`:
  `[emit.py](../../../plcc-ng/src/plcc/java/emit.py)`. They resolve in the IDE
  for `tasks/` and `completed/`; inside a code repo's container, links into
  *other* repos do not resolve (only that repo and this one are mounted).
- **To specs:** in `references`, as such a link.
- **To GitHub issues:** full URL in `references`; comment on the GitHub issue
  with the CR ID.
- **From code:** the branch name `cr-N-…`. `git log --merges -i --grep cr-N`
  finds the merge; `git log M^1..M^2` lists its commits.

## Searching

`backlog search "<q>" --project plcc-ng --plain` or
`backlog task list --search "<q>" --project plcc-ng --plain` filter by project
(plain output does not show each hit's project; `--json` does). Search all
projects before filing.

## Pushing and collisions

Push with `/workspaces/dev/bin/push.bash`. It takes a lock that every ourPLCC
container on the machine shares, fetches, rebases your tracker commits onto
`origin/main`, runs `bin/check.py --pre-push`, and pushes. It stops without
pushing, and says why, when:

- `change-requests` has uncommitted changes: commit or discard them.
- The rebase conflicts: it aborts the rebase and keeps your commits. Run
  `git pull --rebase` in `/workspaces/change-requests`, resolve, and run it
  again.
- `bin/check.py` fails. A duplicate ID means two people allocated the same
  number before either pushed: run `backlog doctor --fix` to renumber the
  unpushed CR, commit, and run it again.
- The push is rejected because another push landed after the fetch: run it
  again.
- It waited two minutes for the lock: another push or a container start
  holds it. Run it again; if it keeps timing out, look for a stuck
  `bin/push.bash` or `shared-clones.bash` in your other containers.

Do not edit the tracker from another container while a push runs. Backlog.md
does not take the lock, so its commit can land in the middle of the rebase
and be dropped.

Locally, every container shares one tracker tree, so one person's sessions
never allocate the same ID. Two Codespaces, or a Codespace and a local
container, are two trees and can collide like two people. Nothing on GitHub
checks a direct push to `change-requests`; the next `bin/push.bash` fails on
a bad one and names the problem, and `dev`'s CI checks `change-requests` on
every push to `dev`. Fix problems by revert.

## Checks (`bin/check.py`)

`bin/check.py --root <tracker>` fails on: duplicate IDs (drafts included) or a filename that does not match its `id`; a
`DRAFT-N` cited outside its own file; a CR without exactly one configured
`project` or `type`; an unconfigured label; anything in `archive/`; and, with
`--pre-push`, uncommitted changes under `backlog/`. `CR-999` is exempt from
the project and type rules.

## Upgrading Backlog.md

1. Change `.backlog-version`.
2. Regenerate `upstream/<new>/` (`backlog instructions <guide>` for
   `overview`, `task-creation`, `task-execution`, `task-finalization`,
   `init-required`) and diff it against the previous version.
3. Fold relevant changes into this guide (and, where they touch agent
   rules, into [ORG-AGENTS.md](../ORG-AGENTS.md)) and update the version it
   was checked against — in the same commit.
4. Once the change merges, rebuild every ourPLCC container to pick up the new
   version; each warns on start while its `backlog` differs from
   `.backlog-version`.

## Migration tooling

`migrate/` converts legacy in-repo trackers (Python 3 standard library), with
one driver per repo: `python3 -m migrate.plcc_ng`,
`python3 -m migrate.languages_ng`, and `python3 -m migrate.plcc_ng_demo`
(each takes `--repo`, `--tracker`, `--triage`, `--report`).
`python3 -m migrate.verify` and `python3 -m migrate.citations` take
`--driver plcc-ng|languages-ng|plcc-ng-demo` (default `plcc-ng`);
`python3 -m migrate.repo_links --project <repo>` picks the driver from the
project. Decisions are in `migrate/<repo>-triage.json`, results in
`migrate/reports/<repo>.md`. plcc-ng's triage keys (`open`,
`type_overrides`) are a legacy number (`"105"`) or, for a number two files
share, the file stem (`"035-python-emitter-missing-semantics-blocks"`).
plcc-ng-demo's tracker has plcc-ng's format, so its driver runs plcc-ng's
converter at offset +800; its triage file adds `duplicates` (legacy number →
the plcc-ng CR it duplicates), per
[its migration spec](specs/2026-10-11-plcc-ng-demo-migration-design.md).
languages-ng's are legacy numbers only, and its triage file adds
`duplicates` (legacy number → the plcc-ng CR it duplicates), `references`
(legacy number → `{"#N": replacement}` for a bare `#N` the tool cannot
resolve), and open entries `"as": "wontdo"` with a `summary`; its rules are in
[its migration spec](specs/2026-10-11-languages-ng-migration-design.md). Tools
that call `backlog` set `BACKLOG_CWD` to their target explicitly.

## Working on the tracker tooling

`bin/check.py` and `migrate/` use only the Python 3 standard library, so the
hooks run in every container without extra installs. Changes to `dev` go
through a pull request; its `main` takes no direct pushes. In a container,
run what CI runs (`.github/workflows/check.yml`) before pushing a tooling
change:

```bash
python3 -m unittest discover -s tests -t .
python3 -m unittest discover -s migrate/tests -t .
python3 bin/check.py --pre-push --root /workspaces/change-requests
(cd /workspaces/change-requests && backlog doctor)
```

A new rule in `bin/check.py` gets a test in `tests/test_check.py` and a line
in [Checks](#checks-bincheckpy) above.

`bin/push.bash`'s tests in `tests/test_push.py` build throwaway repos; change
them with the script.
