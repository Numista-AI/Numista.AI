# PLAN NET-810: U.S. Mint Product Fields in Coin Detail View (v1)

**Document Version:** 1.0  
**Date:** 2026-11-06 23:55 ET  
**Author:** Antigravity Chief of Staff v4 / Catalog Night Team  
**Status:** PLAN ONLY — NO CODE / NO EXECUTION / NO DEPLOY / NO MERGE  
**Target Branch:** `origin/p7-v8.9`  
**Standing Locks:** `origin/main` locked at `9f04550a` | Stripe strictly OFF | Zero Firestore writes | Zero PII | Review cycle has NO Argon

---

## 1. Executive Summary & Context

Founder Eric requested at 4:01 PM ET (5 Nov 2026) the addition of U.S. Mint product fields in the coin detail view to cleanly surface official Mint pricing, product schedule status, and release timing without conflating numismatic market valuations or cluttering browse/card surfaces.

This plan details the end-to-end specification for ingesting, storing, and rendering four optional U.S. Mint product fields derived from `SCHEMA_DIFF_product_price_mint_schedule_20261105.json` and `Plan.v1_catalog_Mint_product_fields_excerpt.md`.

### The Four Optional Mint Fields
1. `product_price_usd` (`double?` / `number | null`): Official U.S. Mint catalog issue price in USD.
2. `mint_schedule_status` (`String?` / `string | null`): Official Mint product schedule status (`NOT_AVAILABLE`, `COMING_SOON`, `ON_SALE`, `SOLD_OUT`, `UNKNOWN`).
3. `product_availability` (`String?` / `string | null`): Alias-friendly availability flag.
4. `release_time_et` (`String?` / `string | null`): Release time-of-day in Eastern Time (e.g., `"noon"`).

---

## 2. Strict UX & Display Rules

Every implementation requirement below is strictly mandatory:

| Rule # | Requirement | Implementation Specification |
| :--- | :--- | :--- |
| **R1** | **Detail View Only** | Fields MUST only render within the Detail View (`_DetailsTab` in `coin_detail_screen.dart` and the Overview tab of `UnifiedCoinDetailsModal`). **Strictly forbidden on collection cards, browse cards, search cards, and table rows.** |
| **R2** | **Exact Issue Price Label** | Issue price MUST be labeled exactly: **`"U.S. Mint issue price"`**. Under no circumstances may it be labeled `"value"`, `"market value"`, `"price"`, or `"retail price"`. |
| **R3** | **Zero Buy Links / Urgency** | Zero outbound buy buttons, zero external affiliate links, zero store links, and zero urgency copy (e.g., no `"Buy Now"`, `"Hurry"`, `"Limited Quantity"`, `"Don't Miss Out"`). |
| **R4** | **Fail-Closed Null / UNKNOWN Suppression** | If a field is `null`, empty string, `<= 0` (for price), or `"UNKNOWN"`, it MUST be completely omitted/hidden. No placeholder strings (no `"N/A"`, `"TBD"`, or `"None"`). |
| **R5** | **Status Field Precedence** | When both `mint_schedule_status` and `product_availability` are populated, `mint_schedule_status` MUST take precedence. `product_availability` is evaluated solely as a fallback if `mint_schedule_status` is missing or empty. |
| **R6** | **Neutral Styling** | Status text MUST be rendered in neutral, muted gray typography (`_kSubtext(context)` / `#9E9E9E`). No alarming badges, flashing tags, or high-urgency green/red chips. |
| **R7** | **Paired Release Time** | `release_time_et` MUST ONLY be displayed when `release_date` is also present and non-empty. Format: `"${releaseDate}, ${releaseTimeEt} ET"` (e.g., `"Nov 12, 2026, noon ET"`). If `release_date` is absent, `release_time_et` MUST be suppressed. |
| **R8** | **Publish Allow-List Gate** | These 4 fields are dropped by default during export/publishing. They may only be included in the public catalog publish allow-list after completing the full Review Cycle and receiving Founder Eric's typed YES. |

---

## 3. Data Model & Serialization Specification

### 3.1 `CoinModel` Field Extensions (`numista_mobile/lib/models/coin_model.dart`)

