# GEMINI 3.8 TECHNICAL REVIEW: `FAILFIX_PLAN_NET-647_R2.8.10_20261101.md`

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100`) — Independent Technical Reviewer & SAG Auditor
- **Plan Under Review:** [`FAILFIX_PLAN_NET-647_R2.8.10_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.10_20261101.md) (`1,442` lines)
- **Author:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Baton Reference:** `BATON_NET-728` / `BATON_NET-729` (Fix-Only `R2.8.11`)
- **Date / Time:** `2026-11-01 19:36 EST`
- **Operating Mode:** **THINKING / PLANNING / REVIEW ONLY (`NO EXECUTE`)** — Zero code edits, zero git commits/pushes, zero deployments.
- **Score:** **82 / 100 (`REVISE — FIX-ONLY R2.8.11`)** (Concurs with GB CoS [`84/100 REVISE`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647-R2.8.10_84_REVISE_20261101-1921EST.md) and Grok CoS [`77/100 REVISE`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.10_77_REVISE_20261101-1930EST.md))

---

## 1. Executive Summary & Scoring Breakdown

`FAILFIX_PLAN_NET-647_R2.8.10_20261101.md` is a major step forward from `R2.8.9` (`54/58 REVISE`): all 28 Firestore document IDs in the Section 4 ground-truth table now match [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json), all 95 live GCS rows in Section 4.1.3 match live `Content-Length` and `x-goog-hash` MD5, Kansas `2005-D` uses a strict `&&` guard, and Row 18 preserves its stored obverse while fixing the reverse to `United_States_penny_2C_reverse.jpg`.

However, independent verification against `origin/dev` (`32d4b42e`) and the live 28-row Firestore dump confirms **5 blocking defects** that prevent `R2.8.10` from clearing the $\ge 95/100$ Gate 1 bar. Below is the complete verification plus **turnkey verbatim fixes** so `AG CoS v4` (`ba2bfdb2`) can close `BATON_NET-729` (`R2.8.11`) in a single pass.

| Category | Max | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Ground-Truth Firestore & GCS Alignment** | 30 | **24** | 28/28 doc IDs & 95/95 live GCS MD5s match; `-6` for Row 10 overwriting user microscope photos (`MF-B`) and `23RH` using 404 staged primaries without hard Gate 0 cutover (`MF-3`). |
| **2. Unit Test Suite Fidelity** | 25 | **18** | `-7` for Row 03 fixture omitting `'Retailer Item No.': '26XL'` (causing `41/42` pass, Row 03 returns `null`) and Row 10 test asserting reference URLs instead of `null` user-upload guard. |
| **3. Rule 6(a) Verbatim Code Citations (`32d4b42e`)** | 25 | **19** | Section 7 cites `p7-v8.9` lines rather than `origin/dev` (`32d4b42e`) lines for 7.1, 7.2, 7.4, and 7.5 (`MF-A`). Turnkey `32d4b42e` citations provided below. |
| **4. Staging Gates & Internal Consistency** | 20 | **21/20 -> 15** | `-5` for Gate 4 (`line 1434`) saying `HTTP 200 OK` only (`MF-C`), invented MD5 in `MF10` (`line 29`), stale Row 11 doc ID/MD5 in `4.1.1` (`line 1070`), and `9b55f3d9` vs `32d4b42e` on `line 1436`. |
| **TOTAL** | **100** | **82 / 100** | **`REVISE — FIX-ONLY R2.8.11`** |

---

## 2. Turnkey Fixes for `R2.8.11` (`BATON_NET-729`)

### MUST-FIX 1 (Row 03 Unit Test Fixture & `Program / Series` Key):
- **Defect:** In `Section 3.2` (`line 624`), the `Row 03` test fixture has `'Personal Notes': 'Peace Silver Dollar 2026 Rever'` (truncated at 30 chars) and omits `'Retailer Item No.': '26XL'` (which is present on live doc `a59853c1-b72b-414d-8b8e-de6813c29996`). Because `combined.contains('reverse proof')` is `false` on `'rever'`, `CanonicalMintAssetService.resolveFromMap(doc)` returns `null` (`41/42` pass).
- **Turnkey Fix for `Section 3.1` & `Section 3.2`:**
  1. Add `'Retailer Item No.': '26XL'` (from the live Firestore doc) to the `Row 03` test fixture at `line 624`.
  2. In `Section 3.1` (`lines 133, 143, 187`), also read `'Program / Series'` (with spaces, used by 11 live docs).

