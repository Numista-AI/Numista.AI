# EXECUTE_DONE — NET-678 (AG CoS v4: NET-647 Mint FAIL-FIX R2.6 Executed & Deployed to `p7-gate`)

- **From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **To:** Field Tester, Grok Bot CoS, Grok Desk, Stand Alone Grok (SAG), Argon, Eric
- **Date / Time:** 2026-10-31 19:42 EDT
- **Re:** `EXECUTE_AG-COS-V4_NET-673_NET-647-R2.6_20261031-1840.md` & `WAKE_AG-COS-V4_NET-675_LIFT-HOLD_7-UPLOADS_20261031-1900.md`
- **Execution Target:** Branch `p7-v8.9` ONLY; Firebase Hosting Preview Channel `p7-gate` ONLY
- **Live Preview URL:** https://numista-vault--p7-gate-8avtpz22.web.app
- **Git Commit:** `33076f6af727c49a020da0d2d4e96a9560d002d6` (pushed to `origin/p7-v8.9`)
- **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF. Zero commits or pushes to `dev` or `main`.

---

## 1. Executive Summary & Verification Outcomes

All 11 surgical fixes approved in Plan R2.6 under Founder typed YES ("YES to approve EXECUTE for NET-647 R2.6.") have been implemented, verified, and deployed to preview channel `p7-gate`:

1. **Rule 8 Verification (Exit Code 0):**
   - **Flutter Analyzer:** `cd numista_mobile; flutter analyze --no-pub` -> **0 issues found (ran in 8.3s, exit code 0)**.
   - **Flutter Test Suite:** `cd numista_mobile; flutter test` -> **652/652 tests passed across all 41 test files (ran in 32s, exit code 0)**.
     - Includes new dedicated unit test `test/format_currency_test.dart` (7/7 passed) asserting exact commercial half-up rounding for all currency divisions.
   - **Backend Regression Tests:** `python -m pytest numista_backend/tests/test_us_mint_catalog.py numista_backend/tests/test_bulk_update.py` -> **13/13 passed in 15.08s (exit code 0)**.

2. **Clean Web Build & Version Stamping:**
   - Compiled release assets via `flutter build web --release` (Exit code 0, 121.7s).
   - Stamped `build/web/version.json`:
     ```json
     {
       "app_name": "numista_ai",
       "version": "8.18.15",
       "build_number": "81818",
       "package_name": "numista_ai",
       "git_commit": "33076f6af727c49a020da0d2d4e96a9560d002d6",
       "build_timestamp": "2026-10-31T23:37:00Z",
       "channel": "p7-gate"
     }
     ```
   - Deployed to channel `p7-gate`: `https://numista-vault--p7-gate-8avtpz22.web.app` (version `5e69b75858b8cfa6`).
   - Verified live HTTP 200 probe against `https://numista-vault--p7-gate-8avtpz22.web.app/version.json` returning exact commit `33076f6af727c49a020da0d2d4e96a9560d002d6`.

---

## 2. 7 Official US Mint Asset Uploads (NET-675 Compliance)

Per NET-675 lifted hold, the 7 official US Mint images were uploaded to `gs://numista-reference-library/reference_library/us_mint_official/2026_products/` using `--no-clobber`. Zero existing objects deleted or renamed:

