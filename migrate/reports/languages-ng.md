# languages-ng migration report

Converted 53 files: 42 -> completed/, 10 -> tasks/, 1 -> drafts/.

## Duplicates of plcc-ng issues

- #003 -> CR-503: duplicate of CR-162
- #004 -> CR-504: duplicate of CR-163
- #006 -> CR-506: duplicate of CR-164
- #010 -> CR-510: duplicate of CR-174
- #022 -> CR-522: duplicate of CR-185
- #036 -> CR-536: duplicate of CR-186
- #037 -> CR-537: duplicate of CR-187
- #038 -> CR-538: duplicate of CR-188

## Type mappings (non-identity)

- #010: 'chore' -> fix
- #036: 'chore' -> fix
- #037: 'chore' -> feat
- #038: 'chore' -> fix

## Won't-do (obsolete)

- #020 -> CR-520: Obsolete: languages-ng's file-based tracker was retired.
- #043 -> CR-543: Obsolete: languages-ng's file-based tracker was retired.
- #050 -> CR-550: Obsolete: languages-ng's file-based tracker was retired.
- #051 -> CR-551: Obsolete: languages-ng's file-based tracker was retired.
- #053 -> CR-553: Obsolete: languages-ng's file-based tracker was retired.

## Drafts (lose their number; provenance line keeps it greppable)

- #042 -> DRAFT-2: test.bash's 75-minute run, and two implementers lost mid-task

## Unresolved #N references (add a references entry to the triage file)

(none)

## Defaulted #N references (unqualified #N read as a languages-ng issue)