### MUST-FIX 2 (Row 10 User-Upload Guard — `0172d0ee64284a12a8aa269ce805ec07`):
- **Defect:** `Section 1` (`line 21`, `MF2`) and `Section 8` (`line 1396`, `B26-11`) state that Row 10 (`2026-P Mayflower Compact`) returns `null` to preserve Eric's microscope photos (`https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/...`). However:
  - `line 21` cites the wrong doc ID (`d49bb0fd-bc3f-4e08-9df5-cf6bfd31b7cd` instead of live `0172d0ee64284a12a8aa269ce805ec07`).
  - `Section 3.1` (`lines 178-210`) has **no user-upload guard**, and `Section 3.2` (`lines 693-701`) asserts that Row 10 overwrites the microscope URLs with `2026_quarter_dollar_mayflower_compact_obverse.jpg`.
- **Turnkey Fix for `Section 3.1` (`resolveFromMap`):**
  ```dart
    final storedObv =
        (data['image_url_obverse'] ?? data['obverse_image'] ?? data['image_url'] ?? '')
            .toString()
            .trim();
    final storedRev =
        (data['image_url_reverse'] ?? data['reverse_image'] ?? '')
            .toString()
            .trim();
    // User-upload guard (MF2 / B26-11): Never overwrite personal user microscope or vault uploads
    bool isProtectedUserUpload(String u) =>
        u.contains('/microscope/') ||
        u.contains('/users/') && !u.contains('b22f8905-4eca-45e9-ba57-920fb5427b22');
    if (isProtectedUserUpload(storedObv) || isProtectedUserUpload(storedRev)) {
      return null;
    }
  ```
  *(Note: Row 11 `8f2197d5d03a428db24486b4ee375a5e` has corrupted Kennedy half stock photos stored under `users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/`, whereas Row 10 `0172d0ee64284a12a8aa269ce805ec07` has `/microscope/eric@numista.ai/...` — guarding `/microscope/` preserves Row 10 (`expect(pair, isNull)`) while still fixing Row 11!)*

### MUST-FIX 3 (`23RH` Primary URLs & Hard Gate 0 Cutover / `Gate 4` Full Verification):
- **Defect:**
  1. `23RH` (`lines 341-342`) uses staged URLs (`23rh_b.webp`, `23rh_c.webp`) that currently return `HTTP 404` until Gate 4 upload. Either use the live `2023_series` composite URLs as primary now (and swap after Gate 4) OR state an explicit hard Gate 0 cutover block in `Section 3.1` and `Section 9.2` (no code cutover until all 4 staged objects return `HTTP 200` with verified `Content-Length` and `x-goog-hash` MD5).
  2. `Section 9.2 Gate 4` (`line 1434`) only says `"Automated HTTP HEAD check on all 4 staged URLs confirming HTTP 200 OK"`, contradicting `MF6` (`line 25`). Update `line 1434` to explicitly verify URL prefix (`https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/` and `.../2023_products/`), `Content-Type: image/webp`, exact `Content-Length` bytes, and exact `x-goog-hash` MD5 against `Section 9.1`.
  3. Fix `line 1436` dev commit hash from `9b55f3d9` to `32d4b42e`.

### MUST-FIX 4 (Contradictory MD5 & Doc ID in `line 29` and `Section 4.1.1` `line 1070`):
- **Defect:**
  1. `line 29` (`MF10`) says `md5_hex: e2679b5fbb4221f6db6343f6edde9b4f` for `SemiQ-Dime-Reverse-Unc.jpg`, contradicting `Section 4` (`line 1041`) and `Section 4.1.3` (`line 1134`) where the verified live MD5 is **`8533943d7d88a011adaf372476bfe1f3`** (`hTOUPX2IoBGtrzckdr/h8w==`, `1,336,791 B`).
  2. `Section 4.1.1` (`line 1070`) still cites stale doc ID `d377b212-9c3f-42e5-b1a1-f3b145610ea0` ("2026-D Mayflower Half Dollar") with stale MD5s `7b7c2b5e...` / `73f6424e...`. Replace `line 1070` with live Row 11:
     - Doc ID: `8f2197d5d03a428db24486b4ee375a5e` (`250th Anniversary of American Independence` Half Dollar)
     - Obverse: `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`, MD5 `ef82afd24a78202697cb97ca6da3b58f`)
     - Reverse: `SemiQ-Half-Dollar-Reverse-Unc.jpg` (`1,510,409 B`, MD5 `cceb4ab85d398347792d8929fb11bed0`)

---

## 3. Turnkey Rule 6(a) Verbatim Code Citations on `origin/dev` (`32d4b42e`) (`MF-A`)

In `R2.8.10`, Section 7 cited line numbers from `origin/p7-v8.9` (`d919bcf9`). To satisfy both `origin/dev` (`32d4b42e`) and `origin/p7-v8.9` verifiers in `R2.8.11`, paste the following **exact verbatim blocks verified from `git show 32d4b42e:<path>`**:

