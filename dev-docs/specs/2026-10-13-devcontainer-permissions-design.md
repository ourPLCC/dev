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
tracker clone lives.

## Supersedes

- [2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md):
  in "Setup in each code repo", the devcontainer snippet, the host sibling
  clone, "pushes happen from the host", and "Hosts are Linux or macOS"; in
  "Git ownership", the reliance on bind mounts presenting files as the
  container user (a volume keeps real UIDs; see "Where `dev` lives"); in
  "Collisions", "one host clone" (now one volume per machine); in "Push
  access" and "`bin/check.py`", that hooks and pre-push run on the host (they
  now run in the container; `bin/check.py` stays standard-library Python);
  and "writers push directly to `main`", which now holds only for tracker
  data (see "`dev`'s `main`").
- [2026-10-10-org-developer-docs-design.md](2026-10-10-org-developer-docs-design.md):
  "Relative paths work on the host and in the container, since the repos are
  siblings in both." They are siblings in the container only.
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
- **GitHub enforces** the limits: rulesets forbid direct pushes to every code
  repo's `main` and to `gh-pages`, forbid tag pushes, and restrict direct
  pushes to `dev`'s `main` to tracker data; the token's scope forbids repos
  outside ourPLCC, workflow files, settings, and running workflows by hand.
- **Code a pushed branch runs in CI cannot release.** Workflows get read-only
  tokens by default; release credentials live in environments that only `main`
  and release tags can use; publishing to PyPI waits for the human's approval.
- **Agents never merge PRs.** GitHub cannot tell an agent from its human, so
  this rests on ORG-AGENTS.md and Claude Code deny rules; the PyPI approval
  gate means a merge an agent makes anyway publishes nothing.
- **`gh`** is git's only credential helper for github.com, and git never falls
  back to VS Code's sign-in. Locally, `gh`'s login lives in a shared named
  volume `ourplcc-gh`; in a Codespace, it uses the Codespace's own token.
- The tracker clone moves from a host folder to a shared named volume
  `ourplcc-dev`, cloned from inside the container by a script. Nothing runs on
  the host, so Windows hosts and Codespaces work.
- The rule "commit in the container, push from the host" becomes "push from
  the container, through `dev`'s `bin/push.bash`".

## What a container may do

The same in a local container and in a Codespace, except where "Codespaces"
below narrows it.

| Operation | Human | Agent | Enforced by |
| --- | --- | --- | --- |
| Push, force-push, or delete a branch other than `main` and `gh-pages`, in any ourPLCC repo | yes | yes | — |
| Push tracker data (`backlog/`, except `backlog/config.yml`) to `dev`'s `main` | yes | yes | — |
| Push anything else to `dev`'s `main` | no | no | `dev` push ruleset |
| Push to a code repo's `main` or to `gh-pages` | no | no | branch rulesets |
| Push, move, or delete a tag | no | no | tag ruleset |
| Open, update, comment on, or close a PR | yes | yes | — |
| Merge a PR | yes | **no** | ORG-AGENTS.md and Claude Code deny rules only |
| Publish a package | no | no | `pypi` environment's required reviewer |
| Run code in CI by pushing a branch or opening a PR | yes | yes | — (CI tokens are read-only; see "Workflows") |
| Push a change to `.github/workflows/` | no | no | token lacks Workflows |
| Dispatch or re-run workflows; change settings, rulesets, environments, or secrets | no | no | token lacks Actions, Administration, Environments, Secrets |
| Anything in a repo outside ourPLCC | no | no | token's resource owner |
| Log `gh` in with another credential | no | no | ORG-AGENTS.md and Claude Code deny rules only |

Merging is the human's because, in a code repo, merging to `main` is the
release: semantic-release picks the version from the commit types. Even if an
agent merges, nothing reaches PyPI until the human approves the `pypi`
deployment in GitHub's web UI, which the token cannot do.

Work the container cannot do — editing workflows, changing settings,
rulesets, environments, or secrets, approving deployments — is done in
GitHub's web UI or on the host, with the human's full credentials.

The existing limits on autonomy in ORG-AGENTS.md stand: CRs and drafts only
with the human's approval, and discovered work goes in the CR's notes. Its
"Limits on autonomy" section gains:

- Never merge a pull request.
- Never run `gh auth login`, `gh auth refresh`, or `gh auth token`; if `gh`
  is not logged in, stop and tell the human.