- 6: #4 -> CR-504 in "name` for the JavaScript reserved-word collision (see issue #4) — one fix in the grammar, in"
- 8: #3 -> CR-503 in "l course-material spellings where 2.0.0 allows it (issues #3 and #6 for sure; #4 subject t"
- 8: #6 -> CR-506 in "e-material spellings where 2.0.0 allows it (issues #3 and #6 for sure; #4 subject to the"
- 8: #4 -> CR-504 in "ellings where 2.0.0 allows it (issues #3 and #6 for sure; #4 subject to the reserved-wor"
- 8: #3 -> CR-503 in "docs/course-material-impact.md` accordingly. - Close issues #3, #4, #6 as resolved-upstream"
- 8: #4 -> CR-504 in "/course-material-impact.md` accordingly. - Close issues #3, #4, #6 as resolved-upstream wher"
- 8: #6 -> CR-506 in "rse-material-impact.md` accordingly. - Close issues #3, #4, #6 as resolved-upstream where 2."
- 10: #9 -> CR-509 in "n was **paused** on this. The decision (see roadmap / issue #9) was to keep V3's grammar in"
- 11: #10 -> CR-510 in "The fixed `_handle_arbno` / `_parse_arbno` code from issue #10 is present in the image-dated"
- 11: #10 -> CR-510 in "n`: after bumping the digest, rebuild without cache. Issue #10 needs no correction. It accur"
- 12: #9 -> CR-509 in "e-branch review fix wave for the V3 migration branch (issue #9, already closed). Not caused"
- 13: #11 -> CR-511 in "The ad-hoc link checker used in the issue-#11 plan (the Python snippet in T"
- 13: #11 -> CR-511 in "esolvable, so no amount of link repair will silence it. The #11 plan's Task 3 Step 4 was writ"
- 13: #11 -> CR-511 in "s literally. ### Notes None of this was introduced by the #11 branch. Its single authored e"
- 13: #11 -> CR-511 in "ner-cache-diagnosis.md:202`) is a fenced quotation of issue #11's pre-close body, showing the"
- 13: #11 -> CR-511 in "ver rewritten. Found during the whole-branch review of the #11 branch, which surfaced the ch"
- 15: #14 -> CR-514 in "d during the whole-branch review of the V4 migration (issue #14, already closed). Not caused"
- 16: #14 -> CR-514 in "d during the whole-branch review of the V4 migration (issue #14, already closed). V4 did not"
- 18: #17 -> CR-517 in "The result is text that contradicts itself. After closing #17, the V5 plan's Task 1 read:"
- 18: #17 -> CR-517 in ". - `close.bash` then re-corrupted the same four lines when #17 closed, which is how this i"
- 18: #17 -> CR-517 in "ored by hand afterward, and will be re-corrupted again if #17 is ever reopened and reclos"
- 20: #18 -> CR-518 in "Notes All three were raised in the whole-branch review of #18 and deferred by explicit deci"
- 20: #49 -> CR-549 in ". Fixing item 1 should fix both. Retitled and re-scoped by #49. The filename keeps its origi"
- 27: #25 -> CR-525 in "t supersedes the `git ls-files`-driven copy added for issue #25 — for migrated languages. **"
- 27: #25 -> CR-525 in "25 — for migrated languages. **Verified** during the issue #25 design across all three Env f"
- 27: #31 -> CR-531 in "added. The bound comes from `bin/bats-tmpdir.bash` (issue #31), which empties each passing"
- 27: #35 -> CR-535 in "ount above is now zero** — OBJ migrated to plcc-ng in issue #35, following TYPE0 and TYPE1. `"
- 27: #35 -> CR-535 in "h`, which is the remaining surface. Also stale as of issue #35: `bin/relocate.bash:41`'s com"
- 27: #35 -> CR-535 in "" — is now factually false, since both have migrated. Issue #35's completion note cites this"
- 28: #25 -> CR-525 in "failing loudly — the same silent-corruption class as issue #25, reintroduced one layer down."
- 28: #25 -> CR-525 in "st handed to `tar`. This matters for the same reason issue #25 mattered: a test can run agai"
- 28: #25 -> CR-525 in "to Reproduce Reproduced by the final reviewer of the issue #25 branch: 1. `chmod 000` the *"
- 28: #25 -> CR-525 in "to read the file, the `pipefail` subshell (added for issue #25) propagates that failure, and"
- 28: #25 -> CR-525 in ". This is a genuine behavior change introduced by the issue #25 fix, and it is inert today on"
- 28: #25 -> CR-525 in ", so the defect is dormant. It was triaged during the issue #25 review as confirmed but non-b"
- 28: #25 -> CR-525 in "ission problem loudly — the same propagation path the issue #25 fix already built via `set -o"
- 30: #19 -> CR-519 in "ies in Python with a `RecursionError`, inherited from issue #19 and unchanged by this port."
- 31: #27 -> CR-527 in "d to `-s` stops contributing to this problem. That makes #27 the structural fix, and this"
- 31: #27 -> CR-527 in "osts on a constrained machine. 2. *The silence.* Even with #27 done, a run that dies for any"
- 31: #27 -> CR-527 in "that counts cleanly. Worth considering independently of #27: have `bin/test.bash` check t"
- 33: #31 -> CR-531 in "### Summary Issue #31's `check_run_complete` only r"
- 33: #31 -> CR-531 in "g pass count, and a leaked report directory — the exact lie #31 set out to eliminate, one lay"
- 33: #31 -> CR-531 in "e guard, not the `EXIT` trap. What survives is exactly what #31 set out to eliminate: - the"
- 33: #31 -> CR-531 in "ave is gone. **This is the same silent-corruption class as #31, #25, and #28**, one layer up"
- 33: #25 -> CR-525 in "s gone. **This is the same silent-corruption class as #31, #25, and #28**, one layer up: the"
- 33: #28 -> CR-528 in "**This is the same silent-corruption class as #31, #25, and #28**, one layer up: the failure"
- 33: #31 -> CR-531 in "ne layer up: the failure is shaped like an ordinary result. #31 moved the detection from "the"
- 35: #12 -> CR-512 in "d-PLCC, because old-PLCC is needed nowhere. The direction #12 already names — base the CI i"
- 35: #12 -> CR-512 in "t-langauges.dockerfile` — is now the whole fix. Note that #12's first deferral reason ("the"
- 35: #12 -> CR-512 in "request` job does fire. Both premises need rewriting when #12 is picked up. - **[#27](027-"
- 36: #37 -> CR-537 in "rrives and OBJ later wants to emit output directly, that is #37's revert, not a reopening of"
- 40: #35 -> CR-535 in "g the final whole-branch review of the OBJ migration (issue #35)."
- 41: #35 -> CR-535 in "g the final whole-branch review of the OBJ migration (issue #35). Both fixes are mechanical ("
- 42: #35 -> CR-535 in "g the final whole-branch review of the OBJ migration (issue #35). If this recurs on a future"
- 44: #12 -> CR-512 in "ir` can fail under `src/`. It cost a CI round-trip on issue #12: all 165 language tests faile"
- 44: #28 -> CR-528 in "e `safe.directory` remedy had been discarded. Same shape as #28. ### Description `relocate_"
- 44: #12 -> CR-512 in "is not hypothetical. It cost a full CI round-trip on issue #12. The first run of the new `co"
- 44: #12 -> CR-512 in "The CI symptom that surfaced this is already fixed on issue #12's branch by a "Trust the work"
- 47: #46 -> CR-546 in "md` exists or ever has, and the Release notes are empty per #46. The rule is right; its state"
- 47: #46 -> CR-546 in "ind of claim someone reasons from later. ### Notes Fixing #46 makes the "GitHub Release not"
- 49: #20 -> CR-520 in "ing `awk` that this issue deletes. It does **not** obsolete #20 entirely: the four sweep-up i"
- 49: #20 -> CR-520 in "is change untouched. Whoever does this work should re-scope #20 rather than close it. **Reso"
- 49: #20 -> CR-520 in "being trimmed out of a surviving document. And of the four #20 sweep-up items named above, o"
- 50: #49 -> CR-549 in "Notes Two fix directions, from the whole-branch review of #49: 1. **Break the coupling str"
- 50: #49 -> CR-549 in "referred; direction 2 is what would have caught this during #49 rather than during its review"
- 50: #47 -> CR-547 in "omething about the tooling that quietly stopped being true. #47 was a claim that was never tr"
- 51: #49 -> CR-549 in "an issue's body. All three were hand-traced correct during #49's review, so this is a regres"
- 51: #20 -> CR-520 in "[#20](020-close-bash-roadmap-awk-edge-cases.md), not after: #20 changes the argument guard an"
- 51: #20 -> CR-520 in "that change safe. Filed separately rather than folded into #20 because #20 is about defects"
- 51: #20 -> CR-520 in "safe. Filed separately rather than folded into #20 because #20 is about defects in that code"
- 51: #49 -> CR-549 in "ed by different work. Raised in the whole-branch review of #49 and deferred there by explici"
- 51: #49 -> CR-549 in "eview of #49 and deferred there by explicit decision, since #49's own scope was the roadmap r"
- 52: #37 -> CR-537 in "rget: ourPLCC/plcc-ng` reads as "nothing for us here" while #37 quietly carries a revert of O"
- 52: #37 -> CR-537 in "ral reading of `target: ourPLCC/plcc-ng`, and it is wrong — #37 carries a revert of OBJ's `Pr"
- 52: #37 -> CR-537 in "*output record kind**, which is upstream #187 — this repo's #37. Upstream #186 landing alone"
- 52: #36 -> CR-536 in "a diagnostic without giving OBJ anywhere to emit output. So #36 gates nothing locally, and bo"
- 52: #37 -> CR-537 in "o #36 gates nothing locally, and both workarounds belong to #37. **No scalar field can expre"
- 52: #36 -> CR-536 in "tempt to add an `upstream-fixed:` date broke immediately on #36, which names two upstream ref"
- 52: #37 -> CR-537 in "st** titled "069 improve parse trace," not to the issue our #37 means. Upstream is also migra"
- 52: #36 -> CR-536 in "ange. With one open upstream-targeted issue remaining after #36 closes, a durable pointer plu"

## Link findings

- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: ../../bin/issues/close.bash
- link to retired tracker file made plain text: ../issue-conventions.md
- qualified cross-repo mention (verify): plcc-ng #185 -> CR-185
- qualified cross-repo mention (verify): plcc-ng #186 -> CR-186
- link to retired tracker file made plain text: ../issue-conventions.md
- qualified cross-repo mention (verify): plcc-ng #187 -> CR-187
- qualified cross-repo mention (verify): plcc-ng #188 -> CR-188
- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: .
- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: ../issue-conventions.md
- link to retired tracker file made plain text: ../issues/
- link to retired tracker file made plain text: ../roadmap.md
- link to retired tracker file made plain text: ../../bin/issues/list.bash
- link to retired tracker file made plain text: ../issue-conventions.md
