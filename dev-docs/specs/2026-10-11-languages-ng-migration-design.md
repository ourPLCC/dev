# Migrating languages-ng's tracker into `ourPLCC/dev` — design

Date: 2026-10-11

## Problem

languages-ng still keeps its own file-based tracker in `dev-docs/issues/`
(53 issues, 001–053). The central tracker design
([2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md),
"the central spec" below) says languages-ng is migrated "from this spec", but
the spec was written while migrating plcc-ng, and languages-ng differs in ways
it does not settle:

- Its issues use YAML frontmatter, not plcc-ng's `**Type:**` lines, and record
  closure in a `closed:` field instead of moving files to `done/`. `migrate/`
  reads only plcc-ng's format.
- Its prose uses a bare `#N` for three things: its own issues, its GitHub pull
  requests, and plcc-ng issues. The central spec's rule for unqualified `#N`
  assumes plcc-ng's usage.
- Its agent and contributor docs predate the org developer guide
  ([2026-10-10-org-developer-docs-design.md](2026-10-10-org-developer-docs-design.md)),
  which replaced the central spec's per-repo `CLAUDE.md` setup with an
  `AGENTS.md` that imports the org guide.

This spec records only what languages-ng adds to the central spec. Everything
the central spec says about the migration and not overridden here applies.

## Supersedes

[2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md),
for languages-ng only:

- "Duplicated upstream findings": the list of hand-copied issues (below adds
  languages-ng 010).
- "Links", the rule for an unqualified `#N`.

## Decision summary

Extend `migrate/` with a languages-ng parser and loader rather than converting
by hand. The issues hold about 174 Markdown links and 118 bare `#N`
references outside code; the existing link rewriting, emitting, and
verification already handle the links, fences, section markers, and provenance,
and the same code rewrites links in the code repo's docs at switch-over. Only
reading the files is new. Where a reference's meaning cannot be read off its
text, the tool reports it and a human decides; it does not guess.

## Reading languages-ng issues

A new driver beside `migrate/plcc_ng.py` loads every `dev-docs/issues/NNN-*.md`
(not `TEMPLATE.md` or `index.md`) and produces the same `LegacyIssue` record,
so `emit.py` and `links.py` are reused unchanged except as noted below.

- **Frontmatter** keys are exactly `type`, `target`, `opened`, `closed`, and
  optionally `upstream`. Any other key, or a missing required key, stops the
  run with an error naming the file.
- **Title** from the `# NNN - Title` line; the number must match the
  filename's.
- **Template comment:** stripped by the existing `Classify by user-facing
  impact` pattern (39 files carry it).
- **Sections:** `## Summary`, when present (21 issues), comes first, demoted
  to `### Summary`, followed by the `## Description` text under its own
  `### Description` heading (without one, the description would read as part
  of the summary); then every other section demoted to `###`, as for plcc-ng.
  Without a Summary, the description text leads unheaded, as for plcc-ng. The
  Summary leads because it is the one-paragraph triage view.

| CR field | Source |
| --- | --- |
| ID | `CR-<N + 500>`. No number repeats, so no duplicate-remap range is used. |
| status, folder | `closed:` set → `Done` in `completed/`; empty → per triage |
| `created_date` | `opened:` |
| `project` | `target:` `this repo` → `languages-ng`; `ourPLCC/plcc-ng` → `plcc-ng`; anything else is an error |
| `type` | `type:` through the existing type map, then triage overrides |

`upstream:` is not carried as a field; each issue's prose already says where
it was filed upstream.

`verify.py` and `citations.py` import plcc-ng's loader today. They take the
repo's driver (loader, triage placement, provenance predicate) as a parameter
so both repos use them.

## Bare `#N` references

Outside code fences, code spans, and links, a bare `#N` in a languages-ng issue
is resolved by its context:

