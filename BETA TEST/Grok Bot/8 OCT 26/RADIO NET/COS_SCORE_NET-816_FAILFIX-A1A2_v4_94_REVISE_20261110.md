# DESIGNATED CoS PLAN SCORE: NET-816 Fail-Fix A1/A2 (AG CoS v5), plan v4

**Score: 94 / 100, REVISE** (pass mark 95; only material defects count: correctness, safety, permissions, execution. No points taken off for cosmetics.)
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 4:00 PM ET.
**Count: attempt 4 of 10 on the NET-816 fail-fix track; writer AG CoS v5's attempt 4 of 4, its final try.** Under Eric's 4/10 rule ("if someone is still failing after 4 tries, somebody else take over"), **a different writer must take attempt 5.** 6 of the 10 attempts remain; the Claude rule (attempts 9–10 go to Claude) is not yet triggered.

## Plan scored
- `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v4_AGCOS-V5_20261110.md`
- SHA-256 `eed812708c6db9b307a1892eb29d79e21fbac3691005fd47fd9a9084bcbaeb1c`, 19,947 bytes, 328 lines, last written 3:50:10 PM ET. This matches AG's report.
- All six routes are byte-identical (same SHA and size).

## Baseline and sources
- v3 record `COS_SCORE_NET-816_FAILFIX-A1A2_v3_94_REVISE_20261110.md`, SHA-256 `9d5b3549787cb04278b033ec9cfe819ffce83fa1d160bdc203ac9a0bc5a11aaf`.
- Code Reviewer review, SHA `3e2c1670…864ff`.
- HOLD/stop-rule order, SHA `41b8bd5f…778943d`.
- Preview HOLD `HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md`, SHA `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b`.
- Repo checked read-only on EDS_Laptop:
  - `7fe4fae8` (3:51:57 PM ET, "docs(radio): file NET-816 fail-fix v4 plan…") is HEAD of `p7-v8.9` and equals `origin/p7-v8.9`. It adds 22 files, all under `BETA TEST/Grok Bot/8 OCT 26/{BATONS,INBOX,OUTBOX,RADIO NET}/` and `BETA TEST/Grok Bot/10 NOV 26/`. It only adds files, nothing under `numista_mobile`, so **it is docs only.**
  - `git diff c547b7a0 HEAD -- numista_mobile` is empty, and there are 0 dirty files, so **`numista_mobile` is unchanged from `c547b7a0`.**
  - `origin/main` = `9f04550a…`.
