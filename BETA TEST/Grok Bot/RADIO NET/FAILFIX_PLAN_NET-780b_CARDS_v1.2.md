# FAILFIX PLAN v1.2: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 3:30 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`, `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`  
**Source Scoring:** `COS_SCORE_NET-791_FAILFIX-780b-780c-v1.1_20261105.md` (CoS 82 FAIL / SAG 67 FAIL on v1.1 $\rightarrow$ v1.2 Target $\ge 95$)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Zero code deployments to production without prior Firebase Preview Channel sign-off and Eric's separate typed YES.  
4. Zero Firestore writes, database seeding, or security rules changes.  

---

## 1. Executive Summary & v1.2 Resolution Overview

In Field Tester's audit of `p7-gate` (`shots_net748`), three card rendering defects were identified in the collection grid:
1. **Card 1 (`2026 American Eagle One...`) Broken Image:** Displaying a broken image placeholder icon (`06_2026_silver_eagle_broken_icon.webp`).
2. **Card 2 (`2023-D 5c` Jefferson Nickel) Broken Image:** Displaying a broken image / spinner placeholder (`10_2023_cards.webp`).
3. **Card 1 Price Defect:** Displaying raw text string `'Pending'` instead of a formatted valuation or styled badge chip.

While v1.1 addressed initial citations and backup commit `3936ba5f`, Grok CoS (82 FAIL) and SAG (67 FAIL) flagged three critical defects in the v1.1 plan text. **Plan v1.2 completely resolves all findings:**

1. **Nickel Regex Boundary Fix (§4.B):** In v1.1, `RegExp(r'\b(5c|5¢|five cents?|nickel)\b')` failed because `¢` is a non-word character (`\W`), so a trailing `\b` word boundary immediately following `¢` never matches `"5¢"`. Fixed to `RegExp(r'(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)')` and aligned Test 3.
2. **Strict CDN CPG Retail Rule & Zero AI Fallback (§4.C):** Per Founder Eric's binding 5 Nov 10:36 AM directive ("CDN CPG retail only; don't prefer AI over CDN"), the unlabeled AI fallback (`valCpg > 0 ? valCpg : valAi`) is **PERMANENTLY DELETED**. Card valuation displays CDN `cpgRetail` only. If `cpgRetail` is missing or $\le 0$, the UI displays strictly the styled gold `'Valuation Pending'` chip. No AI value, melt value, issue price, or purchase cost is ever displayed as the card valuation.
3. **PII & Provenance Redactions (§3.A):** Redacted real-looking NGC certification numbers to `"[cert no. redacted]"` and replaced demo dollar figures (`$95.00`, melt `$23.40`) with generic sample placeholders.
4. **Dedicated Rollback Section (§6.A):** Added pinned Git revert commands targeting baseline commit `9f04550a`.
5. **Cross-Cutting Policy Directives (§1 & §7):**
   - **Catalog-First AI Rule:** AI-generated images may reside ONLY in labeled metadata field `ai_replica_images`; strictly prohibited from primary card art, browse index, or type image slots.
   - **US-Only Intake Scope:** Strictly US coinage, currency, and historical medals (states, territories, possessions).
   - **$0 Spend Cap:** Zero budget expenditure ($0.00).
   - **No Wholesale Pricing:** Retail CPG only; zero dealer wholesale bids displayed.
   - **Thanksgiving Launch Cut (26 Nov 2026):** For landing `numista.ai` Meta ads, the card pending-chip + closed-CSP fallback are the active deliverables; bulk mirroring of external images is not a launch blocker.

---

## 2. Explanation of Commit `3936ba5f`

For complete historical audit transparency:
- **Commit Hash:** `3936ba5fa33b32741b9093a95d5c4d4043714a26`
- **Author:** `Numista Deployer <deploy@numista.ai>`
- **Timestamp:** Wednesday, 4 Nov 2026, 6:00:06 PM ET
- **Commit Message:** `chore: auto-backup 2026-11-04 18:00`
- **Source Code Files Touched:** **0 files (0 lines of code)**. Zero Flutter, Dart, Python, or Firebase configuration files were touched.
- **What Changed:** Automated scheduled hourly documentation backup cron running on the developer workstation. The commit staged and backed up 14 documentation and baton files in `BETA TEST/Grok Bot/8 OCT 26/BATONS/` and `RADIO NET/`, specifically capturing `EXECUTE_DONE_NET-783`, `PLAN_A_AG_Prompts_RetryCaps_v1.3.md`, `BATON_NET-787`, `BATON_NET-788`, and `WHOSE_TURN.md`.
- **Preceding Commit:** Commit `c294fd3c` (authored at 5:39 PM ET) was the prior documentation commit. `3936ba5f` sits cleanly on top with purely markdown files. Field Tester's tested code bundle remains 100% identical.