| Context | Count | Result |
| --- | --- | --- |
| Preceded by `PR` or `pull request` | 6 | `[#N](https://github.com/ourPLCC/languages-ng/pull/N)` |
| Qualified with plcc-ng (`plcc-ng #187`, `` `ourPLCC/plcc-ng` issue #187 ``) | 4 | `CR-N` (plcc-ng's offset, +0) |
| Unqualified, N ≤ 53 | 92 | `CR-<N + 500>`, listed in the report as defaulted, with its surrounding text |
| Unqualified, N > 53 | 16 | Left as text and listed in the report with its surrounding text; resolved by a triage entry |

The N ≤ 53 default is languages-ng's own convention: inside issue files a bare
`#N` names an issue, and its PRs are written `PR #N` (languages-ng 052 and 053
limited the ambiguity to commit messages and PR bodies). A spot check of 9
randomly chosen references found all 9 pointing at the issue the rule chooses,
and languages-ng's pull requests stop at #24.

A triage entry for an N > 53 reference names the file and the reference and
gives its replacement (for example `CR-187`, or the text unchanged). Until
every such reference has an entry, the conversion still runs but `verify.py`
fails, so the dry run can produce the list and the final run cannot ship
with gaps.

## Triage

Recorded in `migrate/languages-ng-triage.json`, in the same shape as
`plcc-ng-triage.json` plus two tables: `duplicates` (legacy number → plcc-ng
number) and `references` (the N > 53 decisions). A re-run reapplies it.

**Duplicates of plcc-ng issues** become `Done` + `wontdo` in `completed/`,
with project `plcc-ng`, the type of the plcc-ng issue they duplicate, and the
final summary `Duplicate of CR-<n>, filed upstream by hand.` These are all the
issues whose `target:` is plcc-ng:

| languages-ng | plcc-ng | languages-ng status |
| --- | --- | --- |
| 003 | 162 | closed |
| 004 | 163 | closed |
| 006 | 164 | closed |
| 010 | 174 | closed |
| 022 | 185 | closed |
| 036 | 186 | closed |
| 037 | 187 | open |
| 038 | 188 | closed |

010 is not in the central spec's list but reports the same arbno defect as
plcc-ng 174, filed the same day.

**Open issues about the retired tracker** become `Done` + `wontdo` in
`completed/` with the final summary `Obsolete: languages-ng's file-based
tracker was retired.`

| Issue | Why obsolete |
| --- | --- |
| 020 | `close.bash` argument handling; `bin/issues/` is deleted |
| 043 | `new.bash --help` creates an issue; same |
| 050 | `head -n N` coupled to `TEMPLATE.md`, which is deleted |
| 051 | `close.bash` argument paths untested; same as 020 |
| 053 | Bare `#N` is ambiguous in commits and PRs; CR IDs replace it, and GitHub does not act on `Closes CR-N` |

**Other open issues:**

- `To Do` CRs: 016, 019, 027, 028, 033, 039, 040, 041, 044. Each has
  testable acceptance criteria and a type that already fits the org types.
- `In Progress`: 046. Its fix is merged, but no release has shipped since,
  so it closes on verification by a real release.
- Draft: 042. It records an observation, not a diagnosis, so it fails the
  litmus test, and nothing cites it (other issues, specs, plans, and commits
  checked).

**Expected counts:** `completed/` 42 (36 closed issues, open 037, the five
obsolete), `tasks/` 10, `drafts/` 1.

## Switch-over in languages-ng

**Devcontainer.** Keep the digest-pinned `plcc-ng` image: CI runs the same
image and `bin/tests/image-pin.bats` keeps the two identical. Add plcc-ng's
tracker setup:

- `initializeCommand` that clones `../dev` if missing and sets its
  `core.hooksPath`;
- mounts: `../dev` at `/workspaces/dev`, and a named volume
  `languages-ng-claude` at `/home/vscode/.claude`, so assistant memory and
  settings survive a rebuild;
- `containerEnv`: `BACKLOG_CWD=/workspaces/dev`, and `safe.directory` entries
  for `/workspaces/dev` and `/workspaces/languages-ng`;
- `postCreateCommand`: chown the volume, install the pinned `backlog`, assert
  `git status` in both repos, run `bin/install/claude-imports.bash` (copied
  from plcc-ng), and keep `bin/install/bats.bash`.

If the image lacks `node`/`npm` (for `backlog`) or `jq` (for the import
approval), add the devcontainer features that provide them.

**`CLAUDE.md` → `AGENTS.md`.** `AGENTS.md` imports `../dev/ORG-AGENTS.md`,
`../dev/CONTRIBUTING.md`, then `CONTRIBUTING.md`, each on its own line, and
keeps only agent-only rules. Each current section goes:

| `CLAUDE.md` section | Goes to |
| --- | --- |
| Anything worth remembering goes in a committed file | Dropped. It worked around the missing `~/.claude` volume, which the devcontainer now has. |
| Read CONTRIBUTING.md | Dropped; the import replaces it |
| Creating and closing issues | Dropped; the org guide covers the tracker |
| Design specs and implementation plans (locations) | Dropped; the org guide covers both |
| Shell and config embedded in a plan; Verifying a subagent's commits | `AGENTS.md`, with issue links rewritten to `CR-5xx` |
| Course-material impact log | `CONTRIBUTING.md`; it is a workflow rule for everyone |

**`CONTRIBUTING.md`** opens with the link to the org developer guide and a
"Where this repo differs" section. Like plcc-ng's, that section notes that the
existing `dev-docs/plans/` are kept plans, frozen as history, with none added.
The development-environment section covers the `../dev` clone, gives the
tracker `project` value `languages-ng`, and says old numbers resolve at +500
(`#12` is `CR-512`). The issue-script rows leave the commands table.

**Retire the old tracker.** Delete `dev-docs/issues/`,
`dev-docs/issue-conventions.md`, `bin/issues/`, and
`bin/tests/issues-{check,close,list}.bats`. Add `.plans/` to `.gitignore`
and allow `Bash(backlog:*)` in `.claude/settings.json`.

**Links elsewhere in the repo.**

- Markdown files (frozen specs and plans, reviews, `dev-docs/index.md`):
  `rewrite_repo_doc` rewrites links into `dev-docs/issues/` to `CR-5xx` and
  links to retired files to plain text. Frozen documents get link-only edits;
  their bare `#N` prose is left alone.
- Comments naming issue paths, edited by hand to `CR-5xx`:
  `.devcontainer/devcontainer.json` (011), `.releaserc.yaml` (046, 048),
  `bin/check-run-complete.bash` (031).
- Live docs (`AGENTS.md`, `CONTRIBUTING.md`, `dev-docs/index.md`): bare `#N`
  is rewritten to `CR-5xx` as well.

## Order

1. `migrate/` gains the languages-ng driver, with tests, on its own branch in
   this repo.
2. Dry run from a fresh clone of languages-ng `main`, into a scratch copy of
   the tracker. A human reviews the report and settles the N > 53 references.
3. The languages-ng switch-over branch is prepared.
4. The conversion re-runs from languages-ng `main` (the freeze point), picking
   up anything filed since the dry run, and lands in the tracker.
5. Human checkpoint before merging the languages-ng branch: rebuild from it on
   the host; the container starts, `backlog task list` works, and
   `bin/test.bash` passes. CI is green. From this point no issue is filed in
   `dev-docs/issues/`.

## Verification

- `migrate/tests` cover the parser, the loader, the `#N` rules, and triage
  application; the plcc-ng tests still pass.
- `verify.py` for languages-ng: per-folder counts match the expected counts
  above; `backlog task view` succeeds for every converted ID; `backlog doctor`
  and `bin/check.py` are clean.
- The report lists type mappings, duplicates, won't-do issues, drafts,
  defaulted `#N` references, and link findings.
- In languages-ng after switch-over, `grep -rn 'dev-docs/issues'` finds
  nothing outside `.git` and the frozen `dev-docs/plans/`,
  `dev-docs/specs/`, and `dev-docs/reviews/`. Frozen documents get
  link-only edits (above), so their plain-text mentions of old paths and
  commands stay, as plcc-ng's do.

## Rejected alternatives

| Alternative | Why not |
| --- | --- |
| Convert the 53 issues by hand | About 380 link and reference edits plus frontmatter, section markers, and provenance per file; a missing section marker hides text from search with no error |
| Ask a human about all 108 unqualified `#N` | The 9-of-9 spot check and the repo's convention make 92 of them mechanical; the list would confirm the default every time |
| Guess N > 53 as plcc-ng issues | Probably right, but it is a guess, and 16 checks are cheap |
| Keep `CLAUDE.md`'s memory section, reworded | Its premise was the missing volume; with the volume, the org rule (commit what a teammate needs) covers the rest |
