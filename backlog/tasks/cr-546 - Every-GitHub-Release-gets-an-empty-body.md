---
id: CR-546
title: Every GitHub Release gets an empty body
status: In Progress
assignee:
  - '@StoneyJackson'
created_date: '2026-08-13'
updated_date: '2026-10-12 12:31'
labels: []
dependencies: []
type: chore
project: languages-ng
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
### Summary

`.releaserc.yaml`'s `plugins` key replaces semantic-release's default plugin
list rather than extending it, so
`@semantic-release/release-notes-generator` never loads, nothing implements
`generateNotes`, and every Release is created with an empty body. The plugin
entry is merged as of PR [#12](https://github.com/ourPLCC/languages-ng/pull/12); the issue stays open awaiting verification,
which needs a `feat` or `fix` to reach `main` and actually cut a version
whose body can be inspected.

### Description

[.releaserc.yaml](../../../languages-ng/.releaserc.yaml) names two plugins:

```yaml
plugins:
    - - "@semantic-release/commit-analyzer"
      - preset: conventionalcommits
    - - "@semantic-release/github"
```

Supplying a `plugins` key **replaces** semantic-release's default plugin
list rather than extending it. In `semantic-release@25`'s
`lib/get-config.js`, the default array is spread first and the user's
options are spread over it:

```js
options = {
  ...
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/npm",
    "@semantic-release/github",
  ],
  // Remove `null` and `undefined` options, so they can be replaced with default ones
  ...pickBy(options, (option) => !isNil(option)),
};
```

So `@semantic-release/release-notes-generator` never loads. Nothing
implements the `generateNotes` step, `nextRelease.notes` comes back empty,
and `@semantic-release/github` creates the Release with an empty body.

The tag, the version number, and the Release entry itself are all correct.
Only the notes are missing — which is why this went unnoticed. The only
release on the remote, `v1.0.0` (2026-08-13), was cut from `9e4dc6a`,
before the fix, and its body is empty.

Dropping `@semantic-release/npm` from the list is deliberate and correct —
this repository publishes no npm package. Dropping the notes generator was
not.

### Steps to Reproduce

1. Open any release under
   <https://github.com/ourPLCC/languages-ng/releases>.
2. The body is empty.

### Notes

The fix is one entry in `.releaserc.yaml`, ordered between the analyzer
and the GitHub plugin, since `generateNotes` must run before the Release
is created:

```yaml
    - - "@semantic-release/release-notes-generator"
      - preset: conventionalcommits
```

The `preset` must match the analyzer's, or the notes will be grouped by
Angular's conventions while the version was computed by
conventionalcommits'. The preset package is already installed by the
release workflow's `npx` invocation, so no other change is needed.

Found during CR-545, whose
review ran the release pipeline end to end in a scratch repository and
observed the empty `generateNotes` output directly. Deliberately left out
of that branch: `.releaserc.yaml` was off-limits under its plan's
constraints, and the change is independent of restoring the pipeline.

The large release this was meant to precede has already been cut:
`v1.0.0` covers the whole plcc-ng migration and was cut before the fix
landed. semantic-release will not regenerate notes for an existing tag,
and that body is being left empty.

Migrated from languages-ng #046.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The first GitHub Release cut after PR #12 merged has a non-empty body, grouped by conventionalcommits types.
<!-- AC:END -->
