# ACK RADIO NET-837: Catalog Chunk 1 Writer (`9bbe20e4`) — Delivered `v2.1` (Attempt 2 of 4)

- **From:** Catalog Chunk 1 Writer (`9bbe20e4-a0d5-4a25-b16a-f616630ad4bb`)
- **To:** Grok Bot CoS (`GROKCOS`), Task Master, Stand Alone Grok (`SAG`)
- **Filed DTG:** `2026-11-07T16:08:00-05:00` (4:08 PM EST, America/New_York — real filing clock)
- **Authority:** `RADIO_NET-837_GROKCOS-to-CHUNK1WRITER-9bbe20e4_REVISE-816-CHUNK1-v2.1_20261107.md` & `COS_SCORE_NET-816_CATALOG_CHUNK1_v2.0_20261107.md` (68/100 FAIL)
- **Deliverable:** `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.1.md` + `BATON_NET-816_GROKCOS_REVIEW_CATALOG_CHUNK1_v2.1_20261107-1608.md`
- **Attempt Counter:** **Attempt 2 of 4** (same writer `9bbe20e4`; AG CoS v4 lineage kept separately)

## Summary of All 7 CoS-68 Must-Fixes Closed in `v2.1`

1. **Landing path (§3, §7):** Added **Prerequisite Commit 1** on `p7-v8.9` porting the 12-file Catalog transitive closure from `b0b058087f1492244a0c0b769e126b38ac1ba06c` (`lib/screens/catalog/*`, `lib/services/catalog/*`, `lib/widgets/catalog/*`, `assets/catalog/catalog_public_v1.json`, `test/catalog_browse_test.dart`, `test/nac_code_parser_test.dart`) plus `git apply`-verified diffs for `numista_mobile/pubspec.yaml` (`- assets/catalog/`) and `numista_mobile/lib/main.dart` (`/catalog` route). Verified all external dependencies (`url_launcher`, `web`, `flutter`, `flutter_test`) on `origin/p7-v8.9`. Updated §7 rollback to cover both Commit 2 and Prerequisite Commit 1 via `git revert`.
2. **Test compile (§6):** Removed the duplicate `r'$50'` key from `const expectedCatalogDenomValues` (now contains the exact **66 unique non-null `denomination` strings**, asserted `expectedCatalogDenomValues.length == 66`, plus `seenPairs.length == 71` across all 71 `(type, denomination)` pairs).
3. **Widget finders (§6):** Scoped card text finders to `find.descendant(of: find.byType(GridView), matching: ...)` so `initialQuery` in `_searchController` (`catalog_browse_screen.dart:44, 505-506`) never double-matches.
4. **Caller blast radius (§4.D, §6):** Audited all 5 production call sites (`home_dashboard.dart:300`, `header_stats_bar.dart:108`, `melt_value_service.dart:141, 146, 200`), documented user collection face-value and melt-value movements with concrete before/after examples, and added regression tests for `qty`-weighted `usdFaceSum` and `MeltValueService.compute`.
5. **Face-value semantics (§4.A, §4.C, §6):** Added early guard in `MeltValueService.parseFaceValue` returning `0.0` (`'—'` on card) for multi-denomination sets (`'$100/$50/$25/$10 platinum'`, `'$50/$25/$10/$5 gold'`, `'$1, $2, $5, $10 (uncut sheet)'`), ranges (`'3¢–50¢'`), unstruck planchets (`'50 cent coin planchet'`, `'Planchet for 1 Cent Coin'`), and non-USD units (`'3.6 Candareens'`).
6. **AI-estimate chip (§4.B, §5):** Aligned `_CatalogCard` with NET-817's production `'AI Estimated Value'` key (`item['AI Estimated Value'] ?? item['ai_estimated_value']`) and replaced the unbacked `'Value pending AI estimate'` promise on static catalog entries with honest copy `'Face value \u00b7 No retail estimate'` (`#856404` on `#FFF3CD`, 4.96:1 WCAG AA).
7. **Hygiene (§1, §3, §4, §5):** Verified all 4 unified diffs with `git apply --cached --check` (`exit=0`), corrected counts to **71 `(type, denomination)` pairs / 67 distinct `denomination` values (66 non-null strings + `null`)**, and recorded the `p7-v8.9` tip at `v2.0` filing as `c8c4dbdd`.

OVER, Catalog Chunk 1 Writer (`9bbe20e4`)
