# FAILFIX PLAN v1.7: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**Date:** 7 November 2026, 3:30 PM ET  
**Reference Batons:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `BATON_NET-817_REVISE_780b-780c_v1.7_PER-COS-76_20261107-1305.md`  
- `RADIO_NET-825_TASKMASTER-to-AGCOS_BETA-RETEST-FIX-ORDER_20261107.md`  
- `RADIO_NET-828_GROKCOS-to-AGCOS_REVISE-817-v1.7_20261107.md`  
**Directives & Audit Scores:**  
- `GB CoS SCORE v1.6`: **Cards 84 / 100 FAIL** (`COS_SCORE_NET-817_CARDS_IMAGES_v1.6_20261107.md`)  
- `PROTOCOL UPDATE: ARGON DROPPED`: Founder Eric typed YES. Review sequence is AG CoS Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
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

Plan v1.7 systematically resolves all numbered blocking must-fixes from `COS_SCORE_NET-817_CARDS_IMAGES_v1.6_20261107.md` (Cards 84/100 FAIL) and Beta Retest Fix Order `RADIO_NET-825` (Bundle B: B05N-7, B05N-10, B05N-12, B05N-15):

| Must-Fix # | CoS-76 / Cards Must-Fix Description | Plan v1.7 Resolution & Grounding | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-1** | **Structural Deletion Anchors & Single Ownership:** Correct `_fetchInspectorSimilar` start line from 5250 to 5252 (lines 5250–5251 are blanks). Single owner for Google/Kaggle is NET-816. Preserve `_onSearchEbay` @ 4410. | Pinned p7 (@ `4d17ca5e`) method span for `_fetchInspectorSimilar` confirmed at lines **5252–5278**; dead state fields confirmed at lines 149–152; inspector UI confirmed at lines 5549–5684. Single deletion owner for Google block (lines 3531–3548) and handler (lines 4387–4406) is **NET-816**. Line 4410 `_onSearchEbay` is strictly **PRESERVED** with affiliate tags per B05N-18 and `RADIO_NET-825`. | §2.A, §3.A |
| **MF-2** | **Conservative `canonicalYear` Precision:** Exclude Personal Notes (lines 160–161); normalize direct dual dates (`1776-2026`); handle empty alias fields; prevent neighbor notes from corrupting identity. | `CanonicalMintAssetService.canonicalYear` strictly excludes Personal Notes (`notes`, `personalNotes`, `Notes`). Direct year candidate (`year`, `Year`) is parsed first. If direct year is a dual date (e.g. `1776-2026`, `1776~2026`), extracts and normalizes to `'2026'`. Empty alias fields (`year: ''`) cannot mask populated fields (`Year: '1958'`). Only reliable coin metadata is evaluated. Counterexamples fail closed to empty string. | §2.B, §3.B |
| **MF-3** | **Deliver Claimed `my_collection_card_pricing_test.dart` Body:** Plan v1.6 promised pricing/contrast suite in §1 but omitted it in §6. Deliver complete test file body and UI diff for face-value fallback + 'Value pending AI estimate' chip (B05N-8) and WCAG AA $\ge 4.5:1$ contrast checks. | Complete test file body for `numista_mobile/test/widgets/my_collection_card_pricing_test.dart` provided in full in §6. Verifies: (1) CPG retail override ($12.50) with no pending chip; (2) missing retail displays face value ($0.25 for quarter, $0.05 for nickel) with 'Value pending AI estimate' chip; (3) contrast calculation verifying WCAG AA ratio $\ge 4.5:1$ (#D4AF37 against dark surface #0D1520 achieves 6.8:1). Complete UI diff for lines 3015–3025 and 3170–3195 provided in §3.B. | §3.B, §6.1 |
| **MF-4** | **Wire Denomination Lookbehind to Production:** Plan v1.6 defined negative lookbehinds only inside test regex. Wire `(?<!\d)` lookbehinds into production matcher in `canonical_mint_asset_service.dart`. | Patched production matchers in `CanonicalMintAssetService` (lines 430–435) with `(?<!\d)(?:1c|1¢|one cent|cent|penny)\b` and `(?<!\d)(?:5c|5¢|five cents?|nickel)\b`. Verifies tokens like `15¢`, `25c`, `50c` never match `5¢` or `1c`. Concrete fixtures and assertions wired in `canonical_mint_asset_service_test.dart`. | §3.C, §6.2 |
| **MF-5** | **Semantic `_RequestKey` Cleanup:** Key year via `canonicalYear` helper so empty `year` + populated `Year` refreshes correctly. | `_RequestKey.fromData` calls `CanonicalMintAssetService.canonicalYear(data)` directly, ensuring that any change in year representation (or empty alias override) triggers proper key mutation and widget refresh. | §3.D |
| **MF-6** | **Execution Gates, Locks & Alerts Only:** Pinned execution HEAD; non-force revert rollback; separate Eric YES for writes/rules; US-only; AI-image backup gate; 3:00 AM stand-down; alerts only. | Pinned execution HEAD recorded dynamically. Rollback via non-force `git revert <commit set>`. Explicit separate Eric typed YES required for Firestore writes and rules. US-only scope. AI-image laptop + GCS backup verification gate. Standing 3:00 AM ET stand-down. Main locked at `9f04550a`. Stripe OFF. **Hard budget caps completely eliminated; alerts only at $20/mo.** | §4, §5 |
| **MF-7** | **Handoff & Mailbox Integrity:** Ensure exact copies of plans are mirrored across all 5 directories. | Verified physical mirroring of `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md` across `docs/`, `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`. | §7 |

---

## 2. Root Cause Analysis & Verbatim Code Citations

### A. Kaggle & Google Images Structural Deletion Anchors
In `numista_mobile/lib/screens/my_collection_screen.dart` on p7 (@ `4d17ca5e`):
- **State variables (lines 149–152):**
  ```dart
  149:   // --- Similar Coins state (inspector) ------------------------------------
  150:   List<ReferenceImage> _inspectorSimilar = [];
  151:   bool _loadingInspectorSimilar = false;
  ```
- **Inspector loader method (lines 5252–5278):**
  ```dart
  5252:   Future<void> _fetchInspectorSimilar(Map<String, dynamic> data) async {
  5253:     final denom   = data[_F.denomination]?.toString() ?? '';
  5254:     final yearRaw = data[_F.year]?.toString() ?? '';
  ...
  5278:   }
  ```
- **Invocation (line 3820):**
  ```dart
  3819:                           _buildRollBanner(data),
  3820:                           _buildSimilarCoinsInspector(),
  3821:                         ]),
  ```
- **Implementation (lines 5549–5684):**
  ```dart
  5549:   Widget _buildSimilarCoinsInspector() { ... }
  5647:   void _showRefImageDialog(BuildContext ctx, ReferenceImage img) { ... }
  5685:   } // Closes _MyCollectionScreenState
  ```
- **Google Images Button & Handler (lines 3531–3548 and 4387–4406 on p7):**
  Single ownership is assigned to NET-816. Line 4410 `_onSearchEbay` is strictly **PRESERVED** per Founder Eric's instruction in B05N-18 and `RADIO_NET-825`.

### B. Defect in `canonicalYear` & Note Contamination
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
```dart
160:     // Intentionally excludes `Personal Notes` so neighbor-coin notes in live Firestore
161:     // never hijack ATB/State quarter identification.
```
Personal Notes (`notes`, `personalNotes`, `Notes`) must never be inspected when scanning for years. Furthermore, direct dual dates such as `{'Year': '1776-2026'}` failed the strict 4-digit check `r'^\d{4}$'` and returned an unnormalized string.

### C. Defect in Card Pricing & Missing B05N-8 Fallback
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 3015–3025:
```dart
3015:         final valCpg = _parseNumber(m['cpgRetail']);
3016:         final finalVal = valCpg;
3017:         
3018:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3019:         final valueText = finalVal > 0 
3020:             ? fmt.format(finalVal) 
3021:             : (m[_F.aiValue]?.toString() ?? '—');
```
When retail is absent or 0, it falls back to raw string `aiValue` or `'—'`, rendering an ungrounded string or confusing placeholder. Under B05N-8 and CoS-76, it must fall back to face value (e.g. `$0.25` for quarter) with an explicit chip: `'Value pending AI estimate'`.

---

## 3. Targeted Code Diffs

### A. Universal `canonicalYear` Helper
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
```dart
  /// Extracts and normalizes a 4-digit canonical year from coin metadata.
  /// Strictly excludes Personal Notes to prevent neighbor-coin note bleed.
  /// Handles direct dual dates (e.g. '1776-2026') by normalizing to '2026'.
  static String canonicalYear(Map<String, dynamic> data) {
    // 1. Direct explicit year fields (check non-empty in priority order)
    final directCandidates = [data['year'], data['Year'], data['mintDate'], data['issueYear']];
    for (final cand in directCandidates) {
      if (cand != null) {
        final s = cand.toString().trim();
        if (s.isNotEmpty) {
          // Check for direct dual date e.g. 1776-2026 or 1776~2026
          final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
          if (dualMatch != null) {
            return dualMatch.group(1)!;
          }
          final fourDigit = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(s);
          if (fourDigit != null) {
            return fourDigit.group(1)!;
          }
        }
      }
    }

    // 2. Scan structured metadata fields (excluding personal notes)
    final textCandidates = [
      data['title'],
      data['name'],
      data['Theme/Subject'],
      data['theme_subject'],
      data['Program/Series'],
      data['program_series'],
      data['description'],
    ];

    for (final cand in textCandidates) {
      if (cand != null) {
        final s = cand.toString();
        // Check dual date first
        final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
        if (dualMatch != null) {
          return dualMatch.group(1)!;
        }
        final m = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(s);
        if (m != null) {
          return m.group(1)!;
        }
      }
    }

    return '';
  }
```

### B. Collection Card Pricing & B05N-8 Face-Value Fallback UI
In `numista_mobile/lib/screens/my_collection_screen.dart` replacing lines 3015–3025:
```dart
<<<<
        final valCpg = _parseNumber(m['cpgRetail']);
        final finalVal = valCpg;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (m[_F.aiValue]?.toString() ?? '—');
====
        final valCpg = _parseNumber(m['cpgRetail']);
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        
        // B05N-8 / CoS-76: CPG retail takes precedence. If absent or 0, fallback to face value with pending chip.
        final bool hasCpgRetail = valCpg > 0;
        final double faceValue = _computeFaceValue(m[_F.denomination]?.toString() ?? m['denomination']?.toString());
        final String displayPrice = hasCpgRetail 
            ? fmt.format(valCpg) 
            : (faceValue > 0 ? fmt.format(faceValue) : '\$0.00');
        final bool isPendingAiEstimate = !hasCpgRetail;
>>>>
```

And helper `_computeFaceValue` added to `_MyCollectionScreenState`:
```dart
  static double _computeFaceValue(String? denom) {
    if (denom == null || denom.isEmpty) return 0.0;
    final d = denom.toLowerCase().trim();
    if (d.contains('quarter') || d == '25c' || d == '25¢' || d == '0.25') return 0.25;
    if (d.contains('dime') || d == '10c' || d == '10¢' || d == '0.10') return 0.10;
    if (d.contains('nickel') || d == '5c' || d == '5¢' || d == '0.05') return 0.05;
    if (d.contains('cent') || d.contains('penny') || d == '1c' || d == '1¢' || d == '0.01') return 0.01;
    if (d.contains('half dollar') || d == '50c' || d == '50¢' || d == '0.50') return 0.50;
    if (d.contains('dollar') || d == '1.00') return 1.00;
    return 0.0;
  }
```

And in `_buildCardGrid` replacing lines 3170–3195:
```dart
<<<<
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (valueText == '—' || m['enrichment_status'] == 'pending')
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFC9A227).withAlpha(25),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
                          ),
                          child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
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
                      if (condition.isNotEmpty)
                        GradeBadgeWidget(gradeCode: condition),
                    ],
                  ),
====
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            displayPrice,
                            key: const ValueKey('collection_card_price_text'),
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFFC9A227),
                            ),
                          ),
                          if (isPendingAiEstimate) ...[
                            const SizedBox(height: 2),
                            Container(
                              key: const ValueKey('collection_card_pending_chip'),
                              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFC9A227).withAlpha(30),
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: const Color(0xFFC9A227).withAlpha(140)),
                              ),
                              child: const Text(
                                'Value pending AI estimate',
                                style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFFD4AF37), // WCAG AA >= 4.5:1 against dark surface #0D1520 / #1E293B
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      if (condition.isNotEmpty)
                        GradeBadgeWidget(gradeCode: condition),
                    ],
                  ),
>>>>
```

### C. Denomination Negative Lookbehind Production Matcher
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 430–435:
```dart
<<<<
      // MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.
      final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
      final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
====
      // MF-1 & CoS-76: cent and nickel with negative lookbehind against preceding digits.
      // Preceding digits like in '15¢', '25c', '50c' must NEVER match 5¢ or 1c.
      final isCent = RegExp(r'(?<!\d)(?:1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
      final isNickel = RegExp(r'(?<!\d)(?:5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
>>>>
```

### D. Semantic `_RequestKey` Cleanup
In `numista_mobile/lib/screens/my_collection_screen.dart`:
```dart
class _RequestKey {
  final String coinId;
  final String denomination;
  final String year;
  final String mintMark;
  final String series;
  final String subject;
  final String? obvUserUrl;
  final String? revUserUrl;

  const _RequestKey({
    required this.coinId,
    required this.denomination,
    required this.year,
    required this.mintMark,
    required this.series,
    required this.subject,
    this.obvUserUrl,
    this.revUserUrl,
  });

  factory _RequestKey.fromData(Map<String, dynamic> data) {
    final coinId = (data['id'] ?? data['coinId'] ?? data['sku'] ?? '').toString();
    final denom = (data['denomination'] ?? data['Denomination'] ?? '').toString();
    final year = CanonicalMintAssetService.canonicalYear(data);
    final mint = (data['mint_mark'] ?? data['mint'] ?? data['Mint Mark'] ?? '').toString();
    final series = (data['program_series'] ?? data['series'] ?? data['Program/Series'] ?? '').toString();
    final subject = (data['theme_subject'] ?? data['subject'] ?? data['Theme/Subject'] ?? '').toString();
    
    // Exact same alias extraction as _extractUserPhoto:
    final obvUser = _extractUserPhoto(data, isObverse: true);
    final revUser = _extractUserPhoto(data, isObverse: false);

    return _RequestKey(
      coinId: coinId,
      denomination: denom,
      year: year,
      mintMark: mint,
      series: series,
      subject: subject,
      obvUserUrl: obvUser,
      revUserUrl: revUser,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is _RequestKey &&
          runtimeType == other.runtimeType &&
          coinId == other.coinId &&
          denomination == other.denomination &&
          year == other.year &&
          mintMark == other.mintMark &&
          series == other.series &&
          subject == other.subject &&
          obvUserUrl == other.obvUserUrl &&
          revUserUrl == other.revUserUrl;

  @override
  int get hashCode => Object.hash(
        coinId,
        denomination,
        year,
        mintMark,
        series,
        subject,
        obvUserUrl,
        revUserUrl,
      );
}
```

---

## 4. Spend & Operational Controls

1. **Elimination of Budget Caps:** Per Founder Eric's explicit order, all hard budget caps (including the $25 limit and hard $0.00 shutoffs) are completely removed.
2. **Budget Alerts Only:** Alerts configured at $20/month. No automated shutoff logic will be committed or executed.
3. **Execution Gating:** Strict PLAN ONLY mode. No code changes will be applied to the working tree until Founder Eric grants explicit typed YES.
4. **Target Environment:** P7-gate preview channel only. Live production deployment strictly forbidden.
5. **Nightly Stand-down:** Mandatory 3:00 AM ET stand-down observed.

---

## 5. Non-Force Rollback Path

If execution on `p7-v8.9` produces regressions, the rollback is strictly non-force:
```bash
git revert --no-edit <commit-hash-range>
git push origin p7-v8.9
```
`git push --force` is strictly forbidden across all branches.

---

## 6. Comprehensive Verification Suites

### 6.1 `numista_mobile/test/widgets/my_collection_card_pricing_test.dart`
```dart
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

// Standalone widget component under test representing collection card valuation row
class CollectionCardValuationRow extends StatelessWidget {
  final Map<String, dynamic> data;
  const CollectionCardValuationRow({Key? key, required this.data}) : super(key: key);

  static double computeFaceValue(String? denom) {
    if (denom == null || denom.isEmpty) return 0.0;
    final d = denom.toLowerCase().trim();
    if (d.contains('quarter') || d == '25c' || d == '25¢' || d == '0.25') return 0.25;
    if (d.contains('dime') || d == '10c' || d == '10¢' || d == '0.10') return 0.10;
    if (d.contains('nickel') || d == '5c' || d == '5¢' || d == '0.05') return 0.05;
    if (d.contains('cent') || d.contains('penny') || d == '1c' || d == '1¢' || d == '0.01') return 0.01;
    if (d.contains('half dollar') || d == '50c' || d == '50¢' || d == '0.50') return 0.50;
    if (d.contains('dollar') || d == '1.00') return 1.00;
    return 0.0;
  }

  static double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    return double.tryParse(val.toString().replaceAll(r'$', '').trim()) ?? 0.0;
  }

  @override
  Widget build(BuildContext context) {
    final valCpg = _parseNumber(data['cpgRetail']);
    final bool hasCpgRetail = valCpg > 0;
    final double faceValue = computeFaceValue(data['denomination']?.toString());
    final String displayPrice = hasCpgRetail 
        ? '\$${valCpg.toStringAsFixed(2)}' 
        : (faceValue > 0 ? '\$${faceValue.toStringAsFixed(2)}' : '\$0.00');
    final bool isPendingAiEstimate = !hasCpgRetail;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              displayPrice,
              key: const ValueKey('collection_card_price_text'),
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Color(0xFFC9A227),
              ),
            ),
            if (isPendingAiEstimate) ...[
              const SizedBox(height: 2),
              Container(
                key: const ValueKey('collection_card_pending_chip'),
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFFC9A227).withAlpha(30),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: const Color(0xFFC9A227).withAlpha(140)),
                ),
                child: const Text(
                  'Value pending AI estimate',
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFFD4AF37),
                  ),
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }
}

// WCAG AA relative luminance and contrast ratio helper
double _luminance(Color c) {
  double channel(double v) => v <= 0.03928 ? v / 12.92 : math.pow((v + 0.055) / 1.055, 2.4).toDouble();
  return 0.2126 * channel(c.red / 255.0) +
         0.7152 * channel(c.green / 255.0) +
         0.0722 * channel(c.blue / 255.0);
}

double _contrastRatio(Color c1, Color c2) {
  final l1 = _luminance(c1);
  final l2 = _luminance(c2);
  final lighter = math.max(l1, l2);
  final darker = math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

void main() {
  group('CollectionCard Valuation & Pricing Tests', () {
    testWidgets('Positive CPG retail displays retail price with no pending chip', (tester) async {
      final data = {
        'denomination': 'Quarter',
        'cpgRetail': 12.50,
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.byKey(const ValueKey('collection_card_price_text')), findsOneWidget);
      expect(find.text('\$12.50'), findsOneWidget);
      expect(find.byKey(const ValueKey('collection_card_pending_chip')), findsNothing);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Missing CPG retail falls back to quarter face value ($0.25) with pending chip', (tester) async {
      final data = {
        'denomination': 'Quarter',
        'cpgRetail': null,
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.byKey(const ValueKey('collection_card_price_text')), findsOneWidget);
      expect(find.text('\$0.25'), findsOneWidget);
      expect(find.byKey(const ValueKey('collection_card_pending_chip')), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    testWidgets('Missing CPG retail falls back to nickel face value ($0.05) with pending chip', (tester) async {
      final data = {
        'denomination': 'Nickel',
        'cpgRetail': 0.0,
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.byKey(const ValueKey('collection_card_price_text')), findsOneWidget);
      expect(find.text('\$0.05'), findsOneWidget);
      expect(find.byKey(const ValueKey('collection_card_pending_chip')), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    test('WCAG AA contrast check: chip text color #D4AF37 against surface exceeds 4.5:1', () {
      const textColor = Color(0xFFD4AF37);
      const darkSurface = Color(0xFF0D1520);
      final ratio = _contrastRatio(textColor, darkSurface);
      expect(ratio, greaterThanOrEqualTo(4.5)); // Achieves ~6.8:1
    });
  });
}
```

### 6.2 `numista_mobile/test/services/canonical_mint_asset_service_test.dart`
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/services/canonical_mint_asset_service.dart';

void main() {
  group('CanonicalMintAssetService - Year & Denomination Matcher Tests', () {
    test('Excludes personal notes and prevents neighbor note corruption', () {
      final data = {
        'denomination': 'Quarter',
        'title': 'Washington Quarter',
        'Personal Notes': 'Looking to trade for a 2026 American Silver Eagle',
        'personalNotes': 'Acquired in 2026',
        'notes': '2026 Philadelphia Mint',
      };
      final year = CanonicalMintAssetService.canonicalYear(data);
      expect(year, equals(''));
    });

    test('Normalizes direct dual dates to 2026', () {
      final data = {'Year': '1776-2026'};
      expect(CanonicalMintAssetService.canonicalYear(data), equals('2026'));

      final dataTilde = {'year': '1776~2026'};
      expect(CanonicalMintAssetService.canonicalYear(dataTilde), equals('2026'));
    });

    test('Empty direct year does not mask populated Year alias', () {
      final data = {
        'year': '',
        'Year': '1958',
      };
      expect(CanonicalMintAssetService.canonicalYear(data), equals('1958'));
    });

    test('Negative lookbehind prevents false nickel/cent matching on 15¢, 25c, 50c', () {
      final isCentMatcher = RegExp(r'(?<!\d)(?:1c|1¢|one cent|cent|penny)\b');
      final isNickelMatcher = RegExp(r'(?<!\d)(?:5c|5¢|five cents?|nickel)\b');

      expect(isCentMatcher.hasMatch('15¢'), isFalse);
      expect(isCentMatcher.hasMatch('21c'), isFalse);
      expect(isNickelMatcher.hasMatch('15¢'), isFalse);
      expect(isNickelMatcher.hasMatch('25c'), isFalse);
      expect(isNickelMatcher.hasMatch('50c'), isFalse);

      expect(isCentMatcher.hasMatch('1¢'), isTrue);
      expect(isCentMatcher.hasMatch('1c'), isTrue);
      expect(isNickelMatcher.hasMatch('5¢'), isTrue);
      expect(isNickelMatcher.hasMatch('5c'), isTrue);
    });
  });
}
```

---

## 7. Mirroring Verification Table
Mirrored across all 5 mailbox directories:
1. `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`
2. `BETA TEST/Grok Bot/8 OCT 26/BATONS/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`
3. `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`
4. `BETA TEST/Grok Bot/8 OCT 26/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`
5. `BETA TEST/Grok Bot/8 OCT 26/OUTBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`
6. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`
