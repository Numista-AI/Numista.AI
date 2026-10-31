# BATON: NET-647 MINT FAIL-FIX — FIELD TESTER (LIVE RE-TEST ON P7-GATE)
- **From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **To:** Field Tester
- **Date / Time:** 2026-10-31 19:42 EDT
- **Baton Holder:** **FIELD TESTER**
- **Channel Under Test:** https://numista-vault--p7-gate-8avtpz22.web.app
- **Target Commit:** `33076f6af727c49a020da0d2d4e96a9560d002d6` (branch `p7-v8.9`)
- **Version Stamp:** `8.18.15` (build `81818`, channel `p7-gate`)

## Field Tester Test Objectives:
1. **11 US Mint SKU Thumbnails:**
   - Verify all 11 Mint review cards load clean, genuine 2026 obverse/reverse/lens images from `gs://numista-reference-library/reference_library/us_mint_official/2026_products/`.
   - Confirm zero placeholder, blank, or broken image cards.
2. **25-Coin Roll Pricing Precision:**
   - Verify 25-coin roll unit cost displays exactly `$2.44 each` (not `$2.40` or fractional cents).
3. **2-Coin / Set Pricing Precision:**
   - Verify 2-coin items display exact commercial half-up rounding (e.g. `$32.49 each`, `$84.50 each`).
4. **Storage Location Single-Write Path:**
   - Edit Storage Location in review dialog and confirm persistence via `POST /api/review/bulk_update`.
   - Confirm dual-field persistence (`storage_location` and `Storage Location`).

## Standing Gate:
- `NET-646 v3.3` starts ONLY after Field Tester files PASS.
- Locks intact: `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF.

**OVER.**
