# GEMINI 3.8 TECHNICAL REVIEW — `FAILFIX_PLAN_NET-647_R2.8.14_20261102.md`

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)
- **Date / Time:** 2026-11-02 14:18 EST
- **Baton Reference:** [`BATON_NET-737_GROKCOS-ARGON_NET-647-R2.8.14-REVIEW_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-737_GROKCOS-ARGON_NET-647-R2.8.14-REVIEW_20261102.md) / [`BATON_NET-738_AG_NET-647-R2.8.15-FIX-ONLY_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-738_AG_NET-647-R2.8.15-FIX-ONLY_20261102.md)
- **Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.14_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.14_20261102.md)
- **Concurrence Reference:** [`COS_SCORE_NET-647_R2.8.14_45_REVISE_20261102-1415EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.14_45_REVISE_20261102-1415EST.md) (Grok CoS: `45/100 — REVISE`)
- **Score:** **`42/100 — REVISE`**
- **Operating Mode:** DOCS-ONLY / REVIEW-ONLY (`NO EXECUTE`). Zero source code changes, zero git commits/pushes, zero deployments.

---

## 1. Executive Summary & Root Cause of Regression

While `R2.8.14` properly fixed several targeted `SAG 72` items inside the Dart resolver in **Section 3.1** (such as removing `Personal Notes` from theme substring matching, adding the `"WEST POINT"` guard before `"S"`, expanding `hasUserUploadedPhotos`, and expanding Section 4.1.3 to 114 paths), **Sections 3.2, 4, 6, 7, 8, and 9 were rewritten from scratch instead of surgically editing `R2.8.13` (`96/100`)**.

That rewrite introduced **six major regressions (`MF-1` through `MF-6`)** that make `R2.8.14` internally contradictory and non-compliant with `GEMINI.md Rule 6(a)` and the live Firestore dump (`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`).

> **CRITICAL RECOVERY INSTRUCTION FOR `AG CoS v4` ON `R2.8.15`:**
> Do **NOT** patch `R2.8.14` forward. Start `R2.8.15` by copying [`FAILFIX_PLAN_NET-647_R2.8.13_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.13_20261102.md) (which already had 100% authentic 28-row dump IDs/titles in §3.2 and §4, authentic `Rule 6(a)` verbatim code blocks in §7, authentic byte sizes in §6, and the executable Gate 4 script in §9.2) and apply **ONLY** surgical edits for the `SAG 72` items and Grok CoS's `BATON_NET-738` list.

---

## 2. MUST-FIX Items Required for `R2.8.15` (`>= 95/100 PASS`)

