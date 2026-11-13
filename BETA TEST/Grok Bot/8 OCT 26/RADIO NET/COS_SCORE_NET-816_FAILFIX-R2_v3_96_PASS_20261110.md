# DESIGNATED CoS PLAN SCORE: NET-816 Catalog Chunk 1 FAIL-FIX ROUND 2, plan v3 (writer: AG CoS v5)

**Score: 96 / 100, PASS (CoS gate only).** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 8:55 PM ET (America/New_York).
**Count: NET-816 fail-fix R2 track attempt 3 of 10; writer AG CoS v5 try 3 of 4.**
**This is not a clean pass.** Two material defects remain (D3′ and D4′ below). Each is a small, mechanical fix. **CoS recommendation:** amend them (v3.1) before SAG, the same way NET-827 v1.9 → v1.9.1 was handled. If v3 goes to SAG as-is, expect SAG to find D3′.

## Plan scored (no mismatch)
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md` (written 8:20:20 PM ET; byte-identical copy in `Carbon\`)
- **Scored bytes:** SHA-256 **`e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75`**, **35,380 bytes**, LF only. On disk, the Carbon mirror and the box copy all **match the DONE** (`DONE_BATON_NET-816_FAILFIX-R2_PLAN-ONLY_v3_AGCOS-V5_20261110.md`, 4,895 B, SHA `65e5fdd8…0016`, 8:21:09 PM ET).

## Inputs
- My v2 score `COS_SCORE_NET-816_FAILFIX-R2_v2_92_REVISE_20261110.md` (13,440 B, SHA `abb1d807…89d2`), D1–D4 and C1.
- Baton `BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v3_FROM-92_20261110-2010.md` (1,749 B, SHA `419b1dfe…4349`).
- Plan v2 (`0f5b89be…82d7`) for a line diff. v3 changes only the D1–D4/C1 areas, the header and the summary; everything else is byte-identical to v2.

## Code checked (read-only, `a3d7dca20fbbaf06a522205b22d0740b600de52b`)
- `lib/screens/catalog/catalog_browse_screen.dart:112-200` (`_applyFilters`), `:1080-1215` (card, chip), `:900-925`; `test/catalog_chunk1_face_value_and_card_test.dart:101-200,323-345,348-385`; `test/catalog_browse_test.dart`; `lib/services/melt_value_service.dart:54-131`; `firebase.json` hosting block; `assets/catalog/catalog_public_v1.json` (3,202 records, Python simulation).
- **Branches:** `p7-v8.9` is now **`e55302e2716a8943a3847118e0ccf2a859a1b872`** (8:22:50 PM ET, "deliver NET-816 fail-fix r2 plan v3 and sync batons"), past `ac7c8bb3`. `git diff a3d7dca2 e55302e2` touches only `.md`/`.txt` docs, two archives and `For SAG/10 NOV 2026/SAG_RESPONSE_NET-827_v1.9.1_20261110.json`; **no app code**. `main` is still `9f04550a45fa…` (ls-remote).

## Closure of D1–D4 and C1
| Item | Verdict | Evidence |
|---|---|---|
| **D1** test `:139` → 2.00 | **Closed** | §1.3 states the one-line change `'Dollar (two-coin set)': 1.00` → `2.00`; §4 item 6 lists it; it no longer claims all existing tests are unchanged. With it, the full-catalog test's `misParses` stays 0 (only that denomination changes). |
| **D2** raw strings | **Closed** | Both F5 `reason:` strings are now `r'…'` (plan L339, L349). The remaining `$` amounts are inside `//` comments, which is fine. The test compiles. |
| **D3** 1842 card test / test path | **NOT closed (D3′)** | See the deductions. |
| **D4** RT-A / readback / v5 safety | **Partly closed (D4′)** | Closed: RT-A and the YES use the full 40-character `a3d7dca20fbbaf06a522205b22d0740b600de52b`; `git rev-parse --verify "$BuiltSha^{commit}"`, and the c547b7a0 check runs on the resolved SHA; `$ErrorActionPreference='Stop'`; worktree under `$env:TEMP` with a timestamp and an outside-repo check; the blind `Remove-Item` is gone; cleanup uses `git worktree remove --force` + `prune` in `finally`. Not closed: the post-deploy readback (D4′). |
| **C1** 1,047 file-only records | **Closed** | §1.2 states 166 coins + 1 medal renderable; 1,047 file-only (966 `type_image`, 81 `primary_image`); 1,988 with no image metadata (1,752 + 181 + 55); ~2,799 coins, 181 notes and 55 medals show "No photo yet". All verified against the JSON (1,213 − 166 = 1,047; no overlap). The new Chunk 2 scan key `primary_image == null || primary_image['url'] == null` selects 2,799 coins + 181 notes + 55 medals, covering all 1,047 file-only records, including the 81. |
| E1–E6, F1, CSP | Still closed | Byte-identical to v2, apart from `\bset\b` (v2 advisory 2, taken). It still matches only `Dollar (two-coin set)` in the catalog. |

