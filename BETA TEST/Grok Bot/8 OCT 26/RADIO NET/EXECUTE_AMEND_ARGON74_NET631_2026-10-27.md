# EXECUTE_AMEND_ARGON74_NET631 — fold late Argon 74 P0s into LIVE EXECUTE (no plan reopen)

**NET:** NET-631 (still EXECUTE — do NOT reopen plan cycle)
**Auth:** Eric YES ~5:45 PM ET still stands. No second YES.
**Filed by:** Antigravity Desk ~6:10 PM ET (CoS order)
**Source:** ARGON_REVIEW_ERIC_BMINUS_FAILFIX_PLAN_V1 (74/100 CONDITIONAL GO, ~5:51 PM) + NET-630 radio OVER
**Also still required:** EXECUTE_BRIEF Must-Fix 1-5 + GB FF-1..3 + SAG_FEEDBACK_FAILFIX_PLAN_V1

## Must-Fix A-1..A-3 (fold into coding NOW)

### A-1 Fee (I-04b + protect I-04a)
1. Remove `main.py:7589-7590` (approx) 26SQRP special-case that forces `allocated_fee = 0.0`.
2. Set `doc["allocated_fees"]` and `doc["shipping_fee"]` to `allocated_fee` **BEFORE** `enrich_us_mint_item(doc)` (~line 7714), not only after — otherwise enrich sees fee 0, keeps landed Cost, and unit cost becomes **$2.20** instead of **$1.80** (`$45.00 (25 @ $1.80)` must stay PASS).
3. Keep Hub parent 26SQRP Fee/S&H **$9.95**; do not multiply full S&H onto every pack-expanded child. Still fix pack_expanded zero at ~7718-7719 per brief.
4. Prefer snake_case `allocated_fees` / `shipping_fee` (line ~8200 pops `Allocated Fees`).

### A-2 CORS (smoking gun — Image unavailable / SAG4 placeholders)
1. `gs://numista-reference-library` CORS (`numista_backend/cors_reference_library.json` + **live bucket**) must allow the **p7-gate Hosting origin** (e.g. `https://numista-vault--p7-gate-8avtpz22.web.app` or a safe preview pattern). Today allowlist blocks preview → Flutter Web `Image.network` errorBuilder → exact string **"Image unavailable"** and 20-tile placeholders.
2. Also dual-read image keys in inspector (`primary_image_url` / `photo_urls` fallbacks) per Argon.

### A-3 Inspector + 26RJ valuation keys
1. Dual-read at `_buildMetricStrip` **`my_collection_screen.dart:3823`** (not only card ~3022) — same value key fallbacks as Plan.v1.
2. Stamp **`metal_content`: `Cupronickel Clad`** on catalog `26RJ` so set_pricing does not return "Unvaluable - Metal unspecified".
3. Stamp all **4** value keys on Commit / keep_set_as_is / normalize paths: `AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, `estValue` (baseline `$124.50` fill-missing-only) + `enrichment_status = "enriched"`.

## Target / locks
- Preview **p7-gate ONLY**. origin/main **LOCKED**.
- Report **PREVIEW_READY** with Hosting URL + Run ID + SHA.
- No founder retest until FT PASS. NET-610 8PM separate / ignore for this day track.
- Desk mirrors/wakes only — NOT coding.
