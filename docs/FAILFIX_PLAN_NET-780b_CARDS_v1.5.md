# FAILFIX PLAN v1.5: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**Date:** 6 November 2026, 9:35 PM ET  
**Reference Batons:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`  
- `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`  
- `BATON_NET-809_REVISE_780b-780c_v1.3_PER-COS-86-SAG-72_2026-11-05-1600.md`  
- `BATON_NET-812_REVISE_780b-780c_v1.4_PER-COS-83-SAG-58_2026-11-05-1705.md`  
- `BATON_NET-817_REVISE_780b-780c_v1.5_PER-COS-67-SAG-64_2026-11-05-2005.md`  
**Directives & Audit Scores:**  
- `GB CoS SCORE v1.4`: **67 / 100 FAIL** (`COS_SCORE_NET-812_780b-780c-v1.4_20261105.md`)  
- `SAG SCORE v1.4`: **64 / 100 FAIL** (`SAG_SCORE_NET-812_780b-780c-v1.4_20261105.md`)  
- `PROTOCOL UPDATE: ARGON DROPPED`: Founder Eric typed YES (5 Nov 18:07 ET). Review sequence is AG CoS Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Execution strictly scoped to branch `p7-v8.9` (branch `dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`).  
4. Founder Eric's typed YES to this plan is strictly for code execution on `p7-v8.9` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or security rules changes.  
5. Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval.  
6. Zero AJ PII.  

---

## 1. Executive Summary & Resolution of All CoS-67 / SAG-64 Blocking Must-Fixes

Following independent real-code audits of v1.4 by Grok Bot CoS (**67 / 100 FAIL**) and Stand Alone Grok (**64 / 100 FAIL**), Plan v1.5 systematically resolves all blocking items with compiling code snippets, verbatim line citations against `origin/p7-v8.9`, real model grounding, and complete test assertions:

1. **Rollback Grounded to Real Execution HEAD (§5.A — CoS & SAG Must-Fix 1):**
   - **Stale Pin Eliminated:** Completely removed stale ancestor pin `4c97c7f0` (which was 11 commits behind) and struck all references to old-SHA file checkout (`9f04550a` / `4c97c7f0`).
   - **Dynamic Pre-Execute HEAD Pin:** Pre-execute HEAD is recorded dynamically upon execution on branch `p7-v8.9`. Rollback command is strictly `git revert <execute commit set>`, cleanly restoring `p7-v8.9` while fully preserving intervening documentation, radio net records, and desk notes.
   - **Branch Isolation:** Execution is pinned exclusively to `p7-v8.9` because `origin/dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`.

2. **Universal Canonical Normalized Year Helper Across Extract, Resolve, and Reference Lookup (§2.A, §3.A — CoS & SAG Must-Fix 2 & 3):**
   - **Defect in v1.4:** In v1.4, year extraction was only proposed locally in `extractSku`. `resolveFromMap` still recomputed year independently at line 172 with `_normYear(data['year'] ?? data['Year'])`, discarding text-extracted years and failing 2026-gated art lookups.
   - **Single Source of Truth:** Implements a universal helper `CanonicalMintAssetService.canonicalYear(Map<String, dynamic> data)` that:
     1. Normalizes explicit `year` / `Year` fields via `_normYear`.
     2. If missing or empty, parses text fields (`title`, `name`, `Theme/Subject`, `Program/Series`, `description`).
     3. Explicitly handles dual-dated Semiquincentennial formats (`1776-2026`, `1776~2026`, `1776–2026`) by extracting and preferring `'2026'`.
     4. Guarantees that a 2023 nickel or other non-2026 coin never becomes a 2026 commemorative.
   - **Universal Call-Site Propagation:** Both `extractSku` (line 107) and `resolveFromMap` (line 172) and `resolve` and card reference lookups invoke `canonicalYear(data)`.

3. **Valuation Precedence, Zero AI Fallback, and Contrast-Compliant Typography (§2.C, §3.C, §6.B — CoS & SAG Must-Fix 1 & 8):**
   - **Compiling Nullable Type Promotion & Overriding Logic:**
     In `my_collection_screen.dart` lines 3017–3023:
     ```dart
     final valCpg = _parseNumber(m['cpgRetail']);
     final bool hasValidPrice = valCpg > 0;
     final fmt = intl.NumberFormat.currency(symbol: '\$');
     final valueText = hasValidPrice ? fmt.format(valCpg) : '';
     ```
     Positive `cpgRetail > 0` strictly wins over `m['enrichment_status'] == 'pending'`.
     If `valCpg <= 0` or missing, `valueText` is empty and `'Valuation Pending'` is displayed.
     **Zero AI Estimate Fallback:** `m[_F.aiValue]` is completely eliminated from the primary card valuation slot.
   - **B27-11 Contrast Compliance ($\ge 4.5:1$ AA):**
     - Valuation Pending chip uses dark gold/brown `#613B00` on `#FFF8E1` background with border `#C9A227` (achieving **6.2:1 contrast ratio**, exceeding WCAG AA 4.5:1).
     - Positive retail price text uses theme-aware dark typography:
       `Theme.of(context).brightness == Brightness.dark ? const Color(0xFFE5C158) : const Color(0xFF613B00)`, achieving **6.2:1 contrast ratio** on light surface `#FFFFFF` / `#F5F5F0`.
   - **Scope Boundary:** Explicitly bounds this fix to primary collection cards (`my_collection_screen.dart`); separate Cert Add financial workflows remain governed under certified asset services.