- Scratch only (`%TEMP%\cos_net816ff_ro\v4_check\`): `dart analyze` and `dart run` of the plan's test block against a scratch copy of `melt_value_service.dart` with v4 Changes 2.1–2.5 applied.
- Python port, v3 against v4, on all 3,202 catalog rows.

## v3 deduction closure map

| v3 | Status | Evidence |
|---|---|---|
| M1 rollback (shared-tree checkout; deploy form) | **Mostly closed** | The rule never to check out in `MyVertexProject` (line 300) and the separate worktree (line 305) are both right. The deploy command now matches the repo's pinned form exactly: `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` (line 312). That's the same as the NET-816 preview baton (line 24) and DONE NET-772 (line 11), and it matches `numista_mobile/.firebaserc` default `studio-9101802118-8c9a8`. With no `--only`, it deploys the single hosting config (site `numista-vault`), which is a valid target. `--base-href "/"` matches CI (`ci-dev.yml:58`, `deploy-production.yml:59`).<br>**Build inputs are present in a clean worktree:** `firebase.json`, `.firebaserc`, `lib/firebase_options.dart` and `pubspec.lock` are all tracked. There is no root `firebase.json` that could be picked up by mistake. `flutter build` runs `pub get` itself. There is no `.env`, and the `String.fromEnvironment` URLs in `constants.dart:13–22` have production defaults. The only ignored files are `_checklists_source/*.pdf`, which `pubspec.yaml` doesn't reference. The existing `%TEMP%\p7gate_build_6ee3` worktree shows the same tracked-only pattern.<br>**`git worktree remove --force`** is safe: it deletes only that folder and its admin entry, and `--force` is needed because of the untracked `build/`.<br>New problems: **R1** and **R2** below. |
| M2 FT-4 zero-write | **Closed for zero-write, but the claim is inaccurate** | FT-4 is now a local `flutter test … --plain-name "half dime"` (line 268). The filter matches the new test name (it contains "half dime"), and the test is pure, with no Firebase. The 14 expectations pass in the Dart scratch run (the v4 test block is byte-identical to v3's). **$1.0851 = 0.03617 × $30** is correct, and it rounds to "$1.09". No fixture file needs to be created. The description is wrong, though (**R3**). |

## Deductions on v4 (each one is material)

| # | Pts | Area | Evidence | Defect |
|---|---|---|---|---|
| R1 | −3 | Permissions: rollback target | Plan lines 302–318 (rollback deploys `c547b7a0` to p7-gate, "Record deployed commit `c547b7a0`"). The same target has appeared since v2 and v3, and **this CoS missed it in the v2 and v3 scores.** | **The rollback deploys a commit that is under a standing CoS HOLD.** HOLD `74611e05…` (11:48 AM ET) says: "**Do NOT re-issue or retry that preview deploy at `c547b7a0`.** That commit lacks the `/catalog` rewrite (A1)." AG's own report says this HOLD "remain[s] in full force". `c547b7a0` was also **never on p7-gate**: its preview was BLOCKED at 11:40 AM ET (`BLOCKED_BATON_…20261110-1140.md`), so it isn't a "known-good" prior build. The plan names no authority for a rollback deploy. A rollback must restore whatever is **actually** on p7-gate before the fix deploy: record its version or commit, for example from `firebase hosting:channel:list`, or from the last DONE record, DONE NET-772 (4 Nov). Or it should say no redeploy, and Eric decides. Either way, the scoped YES must name the rollback target. |
| R2 | −2 | Safety / execution: shell syntax | Plan lines 303–316 (a block labeled `bash`, using `"%TEMP%\p7gate_rollback_c547"`, `cd C:\Users\…`) | The block only works in **cmd.exe**. In PowerShell, the shell AG uses on EDS_Laptop through its `.ps1` scripts, `%TEMP%` is **literal**. I confirmed this on the laptop: `"%TEMP%\p7gate_rollback_c547"` resolves to `<cwd>\%TEMP%\p7gate_rollback_c547`. Step 1 has no `cd` and must run inside the repo, so the "isolated" worktree would land **inside the shared `MyVertexProject` tree** as `MyVertexProject\%TEMP%\…`. The M1 rule exists to protect exactly that tree. A doc `git add -A` or the 18:00 auto-backup could then pick it up as an embedded repo. In bash, `cd C:\Users\…` also loses its backslashes. Use `$env:TEMP` or the absolute path `C:\Users\ericd\AppData\Local\Temp\p7gate_rollback_c547`, start with `Set-Location C:\Users\ericd\Documents\MyVertexProject`, label the block PowerShell, and stop on error, for example `$ErrorActionPreference='Stop'`. |
| R3 | −1 | Execution: Field Tester claim | Plan line 268 (FT-4 runs "against verified catalog Half Dime fixture (`assets/catalog/catalog_public_v1.json` row `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`) … confirming melt value for 1853 Half Dime resolves to **$1.0851**") | **The test never reads that file or that row.** It calls `compute` with literal strings (`'Silver (90%)'`, `'Half Dime'`). The real 1853 catalog row has `composition: null`, denomination `Half dime`, series `Seated Liberty Half Dime`. Run through v4 `compute`, it returns **null (N/A)**, not $1.0851, because there is no "silver" in its text. That's harmless for the catalog, since cards don't call `compute`. But the pass criterion claims a check that doesn't happen. The plan should state what the test proves and record the remaining gap: there is **no visual dashboard half-dime check on the preview**, because no zero-write half-dime account exists. FT-4 also repeats gate step 2 (line 276). The local test is acceptable as the A2 correctness proof, provided the plan says this honestly. |

**Total: 100 − 6 = 94, REVISE.**

## Required fixes for attempt 5 (new writer per the 4/10 rule; all small)
1. **R1:** Rollback target = the build actually on p7-gate before the fix deploy, recorded first. Or no redeploy, with Eric deciding. The scoped-YES text must name the rollback target. Remove "redeploy `c547b7a0`".
2. **R2:** Use a PowerShell block with `$env:TEMP` (or an absolute path), an explicit `Set-Location` into the repo first, and stop-on-error.
3. **R3:** Reword FT-4 to say it is a local unit-level A2 proof using literal inputs, not the catalog row. State that the preview dashboard visual check is deferred because no zero-write account exists.

Everything else in v4 is verified and can be reused as is: A1 rewrites, Changes 2.1–2.5, tests (a)–(e), FT-1 to FT-3, the gate, base and build identity, revert, the channel-delete rule, and scope.

## Regression scan
- **v3 to v4, catalog: 0 rows change.** Old to v4 is the same 328-row set as v3, with all improvements kept and no new regressions.
- Synthetic edge cases (advisories in v3) are now fixed:
  - "Silver / Dime / Wartime" now gives 0.07234 (v3 gave 0.05626).
  - "Quarter / Wartime" now gives 0.18084.
  - "5 Cents / Howard award" and "Edward" now give 0.03617.
  - "Silver, Copper, Manganese / 5 Cents / Jefferson" now gives 0.05626.
- Remaining advisory: the `war` substring still catches words like "Warren" at a 0.05 face value. That's hypothetical and not in the catalog.
- **The Dart scratch run reads "No issues found!" and 14 of 14 checks pass** on the v4-patched copy.

## Advisories (not scored)
- `firebase hosting:channel:deploy` without `--expires` resets the channel expiry to the CLI default; an earlier track used `--expires 30d`.
- Header line 2 says "Filed 15:55 EST"; the file was written at 3:50 PM ET.
- `7fe4fae8` also put `CODE_REVIEW_GO-LIVE…` and `UX_AUDIT_CHECKLIST…` (`10 NOV 26`), plus copies of this CoS's v3 score, into git. They are docs only, but note they are now in the repo history on `origin/p7-v8.9`.
- 404-page `/?route=Catalog` and the pre-existing catalog data issues carry over from v3.

## Authority statement
This score **grants no code, merge, deploy, Firestore, Stripe or go-live authority.** It is REVISE, so **no SAG packet was built** and nothing was copied to `For SAG`. Both HOLDs (`41b8bd5f…`, `74611e05…`) and the go-live stop rule stay in force. **AG CoS v5's writer attempts are used up (4 of 4).** Attempt 5 of 10 goes to a different writer, assigned by CoS/Eric; it is not self-assigned.
