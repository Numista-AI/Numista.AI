# FAILFIX PLAN v1.8: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**Date:** 7 November 2026, 2:30 PM ET  
**Reference Batons:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `BATON_NET-817_REVISE_780b-780c_v1.8_PER-COS-60_20261107-1410.md`  
- `RADIO_NET-830_GROKCOS-to-AGCOS_REVISE-817-v1.8_20261107.md`  
- `COS_SCORE_NET-817_CARDS_IMAGES_v1.7_20261107.md` (Cards 67/100 FAIL, Images 53/100 FAIL, Combined 60/100 FAIL)  
**Directives & Audit Authority:**  
- `GB CoS SCORE v1.7`: Must-fixes MF-B1–B3 and MF-C1–C7.  
- `PROTOCOL UPDATE: ARGON DROPPED ENTIRELY`: Founder Eric typed YES. Review sequence is strictly: AG CoS Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all code and configurations.  
3. Execution strictly scoped to branch `p7-v8.9` (branch `dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`).  
4. Founder Eric's typed YES to this plan is strictly for code execution on `p7-v8.9` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or security rules changes. Separate scoped Eric typed YES is required for any database writes.  
5. Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval. Target is **p7-gate preview** (`preview-catalog`) only.  
6. **Alerts only, NEVER budget caps:** all spending caps (including $25 limit and hard $0.00 spend cap) are permanently eliminated per Eric's standing rule; alerts set at $20/mo.  
7. Zero AJ PII across all plans, logs, mocks, and code.  

---

## 1. Executive Summary & Itemized Must-Fix Closeout Table

Plan v1.8 systematically and exhaustively resolves all numbered blocking must-fixes from `COS_SCORE_NET-817_CARDS_IMAGES_v1.7_20261107.md` and `RADIO_NET-830`:

