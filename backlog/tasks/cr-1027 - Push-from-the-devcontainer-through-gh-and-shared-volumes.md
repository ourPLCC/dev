---
id: CR-1027
title: Push from the devcontainer through gh and shared volumes
status: In Progress
assignee:
  - '@stoney'
created_date: '2026-10-13 13:54'
updated_date: '2026-10-26 19:43'
labels: []
dependencies:
  - CR-1021
  - CR-1022
  - CR-1023
  - CR-1024
  - CR-1025
  - CR-1026
references:
  - ../../dev-docs/specs/2026-10-13-devcontainer-permissions-design.md
type: chore
project: plcc-ng
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Nobody can push from inside plcc-ng's devcontainer, so every push happens on the host, and agents can't push a branch or open a PR. The devcontainer's initializeCommand also runs POSIX shell on the host and bind-mounts a host folder, which rules out Windows hosts and Codespaces. As the first repo to adopt the shared setup, plcc-ng also settles the spec's open checks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The devcontainer applies the spec's 'How the credential reaches the container': the gh feature, gh as the only github.com credential helper, no askpass fallback, no SSH agent, remoteUser vscode with UID 1000
- [ ] #2 The devcontainer applies the spec's 'Where the shared clones live': the ourplcc-gh, ourplcc-dev, and ourplcc-change-requests volumes, BACKLOG_CWD, no initializeCommand, and bin/install/shared-clones.bash
- [ ] #3 .claude/settings.json denies the commands the spec lists
- [ ] #4 .gitattributes starts with * text=auto eol=lf
- [ ] #5 CONTRIBUTING.md describes the volumes in place of the ../dev clone and drops the ../change-requests rename paragraph
- [ ] #6 The spec's Verification checklist passes on a Linux or macOS host, a Windows host, and a new Codespace
- [ ] #7 The spec's open checks are settled, and the spec is updated where a result contradicts it
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
From CR-1021's final review: bin/install/shared-clones.bash must take the shared lock as flock -o -w 120 /workspaces/dev <command>, never by opening a descriptor in its own shell, or a child that outlives it (git maintenance detached by fetch) keeps the lock. dev's bin/push.bash (dev PR #15) shows the pattern. The spec's new open check, that the lock in one container blocks another container on the same volume, is settled here.

2026-10-13: the maintainer narrowed CR-1028-CR-1030's verification to a smoke test; this CR alone runs the full Verification checklist on all three hosts. The permissions spec's Verification section still says each code repo's CR passes the checklist in all three; amend it in the same dev PR as the open-check results (AC 7).

2026-10-26: started on plcc-ng branch cr-1027-push-from-devcontainer; plan in .plans/2026-10-26-cr-1027-push-from-devcontainer.md. Next: Part A Task 1 (bin/install/backlog.bash).

2026-10-26: Part A (Tasks 1-5) done on plcc-ng branch cr-1027-push-from-devcontainer, 6 commits, unpushed; final review clean after one fix; commands tier 332/332, units and docs green. Deferred minors from the review: clone killed mid-checkout passes as complete; CONTRIBUTING offline recovery should also say rerun bin/install/backlog.bash; backlog.bash --check can exit non-zero if backlog --version fails; CONTRIBUTING 'token of your own' untrue in a Codespace; install-helpers row should say 'clean checkout of main'; a hanging fetch holds the shared lock until TCP timeout. devcontainer-lock.json lacks the github-cli entry until the first rebuild (Part B1): commit it then. Next: Task 6 (human, on the host): push the branch and open a draft PR.

2026-10-26: Task 6 done: branch pushed, draft PR https://github.com/ourPLCC/plcc-ng/pull/338 (merge only in CR-1022 cutover step 6). Next: Part B (open checks, human) in a separate test container, B1 first; no tracker edits or pushes there.

2026-10-26 B1 passed (macOS host, test clone ~/cr-1027-test/plcc-ng): both volumes cloned and owned by vscode, dev at origin/main, change-requests hooksPath /workspaces/dev/.githooks, backlog 1.53.0 = pin; a rebuild kept both clones. First build's postStart failed in ghcup: Docker Desktop disk full (two plcc-ng containers each install GHC); docker builder prune freed 13 GB. Not caused by the branch. For B2: the Dev Containers CLI passes --remote-env SSH_AUTH_SOCK=/tmp/vscode-ssh-auth-*.sock, which may override devcontainer.json's empty SSH_AUTH_SOCK.

2026-10-26 B2 (open check 1) FAILS the strong test: SSH_AUTH_SOCK is empty and ssh-add finds no agent by default, but VS Code still creates /tmp/vscode-ssh-auth-<uuid>.sock in the container, and SSH_AUTH_SOCK=<that socket> ssh-add -l reaches the host agent ('The agent has no identities', exit 1). So an empty SSH_AUTH_SOCK hides the agent but doesn't block it. Two web searches found no documented Dev Containers setting that turns the forwarding off. Lock entry for github-cli committed (468ba608, unpushed).

2026-10-26 B2 follow-up: a new terminal does not recreate the socket, but a window reload does (new uuid). Maintainer chose both: postAttachCommand 'rm -f /tmp/vscode-ssh-auth-*.sock' (commit on branch, defense in depth; a race at attach and a process that survives a reload remain), AND amend the permissions spec's open check 1 plus dev's CONTRIBUTING.md (token section): VS Code always forwards the host agent and no setting turns it off, so contributors keep no GitHub-capable SSH key loaded in the host agent and use HTTPS with Git Credential Manager on the host. The spec and CONTRIBUTING edits go in dev PR #15 with the other open-check results.

2026-10-26 B2 passes with the postAttachCommand (branch at 526eccbf): after a rebuild, once postStart finished, no socket; after a window reload, no socket. Residual risk for the spec amendment: postAttachCommand runs only after postStartCommand finishes, so on every container start the socket is reachable while postStart runs (minutes on first build while GHC installs), plus the attach race and a process that survives a reload.

2026-10-26 B3 (open check 5) passes: while the test container held 'flock /workspaces/dev sleep 60', a second container on the ourplcc-dev volume (docker run debian:trixie flock -w 5 /workspaces/dev true) exited 1; with no holder, the same command exited 0 at once. The lock crosses containers on a shared volume (Docker Desktop, macOS).

2026-10-26 B4 (Verification 10) passes: credential.https://github.com.helper lists only the empty reset and '!gh auth git-credential', both from the environment; gh not logged in; 'git push --dry-run' failed in 0.35 s with 'terminal prompts disabled', exit 128. No general credential.helper was installed by VS Code this time (likely git.terminalAuthentication/github.gitAuthentication false), so the reset was not exercised against one. The host's ~/.gitconfig was copied in, including an unrelated gitlab.com helper.

For triage at close (maintainer wants it addressed eventually): VS Code copies the host's ~/.gitconfig into every container, so host-only config such as the gitlab.com helper reading $GITLAB_TOKEN rides along. Options to weigh: fix it on the host only (personal), or have ourPLCC containers stop copying it (VS Code user setting dev.containers.copyGitConfig). The latter also drops user.name/email and the GPG signing config the permissions spec relies on, so it would need a replacement.

2026-10-26 B5: Codespace on the branch. The permissions prompt offered ourPLCC/dev Contents write (plus mandatory Metadata read) and listed ourPLCC/change-requests Contents write as 'not available' (the repo doesn't exist yet; the grant doesn't follow the redirect to dev). Authorized. C4 must confirm a Codespace created after the cutover gets the change-requests grant.

2026-10-26 B5 open check 4 passes: in a Codespace, /workspaces/dev and /workspaces/change-requests are Docker volumes (/volumes/ourplcc-*/_data), dev cloned at origin/main, gh logged in via the Codespace GITHUB_TOKEN (ghu_) with no login. Open check 2, part a: the Codespace token CAN push a .github/workflows/ change (pushed branch cr-1027-probe-workflow, exit 0; branch then deleted). Spec's table must record this difference for Codespaces; bounded because CI runs only on pull_request with read-only GITHUB_TOKEN and release secrets live in the release environment (main and v* only).

2026-10-26 B5 open check 2, parts b-d: (b) tag push rejected by the tag ruleset (GH013, creations restricted); (c) fast-forward push to gh-pages rejected by the gh-pages ruleset (GH013, cannot update protected ref); (d) the Codespace token CAN create a draft release (untagged, private, triggers nothing; deleted after). Contents write likely allows the same with the local token, so it may not be Codespaces-specific; publishing creates the tag, which the tag ruleset should stop. Publish not tested (a tag that got through couldn't be deleted without editing the ruleset); Verification 7 in Part C covers gh release create for a new tag. Spec amendment: the table's tag row should say drafts are possible and the tag ruleset is the gate.

2026-10-26 B5 open check 3 started: Codespace terminal left open, GITHUB_TOKEN fingerprint (sha256, first 8) 8f433a70 at 19:42:51 UTC. Later: compare with a new terminal's fingerprint; in the old terminal run gh api user and git ls-remote origin. Settled when the fingerprint has changed and the old terminal still works.
<!-- SECTION:NOTES:END -->
