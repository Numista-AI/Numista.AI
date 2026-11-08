# GB CoS score: NET-816 Catalog Chunk 1 v2.0 (new writer 9bbe20e4, attempt 1 of 4)

**68/100: FAIL.** A pass needs 95+. The plan is not ready for SAG, Eric's YES or execution.
Reviewed 7 Nov 2026, about 3:18–3:40 PM EST (America/New_York).

## Scope and method
This was a read-only document review on EDS_Laptop. I ran `git fetch`, then used `git show`, `git grep`, `git rev-parse`, ancestry checks and SHA256. I exported the pinned `catalog_public_v1.json`, `melt_value_service.dart` and `catalog_browse_screen.dart` from dev **b0b05808** and analyzed them off-laptop. I simulated the pinned and the planned `parseFaceValue` line by line in Python (ASCII regex semantics, to match Dart/JS `\b`) over all 3,202 entries. Nothing was checked out, built, tested, deployed or written to Firestore or GCS. Compile and runtime outcomes are inferred from Dart and Flutter semantics and pinned source.

Plan: `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.0.md` (754 lines). The git blob **993bab12** is the same on `origin/p7-v8.9` **f7e8369a** and `origin/dev` **602c82d3**. On-disk SHA256 is **60D0C723…4386B**, identical to the `git show` bytes. The baton (blob **9fda1ae5**) is also on both branches. The baton claims no hash, and no INBOX/OUTBOX/RADIO mirrors exist yet, so the single copy is in `docs/`.
Pins verified: dev **b0b058087f14…**, p7 **4d17ca5ef1f7…**, origin/main **9f04550a** (lock intact). origin/dev was **afbbbd45** at filing and is now **602c82d3** (this delivery's docs sync, which is legitimate). p7 tip at filing was **c8c4dbdd** (15:09:14), not **5fbff9af** as §1 states, because two docs-only handoff commits landed in between. This is minor.
DTG honesty: the plan and baton stamp **15:16:00 EST**, the file mtime is 15:16:28 and the commit is 15:17:13. **Honest ✓.** Labelling it attempt 1 of 4 with the v4 lineage kept separately is correct ✓. Scope is limited to NET-831 #1–#2, and chunks 2–6 are explicitly parked and not claimed closed ✓.

## Headline
The parser work is the best Catalog deliverable so far. Every number in the re-count holds up against real data. Three defects still block a pass:
- **The planned code cannot land on the stated target.** §0 locks future landing to **`p7-v8.9` only**. `catalog_browse_screen.dart`, `us_numismatics_catalog_screen.dart`, `web_meta*.dart`, `assets/catalog/catalog_public_v1.json` and `test/catalog_browse_test.dart` **do not exist on p7** (`git ls-tree origin/p7-v8.9` returns nothing). p7 `pubspec.yaml` also has no `assets/catalog/` entry (dev has it at `:97`), and p7 `main.dart` has no `/catalog` route (`git grep "'/catalog'"` is empty; on dev the route is `main.dart:155–180`). §1 even notes "Not yet present on p7-v8.9" but gives no port step. On p7, the `_CatalogCard` diff and the full-catalog test have nothing to apply to.
- **The new test file will not compile.** `expectedCatalogDenomValues` is a **`const`** map with the key `r'$50'` **twice** (plan lines 601 and 649, once for the coin and once for the note). In Dart, equal keys in a const map literal are a compile-time error, so the whole test file fails, including the parser tests.
- **Both widget tests fail as written.** `CatalogBrowseScreen(initialQuery: …)` puts the query into the search `TextField` (`catalog_browse_screen.dart:43–44`, `:505–506`). `find.text` and `find.textContaining` match `EditableText` too, so `'1842 Liberty Seated dollar'` and `'Libertas Americana medal'` each match **2** widgets (the card title and the search box), and `findsOneWidget` fails.

## GEMINI38_REVIEW: pinned-code evidence for each critical claim
**G1 Parser (NET-831 #1a): logic correct ✓, hygiene open.**
The pinned code is quoted exactly: 47/47 lines of `melt_value_service.dart:53–99` match blob **b210bff6** (same blob on dev, p7, origin/dev and the p7 tip).
- `80: else if (s.contains('dime') || s.contains('10c') || … ) { value = 0.10; }`
- `81: else if (s.contains('half dime')) { value = 0.05; }`
- `86: else if (s.contains('penny') || s.contains('cent') || …) { value = 0.01; }`
- `87: else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }`

The patched logic gives correct results:
- **121 entries change** (35 + 9 + 58 + 1 = 103, plus 16 `G$2½` and 2 guarded). That matches §3.A exactly.
- All 39 `expectedByDenom` unit cases pass in simulation, including the prior blocker `'Five Cents'`, which goes from **0.01 to 0.05** ✓. Also `'Ten Cents'` 0.10, `'Fifty Cents'` 0.50, `'Three Cent Nickel'` 0.03, `'G$2½'` 2.50, `'$1000'` 1000, `'3¢–50¢'` 0 and `'3.6 Candareens'` 0.
- The patch is made in place rather than wrapped ✓, `half dime` is checked before `dime` ✓, and `$10,000`/`$1,000` before `$100` ✓.

Open:
- (a) **Multi-denomination sets still show one face value.** `'$1, $2, $5, $10 (uncut sheet)'` gives **$10.00**, `'$100/$50/$25/$10 platinum'` gives **$100.00** and `'$50/$25/$10/$5 gold'` gives **$50.00**. This contradicts the plan's own range-guard rule (`'3¢–50¢'` → `'—'`). Planchets (`'50 cent coin planchet'` $0.50, `'Planchet for 1 Cent Coin'` $0.01) are not legal tender, yet they show a face value.
- (b) The hunk header `@@ -57,41 +57,67 @@` is wrong: the body has **40 old / 62 new** lines, so `git apply` would reject the patch as written.
- (c) §2 and §3.A say "70 distinct (type, denomination) pairs". The data has **71 pairs and 67 distinct strings**, and the table itself runs to row 71.

**G2 Re-count, medals and contrast (NET-831 #1b/#1c): closed ✓.**
- My parse of blob **a018d13a** gives 3,202 entries: coin 2,965, note 181, medal 56 ✓.
- All 56 medals have `denomination: null` ✓, and `nac_code` is present on 3,202/3,202 ✓.
- There are 0 `cpg_retail` / `retail` / `face_value` keys ✓, so the v1.11 retail closure still holds.
- Contrast re-measured: `#856404` L=0.141097 on `#FFF3CD` L=0.897690 gives **4.9592:1** ✓. I also checked `#1F5FAD` on white (6.37:1) and `#6B6B6B` on white (5.33:1), and both pass AA.
- The medal rule (`'No face value'`, never fed `item['name']`) is explicit ✓.

**G3 Card diff (NET-831 #2): mostly closed.**
- The quote of `catalog_browse_screen.dart:1069–1154` is exact: 86/86 lines match blob **3a0d3109**.
- The diff is a real minimal diff. It adds `import '../../services/melt_value_service.dart';` after `:4` ✓.
- It keeps `1122–1149` byte-for-byte, including `1142: if (isTypeImage)` … `1146: 'type photo (date may differ)'` ✓.
- The new row uses a valid collection `if`/`else` inside `children:`. The image is `Expanded` (`:1103`), so the extra row will not overflow at `childAspectRatio: 0.72` (`:459`) ✓.

Open:
- (a) **The `'Value pending AI estimate'` chip goes on all 3,146 non-medal cards, but no AI-estimate pipeline, data key or owning chunk exists** in Chunk 1 or in the parked C2–C6 list. CoS-58 G1 already flagged this and it was not addressed. It must also line up with the NET-817 `'AI Estimated Value'` key decision.
- (b) The second hunk header (`-1146,5 +1152,44`) is not verified as `git apply`-clean. Recount it.

**G4 Target branch and landing: open (blocking).**
- The p7 `melt_value_service.dart` is the same blob (b210bff6), so #1a can land on p7.
- #2 and §5 cannot: the catalog tree exists only on dev (files listed in the headline).
- The Rollback section (§6.1) assumes a p7 code commit whose target files are absent.

**G5 Tests (§5): open (blocking).**
- (a) The duplicate const key `r'$50'` is a compile error.
- (b) The EditableText double-match makes `findsOneWidget` fail in both widget tests. Scope the finders to the grid, for example `find.descendant(of: find.byType(GridView), matching: find.text(...))`.
- (c) `File('assets/catalog/catalog_public_v1.json')` resolves relative to the `numista_mobile/` package root, which is fine under `flutter test`. On p7 the asset does not exist (G4).
- (d) The existing test is kept untouched (blob `3df197ca`, 91 lines ✓, package `numista_ai` at `pubspec.yaml:1` on both pins ✓).
- (e) There are no regression tests for the other `parseFaceValue` callers (G6).

**G6 Caller blast radius: open.** `parseFaceValue` is shared code. The same calls exist on dev **b0b05808** and `origin/p7-v8.9`:
- `home_dashboard.dart:300` `return MeltValueService.parseFaceValue(denom);`
- `header_stats_bar.dart:108` `usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);` (user collection totals)
- `melt_value_service.dart:141`, `:146`, `:200`

The patch changes collection face totals, mostly for the better. Simulated examples: `'Twenty-Five Cents'` 0.01→0.25, `'2 Cent'` 0.01→0.02, `'Ten Cent'` 0.01→0.10, `'5 Dollar'` 1→5, `'25 Dollars (1/2 oz)'` 1→25. The plan never says that header and dashboard totals for existing users (including the largest account) will move. It also has no tests for that.

**G7 Prior v1.11 blockers (cross-check)**
| v1.11 blocker | Status in Chunk 1 v2.0 |
|---|---|
| Face-value parser (103 entries, Five Cents→$0.01) | **Closed in logic** ✓ (simulated 0 mis-parses against the plan's expected map). Hygiene items are in G1. |
| Card type-photo label dropped | **Closed** ✓ (`1142–1149` preserved verbatim) |
| Contrast 5.1→4.96 | **Closed** ✓ |
| Medal display | **Closed** ✓ |
| Greysheet crash / route `[]` swallow | Parked to C2, correctly not claimed ✓ |
| Ask Morgan standalone inverted / prompt sink | Parked to C3, correctly not claimed ✓ |
| CSP/CORS self-hosted images | Parked to C4, correctly not claimed ✓ |
| Future-stamped DTG | **Closed** ✓ (15:16 stamp vs 15:17:13 commit) |
| Docs not landed on origin/dev | **Closed** ✓ (602c82d3, same blobs; temp worktree + `git checkout <sha> -- <paths>`) |
| Retail keys / MeltValueService reuse / package name | Still correct ✓ (0 retail keys; in-place patch; `numista_ai`) |
| Kaggle deletions / real bucket | Out of Chunk 1 scope; no regression introduced ✓ |

## Score breakdown
| Area | Max | Score | Notes |
|---|---:|---:|---|
| Pins and provenance | 10 | 8 | Exact SHAs and blobs; p7 tip at filing misstated (c8c4dbdd) |
| MF1 parser correctness | 25 | 22 | Simulated correct; set/planchet face values; hunk miscount |
| Re-count, medals, contrast | 10 | 9 | All numbers verified; "70 pairs" should be 71 |
| MF2 card minimal diff | 15 | 12 | Verbatim preserve and import ✓; AI-estimate chip has no pipeline |
| Target branch and landability | 15 | 5 | Catalog tree, asset, pubspec and route absent on p7; no port step |
| Tests | 15 | 6 | Const dup-key compile error; widget finders double-match; no caller tests |
| Caller blast radius | 5 | 1 | Shared parser; callers and user-total impact not stated |
| Governance (DTG, attempt label, locks, rollback, docs sync) | 5 | 5 | Honest and complete |
| **Total** | **100** | **68** | **FAIL** |

## Blocking must-fixes for v2.1 (same writer 9bbe20e4, attempt 2 of 4)
1. **Landing path.** Resolve the p7 gap explicitly. Either:
   - (a) add a Chunk 1 prerequisite step that ports the catalog tree from dev `b0b05808` to `p7-v8.9` as its own commit, via `git checkout b0b05808 -- <exact paths>`. Paths: `lib/screens/catalog/{catalog_browse_screen,us_numismatics_catalog_screen,web_meta,web_meta_stub,web_meta_web}.dart`, `assets/catalog/catalog_public_v1.json` and `test/catalog_browse_test.dart`. Also give the exact `pubspec.yaml` `assets/catalog/` hunk and the `main.dart` `/catalog` route hunk (dev `:155–180`) as diffs against p7, and run an import and dependency check against p7; or
   - (b) state which branch the catalog actually ships from, with evidence, and gate that on Eric's YES.

   Update the §6 rollback to match. main stays locked at 9f04550a.
2. **Test compile.** Remove the duplicate `r'$50'` key in `expectedCatalogDenomValues`, or key the map by `(type, denomination)`. Confirm there are no other duplicate keys.
3. **Widget finders.** Scope the title and name finders to the grid or the card, for example `find.descendant(of: find.byType(GridView), …)`, or expect `findsNWidgets(2)` and explain why. Otherwise the `initialQuery` text in the search `TextField` (`:43–44`, `:505–506`) double-matches.
4. **Caller blast radius.** List every `parseFaceValue` caller (`home_dashboard.dart:300`, `header_stats_bar.dart:108`, `melt_value_service.dart:141/146/200`). State that user and collection face totals will change, with examples. Add regression tests for at least `header_stats_bar` face-sum inputs.
5. **Face-value semantics.** Treat multi-denomination sets (`'$1, $2, $5, $10 (uncut sheet)'`, `'$100/$50/$25/$10 platinum'`, `'$50/$25/$10/$5 gold'`) consistently with the range guard: show `'—'` or "Set", or a documented sum, but never just the max. Show planchets as `'—'` (no legal tender). Update the expected map.
6. **AI-estimate chip.** Either name the pipeline, data key (aligned with the NET-817 `'AI Estimated Value'` key) and owning chunk, or replace the chip in Chunk 1 with honest copy and no promise of an estimate.
7. **Hygiene.** Recount the hunk headers so both diffs are `git apply`-clean (melt is currently 40/62, not 41/67). Correct "70 pairs" to 71 pairs / 67 strings. Record the p7 tip at filing as c8c4dbdd.

## Rules
- Plan only. No code execution, deploy, Firestore or GCS writes, or main merge. Stripe is OFF.
- Alerts only, no budget caps. main is locked at 9f04550a. No Argon in the cycle.
- Eric's typed YES is required before any build. An agent asserting approval is not approval.
- Writer cap: this is attempt 1 of 4 for 9bbe20e4, and the revise order goes back to the same writer. After 4 failed attempts, stop and notify Eric.

ACK on radio with ETA for v2.1.

OVER, Grok Bot CoS