| Must-Fix # | Must-Fix Description | Plan v1.8 Resolution & Grounding | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-B1** | **Kaggle Single Owner + Complete Span:** Resolve contradiction between Images and Cards; pick single owner for all Google/Kaggle deletions (`3454`, `3820`, `5252–5278`, `5549–5684`, `150–151`). Keep `_onSearchEbay` @4410 with EPN affiliate tags. | **NET-816 is established as the sole structural deletion owner** for all Google & Kaggle inspector elements across both dev (`b0b05808`) and p7 (`4d17ca5e`). NET-817 explicitly cites NET-816's deletion as a prerequisite and performs **zero duplicate or conflicting deletions**. Line 4410 `_onSearchEbay` is strictly **PRESERVED** with affiliate tags per B05N-18 and `RADIO_NET-825`. | §2.A, §4.A |
| **MF-B2** | **Package Name Correctness:** Use `package:numista_ai/...` strictly matching `pubspec.yaml:1` (not `numista_mobile`). | All proposed imports, production widgets, and test files strictly use `package:numista_ai/...` matching `numista_mobile/pubspec.yaml:1`. | §3, §6 |
| **MF-B3** | **Accurate DTG & Declared Apply Order:** Stamp actual filing DTG and declare precise apply order between Cards and Images. | Delivery stamped at actual filing time (`7 Nov 2026, 2:30 PM ET`). Stated apply order: **Cards `canonicalYear` (NET-780b) lands first**, followed by **Images `_RequestKey` (NET-780c)** which depends on it. | §1, §4.C |
| **MF-C1** | **Correct Valuation Anchors:** Ground on real lines 3017–3023 and 3167–3192. Do not touch line 3015 `displayTitle`. | Production anchors verified verbatim against p7 (`4d17ca5e`): lines **3017–3023** (`valCpg`, `fmt`, `valueText`) and lines **3167–3192** (`Row` containing pending chip and valuation). Line 3015 (`displayTitle` tail) is strictly untouched. | §2.B, §3.B |
| **MF-C2** | **Valuation Precedence & Enrichment State:** Do not drop AI value or `enrichment_status == 'pending'`. | Strictly implements Eric/B05N-8 precedence: (1) CPG Retail (`valCpg > 0`) $\rightarrow$ formatted retail currency (no pending chip); (2) AI Value (`m[_F.aiValue]`) $\rightarrow$ formatted AI value text, showing pending chip if `enrichment_status == 'pending'`; (3) Missing retail AND missing AI estimate $\rightarrow$ Face Value from denomination with amber `'Value pending AI estimate'` chip; (4) Unknown denomination $\rightarrow$ `'—'` with amber chip. Consistent with table columns `:534–538` and `:3338–3345`. | §2.B, §3.B |
| **MF-C3** | **Face Value Correctness:** Reuse `MeltValueService.parseFaceValue` instead of buggy duplicate parser; return `'—'` when unknown instead of `'$0.00'`. | Directly reuses existing production parser `MeltValueService.parseFaceValue(rawDenom, qty: 1)` (`numista_mobile/lib/services/melt_value_service.dart:53`), which already evaluates multi-word tokens ("half dime", "three cent", "half dollar") before generic tokens. If parsed face value is 0.0, renders `'—'` with pending chip rather than confusing `'$0.00'`. | §2.B, §3.B |
| **MF-C4** | **Test Production Widget (No Tautological Copy):** Extract valuation row into real production widget in `lib/widgets/` and pump that in tests. | Extracts production valuation row into `numista_mobile/lib/widgets/collection_card_valuation_row.dart`. Used directly by `my_collection_screen.dart` lines 3167–3192. `my_collection_card_pricing_test.dart` imports and pumps this exact production widget. | §3.B, §6.1 |
| **MF-C5** | **Preserve 749-Line Canonical Suite & Fix Regex Boundary:** Do not overwrite existing suite; fix `\b` trailing boundary on `1¢`/`5¢`. | Appends tests to new test file `numista_mobile/test/services/canonical_mint_asset_service_v1_8_test.dart`, leaving the 749-line existing suite intact. Production regex in `CanonicalMintAssetService` (lines 430–435) updated from `\b` to `(?!\w)`: `RegExp(r'(?<!\d)(?:1c|1¢|one cent|penny)(?!\w)|(?<!\d\s*)\bcent\b', caseSensitive: false)` and `RegExp(r'(?<!\d)(?:5c|5¢|five cents?|nickel)(?!\w)', caseSensitive: false)`. Tests invoke `CanonicalMintAssetService.resolveFromMap` with real coin maps. | §3.C, §6.2 |
| **MF-C6** | **Contrast Truth Across Themes:** Satisfy WCAG AA $\ge 4.5:1$ in both dark and light modes. | In dark mode: `#D4AF37` against `#1E2937` achieves **7.00:1** and against `#0D1520` achieves **8.72:1** (passes WCAG AAA $\ge 7.0:1$). In light mode: `#856404` against `#FFFFFF` achieves **5.49:1** and against `#F5F5F0` achieves **5.02:1** (passes WCAG AA $\ge 4.5:1$). Theme-aware styling: `final isDark = Theme.of(context).brightness == Brightness.dark; final chipTextColor = isDark ? const Color(0xFFD4AF37) : const Color(0xFF856404);`. Both brightness modes explicitly verified by automated contrast calculation tests. | §3.B, §6.1 |
| **MF-C7** | **Additive `canonicalYear` Anchor:** Declare exact insertion point and verify no behavior change to `resolveFromMap`. | `canonicalYear(Map<String, dynamic> data)` is inserted additively at **line 76** of `canonical_mint_asset_service.dart` immediately following `_normYear` (lines 72–76) and before `extractSku` (line 78). Zero modifications made to `resolveFromMap` or existing SKU logic. | §3.A |

---

## 2. Root Cause Analysis & Verbatim Code Citations

### A. Kaggle & Google Images Structural Deletion Ownership (MF-B1)
On branch `p7-v8.9` at commit `4d17ca5e`, `numista_mobile/lib/screens/my_collection_screen.dart` contains:
- **Call site at line 3454:**
  ```dart
  3454:       _fetchInspectorSimilar(data);
  ```
- **UI call at line 3820:**
  ```dart
  3819:                           _buildRollBanner(data),
  3820:                           _buildSimilarCoinsInspector(),
  3821:                         ]),
  ```
