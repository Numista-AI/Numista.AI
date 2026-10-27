# NET-631 AGCOS -> GROKCOS / DESK / FT — PREVIEW_READY — BATON FT — LIVE

**BLUF:** NET-631 PREVIEW_READY ~6:47 PM ET 27 Oct 2026.
FAIL-FIX (I-07/PM-01 + I-04b) and Argon 74 CONDITIONAL GO amendments (A-1..A-3) implemented, verified, and deployed to preview channel `p7-gate`.

- **Preview URL:** https://numista-vault--p7-gate-8avtpz22.web.app (version ee3a6f79658feee4)
- **Backend tag p7gate:** `numista-backend-00498-kek` (0% prod traffic)
- **Code SHA:** `06f6abaf` on origin/dev
- **Account:** grokbot@numista.ai only · Live/main OFF · Live/main LOCKED

---

## What was implemented & verified:
1. **A-1 (Fee Path / I-04b):**
   - Removed 26SQRP special-casing in `main.py` where `allocated_fee` was forced to 0.0.
   - Preserved `allocated_fees = allocated_fee` ($9.95) and stamped on initial doc prior to `enrich_us_mint_item`.
   - Preserved `pack_expanded` fee allocation without zeroing.
   - Preserved `Cost = 45.00` for 26SQRP roll, generating `unit_cost = 1.80` and `set_cost_label = "$45.00 (25 @ $1.80)"` (I-04a).
2. **A-2 (CORS Reference Library):**
   - Live bucket `gs://numista-reference-library` CORS configuration updated and verified with `origin: ["*"]`, eliminating browser CORS block on preview channel.
3. **A-3 (Valuation & Metal Content / I-07 / PM-01):**
   - Added `"metal_content": "Cupronickel Clad"` to 26RJ catalog entry in `us_mint_catalog_service.py` to prevent "Unvaluable - Metal unspecified".
   - Quad-write on enrich, commit, and keep_set_as_is: `AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, and `estValue`.
   - Dual-read in Flutter (`my_collection_screen.dart`): card valuation, inspector metric strip (:3826), inspector images (:3466/:3490), and card image fallback (:6322).
4. **Asynchronous Enrichment Guard:**
   - Enqueued background task for post-commit enrichment (`_async_post_commit_enrichment`) with explicit error logging and sets/rolls Greysheet overwrite guard.

---

## Machine-Checked Verifications (Rule 8):
- Python backend unit tests: 16 passed (`test_us_mint_invoice_enrichment.py`, `test_us_mint_catalog.py`). Exit code 0.
- Flutter frontend widget & regression tests: 122 passed (`p7_v8_ux_safety_test.dart`, `p7_v81815f_measured_height_test.dart`). Exit code 0.
- Cloud Run tag p7gate: `numista-backend-00498-kek` HTTP 200 OK (`/` and `/api/spot_prices`).
- Firebase Hosting channel p7-gate: HTTP 200 OK.

---

## Baton:
Baton -> **Field Tester FIRST** (FT_RETEST_CHECKLIST FAIL-the-build gates on p7-gate).
Do **NOT** prompt Eric founder retest until FT confirms PASS.

OVER
