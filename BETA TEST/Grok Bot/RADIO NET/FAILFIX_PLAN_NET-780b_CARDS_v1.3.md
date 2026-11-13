# FAILFIX PLAN v1.3: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 4:30 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`, `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`, `BATON_NET-809_REVISE_780b-780c_v1.3_PER-COS-86-SAG-72_2026-11-05-1600.md`  
**Source Scoring:** `COS_SCORE_NET-805_780b-780c-v1.2_20261105.md` (CoS 86 FAIL / SAG 72 FAIL on v1.2 $\rightarrow$ v1.3 Target $\ge 95$)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Zero code deployments to production without prior Firebase Preview Channel sign-off and Eric's separate typed YES.  
4. Zero Firestore writes, database seeding, or security rules changes.  

---

## 1. Executive Summary & CoS-86 / SAG-72 Resolution Overview

In the v1.2 review, Grok Bot CoS (86 FAIL) and SAG (72 FAIL) confirmed that cert redactions, demo dollar figure removals, and the 3,202 census were resolved, but identified four blocking must-fixes in rollback safety, regex boundary precision, valuation chip logic, and spend control.

**Plan v1.3 systematically resolves all findings:**

1. **Repo-Safe Rollback Architecture (§6.A — CoS & SAG Blocking Must-Fix 1):**
   - **Struck `git checkout 9f04550a -- <files>` entirely.** On branch `p7-v8.9`, commit `9f04550a` is 12 commits and +703/−18 lines behind HEAD on `my_collection_screen.dart` and `canonical_mint_asset_service.dart`. Checking out files from `9f04550a` would erase all p7 work (including existing chip logic and cent/nickel regexes).
   - **Pinned Rollback:** Rollback is pinned strictly to pre-execute `p7-v8.9` commit `a5eeb19b` via `git revert <execute SHA>`, or discarding working tree edits with `git checkout a5eeb19b -- <files>`. Locked main SHA `9f04550a` is never used as a file checkout target.

2. **Negative Lookbehind Nickel Regex (§4.B & §5 — CoS & SAG Blocking Must-Fix 2):**
   - **Corrected Line 433 Citation:** Removed the inaccurate "mojibake" claim. Real repository line 433 has a genuine `¢` character: `RegExp(r'\b(5c|5¢|five cents?|nickel)\b')`.
   - **Negative Lookbehind Anchoring:** Unanchored `5¢` erroneously matches `"15¢"`. The pattern is anchored with negative lookbehind: `RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false)`.
   - **Test 3 Aligned:** Must strictly **fail** `"15¢"` and `"25c"`, and **pass** `"5¢"`, `"5c"`, `"five cents"`, and `"nickel"`.

3. **Valuation Chip Logic (§4.C — CoS & SAG Blocking Must-Fix 4):**
   - **Positive CDN Price Takes Absolute Precedence:** If `valCpg > 0`, the card **always** displays the formatted retail price `fmt.format(valCpg)`.
   - **Chip Fired Only When Retail Missing:** The gold `'Valuation Pending'` chip is rendered **strictly when `valCpg <= 0`**. Checking `aiValue == 'pending'` or `enrichment_status == 'pending'` when `valCpg > 0` is deleted so real CDN prices are never hidden.
   - **Zero Secondary Valuation Fallback:** No AI estimate, melt price, issue price, or purchase cost is ever displayed in the primary card valuation slot.

4. **Hard $0.00 Spend Cap & Execution Fence (§6.A & §7 — CoS & SAG Must-Fix 6):**
   - Clarified that this YES authorizes **strictly Dart/Flutter UI bug fixes** on branch `p7-v8.9` / `dev`.
   - Bulk image ingestion/mirroring is explicitly removed from this execution scope. A hard abort is enforced before any `gsutil` or storage mutation call.

---

## 2. Root Cause Analysis & Verbatim Code Citations

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
...
118:     if (year == '2026' &&
119:         RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
120:         !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
121:       return '26EA';
122:     }
```
**Mechanism:** When guest demo or user import records omit `Year` or store it inside `Theme/Subject`, `year` is `''`. `extractSku` returns `''`, `resolveFromMap` returns `null`, and `_CollectionCardImage` falls back to an external URL blocked by CanvasKit CSP, showing a broken image icon.

### B. Defect 2: 2023-D 5c (Jefferson Nickel) Regex & Artwork Boundary
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` line 433:
```dart
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
```
**Mechanism:**
1. Line 433 has a real `¢` symbol. Because `¢` is a non-word character (`\W`), the trailing word boundary `\b` immediately following `¢` fails to match `"5¢"`.
2. Conversely, an unanchored `5¢` pattern matches `"15¢"` (false positive).
3. 2023 Jefferson nickels must never map to 2026 Semiquincentennial commemorative nickel artwork; they must resolve to standard historical circulating assets or fall back to internal reference library imagery.

