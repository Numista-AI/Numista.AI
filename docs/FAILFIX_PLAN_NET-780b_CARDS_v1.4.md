# FAILFIX PLAN v1.4: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 7:25 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`, `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`, `BATON_NET-809_REVISE_780b-780c_v1.3_PER-COS-86-SAG-72_2026-11-05-1600.md`, `BATON_NET-812_REVISE_780b-780c_v1.4_PER-COS-83-SAG-58_2026-11-05-1705.md`  
**Source Scoring:** `COS_SCORE_NET-809_780b-780c-v1.3_20261105.md` (CoS 83 FAIL), `SAG_SCORE_NET-809_20261105.md` (SAG 58 FAIL) $\rightarrow$ v1.4 Target $\ge 95$  
**Protocol Update:** Argon Reviewer DROPPED per Founder Eric YES 6:07 PM ET 5 Nov FIN OPS. Plan review sequence: AG CoS v4 $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Zero code deployments to production without prior Firebase Preview Channel sign-off and Eric's separate typed YES.  
4. Zero Firestore writes, database seeding, or security rules changes.  

---

## 1. Executive Summary & CoS-83 / SAG-58 Resolution Overview

In the v1.3 review of NET-809, Grok Bot CoS (83 FAIL) and SAG (58 FAIL) validated that cert redactions, absence of AJ PII, genuine `¢` recognition, and the $0.00 spend guard were sound. However, both reviewers identified critical blockers regarding rollback commit pinning, valuation chip line anchoring, and scope precision.

**Plan v1.4 systematically resolves all findings:**

1. **Rollback Grounded to Pre-Execute Branch HEAD (§6.A — CoS & SAG Must-Fix 1):**
   - **Corrected Git Pinning:** Struck all references to `a5eeb19b` as branch restore target. Clarified that `+703/-18` is strictly the two-file diff `9f04550a..a5eeb19b`, not the branch distance to HEAD.
   - Pinned pre-execute `p7-v8.9` SHA to `4c97c7f0` (the verified branch SHA at review start). Rollback execution uses `git revert <execute commit set>` returning `p7-v8.9` cleanly to `4c97c7f0`.
   - Never checks out `9f04550a` or old file revisions as branch rollback.
   - Removed any GCS deactivation guarantee claim under this $0.00/no-cloud YES.

2. **Valuation Chip Anchored to Exact Lines 3170 and 3017–3023 (§2.C & §3.C — CoS & SAG Must-Fix 2):**
   - Corrected line citation from erroneous 3175 to exact repository line 3170:
     `if (valueText == '—' || m['enrichment_status'] == 'pending')`.
   - Replaced flawed logic with `final bool hasValidPrice = valCpg > 0;` defined at lines 3017–3023 in the same scope as `valCpg`.
   - At line 3170: if `!hasValidPrice`, render `'Valuation Pending'` gold chip; `else` render `Text(valueText)`.
   - **Absolute Precedence:** If `valCpg > 0`, CDN retail price is formatted and displayed regardless of `m['enrichment_status']`.
   - **Zero AI Estimate Fallback:** `m[_F.aiValue]` is never displayed in the primary card valuation slot.

3. **Grounded Negative Lookbehind Nickel & Cent Regex (§2.B & §3.B — CoS & SAG Must-Fix 3):**
   - Retained and verified negative lookbehind pattern: `r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)'` (caseSensitive: false).
   - Solves the trailing non-word boundary issue with `¢` (`\W`) while blocking `"15¢"` and `"25c"`.
   - Cent pattern aligned: `r'(?:\b1c\b|(?<!\d)1¢|\bone cent\b|\bcent\b|\bpenny\b)'` (caseSensitive: false).

4. **Hard $0.00 Spend Cap & Execution Fence (§6.A & §7):**
   - Strictly Dart/Flutter UI bug fixes on branch `p7-v8.9` / `dev`.
   - Zero cloud mutations, zero storage writes, zero external network calls.

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
**Mechanism:** When guest demo or user import records omit explicit `Year` or store it inside `Theme/Subject` or `title`, `year` is `''`. `extractSku` returns `''`, `resolveFromMap` returns `null`, and `_CollectionCardImage` falls back to an external URL blocked by CanvasKit CSP, showing a broken image icon.

