---
id: DRAFT-4
title: course-materials-ng's External links check fails on sites that block bots
status: Draft
assignee: []
created_date: '2026-10-13 20:30'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In course-materials-ng, checks.yml's External links job (lycheeverse/lychee-action over textbook/**/*.md) fails on pull requests because some linked sites refuse automated requests. Seen on PR #68 (2026-10-13), which changed only workflows. The check is not required by main's ruleset, so it blocks nothing, but a check that always fails trains people to ignore it. Options include excluding the blocking hosts in a lychee config, accepting 403/429 for them, or running the check on a schedule instead of on PRs. Found during CR-1025.
<!-- SECTION:DESCRIPTION:END -->
