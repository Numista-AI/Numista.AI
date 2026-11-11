# DESIGNATED CoS PLAN SCORE: NET-816 Catalog Chunk 1 FAIL-FIX ROUND 2, plan v1 (writer: AG CoS v5)

**Score: 83 / 100, REVISE.** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted, and external prerequisites are not counted as plan defects.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 7:55 PM ET (America/New_York).
**Count: NET-816 fail-fix R2 track attempt 1 of 10; writer AG CoS v5 try 1 of 4.**

## Plan scored, and a hash mismatch
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-R2_v1_AGCOS-V5_20261110.md`
- **Scored bytes (on disk):** SHA-256 **`51cbf837ddfb828c69c5b2281aafcb38fee8bc05db3dbc4d88a3f280d866a811`**, **17,414 bytes**, 258 lines. Copied to the box at `/workspace/net816-failfix/round2/`; the hash matches the on-disk value.
- **MISMATCH:** the DONE baton claims **17,156 B, SHA `72d2ecbd…b6e`**. Those bytes weren't on disk, so this score applies only to `51cbf837…a811`. Any later SAG or YES must cite `51cbf837…a811`, or this plan must be re-scored.

## Inputs
- Baton `BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_FROM-FT47_20261110-1845.md` (F1–F5 plus notes).
- Field Tester report `FT_RESULT_NET816_CATALOG_CHUNK1_p7gate_20261110.md` (47/100 FAIL), copied to the box.
- Earlier NET-816 material (A1/A2 v1–v5 scores, the Claude attempt-5 packet).
- Eric's 31 Oct interim image rules (NET-674): GCS and Firestore are read-only for images, and new images are staged on the box with a `MANIFEST.csv` marked `status=PROPOSAL`.

## Code checked (read-only)
- Public GitHub `Numista-AI/Numista.AI`.
- **Commit `49e77cf7` exists:** `49e77cf783310dd1666b82bc66c071c0ce46c359`, 10 Nov 2026 7:05 PM ET, "docs(radio): ACK batons for NET-816 fail-fix R2 and NET-827 plan v1.9 attempt 4". It's a docs-only commit on `p7-v8.9`, a descendant of `a3d7dca2` with **no app-code changes** (`git diff a3d7dca2 49e77cf7` touches only docs/radio files). The plan's pin is real and equivalent to `a3d7dca2` for code. This supersedes my earlier "likely invented" suspicion, including advisory X10 in the NET-827 v1.9 harvest.
- `p7-v8.9` has since moved to `ba1c7843` (7:20 PM ET, docs only). `main` is still `9f04550a`.
- **Files read at `a3d7dca2`:**
  - `numista_mobile/lib/main.dart:51,115-170`
  - `numista_mobile/firebase.json:283-284` (CSP)
  - `lib/services/melt_value_service.dart:1-256`
  - `lib/screens/catalog/catalog_browse_screen.dart:155-170,1090-1170`
  - `assets/catalog/catalog_public_v1.json` (3,202 records; image hosts and gaps counted)
  - callers of `parseFaceValue`
  - `test/catalog_chunk1_face_value_and_card_test.dart`
  - `numista_backend/main.py:9200-9600`
  - `coin_search_screen.dart:395`, `coin_search_service.dart:151`

## What v1 gets right (verified)
- **F1 closed.** The root cause is right: `main.dart:51` uses `Uri.base`, and the catalog branch checks only `uri.path`; with `/#/catalog`, `path == '/'` and the route sits in `uri.fragment`. The fix matches only `/catalog` and `/catalog/<id>` fragments, so other hash routes (`/#/claim`, etc.) are untouched. It reuses the existing catalog branch unchanged.
- **F2 CSP closed for Wikimedia.** The proposed CSP is byte-identical to `firebase.json:284` plus `https://upload.wikimedia.org https://commons.wikimedia.org https://*.wikimedia.org` in both `img-src` and `connect-src` (checked programmatically). That covers the 166 `upload.wikimedia.org` and 10 `thumb.wikimedia.org` image refs in the catalog JSON. It's the only CSP in the repo (no `web/index.html` meta CSP).
- **F3 root cause is mostly right.** `Dollar (two-coin set)` is the only set denomination in the catalog (`NAC1.CN.US.1D.DIAMONDFLD.2026.XX.26XS.B`). `parseFaceValue` returns 1.0 for it; the precise reason is that `melt_value_service.dart:60` strips the parenthetical before matching. "No face value" for 0 already exists (`catalog_browse_screen.dart:1162`).
- **F5 math is right where it uses the table:** 0.03617 oz (`melt_value_service.dart:12`) × $51.51 = **$1.86**. It also rejects the stale $1.09 ($30 spot). No Firestore write; the optional test coin is left to a separate Eric YES.
- **Note 2 (Coin Search 500) trace is correct:** `coin_search_screen.dart:395` "Definitive Registry", `coin_search_service.dart:151` `GET /api/reference/search`, `main.py:9509` route, and `main.py:9596-9597` blanket `except` → 500. The likely causes named (missing `numista_coins.db`, SQLite error, or the Firestore call in `_get_user_owned_doc_ids`) are plausible and consistent with the code.
- Holds `74611e05`/`41b8bd5f` stated; main pinned; plan-only; gates CoS 95 → SAG 95 → Eric's typed scoped YES.