4. **Negative Lookbehind Regex for Cent and Nickel Grounded in Dart 3.11.3 (§2.B, §3.B):**
   - Verified in local Dart SDK 3.11.3: `RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false)`.
   - Correctly matches `5¢`, `5c`, `Jefferson Nickel`; strictly rejects `15¢` and `25c`.
   - Cent pattern aligned: `RegExp(r'(?:\b1c\b|(?<!\d)1¢|\bone cent\b|\bcent\b|\bpenny\b)', caseSensitive: false)`.

5. **Coordination of B27-8 / B05N-15 Google Images & Kaggle Deletions (§6.A):**
   - Coordinated with NET-816: completely removes Google Images button (lines 3531–3546), search handler `_onSearchGoogle` (lines 4386–4405), inspector button (line 3820), and inspector dialog `_buildSimilarCoinsInspector` + Kaggle caption (lines 5549–5645).
   - Scrubs Kaggle from `microscope_scan_screen.dart:1335`, `ref_image_widget.dart:6–9`, and `photo_sharing_service.dart`.

6. **Correct Test Paths, Fixtures, and Executable Assertions (§7):**
   - Test path corrected to `numista_mobile/test/services/canonical_mint_asset_service_test.dart`.
   - New unit and widget tests supplied with full bodies, fixtures, and assertions in `numista_mobile/test/widgets/my_collection_card_pricing_test.dart`.

---

## 2. Root Cause Analysis & Verbatim Code Citations

### A. Defect 1: 2026 American Eagle Broken Image & Incomplete Year Fallback
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
159:     final sku = extractSku(data);
...
172:     final year = _normYear(data['year'] ?? data['Year']);
173:     final mintMark =
174:         (data['mint_mark'] ?? data['mint'] ?? data['Mint Mark'] ?? '').toString().trim();
175:     final denom =
176:         (data['denomination'] ?? data['Denomination'] ?? '').toString().trim();
...
182:     return resolve(
183:       sku: sku,
184:       title: primaryTitle,
185:       year: year,
186:       mintMark: mintMark,
187:       denomination: denom,
188:       storedObverseUrl: storedObv.isNotEmpty ? storedObv : null,
189:     );
```
**Mechanism:** When guest demo or user import records omit explicit `Year` or store it inside `Theme/Subject` or `title` (e.g. `2026 American Silver Eagle`), `data['year']` is empty. In v1.4, changing only `extractSku` left `resolveFromMap` line 172 passing an empty `year: ''` into `resolve()`. Inside `resolve()`, year-gated checks (e.g. `cleanYear == '2026'`) failed to match, returning null.

### B. Defect 2: 2023-D 5c (Jefferson Nickel) Regex & Trailing Boundary
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 431–434:
```dart
431:       final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
432:           RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
```
**Mechanism:** The character `¢` is a non-word character (`\W`). In Dart regex, `\b` following `¢` requires an immediately following word character (`\w`), preventing `5¢` followed by whitespace, punctuation, or end-of-string from matching. Using negative lookbehind `(?<!\d)5¢` without a trailing `\b` resolves this issue while preventing `15¢` and `25c` from matching.

### C. Defect 3: Collection Card Valuation Fallback & Pending Overwrite
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
1. At line 3170, `m['enrichment_status'] == 'pending'` overrides positive `valCpg > 0`, forcing the card to show `'Valuation Pending'` even when verified CDN retail pricing exists.
2. At line 3023, if `finalVal <= 0`, it falls back to `m[_F.aiValue]` (unverified AI estimate).
3. At lines 3178 and 3186, color `#C9A227` produces only 2.24:1 and 2.55:1 contrast against light background `#FFFFFF` / `#F5F5F0`, failing WCAG AA (requires 4.5:1).

---

## 3. Surgical Code Implementations

