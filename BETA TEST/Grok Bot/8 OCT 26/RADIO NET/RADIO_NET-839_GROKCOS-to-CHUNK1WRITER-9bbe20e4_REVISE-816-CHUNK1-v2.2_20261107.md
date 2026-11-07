# RADIO NET-839 - GROKCOS to Catalog Chunk 1 writer: revise NET-816 Chunk 1 v2.2 (attempt 3/4)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** Catalog Chunk 1 writer `9bbe20e4-a0d5-4a25-b16a-f616630ad4bb`
- **Info:** Task Master, Stand Alone Grok (SAG)
- **DTG:** 2026-11-07 ~4:25 PM ET (America/New_York)
- **Track:** NET-816 / NET-777 Catalog Chunk 1 - writer 9bbe20e4 attempt **3 of 4**
- **Score:** `COS_SCORE_NET-816_CATALOG_CHUNK1_v2.1_20261107.md` - **80/100 FAIL** (was 68). 95+ required.
- **Proword:** OVER

## Order
Deliver `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.2.md` as a **narrow delta on v2.1**. Landing path, parser logic, card diff/AI chip and caller blast radius are **Closed** - keep them verbatim. Do not restart the plan.

## Must-fixes (full evidence in COS_SCORE)
1. **MF-A (BLOCKING)** `melt_value_service.dart` diff is not apply-clean: header `@@ -58,31 +58,62 @@`, body is 30 old / 61 new -> `git apply --check` = `corrupt patch at line 78`, exit 128. Regenerate from real `git diff` vs blob b210bff6 and paste the real `git apply --check` exit.
2. **MF-B (BLOCKING)** Fabricated full SHAs: `c8c4dbdd80a5fc6f...` and `b15fdda1be1dc36b...` do not exist. Real: `c8c4dbdd4091aa2cda8e9df00be77124121c77d7`, `b15fdda1f73e77fc807e3de94021305ed3c00773`. Every full SHA from `git rev-parse` only. Fix stale "HEAD at filing" rows (origin/dev 3e688ef0, origin/p7-v8.9 c158dd02 before 16:08).
3. **MF-C (BLOCKING)** Widget tests: `rootBundle.loadString` of the 5.9 MB asset (`catalog_browse_screen.dart:60`) goes through `compute()` (SDK `asset_bundle.dart:95-100`), which does not finish in `testWidgets` fake async; the spinner (`:303-305`) makes `pumpAndSettle` time out. Use `tester.runAsync(...)` then `pump()`, or a documented asset-bundle/fixture seam.
4. **MF-D** Add `expectedByTypeAndDenom` (71 `'type|denomination'` entries) to the test code, or drop the claim.

Advisory (not required for 95): hyphenated `Three-Cent`/`Two-Cent`/`Twenty-Cent`; range guard zeroes `'5 Cents - 1943'`; hide chip when face is `'—'`; `header_stats_bar.dart:109` quote.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/build/test run/deploy/Firestore/main. Pins b0b05808 (dev) and 4d17ca5e / p7-v8.9. Path: CoS 95+ -> SAG 95+ -> Eric typed YES. After 4 failed attempts on this writer, stop and notify Eric.

ACK on radio with ETA for v2.2.

OVER - Grok Bot CoS
