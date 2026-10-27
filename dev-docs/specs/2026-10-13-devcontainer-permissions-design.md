# Permissions in ourPLCC devcontainers — design

Date: 2026-10-13

## Problem

Nobody can push from inside a local ourPLCC devcontainer. The remotes are
HTTPS, there is no `gh` CLI and no credential helper for github.com, and the
SSH agent VS Code forwards is unused. So every push happens on the host: each
code branch, and each tracker change Backlog.md auto-commits. An agent in the
container can commit but cannot push a branch or open a PR, which stalls the
"Branch → PR" step of the workflow.

Two more limits come from how the tracker clone reaches the container. The
devcontainer's `initializeCommand` clones `../dev` on the host in POSIX shell,
so Windows hosts cannot use it; and the container bind-mounts that host
folder, so a Codespace cannot start at all.

This spec decides, for every ourPLCC repo's devcontainer, what a human and an
agent in it may do on GitHub, how the credential for that reaches the
container, which GitHub-side settings make those limits hold, and where the
shared clones live.

## Supersedes

- [2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md):
  in "Setup in each code repo", the devcontainer snippet, the host sibling
  clone, "pushes happen from the host", and "Hosts are Linux or macOS"; in
  "Git ownership", the reliance on bind mounts presenting files as the
  container user (a volume keeps real UIDs; see "Where the shared clones
  live"); in "Collisions", "one host clone" (now one volume per machine); in
  "Push access" and "`bin/check.py`", that hooks and pre-push run on the host
  (they now run in the container; `bin/check.py` stays standard-library
  Python).
- [2026-10-10-org-developer-docs-design.md](2026-10-10-org-developer-docs-design.md):
  that `dev` is the home of the change-request tracker (the tracker data
  moves to `ourPLCC/change-requests`; `dev` keeps the guides, the agent rules,
  and the tracker's tooling); and "Relative paths work on the host and in the
  container, since the repos are siblings in both" (they are siblings in the
  container only).
- [2026-10-11-languages-ng-migration-design.md](2026-10-11-languages-ng-migration-design.md):
  the `initializeCommand` and the `../dev` bind mount in "Switch-over in
  languages-ng".
- [2026-10-11-plcc-ng-demo-migration-design.md](2026-10-11-plcc-ng-demo-migration-design.md):
  the devcontainer in "Switch-over in plcc-ng-demo" (the `../dev` clone and
  mount), and rebuilding "from it on the host".

## Threat model

An agent in a container reads untrusted text: public issues and PR comments,
fetched web pages, dependency output. A prompt injection in that text can make
it do anything its tools and credential allow. This spec therefore treats the
agent as able to misuse every permission the container holds, and puts each
limit that matters on GitHub's side or in the release path, not in the
agent's instructions. Where a limit rests only on instructions and Claude Code
permission rules, the spec says so.

## Decision summary

- Humans and agents in a container act as the human, through **one
  fine-grained personal access token per contributor**, scoped to the
  `ourPLCC` owner with Contents and Pull requests read/write and nothing else,
  loaded only with `gh auth login --with-token`.
- **The tracker data moves out of `dev`** into a new repo,
  `ourPLCC/change-requests`, which holds only `backlog/`. It is the one repo
  whose `main` takes direct pushes, so it holds nothing that runs or instructs:
  no hooks, scripts, or agent rules. `dev` keeps those, and like every other
  repo takes changes to `main` only through pull requests. The split's
  mechanics have their own spec; see "Rollout".
- **GitHub enforces** the limits: per-repo rulesets forbid direct pushes to
  every `main` except `change-requests`', and to `gh-pages`, and forbid tag
  pushes; the token's scope forbids repos outside ourPLCC, workflow files,
  settings, and running workflows by hand.
- **Code a pushed branch runs in CI cannot release.** Workflows get read-only
  tokens by default; release credentials live in environments that only `main`
  and release tags can use; publishing to PyPI waits for the human's approval.
- **Agents never merge PRs.** GitHub cannot tell an agent from its human, so
  this rests on ORG-AGENTS.md and Claude Code deny rules; the PyPI approval
  gate means a merge an agent makes anyway publishes nothing.
- **`gh`** is git's only credential helper for github.com, and git never falls
  back to VS Code's sign-in. Locally, `gh`'s login lives in a shared named
  volume `ourplcc-gh`; in a Codespace, it uses the Codespace's own token.
- `dev` and `change-requests` are cloned into shared named volumes from inside
  the container. Nothing runs on the host, so Windows hosts and Codespaces
  work.
- The rule "commit in the container, push from the host" becomes "push from
  the container, through `dev`'s `bin/push.bash`".

## What a container may do

The same in a local container and in a Codespace, except where "Codespaces"
below narrows or widens it.

| Operation | Human | Agent | Enforced by |
| --- | --- | --- | --- |
| Push, force-push, or delete a branch other than `main` and `gh-pages`, in any ourPLCC repo | yes | yes | — |
| Push to `change-requests`' `main` | yes | yes | — |
| Force-push or delete `change-requests`' `main` | no | no | branch ruleset |
| Push to any other repo's `main` (`dev` included), or to `gh-pages` | no | no | branch rulesets |
| Push, move, or delete a tag | no | no | tag rulesets |
| Create, edit, or delete a draft release | yes | yes | — (publishing one creates its tag, which the tag rulesets block) |
| Open, update, comment on, or close a PR | yes | yes | — |
| Merge a PR | yes | **no** | ORG-AGENTS.md and Claude Code deny rules only |
| Publish a package | no | no | `pypi` environment's required reviewer |
| Run code in CI by pushing a branch or opening a PR | yes | yes | — (CI tokens are read-only; see "Workflows") |
| Push a change to `.github/workflows/` | no (yes in a Codespace) | no (yes in a Codespace) | token lacks Workflows; see "Codespaces" |
| Dispatch or re-run workflows; change settings, rulesets, environments, or secrets | no | no | token lacks Actions, Administration, Environments, Secrets |
| Anything in a repo outside ourPLCC | no | no | token's resource owner |
| Log `gh` in with another credential | no | no | ORG-AGENTS.md and Claude Code deny rules only |

Merging is the human's because, in a code repo, merging to `main` is the
release: semantic-release picks the version from the commit types. Even if an
agent merges, nothing reaches PyPI until the human approves the `pypi`
deployment in GitHub's web UI, which the token cannot do. In `dev`, an
agent's merge would change every agent's instructions; that, too, rests on
the rule.

Work the container cannot do — editing workflows, changing settings,
rulesets, environments, or secrets, approving deployments — is done in
GitHub's web UI or on the host, with the human's full credentials.

The existing limits on autonomy in ORG-AGENTS.md stand: CRs and drafts only
with the human's approval, and discovered work goes in the CR's notes. Its
"Limits on autonomy" section gains:

- Never merge a pull request.
- Never run `gh auth login`, `gh auth refresh`, or `gh auth token`; if `gh`
  is not logged in, stop and tell the human.
- Push `change-requests` only through `dev`'s `bin/push.bash`, and only to
  publish tracker changes the human approved.

Each repo's checked-in `.claude/settings.json` denies the same commands, as a
backstop rather than a boundary (an agent can reach the same API through other
commands):

```json
"deny": [
  "Bash(gh pr merge:*)",
  "Bash(gh auth login:*)",
  "Bash(gh auth refresh:*)",
  "Bash(gh auth token:*)",
  "Read(~/.config/gh/**)"
]
```

CR text in `change-requests` is data an agent reads, like issue text, and
anyone with the token can write it. It carries no more authority than an
issue: agent rules live in `dev`, behind review.

## GitHub-side settings

Set by an org owner, before any container gets push access.

### Tokens

- Fine-grained personal access tokens are allowed, **require approval**, and
  an org owner approves each one. Maximum lifetime: 90 days.
- Classic personal access tokens are blocked for the org, so a classic token
  pasted into `gh` cannot reach ourPLCC.
- OAuth app access is left as it is. Restricting it would also cut off the
  host's own Git Credential Manager, which the host needs for the work the
  container cannot do. The cost: a `gh auth login` taken through the browser
  default yields an unscoped token. The `--with-token`-only instruction, the
  deny rules, and Verification step 9 stand in for that restriction.

### Workflows

- The org's default `GITHUB_TOKEN` permission is **read-only** (set
  2026-10-13), and GitHub Actions may not create or approve pull requests.
  Every workflow in every ourPLCC repo declares an explicit, minimal
  `permissions:` block (for example `contents: read` for CI). On 2026-10-13,
  at least languages-ng's `test-languages.yaml`, plcc-ng's `ci.yml` and
  `docs-tests.yml`, and dev's `check.yml` lack one.