## Deductions (each one is material)

| # | Pts | Area | Evidence | Why it matters | Exact fix |
|---|---|---|---|---|---|
| E1 | −5 | Correctness: F3 "exact code fix" replaces the whole face-value parser | Plan lines 108–149 replace `parseFaceValue` with a new 35-line function and signature `parseFaceValue(String? denomination)`. Code: `melt_value_service.dart:54-131` takes `(String rawDenom, {int qty = 1})`. It's called with `qty:` at `header_stats_bar.dart:108` and `test/catalog_chunk1_face_value_and_card_test.dart:217`, and has $10,000/$1,000/$500/$100/$50/$40/$25, `$4`/stella, planchet/candareen/multi-denomination guards, leading-number and fraction patterns, and a numeric fallback. | (1) **Compile break**: the `qty:` callers no longer compile. (2) **Wrong values**: `cent` is tested before `two cent`/`three cent`/`5 cent`/`10 cent`/`25 cent`/`50 cent`/`twenty cent`, so all of those return **$0.01**; $100/$50/$1,000 notes, $4 stellas and range strings lose their handling. (3) It undoes the NET-816/NET-837 face-value work that just passed Field Tester on every other denomination, and fails the existing chunk-1 tests. | Keep the existing function. Add one step **before** the parenthetical strip: detect `(\d+|two|three|four|five)[- ]coin set` and set a multiplier, and return 0.0 (No face value chip) for other `set` text. Then `return value * count * multiplier`. Add `Dollar (two-coin set)` → 2.00 to the **existing** chunk-1 test group, and keep all existing cases. |
| E2 | −4 | Execution / safety: no build, deploy or rollback section | No section covers the p7-gate build/deploy, worktree, rollback, or what Eric's YES must name. §5 says only "Deployments require CoS 95, SAG 95, and Eric's typed scoped YES". | You required: deploys to p7-gate only, under Eric's scoped YES; rollback that never redeploys against a hold; PS 5.1 scripts. None of that is specified. There's no `c547b7a0` refusal, no rollback target (the current p7-gate release `a47a275d1eb6b51f` = `a3d7dca2`), no isolated worktree (the shared tree holds other tracks' work), and no statement that the live site/`main` isn't deployed. The F4 stamp has nowhere to run. | Add the PS 5.1 runbook used in the passed NET-816 v5 plan: `Invoke-Native` with `$LASTEXITCODE`; TEMP worktree `git worktree add --detach` at the built SHA; throw on `c547b7a0*` and on any non-p7-gate target; `flutter build web --release`; F4 stamp; `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`; `try/finally` worktree remove + prune. Rollback: RT-A = redeploy `a3d7dca2` (not held) to p7-gate with the same block, or RT-B = leave as is. Never `c547b7a0`, never live/main. Eric's YES names the SHA, p7-gate and the rollback target. |
| E3 | −3 | Correctness: F5 test and display can't work as written | Plan line 188: `calculateMeltValue(weightGrams: 1.24, fineness: 0.90, spotPrice: 51.51)` returns $1.86. Line 191: catalog detail shows melt "based on live silver spot". Code: no `calculateMeltValue` exists; the API is `MeltValueService.compute({metalContent, denomination, spotPrices, …})` (`:135`). 1.24 g × 0.900 ÷ 31.1035 × 51.51 = **$1.848 → $1.85**, not $1.86. $1.86 comes from the table's 0.03617 oz (nominal 1.25 g). The existing chunk-1 half-dime test pins $30 spot → $1.0851. The public catalog runs signed-out, and the plan names no spot source. | The unit test either fails or gets "fixed" to the wrong number, and the catalog-detail melt has no data source, so Field Tester still can't observe F5. | Test `MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half Dime', spotPrices: {'Silver': 51.51})` == 0.03617 × 51.51 (±0.005) in the **existing** chunk-1 test, and keep a $30 case. For the catalog detail, name the spot source a signed-out page can read (e.g. an existing public endpoint, or show melt only when signed in), or drop the display and rely on the unit test plus a separately approved test coin. |
| E4 | −2 | Execution: F4 stamp isn't runnable or reliable | Plan lines 159–171: "e.g. `scripts/build_preview.ps1`". No such script exists at `a3d7dca2`. Relative path `numista_mobile/build/web/version.json`. `if (Test-Path)` skips silently. `git rev-parse` has no exit check. `Set-Content -Encoding UTF8` in PS 5.1 writes a BOM. | If the build is run from another directory, or the file is missing, the deploy goes out **without** `git_commit` and no error, which is exactly the F4 failure. Stamping `HEAD` of the shared tree, not the built worktree, can pin the wrong SHA. | Put the stamp inside the E2 runbook, after `flutter build web` and before the deploy, in the worktree. `$sha = (git -C $wt rev-parse HEAD)`, with an exit check, and assert it equals the approved SHA. Throw if `version.json` is missing. Write UTF-8 without BOM (`[IO.File]::WriteAllText($p, $json, (New-Object Text.UTF8Encoding $false))`). Re-read and assert `git_commit`. |
| E5 | −2 | Correctness: image-gap plan departs from Eric's image rules | Plan lines 95–98: Chunk 2 = "automated synchronization script matching … `gs://numista-reference-library/coins/` and update `catalog_public_v1.json`". | Eric's rule (baton F2; 29/31 Oct) is to fill gaps from the reference library **and his own collection photos** before any placeholder. The step names only the bucket. It ignores the 31 Oct interim rules: GCS read-only for images, and new or matched images staged as a `MANIFEST.csv` `status=PROPOSAL` for review before any catalog change. It doesn't cover the 181 notes and 55 medals that also have no image. | Scope Chunk 2 as: read-only match against `gs://numista-reference-library` **and** Eric's collection photos (name the source/path, UNKNOWN until he points to it); output a `MANIFEST.csv` (`status=PROPOSAL`) on the box for GB CoS/Eric review; only then a separate gated catalog-JSON change. No GCS or Firestore writes. Include notes and medals at lower priority. |
| E6 | −1 | Correctness: F2 host list and post-fix count | Baton: "list every host … report how many coins still have no image after the fix". Catalog image fields also reference `images.metmuseum.org` and `numismatics.org` (1 each). Plan line 96 gives only the current 1,213/1,752. | Two images stay blocked. The "Photos only" count is data-based (2,965 − 1,752 = 1,213), so the CSP fix leaves **1,752 coins with no image**; the plan doesn't say so, and implies the CSP fix moves the number. | Add the two hosts (or state why they're excluded). State: after the CSP fix, 1,752 coins (plus 181 notes, 55 medals) still have no image field; the CSP fix only makes the existing ~176 Wikimedia images render. |