- Push `dev` only through `bin/push.bash`, and only to publish tracker changes
  the human approved.

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

## GitHub-side settings

Set once by an org owner, before any container gets push access.

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

- The org's default `GITHUB_TOKEN` permission is **read-only**, and every
  workflow in every ourPLCC repo declares an explicit, minimal `permissions:`
  block (for example `contents: read` for CI).
- Jobs that use the release GitHub App's secrets (`RELEASE_APP_ID`,
  `RELEASE_APP_PRIVATE_KEY`) run in an environment `release`. Its deployment
  policy allows `main` and `v*` tags only, and the secrets move from
  repository secrets into it. Code on any other branch cannot obtain the App's
  token, even through a dispatched run.
- The `pypi` environment allows `v*` tags only and has the human as required
  reviewer.
- The docs workflow pushes `gh-pages` with the release App's token, in the
  `release` environment, instead of `GITHUB_TOKEN`, so `gh-pages` can be
  protected with the App as its only bypass.

### Rulesets

The release App is the only bypass actor on every ruleset below except the
`dev` push ruleset; nobody else bypasses, org owners included.

- **Code repos' `main`** (every repo except `dev`): require a pull request,
  block force-pushes, block deletion.
- **`gh-pages`** (every repo that has one): block all pushes, force-pushes,
  and deletion.
- **Tags** (every repo, all tags): block creation, update, and deletion.
- **`dev`'s `main`**: a push ruleset rejecting direct pushes that change
  anything outside `backlog/`, or `backlog/config.yml`. Changes to those paths
  reach `main` through a pull request, so `dev`'s guides, `ORG-AGENTS.md`,
  hooks, `bin/`, and `.backlog-version` (which every container executes or
  loads) are reviewed like code. Repository admins bypass it for pull requests
  only, never for direct pushes.

Immutable releases are on for every repo that publishes releases, so a
published release's notes and assets cannot be changed.

Org-wide rulesets if the org's plan provides them; otherwise one per repo with
the same content, and "rulesets applied" is a step in creating a repo.

### Repos that release differently

Every repo the rulesets cover is checked for other actors that push to
`main`, `gh-pages`, or tags (a different App, `GITHUB_TOKEN`, a deploy key).
Each one is either added as a bypass actor, with the reason recorded in that
repo's CR, or changed to use the release App.

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
  "GIT_CONFIG_KEY_2":   "credential.https://github.com.helper",
  "GIT_CONFIG_VALUE_2": "",
  "GIT_CONFIG_KEY_3":   "credential.https://github.com.helper",
  "GIT_CONFIG_VALUE_3": "!gh auth git-credential"
  ```

  (with `GIT_CONFIG_COUNT` raised to match). Environment config is read after
  system, global, and repo config, and an empty value clears the helper list
  built so far. So it removes the helpers in the `~/.gitconfig` VS Code copies
  from the host (Git Credential Manager, osxkeychain) and the one VS Code
  installs to forward the host's credentials, both of which would carry the
  host's unscoped credentials into the container. It needs no setup step and
  is in force after every rebuild. `gh auth setup-git` is not used, because it
  writes the `~/.gitconfig` that VS Code overwrites from the host.
- Stops git falling back to VS Code's GitHub sign-in when `gh` has no token:
  `"GIT_TERMINAL_PROMPT": "0"` in `containerEnv`, and
  `"git.terminalAuthentication": false` and `"github.gitAuthentication": false`
  in `customizations.vscode.settings`. A push with no token fails instead of
  borrowing an unscoped one.
- Does not expose the host's SSH agent: SSH remotes would push with the host's
  keys, unscoped. The likely mechanism is `"remoteEnv": {"SSH_AUTH_SOCK": ""}`;
  see "Open checks".
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
  `ourPLCC/dev` contents write; the Codespace's own repo is granted by default.
  GitHub asks for this grant when the Codespace is created. Choosing to
  continue without it leaves `dev` read-only, so the docs say to authorize it.
  A change to the grant reaches only Codespaces created afterwards.
- So in a Codespace the scope is that repo plus `dev`, narrower than local.
  The table above still holds within that scope.

## Where `dev` lives

Every devcontainer replaces the host clone and bind mount with a volume:

- **No `initializeCommand`.** Nothing runs on the host.
- **Mount** `source=ourplcc-dev,target=/workspaces/dev,type=volume`.
- **`bin/install/dev-clone.bash`**, a copy in each repo's `bin/install/` (it
  must exist before `dev` does), run from `postCreateCommand` and again from
  `postStartCommand`. Idempotent. Under `flock` on a lock file in the volume,
  so two containers created at once do not clone into the same directory:
  - chown `/workspaces/dev` to the container user;
  - if `/workspaces/dev` has no `.git`, or `git -C /workspaces/dev rev-parse
    HEAD` fails (an interrupted clone), clone `https://github.com/ourPLCC/dev`
    into it, moving any leftover aside first;
  - set its `core.hooksPath` to `.githooks`.

  If the clone fails (offline), the script says so and exits non-zero; the
  container still starts, and rerunning the script is the recovery.