```dart
// numista_mobile/lib/models/coin_model.dart

class CoinModel {
  // Existing fields...
  final String id;
  final String year;
  final String mintMark;
  final String denomination;
  // ...
  
  // ── U.S. Mint Product Fields (NET-810) ──────────────────────────────────
  final double? productPriceUsd;       // U.S. Mint catalog issue price in USD
  final String? mintScheduleStatus;    // NOT_AVAILABLE, COMING_SOON, ON_SALE, SOLD_OUT, UNKNOWN
  final String? productAvailability;   // Fallback availability status
  final String? releaseDate;           // Release date string (e.g. "Nov 12, 2026")
  final String? releaseTimeEt;         // Release time-of-day in ET (e.g. "noon")

  const CoinModel({
    required this.id,
    this.year = '',
    this.mintMark = '',
    this.denomination = '',
    // ...
    this.productPriceUsd,
    this.mintScheduleStatus,
    this.productAvailability,
    this.releaseDate,
    this.releaseTimeEt,
  });

  factory CoinModel.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>? ?? {};
    return CoinModel.fromMap(data, id: doc.id);
  }

  factory CoinModel.fromMap(Map<String, dynamic> data, {required String id}) {
    // Helper to safely parse nullable double
    double? parseNullableDouble(dynamic v) {
      if (v == null) return null;
      if (v is num) return v.toDouble();
      if (v is String) return double.tryParse(v.replaceAll(RegExp(r'[^\d.]'), ''));
      return null;
    }

    return CoinModel(
      id: id,
      year: data['year']?.toString() ?? '',
      mintMark: data['mint_mark']?.toString() ?? '',
      denomination: data['denomination']?.toString() ?? '',
      // ... existing fields ...
      
      // NET-810 Fields
      productPriceUsd: parseNullableDouble(data['product_price_usd']),
      mintScheduleStatus: data['mint_schedule_status']?.toString().trim(),
      productAvailability: data['product_availability']?.toString().trim(),
      releaseDate: data['release_date']?.toString().trim(),
      releaseTimeEt: data['release_time_et']?.toString().trim(),
    );
  }

  Map<String, dynamic> toFirestore({bool includeMintProductFields = false}) {
    final map = <String, dynamic>{
      // ... existing serialized fields ...
    };

    // Publish Allow-List Gate: only serialize when explicitly allow-listed
    if (includeMintProductFields) {
      if (productPriceUsd != null && productPriceUsd! > 0) {
        map['product_price_usd'] = productPriceUsd;
      }
      if (mintScheduleStatus != null && 
          mintScheduleStatus!.isNotEmpty && 
          mintScheduleStatus != 'UNKNOWN') {
        map['mint_schedule_status'] = mintScheduleStatus;
      }
      if (productAvailability != null && 
          productAvailability!.isNotEmpty && 
          productAvailability != 'UNKNOWN') {
        map['product_availability'] = productAvailability;
      }
      if (releaseDate != null && releaseDate!.isNotEmpty) {
        map['release_date'] = releaseDate;
      }
      if (releaseTimeEt != null && releaseTimeEt!.isNotEmpty) {
        map['release_time_et'] = releaseTimeEt;
      }
    }

    return map;
  }
}
```

---

## 4. UI / Widget Implementation Specification

### 4.1 Resolution Helper Function

```dart
/// Helper that applies display rules R2, R4, R5, R6, R7 for Mint product metadata.
class MintProductHelper {
  /// Resolves the effective status string, preferring mint_schedule_status.
  static String? resolveEffectiveStatus(CoinModel coin) {
    final mStatus = coin.mintScheduleStatus?.trim();
    if (mStatus != null && mStatus.isNotEmpty && mStatus.toUpperCase() != 'UNKNOWN') {
      return _formatStatusLabel(mStatus);
    }
    final pAvail = coin.productAvailability?.trim();
    if (pAvail != null && pAvail.isNotEmpty && pAvail.toUpperCase() != 'UNKNOWN') {
      return _formatStatusLabel(pAvail);
    }
    return null;
  }

  static String _formatStatusLabel(String raw) {
    switch (raw.toUpperCase()) {
      case 'ON_SALE': return 'On Sale';
      case 'COMING_SOON': return 'Coming Soon';
      case 'NOT_AVAILABLE': return 'Not Available';
      case 'SOLD_OUT': return 'Sold Out';
      default: return raw.replaceAll('_', ' ');
    }
  }

  /// Formats release schedule: requires both release_date and release_time_et to show time.
  static String? formatReleaseSchedule(CoinModel coin) {
    final date = coin.releaseDate?.trim();
    final time = coin.releaseTimeEt?.trim();
    if (date == null || date.isEmpty) return null;
    if (time != null && time.isNotEmpty) {
      return '$date, $time ET';
    }
    return date;
  }

  /// Formats official issue price with exact label.
  static (String label, String value)? formatIssuePrice(CoinModel coin) {
    final price = coin.productPriceUsd;
    if (price == null || price <= 0) return null;
    final formatted = price % 1 == 0 
        ? '\$${price.toInt()}' 
        : '\$${price.toStringAsFixed(2)}';
    return ('U.S. Mint issue price', formatted);
  }
}
```

### 4.2 Integration in `_DetailsTab` (`numista_mobile/lib/screens/coin_detail_screen.dart`)