### C. Defect 3: 2026 American Eagle Price Displays Raw 'Pending'
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 3017–3023 and 3175–3185:
```dart
3017:         final valCpg = _parseNumber(m['cpgRetail']);
3018:         final finalVal = valCpg;
3019:         
3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3021:         final valueText = finalVal > 0 
3022:             ? fmt.format(finalVal) 
3023:             : (m[_F.aiValue]?.toString() ?? '—');
...
3175:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
3176:                         Container(... child: const Text('Valuation Pending', ...))
3177:                       else
3178:                         Text(valueText, ...)
```
**Mechanism:** When `cpgRetail` is missing (`valCpg == 0`), `m[_F.aiValue]` contains raw text `'Pending'`. Line 3023 sets `valueText = 'Pending'`. Because `'Pending' != '—'` and `enrichment_status` is not set, line 3178 renders raw text `'Pending'`. Furthermore, checking `m['enrichment_status'] == 'pending'` in line 3175 would hide a real retail price when `valCpg > 0`.

---

## 3. Planned Implementation

### A. Fix 1: Year-from-Text Fallback & User-Uploaded Photo Guard
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. **Explicit Year First, Then Fallback:**
   ```dart
   String year = _normYear(data['year'] ?? data['Year']);
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
2. **Preserve User Photos:**
   ```dart
   if (hasUserUploadedPhotos(data)) {
     return null; // Never overwrite user's own photos
   }
   ```
3. **Eagle Detection:** With `year == '2026'`, line 118 returns SKU `'26EA'`.

### B. Fix 2: Circulating Nickel Regex Fix (Negative Lookbehind Anchored)
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` line 433:
```dart
// Negative lookbehind (?<!\d)5¢ prevents matching 15¢ or 25¢ while matching 5¢ cleanly:
final isNickel = RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false).hasMatch(cleanDenom) ||
    RegExp(r'\b(jefferson nickel|nickel|five cents?)\b', caseSensitive: false).hasMatch(cleanTitle);
```

### C. Fix 3: Strict CDN CPG Retail Valuation & Gold Chip Display
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **CDN CPG Retail Only (lines 3017–3024):**
   ```dart
   final valCpg = _parseNumber(m['cpgRetail']);
   final bool hasValidPrice = valCpg > 0;
   final fmt = intl.NumberFormat.currency(symbol: '\$');
   final String valueText = hasValidPrice ? fmt.format(valCpg) : '';
   ```
2. **Gold Chip Fired Strictly When Retail Price Missing (lines 3175–3185):**
   ```dart
   if (!hasValidPrice)
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
       style: const TextStyle(
         fontSize: 13,
         fontWeight: FontWeight.bold,
         color: Color(0xFFC9A227),
       ),
     ),
   ```
3. **Cost / Secondary Values:** Purchase price/cost is rendered strictly in secondary metadata lines; never in the primary valuation slot. Zero wholesale dealer bids.

---

## 4. Verification & Test Steps

1. **Unit Tests (`canonical_mint_asset_service_test.dart`):**
   - **Test 1:** `extractSku` extracts `26EA` when `Year` is omitted but `"2026 American Silver Eagle"` is in `Theme/Subject`.
   - **Test 2:** `resolveFromMap` returns `null` when `hasUserUploadedPhotos(data)` is true.
   - **Test 3 (Nickel Boundary Regex):**
     - Assert `RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false)`:
       - **PASS:** `"5¢"`, `"5c"`, `"five cents"`, `"Five Cents"`, `"nickel"`.
       - **FAIL:** `"15¢"`, `"25c"`, `"$5 coin"`.
2. **UI Card Check on `p7-gate`:**
   - Card 1 (2026 Silver Eagle): Displays high-res US Mint reverse artwork and gold `'Valuation Pending'` chip (zero raw text `'Pending'`).
   - Card 2 (2023 Jefferson Nickel): Resolves circulating nickel artwork via `CoinImageService` reference library without broken spinner or commemorative mismatch.
   - Pricing: When `cpgRetail > 0`, formatted CDN price displays. When `cpgRetail <= 0`, gold chip displays.

---

## 5. Dedicated Rollback Procedures & Standing Locks

### A. Dedicated Rollback Procedures
1. **Repo-Safe Code Revert:**
   If card rendering or pricing logic introduces any regression, revert target files cleanly to pre-execute `p7-v8.9` commit `a5eeb19b`:
   ```bash
   git revert <execute SHA>
   ```
   Or to discard uncommitted working tree changes:
   ```bash
   git checkout a5eeb19b -- numista_mobile/lib/services/canonical_mint_asset_service.dart numista_mobile/lib/screens/my_collection_screen.dart
   ```
   *(Locked main commit `9f04550a` is strictly forbidden as a file restore target).*
2. **Execution Boundary:** This YES authorizes strictly code fixes on branch `p7-v8.9`/`dev`. Zero deployments to production `numista-vault.web.app` without Preview Channel sign-off and separate typed YES.

### B. Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF.
- Zero Firestore writes, seeding, or security rules changes.
- Hard $0.00 spend cap (hard abort before any storage mutation call).
