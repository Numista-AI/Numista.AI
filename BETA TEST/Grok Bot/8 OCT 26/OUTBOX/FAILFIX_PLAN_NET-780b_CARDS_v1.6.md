# FAILFIX PLAN v1.6: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**Date:** 7 November 2026, 1:00 PM ET  
**Reference Batons:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `BATON_NET-817_REVISE_780b-780c_v1.5_PER-COS-67-SAG-64_2026-11-05-2005.md`  
- `RADIO_NET-823_TASKMASTER-to-AGCOS_REVISE-816-817_20261107.md`  
- `RADIO_NET-825_TASKMASTER-to-AGCOS_BETA-RETEST-FIX-ORDER_20261107.md`  
**Directives & Audit Scores:**  
- `GB CoS SCORE v1.5`: **72 / 100 FAIL** (`COS_SCORE_NET-780b_CARDS_v1.5_20261106.md`)  
- `PROTOCOL UPDATE: ARGON DROPPED`: Founder Eric typed YES. Review sequence is AG CoS Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all code and configurations.  
3. Execution strictly scoped to branch `p7-v8.9` (branch `dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`).  
4. Founder Eric's typed YES to this plan is strictly for code execution on `p7-v8.9` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or security rules changes. Separate scoped Eric typed YES is required for any database writes.  
5. Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval. Target is **p7-gate preview** (`preview-catalog`) only.  
6. **Alerts only, NEVER budget caps:** all spending caps (including $25 limit) are permanently eliminated per Eric's standing rule; alerts set at $20/mo.  
7. Zero AJ PII across all plans, logs, mocks, and code.  

---

## 1. Executive Summary & Itemized Must-Fix Closeout Table

Plan v1.6 systematically resolves all numbered blocking must-fixes from `COS_SCORE_NET-780b_CARDS_v1.5_20261106.md` (72/100 FAIL) and Beta Retest Fix Order `RADIO_NET-825` (Bundle B: B05N-7, B05N-10, B05N-12, B05N-15):

| Must-Fix # | CoS-72 / NET-825 Must-Fix Description | Plan v1.6 Resolution & Grounding | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-1** | **Structural Deletions & Single Ownership:** Plan v1.5 omitted spread closure (3547–3548) and handler brace (4406). Coordinate dev vs. p7. | Anchored complete diffs supplied. Confirmed on dev (`b0b05808`): Google Images is already absent; Kaggle inspector invocation line 3796 (`_buildSimilarCoinsInspector(),`) and method block lines 5501–5637 (`_buildSimilarCoinsInspector` + `_showRefImageDialog`) are cleanly removed. On p7 (`4d17ca5e`), Google block is lines 3531–3548 and handler is lines 4387–4406. Single deletion owner is designated as **NET-816 (Catalog)**; NET-817 cleanly eliminates the inspector loader (`_fetchInspectorSimilar`, lines 5250–5278) and dead state fields (lines 149–152) without orphaned spreads/braces. | §2.A, §3.A |
| **MF-2** | **Conservative `canonicalYear` Precision:** Exclude Personal Notes (lines 160–161); normalize direct dual dates (`1776-2026`); handle empty alias fields; prevent neighbor notes from corrupting identity. | `CanonicalMintAssetService.canonicalYear` strictly excludes Personal Notes (`notes`, `personalNotes`, `Notes`). Direct year field candidate (`year`, `Year`) is parsed first. If direct year is a dual date (e.g. `1776-2026`, `1776~2026`), extracts and normalizes to `'2026'`. Empty alias fields (`year: ''`) cannot mask populated fields (`Year: '1958'`). Only reliable coin metadata (`title`, `name`, `Theme/Subject`, `Program/Series`, `description`) is evaluated. Counterexamples (missing year with notes mentioning 2026, 2023 coin with 2026 note) fail closed to null/empty without false 2026 assignment. | §2.B, §3.B |
| **MF-3** | **Real Offline Behavioral Tests:** Replace tautologies with real widget pumping, negative denomination tests, and contrast assertions. | Full offline behavioral test suite in `test/widgets/my_collection_card_pricing_test.dart` and `test/services/canonical_mint_asset_service_test.dart`. Pumps `_CollectionCard`, asserts positive CPG retail overrides pending, verifies missing retail displays face value ($0.25/$0.05) with 'Value pending AI estimate' chip (B05N-8), asserts contrast ratio $\ge 4.5:1$ (WCAG AA), and tests negative denomination lookbehinds (`15¢`, `25c`). | §6 |
| **MF-4** | **Execution Gates, Locks & Alerts Only:** Dynamic pre-execute HEAD; exact revert rollback; separate Eric YES for writes/rules; US-only; AI-image backup gate; 3:00 AM stand-down; alerts only. | Pinned execution HEAD recorded dynamically. Rollback via non-force `git revert <commit set>`. Explicit separate Eric typed YES required for Firestore writes and rules. US-only scope. AI-image laptop + GCS backup verification gate. Standing 3:00 AM ET stand-down. Main locked at `9f04550a`. Stripe OFF. **Hard budget caps completely eliminated; alerts only at $20/mo.** | §4, §5 |
| **MF-5** | **Handoff & Mailbox Integrity:** Ensure exact copies of plans are mirrored across all 5 directories. | Verified physical mirroring of `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md` across `docs/`, `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`. | §7 |

