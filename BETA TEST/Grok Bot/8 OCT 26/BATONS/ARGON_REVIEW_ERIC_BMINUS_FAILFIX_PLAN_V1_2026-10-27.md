# ARGON_REVIEW_ERIC_BMINUS_FAILFIX_PLAN_V1_2026-10-27.md

**Reviewer:** Gemini 4 Argon (`Numista.Ai Argon`) — **THINKING JOBS ONLY**  
**Date / Time:** 2026-10-27 ~5:46 PM ET  
**Target Plan:** [`ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md) (filed by AG CoS v2 under `NET-629`)  
**Target FT Report:** [`FT_RESULT_NET627_ERIC_BMINUS_751a4305_FAIL.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/FT_RESULT_NET627_ERIC_BMINUS_751a4305_FAIL.md)  
**Target SAG Trigger Model:** [`SAG_FEEDBACK_NET627_FAILFIX_2026-10-27.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/SAG_FEEDBACK_NET627_FAILFIX_2026-10-27.md)  
**Score:** **74 / 100 — CONDITIONAL GO (3 P0 Root-Cause Gaps Identified — Must Fold into Plan.v2 / Build Before Preview Deploy)**  
**Code Changes Made by Argon:** **NONE** (Zero code edits, zero commits, zero deploys).

---

## 1. Executive Summary

`ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md` correctly identifies:
1. `commit_reviews` (`numista_backend/main.py:3628-3639`) wrote `ai_est_value` and `estValue` (`$124.50`) but omitted the canonical PascalCase `'AI Estimated Value'` (`_F.aiValue`) read by `my_collection_screen.dart:3022` and `3823`, leaving the `26RJ` card in `'Valuation Pending'` and the Coin Inspector metric strip Est. Value as `'--'`.
2. `keep_set_as_is` (`numista_backend/main.py:3740-3785`) did not invoke `enrich_us_mint_item()` or stamp the baseline valuation at all.
3. `normalize_and_validate_receipt` (`numista_backend/main.py:7718-7719`) zeroes `doc["allocated_fees"]` and `doc["shipping_fee"]` when `doc.get("pack_expanded")` is truthy.

**HOWEVER, line-by-line code + live infrastructure verification against `dev` (`751a4305`) uncovered THREE P0 ROOT-CAUSE GAPS where `Fail-Fix Plan.v1` as written would STILL FAIL both `I-04b` and `I-07 / PM-01` / `SAG4` on the `p7-gate` preview channel:**

1. **[P0 BLOCKER — `I-04b` (`26SQRP` Fee `$0.00` on Review Hub)]:** `Fail-Fix Plan.v1` (§2.A.1) only removes `0.0 if doc.get("pack_expanded") else allocated_fee` at `numista_backend/main.py:7718-7719`, assuming `allocated_fee` holds `9.95`. **It does not!** Higher up in the same function at **`numista_backend/main.py:7589-7590`**, an explicit `if` branch hardcodes `allocated_fee = 0.0` whenever `26SQRP` appears anywhere on the invoice! Unless lines `7589-7590` are also fixed, `allocated_fee` is already `0.0` when execution reaches line `7718`, and `26SQRP` will **still display `Fee $0.00`**!
2. **[P0 BLOCKER — `I-07` / `PM-01` (`"Image unavailable"`) & `SAG4` (`20 tiles all placeholders`)]:** Why did `FT_RESULT_NET627` specifically report the exact string **`"Image unavailable"`** in `26RJ` detail and **`"all placeholders"`** across all 20 tiles of `CoinSetViewer` on `https://numista-vault--p7-gate-8avtpz22.web.app`?
   - In `numista_mobile/lib/screens/my_collection_screen.dart:4835`, the string `'Image unavailable'` is **ONLY** rendered when `isError: true` is passed to `_vaultPlaceholder(...)` from `Image.network(... errorBuilder: ...)` at line `3725` — meaning `activeUrl` (`https://storage.googleapis.com/numista-reference-library/.../26rj_a.jpg`) **WAS present**, and the browser `Image.network` fetch **failed in Flutter Web CanvasKit/HTML**!
   - Why did `Image.network` fail on `https://numista-vault--p7-gate-8avtpz22.web.app`? Live inspection of the GCS bucket `gs://numista-reference-library` (`numista_backend/cors_reference_library.json:3-8`) proves its CORS allowlist is:
     `['https://numista.ai', 'https://numista-vault.web.app', 'http://localhost:*', 'http://127.0.0.1:*']`
     It **blocks** `https://numista-vault--p7-gate-8avtpz22.web.app` (no `Access-Control-Allow-Origin` header returned for `--p7-gate` preview origins)! Because Flutter Web (`Image.network`) fetches images via CORS-enabled XHR/`fetch`, **every single image in `gs://numista-reference-library` (`26rj_a.jpg`, `26rj_e.jpg`, and all 20 coin images in `coin_set_index/uncirculated-coin-set-2026`) is blocked by CORS on the `p7-gate` preview URL!**
3. **[P0 BLOCKER — `I-07` / `PM-01` (`CoinDetailScreen` `"Est. Value $0.00"` vs Set Issue Price `$124.50`)]:** When `CoinDetailScreen` (`numista_mobile/lib/screens/coin_detail_screen.dart`) opens for a Set item (`26RJ`), `_fetchSetValuation()` calls `/api/sets/valuate` (`numista_backend/main.py` / `numista_backend/set_pricing.py:105`), which looks up `2026_mint_set_clad_20` in `numista_backend/data/us_mint_sets_catalog.json:70-82` (`display_range: "$25.50 - $36.40"`, `median: 31.00`), or if `Metal Content` is empty (`""`, because `US_MINT_PRODUCT_CATALOG["26RJ"]` at `us_mint_catalog_service.py:185-204` has NO `"metal_content"` key!), `resolve_set_sku` (`set_pricing.py:88-93`) returns `"ai_estimated_value": "Unvaluable - Metal unspecified"`, which `_parseAiValue` in `coin_detail_screen.dart:1662` parses as `0.0`! Furthermore, in `my_collection_screen.dart:3467, 3490`, `_showCoinInspectorDialog` only checks `data[_F.imageObverse]` (`image_url_obverse`) and `data['obverse_image']`, ignoring `primary_image_url` and `photo_urls`.

---

## 2. Verbatim Code Audit & Required Corrections (Rule 6a)

### Finding A-1 (P0 BLOCKER — `I-04b`): `main.py:7589-7590` Hardcodes `allocated_fee = 0.0` for `26SQRP`

- **Citation 1 — `numista_backend/main.py:7583-7599`:**
  ```python
  7583:     results = []
  7584:     for it in items:
  7585:         item_qty = _get_item_qty(it)
  7586:         sticker_price = clean_valuation_value(it.get("Cost") or 0.0)
  7587: 
  7588:         # Proportional Landed Cost Allocation
  7589:         # Under Plan v3.1, US Mint orders keep shipping on receipt but waive fee allocation to child coins
  7590:         if is_us_mint_order and any((it.get("item_number") or it.get("Retailer Item No.") or "").upper() == "26SQRP" or "26sqrp" in ((it.get("Personal Notes") or "") + " " + fname).lower() for it in items):
  7591:             allocated_fee = 0.0
  7592:         elif raw_item_sum > 0.0 and total_global_fees > 0.0:
  7593:             allocated_fee = round(total_global_fees * (sticker_price / raw_item_sum), 2)
  7594:         elif len(items) == 1 and total_global_fees > 0.0:
  7595:             allocated_fee = round(total_global_fees, 2)
  7596:         else:
  7597:             allocated_fee = 0.0
  7598: 
  7599:         landed_cost_basis = round(sticker_price + allocated_fee, 2)
  ```
- **Citation 2 — `numista_backend/main.py:7714-7737`:**
  ```python
  7714:             enrich_us_mint_item(doc)
  7715:             doc["Purchase Cost"] = doc.get("Cost")
  7716:             # Plan 4.1 §3.1 item 1: Pure snake_case allocated_fees & shipping_fee
  7717:             # NET-565: Only pack/roll expansions waive the fee; regular Mint items (e.g. 23RH) carry Mint S&H.
  7718:             doc["allocated_fees"] = 0.0 if doc.get("pack_expanded") else allocated_fee
  7719:             doc["shipping_fee"] = 0.0 if doc.get("pack_expanded") else allocated_fee
  ...
  7729:             if doc.get("pack_expanded") and doc.get("unit_cost"):
  7730:                 qty_val = doc.get("Quantity") or doc.get("quantity") or 1
  7731:                 cost_val = float(doc.get("Cost") or 0.0)
  7732:                 unit_val = float(doc.get("unit_cost") or 0.0)
  7733:                 doc["set_cost_label"] = f"${cost_val:.2f} ({qty_val} @ ${unit_val:.2f})"
  ```
- **Citation 3 — `numista_backend/services/us_mint_catalog_service.py:484-501`:**
  ```python
  484:             raw_cost = coin_doc.get("Cost") or coin_doc.get("Purchase Cost") or 0.0
  485:             alloc_fees = coin_doc.get("Allocated Fees") or coin_doc.get("allocated_fees") or 0.0
  486:             try:
  487:                 cost_f = float(re.sub(r"[^\d.]", "", str(raw_cost)))
  488:             except (ValueError, TypeError):
  489:                 cost_f = 0.0
  490:             try:
  491:                 fee_f = float(re.sub(r"[^\d.]", "", str(alloc_fees)))
  492:             except (ValueError, TypeError):
  493:                 fee_f = 0.0
  494:             # Strip allocated shipping/fees if they were baked into landed Cost
  495:             sticker_f = round(cost_f - fee_f, 2) if (fee_f > 0 and cost_f > fee_f) else cost_f
  496:             if sticker_f > 0:
  497:                 unit_cost = round(sticker_f / pack_qty, 2)
  498:                 coin_doc["Cost"] = sticker_f
  499:                 coin_doc["Purchase Cost"] = f"${sticker_f:.2f}"
  500:                 coin_doc["unit_cost"] = unit_cost
  501:                 coin_doc["set_cost_label"] = f"${sticker_f:.2f} ({pack_qty} @ ${unit_cost:.2f})"
  502:             coin_doc["Allocated Fees"] = 0.0
  ```
- **Citation 4 — `numista_backend/main.py:8200`:**
  ```python
  8200:                         coin_doc.pop("Allocated Fees", None)
  ```
- **Why `Fail-Fix Plan.v1` Fails Without This Fix:**
  1. At `main.py:7589-7590`, `allocated_fee` is forced to `0.0` when `26SQRP` is on the invoice.
  2. Even if you remove lines `7589-7590` so `allocated_fee = 9.95`, look at what happens next:
     - Line `7598` sets `landed_cost_basis = round(sticker_price + allocated_fee, 2)` (`45.00 + 9.95 = 54.95`).
     - Line `7679` sets `doc["Cost"] = 54.95`, **WITHOUT setting `doc["allocated_fees"]` before calling `enrich_us_mint_item(doc)` at line `7714`!**
     - Inside `enrich_us_mint_item(doc)` (`us_mint_catalog_service.py:485`), `alloc_fees = coin_doc.get("Allocated Fees") or coin_doc.get("allocated_fees") or 0.0` evaluates to **`0.0`** because `doc["allocated_fees"]` isn't set until line `7718`!
     - Then `sticker_f` at line `495` becomes `54.95` instead of `45.00`, `unit_cost` becomes `$2.20` (`54.95 / 25`), and `set_cost_label` becomes `"$54.95 (25 @ $2.20)"` — **REGRESSING `I-04a` (`$45.00 (25 @ $1.80)`)!**
     - And at `us_mint_catalog_service.py:502`, `coin_doc["Allocated Fees"] = 0.0` is stamped (and later popped at `main.py:8200`).
- **Required Exact Fix for `I-04a` + `I-04b`:**
  1. In `numista_backend/main.py:7589-7596`, remove the `26SQRP` special-case `allocated_fee = 0.0` branch so `allocated_fee` is computed normally (`9.95`).
  2. Set `"allocated_fees": allocated_fee` and `"shipping_fee": allocated_fee` in the initial `doc` dictionary at `main.py:7680` **BEFORE** calling `enrich_us_mint_item(doc)` at line `7714` (or keep `doc["Cost"] = sticker_price if is_us_mint_order else landed_cost_basis`), so `enrich_us_mint_item` (`us_mint_catalog_service.py:485, 495`) sees `fee_f = 9.95` and strips it from `54.95` -> `sticker_f = 45.00`, `unit_cost = 1.80`, `set_cost_label = "$45.00 (25 @ $1.80)"` (`I-04a` stays 100% PASS!).
  3. In `us_mint_catalog_service.py:502`, remove `coin_doc["Allocated Fees"] = 0.0` (or in `main.py:7718-7719`, set `doc["allocated_fees"] = allocated_fee` and `doc["shipping_fee"] = allocated_fee` after `enrich_us_mint_item(doc)` without `doc["Allocated Fees"]` — note `main.py:8200` pops `"Allocated Fees"` anyway to enforce pure snake_case!).

---

### Finding A-2 (P0 BLOCKER — `I-07` / `PM-01` & `SAG4`): GCS Bucket `gs://numista-reference-library` CORS Blocks `p7-gate` Preview Channel!

- **Citation 1 — `numista_mobile/lib/screens/my_collection_screen.dart:3720-3726` & `4835`:**
  ```dart
  3720:                         ? Image.network(activeUrl, fit: BoxFit.contain,
  3721:                             loadingBuilder: (ctx, child, prog) =>
  3722:                                 prog == null ? child : const Center(child: CircularProgressIndicator()),
  3723:                             errorBuilder: (ctx, err, st) {
  3724:                               debugPrint('Image load error: $err  url: $activeUrl');
  3725:                               return _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse', isError: true);
  3726:                             },
  ```
  ```dart
  4835:             isError ? 'Image unavailable' : 'No $side photo yet',
  ```
- **Citation 2 — `numista_mobile/lib/widgets/coin_set_viewer.dart:377-386`:**
  ```dart
  377:                         child: _currentUrl != null
  378:                             ? Image.network(
  379:                                 _currentUrl!,
  380:                                 key: ValueKey(_currentUrl),
  381:                                 fit: BoxFit.cover,
  382:                                 errorBuilder: (_, e, st) => const Center(
  383:                                   child: Icon(Icons.broken_image_outlined,
  384:                                       color: _kSubtext, size: 28),
  385:                                 ),
  386:                               )
  ```
- **Citation 3 — `numista_backend/cors_reference_library.json:1-17`:**
  ```json
  1: [
  2:   {
  3:     "origin": [
  4:       "https://numista.ai",
  5:       "https://numista-vault.web.app",
  6:       "http://localhost:*",
  7:       "http://127.0.0.1:*"
  8:     ],
  9:     "method": ["GET", "HEAD"],
  10:     "responseHeader": [
  11:       "Content-Type",
  12:       "Access-Control-Allow-Origin",
  13:       "Cache-Control"
  14:     ],
  15:     "maxAgeSeconds": 3600
  16:   }
  17: ]
  ```
- **Live Probe Evidence:**
  - HTTP `HEAD` to `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg`:
    - With `Origin: https://numista-vault.web.app` -> returns `Access-Control-Allow-Origin: https://numista-vault.web.app` (200 OK).
    - With `Origin: https://numista-vault--p7-gate-8avtpz22.web.app` -> returns **`{'Vary': 'Origin'}` with NO `Access-Control-Allow-Origin` header!**
  - In Flutter Web, `Image.network` uses CORS-mode `fetch`/XHR to decode bytes into CanvasKit/Skia. When `Access-Control-Allow-Origin` is missing, the browser aborts the request with a CORS error, triggering `errorBuilder` -> `'Image unavailable'` (`my_collection_screen.dart:3725, 4835`) on the `26RJ` hero AND `Icons.broken_image_outlined` (`coin_set_viewer.dart:383`) on all 20 coin tiles in `CoinSetViewer`!
- **Required Exact Fix for `I-07` / `PM-01` & `SAG4`:**
  1. Update `numista_backend/cors_reference_library.json` (and apply via `gcloud storage buckets update gs://numista-reference-library --cors-file=numista_backend/cors_reference_library.json` or Python `google.cloud.storage` `bucket.cors` update) to include `"https://numista-vault--p7-gate-8avtpz22.web.app"` and `"https://*.web.app"` / `"https://*.firebaseapp.com"` (or `"*"` for public reference library read-only `GET`/`HEAD`, matching `gs://us_mint_coin_images` which already uses `'origin': ['*']`).
  2. Also update `_showCoinInspectorDialog` (`numista_mobile/lib/screens/my_collection_screen.dart:3467, 3490`) so its `hasObv` / `hasRev` / `activeUrl` checks include `primary_image_url` and `photo_urls` alongside `_F.imageObverse` (`image_url_obverse`) and `obverse_image`:
     - **Citation — `numista_mobile/lib/screens/my_collection_screen.dart:3467-3468` & `3490-3491`:**
       ```dart
       3467:     final initObv = _cleanUrl(data[_F.imageObverse] ?? data['obverse_image']);
       3468:     final initRev = _cleanUrl(data[_F.imageReverse] ?? data['reverse_image']);
       ...
       3490:             final hasObv = _cleanUrl(data[_F.imageObverse] ?? data['obverse_image']).isNotEmpty;
       3491:             final hasRev = _cleanUrl(data[_F.imageReverse] ?? data['reverse_image']).isNotEmpty;
       ```

---

### Finding A-3 (P0 BLOCKER — `I-07` / `PM-01` Valuation & `SAG2` Enrichment): `commit_reviews`, `keep_set_as_is`, `US_MINT_PRODUCT_CATALOG["26RJ"]`, and `_buildMetricStrip`

- **Citation 1 — `numista_backend/main.py:3628-3639` (`commit_reviews`):**
  ```python
  3628:                     if not data.get('ai_est_value') and not data.get('estValue'):
  3629:                         cat_p = data.get('issue_price') or data.get('Sticker Price') or data.get('Cost') or data.get('Purchase Cost') or 0.0
  3630:                         try:
  3631:                             clean_cat_p = float(re.sub(r"[^\d.]", "", str(cat_p)))
  3632:                         except Exception:
  3633:                             clean_cat_p = 0.0
  3634:                         if clean_cat_p > 0.0:
  3635:                             data['ai_est_value'] = clean_cat_p
  3636:                             data['estValue'] = f"${clean_cat_p:.2f}"
  3637:                             data['valuation_source'] = "US Mint Catalog Baseline"
  3638:                             data['enrichment_status'] = "enriched"
  ```
- **Citation 2 — `numista_backend/main.py:3762-3778` (`keep_set_as_is`):**
  ```python
  3762:     committed["is_set"] = True
  3763:     committed["set_Action"] = "keep_as_set"
  3764:     committed["committed_at"] = firestore.SERVER_TIMESTAMP
  3765: 
  3766:     # Ensure Golden Schema required defaults
  3767:     if not committed.get("Condition"):
  3768:         committed["Condition"] = "Unspecified / Raw"
  3769:     if not committed.get("enrichment_status"):
  3770:         committed["enrichment_status"] = "pending"
  ```
- **Citation 3 — `numista_mobile/lib/screens/my_collection_screen.dart:3016-3022`, `3169`, `3823`:**
  ```dart
  3016:     final valCpg = _parseNumber(m['cpgRetail']);
  3017:     final finalVal = valCpg;
  3018:     
  3019:     final fmt = intl.NumberFormat.currency(symbol: '\$');
  3020:     final valueText = finalVal > 0 
  3021:         ? fmt.format(finalVal) 
  3022:         : (m[_F.aiValue]?.toString() ?? '—');
  ```
  ```dart
  3169:                     if (valueText == '—' || m['enrichment_status'] == 'pending')
  ```
  ```dart
  3823:       Expanded(child: _metricCard('Est. Value', data[_F.aiValue]?.toString() ?? '--', Color(0xFF1A73E8), Icons.attach_money)),
  ```
- **Citation 4 — `numista_backend/services/us_mint_catalog_service.py:185-204` (`26RJ` catalog entry):**
  ```python
  185:     "26RJ": {
  186:         "title": "United States Mint Uncirculated Coin Set 2026 (26RJ)",
  187:         "formal_name": "United States Mint Uncirculated Coin Set 2026",
  188:         "year": 2026,
  189:         "mint_mark": "P & D",
  190:         "mint_facility": "Philadelphia (P) & Denver (D)",
  191:         "denomination": "Set",
  192:         "program_series": "United States Mint Uncirculated Set",
  193:         "theme_subject": "2026 Semiquincentennial 20-Coin Uncirculated P&D Set",
  194:         "strike_type": "Uncirculated",
  195:         "condition": "Uncirculated",
  196:         "issue_price": 124.50,
  197:         "retailer": "United States Mint",
  198:         "is_set": True,
  199:         "set_id": "uncirculated-coin-set-2026",
  200:         "image_url_obverse": "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg",
  201:         "image_url_reverse": "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg",
  202:         "set_coin_count": 20,
  203:         "catalog_url": "https://catalog.usmint.gov/",
  204:     },
  ```
- **Why Three Sub-Fixes Are Required Here:**
  1. **`my_collection_screen.dart:3823` (`_buildMetricStrip` in Coin Inspector):** `Fail-Fix Plan.v1` (§2.B.1) updates `my_collection_screen.dart:3020-3023` (the grid card), **but forgets `my_collection_screen.dart:3823`** (`_buildMetricStrip` inside `_showCoinInspectorDialog`), which still reads `data[_F.aiValue]?.toString() ?? '--'`! Update line `3823` to use the same fallback chain (`data[_F.aiValue] ?? data['ai_estimated_value'] ?? data['estValue'] ?? '--'`).
  2. **`commit_reviews` guard condition (`main.py:3628`):** In `Fail-Fix Plan.v1` (§2.A.2), the guard `if not data.get('ai_est_value') and not data.get('estValue'):` was removed in the snippet — make sure the condition checks `if not data.get('AI Estimated Value') or data.get('AI Estimated Value') in ('Pending', '—', '--', '$0.00', '0'):` so any item missing `'AI Estimated Value'` gets stamped with `AI Estimated Value = "$124.50"`, `ai_estimated_value = "$124.50"`, `ai_est_value = 124.50`, `estValue = "$124.50"`, and `enrichment_status = "enriched"` in **both** `commit_reviews` (`main.py:3628`) AND `keep_set_as_is` (`main.py:3766`) AND `normalize_and_validate_receipt` (`main.py:7715`) so even if a document is inspected immediately after commit, all four valuation fields are populated from creation!
  3. **`US_MINT_PRODUCT_CATALOG["26RJ"]` (`us_mint_catalog_service.py:185-204`) & `us_mint_sets_catalog.json:70-82`:**
     - Add `"metal_content": "Cupronickel Clad"` to `US_MINT_PRODUCT_CATALOG["26RJ"]` so `set_pricing.py:80-93` never fails with `"Unvaluable - Metal unspecified"`.
     - In `numista_backend/data/us_mint_sets_catalog.json:70-82`, `2026_mint_set_clad_20` currently has `"median": 31.00, "display_range": "$25.50 - $36.40"`. If `/api/sets/valuate` runs on `26RJ`, it would overwrite `$124.50` with `$25.50 - $36.40` unless `2026_mint_set_clad_20` reflects the US Mint issue price baseline (`124.50`) or `commit_reviews` / `_async_post_commit_enrichment` preserves the catalog `issue_price` baseline (`$124.50`) when `retailer_item_num == "26RJ"`.

---

## 3. Summary Checklist of Required Additions to `Fail-Fix Plan` (for GB CoS, SAG, and AG CoS Build)

| # | Gate | File & Lines | Required Addition |
|---|---|---|---|
| **1** | **I-04b** (`26SQRP` Fee `$9.95` on Hub) | `numista_backend/main.py:7589-7590`, `7680`, `7718-7719` & `us_mint_catalog_service.py:502` | Remove `if is_us_mint_order and any(... "26SQRP" ...): allocated_fee = 0.0` at `main.py:7589-7590`; pass `allocated_fees = allocated_fee` into `doc` before `enrich_us_mint_item(doc)` so `I-04a` (`$45.00 (25 @ $1.80)`) stays intact; keep `doc["allocated_fees"] = allocated_fee` and `doc["shipping_fee"] = allocated_fee` at `7718-7719` (do NOT write `"Allocated Fees"` since line `8200` pops it). |
| **2** | **I-07 / PM-01 & SAG4** (`26RJ` Hero + 20-Coin Set Images on `p7-gate`) | `numista_backend/cors_reference_library.json:1-17` (`gs://numista-reference-library` CORS) & `my_collection_screen.dart:3467-3491` | Update CORS on `gs://numista-reference-library` to allow `https://numista-vault--p7-gate-8avtpz22.web.app` (or `"*"` for `GET`/`HEAD` on public reference images, matching `gs://us_mint_coin_images`) so `Image.network` on the preview channel stops throwing CORS `errorBuilder` (`"Image unavailable"` / broken tile icons). Also add `primary_image_url` / `photo_urls` fallback to `_showCoinInspectorDialog` (`3467, 3490`). |
| **3** | **I-07 / PM-01** (`26RJ` Valuation `$124.50` Post-Commit) | `numista_backend/main.py:3628-3639`, `3766-3778`, `7715` & `my_collection_screen.dart:3020-3023`, `3823` | Stamp `AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, `estValue` = `"$124.50"` and `enrichment_status = "enriched"` in `normalize_and_validate_receipt`, `commit_reviews`, and `keep_set_as_is`; add fallback chain in both `my_collection_screen.dart:3022` (card) and `3823` (`_buildMetricStrip`); add `"metal_content": "Cupronickel Clad"` to `US_MINT_PRODUCT_CATALOG["26RJ"]`. |

---

## 4. Verdict & Handoff

- **Verdict:** **74 / 100 — CONDITIONAL GO** (Proceed to **Grok Bot CoS (GB CoS)** review in the locked 4-stage chain `AG CoS -> Argon -> GB CoS -> SAG -> Eric typed YES -> EXECUTE preview-only`, with Findings **A-1**, **A-2**, and **A-3** mandatory for the implementation/Plan.v2 fold).
- **Next Baton:** **Grok Bot CoS (GB CoS)** to review `ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md` + `ARGON_REVIEW_ERIC_BMINUS_FAILFIX_PLAN_V1_2026-10-27.md`.
