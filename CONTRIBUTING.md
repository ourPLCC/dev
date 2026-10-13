# ourPLCC developer guide

How we work in every ourPLCC repository. Each repo's own `CONTRIBUTING.md`
builds on this guide with what is specific to that repo.

## Precedence

This guide applies unless a repo's `CONTRIBUTING.md` or `dev-docs/` deviates
**explicitly and with a reason** ("Unlike the org guide, this repo … because
…"). An unexplained difference is drift; fix it in whichever copy is wrong.
Repo docs link to this guide rather than restating it, even to agree with it.

## Tracking work

- **GitHub issues** are conversations with people outside the team. Anyone
  reports a problem or suggests an idea by opening an issue on the relevant
  code repo.
- **Change requests (CRs)** are the work we commit to, tracked centrally in
  [ourPLCC/change-requests](https://github.com/ourPLCC/change-requests) with
  [Backlog.md](https://github.com/MrLesk/Backlog.md). A CR is
  work in exactly one repo with testable acceptance criteria, and has an ID
  `CR-N`. Work spanning repos is one CR per repo, linked by dependencies.
- **Drafts** are ideas we have not committed to. Never cite one.

Search before filing; create CRs and drafts with the `backlog` CLI. The full
guide — filing, statuses, IDs, references, checks — is
[dev-docs/tracker.md](dev-docs/tracker.md).

## How work flows

1. **Issue → CR.** A maintainer files a CR for work we commit to, saying
   *why* it exists. No implementation plan at filing time.
2. **Brainstorm → spec.** Set the CR `In Progress` and assign yourself. Settle
   *what* to build in a spec, update the CR's acceptance criteria to match,
   and add the spec to the CR's references.
3. **Plan.** The implementation plan lives in `.plans/` inside the worktree
   (gitignored) and is deleted with it. Plans are not kept.
4. **Branch → PR.** Work on a branch, never on `main`; the PR names the CR.
5. **Merge → close.** After merge, triage the CR's notes, check each
   acceptance criterion against evidence, write a final summary, and set the
   CR `Done`. If only a later event can prove the change (e.g. a real
   release), close the CR once that happens.

## Specs

- A spec lives in the repo whose code it changes, in `dev-docs/specs/`. A
  decision that binds more than one repo has its spec in this repo's
  [dev-docs/specs/](dev-docs/specs/); the work is still one CR per repo, and
  each CR references that spec.
- Specs do not cite CRs; the CR references the spec.

## Branches and commits

- **Branch names** start with the CR ID and describe the work:
  `cr-1042-fix-scanner-skip-regression`.
- **Commits** follow conventional-commit style: `feat(scope): …`,
  `fix(scope): …`, `docs(scope): …`, `test(scope): …`, `refactor(scope): …`,
  `build(scope): …`, `ci: …`, `chore: …`. Match the scope names already in use
  in the repo's git log. A CR's type is the commit type of the change that
  decides its version impact (`fix` → patch, `feat` → minor); its branch may
  carry other commit types too.