---

## 3. Root Cause Analysis (Verbatim Code Citations)

### A. Defect 1: 2026 American Eagle Broken Image & Missing Year
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
**Mechanism of Failure:**
1. In demo records (`numista_mobile/assets/guest_demo_coins.json`), the record structure is:
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
     "Certification Number": "[cert no. redacted]",
     "Quantity": 1
   }
   ```
   *(Redacted NGC cert number and demo pricing per CoS/SAG audit).*
   The document contains **zero** `title` or `name` key.
2. In user collection imports or RAG payloads where `Year` or `year` is omitted, `_normYear(null)` returns `''`.
3. If the year `"2026"` appears only inside `Theme/Subject` (e.g. `"2026 Semiquincentennial Eagle"`), `year == '2026'` strictly fails.
4. When `extractSku` returns `''`, `resolveFromMap` returns `null`.
5. `_CollectionCardImage` at `my_collection_screen.dart:6377-6380` falls back to `_cleanUrl(data[_F.imageReverse])`, which points to an external Wikimedia URL blocked by CanvasKit CSP (`firebase.json:275-276`), rendering the broken card icon.

### B. Defect 2: 2023-D 5c (Jefferson Nickel) Broken Image & Mojibake
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` line 433 and lines 457–485:
```dart
433:       final isNickel = RegExp(r'\b(5c|5|five cents?|nickel)\b').hasMatch(cleanDenom) ||
...
457:     // 3. 2023 American Women Quarters (Synthetic Tracker B26-14..B26-18)
458:     if (cleanYear == '2023') {
459:       const awqObv =
```
**Mechanism of Failure:**
1. Line 433 contains mojibake character `5` (intended to be `5¢`).
2. Crucially, as noted by SAG Fact 5, using a trailing `\b` after `¢` (e.g. `\b5¢\b`) fails because `¢` is a non-word character (`\W`), so `\b` looks for a transition from word to non-word, which cannot occur after a non-word symbol.
3. Section 3 handles `if (cleanYear == '2023')`, but only iterates through American Women Quarters, with zero handler for Jefferson nickels.
4. Crucially: mapping a 2023 Jefferson nickel to Semiquincentennial nickel artwork (`bulk_programs/nickel/SemiQ-Nickel-*-Unc*.jpg`) would render 2026 commemorative artwork on a 2023 circulating coin.
5. Therefore, 2023 circulating coins must resolve to standard historical circulating assets or fall back to internal reference library imagery, never 2026 Semiquincentennial assets.

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
**Mechanism of Failure:**
1. In demo records and newly imported coins, `cpgRetail` is empty (`valCpg == 0.0`), while `m[_F.aiValue]` contains the raw string `'Pending'`.
2. Line 3023 assigns `valueText = 'Pending'`.
3. Line 3170 checks `if (valueText == '—' || m['enrichment_status'] == 'pending')`. Because `valueText == 'Pending'` is neither `'—'` nor is `m['enrichment_status']` set, it falls through to line 3181 and renders raw unstyled text `'Pending'`.
4. In v1.1, an AI-fallback was proposed (`final finalVal = valCpg > 0 ? valCpg : valAi;`). As SAG Fact 6 and CoS noted, this violates Founder Eric's 5 Nov 10:36 AM directive by displaying an unlabeled AI valuation on the card instead of CDN CPG retail.

---

## 4. Planned Implementation