| SKU | GCS Target Path | Resolution | MD5 Hash | SHA256 Hash |
| :--- | :--- | :--- | :--- | :--- |
| **26SQRP** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp` | 1000x875 | `dfeee8a47f0f7d572c3a4a5c4411a9c0` | `6650b8d66a312cc882c5c853a5fa918ddec2f87a10909ac498f3dd740d0070b0` |
| **26XL** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26xl___a.webp` | 1200x1050 | `403cc019a7a0b0cb00d8f01445abd07a` | `186f565d92bb0879b187d184f59e330b8759e1499b7f5b380a139c15927a4e2f` |
| **26EA** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26ea_a.webp` | 1200x1050 | `790d13287d20ce22b308a27d4efc6199` | `06058e5fa96583e584c90226cb8a12dd0a094457221a90c87546029eabdedb50` |
| **26XE** / **26XF** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp` | 1200x1050 | `96290c2d7393d4a1313db619d784b320` | `8bbca2aea052d24e4f9dd3b2efc1eb9b32f41995814167f99ef9ef233cd1942a` |
| **26RG** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26rg_b.webp` | 1200x1050 | `f6c94fcbdea794f206ccaa7f8ee17de6` | `8dcad07b31a340192f512c5629211fd7254ebe9a23c8f86d2d995dd18ba8c3bd` |
| **26RJ** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp` | 1200x1050 | `31a48b04947cc97d6780a4633aad91de` | `1abe1df8545e5a60083d2497e46af4afd8dfeeb3b41ec4b5fe690be03ffa1819` |
| **26GC** | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp` | 1200x1050 | `4ec332f7878aa432c4730cd0d328e662` | `bc612efa2cc59a2df84d8a72781081a0755b4d22e0d5c6bb71c566b3fa36c427` |

*Note:* `26xh_image_3.jpg` was also uploaded as lowercase twin in 2026_products.

---

## 3. Interim Storage Intake Manifest (NET-674 / NET-675 Compliance)

Per Interim Image Storage Rules line 56:
- **Intake Staging Path:** `image-intake/ag-cos-v4/coins/`
- **Laptop Mirror Path:** `1 NUMISTA.AI/Coin Images/_INTAKE/ag-cos-v4/coins/`
- **Manifest:** `MANIFEST.csv` generated and staged in both paths with `status=PROPOSAL`, containing columns: `proposed_name, side, unique_side, category, source_page_url, image_url, license, credit, accession_or_sku, resolution, sha256, added_by, date, status`.

---

## 4. Code & Architecture Fixes Executed

1. **`numista_backend/services/us_mint_catalog_service.py`:**
   - Canonical CDN URLs wired for all 11 SKUs.
   - `calculate_mint_pricing(raw_line_total, qty)`: Implemented string-based `Decimal(f"{float(clean_total_str):.2f}")` with commercial `ROUND_HALF_UP` integer cents contract.
   - Normalization aliases added (e.g. `2026AIIA` aliased to `2026-AI-IA`).
2. **`numista_backend/main.py` (`bulk_update_reviews`):**
   - Added canonical field normalization mapping `KEY_ALIASES = {"Storage Location": "storage_location", "storage_location": "storage_location"}`.
   - Strict whitelist: `allowed_canonical_keys = {"storage_location", "condition", "notes", "status"}`.
   - Dual-field persistence: writes both `storage_location` and legacy `Storage Location` into Firestore review doc so older query paths remain compatible.
3. **`numista_mobile/lib/screens/review_hub_screen.dart`:**
   - Implemented `ReviewHubScreen.formatCurrency(num amount)`: String-based parser analyzing 4 decimal places with `ROUND_HALF_UP` on digit 3, with negative value guard. Top-level alias `formatCurrency(amount)` provided for state scope.
   - Replaced direct client `FirebaseFirestore.instance...update` on both coin dialog Save and Save+Commit with `POST /api/review/bulk_update` via `HttpAuthClient`.
   - Updated bulk edit dialog to use canonical `'storage_location'`, dropped `'Cost'` and `'Purchase Date'` from bulk dialog to satisfy money field security whitelist.
   - Updated review queue card display to use integer cents contract `unit_cost_cents` -> `unit_cost` -> `line_total / cleanQty` -> formatted with `formatCurrency`.
4. **`numista_backend/scripts/backfill_review_mint_pricing.py`:**
   - Dry-run executed against `users/eric.seaman@yahoo.com/review_queue`.
   - Output CSV: `numista_backend/output/backfill_mint_pricing_before_after.csv`.
   - Confirmed 0 Firestore writes. `--apply` remains disabled awaiting separate explicit Founder typed YES.

---

## 5. Baton Handoff

- **Baton Passed To:** **FIELD TESTER**
- **Action Required:** Live regression re-test of NET-647 US Mint receipts on preview channel `p7-gate` (`https://numista-vault--p7-gate-8avtpz22.web.app`):
  1. Verify all 11 Mint thumbnails display clear, genuine 2026 images without placeholders.
  2. Verify 25-coin roll unit cost displays exactly `$2.44 each` (not `$2.40` or fractional cents).
  3. Verify 2-coin set unit costs display exact commercial half-up rounding (e.g. `$32.49 each`, `$84.50 each`).
  4. Verify changing Storage Location saves via backend `POST /api/review/bulk_update` and persists cleanly.
- **Standing Gate:** `NET-646 v3.3` starts ONLY after Field Tester PASS.
- **OVER.**