- Jobs that use a release GitHub App's secrets run in an environment
  `release`, whose deployment policy allows `main` and `v*` tags only; the
  secrets move from repository secrets into it. Code on any other branch
  cannot obtain the App's token, even through a dispatched run.
- The `pypi` environment allows `main` and `v*` tags only and has the human
  as required reviewer. It allows `main` because a release's publish job runs
  in the workflow a push to `main` starts, and GitHub checks an environment's
  policy against the run's ref, not the tag the job checks out. The required
  reviewer, not the ref policy, is what stops an unapproved publish.
- Every workflow that pushes `main`, `gh-pages`, or a tag does so with a
  release App's token, in the `release` environment, never with
  `GITHUB_TOKEN`, so the rulesets can name the App as their only bypass.

### Rulesets

Per repo: org rulesets need GitHub Team, which ourPLCC does not have.
"Apply the rulesets" is therefore a step in creating any ourPLCC repo. The
release Apps are the only bypass actors; nobody else bypasses, org owners
included, with one exception: course-materials-ng's `main` also lets its
maintainer Alain Kägi (`alainkaegi`) bypass, because he maintains it by
pushing to `main` directly. Its `main` still needs the ruleset for everyone
else: `deploy.yml` runs on every push to `main` with the release App's token,
which reaches every repo in the App's installation. The remaining risk is
that one contributor's token.