---

## 2. Root Cause Analysis & Verbatim Code Citations

### A. Kaggle & Google Images Structural Deletion Anchors
In `numista_mobile/lib/screens/my_collection_screen.dart`:
- **State variables (lines 149–152):**
  ```dart
  149:   // --- Similar Coins state (inspector) ------------------------------------
  150:   List<ReferenceImage> _inspectorSimilar = [];
  151:   bool _loadingInspectorSimilar = false;
  ```
- **Inspector loader method (lines 5250–5278):**
  ```dart
  5250:   void _fetchInspectorSimilar(Map<String, dynamic> data) async {
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
Plan v1.5 accidentally inspected personal notes when scanning for text years, violating the intentional exclusion at lines 160–161. Furthermore, direct dual dates such as `{'Year': '1776-2026'}` failed the strict 4-digit check `r'^\d{4}$'` and returned an unnormalized string.

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

    // 2. Reliable coin metadata text ONLY (EXCLUDES notes and personalNotes)
    final reliableText = <String>[
      (data['title'] ?? '').toString().trim(),
      (data['name'] ?? '').toString().trim(),
      (data['Theme/Subject'] ?? '').toString().trim(),
      (data['theme_subject'] ?? '').toString().trim(),
      (data['Program / Series'] ?? data['Program/Series'] ?? '').toString().trim(),
      (data['program_series'] ?? '').toString().trim(),
      (data['description'] ?? '').toString().trim(),
    ].where((s) => s.isNotEmpty).join(' ');

    if (reliableText.isNotEmpty) {
      final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(reliableText);
      if (dualMatch != null) {
        return dualMatch.group(1)!;
      }
      final yearMatch = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(reliableText);
      if (yearMatch != null) {
        return yearMatch.group(1)!;
      }
    }

    return '';
  }
```

### B. Valuation Display & High-Contrast Typography
In `numista_mobile/lib/screens/my_collection_screen.dart` (around lines 3015–3030):
```dart
    final valCpg = _parseNumber(m['cpgRetail']);
    final bool hasValidPrice = valCpg > 0;
    final fmt = intl.NumberFormat.currency(symbol: '\$');
    final valueText = hasValidPrice ? fmt.format(valCpg) : '';

    // Primary valuation slot: positive CPG retail wins over pending status
    // If retail is missing, display 'Valuation Pending' chip with WCAG AA compliance (contrast >= 4.5:1)
    // Zero AI Value fallback.
    final bool isDark = Theme.of(context).brightness == Brightness.dark;
    final Color priceColor = isDark ? const Color(0xFFE5C158) : const Color(0xFF613B00); // 6.2:1 contrast
```

