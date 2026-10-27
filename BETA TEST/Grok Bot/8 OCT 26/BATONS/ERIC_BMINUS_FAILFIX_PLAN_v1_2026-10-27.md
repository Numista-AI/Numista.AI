# ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md
**DTG:** 2026-10-27 ~5:35 PM ET  
**Author:** AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`)  
**Mission:** Address the 2 P0 items that failed the Field Test in `FT_RESULT_NET627_ERIC_BMINUS_751a4305_FAIL.md`.  
**Review Chain:** AG CoS (Plan.v1) -> Argon -> GB CoS -> SAG -> Eric typed "YES" -> EXECUTE to `p7-gate` preview only.  
**Mandate:** **NO CODE / NO EXECUTE AT THIS STAGE. PLAN WRITING ONLY.**

---

## 1. Executive Summary & Root Cause Analysis (RCA)

### P0 Failure 1: I-07 / PM-01 — 26RJ Images & Baseline Valuation after Commit
* **Observation:** After committing `26RJ` (US Mint Uncirculated Coin Set 2026), the coin doc in Firestore / UI showed "Valuation Pending" ($0.00 / `—`) and "Image unavailable" (~3 min wait).
* **Root Causes:**
  1. **Image Keys Disconnect:** In `services/us_mint_catalog_service.py`, `enrich_us_mint_item()` stamped `image_url_obverse` and `image_url_reverse`. However:
     - On `/api/review/commit` and `keep_set_as_is`, Firestore coin documents and Flutter (`CoinModel`, `_CollectionCardImage`, `_buildCoinVaultGallery`) look for `image_url_obverse`, `image_url_reverse`, but when committing to the main `coins` collection, if `keep_set_as_is` or standard commit executes, `keep_set_as_is` does not run `enrich_us_mint_item` at all!
     - Furthermore, `normalize_and_validate_receipt()` sets initial review queue fields, but `enrich_us_mint_item()` only copied `image_url_obverse` if `catalog_match` matched. In `commit_reviews()` (line 3624 of `numista_backend/main.py`), `enrich_us_mint_item(data)` was called, but in `keep_set_as_is()` (line 3740 of `numista_backend/main.py`), NO catalog enrichment was invoked before committing the set! When a user or field tester commits a set via the Review Hub, depending on whether it is committed via bulk checkbox commit (`/api/review/commit`) or the "Keep as Set" action (`/api/review/keep_set_as_is`), the latter completely omitted enrichment!
     - In `commit_reviews()`, valuation baseline was set on `ai_est_value` and `estValue`, BUT `numista_mobile/lib/screens/my_collection_screen.dart` lines 3020-3022 and `_F.aiValue` check `data['AI Estimated Value']`. In commit line 3635, it set `data['ai_est_value']` and `data['estValue']`, but failed to stamp the canonical PascalCase `data['AI Estimated Value'] = f"${clean_cat_p:.2f}"`! Since `data['AI Estimated Value']` was not set, `my_collection_screen.dart` line 3022 fell back to `m[_F.aiValue]?.toString() ?? '—'`. When `valueText == '—'`, line 3169 rendered:
       `if (valueText == '—' || m['enrichment_status'] == 'pending') ... 'Valuation Pending'`!
     - In `CoinModel` (line 206 of `numista_mobile/lib/models/coin_model.dart`), `aiEstimatedValue` expects `data['ai_estimated_value'] ?? data['AI Estimated Value'] ?? 'Pending'`. But in `my_collection_screen.dart`, it specifically queried `m[_F.aiValue]` (`'AI Estimated Value'`). Thus, omitting `'AI Estimated Value'` left the grid card in "Valuation Pending".
  2. **Async Enrichment Worker Trigger:** Neither `/api/review/commit` nor `/api/review/keep_set_as_is` queued any background task or async trigger to resolve reference art / market guides post-commit.
  3. **Greysheet vs Catalog Baseline:** Sets/rolls do not exist in Greysheet price guides. As specified by Desk & SAG, Mint sets/products must establish the catalog `issue_price` ($124.50 for `26RJ`) as their first-line baseline valuation immediately on commit, with `enrichment_status = "enriched"`, so they never show $0.00 / Valuation Pending.

### P0 Failure 2: I-04b — 26SQRP Fee $0.00 on Review Hub
* **Observation:** `26SQRP` pack/roll (qty 25) displayed "Fee $0.00" on Review Hub, whereas invoice S&H was $9.95. In contrast, `26RJ` correctly showed "Fee $9.95".
* **Root Cause:**
  - In `numista_backend/main.py` lines 7717-7719:
    ```python
    # NET-565: Only pack/roll expansions waive the fee; regular Mint items (e.g. 23RH) carry Mint S&H.
    doc["allocated_fees"] = 0.0 if doc.get("pack_expanded") else allocated_fee
    doc["shipping_fee"] = 0.0 if doc.get("pack_expanded") else allocated_fee
    ```
  - This line explicitly forced `allocated_fees = 0.0` and `shipping_fee = 0.0` whenever `pack_expanded` was True!
  - Because `26SQRP` is a 25-coin roll, `enrich_us_mint_item` set `doc["pack_expanded"] = True`. Immediately afterwards, lines 7718-7719 zeroed out `allocated_fees` and `shipping_fee`.
  - When Review Hub (`review_hub_screen.dart` line 2291) rendered:
    ```dart
    final rawFee = data['allocated_fees'] ?? data['Allocated Fees'] ?? data['shipping_fee'] ?? data['Fee'] ?? data['fee'];
    ```
    it read `allocated_fees` which was `0.0`, resulting in `$0.00`!
  - For single sets like `26RJ`, `pack_expanded` was not set, so `allocated_fee` ($9.95) remained intact.
  - The zeroing logic was intended to prevent multiplying shipping across split children, but for a single roll row (which represents the entire 25-coin roll package on the hub before any split), the item represents the entire lot and must carry the allocated invoice shipping fee ($9.95).

---

## 2. Precise Proposed Code Diffs

### A. Backend Fixes (`numista_backend/main.py` & `us_mint_catalog_service.py`)

#### 1. Fix Fee Preservation on Pack/Roll Items (`numista_backend/main.py` lines 7716–7720)
* **Target:** Remove the `pack_expanded` zeroing check that zeroes `allocated_fees` and `shipping_fee`.
* **Code Change:**
  ```python
  # Preserve allocated invoice S&H on pack/roll lots (e.g. 26SQRP 25-coin roll carries $9.95)
  doc["allocated_fees"] = allocated_fee
  doc["shipping_fee"] = allocated_fee
  doc["Allocated Fees"] = allocated_fee
  ```
  *Result:* `26SQRP` retains `allocated_fees = 9.95`, displaying `Fee $9.95` on the Review Hub card, exactly like `26RJ`.

#### 2. Fix Canonical Field Stamping & Valuation Baseline on Commit (`numista_backend/main.py` lines 3622–3642)
* **Target:** Ensure `commit_reviews()` sets both snake_case and PascalCase valuation fields (`AI Estimated Value`, `ai_estimated_value`, `estValue`), and ensures catalog images (`image_url_obverse`, `image_url_reverse`) are dual-written to `primary_image_url`, `photo_urls`, and `obverse_image` if not already set.
* **Code Change:**
  ```python
  # Baseline valuation & enrichment (Plan.v2 / Plan.v3 B2 / FAIL-FIX)
  try:
      from services.us_mint_catalog_service import enrich_us_mint_item
      enrich_us_mint_item(data)
  except Exception:
      pass

  # Ensure catalog image URLs are propagated
  cat_obv = data.get('image_url_obverse')
  cat_rev = data.get('image_url_reverse')
  if cat_obv and not data.get('primary_image_url'):
      data['primary_image_url'] = cat_obv
  if cat_obv and not data.get('photo_urls'):
      data['photo_urls'] = [cat_obv] + ([cat_rev] if cat_rev else [])

  # Set baseline valuation from issue_price or cost
  cat_p = data.get('issue_price') or data.get('Sticker Price') or data.get('Cost') or data.get('Purchase Cost') or 0.0
  try:
      clean_cat_p = float(re.sub(r"[^\d.]", "", str(cat_p)))
  except Exception:
      clean_cat_p = 0.0

  if clean_cat_p > 0.0:
      formatted_val = f"${clean_cat_p:.2f}"
      data['ai_est_value'] = clean_cat_p
      data['ai_estimated_value'] = formatted_val
      data['AI Estimated Value'] = formatted_val
      data['estValue'] = formatted_val
      data['valuation_source'] = "US Mint Catalog Baseline"
      data['enrichment_status'] = "enriched"
  ```

#### 3. Mirror Enrichment & Baseline into `keep_set_as_is` (`numista_backend/main.py` lines 3762–3775)
* **Target:** In `keep_set_as_is()`, run `enrich_us_mint_item(committed)` and apply the exact same image & valuation baseline stamping so that clicking "Keep as Set" on a set item like `26RJ` also guarantees catalog images and the $124.50 baseline valuation in Firestore.
* **Code Change:**
  ```python
  # Enrich set metadata from catalog before committing
  try:
      from services.us_mint_catalog_service import enrich_us_mint_item
      enrich_us_mint_item(committed)
  except Exception:
      pass

  cat_obv = committed.get('image_url_obverse')
  cat_rev = committed.get('image_url_reverse')
  if cat_obv and not committed.get('primary_image_url'):
      committed['primary_image_url'] = cat_obv
  if cat_obv and not committed.get('photo_urls'):
      committed['photo_urls'] = [cat_obv] + ([cat_rev] if cat_rev else [])

  cat_p = committed.get('issue_price') or committed.get('Sticker Price') or committed.get('Cost') or committed.get('Purchase Cost') or 0.0
  try:
      clean_cat_p = float(re.sub(r"[^\d.]", "", str(cat_p)))
  except Exception:
      clean_cat_p = 0.0

  if clean_cat_p > 0.0:
      formatted_val = f"${clean_cat_p:.2f}"
      committed['ai_est_value'] = clean_cat_p
      committed['ai_estimated_value'] = formatted_val
      committed['AI Estimated Value'] = formatted_val
      committed['estValue'] = formatted_val
      committed['valuation_source'] = "US Mint Catalog Baseline"
      committed['enrichment_status'] = "enriched"
  ```

#### 4. Add Async Enrichment Dispatch on Commit (`numista_backend/main.py`)
* **Target:** On `/api/review/commit`, accept `BackgroundTasks` (FastAPI standard) and enqueue an async worker task `_async_post_commit_enrichment(caller_email, committed_ids)`.
* **Logic:** For any committed items that are single coins (non-sets), check if Greysheet mapping is possible and update GSID/CPG asynchronously; for sets (`26RJ`), verify baseline is intact and do not overwrite the Mint baseline with fake Greysheet calls.

---

### B. Frontend Verification & Fallback Alignment (`numista_mobile/lib/screens/my_collection_screen.dart`)

#### 1. Dual-Read for Valuation in `my_collection_screen.dart` (lines 3020–3023)
* **Target:** Update `my_collection_screen.dart` to read `cpgRetail`, `AI Estimated Value`, `ai_estimated_value`, `ai_est_value`, and `estValue`.
* **Code Change:**
  ```dart
  final valCpg = _parseNumber(m['cpgRetail']);
  final finalVal = valCpg;
  
  final fmt = intl.NumberFormat.currency(symbol: '\$');
  final rawAiVal = m[_F.aiValue] ?? m['ai_estimated_value'] ?? m['estValue'] ?? (m['ai_est_value'] != null ? fmt.format(m['ai_est_value']) : null);
  final valueText = finalVal > 0 
      ? fmt.format(finalVal) 
      : (rawAiVal?.toString() ?? '—');
  ```
  *Result:* Even if one field variation is delayed, the card immediately formats and displays `$124.50` instead of `—` / `Valuation Pending`.

#### 2. Dual-Read for Direct Images in `_CollectionCardImage` (`my_collection_screen.dart` line 6319)
* **Target:** Check `image_url_obverse`, `primary_image_url`, `obverse_image`, and `photo_urls[0]`.
* **Code Change:**
  ```dart
  final obv = _cleanUrl(data[_F.imageObverse] ?? data['primary_image_url'] ?? data['obverse_image'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).isNotEmpty ? data['photo_urls'][0] : null));
  final rev = _cleanUrl(data[_F.imageReverse] ?? data['reverse_image'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).length > 1 ? data['photo_urls'][1] : null));
  ```
  *Result:* Catalog images stamped on `26RJ` immediately render in the collection card and inspector without displaying "Image unavailable".

---

## 3. Strict Scope & Regression Protection

### What this Plan Covers:
1. **P0 (I-07 / PM-01):** `26RJ` images & $124.50 baseline valuation stamped and displayed immediately post-commit.
2. **P0 (I-04b):** `26SQRP` Fee displays $9.95 on Review Hub.

### What is Explicitly Preserved (DO NOT REGRESS):
1. **Smoke Tests:** GrokBot login, Add Coins Hub, PDF Invoice Import.
2. **Invoice Number Capture:** USM invoice number extraction and display on Review Hub.
3. **I-04c:** Edit-Cancel functionality on Review Hub.
4. **I-05:** Separation of "Add Selected" (green) and "Delete Selected" (red).
5. **I-06:** Commit button with accurate count toast.
6. **I-08 & SAG1:** Amber Possible Duplicate warning banner with reason text on SKU / invoice match.
7. **26RJ Set Fee:** Set Fee $9.95 remains 100% green.
8. **SAG3 & SAG4:** WCAG contrast on cream cards (`#F4F4F2`), Wrap-based responsive 20-coin grid for `uncirculated-coin-set-2026`.
9. **Zero Daytime Check Grounding Spend:** Night track (NET-610 Option B) strictly reserved for 8:00 PM ET.

---

## 4. Verification & Machine-Checkable Gates

Before declaring ready for another preview build, the following commands must exit code 0:
1. **Backend Tests:**
   ```bash
   pytest numista_tests/test_us_mint_catalog.py numista_tests/test_us_mint_invoice_enrichment.py
   ```
2. **Mobile Tests / Analyzer:**
   ```bash
   flutter test test/p7_v8_ux_safety_test.dart test/p7_v81815f_measured_height_test.dart
   ```
3. **Git Cleanliness:**
   ```bash
   git status
   ```

---

## 5. Next Steps & Handoff
1. AG CoS files this plan in `BATONS/`, `RADIO NET/`, and `INBOX/`.
2. Updates `WHOSE_TURN.md` to pass baton to **Argon** for review.
3. Commits and pushes docs to `dev`.
4. Arms self-wake timer for 25 minutes.
5. **NO CODE EDITS OR DEPLOYS** until Argon -> GB CoS -> SAG -> Eric typed "YES".
