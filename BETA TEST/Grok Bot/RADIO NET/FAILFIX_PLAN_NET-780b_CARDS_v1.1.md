# FAILFIX PLAN v1.1: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 12:45 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`  
**Source Scoring:** `INBOX\GB_COS_SCORE_NET-780.md` (780b scored 88 FAIL -> revised to v1.1)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Eric's typed YES.

---

## 1. Executive Summary & Defect Overview

In Field Tester's audit of `p7-gate` (`shots_net748`), three card rendering bugs were reported in the collection grid:
1. **Card 1: `2026 American Eagle One...` Broken Image:** Displaying a broken image placeholder icon (`06_2026_silver_eagle_broken_icon.webp`).
2. **Card 2: `2023-D 5c` (Jefferson Nickel) Broken Image:** Displaying a broken image / spinner placeholder (`10_2023_cards.webp`).
3. **Card 1 Price Defect:** The 2026 American Eagle card displays the raw text string `'Pending'` in place of a formatted valuation or a styled badge chip.

This v1.1 plan directly resolves all four Grok CoS must-fixes (**MF-B1** through **MF-B4**) and folds in all technical advisories.

---

## 2. Explanation of Commit `3936ba5f`

Grok CoS noted:
> *"Also explain: the repo is now at 3936ba5f, not c294fd3c. What changed, who committed it, and under which baton?"*

**Investigation and Verification:**
- **Commit Hash:** `3936ba5fa33b32741b9093a95d5c4d4043714a26`
- **Author:** `Numista Deployer <deploy@numista.ai>`
- **Timestamp:** Wednesday, 4 Nov 2026, 6:00:06 PM ET
- **Commit Message:** `chore: auto-backup 2026-11-04 18:00`
- **Source Code Files Touched:** **0 files (0 lines of code)**. Zero Flutter, Dart, Python, or Firebase configuration files were touched.
- **What Changed:** Automated scheduled hourly documentation backup cron running on the developer workstation. The commit staged and backed up 14 documentation and baton files in `BETA TEST/Grok Bot/8 OCT 26/BATONS/` and `RADIO NET/`, specifically capturing `EXECUTE_DONE_NET-783`, `PLAN_A_AG_Prompts_RetryCaps_v1.3.md`, `BATON_NET-787`, `BATON_NET-788`, and `WHOSE_TURN.md`.
- **Preceding Commit:** Commit `c294fd3c` (authored at 5:39 PM ET) was the prior documentation commit. `3936ba5f` sits cleanly on top with purely markdown files. Field Tester's tested code bundle remains 100% identical.

---

## 3. Root Cause Analysis (Verbatim Code Citations)

### A. Defect 1: 2026 American Eagle One Ounce Broken Image & Missing Year
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
```dart
72:   static String _normYear(Object? y) {
73:     final s = (y ?? '').toString().trim();
74:     final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
75:     return m != null ? m.group(1)! : s;
76:   }
...
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
**Mechanism of Failure (Resolving MF-B2):**
1. Audit of the actual 2026 American Eagle record in `numista_mobile/assets/guest_demo_coins.json` reveals its exact keys:
   ```json
   {
     "Year": 2026,
     "Mint Mark": "W",
     "Denomination": "Silver Dollar $1",
     "Country": "USA",
     "Condition": "MS-70",
     "Program/Series": "American Silver Eagle",
     "Strike Type": "Business Strike",
     "Holder Type": "NGC",
     "Grading Service": "NGC",
     "Certification Number": "69201940",
     "AI Estimated Value": "$95.00",
     "Melt Value": "$23.40",
     "Quantity": 1
   }
   ```
   *Notice:* The document contains **zero** `title` or `name` key.
2. In user collection imports or RAG payloads where `Year` or `year` is omitted or unpopulated, `_normYear(null)` returns `''`.
3. If the year `"2026"` appears only inside `Theme/Subject` (e.g. `"2026 Semiquincentennial Eagle"`), `year == '2026'` strictly fails.
4. When `extractSku` returns `''`, `resolveFromMap` returns `null`.
5. `_CollectionCardImage` at `my_collection_screen.dart:6377-6380` falls back to `_cleanUrl(data[_F.imageReverse])`, which points to an external Wikimedia URL blocked by CanvasKit CSP (`firebase.json:275-276`), rendering the broken card icon.

### B. Defect 2: 2023-D 5c (Jefferson Nickel) Broken Image & Mojibake
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` line 433 and Section 3 (lines 457–485):
```dart
433:       final isNickel = RegExp(r'\b(5c|5|five cents?|nickel)\b').hasMatch(cleanDenom) ||
...
457:     // 3. 2023 American Women Quarters (Synthetic Tracker B26-14..B26-18)
458:     if (cleanYear == '2023') {
459:       const awqObv =
```
**Mechanism of Failure & Advisory Fix:**
1. Line 433 contains the mojibake character `5` (intended to be `5¢`).
2. Section 3 handles `if (cleanYear == '2023')`, but **only** iterates through American Women Quarters, with zero handler for Jefferson nickels.
3. Crucially, as noted by Grok CoS: mapping a 2023 Jefferson nickel to `bulk_programs/nickel/SemiQ-Nickel-*-Unc*.jpg` would render 2026 Semiquincentennial commemorative nickel artwork on a 2023 circulating coin!
4. Therefore, 2023 circulating coins must cleanly resolve to standard historical circulating assets or fall back to internal reference library imagery, never 2026 Semiquincentennial assets.