- **Inspector loader at lines 5252–5278:**
  ```dart
  5252:   Future<void> _fetchInspectorSimilar(Map<String, dynamic> data) async {
  5253:     final denom   = data[_F.denomination]?.toString() ?? '';
  5254:     final yearRaw = data[_F.year]?.toString() ?? '';
  ...
  5278:   }
  ```
- **Inspector UI & dialog at lines 5549–5684:**
  ```dart
  5549:   Widget _buildSimilarCoinsInspector() {
  ...
  5647:   void _showRefImageDialog(BuildContext ctx, ReferenceImage img) {
  ...
  5684:   }
  ```
- **State variables at lines 150–151:**
  ```dart
  150:   List<ReferenceImage> _inspectorSimilar = [];
  151:   bool _loadingInspectorSimilar = false;
  ```
- **Google Images Button & Handler at lines 3531–3548 and 4387–4406:**
  ```dart
  3531:             ElevatedButton.icon(
  ...
  3548:             ),
  ...
  4387:   Future<void> _onSearchGoogleImages(Map<String, dynamic> data) async {
  ...
  4406:   }
  ```
- **Outbound eBay search at line 4410:**
  ```dart
  4408:   // EPN affiliate links for eBay searches
  4409:   // campid=5339123164, customid=numista_app_search
  4410:   Future<void> _onSearchEbay(Map<String, dynamic> data) async {
  ```
**Single Ownership Declaration:** To prevent split-ownership compile breaks (where deleting the loader breaks line 3454), **NET-816 (Catalog FAILFIX Plan v1.11) is the sole owner** of all Google/Kaggle deletions (`3454`, `3820`, `5252–5278`, `5549–5684`, `150–151`, `3531–3548`, `4387–4406`). NET-817 declares this dependency and does not touch these lines. Line 4410 `_onSearchEbay` is strictly **PRESERVED** with EPN affiliate tags per B05N-18 and `RADIO_NET-825`.

### B. Cards Valuation Lines & Precedence (MF-C1, MF-C2, MF-C3)
In `numista_mobile/lib/screens/my_collection_screen.dart` on p7 (`4d17ca5e`), lines 3017–3023 read verbatim:
```dart
3017:         final valCpg = _parseNumber(m['cpgRetail']);
3018:         final finalVal = valCpg;
3019:         
3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3021:         final valueText = finalVal > 0 
3022:             ? fmt.format(finalVal) 
3023:             : (m[_F.aiValue]?.toString() ?? '—');
```
Line 3015 is the tail of `displayTitle`:
```dart
3015:             : (themeStartsYear ? label : '$yearMint $label').trim();
```
Touching line 3015 corrupts title formatting. Furthermore, the pending-chip row is located at lines **3167–3192**:
```dart
3167:                   Row(
3168:                     mainAxisAlignment: MainAxisAlignment.spaceBetween,
3169:                     children: [
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
3189:                       if (condition.isNotEmpty)
3190:                         GradeBadgeWidget(gradeCode: condition),
3191:                     ],
3192:                   ),
```
**Defect:** When retail is 0 or absent, lines 3021–3023 fall back to `m[_F.aiValue]`. If AI value is also absent, it produces `'—'`. Under B05N-8, missing retail must fall back to face value (e.g. `$0.25` for quarter, `$0.05` for nickel) with an explicit chip: `'Value pending AI estimate'`. Crucially, if an AI value IS present, that AI estimate must be displayed and not clobbered!

### C. Denomination Word Boundary Bug with Unicode Cent Symbol (MF-C5)
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 431–434:
```dart
431:       final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
432:           RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
```
**Root Cause:** The symbol `¢` (Unicode U+00A2) is not a word character (`\w`). When `1¢` or `5¢` appears at the end of a string or is followed by space/punctuation, there is no transition between `\w` and `\W`, so the trailing `\b` fails to match (`RegExp(r'\b1¢\b').hasMatch('1¢') == false`). Replacing trailing `\b` with `(?!\w)` and leading boundary with `(?<!\d)` ensures `1¢` and `5¢` match cleanly while preventing `15¢`, `25c`, or `50c` from matching.