### B. Defect 2: 2023-D 5c (Jefferson Nickel) Regex & Trailing Boundary
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 431–434:
```dart
431:       final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
432:           RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
```
**Mechanism:**
1. Line 433 contains a real `¢` symbol. Because `¢` is a non-word character (`\W`), the trailing word boundary `\b` immediately following `¢` fails to match `"5¢"` when followed by whitespace, punctuation, or string termination.
2. Conversely, an unanchored pattern without negative lookbehind erroneously matches `"15¢"` and `"25¢"`.
3. 2023 Jefferson nickels must never map to 2026 Semiquincentennial commemorative nickel artwork; they must resolve to standard historical circulating assets or fall back to internal reference library imagery.

### C. Defect 3: 2026 American Eagle Price Displays Raw 'Pending' & Hides Real Retail
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 3017–3023 and 3170–3188:
```dart
3017:         final valCpg = _parseNumber(m['cpgRetail']);
3018:         final finalVal = valCpg;
3019:         
3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3021:         final valueText = finalVal > 0 
3022:             ? fmt.format(finalVal) 
3023:             : (m[_F.aiValue]?.toString() ?? '—');
...
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
3181:                         Text(
3182:                           valueText,
3183:                           style: const TextStyle(
3184:                             fontSize: 13,
3185:                             fontWeight: FontWeight.bold,
3186:                             color: Color(0xFFC9A227),
3187:                           ),
3188:                         ),
```
**Mechanism:**
1. Line 3170 condition `valueText == '—' || m['enrichment_status'] == 'pending'` erroneously triggers the `'Valuation Pending'` chip whenever `enrichment_status == 'pending'`, even when `valCpg > 0` (e.g. `$10.00`). A valid positive retail price is thus completely hidden from the user.
2. In lines 3021–3023, when `finalVal <= 0`, `valueText` falls back to `m[_F.aiValue]`. If `aiValue` contains `'Pending'`, `valueText` becomes `'Pending'`, which is not `'—'`, rendering raw unstyled text `'Pending'` instead of the gold chip.
3. Fallback to `aiValue` in the primary slot violates the zero-AI-estimate valuation policy.

---

## 3. Planned Implementation

### A. Fix 1: Year-from-Text Fallback & User-Uploaded Photo Preservation
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. **Preserve User Photos:** `hasUserUploadedPhotos(data)` remains the very first gate in `resolveFromMap(data)` at lines 156–158:
   ```dart
   if (hasUserUploadedPhotos(data)) {
     return null;
   }
   ```
2. **Year Normalization with Fallback:**
   In `extractSku(Map<String, dynamic> data)`:
   ```dart
   String year = _normYear(data['year'] ?? data['Year']);
   if (year.isEmpty) {
     final titleText = '${data['title'] ?? ''} ${data['name'] ?? ''} ${data['Theme/Subject'] ?? ''}';
     final yearMatch = RegExp(r'\b(202[3-6]|19\d{2})\b').firstMatch(titleText);
     if (yearMatch != null) {
       year = yearMatch.group(1)!;
     }
   }
   ```
   *Note:* Avoid picking `1776` from `1776-2026`; ensure 2026 Semiquincentennial matches 2026.

### B. Fix 2: Anchored Negative Lookbehind Regex for Cent and Nickel
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 431–434:
```dart
      // MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.
      final isCent = RegExp(r'(?:\b1c\b|(?<!\d)1¢|\bone cent\b|\bcent\b|\bpenny\b)', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'(?:\blincoln cent\b|\bone cent\b|\bpenny\b)', caseSensitive: false).hasMatch(cleanTitle);
      final isNickel = RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'(?:\bjefferson nickel\b|\bnickel\b|\bfive cents?\b)', caseSensitive: false).hasMatch(cleanTitle);
```

### C. Fix 3: Valuation Chip Anchored to Line 3170 with Absolute Retail Precedence
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **Lines 3017–3024:**
   ```dart
   final valCpg = _parseNumber(m['cpgRetail']);
   final bool hasValidPrice = valCpg > 0;
   final fmt = intl.NumberFormat.currency(symbol: '\$');
   final valueText = hasValidPrice ? fmt.format(valCpg) : '';
   ```