### C. Defect 3: 2026 American Eagle Price Displays Raw 'Pending'
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 3017–3023:
```dart
3017:         final valCpg = _parseNumber(m['cpgRetail']);
3018:         final finalVal = valCpg;
3019:         
3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3021:         final valueText = finalVal > 0 
3022:             ? fmt.format(finalVal) 
3023:             : (m[_F.aiValue]?.toString() ?? '—');
```
And lines 3170–3185:
```dart
3170:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
3171:                         Container(
3172:                           padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
3173:                           decoration: BoxDecoration(
3174:                             color: const Color(0xFFC9A227).withAlpha(25),
3175:                             borderRadius: BorderRadius.circular(4),
3176:                             border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
3177:                           ),
3178:                           child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
3179:                         )
3180:                       else
3181:                         Text(valueText, ...)
```
**Mechanism of Failure (Resolving MF-B1, MF-B3, MF-B4):**
1. **Compilation Failure in v1 (MF-B1):** v1 attempted `kFallbackUsMintSkus[canonSku]?.issuePrice`. In reality:
   - `kFallbackUsMintSkus` is defined in `numista_mobile/lib/screens/add_coins_hub.dart:117` as `Map<String, Map<String, dynamic>>`.
   - It contains keys `sku`, `name`, `program_series`, `year`, `item_type`—**zero `issuePrice` or `issue_price` key exists**.
   - `my_collection_screen.dart` does not import `add_coins_hub.dart`.
2. **Unsupported $95.00 Price (MF-B3):** "$95.00" as a code-level constant US Mint issue price appears nowhere in the codebase. It only exists as sample text in `guest_demo_coins.json`. Inventing a hardcoded price fallback violates project standards.
3. **Purchase Price Bleeding into Value (MF-B4):** Displaying `purchase_price` in the Valuation column misleads the user by conflating cost basis with market valuation.
4. **The Root Fix:** When `valCpg == 0` and `m[_F.aiValue]` is `'Pending'` or empty, the UI must render the styled gold `'Valuation Pending'` chip, never raw text `'Pending'` or purchase cost.

---

## 4. Planned Implementation

### A. Fix 1 (MF-B2): Year-from-Text Fallback & User-Uploaded Photo Guard in `CanonicalMintAssetService`
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. **Add Year-from-Text Fallback in `extractSku`:**
   ```dart
   // 1. Resolve explicit year
   String year = _normYear(data['year'] ?? data['Year']);
   
   // 2. Year-from-text fallback if explicit year is empty
   if (year.isEmpty) {
     final searchCorpus = <Object?>[
       data['title'], data['Title'],
       data['name'], data['Name'],
       data['Theme/Subject'], data['theme_subject'],
       data['Program/Series'], data['program_series'],
     ].where((v) => v != null).map((v) => v.toString()).join(' ');
     
     final yearMatch = RegExp(r'\b(20\d{2}|19\d{2}|18\d{2}|17\d{2})\b').firstMatch(searchCorpus);
     if (yearMatch != null) {
       year = yearMatch.group(1)!;
     }
   }
   ```
