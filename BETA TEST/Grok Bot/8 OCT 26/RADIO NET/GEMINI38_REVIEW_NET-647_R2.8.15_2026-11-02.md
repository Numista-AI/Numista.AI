# GEMINI 3.8 TECHNICAL REVIEW — NET-647 R2.8.15
**File:** `GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md`  
**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**Date:** 2 November 2026 (15:44 ET)  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.15_20261102.md) (`172,380 B`, `1634` lines)  
**Parent Batons:** [`BATON_NET-739_GROKCOS-ARGON_NET-647-R2.8.15-REVIEW_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-739_GROKCOS-ARGON_NET-647-R2.8.15-REVIEW_20261102.md), [`BATON_NET-738_AG_NET-647-R2.8.15-FIX-ONLY_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-738_AG_NET-647-R2.8.15-FIX-ONLY_20261102.md)  
**Verdict:** **`88/100 — REVISE (GENERATE R2.8.16 FROM R2.8.15 BASELINE)`**

---

## 1. Executive Summary & Score Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. R2.8.13 Baseline Integrity & Authentic 28-Row Restoration** | 25 | **25 / 25** | `AG CoS v4` properly restored `R2.8.13` as the editing baseline: all 28 authentic rows (`doc_id`, `account`, `title`, and full Firestore maps from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`) are back in §3.2 (`lines 660–1177`) and §4 (`lines 1188–1215`), all 5 verbatim `GEMINI.md Rule 6(a)` repository code citations are restored in §7 (`lines 1403–1538`), §6 true byte sizes (`lines 1385–1395`) are restored, and §9.2 (`lines 1595–1626`) has the executable Python Gate 4 script with footer `**END PLAN R2.8.15**` (`line 1634`). |
| **2. Cross-Section Consistency (§3.1 vs §3.2 vs §4 vs §4.1.1 vs §8)** | 25 | **18 / 25** | **-7 pts (`MF-1`, `MF-4`):** Several edits claimed in Section 1 (`R15-04`, `R15-12`, `R15-14`) were applied in §1/§3.1/§3.2 but **left unapplied in §4, §4.1.1, §8, and §9.2 Gate 6**. Specifically: §4 Row 01 (`line 1188`) still lists `26EA_image_3.jpg` instead of `26ea_b.webp`; §4 Rows 02 & 26 (`lines 1189, 1213`) still list `26XE_image_1.jpg` instead of `26xe_b.webp`; §4 Row 28 (`line 1215`) lists `168,246 B (md5: 84a7e289bf...)` and `164,146 B (md5: e928a6fcfc...)` on the `23RH` composite JPGs instead of `711,501 B (md5: 1e65934dca…)` and `584,055 B (md5: beb40fba68…)`; and §4.1.1 (`lines 1223–1227`) & §8 (`lines 1545–1576`) still reflect `R2.8.13` values. |
| **3. Section 4.1.3 GCS & Staged Asset Inventory Completeness** | 25 | **21 / 25** | **-4 pts (`MF-2`):** Section 4.1.3 (`lines 1242–1247`) has two conflicting summary bullets (`114 assets (110 live in GCS + 4 local staged WebPs)` right above `108 distinct objects / 104 / 108 paths`), and the actual table (`lines 1252–1348`) still has only **97 rows** from `R2.8.13`! As a result, 8 active paths referenced in §3.1/§3.2/§4/§6 (`SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, `2026-semiq-dime-obverse-unc-d.webp`, `26ea_b.webp`, `26xe_b.webp`, `26rj_a.webp`, and 4 dated ATB obverse JPGs) are missing from the §4.1.3 table, and `23rh_b.webp` / `23rh_c.webp` (`lines 1303–1304`) still say `N/A (Staged)` instead of their measured local byte sizes and MD5s. |
| **4. Resolver Safety (`extractSku` `$notes` & Self-Fallbacks)** | 25 | **24 / 25** | **-1 pt (`MF-3`):** In Section 3.1 (`lines 204–206`), `extractSku` still includes `$notes` in `final combined = '$prog $theme $notes $title';`, contradicting `SAG MF-5` and Section 2/3 claims that `Personal Notes` cannot hijack theme matching. Also, 4 SKUs in §3.1 (`1962-LINCOLN-1C` line 543, `ATB` line 643, `26SQRP` line 377, `26RH` line 398) still set `fallbackReverseUrl` to byte-identical or cross-side self-duplicates instead of `null`. |
| **TOTAL** | **100** | **`88 / 100`** | **`REVISE` — Fix `MF-1` through `MF-4` in `R2.8.16` directly on top of `R2.8.15`.** |

---

## 2. Mandatory Surgical Fixes for `R2.8.16` (`MF-1` through `MF-4`)

> [!IMPORTANT]
> **Start `R2.8.16` strictly from `FAILFIX_PLAN_NET-647_R2.8.15_20261102.md` (`1634` lines).** Do **not** drop or summarize any rows in §3.2, §4, or §7. Apply only the 4 surgical fixes below.

### `MF-1` — Fix Section 4 Table Rows 01, 02, 26, and 28 (`lines 1188, 1189, 1213, 1215`) to Match Section 3.1/3.2 and True MD5/Byte Sizes

1. **Row 01 (`line 1188`, `26EA`):**
   - **Current `R2.8.15` (`line 1188`):** Fallback Reverse says `reference_library/us_mint_official/2026_products/26EA_image_3.jpg` (`39,656 B`, `md5: dc9e349730…`).
   - **Required in `R2.8.16`:** Update Fallback Reverse in Row 01 (`line 1188`) to match §3.1 (`line 305`) and §3.2 (`line 672`):
     `reference_library/us_mint_official/2026_products/26ea_b.webp` (`164,146 B`, `md5: 62ad11e997…`, `STAGED Gate 4`)
2. **Row 02 (`line 1189`, `26XE`) and Row 26 (`line 1213`, `26XE`):**
   - **Current `R2.8.15` (`lines 1189, 1213`):** Fallback Reverse says `reference_library/us_mint_official/2026_products/26XE_image_1.jpg` (`28,284 B`, `md5: 25d6b7c5cb…`).
   - **Required in `R2.8.16`:** Update Fallback Reverse in Row 02 (`line 1189`) and Row 26 (`line 1213`) to match §3.1 (`line 315`) and §3.2 (`lines 682, 967`):
     `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a…`, `STAGED Gate 4`)
3. **Row 28 (`line 1215`, `23RH`):**
   - **Current `R2.8.15` (`line 1215`):** Lists wrong byte sizes and fake MD5s next to the two 2023 composite JPGs:
     - `reference_library/bulk_programs/2023_american_women_quarters_five_honorees_composite.jpg` (`168,246 B` (`md5: 84a7e289bf...`))
     - `reference_library/bulk_programs/2023_american_innovation_four_states_composite.jpg` (`164,146 B` (`md5: e928a6fcfc...`))
   - **Required in `R2.8.16`:** Replace with the authentic GCS byte sizes and MD5s already verified in Section 4.1.3 (`lines 1252, 1259`) and Section 9.1 (`lines 1585–1586`):
     - Primary Obverse: `reference_library/bulk_programs/2023_american_women_quarters_five_honorees_composite.jpg` (`711,501 B`, `md5: 1e65934dca…`)
     - Primary Reverse: `reference_library/bulk_programs/2023_american_innovation_four_states_composite.jpg` (`584,055 B`, `md5: beb40fba68…`)
     - Fallback Obverse: `reference_library/us_mint_official/2023_products/23rh_b.webp` (`226,854 B`, `md5: 8a2060d0ca…`, `STAGED Gate 4`)
     - Fallback Reverse: `reference_library/us_mint_official/2023_products/23rh_c.webp` (`161,734 B`, `md5: 08f5b5aaf6…`, `STAGED Gate 4`)

---

### `MF-2` — Replace the 97-Row Table in Section 4.1.3 (`lines 1242–1348`) with the Complete 114-Row Asset Table

In `R2.8.15` (`lines 1242–1247`), two conflicting summary bullets appear back-to-back (`114 assets (110 live in GCS + 4 local staged WebPs)` followed by `108 distinct objects / 104 / 108 paths`), and the table below (`lines 1252–1348`) still has only **97 rows** from `R2.8.13`.

**Required in `R2.8.16`:**
1. Remove the stale `108 distinct objects / 104 / 108 paths` bullet (`lines 1244–1246`) so Section 4.1.3 has a single, consistent header stating **114 total assets (`110 HTTP 200 LIVE in GCS + 4 local staged WebPs uploaded in Gate 4`)**.
2. Replace the 97-row table (`lines 1252–1348`) with the complete **114-row** table (which `AG CoS v4` already compiled in `R2.8.14` `lines 1306–1419`), ensuring:
   - All 9 missing paths are included with their exact byte sizes and hex MD5s:
     - `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg` (`1477632`, `b577eb5168da5dbabef488116bb6a6e1`, `HTTP 200 LIVE`)
     - `reference_library/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp` (`154614`, `5752ab82ee56301b9244ca4718da579f`, `HTTP 200 LIVE`)
     - `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-proof-obverse-s.jpg` (`2487255`, `58325f5856be1b8f0db7ae853a60e865`, `HTTP 200 LIVE`)
     - `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg` (`2095043`, `3ca6e745910b724b04569cc8df6fd53e`, `HTTP 200 LIVE`)
     - `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg` (`1987510`, `805c83cbbe92b12be9c9798718ca53c2`, `HTTP 200 LIVE`)
     - `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg` (`1297007`, `d7cd4dc269a0dc5c4b47fa2642573594`, `HTTP 200 LIVE`)
     - `reference_library/us_mint_official/2026_products/26rj_a.webp` (`244540`, `20462bf36da4b28ef9a9da78eb17134e`, `HTTP 200 LIVE`)
   - All 4 local staged WebPs list `STAGED (Gate 4 Upload)` (honest pre-cutover status, **not** `HTTP 200 LIVE`) **and** their measured local byte sizes and hex MD5s (not `N/A (Staged)`):
     - `reference_library/us_mint_official/2023_products/23rh_b.webp` | `STAGED (Gate 4 Upload)` | `226854` | `8a2060d0ca5987b0faf0d8828ece365f`
     - `reference_library/us_mint_official/2023_products/23rh_c.webp` | `STAGED (Gate 4 Upload)` | `161734` | `08f5b5aaf698936913e2a24743dbdea5`
     - `reference_library/us_mint_official/2026_products/26ea_b.webp` | `STAGED (Gate 4 Upload)` | `164146` | `62ad11e997ac0320b57091e3d108d3e0`
     - `reference_library/us_mint_official/2026_products/26xe_b.webp` | `STAGED (Gate 4 Upload)` | `245878` | `3a77694c9a72e6db63811c8b001edbb5`

---

### `MF-3` — Remove `$notes` from `combined` in Section 3.1 `extractSku` (`lines 204–206`) & Null Out Self-Duplicate Fallbacks (`lines 377, 398, 543, 643`)

1. **Remove `$notes` from `combined` (`lines 204–206`):**
   - **Current `R2.8.15` (`lines 204–206`):**
     ```dart
     final notes = (data['Personal Notes'] ?? data['personal_notes'] ?? '').toString().toLowerCase();
     final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
     final combined = '$prog $theme $notes $title';
     ```
   - **Required in `R2.8.16`:** Delete `final notes = ...;` at line 204 and set:
     ```dart
     final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
     final combined = '$prog $theme $title';
     ```
     *(Verification: All 28 authentic rows still resolve 100% identically because Rows 01/07/25/27 match explicit SKU tokens in `lines 185–200` and Rows 05/06/28 match `Program/Series`.)*
2. **Null out the 4 remaining self-duplicate / cross-side duplicate `fallbackReverseUrl` entries in Section 3.1:**
   - `26SQRP` (`line 377`): set `fallbackReverseUrl: null,` (currently `2026-semiq-quarters-reverse-pilgrims.jpg`, which is already `fallbackObverseUrl` on line 376). Update §3.2 Row 05 (`line 728`) and §4 Row 05 (`line 1192`) to `isNull` / `null`.
   - `26RH` (`line 398`): set `fallbackReverseUrl: null,` (currently `2026_american_innovation_four_coins_composite.jpg`, which is already `fallbackObverseUrl` on line 397). Update §3.2 Row 06 (`line 740`) and §4 Row 06 (`line 1193`) to `isNull` / `null`.
   - `1962-LINCOLN-1C` (`line 543`): set `fallbackReverseUrl: null,` (currently `1962_lincoln_memorial_cent_reverse.jpg`, byte-identical self-fallback to `reverseUrl` on line 541). Update §3.2 Row 13 (`line 829`) and §4 Row 13 (`line 1200`) to `isNull` / `null`.
   - `ATB` (`line 643`): set `fallbackReverseUrl: null,` (currently `rev.url`, self-fallback to `reverseUrl` on line 641). Update §3.2 Rows 15–25 & 27 (`lines 853, 865, 877, 889, 901, 913, 925, 937, 949, 959, 976, 1175`) and §4 Rows 15–25 & 27 (`lines 1202–1212, 1214`) to `isNull` / `null`.

---

### `MF-4` — Sync Section 4.1.1 (`lines 1223–1227`), Section 3.2 Half-Dollar Catalog Test, Section 8 (`lines 1545–1576`), and Section 9.2 Gate 6 (`line 1628`)

1. **Section 4.1.1 (`lines 1223–1227`):**
   - Update to explain that Row 11 (`8f2197d5d03a428db24486b4ee375a5e`) is preserved non-destructively via `hasUserUploadedPhotos` (`resolveFromMap` returns `null`), while clean `2026-HALF-D` / `2026-HALF-P` catalog lookups resolve to `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,341,259 B`, `md5: 7a3e675fa02ab1ba430e27e963d93da7`) / `SemiQ-Half-Dollar-Obverse-Unc-P.jpg` (`1,477,632 B`, `md5: b577eb5168da5dbabef488116bb6a6e1`) and `SemiQ-Half-Dollar-Reverse-Unc.jpg` (`1,603,328 B`, `md5: c80e8f5829a0df5c72abfb65361534a9`), with `fallbackReverseUrl: null`.
2. **Section 3.2 (`after line 818`):**
   - Add a `test('Row 11 Reference Resolution: 2026-HALF-D Catalog Lookup (Without User Photos)', ...)` test verifying clean `2026-HALF-D` resolution (`SemiQ-Half-Dollar-Obverse-Unc-D.jpg` / `SemiQ-Half-Dollar-Reverse-Unc.jpg` / `SemiQ-Half-Dollar-Obverse-Unc-P.jpg` / `null`), mirroring `Row 10 Reference Resolution` at `line 786`. Update the test count in `lines 70, 91, 664` (`30 unit tests: 28 live row tests + 2 clean catalog reference tests`).
3. **Section 8 (`lines 1545–1576`):**
   - Update the table header (`line 1545`) from `Resolution in R2.8.13` to `Resolution in R2.8.16`, and sync:
     - `B26-6` (`line 1552`): `26rj_e.jpg / 26rj_b.jpg (fallback 26RJ_image_1.jpg / 26RJ_image_2.jpg)`
     - `B26-12` (`line 1558`): `Row 11 user microscope photos preserved via hasUserUploadedPhotos guard; clean 2026-HALF-D resolves to SemiQ-Half-Dollar-Obverse-Unc-D.jpg`
     - `B26-13` (`line 1559`): `SemiQ-Half-Dollar-Obverse-Unc-P.jpg (fallback 2026_half_dollar_enduring_liberty_obverse.jpg)`
     - `B26-15..B26-19` (`lines 1561–1565`): `Dated 2019-P / 2020-P / 2013-P / 2018-P ATB obverse + park reverse`
     - `B26-25` (`line 1571`): `Undated America_the_Beautiful_quarter_2C_obverse.jpg (fallback 50_State_and_Territories_quarter_obverse__28Denver_29.jpg)`
     - `B26-27` (`line 1573`): `2023 composite primaries + staged 23rh_b.webp / 23rh_c.webp fallbacks`
4. **Section 9.2 Gate 6 (`line 1628`):**
   - Update `line 1628` from `` `origin/dev` tip remains at `32d4b42e` `` to `` `origin/dev` tip at `01a03f90` (source code tree identical to `32d4b42e`) ``.

---

## 3. Verbatim Code Citations Checked (`GEMINI.md Rule 6(a)`)

All repository citations in Section 7 of `R2.8.15` (`lines 1403–1538`) were verified against `git show 01a03f90:<path>`:

### 3.1 `lib/screens/my_collection_screen.dart:6320-6366` (`_editCoin` image preservation)
```dart
6320:     String? finalFrontUrl = _resolveImageUrl(
6321:       data['frontImageUrl'] ?? data['front_image_url'] ?? data['image_url'],
6322:     );
6323:     String? finalBackUrl = _resolveImageUrl(
6324:       data['backImageUrl'] ?? data['back_image_url'],
6325:     );
6326:     try {
6327:       if (newFrontPhoto != null) {
6328:         final bytes = await newFrontPhoto!.readAsBytes();
6329:         finalFrontUrl = await _apiService.uploadCoinPhoto(
6330:           bytes: bytes,
6331:           filename: 'front_${DateTime.now().millisecondsSinceEpoch}.jpg',
6332:         );
6333:       }
6334:       if (newBackPhoto != null) {
6335:         final bytes = await newBackPhoto!.readAsBytes();
6336:         finalBackUrl = await _apiService.uploadCoinPhoto(
6337:           bytes: bytes,
6338:           filename: 'back_${DateTime.now().millisecondsSinceEpoch}.jpg',
6339:         );
6340:       }
6341:     } catch (e) {
6342:       if (mounted) {
6343:         ScaffoldMessenger.of(context).showSnackBar(
6344:           SnackBar(
6345:             content: Text('Photo upload failed: $e'),
6346:             backgroundColor: Colors.redAccent,
6347:           ),
6348:         );
6349:       }
6350:       return;
6351:     }
6352: 
6353:     final updatedData = Map<String, dynamic>.from(data);
6354:     updatedData['title'] = titleCtrl.text.trim();
6355:     updatedData['name'] = titleCtrl.text.trim();
6356:     updatedData['estimated_value'] =
6357:         double.tryParse(valCtrl.text.trim()) ?? 0.0;
6358:     if (finalFrontUrl != null) {
6359:       updatedData['frontImageUrl'] = finalFrontUrl;
6360:       updatedData['front_image_url'] = finalFrontUrl;
6361:       updatedData['image_url'] = finalFrontUrl;
6362:     }
6363:     if (finalBackUrl != null) {
6364:       updatedData['backImageUrl'] = finalBackUrl;
6365:       updatedData['back_image_url'] = finalBackUrl;
6366:     }
```

### 3.2 `lib/screens/my_collection_screen.dart:3016-3023` (`_resolveImageUrl` pass-through)
```dart
3016:   String? _resolveImageUrl(dynamic raw) {
3017:     if (raw == null) return null;
3018:     final s = raw.toString().trim();
3019:     if (s.isEmpty || s == 'null') return null;
3020:     if (s.startsWith('http://') || s.startsWith('https://')) return s;
3021:     if (s.startsWith('assets/')) return s;
3022:     return '${ApiService.baseUrl}/images/$s';
3023:   }
```

### 3.3 `lib/services/coin_image_service.dart:535-571` (`_buildSingleCoinImage` fallback chain)
```dart
535:   static Widget _buildSingleCoinImage({
536:     required String imageUrl,
537:     String? fallbackUrl,
538:     required double size,
539:     required bool showVerificationBadge,
540:     required bool isVerified,
541:     required VoidCallback? onTap,
542:     required bool isObverse,
543:     String? coinName,
544:     String? denomination,
545:   }) {
546:     return GestureDetector(
547:       onTap: onTap,
548:       child: Stack(
549:         children: [
550:           Container(
551:             width: size,
552:             height: size,
553:             decoration: BoxDecoration(
554:               shape: BoxShape.circle,
555:               color: const Color(0xFF1E1E1E),
556:               border: Border.all(
557:                 color: isVerified
558:                     ? const Color(0xFFD4AF37).withValues(alpha: 0.6)
559:                     : Colors.white.withValues(alpha: 0.15),
560:                 width: 2,
561:               ),
562:               boxShadow: [
563:                 BoxShadow(
564:                   color: Colors.black.withValues(alpha: 0.4),
565:                   blurRadius: 8,
566:                   offset: const Offset(0, 4),
567:                 ),
568:               ],
569:             ),
570:             child: ClipOval(
571:               child: _buildNetworkOrAssetImage(
```

### 3.4 `lib/screens/review_hub_screen.dart:2282-2289` (`ReviewHubScreen._resolveImageUrl`)
```dart
2282:   String? _resolveImageUrl(dynamic raw) {
2283:     if (raw == null) return null;
2284:     final s = raw.toString().trim();
2285:     if (s.isEmpty || s == 'null') return null;
2286:     if (s.startsWith('http://') || s.startsWith('https://')) return s;
2287:     if (s.startsWith('assets/')) return s;
2288:     return '${ApiService.baseUrl}/images/$s';
2289:   }
```

### 3.5 `numista_backend/main.py:8369-8376` (`upload_coin_photo` endpoint)
```python
8369: @app.post("/api/vault/upload-photo")
8370: async def upload_coin_photo(
8371:     request: Request,
8372:     file: UploadFile = File(...),
8373:     uid: str = Depends(verify_token)
8374: ):
8375:     """Uploads a user's coin photo (e.g. microscope capture) to Cloud Storage and returns the public URL."""
8376:     await limiter.check_rate_limit(request, uid=uid, limit=20, window=60)
```

---
**Signed:** Argon (`31035602-8cdd-403f-8b72-7280605f5100`) — Independent Technical Reviewer & SAG Auditor
