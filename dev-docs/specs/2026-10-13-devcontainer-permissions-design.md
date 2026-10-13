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
container, and where the tracker clone lives.

## Supersedes

- [2026-10-08-199-central-tracker-design.md](../../../plcc-ng/dev-docs/specs/2026-10-08-199-central-tracker-design.md):
  in "Setup in each code repo", the devcontainer snippet, the host sibling
  clone, "pushes happen from the host", and "Hosts are Linux or macOS"; in
  "Collisions", "one host clone" (now one volume per machine); in "Push
  access" and "`bin/check.py`", that hooks and pre-push run on the host (they
  now run in the container; `bin/check.py` stays standard-library Python).
- [2026-10-10-org-developer-docs-design.md](2026-10-10-org-developer-docs-design.md):
  "Relative paths work on the host and in the container, since the repos are
  siblings in both." They are siblings in the container only.
- [2026-10-11-languages-ng-migration-design.md](2026-10-11-languages-ng-migration-design.md):
  the `initializeCommand` and the `../dev` bind mount in "Switch-over in
  languages-ng". The same holds for plcc-ng-demo, which is set up as plcc-ng's.

## Decision summary

- Humans and agents in a container act as the human, through **one
  fine-grained personal access token per contributor**, scoped to the
  `ourPLCC` owner with Contents and Pull requests read/write and nothing else.
- GitHub enforces every limit but one: **rulesets** forbid direct pushes to
  every repo's `main` except `dev`'s, and forbid `v*` tags; the token's scope
  forbids repos outside ourPLCC, workflow files, settings, and triggering
  workflows. The one rule GitHub cannot enforce, because the agent is the
  human to GitHub, is that **agents never merge PRs**; ORG-AGENTS.md states it.
- **`gh`** is git's only credential helper for github.com. Locally, its login
  lives in a shared named volume `ourplcc-gh`; in a Codespace, it uses the
  Codespace's own token.
- The tracker clone moves from a host folder to a shared named volume
  `ourplcc-dev`, cloned from inside the container. Nothing runs on the host,
  so Windows hosts and Codespaces work.
- The rule "commit in the container, push from the host" becomes "push from
  the container".

## What a container may do

The same in a local container and in a Codespace, except where "Codespaces"
below narrows it.

| Operation | Human | Agent | Enforced by |
|---|---|---|---|
| Push, force-push, or delete a non-default branch of any ourPLCC repo | yes | yes | — |
| Push to `ourPLCC/dev`'s `main` | yes | yes | — |
| Push to any other repo's `main` | no | no | default-branch ruleset |
| Open, update, comment on, or close a PR | yes | yes | — |
| Merge a PR | yes | **no** | ORG-AGENTS.md (rule only) |
| Push a change to `.github/workflows/` | no | no | token lacks Workflows |
| Create, move, or delete a `v*` tag | no | no | tag ruleset |
| Change repo or org settings, rulesets, or secrets; run workflows | no | no | token lacks Administration, Secrets, Actions |
| Anything in a repo outside ourPLCC | no | no | token's resource owner |

Merging is the human's because, in a code repo, merging to `main` is the
release: semantic-release picks the version from the commit types, and the
package is published. An agent never merges, even when it could.

Work the container cannot do — editing workflows, changing settings,
rulesets, or secrets — is done on the host or in GitHub's web UI, with the
human's full credentials.

The existing limits on autonomy in ORG-AGENTS.md stand: CRs and drafts only
with the human's approval, and discovered work goes in the CR's notes. Its
"Limits on autonomy" section gains:

- Never merge a pull request.
- Push `dev`'s `main` only to publish tracker changes the human approved.

## GitHub-side guardrails

Set once by an org owner:

- **Fine-grained tokens** are allowed for the `ourPLCC` org.
- **Default-branch ruleset** on every repo except `dev`: require a pull
  request, block force-pushes, block deletion.
- **Tag ruleset** on every repo, for `refs/tags/v*`: block creation, update,
  and deletion.
- **Bypass list** on both rulesets: the release GitHub App only (the App whose
  token semantic-release uses to push the release commit and tag), and
  nobody else, including org owners.

