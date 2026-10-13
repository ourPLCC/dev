# Agent rules for every ourPLCC repo

If a human contributor would need to know it, it goes in `CONTRIBUTING.md` or
`dev-docs/`, even if agents need it too. Agent files hold only what exists
because the reader is an agent.

## Mechanics

- Run `backlog` as a single plain command, never wrapped in other shell code:
  permission rules match the command's start.
- Never edit tracker files by hand; use the `backlog` CLI.
- Follow the ourPLCC tracker guide, not `backlog instructions`; its guidance
  differs from ours on plans, cleanup, and drafts.

## Limits on autonomy

- Create CRs or drafts only with the human's approval.
- During automated plan execution, record discovered work in the CR's notes
  (`backlog task edit CR-N --append-notes "…"`), never as new CRs.
- When closing the CR, triage those notes with the human: new draft, new CR,
  fold into an existing CR, or drop.
- Never merge a pull request.
- Never run `gh auth login`, `gh auth refresh`, or `gh auth token`; if `gh`
  is not logged in, stop and tell the human.
- Push `change-requests` only through `dev`'s `bin/push.bash`, and only to
  publish tracker changes the human approved.