2. **Lines 3170–3188:**
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
   **Guarantees:**
   - If `valCpg > 0`, `hasValidPrice == true`, retail price `$XX.XX` is always displayed; `enrichment_status` never suppresses it.
   - If `valCpg <= 0`, `hasValidPrice == false`, gold `'Valuation Pending'` chip is rendered.
   - Zero AI estimate fallback in this slot (`m[_F.aiValue]` is never displayed).

---

## 4. Verification Test Cases

| Test ID | Input Data | Expected Output | Assertion Command |
|---|---|---|---|
| **T-780b-1** | `{'title': '2026 American Eagle Silver Uncirculated', 'year': ''}` | Returns SKU `26EA`, obverse/reverse URLs resolved | `flutter test test/canonical_mint_asset_service_test.dart -n "extracts 26EA with year in title"` |
| **T-780b-2** | `cleanDenom = '5¢'`, `cleanTitle = '2023-D Jefferson Nickel'` | `isNickel == true`, does NOT match 2026 commemorative | `flutter test test/canonical_mint_asset_service_test.dart -n "nickel matches 5¢"` |
| **T-780b-3** | `cleanDenom = '15¢'`, `'25c'`, `'25¢'` | `isNickel == false` (negative lookbehind blocks false positive) | `flutter test test/canonical_mint_asset_service_test.dart -n "nickel rejects 15¢ and 25c"` |
| **T-780b-4** | `cleanDenom = '1¢'`, `cleanTitle = 'Lincoln Cent'` | `isCent == true`, does NOT match 15¢ | `flutter test test/canonical_mint_asset_service_test.dart -n "cent matches 1¢ and rejects 11¢"` |
| **T-780b-5** | `{'cpgRetail': 45.00, 'enrichment_status': 'pending'}` | Displays `'$45.00'`, `'Valuation Pending'` chip NOT shown | `flutter test test/my_collection_card_pricing_test.dart -n "positive cpgRetail displays price despite pending enrichment"` |
| **T-780b-6** | `{'cpgRetail': 0.0, 'aiValue': 38.50}` | Displays `'Valuation Pending'` chip; AI value 38.50 NOT rendered | `flutter test test/my_collection_card_pricing_test.dart -n "zero cpgRetail shows Valuation Pending without AI fallback"` |

---

## 5. Rollback Architecture & Failsafes

### A. Rollback Protocol
- **Pre-Execute Pinned SHA:** `p7-v8.9` at commit `4c97c7f0`.
- **Rollback Command:**
  ```bash
  git revert --no-edit <EXECUTE_COMMIT_SHAS>
  ```
- If clean tree restoration is needed prior to commit:
  ```bash
  git checkout 4c97c7f0 -- numista_mobile/lib/services/canonical_mint_asset_service.dart numista_mobile/lib/screens/my_collection_screen.dart
  ```
- **Strict Invariants:**
  1. Never run `git checkout 9f04550a -- <files>` (would destroy +703 lines of valid work).
  2. Never checkout stale `a5eeb19b` as a branch rollback.
  3. No cloud mutations or GCS manifest operations exist under this YES; no cloud deactivation rollback is needed or claimed.

### B. Spend & Safety Fence
- Authorizes **strictly Dart client modifications** on branch `p7-v8.9`.
- **$0.00 Total Spend Cap:** No external API queries, no Google Cloud mutations, no Firebase Hosting deployments.
- `origin/main` strictly locked at `9f04550a`. Stripe strictly OFF.

---

## 6. Sign-off Matrix

| Reviewer | Target Score | Review Chain Order |
|---|---|---|
| **Antigravity CoS v4** | Author | Step 1 (Filed) |
| **Grok Bot CoS** | $\ge 95$ | Step 2 (Mandatory Gate) |
| **Stand Alone Grok (SAG, grok-4.7)** | $\ge 95$ | Step 3 (Mandatory Independent Gate) |
| **Argon (Gemini 3.8)** | **DROPPED** | Per Founder Eric YES 6:07 PM ET 5 Nov FIN OPS |
| **Founder Eric** | Typed YES | Step 4 (Sole Authorization for Code Execution) |
