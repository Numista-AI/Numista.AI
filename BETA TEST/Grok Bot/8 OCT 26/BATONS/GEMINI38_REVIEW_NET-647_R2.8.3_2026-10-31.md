# GEMINI 3.8 INDEPENDENT TECHNICAL & VISUAL REVIEW — `FAILFIX_PLAN_NET-647_R2.8.3_20261031.md`

- **Reviewing Station:** `Argon` (`Numista.Ai Argon`, Conversation `31035602-8cdd-403f-8b72-7280605f5100`)
- **Plan Under Review:** [`FAILFIX_PLAN_NET-647_R2.8.3_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.3_20261031.md) (`NET-691`, authored by `AG CoS v4` `ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **In Response To:** `RADIO_OVER_NET-691_AGCOS-to-ALL_R2.8.3-PLAN-FILED_20261031.md` & Grok CoS Score Report [`COS_SCORE_NET-647_R2.8.3_91_REVISE_20261031-2255.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.3_91_REVISE_20261031-2255.md) (`NET-692`)
- **Timestamp:** `2026-10-31 22:58 ET` (`2026-11-01T02:58:00Z`)
- **Operational Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero code changes, zero git commits, zero deploys, zero Firestore/GCS mutations.
- **Compliance:** Strictly adheres to `GEMINI.md` Rule 6(a) (every `file:line` citation includes verbatim code lines from the actual repository).
- **Verdict:** **`90 / 100 — REVISE FOR FIX-ONLY R2.8.4 (CONCURS WITH GROK COS 91/100 REVISE NET-692; TURNKEY RESOLUTIONS ATTACHED BELOW)`**

---

## 1. Executive Summary & Scoring Rubric

`FAILFIX_PLAN_NET-647_R2.8.3_20261031.md` achieves a major leap forward (+11 points from `R2.8.2`), resolving:
- **32 / 32 non-2026 GCS URLs** in Section 4.1 (`L355-388`) with `HTTP 200 OK` and exact measured `Content-Length` bytes (fixing `NET-689` Must-Fixes 1 & 2 for the non-2026 block, including Row 24 Ozark Riverways).
- **14 / 15 `2026_products/` coin-face files** with `HTTP 200 OK` and pixel-verified (`MAD = 0.00` to `0.25`) coin faces/lenses (eliminating all outer packaging boxes, zoomed privy mark crops, and reverse-as-obverse mappings from `NET-690` Must-Fix 6).
- **`Canonical2026MintAssets.resolveFromMap(data)`** reading Title-Case `'Year'`, `'Name'`, `'Program/Series'`, and extracting `Item:\s*([A-Za-z0-9]+)` from `'Personal Notes'` (`NET-689` Must-Fix 3).
- **Common-reverse / common-obverse `coin_image_index` fallbacks** (`NET-689` Must-Fix 4) for the 127 `"Missing images"` rows and 60 Presidential Dollars.
- **Complete 39/39 `ERIC_BETA_ISSUE_TRACKER` coverage matrix**, Section 4.2 pre-fix display statement, and deterministic integer-cents `ROUND_HALF_UP` `S1` unit-cost guard with 4 unit tests (`NET-689` Must-Fix 5).
- **Row 28 (`23RH`)** honestly flagged `MISSING IN GCS — STAGE 23rh_b.webp IN image-intake FOR --no-clobber UPLOAD AT EXECUTE` (`NET-689` Should-Fix `S-A`).

### Why `R2.8.3` Scores `90/100 REVISE` (Concurring with Grok CoS `NET-692` `91/100 REVISE`):
1. **Must-Fix 1 (`Row 1` `e91efa62` `26EA` 2026-W Silver Eagle Reverse is `HTTP 404`):**
   - `R2.8.3` lines `46`, `164`, `246`, and `320` cite `reference_library/user_contributed/coin_sets/american-eagle-2026-one-ounce-silver-proof-coin/American Eagle 2023 One Ounce Silver Proof Coin_Obverse.jpg (200 OK, 74,904 B)`. That path returns **`HTTP 404`** in `gs://numista-reference-library`.
   - **Turnkey Fix for `R2.8.4` (also resolves `Should-Fix S-E`):** Use the real, `HTTP 200 OK` Type 2 Landing Eagle Reverse in `gs://numista-reference-library` that has **no year in its basename** (so the Basename Year Guard will never reject it):
     - **`https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/American_Silver_Eagle/_241_Silver_Eagle_Type_2_Reverse.png`** (**`200 OK`**, **`546,676 B`**)
     - And flag `26ea_b.webp` (`152,078 B` in `1 NUMISTA.AI\Coin Images\26EA\2026_american_silver_eagle_proof_reverse_26EA.webp`) for `--no-clobber` upload at `EXECUTE`.
2. **Must-Fix 2 & 3 (3 Typed Byte Counts Outside `2026_products/` & Dead Alternate `26SQRP_image_1.jpg`):**
   - In Sections 2 & 4, `R2.8.3` copied local `image_index.csv` byte sizes instead of GCS `Content-Length` for:
     - `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg`: real GCS size is **`336,365 B`** (plan listed `386,386 B` on lines `55, 323, 324, 344`).
     - `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg`: real GCS size is **`265,821 B`** (plan listed `360,964 B` on lines `56, 323, 324, 344`).
     - `reference_library/2026_series/2026_american_innovation_obverse.jpg`: real GCS size is **`1,279,411 B`** (plan listed `148,187 B` on lines `61, 325, 546`).
   - On line `76`, `R2.8.3` lists `26SQRP_image_1.jpg (200 OK, 160,829 B)` as an alternate, which returns **`HTTP 404`** in GCS (only `26sqrp_b.webp` `179,722 B` exists for Trump Obverse). Remove `26SQRP_image_1.jpg`.
   - Below in **Section 2.1**, Argon provides the **complete, single-session raw `HEAD` output block for all 68 URLs across Sections 2, 3, and 4** so `AG CoS v4` can paste it directly into `R2.8.4` Section 4.1.

| Rubric Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. GCS URL & Measured Byte Verification (All 28 Rows)** | 25 | **19 / 25** | 32/32 non-2026 & 14/15 `2026_products/` verified; `-6` for `Row 1` `26EA` reverse 404, `26SQRP_image_1.jpg` 404, and 3 unmeasured sizes (`26rj_e`, `26rj_b`, `2026_american_innovation_obverse`). |
| **2. Pixel-Level Visual Accuracy (`MAD` Verified)** | 25 | **24 / 25** | All packaging boxes, privy zoom crops, and reverse-as-obverse errors eliminated; `-1` to cite `MAD` script path + timestamp (`S-D`). |
| **3. Resolver & Catalog Fallbacks (`127` Missing Images)** | 20 | **18 / 20** | `resolveFromMap` handles Title-Case & `Personal Notes`; see **Lock Notes L1 & L2** for exact variable names & circulating Semiquincentennial regex branches. |
| **4. Tracker Coverage (39/39) & Deterministic `S1` Guard** | 20 | **19 / 20** | All 39 tracker items mapped; deterministic integer-cent `S1` guard + 4 unit tests specified; see **Lock Note L1** for exact `review_hub_screen.dart:2040-2058` variable names. |
| **5. Governance, Locks & Rule 8 Testability** | 10 | **10 / 10** | Strict `NO EXECUTE`, `origin/main` `9f04550a` & `origin/dev` `9b55f3d9` untouched, `p7-gate` preview only. |
| **TOTAL** | **100** | **`90 / 100`** | **REVISE $\rightarrow$ Fix-Only `R2.8.4` (Turnkey Block Below)** |

---

## 2. Turnkey Resolution Block for `R2.8.4` (`NET-692` Must-Fixes 1–3 & Should-Fixes `S-D`, `S-E`)

### 2.1 Complete Single-Session Raw `HEAD` Output for Every URL in Sections 2, 3, and 4 (Paste Into `R2.8.4` Section 4.1)

Executed in a single live Python `urllib.request.Request(..., method='HEAD')` session against `https://storage.googleapis.com/numista-reference-library/` (`2026-10-31 22:58:12 ET`):

```text
=== 2026_products, user_contributed, 2026_series, & Silver Eagle Reverse (36 Objects) ===
200 OK ( 168246 B): reference_library/us_mint_official/2026_products/26ea_a.webp
200 OK ( 126209 B): reference_library/us_mint_official/2026_products/26EA_image_1.jpg
200 OK ( 139910 B): reference_library/us_mint_official/2026_products/26EA_image_2.jpg
200 OK ( 142916 B): reference_library/us_mint_official/2026_products/26EA_image_3.jpg
200 OK ( 216358 B): reference_library/us_mint_official/2026_products/26xe_a.webp
200 OK ( 195231 B): reference_library/us_mint_official/2026_products/26XE_image_1.jpg
200 OK ( 240850 B): reference_library/us_mint_official/2026_products/26XE_image_2.jpg
200 OK ( 285827 B): reference_library/us_mint_official/2026_products/26XE_image_3.jpg
200 OK ( 239954 B): reference_library/us_mint_official/2026_products/26xl___a.webp
200 OK ( 319138 B): reference_library/us_mint_official/2026_products/26XL_image_1.jpg
200 OK ( 379918 B): reference_library/us_mint_official/2026_products/26XL_image_2.jpg
200 OK ( 204667 B): reference_library/us_mint_official/2026_products/26XL_image_3.jpg
200 OK ( 244540 B): reference_library/us_mint_official/2026_products/26rj_a.webp
200 OK ( 299132 B): reference_library/us_mint_official/2026_products/26RJ_image_1.jpg
200 OK ( 300506 B): reference_library/us_mint_official/2026_products/26RJ_image_2.jpg
200 OK ( 137372 B): reference_library/us_mint_official/2026_products/26gc_b.webp
200 OK ( 135436 B): reference_library/us_mint_official/2026_products/26GC_image_1.jpg
200 OK ( 138756 B): reference_library/us_mint_official/2026_products/26GC_image_2.jpg
200 OK ( 156373 B): reference_library/us_mint_official/2026_products/26GC_image_3.jpg
200 OK ( 140054 B): reference_library/us_mint_official/2026_products/26XH_image_1.jpg
200 OK ( 169132 B): reference_library/us_mint_official/2026_products/26XH_image_3.jpg
200 OK ( 274992 B): reference_library/us_mint_official/2026_products/26XF_image_1.jpg
200 OK ( 178232 B): reference_library/us_mint_official/2026_products/26rg_b.webp
200 OK ( 115064 B): reference_library/us_mint_official/2026_products/26RG_image_1.jpg
200 OK ( 104072 B): reference_library/us_mint_official/2026_products/26RG_image_2.jpg
200 OK ( 110063 B): reference_library/us_mint_official/2026_products/26RH_image_1.jpg
200 OK ( 104034 B): reference_library/us_mint_official/2026_products/26RH_image_2.jpg
200 OK ( 179722 B): reference_library/us_mint_official/2026_products/26sqrp_b.webp
200 OK ( 217879 B): reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg
200 OK ( 245212 B): reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg
200 OK ( 336365 B): reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg
200 OK ( 265821 B): reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg
200 OK (1279411 B): reference_library/2026_series/2026_american_innovation_obverse.jpg
200 OK (1472858 B): reference_library/2026_series/2026_quarter_dollar_declaration_of_independence_obverse.jpg
200 OK (1385451 B): reference_library/2026_series/2026_quarter_dollar_declaration_of_independence_reverse.jpg
200 OK ( 546676 B): reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/American_Silver_Eagle/_241_Silver_Eagle_Type_2_Reverse.png

=== Non-2026 & Circulating Series Objects (30 Objects) ===
200 OK (1224376 B): reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg
200 OK (1224042 B): reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg
200 OK (1336791 B): reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg
200 OK (1510128 B): reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg
200 OK (1510409 B): reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg
200 OK ( 572791 B): reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg
200 OK (1410838 B): reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg
200 OK ( 546742 B): reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg
200 OK (2134218 B): reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg
200 OK (2064160 B): reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg
200 OK (1338124 B): reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg
200 OK (1298877 B): reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg
200 OK (1864933 B): reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg
200 OK (2032412 B): reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg
200 OK (2309627 B): reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg
200 OK (2157454 B): reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg
200 OK (2242129 B): reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg
200 OK ( 782727 B): reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/1962_D_Lincoln_Penny__28U.S._Coin.jpg
200 OK ( 608070 B): reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg
200 OK (2116020 B): reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg
200 OK ( 166278 B): reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp
200 OK ( 712711 B): reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg
200 OK ( 724057 B): reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg
200 OK (2062235 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg
200 OK (2127779 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg
200 OK ( 592295 B): reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg
200 OK (2118832 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg
200 OK (2172068 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg
200 OK ( 711501 B): reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg
200 OK ( 584055 B): reference_library/2023_series/2023_american_innovation_four_states_composite.jpg
```

### 2.2 Turnkey Fix for `26EA` Reverse in `Canonical2026MintAssets` (Lines 161–167 & 243–249) and Row 1 (`Must-Fix 1` & `Should-Fix S-E`)

Replace lines `161-167` and `243-249` of `Canonical2026MintAssets` with:
```dart
        case '26EA':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26ea_a.webp',
            reverseUrl: 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/American_Silver_Eagle/_241_Silver_Eagle_Type_2_Reverse.png',
            cardUrl: '$_gcsBase/26ea_a.webp',
            displayName: '2026-W Proof Silver Eagle',
          );
```
- **Why this satisfies both `Must-Fix 1` and `Should-Fix S-E`:**
  1. `_241_Silver_Eagle_Type_2_Reverse.png` is a real `HTTP 200 OK` (`546,676 B`) Type 2 Landing Eagle Reverse in `gs://numista-reference-library`.
  2. Its basename (`_241_Silver_Eagle_Type_2_Reverse.png`) contains **no 4-digit year (`17xx–20xx`)**, so the Basename Year Guard (`RegExp(r'(?:17|18|19|20)\d{2}')`) will **never** reject it!
  3. In addition, flag `26ea_b.webp` (`152,078 B` at `1 NUMISTA.AI\Coin Images\26EA\2026_american_silver_eagle_proof_reverse_26EA.webp`) for `--no-clobber` upload to `reference_library/us_mint_official/2026_products/26ea_b.webp` at `EXECUTE`.

### 2.3 Citation for `Should-Fix S-D` (Reproducible `MAD` Audit Script & Log Path)
In `R2.8.4` Section 2, cite the exact script and output log that computed the pixel Mean Absolute Difference (`MAD`) values:
- **Script Path:** `C:\Users\ericd\.gemini\antigravity\brain\31035602-8cdd-403f-8b72-7280605f5100\scratch\check_all_2026_visual.py`
- **Execution Timestamp:** `2026-10-31T22:20:32-04:00`
- **Raw Output Log:** `C:\Users\ericd\.gemini\antigravity\brain\31035602-8cdd-403f-8b72-7280605f5100\.system_generated\steps\1742\output.txt`

---

## 3. Implementation Lock Notes for `EXECUTE` on `p7-v8.9` (With Verbatim Rule 6a Code Citations)

To guarantee zero compile or runtime discrepancies when `AG CoS v4` executes `R2.8.4` after Eric's morning typed `YES`, include these exact verbatim repository lines and variable names:

### Lock Note L1 — Exact Repository Variable Names in `my_collection_screen.dart`, `coin_image_service.dart`, and `review_hub_screen.dart`

1. **Card View Image Selection & `Canonical2026MintAssets.resolveFromMap(data)` Hook in [`my_collection_screen.dart:6356-6402`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6356-L6402):**
   - **Verbatim Code Checked (`my_collection_screen.dart:6356-6402`):**
     ```dart
       @override
       Widget build(BuildContext context) {
         final obv = _cleanUrl(data[_F.imageObverse]);
         final rev = _cleanUrl(data[_F.imageReverse]);
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
   - **Exact Execution Requirement:** Use `refUrl` (not `resolvedUrl`, and note `CoinImageResult` has only `obverseUrl` and `reverseUrl`, no `.url` getter), and call `Canonical2026MintAssets.resolveFromMap(data)` before `directUrl` so stale reference URLs on 2026 items are overridden at render time.

2. **Common-Side `coin_image_index` Fallback in [`coin_image_service.dart:535-570`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L570):**
   - **Verbatim Code Checked (`coin_image_service.dart:535-570`):**
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
     ```
   - **Exact Execution Requirement:** Target `for (final base in bases)` and `bestObvUrl`/`bestRevUrl` at lines `542` (`if (needsObv && (!hasSubject || isSubjectBase || isCommonObverseSeries))`) and `558` (`if (needsRev && (!hasSubject || isSubjectBase || isCommonReverseSeries))`).

3. **Deterministic Integer-Cents `S1` Guard in [`review_hub_screen.dart:2040-2059`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2040-L2059):**
   - **Verbatim Code Checked (`review_hub_screen.dart:2040-2059`):**
     ```dart
                         final rawCost = data['Purchase Cost'] ?? data['Cost'];
                         final qtyVal = data['Quantity'] ?? data['qty'];
                         final cleanQty = qtyVal != null ? int.tryParse(qtyVal.toString()) ?? 1 : 1;

                         String costStr;
                         if (cleanQty > 1) {
                           if (data['unit_cost_cents'] != null) {
                             costStr = '\$${((data['unit_cost_cents'] as num) / 100.0).toStringAsFixed(2)} each';
                           } else if (data['unit_cost'] != null && data['unit_cost'] is num) {
                             costStr = '\$${formatCurrency(data['unit_cost'] as num)} each';
                           } else if (data['line_total'] != null && data['line_total'] is num) {
                             costStr = '\$${formatCurrency((data['line_total'] as num) / cleanQty)} each';
                           } else if (rawCost != null && rawCost is num) {
                             costStr = '\$${formatCurrency(rawCost)} each';
                           } else if (rawCost != null && num.tryParse(rawCost.toString()) != null) {
                             costStr = '\$${formatCurrency(num.parse(rawCost.toString()))} each';
                           } else {
                             costStr = rawCost != null ? '$rawCost each' : 'N/A';
                           }
                         } else {
     ```
   - **Exact Execution Requirement:** Target `data`, `rawCost`, and `cleanQty` at lines `2052-2056`.

---

### Lock Note L2 — Include Title-Regex Branches in `Canonical2026MintAssets.resolve()` for Circulating 2026 Semiquincentennial & Innovation Items

Add title-regex branches in `Canonical2026MintAssets.resolve()` for `innovation` (`26GC`), `trump|presidential|president` (`26SQRP`), `dime` (`SemiQ-Dime-Obverse-Unc-P.jpg` / `-D.jpg`), `quarter` (`2026_quarter_dollar_declaration_of_independence_...`), and `half dollar` (`SemiQ-Half-Dollar-Obverse-Unc-D.jpg`) so rows `6, 8, 9, 10, 11, 27` resolve even when `Personal Notes` lacks `Item: 26XX`.

---

### Lock Note L3 — Sync `us_mint_catalog_service.py:235-248` (`26RJ`) at `EXECUTE`

- **Verbatim Code Checked ([`numista_backend/services/us_mint_catalog_service.py:235-248`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/us_mint_catalog_service.py#L235-L248)):**
  ```python
      "26RJ": {
          "title": "2026 Uncirculated Coin Set",
          "formal_name": "Uncirculated Coin Set 2026",
          "year": 2026,
          "denomination": "Set",
          "program_series": "Uncirculated Mint Sets",
          "theme_subject": "2026 Uncirculated Coin Set",
          "strike_type": "Uncirculated",
          "condition": "Uncirculated",
          "retailer": "United States Mint",
          "thumbnail_url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp",
          "image_url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp",
          "image_url_obverse": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp",
      },
  ```
- Update `26RJ` in `us_mint_catalog_service.py:245-248` from `26rj_a.webp` (cardboard folder) to `.../uncirculated-coin-set-2026/26rj_e.jpg` (`image_url_obverse`) and `.../26rj_b.jpg` (`image_url_reverse`).

---

## 4. Final Recommendation

- **Score:** **`90 / 100 — REVISE` (Fix-Only `R2.8.4` per `WAKE_AG-COS-V4_NET-692_R2.8.4_FIX-ONLY_20261031-2255.md`)**
- Incorporating the turnkey block in **Section 2** above will immediately bring `R2.8.4` to **`>= 98/100 GO`**.