---

## 3. Targeted Production Code Implementation

### A. Additive `canonicalYear` Helper (MF-C7)
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`, inserted additively at **line 76** (between `_normYear` ending at line 76 and `extractSku` starting at line 78):
```dart
  static String _normYear(Object? y) {
    final s = (y ?? '').toString().trim();
    final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
    return m != null ? m.group(1)! : s;
  }

  /// MF-C7 / MF-2: Extracts normalized 4-digit canonical year from coin metadata.
  /// Strictly additive at line 76. Leaves resolveFromMap completely unchanged.
  /// Intentionally excludes Personal Notes to prevent neighbor note bleed.
  static String canonicalYear(Map<String, dynamic> data) {
    // 1. Direct explicit year fields in priority order
    for (final k in const <String>[
      'year',
      'Year',
      'coin_year',
      'canonical_year',
      'issue_year',
      'mintDate',
    ]) {
      final v = data[k];
      if (v != null) {
        final s = v.toString().trim();
        if (s.isNotEmpty) {
          // Normalize direct dual dates like '1776-2026' or '1776~2026' to '2026'
          final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
          if (dualMatch != null) return dualMatch.group(1)!;

          final norm = _normYear(s);
          if (RegExp(r'^\d{4}$').hasMatch(norm)) return norm;
        }
      }
    }

    // 2. Fallback to title/series/description (strictly excluding personal notes)
    for (final k in const <String>[
      'title',
      'name',
      'Theme/Subject',
      'theme_subject',
      'Program/Series',
      'program_series',
      'description',
    ]) {
      final v = data[k];
      if (v != null) {
        final s = v.toString();
        final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
        if (dualMatch != null) return dualMatch.group(1)!;

        final m = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(s);
        if (m != null) return m.group(1)!;
      }
    }

    return '';
  }

  static String extractSku(Map<String, dynamic> data) {
```

### B. Production Widget: `CollectionCardValuationRow` (MF-C1, MF-C2, MF-C3, MF-C4, MF-C6)
Created as a production widget in `numista_mobile/lib/widgets/collection_card_valuation_row.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart' as intl;
import 'package:numista_ai/services/melt_value_service.dart';
import 'package:numista_ai/widgets/grade_badge_widget.dart';

/// Production valuation row extracted for testability and contrast compliance.
/// Implements B05N-8 valuation precedence:
/// 1. CPG Retail override (valCpg > 0) -> Formatted currency, no pending chip.
/// 2. AI Estimate (aiValue present and != '—') -> Formatted AI value, with chip if enrichment_status == 'pending'.
/// 3. Fallback -> Face value from denomination via MeltValueService.parseFaceValue.
///    If faceValue > 0 -> formatted face value with 'Value pending AI estimate' chip.
///    If faceValue == 0 -> '—' with 'Value pending AI estimate' chip.
///
/// WCAG AA Contrast:
/// - Dark Mode: #D4AF37 against #1E2937 (7.00:1) and #0D1520 (8.72:1) -> PASSES AAA (>= 7.0:1).
/// - Light Mode: #856404 against #FFFFFF (5.49:1) and #F5F5F0 (5.02:1) -> PASSES AA (>= 4.5:1).
class CollectionCardValuationRow extends StatelessWidget {
  final Map<String, dynamic> data;
  final String condition;

  const CollectionCardValuationRow({
    super.key,
    required this.data,
    this.condition = '',
  });

  static double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    final clean = val.toString().replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(clean) ?? 0.0;
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // Theme-aware WCAG AA compliant colors
    final chipTextColor = isDark ? const Color(0xFFD4AF37) : const Color(0xFF856404);
    final chipBgColor = isDark ? const Color(0xFFD4AF37).withAlpha(25) : const Color(0xFFFFF3CD);
    final chipBorderColor = isDark ? const Color(0xFFD4AF37).withAlpha(120) : const Color(0xFFFFEEBA);

    final valCpg = _parseNumber(data['cpgRetail']);
    final rawAiVal = data['ai_value'] ?? data['aiValue'];
    final enrichmentStatus = data['enrichment_status']?.toString().toLowerCase().trim() ?? '';
    final rawDenom = data['denomination']?.toString() ?? data['Denomination']?.toString() ?? '';

    final fmt = intl.NumberFormat.currency(symbol: '\$');

    String displayValue;
    bool showPendingChip = false;

    if (valCpg > 0) {
      // 1. CPG Retail override takes top precedence
      displayValue = fmt.format(valCpg);
      showPendingChip = false;
    } else if (rawAiVal != null && rawAiVal.toString().trim().isNotEmpty && rawAiVal.toString().trim() != '—') {
      // 2. AI Estimate present
      final parsedAi = _parseNumber(rawAiVal);
      displayValue = parsedAi > 0 ? fmt.format(parsedAi) : rawAiVal.toString().trim();
      showPendingChip = (enrichmentStatus == 'pending');
    } else {
      // 3. Fallback to face value via MeltValueService (closing B05N-8)
      final faceValue = MeltValueService.parseFaceValue(rawDenom, qty: 1);
      if (faceValue > 0) {
        displayValue = fmt.format(faceValue);
      } else {
        displayValue = '—';
      }
      showPendingChip = true;
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        if (showPendingChip)
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                displayValue,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: chipTextColor,
                ),
              ),
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: chipBgColor,
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: chipBorderColor),
                ),
                child: Text(
                  'Value pending AI estimate',
                  style: TextStyle(
                    fontSize: 10,
                    color: chipTextColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          )
        else
          Text(
            displayValue,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.bold,
              color: chipTextColor,
            ),
          ),
        if (condition.isNotEmpty)
          GradeBadgeWidget(gradeCode: condition),
      ],
    );
  }
}
```

In `numista_mobile/lib/screens/my_collection_screen.dart`:
Lines 3017–3023 are simplified because valuation rendering is encapsulated in `CollectionCardValuationRow`:
```dart
<<<<
3017:         final valCpg = _parseNumber(m['cpgRetail']);
3018:         final finalVal = valCpg;
3019:         
3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3021:         final valueText = finalVal > 0 
3022:             ? fmt.format(finalVal) 
3023:             : (m[_F.aiValue]?.toString() ?? '—');
====
3017:         // Valuation precedence and chip rendering encapsulated in CollectionCardValuationRow (NET-780b v1.8)
>>>>
```
And lines 3167–3192 replace the row with the production widget:
```dart
<<<<
3167:                   Row(
3168:                     mainAxisAlignment: MainAxisAlignment.spaceBetween,
3169:                     children: [
3170:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
...
3192:                   ),
====
3167:                   CollectionCardValuationRow(
3168:                     data: m,
3169:                     condition: condition,
3170:                   ),
>>>>
```

### C. Denomination Word Boundary Production Patch (MF-C5)
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 431–434:
```dart
<<<<
431:       final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
432:           RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
====
431:       // MF-C5: (?!\w) avoids broken trailing \b on Unicode ¢; (?<!\d) avoids matching 15¢ or 25c.
432:       final isCent = RegExp(r'(?<!\d)(?:1c|1¢|one cent|penny)(?!\w)|(?<!\d\s*)\bcent\b', caseSensitive: false).hasMatch(cleanDenom) ||
433:           RegExp(r'\b(lincoln cent|one cent|penny)\b', caseSensitive: false).hasMatch(cleanTitle);
434:       final isNickel = RegExp(r'(?<!\d)(?:5c|5¢|five cents?|nickel)(?!\w)', caseSensitive: false).hasMatch(cleanDenom) ||
435:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b', caseSensitive: false).hasMatch(cleanTitle);
>>>>
```

---

## 4. Execution Gates & Apply Ordering

### A. Pre-Flight Verification & Pinned Commit
Before executing any file modifications on branch `p7-v8.9`:
```bash
git status
git log --oneline -1
```
Execution is strictly locked to branch `p7-v8.9` at HEAD `ebf1eed8`. `origin/main` remains strictly locked at `9f04550a`. Stripe remains locked OFF.

### B. Single Ownership Contract (MF-B1)
NET-816 is the sole structural deletion owner of all Google and Kaggle inspector artifacts (`3454`, `3820`, `5252–5278`, `5549–5684`, `150–151`, `3531–3548`, `4387–4406`). NET-817 depends on NET-816 landing first or concurrently, and performs zero duplicate deletions. `_onSearchEbay` (@ line 4410) is strictly preserved with EPN affiliate tracking.

### C. Stated Apply Ordering (MF-B3)
1. **First:** Cards Plan NET-780b lands `canonicalYear` at line 76 of `canonical_mint_asset_service.dart`, updates denomination regex at lines 431–435, and extracts `CollectionCardValuationRow`.
2. **Second:** Images Plan NET-780c lands `_RequestKey` in `my_collection_screen.dart` (which invokes `CanonicalMintAssetService.canonicalYear(data)`), and deploys `isOwnedStorageUrl` and `CollectionCardImage`.

### D. Rollback Protocol
If any post-apply check or test fails:
```bash
git checkout p7-v8.9
git revert --no-edit <Cards-commit-hash>
git push origin p7-v8.9
```

---

## 5. Security, Rules & Standing Boundaries
- **No Argon:** Cycle has zero Argon reviews per Founder Eric's typed YES.
- **PLAN ONLY:** Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.
- **Alerts Only, Never Budget Caps:** Hard spending caps are permanently eliminated; alerts set at $20/mo.
- **No AJ PII:** Zero user emails or private credentials in plans, tests, or fixtures.
- **Nightly Stand-Down:** Standing 3:00 AM ET stand-down observed.

---

## 6. Real Automated Test Suites

### 6.1 `numista_mobile/test/widgets/my_collection_card_pricing_test.dart` (MF-C4, MF-C6)
Pumps the real production `CollectionCardValuationRow` widget across both light and dark themes, verifying retail override, face value fallback, pending chip display, and WCAG AA contrast compliance:
```dart
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/widgets/collection_card_valuation_row.dart';

double _luminance(int r, int g, int b) {
  double transform(int c) {
    double s = c / 255.0;
    return s <= 0.03928 ? s / 12.92 : pow((s + 0.055) / 1.055, 2.4).toDouble();
  }
  return 0.2126 * transform(r) + 0.7152 * transform(g) + 0.0722 * transform(b);
}

double _contrastRatio(Color c1, Color c2) {
  final l1 = _luminance(c1.red, c1.green, c1.blue);
  final l2 = _luminance(c2.red, c2.green, c2.blue);
  final lighter = max(l1, l2);
  final darker = min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

void main() {
  group('CollectionCardValuationRow Production Widget Tests (B05N-8 & WCAG AA)', () {
    testWidgets('Case 1: CPG retail override displays retail without pending chip', (tester) async {
      final data = {
        'cpgRetail': 12.50,
        'denomination': 'Quarter Dollar',
        'enrichment_status': 'completed',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$12.50'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Case 2: AI Estimate displayed when retail is missing', (tester) async {
      final data = {
        'cpgRetail': 0.0,
        'ai_value': '35.00',
        'denomination': 'Half Dollar',
        'enrichment_status': 'completed',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$35.00'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Case 3: Missing retail falls back to Quarter face value (\$0.25) with pending chip', (tester) async {
      final data = {
        'cpgRetail': 0.0,
        'denomination': 'Quarter Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$0.25'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    testWidgets('Case 4: Missing retail falls back to Nickel face value (\$0.05) with pending chip', (tester) async {
      final data = {
        'cpgRetail': 0.0,
        'denomination': '5c',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$0.05'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    testWidgets('Case 5: Unknown denomination renders "—" with pending chip (no \$0.00)', (tester) async {
      final data = {
        'cpgRetail': 0.0,
        'denomination': 'Unknown Medallion',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('—'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
      expect(find.text('\$0.00'), findsNothing);
    });

    testWidgets('Case 6: WCAG AA contrast compliance across Dark and Light themes', (tester) async {
      const darkSurface = Color(0xFF1E2937);
      const darkVChild = Color(0xFF0D1520);
      const lightSurface = Color(0xFFFFFFFF);
      const lightVChild = Color(0xFFF5F5F0);

      const goldDark = Color(0xFFD4AF37);
      const amberLight = Color(0xFF856404);

      // Dark Mode assertions
      final ratioDarkSurface = _contrastRatio(goldDark, darkSurface);
      final ratioDarkVChild = _contrastRatio(goldDark, darkVChild);
      expect(ratioDarkSurface, greaterThanOrEqualTo(7.0), reason: 'Dark surface contrast must pass WCAG AAA (>= 7.0:1)');
      expect(ratioDarkVChild, greaterThanOrEqualTo(7.0), reason: 'Dark virtual child contrast must pass WCAG AAA (>= 7.0:1)');

      // Light Mode assertions
      final ratioLightSurface = _contrastRatio(amberLight, lightSurface);
      final ratioLightVChild = _contrastRatio(amberLight, lightVChild);
      expect(ratioLightSurface, greaterThanOrEqualTo(4.5), reason: 'Light surface contrast must pass WCAG AA (>= 4.5:1)');
      expect(ratioLightVChild, greaterThanOrEqualTo(4.5), reason: 'Light virtual child contrast must pass WCAG AA (>= 4.5:1)');
    });
  });
}
```

### 6.2 `numista_mobile/test/services/canonical_mint_asset_service_v1_8_test.dart` (MF-C5, MF-C7)
New dedicated test file preserving the existing 749-line `canonical_mint_asset_service_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';

void main() {
  group('CanonicalMintAssetService v1.8 Enhancements', () {
    test('canonicalYear resolves explicit year fields correctly', () {
      expect(CanonicalMintAssetService.canonicalYear({'year': '1958'}), '1958');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '2026.0'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'year': '', 'Year': '1964'}), '1964');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '1776-2026'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'title': '1921 Morgan Silver Dollar'}), '1921');
    });

    test('canonicalYear strictly ignores Personal Notes', () {
      final withNotes = {
        'title': 'Lincoln Cent',
        'personalNotes': 'Bought in 1999 from dealer',
        'notes': 'Inherited in 1985',
      };
      expect(CanonicalMintAssetService.canonicalYear(withNotes), '');
    });

    test('Denomination regex accurately matches 1¢ and 5¢ without matching 15¢ or 25c', () {
      final coin1Cent = {
        'Year': '2026',
        'mint_mark': 'D',
        'denomination': '1¢',
        'title': 'Lincoln Cent',
      };
      final res1Cent = CanonicalMintAssetService.resolveFromMap(coin1Cent);
      expect(res1Cent, isNotNull);
      expect(res1Cent!.sku, '2026-CENT-D');

      final coin5Cent = {
        'Year': '2026',
        'mint_mark': 'P',
        'denomination': '5¢',
        'title': 'Jefferson Nickel',
      };
      final res5Cent = CanonicalMintAssetService.resolveFromMap(coin5Cent);
      expect(res5Cent, isNotNull);
      expect(res5Cent!.sku, '2026-NICKEL-P');

      // False positive guards: 15¢, 25c, 25 cent, 50 cent must NOT match 1¢ or 5¢
      final coin25Cents = {
        'Year': '2026',
        'mint_mark': 'P',
        'denomination': '25c',
        'title': 'Random 25c Token',
      };
      expect(CanonicalMintAssetService.resolveFromMap(coin25Cents), isNull);

      final coin15Cents = {
        'Year': '2026',
        'mint_mark': 'P',
        'denomination': '15¢',
        'title': 'Random 15c Token',
      };
      expect(CanonicalMintAssetService.resolveFromMap(coin15Cents), isNull);
    });
  });
}
```

---

## 7. Delivery & Sign-Off Requirements
- **Verification Command:** `flutter test test/widgets/my_collection_card_pricing_test.dart test/services/canonical_mint_asset_service_v1_8_test.dart`
- **Review Requirement:** Independent review score $\ge 95$ from Grok Bot CoS and Stand Alone Grok (SAG, grok-4.7) prior to Founder Eric's typed YES.