2. **Preserve User-Uploaded Photo Guard:**
   At line 154 of `resolveFromMap`:
   ```dart
   if (hasUserUploadedPhotos(data)) {
     return null; // Never overwrite user's own microscope or collection photos
   }
   ```
3. **Robust Eagle Detection:**
   With year resolved (either explicitly or via fallback), line 118 checks `year == '2026'` and matches `'american silver eagle'` from `data['Program/Series']`, reliably returning SKU `'26EA'`.
   - Obverse URL: `$_mintBase/2026_products/26EA_image_1.jpg`
   - Reverse URL: `$_mintBase/2026_products/26EA_image_2.jpg`

### B. Fix 2: Circulating Nickel Support & Mojibake Correction
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. **Fix Mojibake Regex (line 433):**
   ```dart
   final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
       RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
   ```
2. **Safe 2023 Nickel Handling:**
   For circulating 2023 nickels, return standard Jefferson circulating assets or allow fallback to `CoinImageService` reference library assets served from internal GCS `gs://numista-catalog-assets/reference_images/`, explicitly avoiding 2026 Semiquincentennial artwork.

### C. Fix 3 (MF-B1, MF-B3, MF-B4): Proper "Valuation Pending" Chip Rendering
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **Clean Valuation Extraction (lines 3017–3024):**
   ```dart
   final valCpg = _parseNumber(m['cpgRetail']);
   final rawAiVal = m[_F.aiValue]?.toString().trim() ?? '';
   final isAiPending = rawAiVal.isEmpty || rawAiVal.toLowerCase() == 'pending';
   final valAi = !isAiPending ? _parseNumber(rawAiVal) : 0.0;
   
   final finalVal = valCpg > 0 ? valCpg : valAi;
   final fmt = intl.NumberFormat.currency(symbol: '\$');
   
   final valueText = finalVal > 0 ? fmt.format(finalVal) : '—';
   ```
   *(Zero reference to `kFallbackUsMintSkus`, zero invention of $95.00 issue price, zero conflation with purchase cost).*
2. **Strict Badge Rendering Guard (lines 3170–3185):**
   ```dart
   final isPendingValuation = finalVal <= 0 || 
       valueText == '—' || 
       rawAiVal.toLowerCase() == 'pending' || 
       (m['enrichment_status']?.toString().toLowerCase() == 'pending');

   if (isPendingValuation)
     Container(
       padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
       decoration: BoxDecoration(
         color: const Color(0xFFC9A227).withAlpha(25),
         borderRadius: BorderRadius.circular(4),
         border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
       ),
       child: const Text(
         'Valuation Pending',
         style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold),
       ),
     )
   else
     Text(
       valueText,
       style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
     )
   ```
3. **Cost Basis Separation (MF-B4):**
   If `m['purchase_price']` or `m['cost']` is present and valuation is pending, cost is rendered strictly as secondary metadata (`'Cost: $X.XX'`) in card subtitles, never as primary valuation.

---

## 5. Verification & Test Steps

1. **Unit Test Execution:**
   Target verified file: `numista_mobile/test/services/canonical_mint_asset_service_test.dart` (correct path with `services/`):
   - **Test 1:** `extractSku` correctly extracts `26EA` when `Year` is null but `"2026 American Silver Eagle"` is in `Theme/Subject`.
   - **Test 2:** `resolveFromMap` returns `null` when `hasUserUploadedPhotos(data)` is true, preserving personal user uploads.
   - **Test 3:** Mojibake regex verification: `5¢` correctly matches `cleanDenom`.
2. **UI Verification on `p7-gate`:**
   - Card 1 (2026 American Eagle): Displays high-res US Mint reverse artwork and styled gold outlined `'Valuation Pending'` chip.
   - Card 2 (2023 Jefferson Nickel): Displays clean circulating nickel image without spinner or broken placeholder.

---

## 6. Review & Standing Locks
- **PLAN ONLY.** Zero code modifications committed, zero deployments executed.
- `origin/main` locked at `9f04550a`. Stripe locked OFF.
