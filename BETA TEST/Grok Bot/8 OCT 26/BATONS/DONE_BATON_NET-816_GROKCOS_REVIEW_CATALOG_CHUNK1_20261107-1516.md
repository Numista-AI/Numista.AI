# BATON: NET-816 / NET-777 Public Catalog Browse — CHUNK 1 Plan Review (`v2.0`)

- **From:** Fresh Antigravity Plan Writer (Catalog Chunk 1)
- **To:** Grok Bot CoS (`GROKCOS`), Task Master, Stand Alone Grok (`SAG`)
- **Filed DTG:** `2026-11-07T15:16:00-05:00` (3:16 PM EST, America/New_York — real filing clock)
- **New-Writer Attempt Counter:** **Attempt 1 of 4** (4-try rule)
- **Prior Lineage (kept separately, not erased):** AG CoS v4 (`ba2bfdb2`) = 10+ attempts (parked); `v1.10` = 48/100 FAIL; `v1.11` = 58/100 FAIL.
- **Deliverable:** `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.0.md`
- **Authority:** `BETA TEST/Grok Bot/8 OCT 26/OUTBOX/STARTER_CATALOG_FRESH-AG_CHUNK1_20261107.md`, `BETA TEST/Grok Bot/8 OCT 26/BATONS/RADIO_NET-831_GROKCOS-to-AGCOS_REVISE-816-v1.12_20261107.md` (items 1–2), and `BETA TEST/Grok Bot/8 OCT 26/BATONS/COS_SCORE_NET-816_CATALOG_v1.11_20261107.md` (lines 14, 17, 20, 23).

## Scope & Summary of Chunk 1 (`v2.0`)

1. **Verified Pins Table (§1):**
   - Re-verified `dev` (`b0b058087f1492244a0c0b769e126b38ac1ba06c`), `origin/dev` (`b15fdda1` ancestor of current `origin/dev` `afbbbd45950c459c04a1e82b437dd346c522c3da`), `p7` (`4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` ancestor of current `p7-v8.9` `5fbff9afa23221e1bc9dc719f786618ac642cf03`), and locked `origin/main` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`).
   - Verified target file blob hashes across branches via `git rev-parse`.
2. **Must-Fix #1 (`RADIO_NET-831` #1 — `MeltValueService.parseFaceValue` In-Place Patch & Full Catalog Re-Count, §3):**
   - Planned in-place unified diff to `numista_mobile/lib/services/melt_value_service.dart:53-99` (not wrapped).
   - Evaluates leading numerics and fractional dollars first (`N Dollars`, `1,000 Dollars`, `10,000 Dollars`, `2 1/2 Dollars`, `G$2½`, `3 cents` / `3 Cents`, `$1000`), checks `$10,000`/`$1,000` before `$100`, checks `half dime` (`0.05`) before `dime` (`0.10`), and checks `three cent` / `3 cent` (`0.03`) and `five cent` (`0.05`) before `cent` (`0.01`).
   - Independently re-counted all 3,202 entries (70 distinct `(type, denomination)` pairs) in `catalog_public_v1.json`: confirmed all **103** reported mis-parses (`Half dime` ×35, `3 cents`/`3 Cents` ×9, `N Dollars` ×58, `$1000` ×1), plus **16** `'G$2½'` Quarter Eagle entries (`$2.00` → `$2.50`) and **2** non-USD/range strings (`'3¢–50¢'` ×1, `'3.6 Candareens'` ×1) guarded to `0.0`.
   - Stated medal display explicitly: all 56 medals (`type == 'medal'`, `denomination == null`) have no legal-tender face value and render `'No face value'` on `_CatalogCard` without `'Face Value N/A'` or `'Value pending AI estimate'`.
   - Re-measured WCAG 2.1 contrast of `#856404` ($L = 0.141097$) on `#FFF3CD` ($L = 0.897690$) as **4.96:1** (`4.9592:1`, WCAG AA pass).
3. **Must-Fix #2 (`RADIO_NET-831` #2 — Minimal `_CatalogCard` Diff, §4):**
   - Planned minimal unified diff to `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`: adds `import '../../services/melt_value_service.dart';` at `:1-5`, preserves lines `1122-1149` (existing title styling, metadata styling, and the `1142-1149` `'type photo (date may differ)'` block) unchanged, and appends the face-value / medal status row after `:1149`.
4. **Planned Tests (§5):**
   - Preserves existing 91-line `numista_mobile/test/catalog_browse_test.dart` untouched.
   - Plans new test file `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` (package `numista_ai`) covering all required denomination strings, full 3,202-entry `catalog_public_v1.json` regression verification (`0` mis-parses), and widget tests asserting `'type photo (date may differ)'` when `isTypeImage` is true and `'No face value'` on medals.

## Standing Locks
- **PLAN ONLY.** Zero code edits, builds, test runs, deploys, Firestore writes, or bucket uploads executed.
- Target: `p7-v8.9` (`p7-gate`) only. `origin/main` locked at `9f04550a`. Stripe OFF. Alerts only, no spend caps.
- Approval chain: GB CoS ≥95 → SAG ≥95 → Founder Eric's typed `YES`.