- **Then the existing steps**: install the `backlog` version named in
  `/workspaces/dev/.backlog-version`, after checking that it is a plain
  `X.Y.Z` version (it is passed to `npm i -g`), the `git status` assertions,
  and the repo's own installs. `postStartCommand` warns when the installed
  `backlog --version` differs from `.backlog-version`.
- `BACKLOG_CWD` and the `safe.directory` entries are unchanged.
- Every image has `python3`, since the `.githooks` hooks run in
  every container that shares the volume.

**Pushing `dev`.** Every push of `dev` goes through a new `bin/push.bash` in
`dev`. Under the same `flock` as the clone, so it cannot run while another
container pushes, it fetches, rebases onto `origin/main`, runs
`bin/check.py --pre-push`, and pushes. Push after every tracker change: the
volume is not a backup.

**Sharing and collisions.** Locally, every ourPLCC container shares one `dev`
working tree, as with the bind mount, so one person's sessions on one machine
never allocate the same ID. Backlog.md's auto-commits from two containers can
still contend for `.git/index.lock`, as they could with the bind mount; the
lock makes a pull-and-rebase no more dangerous than that. Two Codespaces, or a
Codespace and a local container, are two `dev` trees, so one person can
collide with themselves there; `bin/check.py` and `backlog doctor --fix`
handle it as they handle collisions between people.

**What survives.** Locally, a container rebuild keeps the volume and any
unpushed tracker commits; deleting the volume loses them. In a Codespace, a
full rebuild deletes volumes, so unpushed tracker commits are lost; there,
push immediately.

`/workspaces/<repo>` and `/workspaces/dev` are siblings in the container, so
`AGENTS.md`'s `@../dev/...` imports and `claude-imports.bash`'s approvals keep
working. On the host there is no `../dev`; agents run in containers. The
shared container path also gives `dev`'s `.worktrees/` one consistent absolute
path, where the bind mount mixed host and container paths.

Work on `dev` itself happens in `/workspaces/dev` from any ourPLCC container,
on a branch, through a pull request. `dev` gets no devcontainer of its own
here.

## Windows hosts

The code repo is still bind-mounted from the host.

- **Line endings.** A Windows checkout with `core.autocrlf=true` gives the
  container CRLF in every file `.gitattributes` leaves at `text=auto`. That
  breaks byte-for-byte checks such as plcc-ng's docs fixtures, and scripts
  without a `.sh` or `.bash` extension. So every ourPLCC repo's
  `.gitattributes`, `dev`'s included, starts with:

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

In `dev` (through a pull request, per "`dev`'s `main`"):

- `dev-docs/tracker.md`:
  - "Setup": drop the host sibling clone; the container clones `dev` into the
    `ourplcc-dev` volume. Replace "Commit inside the container; **push from
    the host**" with "Commit and push inside the container, with
    `bin/push.bash`, after every tracker change." Hosts: Linux, macOS,
    Windows, or a Codespace.
  - "Pushing and collisions": the same steps, run in the container, through
    `bin/push.bash`; Codespaces can collide with each other.
  - "Upgrading Backlog.md": rebuild every ourPLCC container after the bump.
  - "Working on the tracker tooling": changes outside `backlog/` go through a
    pull request; the checks run in the container.
- `ORG-AGENTS.md`: the three rules under "What a container may do".
- `CONTRIBUTING.md`: a section on working in a devcontainer — creating the
  token and getting it approved, `gh auth login --with-token`, what the
  container cannot do and where to do it instead, approving PyPI deployments,
  the Codespaces grant, and the migration below.
- `bin/check.py`'s docstring: no longer says checks run on hosts.