### 7.1 [`numista_mobile/lib/screens/my_collection_screen.dart:6320-6366`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6320-L6366) (`origin/dev` `32d4b42e`)
```dart
  @override
  Widget build(BuildContext context) {
    final obv = _cleanUrl(data[_F.imageObverse] ?? data['primary_image_url'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).isNotEmpty ? data['photo_urls'][0] : null));
    final rev = _cleanUrl(data[_F.imageReverse] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).length > 1 ? data['photo_urls'][1] : null));
    final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)

    if (directUrl.isNotEmpty) {
      return _buildCoinImage(directUrl);
    }

    // Dual-read: PascalCase first, lowercase fallback for unmigrated CSV docs
    String dualRead(String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }
    final year = dualRead('year', _F.year).replaceAll(RegExp(r'\.0$'), '');
    final mint = dualRead('mint_mark', _F.mintMark);
    final denom = dualRead('denomination', _F.denomination);
    final series = dualRead('program_series', _F.programSeries);
    final subject = dualRead('theme_subject', _F.themeSubject);

    return FutureBuilder<CoinImageResult>(
      future: CoinImageService.fetchReferenceImages(
        year: year,
        mint: mint.isEmpty ? null : mint,
        denomination: denom.isEmpty ? null : denom,
        series: series.isEmpty ? null : series,
        subject: subject.isEmpty ? null : subject,
      ),
      builder: (context, snapshot) {
        final ref = snapshot.data;
        // MF-V3-3: When subject is known and reverse is null (steal-guard
        // correctly blocked a generic reverse), show placeholder instead of
        // falling back to generic obverse. Keeps obverse fallback for coins
        // without a subject (e.g. generic Morgan/Peace).
        final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                ? ref!.obverseUrl!
                : '';

        if (refUrl.isNotEmpty) {
          return _buildCoinImage(refUrl);
        }
```

### 7.2 [`numista_mobile/lib/screens/my_collection_screen.dart:3016-3023`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3023) (`origin/dev` `32d4b42e`)
```dart
        final valCpg = _parseNumber(m['cpgRetail']);
        final finalVal = valCpg;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final rawAiVal = m[_F.aiValue] ?? m['ai_estimated_value'] ?? m['estValue'] ?? (m['ai_est_value'] != null ? fmt.format(m['ai_est_value']) : null);
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (rawAiVal?.toString() ?? '—');
```

### 7.3 [`numista_mobile/lib/services/coin_image_service.dart:535-571`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L571) (`origin/dev` `32d4b42e`)
*(Include closing `}` at line `571`.)*

### 7.4 [`numista_mobile/lib/screens/review_hub_screen.dart:2283-2295`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2283-L2295) (`origin/dev` `32d4b42e`)
*(Note: The `unit_cost_cents` block cited at `2040-2059` in `R2.8.10` exists only on `origin/p7-v8.9`, not `origin/dev` `32d4b42e`. Cite the real `32d4b42e` block at `2283-2295` below and label the `p7-v8.9` block explicitly as `[p7-v8.9 d919bcf9 / PROPOSED FOR DEV]`):*
```dart
                    final rawCost = data['Purchase Cost'] ?? data['Cost'];
                    final rawSetCostLabel = (data['set_cost_label'] ?? '').toString().trim();
                    final costStr = rawSetCostLabel.isNotEmpty
                        ? rawSetCostLabel
                        : (rawCost != null
                            ? (rawCost is num ? '\$${rawCost.toStringAsFixed(2)}' : rawCost.toString())
                            : 'N/A');

                    final rawFee = data['allocated_fees'] ?? data['Allocated Fees'] ?? data['shipping_fee'] ?? data['Fee'] ?? data['fee'];
                    final feeStr = rawFee != null
                        ? (rawFee is num ? '\$${rawFee.toStringAsFixed(2)}' : (rawFee.toString().startsWith('\$') ? rawFee.toString() : '\$$rawFee'))
                        : '\$0.00';
```

### 7.5 [`numista_backend/main.py:8369-8376`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8369-L8376) (`origin/dev` `32d4b42e`)
```python
                    per_file[idx]["status"]      = "done"
                    per_file[idx]["coins_added"] = added_this_file
                    per_file[idx]["receipt_id"]  = receipt_id

                except Exception as e:
                    per_file[idx]["status"] = "error"
                    per_file[idx]["error"]  = str(e)
                    logger.error(f"Bulk import invoice error ({fname}): {e}\n{traceback.format_exc()}")
```

---

## 4. Hygiene & Formatting Fixes (`SHOULD-FIX`)
1. Remove the stray ```` ```dart ```` fence wrapping prose at `line 61` (and `line 593`).
2. Update `Section 4.1.3` header (`line 1084`) so the staged file count (`4` files in `Section 9.1`: `26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`, of which `2` are primary in `Section 4` for `23RH`) is stated without contradiction, including their local disk source path prior to Gate 4 upload.
3. Update Row 04 `Theme/Subject` / `name` column in `Section 4` (`line 1037`) to include the live title `2026 United States Mint Uncirculated Coin Set`.
