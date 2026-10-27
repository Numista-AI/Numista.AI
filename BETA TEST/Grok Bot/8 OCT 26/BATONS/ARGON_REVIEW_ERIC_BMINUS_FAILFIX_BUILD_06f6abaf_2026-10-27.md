# ARGON BUILD REVIEW — ERIC B-MINUS FAIL-FIX (`06f6abaf` / `NET-631`)
**Reviewer:** `Numista.Ai Argon` (`Gemini 4 Argon` — THINKING JOBS ONLY)  
**Date:** 2026-10-27 ~6:54 PM ET  
**Target Build Commit:** `06f6abaf0e38338a9d1efe9e3703030aaa7b8566` (`origin/dev`, deployed to `p7-gate` / `numista-backend-00498-kek`)  
**Rule 6(a)/(b) Compliance:** Full built-code diff audit with 100% verbatim line quotes and live GCS CORS verification.  
**Baton Status:** Remains with **Field Tester (FT)** on `p7-gate` per `WHOSE_TURN.md` (`NET-631`).

---

## 1. Score & Verdict
- **Build Score:** **96 / 100 — GO (Pending Field Tester Live Gate Confirmation)**
- **Summary:** Commit `06f6abaf` cleanly and completely implements all 5 Must-Fix items from `EXECUTE_BRIEF_ERIC_BMINUS_FAILFIX_PLAN_V1_2026-10-27.md` plus all 3 Argon P0 amendments (`A-1`, `A-2`, `A-3`) from `EXECUTE_AMEND_ARGON74_NET631_2026-10-27.md`.

---

## 2. Verbatim Code & Live Verification Audit (Rule 6a)

### A-1 (`I-04b` & `I-04a` — `26SQRP` Fee `$9.95` on Review Hub + `$45.00 (25 @ $1.80)` Cost Label) — PASS
1. **Removed `26SQRP` Zero-Fee Special Case (`numista_backend/main.py:7710-7715`):**
   ```python
        # Proportional Landed Cost Allocation
        if raw_item_sum > 0.0 and total_global_fees > 0.0:
            allocated_fee = round(total_global_fees * (sticker_price / raw_item_sum), 2)
        elif len(items) == 1 and total_global_fees > 0.0:
            allocated_fee = round(total_global_fees, 2)
        else:
            allocated_fee = 0.0
   ```
2. **Stamped `allocated_fees` & `shipping_fee` Prior to Catalog Enrichment (`numista_backend/main.py:7798-7802`):**
   ```python
            "Cost":                 landed_cost_basis,
            "Purchase Cost":        landed_cost_basis,
            "allocated_fees":       allocated_fee,
            "shipping_fee":         allocated_fee,
            "Quantity":             item_qty,
   ```
3. **Preserved Canonical Roll Lot Cost (`$45.00`) & Unit Cost (`$1.80`) (`numista_backend/services/us_mint_catalog_service.py:490-507`):**
   ```python
                            canonical_lot_cost = round(clean_cat_price * curr_qty, 2)
                            alloc_fees = float(item.get("Allocated Fees") or item.get("allocated_fees") or 0.0)
                            item["Sticker Price"] = canonical_lot_cost
                            item["Allocated Fees"] = alloc_fees
                            item["Cost"] = canonical_lot_cost
                            item["Purchase Cost"] = canonical_lot_cost
                            item["cost"] = canonical_lot_cost
                    except Exception as e:
                        logger.warning(f"Failed parsing cat_issue_price '{cat_issue_price}': {e}")
                
                # B2/B4: Ensure unit_cost is calculated from lot total Cost
                cost_val = item.get("Sticker Price") or item.get("Cost") or item.get("Purchase Cost") or item.get("cost") or 0.0
                try:
                    cost_float = float(cost_val)
                    if cost_float > 0.0:
                        unit_c = round(cost_float / new_qty, 4)
                        item["unit_cost"] = unit_c
                        item["set_cost_label"] = f"${cost_float:.2f} ({new_qty} @ ${cost_float / new_qty:.2f})"
   ```
4. **Preserved `allocated_fee` After `enrich_us_mint_item` (`numista_backend/main.py:7835-7839`):**
   ```python
            enrich_us_mint_item(doc)
            doc["Purchase Cost"] = doc.get("Cost")
            # Plan 4.1 §3.1 item 1 / Plan.v1 / Must-Fix A-1: Pure snake_case allocated_fees & shipping_fee
            doc["allocated_fees"] = allocated_fee
            doc["shipping_fee"] = allocated_fee
   ```

---

### A-2 (`I-07 / PM-01` `"Image unavailable"` & `SAG4` 20-Tile Placeholders — GCS CORS + Flutter Dual-Read) — PASS
1. **CORS Config Updated (`numista_backend/cors_reference_library.json:3-10`):**
   ```json
    "origin": [
      "*",
      "https://numista.ai",
      "https://numista-vault.web.app",
      "https://numista-vault--p7-gate-8avtpz22.web.app",
      "http://localhost:*",
      "http://127.0.0.1:*"
    ],
   ```