### A. Fix 1: Year-from-Text Fallback & User-Uploaded Photo Guard
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. **Explicit Year First, Then Unambiguous Match Fallback in `extractSku`:**
   ```dart
   // 1. Resolve explicit year
   String year = _normYear(data['year'] ?? data['Year']);
   
   // 2. Year-from-text fallback ONLY if explicit year is empty
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
   With year resolved, line 118 checks `year == '2026'` and matches `'american silver eagle'` from `data['Program/Series']`, returning SKU `'26EA'`.
   - Obverse URL: `$_mintBase/2026_products/26EA_image_1.jpg`
   - Reverse URL: `$_mintBase/2026_products/26EA_image_2.jpg`

### B. Fix 2: Circulating Nickel Regex Fix (Non-Word Boundary Resolved)
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. **Correct Nickel Regex (line 433):**
   ```dart
   // Non-word symbol '¢' cannot have a trailing \b word boundary.
   // Correct pattern safely matches '5c', '5¢', 'five cents', 'five cent', or 'nickel':
   final isNickel = RegExp(r'(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false).hasMatch(cleanDenom) ||
       RegExp(r'\b(jefferson nickel|nickel|five cents?)\b', caseSensitive: false).hasMatch(cleanTitle);
   ```
2. **Safe 2023 Nickel Handling:**
   For circulating 2023 nickels, return standard Jefferson circulating assets or allow fallback to `CoinImageService` reference library assets served from internal GCS `gs://numista-catalog-assets/reference_images/`, explicitly avoiding 2026 Semiquincentennial commemorative artwork.

### C. Fix 3: Strict CDN CPG Retail Valuation & Gold Chip Display
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **CDN CPG Retail Only (No AI Fallback) (lines 3017–3024):**
   ```dart
   // Strict Founder Directive (5 Nov 10:36 AM): Display CDN cpgRetail only.
   // Zero unlabeled AI fallback, zero melt fallback, zero issue price fallback.
   final valCpg = _parseNumber(m['cpgRetail']);
   final fmt = intl.NumberFormat.currency(symbol: '\$');
   
   final String valueText = valCpg > 0 ? fmt.format(valCpg) : '—';
   ```
2. **Strict Gold Badge Rendering Guard (lines 3170–3185):**
   ```dart
   final rawAiVal = m[_F.aiValue]?.toString().trim().toLowerCase() ?? '';
   final bool isValuationPending = valCpg <= 0 || 
       valueText == '—' || 
       rawAiVal == 'pending' || 
       (m['enrichment_status']?.toString().toLowerCase() == 'pending');

   if (isValuationPending)
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
3. **Cost Basis Isolation:**
   If `m['purchase_price']` or `m['cost']` is present, it is rendered strictly as secondary subtitle metadata (`'Cost: $X.XX'`). It is never displayed in the primary Valuation slot.

---

## 5. Verification & Test Steps

1. **Unit Test Execution:**
   Target verified file: `numista_mobile/test/services/canonical_mint_asset_service_test.dart`:
   - **Test 1:** `extractSku` correctly extracts `26EA` when `Year` is null but `"2026 American Silver Eagle"` is in `Theme/Subject`.
   - **Test 2:** `resolveFromMap` returns `null` when `hasUserUploadedPhotos(data)` is true, preserving personal user uploads.
   - **Test 3 (Nickel Regex Test):** Assert `RegExp(r'(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)')` successfully matches `"5¢"`, `"5c"`, `"Five Cents"`, and `"nickel"`.
2. **UI Verification on `p7-gate`:**
   - Card 1 (2026 American Eagle): Displays high-res US Mint reverse artwork and styled gold outlined `'Valuation Pending'` chip (zero raw text `'Pending'`).
   - Card 2 (2023 Jefferson Nickel): Displays clean circulating nickel image without spinner or broken placeholder.

---

## 6. Rollback Procedures & Standing Locks

### A. Dedicated Rollback Procedures
1. **Branch-Only Revert:**
   If card rendering or valuation logic introduces any regression, revert target files cleanly to baseline commit `9f04550a`:
   ```bash
   git checkout 9f04550a -- numista_mobile/lib/services/canonical_mint_asset_service.dart
   git checkout 9f04550a -- numista_mobile/lib/screens/my_collection_screen.dart
   ```
2. **Zero Deployment without Separate YES:**
   Any execution of this plan on `dev` requires Founder Eric's explicit typed YES. Production deployment to `numista-vault.web.app` requires a separate, subsequent approval following Preview Channel sign-off.

### B. Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF.
- Zero Firestore database writes, seeding, or security rules changes.

---

## 7. Cross-Cutting Policy Declarations

1. **Catalog-First AI Rule:** AI-generated images reside strictly in labeled `ai_replica_images`; never in primary cards or browse index.
2. **US-Only Intake Scope:** All coin, note, and medal assets are strictly United States numismatics.
3. **Hard $0.00 Spend Cap:** Zero budget expenditure authorized ($0.00).
4. **No Wholesale Pricing:** Card valuation is strictly CPG retail; wholesale dealer bids are never displayed.
5. **Thanksgiving Launch Cut:** For the 26 Nov 2026 Meta ad launch, the card pending-chip and closed-CSP fallback are the active release deliverables. Bulk mirroring of 3,202 images is not authorized by this YES and is not an ad launch blocker.