```dart
// Inside _DetailsTab.build(BuildContext context) in coin_detail_screen.dart:1526

final fields = <(String, String)>[
  ('Year', coin.year.replaceAll(RegExp(r'\.0$'), '')),
  ('Mint Mark', coin.mintMark),
  ('Denomination', _fmtDenomination(coin.denomination)),
  ('Program / Series', coin.programSeries.isEmpty ? (coin.country.isNotEmpty && coin.country != 'United States' ? 'Standard Circulation' : '') : coin.programSeries),
  ('Theme / Subject', coin.themeSubject),
  ('Variety / Error', coin.variety),
  ('Condition', coin.condition),
  ('Strike Type', coin.strikeType),
  ('Holder Type', coin.holderType),
  ('Grading Service', coin.gradingService),
  ('Metal Content', coin.metalContent),
  ('Country', coin.country),
  ('Storage Location', coin.storageLocation),
  ('Quantity', coin.quantity.isNotEmpty ? coin.quantity : '1'),

  // ── NET-810: U.S. Mint Product Fields (Detail View Only) ────────────────
  if (MintProductHelper.formatIssuePrice(coin) != null)
    MintProductHelper.formatIssuePrice(coin)!,
  if (MintProductHelper.resolveEffectiveStatus(coin) != null)
    ('Mint Schedule Status', MintProductHelper.resolveEffectiveStatus(coin)!),
  if (MintProductHelper.formatReleaseSchedule(coin) != null)
    ('U.S. Mint Release', MintProductHelper.formatReleaseSchedule(coin)!),

  ('Notes', coin.personalNotes),
].where((f) => f.$2.trim().isNotEmpty &&
    f.$2 != 'null' && f.$2 != 'N/A' && f.$2 != 'Ungraded').toList();
```

---

## 5. Automated Verification & Test Suite

The test file `numista_tests/mint_product_fields_test.dart` will execute in the verification phase upon build authorization:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/models/coin_model.dart';
import 'package:numista_mobile/screens/coin_detail_screen.dart';

void main() {
  group('NET-810 Mint Product Fields Validation', () {
    test('Issue price uses exact label and never "value"', () {
      final coin = CoinModel(id: 'c1', productPriceUsd: 375.0);
      final priceItem = MintProductHelper.formatIssuePrice(coin);
      expect(priceItem, isNotNull);
      expect(priceItem!.$1, equals('U.S. Mint issue price'));
      expect(priceItem.$2, equals('\$375'));
      expect(priceItem.$1.toLowerCase().contains('value'), isFalse);
      expect(priceItem.$1.toLowerCase().contains('market'), isFalse);
    });

    test('Null, zero, or UNKNOWN fields are suppressed', () {
      final coin = CoinModel(
        id: 'c2',
        productPriceUsd: 0.0,
        mintScheduleStatus: 'UNKNOWN',
        productAvailability: 'UNKNOWN',
      );
      expect(MintProductHelper.formatIssuePrice(coin), isNull);
      expect(MintProductHelper.resolveEffectiveStatus(coin), isNull);
    });

    test('Prefers mint_schedule_status over product_availability', () {
      final coin = CoinModel(
        id: 'c3',
        mintScheduleStatus: 'ON_SALE',
        productAvailability: 'NOT_AVAILABLE',
      );
      expect(MintProductHelper.resolveEffectiveStatus(coin), equals('On Sale'));
    });

    test('Release time suppressed when release date is absent', () {
      final coin = CoinModel(id: 'c4', releaseTimeEt: 'noon');
      expect(MintProductHelper.formatReleaseSchedule(coin), isNull);
    });

    test('Release time rendered with date when both present', () {
      final coin = CoinModel(
        id: 'c5',
        releaseDate: 'Nov 12, 2026',
        releaseTimeEt: 'noon',
      );
      expect(
        MintProductHelper.formatReleaseSchedule(coin),
        equals('Nov 12, 2026, noon ET'),
      );
    });
  });
}
```

---

## 6. Review Cycle & Operational Governance

1. **Review Sequence (Argon Strictly Dropped):**
   - Step 1: AG CoS delivers plan `PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.md`.
   - Step 2: Grok Bot CoS independent review and scoring ($\ge 95 / 100$).
   - Step 3: Stand Alone Grok (SAG, grok-4.7) independent review and scoring ($\ge 95 / 100$).
   - Step 4: Founder Eric review and typed YES.
   - Step 5: Separate execution baton issued. Zero build or code changes authorized until Step 4 is complete.

2. **Standing Operational Locks:**
   - `origin/main` locked at `9f04550a`.
   - Stripe strictly OFF across all configurations.
   - Zero Firestore writes/seeding.
   - Zero pings to Eric overnight.
   - 3:00 AM ET AG stand-down strictly observed.