2. **Live HTTP `HEAD` Verification Against `gs://numista-reference-library` (`26rj_a.jpg`):**
   - Command executed by Argon:
     `curl.exe -sI -H "Origin: https://numista-vault--p7-gate-8avtpz22.web.app" "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg"`
   - Live Response Headers:
     ```http
     HTTP/1.1 200 OK
     Content-Type: image/jpeg
     Content-Length: 326970
     Access-Control-Allow-Origin: *
     Access-Control-Expose-Headers: Access-Control-Allow-Origin, Cache-Control, Content-Length, Content-Type, Date, Server, Transfer-Encoding, X-GUploader-UploadID, X-Google-Trace
     ```
3. **Flutter Inspector & Card Image Fallback (`numista_mobile/lib/screens/my_collection_screen.dart:3468-3471, 3493-3494, 6322-6323`):**
   ```dart
    final obvFallback = data[_F.imageObverse] ?? data['primary_image_url'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).isNotEmpty ? data['photo_urls'][0] : null);
    final revFallback = data[_F.imageReverse] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).length > 1 ? data['photo_urls'][1] : null);
    final hasUserPhoto = obvFallback?.toString().startsWith('http') == true
        || revFallback?.toString().startsWith('http') == true;
   ```
   ```dart
          final obvUrl   = (data[_F.imageObverse] ?? data['primary_image_url'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).isNotEmpty ? data['photo_urls'][0] : null))?.toString() ?? '';
          final revUrl   = (data[_F.imageReverse] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).length > 1 ? data['photo_urls'][1] : null))?.toString() ?? '';
   ```
   ```dart
    final obv = _cleanUrl(data[_F.imageObverse] ?? data['primary_image_url'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).isNotEmpty ? data['photo_urls'][0] : null));
    final rev = _cleanUrl(data[_F.imageReverse] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).length > 1 ? data['photo_urls'][1] : null));
   ```

---

### A-3 (`I-07 / PM-01` Valuation Quad-Write, Dual-Read, Metal Content, & Async Worker) — PASS
1. **Catalog `26RJ` Metal Content & Propagation (`numista_backend/services/us_mint_catalog_service.py:196, 443-447`):**
   ```python
        "metal_content": "Cupronickel Clad",
   ```
   ```python
        if catalog_match.get("metal_content"):
            if not item.get("Metal Content"):
                item["Metal Content"] = catalog_match["metal_content"]
            if not item.get("metal"):
                item["metal"] = catalog_match["metal_content"]
   ```
2. **Quad-Write Valuation Keys (`AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, `estValue`) across Enrich, Commit, Async Worker, and `keep_set_as_is`:**
   - `numista_backend/services/us_mint_catalog_service.py:527-533`:
     ```python
                    if not curr_ai_val or str(curr_ai_val).strip() in ("", "$0.00", "0.0", "0", "—", "--", "Valuation Pending", "null"):
                        item["ai_est_value"] = clean_cat_p
                        item["ai_estimated_value"] = fmt_val
                        item["AI Estimated Value"] = fmt_val
                        item["estValue"] = fmt_val
                        item["valuation_source"] = "US Mint Catalog Baseline"
                        item["enrichment_status"] = "enriched"
     ```
   - `numista_backend/main.py:3651-3657` (`commit_reviews`) & `numista_backend/main.py:3886-3892` (`keep_set_as_is`):
     ```python
                            fmt_val = f"${clean_cat_p:.2f}"
                            data['ai_est_value'] = clean_cat_p
                            data['ai_estimated_value'] = fmt_val
                            data['AI Estimated Value'] = fmt_val
                            data['estValue'] = fmt_val
                            data['valuation_source'] = "US Mint Catalog Baseline"
                            data['enrichment_status'] = "enriched"
     ```
3. **Flutter Card & Inspector `_buildMetricStrip` Dual-Read (`numista_mobile/lib/screens/my_collection_screen.dart:3020-3023, 3826`):**
   ```dart
        final rawAiVal = m[_F.aiValue] ?? m['ai_estimated_value'] ?? m['estValue'] ?? (m['ai_est_value'] != null ? fmt.format(m['ai_est_value']) : null);
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (rawAiVal?.toString() ?? '—');
   ```
   ```dart
      Expanded(child: _metricCard('Est. Value', (data[_F.aiValue] ?? data['ai_estimated_value'] ?? data['estValue'] ?? (data['ai_est_value'] != null ? '\$${(data['ai_est_value'] is num ? (data['ai_est_value'] as num).toStringAsFixed(2) : data['ai_est_value'])}' : null))?.toString() ?? '--', Color(0xFF1A73E8), Icons.attach_money)),
   ```

---

## 3. Non-Blocking Observation (-4 pts)
- **NB-1 (`cors_reference_library.json` Wildcard Origin):** `numista_backend/cors_reference_library.json:4` added `"*"` alongside the explicit origins (`https://numista.ai`, `https://numista-vault.web.app`, `https://numista-vault--p7-gate-8avtpz22.web.app`). Because `gs://numista-reference-library` only serves public reference coin images via `GET`/`HEAD`, `Access-Control-Allow-Origin: *` is safe and permanently prevents preview-channel CORS blocks across future ephemeral Firebase preview URLs.

---
*Filed by: **Numista.Ai Argon** (`Gemini 4 Argon`) — **THINKING JOBS ONLY** (Plan reviews, code/build reviews, root-cause analysis, and verification audits; zero code edits or deployments).*