- **`main`**, every repo except `change-requests` (`dev` included): require a
  pull request, block force-pushes, block deletion.
- **`change-requests`' `main`**: block force-pushes and deletion; direct
  pushes allowed.
- **`gh-pages`**, every repo that has one: block all pushes, force-pushes, and
  deletion.
- **Tags**, every repo, all tags: block creation, update, and deletion.

### Repos that release differently

From their workflows on 2026-10-13:

- **plcc-ng** releases and deploys docs with its release App, except that
  `docs.yml` pushes `gh-pages` with `GITHUB_TOKEN`: it moves to the App.
- **languages-ng**'s semantic-release creates tags and releases with
  `GITHUB_TOKEN`: it moves to a release App.
- **course-materials-ng** pushes `gh-pages` (mike) with `GITHUB_TOKEN` from
  `deploy.yml` and `release.yml`: both move to a release App.
- **plcc-ng-devcontainer** releases with its own App (`APP_ID`). It either
  joins the bypass lists or adopts the shared release App, decided in that
  repo's CR. Its CI also pushes `:pr-N` images to ghcr from PR branches;
  nothing consumes them, so that stays.

## The token

Each contributor creates their own fine-grained personal access token:

- **Resource owner:** `ourPLCC`. **Repository access:** all repositories.
- **Repository permissions:** Contents read/write, Pull requests read/write;
  Metadata read is implied. No other permission.
- **Expiry:** 90 days at most. When it expires, the contributor makes a new
  one, has it approved, and loads it again.

The token is the contributor's identity: commits pushed and PRs opened with it
are theirs, whether a human or an agent ran the command.

The token sits in plain text in the `ourplcc-gh` volume: no keyring exists in
the container. Any process in any ourPLCC container can read it — `pdm`, `npm`,
the Haskell installer, an agent — and so can any other container on the
machine that mounts the volume by name. The 90-day lifetime, the narrow scope,
and the deny rules bound that exposure; it is accepted, not prevented.

**Commit signing.** Locally, commits are signed by the human's GPG key through
the gpg-agent VS Code forwards, as today. Any process in the container can ask
that agent to sign, so a signature shows the commit came from the human's
container, not that the human wrote it. In a Codespace there is no forwarded
gpg-agent; commits are signed by GitHub when the contributor enables
Codespaces GPG verification for ourPLCC repos, and are unsigned otherwise.

## How the credential reaches the container

### Every devcontainer