In each code repo: `CONTRIBUTING.md`'s development-environment section
describes the volume in place of the `../dev` clone, and drops plcc-ng's
`../change-requests` rename paragraph.

## Rollout

1. **GitHub-side settings**, by an org owner, and the workflow and
   environment changes in each repo that releases or deploys docs. Until
   these are in, no container gets push access.
2. **`dev`**: `bin/push.bash`, the documentation changes, `.gitattributes`.
3. **Every repo that mounts `../dev`** — plcc-ng, languages-ng, plcc-ng-demo,
   plcc-ng-devcontainer, course-materials-ng, and any repo added later — one CR
   each: the devcontainer changes in "How the credential reaches the
   container" and "Where `dev` lives", `bin/install/dev-clone.bash`,
   `.claude/settings.json`'s deny rules, `.gitattributes`, and its
   `CONTRIBUTING.md`.
4. **Contributors migrate** only once every CR in step 3 has merged. Until
   then an unmigrated devcontainer, or an old branch of a migrated one,
   recreates `../dev` on the host, and one person has two `dev` trees.

## Migration, once per contributor

1. In the host's `../dev`, confirm nothing is unpushed: `git status`,
   `git log --branches --not --remotes`, `git worktree list`, and
   `git stash list` all come back clean. Push or discard what they show.
2. Create the token and wait for its approval.
3. Rebuild one ourPLCC container. It clones `dev` into the volume. Run
   `gh auth login --with-token`, then check that `bin/push.bash` pushes.
4. On a Windows host, re-check out each code repo
   (`git rm -r --cached -q . && git reset --hard`) or clone it fresh.
5. Delete the host's `../dev`. Do not check out a pre-migration branch of any
   repo afterwards, or its devcontainer recreates it.

## Verification

Each code repo's CR passes this checklist in a local container on a Linux or
macOS host, in a local container on a Windows host, and in a newly created
Codespace.

Must succeed:

1. Push a new branch and open a PR with `gh pr create`.
2. Push a tracker change to `dev`'s `main` with `bin/push.bash`.
3. After a rebuild (locally; in a Codespace, a plain rebuild, not a full
   one), steps 1 and 2 work with no new login, and unpushed `dev` commits
   made before the rebuild are still there.

Must fail:

4. A direct push to the repo's `main`, and to `gh-pages` if it has one.
5. A direct push to `dev`'s `main` changing a file outside `backlog/`, or
   `backlog/config.yml`.
6. A push of a commit touching `.github/workflows/`.
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
    access to the release App's secrets.

## Open checks

Settled during step 1 or the first repo's CR. A result that contradicts this
spec is fixed here, before the spec is frozen.

- **`dev` push ruleset.** The org's plan offers push rulesets with file-path
  restrictions on `dev`, expressing "anything outside `backlog/`, or
  `backlog/config.yml`", with an admin bypass limited to pull requests. If it
  cannot, fall back to splitting the tracker data into its own repo holding
  only `backlog/`: `dev` becomes pull-request-only like the code repos, and
  containers push only to the data repo. That fallback needs its own revision
  of this spec.
- Org-wide rulesets are available on the org's plan.
- `remoteEnv` with an empty `SSH_AUTH_SOCK` stops git and `ssh` from reaching
  the forwarded agent; if not, another way to stop VS Code forwarding it.
- The Codespace token cannot push workflow changes, create releases, or push
  `gh-pages`. If it can, the table records the difference for Codespaces.
- A long-running process in a Codespace keeps working after the Codespace's
  `GITHUB_TOKEN` is refreshed. If not, the helper becomes a small script that
  defers to Codespaces' own helper when `$CODESPACES` is set.
- Codespaces honors `type=volume` mounts under `/workspaces`.
- Immutable releases are available for the org's repos.

## Out of scope

- Agents merging PRs, and any automated check that would make that safe.
- A separate GitHub identity for agents.
- Other ways to make working across repos smoother, beyond the shared
  volumes.
- A devcontainer for `dev`.

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
| `dev`'s `main` open to direct pushes, guarded by `bin/push.bash` refusing non-tracker paths | A rule an injected agent can skip, on the path that sets every agent's instructions and every container's hooks |
| Keep `dev` as a host bind mount | Needs host-side shell (no Windows) and a host path (no Codespaces) |
| One container for all repos | Mixes every repo's dependencies and drops the boundary between repos |
