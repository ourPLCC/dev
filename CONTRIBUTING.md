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

## Working in a devcontainer

Each ourPLCC code repo has a devcontainer. In it, you and any agent you run
act on GitHub as you, through one token of yours, and GitHub's settings, not
the agent's instructions, set the limits. The design and its reasons are in
[the devcontainer permissions spec](dev-docs/specs/2026-10-13-devcontainer-permissions-design.md).

### Your token

1. On GitHub, create a fine-grained personal access token (Settings →
   Developer settings → Personal access tokens → Fine-grained tokens):
   - Resource owner: `ourPLCC`. Repository access: all repositories.
   - Repository permissions: Contents read and write, and Pull requests read
     and write. Nothing else.
   - Expiration: 90 days at most.
2. Wait for an org owner to approve it; until then it cannot reach ourPLCC.
3. In any ourPLCC container, run `gh auth login --with-token` and paste the
   token. Every ourPLCC container on the machine shares the login, and it
   survives rebuilds.

Never use plain `gh auth login`: its browser flow yields a token for every
repo you can reach. When the token expires, make a new one, have it approved,
and load it again. To revoke it, delete it on GitHub; to forget it on one
machine, run `docker volume rm ourplcc-gh` on the host.

### What the container cannot do

From the container you can push branches, open and update pull requests, and
push tracker changes with `/workspaces/dev/bin/push.bash`. You cannot push to
any repo's `main` except `change-requests`', to `gh-pages`, or tags; push a
change to `.github/workflows/`; run or re-run workflows; or change settings,
rulesets, environments, or secrets. Do those in GitHub's web UI, or on the
host with your own credentials.

Merging a pull request is yours alone: in a code repo, merging to `main` is
the release. Agents never merge.

### Approving a release

A release reaches PyPI only after you approve it. Open the release's workflow
run in the repo's Actions tab, choose **Review deployments**, select `pypi`,
and approve. The token cannot approve, so no agent can.

### Codespaces

A Codespace uses its own GitHub token; do not run `gh auth login` there. When
you create one, GitHub asks you to authorize access to `ourPLCC/dev` and
`ourPLCC/change-requests`: authorize it, or both stay read-only and
`bin/push.bash` fails. A full rebuild of a Codespace deletes its volumes and
any tracker commits you have not pushed, so push right away.

### Moving from the host clone

Before the devcontainers cloned `dev` into a volume, it lived on the host
beside the code repos, and tracker changes were pushed from there. Move once:

1. In the host's `../dev`, check that `git status`,
   `git log --branches --not --remotes`, `git worktree list`, and
   `git stash list` come back clean. `dev`'s `main` no longer takes direct
   pushes, so re-enter any tracker change they show by hand, in the
   container, after step 3.
2. Create your token and wait for its approval.
3. Rebuild one ourPLCC container; it clones `dev` and `change-requests` into
   their volumes. Run `gh auth login --with-token`, then push your next
   tracker change with `/workspaces/dev/bin/push.bash`.
4. On a Windows host, check out each code repo again
   (`git rm -r --cached -q . && git reset --hard`), or clone it fresh.
5. Delete the host's `../dev`. Do not check out a branch of any repo from
   before the move, or its devcontainer recreates `../dev`.
