# NET-630: Argon Review of `ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md` Filed — 74/100 CONDITIONAL GO (3 P0 Root-Cause Gaps Caught) — Baton to GB CoS

- **From:** Gemini 4 Argon (`Numista.Ai Argon` — **THINKING JOBS ONLY**)
- **To:** Grok Bot CoS (`GB CoS`), AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`), Stand-Alone Grok (`SAG`), Desk
- **Date / Time:** 2026-10-27 ~5:48 PM ET
- **Review File:** `ARGON_REVIEW_ERIC_BMINUS_FAILFIX_PLAN_V1_2026-10-27.md` (filed in `BATONS\`, `1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\`, and `INBOX\`)
- **Code / Deploy Status:** **ZERO CODE EDITS, ZERO COMMITS, ZERO DEPLOYS.**

---

## 1. Score & Verdict
- **Score:** **74 / 100 — CONDITIONAL GO**
- **Review Chain:** `AG CoS (Plan.v1) -> Argon (74/100 CONDITIONAL GO) -> GB CoS (NEXT) -> SAG -> Eric typed YES -> EXECUTE preview-only`

---

## 2. Three P0 Root-Cause Gaps Caught by Argon (With Verbatim Code Citations in Review File)

1. **[P0 BLOCKER A-1 — `I-04b` (`26SQRP` Fee `$0.00` on Review Hub)]:**
   - `Fail-Fix Plan.v1` (§2.A.1) only removes `0.0 if doc.get("pack_expanded") else allocated_fee` at `numista_backend/main.py:7718-7719`, assuming `allocated_fee == 9.95`.
   - **Why that still fails:** At **`numista_backend/main.py:7589-7590`**, an explicit branch hardcodes `allocated_fee = 0.0` whenever `26SQRP` is on the invoice!
   - **And watch out for `I-04a` regression:** If you remove `main.py:7589-7590` so `allocated_fee = 9.95`, `landed_cost_basis` at line `7598` becomes `54.95` (`45.00 + 9.95`). Because `doc["allocated_fees"]` was not set before calling `enrich_us_mint_item(doc)` at line `7714`, `us_mint_catalog_service.py:485` sees `alloc_fees = 0.0` and computes `25 @ $2.20` (`$54.95`) instead of `25 @ $1.80` (`$45.00`)!
   - **Fix:** Remove the `26SQRP` `allocated_fee = 0.0` override at `main.py:7589-7590`, set `"allocated_fees": allocated_fee` and `"shipping_fee": allocated_fee` in `doc` at `main.py:7680` **before** `enrich_us_mint_item(doc)` runs at line `7714`, and keep `doc["allocated_fees"] = allocated_fee` / `doc["shipping_fee"] = allocated_fee` after line `7714` (without writing `"Allocated Fees"` since line `8200` pops it).

2. **[P0 BLOCKER A-2 — `I-07` / `PM-01` (`"Image unavailable"`) & `SAG4` (`20 tiles all placeholders`)]:**
   - In `my_collection_screen.dart:3725, 4835`, the string `"Image unavailable"` ONLY renders when `Image.network(activeUrl, ...)` fires `errorBuilder` (`isError: true`).
   - Live HTTP `HEAD` probe against `https://storage.googleapis.com/numista-reference-library/.../26rj_a.jpg` with `Origin: https://numista-vault--p7-gate-8avtpz22.web.app` proved that **`gs://numista-reference-library` CORS (`numista_backend/cors_reference_library.json:1-17`) only allows `https://numista.ai` and `https://numista-vault.web.app` — it blocks `--p7-gate` preview origins!**
   - That is why **both** the `26RJ` hero image (`26rj_a.jpg`) AND **all 20 coin images** in `coin_set_index/uncirculated-coin-set-2026` failed `Image.network` in Flutter Web on `p7-gate`!
   - **Fix:** Update `numista_backend/cors_reference_library.json` and live bucket CORS on `gs://numista-reference-library` to allow `https://numista-vault--p7-gate-8avtpz22.web.app` (or `"*"` for `GET`/`HEAD` on public reference library images, matching `gs://us_mint_coin_images`), plus add `primary_image_url` / `photo_urls` fallback in `_showCoinInspectorDialog` (`my_collection_screen.dart:3467, 3490`).

3. **[P0 BLOCKER A-3 — `I-07` / `PM-01` (`26RJ` Valuation `$124.50` in Card + Coin Inspector + `set_pricing.py`)]:**
   - `Fail-Fix Plan.v1` (§2.B.1) updates `my_collection_screen.dart:3020-3023` (card) to fall back across `AI Estimated Value` / `ai_estimated_value` / `estValue`, **but misses `my_collection_screen.dart:3823`** (`_buildMetricStrip` in Coin Inspector, which still only reads `data[_F.aiValue]?.toString() ?? '--'`).
   - Also add `"metal_content": "Cupronickel Clad"` to `US_MINT_PRODUCT_CATALOG["26RJ"]` (`us_mint_catalog_service.py:185-204`) so `set_pricing.py:80-93` never returns `"Unvaluable - Metal unspecified"`, and stamp all 4 valuation keys (`AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, `estValue` = `"$124.50"`, `enrichment_status = "enriched"`) in `normalize_and_validate_receipt`, `commit_reviews`, and `keep_set_as_is`.

---

## 3. Handoff
- **Baton:** **Grok Bot CoS (`GB CoS`)** for Stage 2 review of `ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md` + `ARGON_REVIEW_ERIC_BMINUS_FAILFIX_PLAN_V1_2026-10-27.md`, then **SAG**, then **Eric typed YES**.
- Over.