Org-wide rulesets if the org's plan provides them, otherwise one per repo with
the same content. A new repo gets them when it is created.

## The token

Each contributor creates their own fine-grained personal access token:

- **Resource owner:** `ourPLCC`. **Repository access:** all repositories.
- **Repository permissions:** Contents read/write, Pull requests read/write;
  Metadata read is implied. No other permission.
- **Expiry:** whatever the org's token policy allows. When it expires, the
  contributor makes a new one and logs in again.

The token is the contributor's identity: commits pushed and PRs opened with it
are theirs, whether a human or an agent ran the command. Commits stay signed by
the contributor's GPG key through the gpg-agent VS Code forwards, as today.

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

  (with `GIT_CONFIG_COUNT` raised to match). The empty value clears helpers
  configured earlier: one in the `~/.gitconfig` VS Code copies from the host
  (Git Credential Manager, osxkeychain), and the one VS Code installs to
  forward the host's credentials. Those would carry the host's unscoped
  credentials into the container. Environment config needs no setup step and
  is in force after every rebuild. `gh auth setup-git` is not used, because it
  writes the `~/.gitconfig` that VS Code overwrites from the host.
- Does not expose the host's SSH agent: SSH remotes would push with the host's
  keys, unscoped. The likely mechanism is `"remoteEnv": {"SSH_AUTH_SOCK": ""}`;
  see "Open checks".
- Keeps the forwarded gpg-agent, which signs commits and grants no push
  access.

`git push` then asks `gh auth git-credential` for github.com credentials, it
answers with the token, and git sends it over HTTPS. `gh pr create` uses the
same token.

### Locally

- A shared named volume `ourplcc-gh` is mounted at `/home/vscode/.config/gh`
  in every ourPLCC devcontainer; `postCreateCommand` chowns it to the
  container user.
- The contributor runs `gh auth login` once, in any ourPLCC container, and
  pastes the token. With no keyring in the container, `gh` keeps it in
  `hosts.yml` in that volume, which every ourPLCC container on the machine
  then shares.
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
- So in a Codespace the scope is that repo plus `dev`, narrower than local.
  The table above still holds within that scope.

## Where `dev` lives

Every devcontainer replaces the host clone and bind mount with a volume:

