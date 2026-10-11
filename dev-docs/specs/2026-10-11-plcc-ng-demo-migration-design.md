# Migrating plcc-ng-demo's tracker into `ourPLCC/dev` — design

Date: 2026-10-11

## Problem

plcc-ng-demo keeps a small file-based tracker in `dev-docs/issues/`: five
issues, 001–005, all closed. The central tracker design
([2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md),
"the central spec" below) says plcc-ng-demo is migrated "from this spec", but
leaves two things open:

- `migrate/` converts plcc-ng's tracker only. plcc-ng-demo's files use the
  same format (a `**Type:**` line, closed issues in `done/`), but the plcc-ng
  driver hard-codes plcc-ng's project, offset, and GitHub URL.
- Three demo issues were copied into plcc-ng by hand. The central spec's rule
  for such duplicates names only languages-ng's.

This spec records only what plcc-ng-demo adds to the central spec and to the
[languages-ng migration spec](2026-10-11-languages-ng-migration-design.md).
Everything those specs say about the migration and do not override here
applies.

## Supersedes

[2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md),
for plcc-ng-demo only: "Duplicated upstream findings" (below lists the demo's).

## Decision summary

Add a plcc-ng-demo driver to `migrate/` that reuses plcc-ng's loader and
converter with the demo's project, offset (+800), and GitHub URL, and adds a
`duplicates` triage table in the shape languages-ng uses. Converting by hand is
not an option: the `backlog` CLI allocates IDs itself, so it cannot create
`CR-801`–`CR-805`, and the tracker files are not edited by hand.

No legacy number repeats, so no duplicate-number range is reserved.

The issues contain no Markdown links and no bare `#N`, so link rewriting has
nothing to do. The driver still runs it, so the report would show anything
missed.

## Triage

Recorded in `migrate/plcc-ng-demo-triage.json`: `open` is empty, and
`duplicates` maps legacy number → plcc-ng number.

**Duplicates of plcc-ng issues** become `Done` + `wontdo` in `completed/`,
with project `plcc-ng`, the type of the plcc-ng CR they duplicate, and the
final summary `Duplicate of CR-<n>, filed upstream by hand.`

| plcc-ng-demo | CR | plcc-ng | type |
| --- | --- | --- | --- |
| 001 | CR-801 | CR-159 | docs |
| 002 | CR-802 | CR-160 | fix |
| 005 | CR-805 | CR-161 | feat |

CR-160 and CR-161 already cite CR-802 and CR-805 as where they were first
filed, so those IDs must exist.

**Demo-local issues** become `Done` in `completed/`, project `plcc-ng-demo`,
type from the legacy `**Type:**`:

| plcc-ng-demo | CR | type |
| --- | --- | --- |
| 003 | CR-803 | docs |
| 004 | CR-804 | chore |

**Expected counts:** `completed/` 5, `tasks/` 0, `drafts/` 0.

## Switch-over in plcc-ng-demo

**Devcontainer.** Set up as plcc-ng's (already done: the `../dev` clone and
mount, `BACKLOG_CWD`, `safe.directory`, the `plcc-ng-demo-claude` volume,
the pinned `backlog`, and `bin/install/claude-imports.bash`).

**`AGENTS.md`** imports `../dev/ORG-AGENTS.md`, `../dev/CONTRIBUTING.md`,
then `CONTRIBUTING.md`, one per line. It has no repo-specific agent rules yet,
so it has no section for them.

**`CONTRIBUTING.md`** (new) opens with the link to the org developer guide,
then:

- "Where this repo differs": nowhere; the existing
  `dev-docs/plans/2026-07-21-plcc-ng-demo.md` is a kept plan, frozen as
  history, with none added.
- Development environment: the `../dev` clone and mount, the tracker
  `project` value `plcc-ng-demo`, old numbers at +800 (`#3` is `CR-803`), and
  why the container approves `AGENTS.md`'s imports and how to check
  (`/memory`), as plcc-ng's says.
- Commands: `bin/install/claude-imports.bash`.

**Retire the old tracker.** Delete `dev-docs/issues/`, `bin/issues/`, and
`dev-docs/roadmap.md` (it holds only the old tracker's empty "Open Issues"
list). Allow `Bash(backlog:*)` in `.claude/settings.json`.

**Frozen documents** (`dev-docs/specs/`, `dev-docs/plans/`) mention
`dev-docs/issues/` and `bin/issues/` only as plain text, so they are not
edited.

## Order

1. `migrate/` gains the plcc-ng-demo driver, with tests, on its own branch in
   this repo.
2. Dry run from plcc-ng-demo `main` into a scratch copy of the tracker; a
   human reviews the report.
3. The plcc-ng-demo switch-over branch is prepared.
4. The conversion re-runs from plcc-ng-demo `main` (the freeze point) and
   lands in the tracker.
5. Human checkpoint before merging the plcc-ng-demo branch: rebuild from it
   on the host; the container starts, `backlog task list` works, and
   `/memory` lists the imported files. From this point no issue is filed in
   `dev-docs/issues/`.

## Verification

- `migrate/tests` cover the new driver and the `duplicates` table; the
  plcc-ng and languages-ng tests still pass.
- `verify.py` for plcc-ng-demo: per-folder counts match the expected counts
  above; `backlog task view` succeeds for 801–805; `backlog doctor` and
  `bin/check.py` are clean.
- In plcc-ng-demo after switch-over, `grep -rn 'dev-docs/issues\|bin/issues\|roadmap'`
  finds nothing outside `.git` and the frozen `dev-docs/plans/` and
  `dev-docs/specs/`, and no relative Markdown link points at a deleted file.

## Rejected alternatives

| Alternative | Why not |
| --- | --- |
| Duplicates as plain `Done` in project `plcc-ng-demo` | They were closed before the move, but the languages-ng rule already settles hand-copied upstream findings; one rule for both repos |
| Generalize `plcc_ng.py` in place with command-line options | A driver per repo is how `drivers.py`, `verify`, and `citations` already select behavior |
| Skip the spec and record the decisions in the CRs | Specs hold decisions and CRs reference them; the duplicate rule overrides the central spec, which belongs in a spec |