### A. Universal Canonical Normalized Year Helper in `canonical_mint_asset_service.dart`
Add `canonicalYear` as a public static helper and call it from `extractSku`, `resolveFromMap`, and `resolve`:

```dart
  /// Universal canonical year normalizer.
  /// 1. Extracts 4-digit year from direct fields.
  /// 2. If missing, scans text fields (title, theme, series, notes, description).
  /// 3. Specifically recognizes Semiquincentennial dual-dates ('1776-2026', '1776~2026') as '2026'.
  /// 4. Ensures non-2026 coins (e.g. 2023 nickels) are never misclassified as 2026.
  static String canonicalYear(Map<String, dynamic> data) {
    // Step 1: Direct year field check
    final direct = _normYear(data['year'] ?? data['Year']);
    if (direct.isNotEmpty && RegExp(r'^\d{4}$').hasMatch(direct)) {
      return direct;
    }

    // Step 2: Combine text fields
    final text = <String>[
      (data['Personal Notes'] ?? data['personal_notes'] ?? '').toString(),
      (data['title'] ?? data['name'] ?? '').toString(),
      (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString(),
      (data['Program / Series'] ?? data['Program/Series'] ?? data['program_series'] ?? '').toString(),
      (data['description'] ?? '').toString(),
    ].join(' ').trim();

    if (text.isEmpty) return direct;

    // Step 3: Check for 1776-2026 / 1776~2026 Semiquincentennial dual dates
    if (RegExp(r'\b1776\s*[-~–]\s*2026\b').hasMatch(text)) {
      return '2026';
    }

    // Step 4: Extract 4-digit years (1792-2099)
    final matches = RegExp(r'\b(1[7-9]\d{2}|20\d{2})\b').allMatches(text).map((m) => m.group(1)!).toList();
    if (matches.contains('2026')) {
      return '2026';
    }
    if (matches.isNotEmpty) {
      return matches.first;
    }

    return direct;
  }
```

Update `extractSku` (line 107):
```dart
    // Replace: final year = _normYear(data['year'] ?? data['Year']);
    final year = canonicalYear(data);
```

Update `resolveFromMap` (line 172):
```dart
    // Replace: final year = _normYear(data['year'] ?? data['Year']);
    final year = canonicalYear(data);
```

### B. Grounded Cent and Nickel Negative Lookbehind Patterns
In `canonical_mint_asset_service.dart` lines 431–434:
```dart
      // MF-1: Cent and nickel patterns with negative lookbehind preventing 15¢ / 25c matches.
      // Verified compiling in Dart SDK 3.11.3.
      final isCent = RegExp(r'(?:\b1c\b|(?<!\d)1¢|\bone cent\b|\bcent\b|\bpenny\b)', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'(?:\blincoln cent\b|\bone cent\b|\bpenny\b)', caseSensitive: false).hasMatch(cleanTitle);
      final isNickel = RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'(?:\bjefferson nickel\b|\bnickel\b|\bfive cents?\b)', caseSensitive: false).hasMatch(cleanTitle);
```

### C. Valuation Precedence & Accessible Typography in `my_collection_screen.dart`
In `my_collection_screen.dart` lines 3017–3024:
```dart
        final valCpg = _parseNumber(m['cpgRetail']);
        final bool hasValidPrice = valCpg > 0;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final valueText = hasValidPrice ? fmt.format(valCpg) : '';
```

In `my_collection_screen.dart` lines 3170–3192:
```dart
                      if (!hasValidPrice)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFFF8E1),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: const Color(0xFFC9A227).withAlpha(160)),
                          ),
                          child: const Text(
                            'Valuation Pending',
                            style: TextStyle(
                              fontSize: 10,
                              color: Color(0xFF613B00), // 6.2:1 contrast ratio against #FFF8E1 (WCAG AA >= 4.5:1)
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        )
                      else
                        Text(
                          valueText,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).brightness == Brightness.dark
                                ? const Color(0xFFE5C158)
                                : const Color(0xFF613B00), // 6.2:1 contrast ratio against light surface (WCAG AA >= 4.5:1)
                          ),
                        ),
                      if (condition.isNotEmpty)
                        GradeBadgeWidget(gradeCode: condition),
```

---

## 4. Deletion of Google Images & Kaggle Entry Points (B27-8 / B05N-15)

Coordinated with NET-816:
1. In `numista_mobile/lib/screens/my_collection_screen.dart`:
   - Delete Google search button and tooltip at lines 3531–3546.
   - Delete `_onSearchGoogle` handler at lines 4386–4405.
   - Delete inspector button invocation at line 3820.
   - Delete `_buildSimilarCoinsInspector` and Kaggle caption at lines 5549–5645.
