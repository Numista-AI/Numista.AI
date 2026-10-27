# NET-631 ACK — AG CoS v2 IN BUILD (Must-Fix 1-5 + FF-1..3 + Argon74 A-1..A-3)
**From:** AG CoS v2
**To:** Antigravity Desk, Grok CoS, Eric
**Date:** 2026-10-27 ~6:12 PM ET
**Auth:** Eric typed YES ~5:45 PM ET (Standing). No plan reopen.

### Status: ACK & CODING
AG CoS v2 is actively executing FAIL-FIX with all amendments folded in:
1. **A-1 / I-04b:**
   - Remove `main.py:7589-7590` 26SQRP fee zeroing.
   - Set `doc["allocated_fees"]` and `doc["shipping_fee"]` to `allocated_fee` **BEFORE** `enrich_us_mint_item(doc)` (~line 7714).
   - Hub parent 26SQRP Fee = $9.95, child landed unit cost stays $1.80 ($45.00 total for 25 coins).
   - Line 7718-7719 `pack_expanded` zeroing clause removed for review item docs.
2. **A-2 CORS & Images:**
   - Update `numista_backend/cors_reference_library.json` and live GCS bucket `gs://numista-reference-library` to include preview origin (`https://numista-vault--p7-gate-8avtpz22.web.app` and preview patterns).
   - Dual-read image keys in `my_collection_screen.dart` inspector & cards (`primary_image_url`, `photo_urls` fallbacks).
3. **A-3 Valuation & Metal Content:**
   - Dual-read `_buildMetricStrip` at `my_collection_screen.dart:3823` across 4 value keys (`AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, `estValue`).
   - Catalog 26RJ: ensure `metal_content: Cupronickel Clad` stamped so set_pricing doesn't return "Unvaluable - Metal unspecified".
   - Stamp 4 value keys baseline ($124.50 fill-missing-only) + `enrichment_status = "enriched"`.
   - Wire `BackgroundTasks` async enrich worker on `commit_reviews` (skip Greysheet on sets/rolls).

Deploying strictly to **preview p7-gate** (Cloud Run tag `p7gate` + Hosting `p7-gate`).
Origin/main is strictly locked. Report PREVIEW_READY upon test & deploy completion.
OVER.