- Installs `gh` with the `ghcr.io/devcontainers/features/github-cli` feature.
- Makes `gh` git's only credential helper for github.com, by extending the
  `GIT_CONFIG_*` entries in `containerEnv` that already set `safe.directory`:

  ```jsonc
  "GIT_CONFIG_KEY_3":   "credential.https://github.com.helper",
  "GIT_CONFIG_VALUE_3": "",
  "GIT_CONFIG_KEY_4":   "credential.https://github.com.helper",
  "GIT_CONFIG_VALUE_4": "!gh auth git-credential"
  ```

  (numbered after the three `safe.directory` entries in "Where the shared
  clones live", with `GIT_CONFIG_COUNT` raised to match). Environment config
  is read after system, global, and repo config, and an empty value clears the
  helper list built so far. So it removes the helpers in the `~/.gitconfig`
  VS Code copies from the host (Git Credential Manager, osxkeychain) and the
  one VS Code installs to forward the host's credentials, both of which would
  carry the host's unscoped credentials into the container. It needs no setup
  step and is in force after every rebuild. `gh auth setup-git` is not used,
  because it writes the `~/.gitconfig` that VS Code overwrites from the host.
- Stops git falling back to VS Code's GitHub sign-in when `gh` has no token:
  `"GIT_TERMINAL_PROMPT": "0"` in `containerEnv`, and
  `"git.terminalAuthentication": false` and `"github.gitAuthentication": false`
  in `customizations.vscode.settings`. A push with no token fails instead of
  borrowing an unscoped one.
- Hides the host's SSH agent, which SSH remotes would push through with the
  host's keys, unscoped. VS Code forwards the agent into every container as
  `/tmp/vscode-ssh-auth-<uuid>.sock`, recreates the socket on every window
  reload, and has no setting that turns this off. So the devcontainer sets
  `"remoteEnv": {"SSH_AUTH_SOCK": ""}`, which stops `git` and `ssh` finding
  the agent by default, and
  `"postAttachCommand": "rm -f /tmp/vscode-ssh-auth-*.sock"`, which removes
  the socket after each attach. That leaves the socket reachable while
  `postStartCommand` runs, on every start (Dev Containers runs
  `postAttachCommand` only after it), in the moment between an attach and
  the removal, and to a process that survives a window reload. Hiding the
  agent is therefore not the boundary. The rule is: keep no SSH key that
  GitHub accepts loaded in the host's agent, and use HTTPS with Git
  Credential Manager on the host. That rests on the contributor, and
  `CONTRIBUTING.md` says so.
- Uses one `remoteUser`, `vscode`, with UID 1000, like every other ourPLCC
  devcontainer, because the shared volumes keep real UIDs.

`git push` then asks `gh auth git-credential` for github.com credentials, it
answers with the token, and git sends it over HTTPS. `gh pr create` uses the
same token.

### Locally

- A shared named volume `ourplcc-gh` is mounted at `/home/vscode/.config/gh`
  in every ourPLCC devcontainer. `postCreateCommand` chowns
  `/home/vscode/.config` and the volume to the container user (Docker creates
  a missing mount parent as root).
- The contributor creates the token, waits for its approval, then runs
  `gh auth login --with-token` once, in any ourPLCC container, and pastes it.
  Every ourPLCC container on the machine then shares that login. The
  browser flow `gh auth login` offers by default is not used: it yields a
  token for every repo the human can reach.
- The token is never in a repo or an image, survives rebuilds with the
  volume, and needs no host setup, so it works the same on Linux, macOS, and
  Windows hosts.
- Revoke by deleting the token on GitHub; forget it locally with
  `docker volume rm ourplcc-gh`.

### Codespaces

- `gh`, and git through it, use the `GITHUB_TOKEN` Codespaces provides. The
  `ourplcc-gh` volume starts empty and stays unused; nobody logs in.
- Each devcontainer declares `customizations.codespaces.repositories` granting
  `ourPLCC/change-requests` contents write and `ourPLCC/dev` contents write
  (for branches and PRs to `dev`); the Codespace's own repo is granted by
  default. GitHub asks for this grant when the Codespace is created. Choosing
  to continue without it leaves both read-only, so the docs say to authorize
  it. A change to the grant reaches only Codespaces created afterwards. The
  grant names a repo that must exist: before the split, GitHub lists
  `ourPLCC/change-requests` as not available, and does not follow its
  redirect to `dev`.
- The token is fixed in each process's environment when the process starts,
  and it expires about 12 hours after the Codespace starts; a restart issues
  a new one. Codespaces' own credential helper reads the same environment
  variable, so a stock Codespace behaves the same way, and deferring to it
  would gain nothing. So once a Codespace has run about 12 hours, pushes and
  `gh` may fail to authenticate until it restarts. Whether a new terminal
  gets a fresh token sooner is untested. A Codespace stops after its idle
  timeout, and a stop ends every process, so this takes a Codespace kept
  active that long.
- So in a Codespace the scope is that repo plus `dev` and `change-requests`,
  narrower than local. The table above holds within that scope, with one
  exception: the Codespace's token can push a change to `.github/workflows/`
  in its own repo, and no setting narrows it. The org's read-only
  `GITHUB_TOKEN` is only a default, which a workflow's own `permissions:`
  block can raise, so a workflow pushed on a branch can run with write access
  to that repo. That reaches its unprotected branches, issues, and PRs, which
  the token reaches anyway; its packages, which matters where people pull
  them, as with plcc-ng-devcontainer's images; and `actions: write`, which can
  start workflows on `main`, running reviewed code with the `release`
  environment's secrets. The rulesets, the `release` environment's refusal of
  other branches, and the `pypi` reviewer still hold. This is accepted, and
  limited by advice rather than enforcement: `CONTRIBUTING.md` says to run
  agents regularly in a local container, and to use one in a Codespace only
  for a one-off task, watched.

## Where the shared clones live

Every devcontainer replaces the host clone and bind mount with two volumes:

| Volume | Mounted at | Holds |
| --- | --- | --- |
| `ourplcc-dev` | `/workspaces/dev` | a clone of `ourPLCC/dev` |
| `ourplcc-change-requests` | `/workspaces/change-requests` | a clone of `ourPLCC/change-requests` |

- **No `initializeCommand`.** Nothing runs on the host.
- **`containerEnv`**: `BACKLOG_CWD=/workspaces/change-requests`, and
  `safe.directory` entries for `/workspaces/dev`,
  `/workspaces/change-requests`, and the repo's own workspace.
- **`bin/install/shared-clones.bash`**, a copy in each repo's `bin/install/`
  (it must exist before `dev` does), run from `postCreateCommand` and again
  from `postStartCommand`. Idempotent. Under `flock /workspaces/dev`, so two
  containers created at once do not clone into the same directory. The lock
  is the volume's mount point itself, not a file in it: a file there would
  dirty `dev`'s working tree and be moved aside as a leftover before the
  clone, and the mount point exists before anything is cloned. Every holder
  takes it as `flock -o -w 120 /workspaces/dev <command>`, never by opening a
  descriptor in its own shell: a child that outlives the holder, such as the
  `git maintenance` a fetch detaches into the background, would inherit that
  descriptor and keep the lock. `-o` keeps the descriptor in `flock` alone;
  `-w 120` turns a stuck holder into an error instead of a silent wait. For
  each of the two volumes:
  - chown it to the container user;
  - if it has no `.git`, or `git rev-parse HEAD` fails in it (an interrupted
    clone), clone the repo into it, moving any leftover aside first.

  Then:
  - set `change-requests`' `core.hooksPath` to `/workspaces/dev/.githooks`, so
    the hooks that check tracker commits come from reviewed code;
  - on start, fast-forward `dev`'s `main` when its working tree is clean and
    on `main`, so every container runs the reviewed tooling and rules. It
    never pulls `change-requests`; `bin/push.bash` does.

  If a clone fails (offline), the script says so and exits non-zero; the
  container still starts, and rerunning the script is the recovery.
- **Then the existing steps**: install the `backlog` version named in
  `/workspaces/dev/.backlog-version`, after checking that it is a plain
  `X.Y.Z` version (it is passed to `npm i -g`), the `git status` assertions,
  and the repo's own installs. `postStartCommand` warns when the installed
  `backlog --version` differs from `.backlog-version`.
- Every image has `python3`, since the hooks run in every container, and
  `flock` (util-linux), since every container takes the lock.

**Pushing tracker changes.** Every push of `change-requests` goes through
`dev`'s `bin/push.bash`. Under the same `flock /workspaces/dev` as the clone,
so it cannot run while another container pushes, it fetches, rebases onto
`origin/main`, runs `dev`'s `bin/check.py --pre-push --root` against
`change-requests`, and pushes. It finds `check.py` from its own location, and
an environment variable overrides the `change-requests` path, for tests. It
exits non-zero, saying why, and pushes nothing when:

- `change-requests` has uncommitted changes (it does not stash them);
- the rebase conflicts (it aborts the rebase, keeping the local commits);
- `check.py` fails, for example on a duplicate ID after the rebase (fix with
  `backlog doctor --fix`, then run it again);
- the push is rejected because another push landed after the fetch (run it
  again; it does not retry).

With nothing to push, it exits zero. Push after every tracker change: the
volume is not a backup.

**Sharing and collisions.** Locally, every ourPLCC container shares one
`change-requests` working tree, as with the bind mount, so one person's
sessions on one machine never allocate the same ID. Backlog.md's auto-commits
from two containers can still contend for `.git/index.lock`, as they could
with the bind mount. The lock does not cover them: Backlog.md does not take
it. A tracker edit from another container while `bin/push.bash` rebases can
land mid-rebase, and the rebase can then drop that commit. The window is a
second or two; wrapping `backlog` to take the lock is not worth it. Instead
the tracker guide says not to edit the tracker from another container while a
push runs. Two Codespaces, or a Codespace and a local container, are two trees, so
one person can collide with themselves there; `bin/check.py` and
`backlog doctor --fix` handle it as they handle collisions between people.

**What survives.** Locally, a container rebuild keeps the volumes and any
unpushed tracker commits; deleting a volume loses them. In a Codespace, a full
rebuild deletes volumes, so unpushed tracker commits are lost; there, push
immediately.

`/workspaces/<repo>` and `/workspaces/dev` are siblings in the container, so
`AGENTS.md`'s `@../dev/...` imports and `claude-imports.bash`'s approvals keep
working. On the host there is no `../dev`; agents run in containers.

Work on `dev` itself happens in `/workspaces/dev` from any ourPLCC container,
on a branch, through a pull request. Neither `dev` nor `change-requests` gets a
devcontainer of its own here.

## Windows hosts

The code repo is still bind-mounted from the host.

- **Line endings.** A Windows checkout with `core.autocrlf=true` gives the
  container CRLF in every file `.gitattributes` leaves at `text=auto`. That
  breaks byte-for-byte checks such as plcc-ng's docs fixtures, and scripts
  without a `.sh` or `.bash` extension. So every ourPLCC repo's
  `.gitattributes`, `dev`'s and `change-requests`' included, starts with:

  ```gitattributes
  * text=auto eol=lf
  ```

  and keeps CRLF only for Windows-only files (`*.bat`, `*.cmd`, `*.ps1`). An
  existing Windows checkout keeps its CRLF files until they are checked out
  again, so the migration re-checks it out.
- **Executable bit.** A Windows clone sets `core.filemode=false`, so a script
  created in the container is committed without its executable bit. Mark new
  scripts with `git update-index --chmod=+x`.
- **Speed.** Bind mounts from Windows are slow. VS Code's "Dev Containers:
  Clone Repository in Container Volume" works with this design, since no
  devcontainer setting depends on a host path, and avoids both problems above.
  Each repo's `CONTRIBUTING.md` recommends it on Windows and offers it on
  macOS; it is not required.

## Documentation changes

In `dev`, through a pull request:

- `dev-docs/tracker.md`:
  - "Setup": drop the host sibling clone; the container clones `dev` and
    `change-requests` into volumes. Replace "Commit inside the container;
    **push from the host**" with "Commit and push inside the container, with
    `bin/push.bash`, after every tracker change." Hosts: Linux, macOS,
    Windows, or a Codespace.
  - "Pushing and collisions": the same steps, run in the container, through
    `bin/push.bash`; Codespaces can collide with each other.
  - "Upgrading Backlog.md": rebuild every ourPLCC container after the bump.
  - "Working on the tracker tooling": changes go through a pull request; the
    checks run in the container.
- `ORG-AGENTS.md`: the three rules under "What a container may do".
- `CONTRIBUTING.md`: a section on working in a devcontainer — creating the
  token and getting it approved, `gh auth login --with-token`, what the
  container cannot do and where to do it instead, approving PyPI deployments,
  the Codespaces grant, and the migration below.
- `bin/check.py`'s docstring: no longer says checks run on hosts.

What moves between `dev` and `change-requests`, and the README that tells
`change-requests`' visitors that it holds committed work while GitHub Issues
hold conversations, belong to the split's spec.

In each code repo: `CONTRIBUTING.md`'s development-environment section
describes the volumes in place of the `../dev` clone, and drops plcc-ng's
`../change-requests` rename paragraph.

## Rollout

1. **GitHub-side settings**, by an org owner: tokens, workflow defaults, the
   `release` and `pypi` environments, and the rulesets of every repo except
   `dev` and `change-requests`, together with each repo's workflow changes in
   "Repos that release differently". Until these are in, no container gets
   push access. `dev`'s `main` ruleset must not be applied here: nobody
   bypasses it, so tracker pushes from the host to `dev` would stop before the
   split. The split's cutover applies `dev`'s and `change-requests`' rulesets.
2. **Split `ourPLCC/change-requests` out of `dev`**, under its own spec and CR
   in `dev`: create the repo, move `backlog/` with its history, rewrite CR
   references whose relative depth changes, point `dev`'s check CI and
   `bin/check.py` at the new repo, and keep `change-requests` free of code.
   Creating `ourPLCC/change-requests` ends GitHub's redirect from that old
   name to `dev`; the split's spec says which old links that breaks. The
   split is a coordinated cutover in one sitting, and steps 3 and 4 merge
   inside it.
3. **`dev`**: `bin/push.bash`, the documentation changes, `.gitattributes`.
   Prepared before the cutover, merged in it after the split.
4. **Every repo that mounts `../dev`** — plcc-ng, languages-ng, plcc-ng-demo,
   plcc-ng-devcontainer, and any repo that adopts the shared setup later — one
   CR each: the devcontainer changes in "How the credential reaches the
   container" and "Where the shared clones live",
   `bin/install/shared-clones.bash`, `.claude/settings.json`'s deny rules,
   `.gitattributes`, and its `CONTRIBUTING.md`. course-materials-ng's
   devcontainer does not use the shared setup, so it needs only step 1 until it
   adopts it. Each is prepared before the cutover and merged in it, after
   step 3. The "Open checks" are settled on the first repo's branch before the
   cutover; none of them needs `change-requests`. The "Verification" checklist
   needs `change-requests`, so it runs after the cutover, and each of these
   CRs closes once it passes rather than at merge.
5. **Contributors migrate.** For the contributor who runs the cutover, the
   cutover is the migration. Anyone else migrates after it.

## Migration, once per contributor

1. **Before the cutover's freeze**, in the host's `../dev`, confirm nothing is
   unpushed: `git status`, `git log --branches --not --remotes`,
   `git worktree list`, and `git stash list` all come back clean. Push or
   discard what they show. After the split, `dev`'s `main` rejects direct
   pushes, so a tracker commit still unpushed then must be re-entered by hand
   in `change-requests`.
2. Create the token and wait for its approval.
3. Rebuild one ourPLCC container. It clones `dev` and `change-requests` into
   their volumes. Run `gh auth login --with-token`, then check that
   `bin/push.bash` pushes.
4. On a Windows host, re-check out each code repo
   (`git rm -r --cached -q . && git reset --hard`) or clone it fresh.
5. Delete the host's `../dev`. Do not check out a pre-migration branch of any
   repo afterwards, or its devcontainer recreates it.

## Verification

The first repo to adopt the shared setup, plcc-ng, passes this checklist in a
local container on a Linux or macOS host, in a local container on a Windows
host, and in a newly created Codespace. The other repos' devcontainer changes
copy plcc-ng's, so each of their CRs instead passes a smoke test in a rebuilt
local container: push a branch and open a PR with `gh`, list CRs with
`backlog task list`, push a tracker change with `bin/push.bash`, and see a
direct push to `main` rejected.

Must succeed:

1. Push a new branch and open a PR with `gh pr create`.
2. Push a tracker change to `change-requests`' `main` with `bin/push.bash`.
3. After a rebuild (locally; in a Codespace, a plain rebuild, not a full
   one), steps 1 and 2 work with no new login, and unpushed tracker commits
   made before the rebuild are still there.

Must fail:

4. A direct push to the repo's `main`, to `dev`'s `main`, and to `gh-pages`
   if the repo has one.
5. A force-push to `change-requests`' `main`.
6. A push of a commit touching `.github/workflows/`, locally. In a Codespace
   it succeeds; see "Codespaces".
7. Pushing any tag; `gh release create` for a new tag.
8. `gh workflow run` on any workflow.

Must hold:

9. `gh auth status` shows a fine-grained token (`github_pat_`) locally, or
   the Codespace's token in a Codespace.
10. `git config --get-all credential.https://github.com.helper` lists only
    the empty reset and `gh`, and with `gh` logged out,
    `git push` fails at once without a prompt.
11. `ssh-add -l` cannot reach an agent.
12. A CI run on the PR from step 1 has a read-only `GITHUB_TOKEN` and no
    access to a release App's secrets.

## Open checks

All settled on plcc-ng's branch before the split, on a macOS host and in a
Codespace; the sections above already reflect each result.

- An empty `SSH_AUTH_SOCK` hides the forwarded agent but does not block it:
  the socket stays in `/tmp`, and pointing `ssh-add` at it reaches the host.
  Removing the socket in `postAttachCommand` closes that path except for the
  gaps "Every devcontainer" lists, so the boundary is the rule about the
  host's agent.
- The Codespace token can push a change to `.github/workflows/` and create a
  draft release; it cannot push a tag or push `gh-pages`, which the rulesets
  reject. Publishing a release was not tried; Verification step 7 covers it.
- A process in a Codespace keeps the token it started with, which expires
  about 12 hours after the Codespace starts. Codespaces' own helper reads the
  same variable, so the planned fallback to it is dropped.
- Codespaces honors `type=volume` mounts under `/workspaces`, and they
  survive a restart.
- `flock /workspaces/dev` in one local container blocks it in another
  container that mounts the same volume.

## Out of scope

- Agents merging PRs, and any automated check that would make that safe.
- A separate GitHub identity for agents.
- The mechanics of the `change-requests` split (its own spec).
- Other ways to make working across repos smoother, beyond the shared
  volumes.
- Devcontainers for `dev` and `change-requests`.

## Alternatives considered

| Alternative | Why not |
| --- | --- |
| SSH remotes with the host's forwarded SSH agent | An SSH key cannot be scoped to one org, so the container could push to every repo the human can |
| A separate credential or identity for agents | Two credential paths per contributor; GitHub-side rulesets and the release gates already bound what an agent with the human's token can do |
| Forward the host's git credentials (VS Code default) | Unscoped, host-OS-specific, and absent in Codespaces |
| Token in a host environment variable via `${localEnv:…}` | VS Code launched from a GUI often does not see the shell's environment, and the setup differs on every host OS |
| `gh auth setup-git` | Writes `~/.gitconfig`, which VS Code replaces with the host's copy |
| Token with the Workflows permission | A workflow on a pushed branch runs before review; workflow edits are rare enough to do outside the container |
| Restrict OAuth app access for the org | Also blocks the host's Git Credential Manager, which the host needs for what the container cannot do |
| Keep tracker data in `dev`, restricting direct pushes to `backlog/` with a push ruleset | Push rulesets are not available to ourPLCC |
| Keep tracker data in `dev`, open to direct pushes, guarded by `bin/push.bash` | A rule an injected agent can skip, on the path that sets every agent's instructions and every container's hooks |
| Tracker data on an orphan branch of `dev`, checked out as a worktree | Same protection as a separate repo, but orphan branches and worktrees are unfamiliar to new contributors, and GitHub shows `main` by default |
| Org rulesets | Need GitHub Team |
| Keep the shared clone as a host bind mount | Needs host-side shell (no Windows) and a host path (no Codespaces) |
| One container for all repos | Mixes every repo's dependencies and drops the boundary between repos |
