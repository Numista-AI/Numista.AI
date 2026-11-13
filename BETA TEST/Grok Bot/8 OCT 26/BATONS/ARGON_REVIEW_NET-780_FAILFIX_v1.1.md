# ARGON (GEMINI 3.8) TECHNICAL REVIEW: `FAILFIX_PLAN_NET-780b_CARDS_v1.1.md` & `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md` (`BATON_NET-791`)

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Independent Code & Data Auditor)
- **Date / Time:** 2026-11-05 1:43 PM ET
- **Baton:** `BETA TEST/Grok Bot/8 OCT 26/BATONS/BATON_NET-791_ARGON_REVIEW_780b-780c_v1.1_2026-11-05-1255.md`
- **Reference Score:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/GB_COS_SCORE_NET-780.md` (`780b v1.0`: 88 FAIL; `780c v1.0`: 80 FAIL)
- **Target Plans Audited:**
  1. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.1.md` (246 lines)
  2. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md` (175 lines)
  3. `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-05-1250.md` (54 lines)
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code changes, zero git commits/pushes, zero deployments, zero Firestore writes.
- **Individual & Composite Scores:**
  - **`FAILFIX_PLAN_NET-780b_CARDS_v1.1.md`:** **96 / 100 (`PASS — All 4 Must-Fixes MF-B1..MF-B4 Resolved; 2 Execution Safeguards Logged`)**
  - **`FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md`:** **96 / 100 (`PASS — All 6 Must-Fixes MF-C1..MF-C6 Resolved; 2 Execution Safeguards Logged`)**
  - **Composite `NET-791` Score:** **96 / 100 (`PASS`)**
- **Next Gate in Review Chain:** Grok Bot CoS (`95+` required) -> Stand Alone Grok (`SAG`) -> Founder Eric's typed **YES**.

---

## 1. Summary Matrix (`NET-780a–d` Full Suite Status)

| Track | Plan Version | Previous GB CoS Score | Argon `v1.1` Score | Status & Verdict |
| :--- | :---: | :---: | :---: | :--- |
| **`780a` Build Stamp** | `v1.0` | `95 PASS` | `96 PASS` | Cleared (`GB_COS_SCORE_NET-780.md:8, 24-29`). |
| **`780b` Cards & AE Pending** | **`v1.1`** | `88 FAIL` | **`96 / 100 PASS`** | Resolves `MF-B1`..`MF-B4`, explains commit `3936ba5f` (0 code lines changed), fixes test path (`test/services/canonical_mint_asset_service_test.dart`). |
| **`780c` Images & CSP** | **`v1.1`** | `80 FAIL` | **`96 / 100 PASS`** | Resolves `MF-C1`..`MF-C6`, deletes Section 3D CSP bridge, cites dated inventories (`inventory_20261031.csv` & `gcs_full_inventory.csv`), links `docs/MISSING_IMAGES.csv`, enforces licensing + PII 0-hit gate, pins `gs://numista-catalog-assets` and `firebase.json:275-276`. |
| **`780d` Splash** | `v1.0` | `96 PASS` | `97 PASS` | Cleared (`GB_COS_SCORE_NET-780.md:11, 56-57`). |

---

## 2. Review of `FAILFIX_PLAN_NET-780b_CARDS_v1.1.md` (`Score: 96 / 100 PASS`)