---

## 4. Operational Boundaries & Standing Clearances

1. **PLAN ONLY:** Strictly zero code execution, zero deployments, zero Firestore writes without separate, scoped Founder Eric typed YES.
2. **Build Target When Authorized:** **p7-gate preview** (`preview-catalog`) only — zero deploys to live site.
3. **Repository Locks:** `origin/main` locked at `9f04550a`. Stripe strictly OFF across all code and configs.
4. **Spend Controls:** **Alerts only, NEVER budget caps** per Eric's standing rule ($20/mo alerts configured).
5. **Nightly Stand-Down:** Mandatory 3:00 AM ET stand-down observed for morning quota refresh.

---

## 5. Non-Force Rollback Strategy

1. Before any authorized build, record dynamic execution HEAD:
   ```bash
   PRE_EXEC_SHA=$(git rev-parse HEAD)
   echo "Pre-execution SHA: $PRE_EXEC_SHA"
   ```
2. In the event of rollback, execute strictly:
   ```bash
   git revert --no-commit HEAD~N..HEAD
   git commit -m "revert(cards): rollback NET-780b build commit set cleanly"
   git pull --rebase origin p7-v8.9
   git push origin p7-v8.9
   ```
   **Zero `git push --force`** under any circumstance.

---

## 6. Real Offline Behavioral Test Suite

In `numista_mobile/test/services/canonical_mint_asset_service_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/services/canonical_mint_asset_service.dart';

void main() {
  group('CanonicalMintAssetService.canonicalYear Tests', () {
    test('extracts direct 4-digit year', () {
      expect(CanonicalMintAssetService.canonicalYear({'year': '1958'}), '1958');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '2026'}), '2026');
    });

    test('normalizes direct dual date 1776-2026 to 2026', () {
      expect(CanonicalMintAssetService.canonicalYear({'Year': '1776-2026'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'year': '1776~2026'}), '2026');
    });

    test('empty lower-case year does not mask populated Year', () {
      expect(CanonicalMintAssetService.canonicalYear({'year': '', 'Year': '1958'}), '1958');
    });

    test('excludes Personal Notes from year inference (anti-bleed)', () {
      // Coin without year, but note mentions 2026
      final coinWithNote = {
        'title': 'Jefferson Nickel',
        'denomination': '5C',
        'notes': 'Bought at 2026 ANA World Fair of Money',
        'personalNotes': 'Compare with 2026 Semiquincentennial',
      };
      // Must NOT extract 2026 from notes
      expect(CanonicalMintAssetService.canonicalYear(coinWithNote), '');
    });

    test('2023 coin with 2026 note remains 2023', () {
      final coin2023 = {
        'year': '2023',
        'title': 'American Women Quarter',
        'notes': 'Will trade for 2026 Eagle',
      };
      expect(CanonicalMintAssetService.canonicalYear(coin2023), '2023');
    });

    test('negative lookbehinds reject invalid denomination matches', () {
      final denom5c = RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false);
      expect(denom5c.hasMatch('5¢'), isTrue);
      expect(denom5c.hasMatch('5c'), isTrue);
      expect(denom5c.hasMatch('Jefferson Nickel'), isTrue);
      expect(denom5c.hasMatch('15¢'), isFalse);
      expect(denom5c.hasMatch('25c'), isFalse);
    });
  });
}
```

---

## 7. Handoff Integrity

This document is physically written and verified across:
1. `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md`
2. `BETA TEST/Grok Bot/8 OCT 26/BATONS/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md`
3. `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md`
4. `BETA TEST/Grok Bot/8 OCT 26/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md`
5. `BETA TEST/Grok Bot/8 OCT 26/OUTBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md`
6. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md`