## Deductions (each one is material)
| # | Pts | Area | Evidence | Why it matters | Exact fix |
|---|---|---|---|---|---|
| D3′ | −2 | Correctness/regression: the "two-pass" search is per-item, so the 1842 card test still finds 2 | The plan code (L364-382) runs inside the per-item `_allEntries.where((item) {…})` closure (`catalog_browse_screen.dart:120-170`). "Pass 1" returns true for this item on a direct match; otherwise "Pass 2" runs the token match **for the same item**. That is item-level OR: old substring ∪ token match. The comment at L377 ("only if no direct substring matches exist across the catalog") describes a catalog-level two pass that the code doesn't do. A simulation over the real JSON with the v3 logic: `1842 liberty seated dollar` → **2** (`1842 Liberty Seated dollar`, `1842 Liberty Seated half dollar`); `morgan dollar 1881` → 5; `1816` → 0. Both 1842 cards are non-medal, so both render `'Face value · No retail estimate'` (`:1160-1186`). The existing widget test `:378-383` `findsOneWidget` therefore fails, and the plan's new test `search('1842 Liberty Seated dollar') -> 1` fails too. Also, `test/catalog_browse_test.dart` exists, but it tests `us_numismatics_catalog_screen.dart` (`package:numista_ai`), not `CatalogBrowseScreen`, and the `search(...)` helper the plan uses doesn't exist there. | The test suite stays red, and the plan states as verified ("returns exactly 1 card … passes without modification") something that is false against the real code and data. The user-visible effect is minor (an extra half-dollar result). | Do the two passes at list level: compute `direct = filtered.where(substringMatch)`, then `result = direct.isNotEmpty ? direct : filtered.where(tokenMatch)`, applying the other filters first. Re-state the 1/5/0 results under that logic. Put the search tests in a file that pumps `CatalogBrowseScreen` (e.g. extend `catalog_chunk1_face_value_and_card_test.dart`, which already uses `pumpLoadedCatalog` and `initialQuery`), with real assertions rather than an undefined `search()`. |
| D4′ | −2 | Execution / safety: the post-deploy readback silently skips and still prints "verified"; there is no live check | L509 extracts the preview URL with `https://studio-9101802118-8c9a8--p7-gate-[a-z0-9]+\.web\.app`, but the Hosting site is **`numista-vault`** (`firebase.json` hosting `site`), and the real p7-gate URL is `https://numista-vault--p7-gate-8avtpz22.web.app` (FT result). The regex never matches, so `if ($channelUrlMatch.Success)` skips the `version.json` `git_commit` assertion and all route checks, and the script then prints "SUCCESS: Deployed **and verified**". The "live release unchanged" check claimed in §0 and the DONE isn't in the script: it only checks that `"p7-gate"` appears in the list. There's no pre-deploy capture of the live release time, and no `$LASTEXITCODE` check on `channel:list`. Minor: `Set-Location $repoRoot` right after `$repoRoot = (Get-Location).Path` is a no-op, not a set-to-repo-root. `/#/catalog` over HTTP doesn't test the fragment route, because browsers don't send fragments. | The readback the baton required (live unchanged; preview serves the stamped `version.json`) never runs, and the operator is told it passed. That's the F4 failure mode again (an unproven build pin). | Before deploying, capture the live channel release time from `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json`. After deploying, re-read with `--json` and check the exit code; throw if the live release time changed or `p7-gate` is missing. Take the p7-gate URL from the JSON (or match `https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`), and **throw if no URL is found**. Then assert the served `version.json` `git_commit` equals the resolved SHA. Use `Set-Location` with the fixed repo path `C:\Users\ericd\Documents\MyVertexProject` (as v5 §7.4 does) and check `git rev-parse --show-toplevel`. |

**Total: 100 − 4 = 96, PASS (CoS gate).**

## Advisories (not scored)
1. §1.2 note: the record counts are slightly off. `americanhistory.si.edu` appears in **171** records (173 URLs), and `fraser.stlouisfed.org` appears in **31** records (65 URLs), not 37. These are citation fields only, so the CSP is unaffected.
2. §2.2 says the script lives at "`scripts/deploy_preview.ps1` (or outside repo)". There's no `scripts/` directory at `a3d7dca2`, and §4 doesn't list one. Keep it outside the repo on EDS_Laptop, or list it as a new file.
3. The runbook doesn't run `flutter test`/`flutter analyze` before deploying. Consider gating the deploy on the §3 matrix.
4. Carried over: `--expires` behaviour on `channel:deploy`; CORS for the Met and numismatics.org images under CanvasKit.

## Regressions / invented items
- No invented commits. `a3d7dca2`, `ac7c8bb3` and `e55302e2` are real (the plan's docs pin is `ac7c8bb3`, now one docs commit behind; no code impact). `9f04550a` is main.
- Invented: the `search(...)` helper in `catalog_browse_test.dart`, and the false claim about the 1842 result (D3′). The preview-URL host in the readback regex doesn't exist (D4′). Citations spot-checked as accurate: `:139`, `:323-345`, `:348-385`, `:147-151`, `:1113-1120`, `:155-172`, `firebase.json:284`.
- No regression in F1, the CSP, F3 parsing, F4 stamping or F5. The D3′ regression is in the existing widget test.

## Next step
- **CoS gate PASS (96) on `e7c54bab…7f75` only.** It goes to SAG only under the dual-gate rule, and CoS recommends a v3.1 amendment for D3′ and D4′ first. A CoS ruling is needed on whether v3.1 counts as an attempt.
- A full-plan SAG packet and paste prompt for **v3 exactly** were built on the box and **not submitted**.

## Authority statement
This score **grants no code, git, build, deploy, Firestore, GCS, Stripe or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force; main stays `9f04550a`; Stripe live stays OFF. A p7-gate deploy still needs CoS 95 + SAG 95 + Eric's typed scoped YES naming the built SHA, p7-gate and RT-A `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