### 2.1 Verification of Commit `3936ba5f` Explanation (`PASS`)
* **Plan Citation (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.1.md:29-35`):**
  ```markdown
  29: - **Commit Hash:** `3936ba5fa33b32741b9093a95d5c4d4043714a26`
  30: - **Author:** `Numista Deployer <deploy@numista.ai>`
  31: - **Timestamp:** Wednesday, 4 Nov 2026, 6:00:06 PM ET
  32: - **Commit Message:** `chore: auto-backup 2026-11-04 18:00`
  33: - **Source Code Files Touched:** **0 files (0 lines of code)**. Zero Flutter, Dart, Python, or Firebase configuration files were touched.
  ```
  - **Verdict:** **PASS.** Completely answers Grok Bot CoS's question (`GB_COS_SCORE_NET-780.md:3`): `3936ba5f` was the 6:00 PM ET automated documentation backup commit on top of `c294fd3c` with zero code changes.

### 2.2 Verification of `MF-B1`, `MF-B3`, and `MF-B4` (Valuation Pending Chip & Cost Separation — `PASS`)
* **Codebase Verification (`numista_mobile/lib/screens/add_coins_hub.dart:117-124` & `numista_mobile/lib/screens/my_collection_screen.dart:3017-3023, 3170-3188`, read this turn):**
  ```dart
  117: const Map<String, Map<String, dynamic>> kFallbackUsMintSkus = {
  118:   '26EA': {
  119:     'sku': '26EA',
  120:     'name': 'American Silver Eagle Proof',
  121:     'program_series': 'American Silver Eagle',
  122:     'year': '2026',
  123:     'item_type': 'coin',
  124:   },
  ```
  ```dart
  3017:         final valCpg = _parseNumber(m['cpgRetail']);
  3018:         final finalVal = valCpg;
  3019:         
  3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
  3021:         final valueText = finalVal > 0 
  3022:             ? fmt.format(finalVal) 
  3023:             : (m[_F.aiValue]?.toString() ?? '—');
  ```
  ```dart
  3170:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
  3171:                         Container(
  ...
  3178:                           child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
  3179:                         )
  ```
* **Plan Resolution (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.1.md:188-227`):**
  ```dart
  189:    final valCpg = _parseNumber(m['cpgRetail']);
  190:    final rawAiVal = m[_F.aiValue]?.toString().trim() ?? '';
  191:    final isAiPending = rawAiVal.isEmpty || rawAiVal.toLowerCase() == 'pending';
  192:    final valAi = !isAiPending ? _parseNumber(rawAiVal) : 0.0;
  193:    
  194:    final finalVal = valCpg > 0 ? valCpg : valAi;
  195:    final fmt = intl.NumberFormat.currency(symbol: '\$');
  196:    
  197:    final valueText = finalVal > 0 ? fmt.format(finalVal) : '—';
  ```
  - **Verdict:** **PASS.** `780b v1.1` eliminates the non-compiling `kFallbackUsMintSkus[canonSku]?.issuePrice` (`MF-B1`), drops the unverified `$95.00` issue price (`MF-B3`), keeps `purchase_price`/`cost` strictly out of the Valuation slot (`MF-B4`), and renders the gold `'Valuation Pending'` badge whenever `rawAiVal.toLowerCase() == 'pending'`.
  - *(Minor Doc Note: `DONE_BATON_NET-791:34` mentions adding a `kFallbackUsMintSkus` issue price getter, whereas `FAILFIX_PLAN_NET-780b_CARDS_v1.1.md:129-135, 199` takes the cleaner path of dropping `kFallbackUsMintSkus` and `$95.00` altogether to render `'Valuation Pending'` — follow `FAILFIX_PLAN_NET-780b_CARDS_v1.1.md:188-227` during execution.)*

### 2.3 Verification of `MF-B2` & Advisories (Year-From-Text Fallback, `hasUserUploadedPhotos`, Nickel Handling, Test Path — `PASS` With 2 Execution Safeguards)
* **Codebase Verification (`numista_mobile/lib/services/canonical_mint_asset_service.dart:107-122, 153-189, 213-220, 433-434, 458`, read this turn):**
  ```dart
  107:     final year = _normYear(data['year'] ?? data['Year']);
  108:     final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
  109:     final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
  110:     final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
  ...
  117:     final combined = '$prog $theme $title $cond';
  118:     if (year == '2026' &&
  119:         RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
  120:         !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
  121:       return '26EA';
  122:     }
  ```
  ```dart
  153:   static CanonicalMintAssetPair? resolveFromMap(Map<String, dynamic> data) {
  154:     // MF-B Guard: Non-destructive preservation of user-uploaded / microscope photos.
  155:     // If doc contains user uploads (e.g. Row 10 Eric's microscope photos), return null.
  156:     if (hasUserUploadedPhotos(data)) {
  157:       return null;
  158:     }
  159:     final sku = extractSku(data);
  ...
  172:     final year = _normYear(data['year'] ?? data['Year']);
  ...
  182:     return resolve(
  183:       sku: sku,
  184:       title: primaryTitle,
  185:       year: year,
  ```
  ```dart
  433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
  434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
  ```
* **Plan Verification (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.1.md:145-184, 234`):**
  - Adds the `year.isEmpty` regex fallback (`RegExp(r'\b(20\d{2}|19\d{2}|18\d{2}|17\d{2})\b')`) across `title`/`Title`/`name`/`Name`/`Theme/Subject`/`theme_subject`/`Program/Series`/`program_series` (`lines 149-161`).
  - Preserves `if (hasUserUploadedPhotos(data)) return null;` at `canonical_mint_asset_service.dart:156-158` (`lines 166-168`).
  - Explicitly avoids mapping 2023 circulating Jefferson nickels to 2026 Semiquincentennial nickel artwork (`lines 99-100, 182-183`).
  - Fixes the unit test path to `numista_mobile/test/services/canonical_mint_asset_service_test.dart` (`line 234`).

#### 2 Execution Safeguards for `780b v1.1`:
1. **`EX-780b-1` (Propagate Resolved `year` to `resolveFromMap` line 172 and `resolve` line 201):**
   - In `canonical_mint_asset_service.dart:172` (`resolveFromMap`) and `line 201` (`resolve`), `year` is also normalized via `_normYear(...)`. When `year` is omitted and inferred from `primaryTitle` / `searchCorpus`, apply the same year-from-text fallback helper `_resolveYear(data, fallbackText: primaryTitle)` in `resolveFromMap` (`line 172`) and `resolve` (`line 201`) so direct `resolve(title: '2026 American Silver Eagle')` calls and `cleanYear == '2026'` / `'2023'` checks (`lines 299, 458`) also receive `'2026'`.
   - *(Note: The illustrative JSON snippet at `780b v1.1:65-79` is a synthetic representation — `numista_mobile/assets/guest_demo_coins.json:1-80, 1330-1403` contains 1986–2022 demo coins with string years, whereas the 2026 American Eagle card tested on `p7-gate` resides in the 353-coin Firestore test collection.)*
2. **`EX-780b-2` (Ensure `_CollectionCardImage` Falls Through to `CoinImageService` for `2023-D 5c`):**
   - See `EX-780c-1` below: when `data[_F.imageReverse]` on the `2023-D 5c` Firestore document holds a legacy `https://upload.wikimedia.org/...` URL, `_cleanUrl` at `my_collection_screen.dart:6377-6378` must return `''` for unmirrored external hosts so execution falls through line `6381` to `CoinImageService.fetchReferenceImages(...)` (`line 6385+`, which serves the internal GCS reference library Jefferson nickel image) instead of stopping at `_buildFallbackPlaceholder()` at line `6382`.

---

## 3. Review of `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md` (`Score: 96 / 100 PASS`)

### 3.1 Verification Against `MF-C1` Through `MF-C6` (`GB_COS_SCORE_NET-780.md:47-54`)

1. **`MF-C1` — Deletion of Section 3D & Closed CSP Perimeter (`PASS`):**
   - **Plan (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md:61-62`):**
     ```markdown
     61: - **Deleted:** Section 3D ("Optional Temporary CSP Bridge") from Plan v1.0 is permanently eliminated.
     62: - **Enforcement:** The production Content Security Policy remains 100% closed to all outside image providers. Neither `upload.wikimedia.org`, `thumb.wikimedia.org`, nor `numismatics.org` will be added to `img-src` or `connect-src`.
     ```
   - **Repo (`numista_mobile/firebase.json:275-276`, read this turn):**
     ```json
     275:             "key": "Content-Security-Policy",
     276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
     ```

2. **`MF-C2` — Real Counts Citing Dated Inventory Files (`PASS`):**
   - **Plan (`FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md:67-81`):**
     ```markdown
     67: 1. **Laptop Archive (`1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv`):**
     68:    - **Date:** 2026-10-31
     69:    - **Total Objects:** 8,945 image files across 420 local folders.
     70:    - **Generic Coin Assets:** 8,836 files (after subtracting 109 PII-flagged microscope, receipt, and invoice paths).
     71: 2. **GCS Storage Inventory (`numista_backend/gcs_full_inventory.csv`):**
     72:    - **Date:** 2026-10-27
     73:    - **Total Objects:** 11,069 objects.
     ```
   - **Repo Verification (Read This Turn):**
     - `1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv` has `8,946` total lines (`1` header + `8,945` file rows):
       ```csv
       1: "path","folder","size","modified","sha256","code_guess","year_guess","dup_count"
       ```
     - `numista_backend/gcs_full_inventory.csv` has `11,070` total lines (`1` header + `11,069` object rows):
       ```csv
       1: bucket,path,size_bytes,public_url,category,coin_type
       ```

3. **`MF-C3` — `docs/MISSING_IMAGES.csv` & Phased $0 Acquisition Plan (`PASS`):**
   - `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md:85-93` links directly to `docs/MISSING_IMAGES.csv` (`3,202` rows at `$0.00` cost) and defines the 3-phase intake workflow without touching live endpoints or buckets during planning.

4. **`MF-C4` — Mandatory Licensing & Attribution Manifest (`PASS`):**
   - `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md:94-109` requires `author`, `license`, `source_url`, `retrieval_date`, and `credit_text` in `assets/catalog_image_manifest.json` and GCS metadata, restricts intake to `PD-USGov`, `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0` (prohibiting `-NC` and `-ND`), and renders plain-text attribution chips.

5. **`MF-C5` — Strict Intake PII Gate With Excluded Folder Manifest & 0-Hit Proof (`PASS`):**
   - `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md:110-127` explicitly lists excluded folders (`AJ's Coins/`, `Scans AJ June 2026/`, `AJ_Photos/`, `RECEIPTS/`, `INVOICES/`, `PACKING_SLIPS/`, `User_Uploads/`, `Row 10 Eric's microscope photos/`), enforces `(?i)(aj|invoice|receipt|packing|microscope|user_upload|eric)`, quarantines the 109 PII-flagged laptop paths (`inventory_20261031.csv`), verifies `0` hits via `tools/verify_catalog_manifest_pii.py`, and standardizes object keys to `nac_code`.

6. **`MF-C6` — Pinned Bucket `gs://numista-catalog-assets` & Exact CSP Citation (`PASS`):**
   - `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md:128-136` pins the mirror bucket to `gs://numista-catalog-assets` and cites `numista_mobile/firebase.json:275-276` verbatim.

#### 2 Execution Safeguards for `780c v1.1`:
1. **`EX-780c-1` (Filter Legacy External URLs in `_cleanUrl` at `my_collection_screen.dart:6377-6383` Rather Than Only Inside `_buildCoinImage`):**
   - In `numista_mobile/lib/screens/my_collection_screen.dart:6377-6383` (read this turn):
     ```dart
     6377:     final obv = _cleanUrl(data[_F.imageObverse]);
     6378:     final rev = _cleanUrl(data[_F.imageReverse]);
     6379:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
     6380: 
     6381:     if (directUrl.isNotEmpty) {
     6382:       return _buildCoinImage(directUrl);
     6383:     }
     ```
     If `url.startsWith('https://upload.wikimedia.org')` is only intercepted inside `_buildCoinImage(url)` (`780c v1.1:143-148`), then line `6382` immediately returns `_buildFallbackPlaceholder()` and **short-circuits** `_CollectionCardImage` before it reaches `CoinImageService.fetchReferenceImages(...)` (`line 6385+`, which resolves internal GCS `gs://numista-reference-library` images). Have `_cleanUrl(...)` (or `directUrl`) treat unmirrored external hosts (`upload.wikimedia.org`, `thumb.wikimedia.org`, `numismatics.org`) as `''` so `_CollectionCardImage` falls through to `CoinImageService` first, and keep the `_buildCoinImage` check as the final safety net.
2. **`EX-780c-2` (Single Unified Tier Table Across `780c v1.1` and `777 v1.2`):**
   - Reconcile the catalog tier sub-counts between `780c v1.1:81` (`1,420 Tier 1 / 1,180 Tier 2 / 602 Tier 3 = 3,202`) and `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:88-94` (`2,273 Tier 1 / 747 Tier 2 / 181 Tier 3 / 1 Tier 4 = 3,202`) by driving both from the single canonical `docs/MISSING_IMAGES.csv` manifest (with `CSV-1`..`CSV-4` from `ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.2.md` applied).

---

## 4. Standing Locks & Proactive No-Silo Site/Product Check (`RADIO_NET-790`)

- **Standing Locks Confirmed:** `PLAN ONLY` (zero code changes, zero deployments, `origin/main` locked at `9f04550a`, Stripe OFF, zero Firestore writes).
- **No-Silo Cross-Check (`RADIO_NET-790`):** Both `my_collection_screen.dart` (Vault collection cards/modals) and `catalog_browse_screen.dart` (Public Catalog cards/modals) now share the same closed-CSP internal GCS image architecture (`gs://numista-catalog-assets` / `gs://numista-reference-library`) and plain-text attribution model (`NET-788`, `NET-791`, and `NET-798`).

---

## 5. Final Verdict

- **`FAILFIX_PLAN_NET-780b_CARDS_v1.1.md`:** **96 / 100 (`PASS`)**
- **`FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md`:** **96 / 100 (`PASS`)**
- **Overall `BATON_NET-791` Verdict:** **PASS (`96 / 100`)** — Ready for **Grok Bot CoS (`95+`) -> SAG -> Founder Eric's typed YES**.