**Total: 100 − 17 = 83, REVISE.**

## Closure matrix

| Item | Status |
|---|---|
| F1 `#/catalog` and `#/catalog/<id>` | **Closed** |
| F2 CSP allows the image hosts | **Mostly closed**: Wikimedia yes; 2 minor hosts missing (E6) |
| F2 gap fill from the reference library + Eric's photos before placeholders | **Open (E5)** |
| F2 remaining no-image count | **Open (E6)** |
| F3 Morgan/Peace set = $2.00, No face value chip otherwise | **Root cause closed; fix as written breaks the parser (E1)** |
| F4 `git_commit` in version.json | **Open (E4, E2)** |
| F5 read-only half-dime check at current spot ($1.86), no Firestore writes | **Math right; test API/weight and display source wrong (E3)**; no-write rule closed |
| Note: "1816" = 0 | Correct: no 1816 record in the 3,202 |
| Note: "Morgan dollar 1881" = 0 | Fix recommendation right (tokenise); analysis partly wrong (advisory 1) |
| Note: Coin Search 500 | Correct trace |
| Holds 74611e05 / 41b8bd5f; main 9f04550a | Stated |
| p7-gate only + Eric's scoped YES; rollback never against a hold; PS 5.1 | **Open (E2)** |
| Branch pin `49e77cf7` | Verified real (docs-only; code = `a3d7dca2`) |

## Advisories (not scored)
1. **Note 1 facts.** The search line is `yearStr.contains(query)`, not `yearStr == query` (`catalog_browse_screen.dart:166`). 1881 Morgans **are** separate records (e.g. `1881-CC Morgan Silver Dollars`, `NAC1.CN.US.1D.MORGANSILV.1881.CC.BASE.Q`), not only variety rows. "Morgan dollar 1881" fails because the whole query is one substring and no name contains "morgan dollar 1881" in that order. The tokenise-all-terms fix is correct and cheap; consider doing it in this round.
2. F1: a fragment with a query (`/#/catalog?item=X`) doesn't match `'/catalog'` exactly. Strip `?…` from the fragment and read `item` from it.
3. F1 has no automated test. Add a small widget/unit test for the effective-path helper (factor it out).
4. Header line 5 pins `49e77cf7` while §0 says Field Tester tested `a3d7dca2`. Both are fine for code, but the build and YES should cite the exact SHA built.
5. The NET-827 plans list `firebase.json` and `melt_value_service.dart` as "not touched". When both tracks are live, sequence or merge carefully so the NET-827 preview build doesn't revert these NET-816 changes.

## Next step
- **REVISE.** AG CoS v5 try 2 of 4 (R2 track attempt 2 of 10). Close E1–E6, keep F1 and the CSP string as they are, and deliver with a fresh SHA that matches the DONE baton.
- **No SAG packet is built,** and nothing is filed or messaged.

## Authority statement
This score **grants no code, git, build, deploy, Firestore, GCS, Stripe or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force; main stays `9f04550a`; Stripe live stays OFF.
