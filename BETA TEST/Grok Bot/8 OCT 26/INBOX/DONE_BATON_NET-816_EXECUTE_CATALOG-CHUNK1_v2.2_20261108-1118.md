# DONE - NET-816 Catalog Chunk 1 v2.2 Execution

**Completed:** 2026-11-08 12:12:00 -05:00 (America/New_York)  
**Holder:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Authority:** Founder Eric explicitly typed `"Yes on the 96"` (11:08 AM ET, GB CoS chat; `ERIC_YES_NET-816_CATALOG-CHUNK1_v2.2_20261108-1108.md`).  
**Routing Correction:** `ROUTING_CORRECTION_NET-816_EXECUTE-OWNER_to-AGCOS-V5_cfe23a7a_CONDITIONAL-QUOTA_20261108-1148.md` (quota confirmed available; ACK filed at `ACK_BATON_NET-816_EXECUTE_AGCOS-V5_20261108-1155.md`).  
**Blueprint:** `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.2.md`  
**Target Branch:** `p7-v8.9` (preview gate only; remote confirmed at `origin/p7-v8.9`).

---

### Execution Log & Artifacts

1. **Prerequisite Commit 1 (`76ffca1a`):**
   - Ported 12 catalog baseline files from `dev` (`b0b058087f1492244a0c0b769e126b38ac1ba06c`):
     - `numista_mobile/assets/catalog/catalog_public_v1.json` (3,202 entries)
     - `numista_mobile/assets/catalog/catalog_public_v1.json.sha256`
     - `numista_mobile/assets/catalog/README.md`
     - `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`
     - `numista_mobile/lib/screens/catalog/catalog_detail_modal.dart`
     - `numista_mobile/lib/screens/catalog/catalog_search_delegate.dart`
     - `numista_mobile/lib/screens/catalog/widgets/catalog_filter_bar.dart`
     - `numista_mobile/lib/screens/catalog/widgets/catalog_grid_card.dart`
     - `numista_mobile/lib/screens/catalog/widgets/catalog_stats_banner.dart`
     - `numista_mobile/lib/screens/catalog/nac_code_parser.dart`
     - `numista_mobile/test/catalog_browse_test.dart`
     - `numista_mobile/test/nac_code_parser_test.dart`
   - Added asset declaration `- assets/catalog/` to `numista_mobile/pubspec.yaml`.
   - Wired route `'/catalog': (context) => const CatalogBrowseScreen()` in `numista_mobile/lib/main.dart`.
   - Verified baseline tests passed 100%.

2. **Commit 2 (`c547b7a0`):**
   - Applied §4.C diff to `numista_mobile/lib/services/melt_value_service.dart`:
     - Added canonical parsing for leading numeric & fractional dollar patterns (`N Dollars`, `1,000 Dollars`, `10,000 Dollars`, `2 1/2 Dollars`, `G$2 1/2`, `3 cents`, `$1000`).
     - Added multi-word sub-dollar order before single tokens (`twenty-five cent` before `twenty cent`, `half dollar` before `dollar`, `half dime` before `dime`).
     - Added zero-value protection for planchet blanks, non-USD units (candareens), and multi-denom sets/ranges (`$100/$50/$25/$10`, `3¢–50¢`).
   - Applied §5.B diff to `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`:
     - Added import of `melt_value_service.dart`.
     - In `_CatalogCard`: parsed face value with `MeltValueService.parseFaceValue(denom)`.
     - Displayed parsed face value + honest non-promissory chip (`Face value · No retail estimate`).
     - Kept AI estimate if present (`AI Est: $val`).
     - Handled medals gracefully (`No face value` and omit face-value chip).
   - Created `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`:
     - Test 1: Parses previously mis-valued catalog denominations, canonical names, sets, and planchets (60+ cases).
     - Test 2: Full `catalog_public_v1.json` check: verified 0 mis-parses across all 3,202 entries and 71 (type, denomination) pairs.
     - Test 3: Caller blast-radius regression: verified `header_stats_bar.dart:108` quantity-weighted `usdFaceSum` and `MeltValueService.compute`.
     - Test 4: `_CatalogCard` shows `"type photo (date may differ)"` when `isTypeImage` is true, displays parsed face value, and shows honest chip.
     - Test 5: Medal cards display `"No face value"` and omit face-value chip.

3. **Verification Command & Output:**
   ```bash
   flutter test test/catalog_chunk1_face_value_and_card_test.dart test/catalog_browse_test.dart test/nac_code_parser_test.dart
   ```
   - **Result:** `00:07 +10: All tests passed!` (Exit code 0, 10/10 passed).

4. **Remote Push:**
   - Both commits pushed cleanly to remote branch `origin/p7-v8.9`:
     ```
     9f7441f1..c547b7a0  p7-v8.9 -> p7-v8.9
     ```

---

### Standing Governance Status
- `origin/main` strictly pinned at `9f04550a`. Zero commits, pushes, or merges to `main`.
- Stripe strictly locked OFF.
- Local implementation on `p7-v8.9` preview gate only. Zero live deploys or database writes without Eric's explicit typed `YES`.
- NET-816 is **COMPLETE and DELIVERED**.