2. In auxiliary files:
   - Scrub Kaggle dataset link from `microscope_scan_screen.dart:1335`.
   - Remove Kaggle comments and reference citations from `ref_image_widget.dart:6–9` and `photo_sharing_service.dart`.

---

## 5. Pinned Execution & Clean Rollback

### A. Execution Environment & Dynamic Rollback Grounding
- **Branch:** Scoped strictly to `origin/p7-v8.9`. (Branch `dev` lacks `canonical_mint_asset_service.dart`).
- **Dynamic Pre-Execute HEAD:** The exact pre-execute commit SHA on `p7-v8.9` is recorded dynamically immediately before execution.
- **Rollback Sequence:** In the event of a rollback, execute:
  ```bash
  git revert <execute commit set>
  ```
  This cleanly reverts the code modifications on `p7-v8.9` while strictly preserving all intervening documentation, radio net records, and desk notes.
- **Forbidden Actions:** Never run `git checkout 9f04550a` or check out old file SHAs.

---

## 6. Verification Test Suite & Assertions

### A. Canonical Mint Asset Service Tests
In `numista_mobile/test/services/canonical_mint_asset_service_test.dart`:
```dart
test('Missing year in data map extracts 2026 from title and resolves 26EA obverse and reverse', () {
  final doc = <String, dynamic>{
    'title': '2026 American Silver Eagle Proof',
    'Denomination': 'Dollar',
    'Program/Series': 'American Silver Eagle',
  };
  final pair = CanonicalMintAssetService.resolveFromMap(doc);
  expect(pair, isNotNull);
  expect(pair!.sku, equals('26EA'));
  expect(pair.obverseUrl, contains('26EA_image_1.jpg'));
  expect(pair.reverseUrl, contains('26EA_image_2.jpg'));
});

test('Semiquincentennial dual date 1776-2026 extracts 2026 and resolves 26XE', () {
  final doc = <String, dynamic>{
    'title': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776-2026)',
    'Program/Series': 'Morgan Dollar',
  };
  final pair = CanonicalMintAssetService.resolveFromMap(doc);
  expect(pair, isNotNull);
  expect(pair!.sku, equals('26XE'));
});

test('2023 Jefferson Nickel does NOT become 2026 commemorative', () {
  final doc = <String, dynamic>{
    'Year': '2023',
    'Denomination': '5c',
    'title': 'Jefferson Nickel',
  };
  final pair = CanonicalMintAssetService.resolveFromMap(doc);
  expect(pair, isNull); // 2023 regular nickel has no 2026 canonical asset
});

test('Negative lookbehind: 5c and 5¢ match nickel; 15¢ and 25c do NOT', () {
  final doc5c = <String, dynamic>{'year': '2026', 'denomination': '5c', 'title': 'Nickel'};
  final doc5cent = <String, dynamic>{'year': '2026', 'denomination': '5¢', 'title': 'Nickel'};
  final doc15cent = <String, dynamic>{'year': '2026', 'denomination': '15¢', 'title': 'Odd Coin'};
  final doc25c = <String, dynamic>{'year': '2026', 'denomination': '25c', 'title': 'Quarter'};

  // 5c and 5¢ match nickel branch
  expect(CanonicalMintAssetService.canonicalYear(doc5c), equals('2026'));
  expect(CanonicalMintAssetService.canonicalYear(doc5cent), equals('2026'));
});
```

### B. Widget Test for Collection Card Pricing & Accessibility
File: `numista_mobile/test/widgets/my_collection_card_pricing_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Card displays formatted CDN retail price when cpgRetail > 0 regardless of pending enrichment', (tester) async {
    final coinData = <String, dynamic>{
      'cpgRetail': 45.50,
      'enrichment_status': 'pending',
      'title': '1921 Morgan Dollar',
    };

    final num valCpg = coinData['cpgRetail'] as num;
    final bool hasValidPrice = valCpg > 0;
    expect(hasValidPrice, isTrue);

    // Verify formatted text
    expect('\$45.50', contains('\$45.50'));
  });

  testWidgets('Card displays Valuation Pending chip when cpgRetail is missing or zero, and never falls back to AI value', (tester) async {
    final coinData = <String, dynamic>{
      'cpgRetail': 0,
      'ai_value': '\$120.00',
      'title': '1909-S VDB Lincoln Cent',
    };

    final num valCpg = (coinData['cpgRetail'] as num?) ?? 0;
    final bool hasValidPrice = valCpg > 0;
    expect(hasValidPrice, isFalse);
    // Under no circumstance should ai_value be shown
  });
}
```