- **No `initializeCommand`.** Nothing runs on the host.
- **Mount** `source=ourplcc-dev,target=/workspaces/dev,type=volume`.
- **`postCreateCommand`**, in order: chown `/workspaces/dev` and
  `/home/vscode/.config/gh`; clone `https://github.com/ourPLCC/dev` into
  `/workspaces/dev` if `/workspaces/dev/.git` is missing; set its
  `core.hooksPath` to `.githooks`; then the existing steps (the pinned
  `backlog` from `/workspaces/dev/.backlog-version`, the `git status`
  assertions, the repo's own installs). The clone comes first because the
  steps after it read it.
- `BACKLOG_CWD` and the `safe.directory` entries are unchanged.
- The container has `python3`, since the `.githooks` hooks now run there,
  pre-push included.

Locally, every ourPLCC container shares one `dev` working tree, as with the
bind mount, so one person's sessions still never allocate the same ID. In a
Codespace, the volume is the Codespace's own. A rebuild keeps the volume and
any unpushed tracker commits; deleting the volume loses them. Hence the
tracker rule: push `dev`'s `main` after tracker changes, from the container.

`/workspaces/<repo>` and `/workspaces/dev` are siblings in the container, so
`AGENTS.md`'s `@../dev/...` imports keep resolving there. They no longer
resolve on the host, which has no `../dev`; agents run in containers.

Work on `dev` itself happens in `/workspaces/dev` from any ourPLCC container.
`dev` gets no devcontainer of its own here.

## Windows hosts

The code repo is still bind-mounted from the host, so a Windows checkout with
`core.autocrlf=true` would give the container CRLF in every file
`.gitattributes` leaves at `text=auto`. That breaks byte-for-byte checks such
as plcc-ng's docs fixtures, and scripts without a `.sh` or `.bash` extension.
So every ourPLCC repo's `.gitattributes`, `dev`'s included, starts with:

```gitattributes
* text=auto eol=lf
```

and keeps CRLF only for Windows-only files (`*.bat`, `*.cmd`, `*.ps1`).

VS Code's "Dev Containers: Clone Repository in Container Volume" works with
this design, since no devcontainer setting depends on a host path. A repo's
`CONTRIBUTING.md` mentions it as an option, mainly for Windows and macOS hosts
where it is faster; it is not required.

## Documentation changes

In `dev`:

- `dev-docs/tracker.md`, "Setup": drop the host sibling clone; the container
  clones `dev` into the `ourplcc-dev` volume. Replace "Commit inside the
  container; **push from the host**" with "Commit and push inside the
  container; push `main` after your tracker changes." Hosts: Linux, macOS, or
  Windows, or a Codespace.
- `dev-docs/tracker.md`, "Pushing and collisions": the same steps, run in the
  container.
- `ORG-AGENTS.md`: the two rules under "What a container may do".
- `CONTRIBUTING.md`: a short section on working in a devcontainer — creating
  the token, `gh auth login` once, what the container cannot do and where to
  do it instead, and the one-time migration below.

In each code repo, `CONTRIBUTING.md`'s development-environment section
describes the volume in place of the `../dev` clone.

## Migration, once per contributor

1. On the host, push any unpushed commits in `../dev`.
2. Rebuild a container whose devcontainer has this spec applied; it clones
   `dev` into the volume. Create the token and run `gh auth login`.
3. Delete the host's `../dev` folder once no container uses the old
   devcontainer.

## Rollout

- `dev`: the documentation changes, and `.gitattributes`.
- The guardrails, set by an org owner before any container gets push access.
- One CR per code repo (plcc-ng, languages-ng, plcc-ng-demo, and any later
  repo): the devcontainer changes in "How the credential reaches the
  container" and "Where `dev` lives", `.gitattributes`, and its
  `CONTRIBUTING.md`.

## Verification

Each code repo's CR passes this checklist in a local container on a Linux or
macOS host, in a local container on a Windows host, and in a Codespace:

1. Push a new branch and open a PR with `gh pr create`.
2. A direct push to `main` is rejected.
3. A push of a commit touching `.github/workflows/` is rejected.
4. Pushing a `v*` tag is rejected.
5. Push a tracker change to `dev`'s `main`.
6. `ssh-add -l` cannot reach an agent.
7. `git config --get-all credential.https://github.com.helper` shows only
   the empty reset and `gh`.
8. After a rebuild, steps 1 and 5 work with no new login, and unpushed `dev`
   commits made before the rebuild are still there.

## Open checks

Settled during the first repo's CR. A result that contradicts this spec is
fixed here, before the spec is frozen.

- `remoteEnv` with an empty `SSH_AUTH_SOCK` stops git and `ssh` from reaching
  the forwarded agent; if not, another way to stop VS Code forwarding it.
- The Codespace token cannot push workflow changes. If it can, the table
  records the difference for Codespaces.
- Codespaces honors `type=volume` mounts under `/workspaces`.
- Whether the org's plan provides org-wide rulesets.

## Out of scope

- Agents merging PRs, and any automated check that would make that safe.
- A separate GitHub identity for agents.
- Other ways to make working across repos smoother, beyond the shared
  volumes.
- A devcontainer for `dev`.

## Alternatives considered

| Alternative | Why not |
|---|---|
| SSH remotes with the host's forwarded SSH agent | An SSH key cannot be scoped to one org, so the container could push to every repo the human can |
| A separate credential or identity for agents | Two credential paths per contributor; GitHub-side rulesets already make an agent with the human's token safe enough |
| Forward the host's git credentials (VS Code default) | Unscoped, host-OS-specific, and absent in Codespaces |
| Token in a host environment variable via `${localEnv:…}` | VS Code launched from a GUI often does not see the shell's environment, and the setup differs on every host OS |
| `gh auth setup-git` | Writes `~/.gitconfig`, which VS Code replaces with the host's copy |
| Token with the Workflows permission | A pushed branch's workflow runs with the repo's secrets before review; workflow edits are rare enough to do on the host |
| Keep `dev` as a host bind mount | Needs host-side shell (no Windows) and a host path (no Codespaces) |
| One container for all repos | Mixes every repo's dependencies and drops the boundary between repos |