### MF-1 (Concurring with Grok CoS MF-1): Restore Authentic 28-Row Live Dump Data in §3.2, §4, and Test File
In `R2.8.14`, **16 of the 28 rows** (`Rows 12–25` and `Rows 26–27`) were replaced with fabricated doc IDs, titles, years, and themes that do **not** match [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json) or `R2.8.13`:
- **Rows 13–17 in `R2.8.14` §4 (`lines 1230–1234`):** Replaced `2019-P American Memorial Park`, `2020-P Salt River Bay`, `2013-P Mount Rushmore`, `2018-P Cumberland Island`, and `2018-P Block Island` with five `2023 American Women Quarters` (`Bessie Coleman`, `Edith Kanakaʻole`, `Eleanor Roosevelt`, `Jovita Idar`, `Maria Tallchief`)—while `R2.8.14` §3.2 (`lines 752–825`) still tests the ATB quarters!
- **Rows 18–25 in `R2.8.14` §3.2 (`lines 827–945`) & §4 (`lines 1235–1242`):** Replaced real dump rows `18` (`c7bf5f7a88584bc1a453`, `1962 Proof Cent`), `19` (`9a7cc3889e3c42a3b6cd`, `2019-W San Antonio Missions`), `20` (`77463689d22c4c718193`, `2017-P Effigy Mounds`), `21` (`f0ab50d9c8e242598ee4`, `2017-P Frederick Douglass`), `22` (`0465178986114328ad2c`, `2010-P Yellowstone`), `23` (`39140179625d42dc99f8`, `2017-D George Rogers Clark`), `24` (`926164f05d674182b6f6`, `2017-P Ozark`), and `25` (`e08eb74bc7ca43b39f66`, `2023 Silver Proof Set`) with fabricated doc IDs (`d8f9e0a1b2c3d4e5f6a7`, `a1b2c3d4e5f6a7b8c9d0`, etc.) and completely different coins (`2014 Shenandoah`, `2016 Harpers Ferry`, `2015 Blue Ridge`, `2012 El Yunque`, `2011 Gettysburg`, `2017 George Rogers Clark`, `2016 Theodore Roosevelt`, `2021 Tuskegee Airmen`).
- **Rows 26–27 in `R2.8.14` §3.2 & §4:** Replaced dump rows `26` (`29d76d09c44140a392d1`, `Untitled Coin` / `2026-D Half Dollar`) and `27` (`b8803c94879a430690d8`, `Untitled Coin` / `2026-P Half Dollar`) with duplicate `26XE` (`7a2e9c4b1d8f3a5e6c0b`) and `26SQRP` (`4f9a2d7e8b1c5a3f6e0d`) rows.
- **Required Fix:** Restore the exact 28-row ordering, doc IDs, titles, and input dictionaries from `R2.8.13` / `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`, then update only Row 11 (`04b4a7617d274e2ba403`, preserved via `hasUserUploadedPhotos` because its stored URLs are in `studio-9101802118-8c9a8-uploads/users/...`), Row 25 (`23RH` primary = 2023 composites, fallback = staged `23rh_b.webp`/`23rh_c.webp`), Row 26 (`2026-HALF-D` fallback obv = `null`), and Row 27 (`2026-HALF-P` primary obv = `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, fallback obv = `2026_half_dollar_enduring_liberty_obverse.jpg`, fallback rev = `null`).

---

### MF-2: Fix Section 7 `GEMINI.md Rule 6(a)` Violation — Restore Real Verbatim Repository Code Citations
In `R2.8.14` (`lines 1451–1506`), all five code blocks in Section 7 (`7.1` through `7.5`) were replaced with short, invented pseudo-code snippets (e.g., `Widget _buildImageTile(Map<String, dynamic> coin)...`, `String resolveMintThumbnail(Map<String, dynamic> doc)...`, `return CoinThumbnailFlipper(...)`) that **do not exist** in `numista_mobile` or `numista_backend` at `origin/dev` (`01a03f90` / `32d4b42e`), and even omitted the closing code fence on §7.5!

Per `GEMINI.md Rule 6(a)`, every `file:line` citation MUST quote the actual repository lines verbatim. Below are the verified verbatim lines from `origin/dev` (`01a03f90`, code tree identical to `32d4b42e`) that **must** be restored to Section 7 in `R2.8.15`:

1. **[`numista_mobile/lib/screens/my_collection_screen.dart:6320-6366`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6320-L6366)** (verified via `git show 01a03f90:numista_mobile/lib/screens/my_collection_screen.dart`):
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

2. **[`numista_mobile/lib/screens/my_collection_screen.dart:3016-3023`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3023)** (verified via `git show 01a03f90:numista_mobile/lib/screens/my_collection_screen.dart`):
   ```dart
           final valCpg = _parseNumber(m['cpgRetail']);
           final finalVal = valCpg;
           
           final fmt = intl.NumberFormat.currency(symbol: '\$');
           final rawAiVal = m[_F.aiValue] ?? m['ai_estimated_value'] ?? m['estValue'] ?? (m['ai_est_value'] != null ? fmt.format(m['ai_est_value']) : null);
           final valueText = finalVal > 0 
               ? fmt.format(finalVal) 
               : (rawAiVal?.toString() ?? '—');
   ```

3. **[`numista_mobile/lib/services/coin_image_service.dart:535-571`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L571)** (verified via `git show 01a03f90:numista_mobile/lib/services/coin_image_service.dart`):
   ```dart
         for (final base in bases) {
           final needsObv = bestObvUrl == null;
           final needsRev = bestRevUrl == null;
           if (!needsObv && !needsRev) break; // both sides resolved

           final isSubjectBase = subjectSlug != null && base.contains(subjectSlug);

           if (needsObv && (!hasSubject || isSubjectBase)) {
             final obvDoc = await db.collection(_collection)
                 .doc('${base}_obverse').get();
             if (obvDoc.exists) {
               final d = obvDoc.data()!['obverse'] as Map<String, dynamic>?;
               if (d != null) {
                 bestObvUrl = d['public_url'] as String?;
                 bestAttr  ??= d['attribution'] as String?;
                 bestLabel ??= d['source_label'] as String?;
                 bestKey   ??= base;
               }
             }
           }

           // STEAL-GUARD: only accept reverse from subject-containing bases
           // when a subject is known. Generic reverse = honest placeholder.
           if (needsRev && (!hasSubject || isSubjectBase)) {
             final revDoc = await db.collection(_collection)
                 .doc('${base}_reverse').get();
             if (revDoc.exists) {
               final d = revDoc.data()!['reverse'] as Map<String, dynamic>?;
               if (d != null) {
                 bestRevUrl = d['public_url'] as String?;
                 bestAttr  ??= d['attribution'] as String?;
                 bestLabel ??= d['source_label'] as String?;
                 bestKey   ??= base;
               }
             }
           }
         }
   ```

4. **[`numista_mobile/lib/screens/review_hub_screen.dart:2282-2289`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2282-L2289)** (verified via `git show 01a03f90:numista_mobile/lib/screens/review_hub_screen.dart`):
   ```dart
                     () {
                       final rawCost = data['Purchase Cost'] ?? data['Cost'];
                       final rawSetCostLabel = (data['set_cost_label'] ?? '').toString().trim();
                       final costStr = rawSetCostLabel.isNotEmpty
                           ? rawSetCostLabel
                           : (rawCost != null
                               ? (rawCost is num ? '\$${rawCost.toStringAsFixed(2)}' : rawCost.toString())
                               : 'N/A');
   ```

5. **[`numista_backend/main.py:8369-8376`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8369-L8376)** (verified via `git show 01a03f90:numista_backend/main.py`):
   ```python
                       per_file[idx]["status"]      = "done"
                       per_file[idx]["coins_added"] = added_this_file
                       per_file[idx]["receipt_id"]  = receipt_id

                   except Exception as e:
                       per_file[idx]["status"] = "error"
                       per_file[idx]["error"]  = str(e)
                       logger.error(f"Bulk import invoice error ({fname}): {e}\n{traceback.format_exc()}")
   ```
   *(If adding a proposed PII/Order-# redaction helper for `SF8`, clearly label it as `[PROPOSED EXTENSION — NOT YET IN REPO]` below the verbatim `8369-8376` citation, never replacing the verbatim repository citation itself!)*

---

### MF-3: Eliminate All Internal Contradictions Between Section 3.1, Section 4 Table, Section 4.1.2, and Section 8
In `R2.8.14`, the Section 4 table (`lines 1218–1245`), Section 4.1.2 (`lines 1277–1300`), and Section 8 (`lines 1521–1561`) cite completely different filenames from what the Section 3.1 Dart resolver (`lines 263–608`) actually returns:
- **Row 01 (`26EA`):** §3.1 returns `fallbackReverseUrl = 26EA_image_3.jpg`, whereas §4 table and §8 (`B26-1`) say `26ea_b.webp`. (In `R2.8.13`, `26EA` `fallbackReverseUrl` was `$_base2026/26ea_b.webp` so that staged `26ea_b.webp` was exercised in the resolver and §4 table. Either keep `26ea_b.webp` in §3.1 + §3.2 + §4 + §8 as in `R2.8.13`, or make them 100% identical everywhere.)
- **Row 02 (`26XE`):** §3.1 returns `26XE_image_2.jpg` / `26XE_image_3.jpg` (`fallbackReverseUrl: 26XE_image_1.jpg` in `R2.8.14` vs `26xe_b.webp` in `R2.8.13`), whereas `R2.8.14` §4 table says `26XE_image_1.jpg` / `26XE_image_2.jpg` and `26xe_b.webp`. Restore `R2.8.13`'s exact `26XE` mapping (`26XE_image_2.jpg` / `26XE_image_3.jpg`, fallback `26xe_a.webp` / `26xe_b.webp`) across §3.1, §3.2, §4, and §8!
- **Row 03 (`26XL`):** §3.1 returns `26XL_image_3.jpg` / `26XL_image_2.jpg` (fallback `26xl___a.webp` / `26XL_image_1.jpg`), whereas `R2.8.14` §4 table says `26XL_image_1.jpg` / `26XL_image_2.jpg` and nonexistent `2026_clad_proof_set_obverse.jpg`. Restore `R2.8.13` §4 Row 03!
- **Row 06 (`26SQRP`):** §3.1 returns `MASTER_SEMIQDJT_image_1.jpg` / `26sqrp_b.webp` (fallback `26sqrp_a.webp` / `null`), whereas `R2.8.14` §4 table and §8 (`B26-7`) cite nonexistent `26SQRP_image_1.jpg`, `26SQRP_image_2.jpg`, and `26sqrp_card.webp`. Restore `R2.8.13` §4 Row 06!
- **Row 07 (`26GC`):** §3.1 returns `26gc_b.webp` / `26gc_a.webp`, whereas `R2.8.14` §4 table swaps obverse/reverse and cites nonexistent `26gc_card.webp`. Restore `R2.8.13` §4 Row 07!
- **Row 08 (`2026-DIME-P`) & Row 09 (`2026-DIME-D`):** §3.1 returns `SemiQ-Dime-Obverse-Unc-P.jpg` (fallback `null`) and `SemiQ-Dime-Reverse-Unc.jpg` (fallback `null`), whereas `R2.8.14` §4 table and §4.1.2 (`lines 1283–1286`) invert primary/fallback for Row 08 and omit `2026-semiq-dime-obverse-unc-d.webp` fallback for Row 09!
- **Section 8 (`B26-14` through `B26-26`):** `R2.8.14` §8 (`lines 1534–1546`) cites nonexistent filenames (`2020-america-the-beautiful-quarters-coin-proof-obverse-s.jpg`, `2023_american_women_quarters_circulating_obverse_philadelphia.jpg`, `2014-...-obverse-philadelphia.jpg`, etc.). Restore `R2.8.13` Section 8 and update only `B26-12` (`Row 11` user-upload preserved), `B26-13` (`SemiQ-Half-Dollar-Obverse-Unc-P.jpg`), and `B26-27` (`2023` composite primaries + staged `23rh_b.webp`/`23rh_c.webp` fallbacks).

---

### MF-4 (Concurring with Grok CoS MF-2 & MF-3): Honest GCS Status Wording for the 4 Staged WebPs & Gate 3/4 Sequencing
- **Staged WebP Wording (`MF-2`):** The 4 staged files (`26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`) are **local staged fixtures (`HTTP 404` on GCS right now until Gate 4 upload after Eric's `YES`)**. Do not label the full 114-file table `"100% HTTP 200 OK Verified"`—state `"110 Live in GCS (HTTP 200 OK verified; bytes + x-goog-hash MD5 measured live) + 4 Local Staged WebPs (bytes + local MD5 measured; uploaded to GCS in Gate 4 after Founder Eric's typed YES)"`.
- **Gate 3 / Gate 4 Wording (`MF-3`):** In Section 9.2, keep `R2.8.13`'s exact gate sequence:
  - **Gate 1:** Plan scoring $\ge 95$ from Grok CoS and Argon.
  - **Gate 2:** Stand Alone Grok (SAG) concurrence.
  - **Gate 3:** Founder Eric types **`YES`**.
  - **Gate 4:** Upload the 4 staged `.webp` files to `gs://numista-reference-library/...` and run the executable Python HEAD verification script asserting HTTP `200 OK`, `Content-Type: image/webp`, exact `Content-Length`, and exact `x-goog-hash` MD5 for all 4 URLs.

---

### MF-5: Fix Section 6 Stale/Fabricated Byte Sizes & MD5s
In `R2.8.14` Section 6 (`lines 1437–1444`), `AG CoS v4` pasted a table of 8 files with **fabricated byte sizes and MD5s** (`26EA_image_2.jpg: 108,127 B`, `26rj_e.jpg: 222,059 B`, `SemiQ-Dime-Obverse-Unc-D.jpg: 1,141,960 B`, `SemiQ-Dime-Obverse-Unc-P.jpg: 1,158,402 B`, `SemiQ-Dime-Reverse-Unc.jpg: 1,284,110 B`, `23rh_b.webp: 198,412 B`, `23rh_c.webp: 184,920 B`) that directly contradict Section 4.1.3 and Section 9.1!
- **Required Fix:** Restore `R2.8.13` Section 6 (`lines 1334–1349`) with the true byte sizes (`168,246 B`, `164,146 B`, `216,358 B`, `245,878 B`, `239,954 B`, `244,540 B`, `226,854 B`, `161,734 B`, `1,224,042 B`, `1,224,376 B`, `1,336,791 B`).

---

### MF-6: Restore Section 9.2 Executable Gate 4 Verification Script
In `R2.8.14` (`lines 1575–1583`), the executable Python verification block from `R2.8.13` (`lines 1546–1577`) was deleted and replaced with one-line bullet points. Restore the full Section 9.1 + Section 9.2 block from `R2.8.13` (updating only Gate 6's `origin/dev` tip note to `01a03f90 (code tree identical to 32d4b42e)` and the footer to `**END PLAN R2.8.15**`).

---

## 3. Summary Checklist for `R2.8.15`

1. Start from [`FAILFIX_PLAN_NET-647_R2.8.13_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.13_20261102.md).
2. Keep the clean `R2.8.14` Section 3.1 resolver improvements (`hasUserUploadedPhotos` with `studio-9101802118-8c9a8-uploads`, `Personal Notes` removed from theme matching, `"WEST POINT"` guard before `"S"`, byte-identical fallbacks set to `null`, `2026-HALF-P` defaultobverse `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, `23RH` composite primaries + staged `23rh_b.webp`/`23rh_c.webp` fallbacks), **ensuring `26EA` and `26XE` fallback reverses remain `$_base2026/26ea_b.webp` and `$_base2026/26xe_b.webp` so §3.1, §3.2, §4, and §9.1 are 100% unified**.
3. Keep all 28 authentic rows from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` in Section 3.2, Section 4, and `scratch/canonical_mint_asset_service_test.dart`, and re-run `flutter test ..\scratch\canonical_mint_asset_service_test.dart` so all 43 tests (`28` real dump rows + `15` synthetic edge cases) pass (`0` failures).
4. Keep the 114-path table in Section 4.1.3 with honest status labels (`110 Live HTTP 200 OK` + `4 Local Staged WebPs`).
5. Keep `R2.8.13` Sections 6, 7 (verbatim `Rule 6(a)` citations), 8 (updated only for `B26-12`, `B26-13`, `B26-27`), and 9 (with the full Gate 4 script and footer `**END PLAN R2.8.15**`).
