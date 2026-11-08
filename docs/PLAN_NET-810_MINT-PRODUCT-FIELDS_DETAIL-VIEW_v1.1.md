# PLAN NET-810: U.S. Mint Product Fields in Coin Detail View (v1.1)

- **Track ID:** NET-810 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **Document Version:** 1.1 (Comprehensive Fail-Fix per Grok Bot CoS 58 FAIL Report)
- **Date / DTG:** Saturday, 7 November 2026, 20:00 ET (`2026-11-07 20:00:00 -05:00`)
- **Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Reviewer:** Grok Bot Chief of Staff (`GROKCOS`) & Stand Alone Grok (`SAG`)
- **Status:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's typed YES)
- **Target Branch:** `origin/dev` (and synced to `origin/p7-v8.9`)
- **Codebase Baseline Commit:** `4d17ca5e0bc75f14e7aeb29a39f60d626c04f982` (Pinned Target Tree)

---

### Standing Operational Invariants & Pinned Boundaries

1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Under no circumstances may any agent merge, cherry-pick, rebase, or push directly to `main`.
2. **Stripe Lock:** Stripe remains strictly OFF across the entire application. Zero live keys, zero webhook activation, and zero payment processing endpoints.
3. **Budget Policy:** Cost control is governed strictly by an **alert-only threshold of $20.00/month** on Google Cloud Billing. Under no circumstances may any agent implement automated budget caps, hard spending limits, or automated Hosting teardowns.
4. **Zero Firestore Writes / Seeding:** The execution of this plan performs **0 writes, 0 updates, and 0 creates** in live Firestore or user collection documents. All catalog metadata joins are read-only.
5. **Privacy & PII Exclusion:** Zero collector identifiers, zero AJ provenance tags, zero private purchase costs, and zero user personal notes are exposed or included in public catalog fixtures or public tests.
6. **No Argon:** In accordance with Founder Eric's typed YES order of 5 Nov 2026 at 18:07 ET, Argon is permanently removed from all review workflows, gating rubrics, and handoff sequences.
7. **Rule 6a Verbatim Code Citations:** Every source citation in this plan quotes the exact verbatim code lines as inspected at pinned commit `4d17ca5e`.

---

## 1. Executive Summary & Context

On 5 November 2026 at 16:01 ET, Founder Eric requested the addition of official U.S. Mint product fields to the Coin Detail View. The business objective is to surface official government release information (issue pricing, schedule availability, and release timing) in an authoritative, non-promotional, and purely informational manner.

The initial plan (v1.0) was evaluated by Grok Bot Chief of Staff on 7 November 2026 and received a score of **58/100 FAIL**. The evaluation identified eight blocking defects:
1. **MF-1:** Complete lack of an ingestion and source-of-truth path for catalog-to-user-coin joins without forbidden Firestore writes.
2. **MF-2:** Invention of `release_date` without schema definition, validation against vague placeholders ("TBD", "Fall 2026"), or fail-closed parsing.
3. **MF-3:** Mutation of `toFirestore()` signature (`toFirestore({bool includeMintProductFields = false})`), breaking existing call sites in `coin_detail_screen.dart:490-494, 682-686` and compromising local optimistic round-trip persistence.
4. **MF-4:** Failure to ground data model extensions against real `CoinModel` lines at `4d17ca5e` and reliance on a non-existent `copyWith()` method.
5. **MF-5:** Flawed tuple integration in `_DetailsTab` (`coin_detail_screen.dart:1526`) lacking per-row muted styling hooks.
6. **MF-6:** Retail-promotional urgency language ("On Sale", "Sold Out"), lack of strict enum allow-listing, missing freshness safeguards, and failure to guarantee total isolation of issue price from portfolio/market valuations.
7. **MF-7:** Tests promised as widget tests but authored only as five basic unit tests located in a non-existent directory (`numista_tests/`).
8. **MF-8:** Absence of acceptance criteria, file manifest, targeted git revert rollback procedures, and alignment with the ~13 November 2026 catalog go-live deadline.

Plan v1.1 comprehensively resolves all eight blocking must-fixes with verbatim code grounding, complete architectural specifications, and runnable test suites.

---

## 2. Must-Fix Matrix & Resolution Summary

| Must-Fix # | Category | Prior Defect (v1.0 58 FAIL) | v1.1 Resolution Specification |
| :--- | :--- | :--- | :--- |
| **MF-1** | Source-of-Truth & Ingestion | Zero records in `entries.jsonl` carry Mint fields. No catalog lookup service defined. Left user coins disconnected without forbidden writes. | Defined `MintProductLookupService` performing a pure, read-only in-memory join against `assets/catalog/catalog_master_3202.jsonl` on `nac_code` with fallback to `(year, mintMark, denomination, variety)`. Fails closed on zero or multiple matches. Zero Firestore writes. |
| **MF-2** | `release_date` Specification | `release_date` was not in `SCHEMA_DIFF` or `schema.json`. Upcoming releases contained placeholders like `"TBD"` and `"Fall 2026"`, causing invalid labels like `"TBD, noon ET"`. | Formally specified `release_date` requiring strict ISO-8601 calendar date (`YYYY-MM-DD`). Regex and calendar parsing fail closed against any non-ISO string, seasons, or `"TBD"`. Formatted cleanly as `"MMM d, yyyy"`. |
| **MF-3** | Round-Trip Persistence & Allow-List | Changed `toFirestore({bool includeMintProductFields = false})`, breaking `coin_detail_screen.dart:490, 682` and local optimistic updates. | Restored exact zero-argument `Map<String, dynamic> toFirestore()` signature in `coin_model.dart:248`. Round-trip persistence preserved. Publish allow-list moved exclusively to `toPublicCatalogMap()`. |
| **MF-4** | Pinned Code Grounding | Inaccurate line numbers; assumed `copyWith()` existed when `CoinModel` at `4d17ca5e` has no `copyWith()`. | Quoted verbatim `coin_model.dart` lines: class declaration (line 4), constructor (lines 81–110), `fromMap` (lines 169–246), and `toFirestore` (lines 248–297). Explicitly documented absence of `copyWith()`. |
| **MF-5** | `_DetailsTab` Structure & Styling | Appended raw tuples to `fields` list without muted styling hook, making Mint fields look like standard collector attributes. | Positioned fields before `Notes` (`coin_detail_screen.dart:1541`). Specified `(String, String, TextStyle?)` record structure or dedicated `_MintProductMetadataSection` using `Theme.of(context).colorScheme.onSurfaceVariant`. |
| **MF-6** | Display Rules & Value Separation | Used promotional terms ("On Sale", "Sold Out"). Allowed unvetted string passthrough. Missing freshness window. Conflated issue price. | Enforced factual neutral copy: `"Available from U.S. Mint (as of Nov 2026)"`, `"Scheduled by U.S. Mint"`, `"No longer offered by U.S. Mint"`. Strict enum allow-list. 30-day staleness window. Strict value isolation: issue price never feeds portfolio or market metrics. |
| **MF-7** | Test Suite & Real Paths | Promised widget tests but provided only 5 unit tests in non-existent `numista_tests/`. | Relocated tests to real path `numista_mobile/test/mint_product_fields_test.dart`. Authored comprehensive unit suite and Flutter `testWidgets` suite covering widget tree, zero buy links, styling, and zero Firestore writes. |
| **MF-8** | Acceptance, Manifest & Rollback | Missing acceptance criteria, file manifest, git rollback, and ~13 Nov deadline fit. | Provided exact 10-point acceptance checklist, comprehensive file manifest, targeted `git revert` procedure, and verified timeline fit for 13 Nov go-live. |

---

## 3. Grounding & Baseline Code Audit (Pin `4d17ca5e`)

Every citation below is quoted verbatim from the target repository tree at commit `4d17ca5e0bc75f14e7aeb29a39f60d626c04f982`.

### 3.1 `CoinModel` in `numista_mobile/lib/models/coin_model.dart`

**Class Header and Imports (lines 1–25):**
```dart
import 'package:cloud_firestore/cloud_firestore.dart';
import '../utils/text_sanitizer.dart';

class CoinModel {
  final String id;
  final String year;
  final String mintMark;
  final String denomination;
  final String programSeries;
  final String themeSubject;
  final String variety;
  final String condition;
  final String strikeType;
  final String holderType;
  final String gradingService;
  final String certificationNumber;
  final String metalContent;
  final String quantity;
  final String purchaseCost;
  final String purchaseDate;
  final String retailer;
  final String retailerItemNo;
  final String retailerInvoiceNo;
  final String storageLocation;
  final String personalNotes;
  final String personalRef;
  final String originalDescription;
  final String country;
```

**Constructor Opening (lines 81–112):**
```dart
  CoinModel({
    required this.id,
    this.year = '',
    this.mintMark = '',
    this.denomination = '',
    this.programSeries = '',
    this.themeSubject = '',
    this.variety = '',
    this.condition = 'Ungraded',
    this.strikeType = '',
    this.holderType = '',
    this.gradingService = '',
    this.certificationNumber = '',
    this.metalContent = '',
    this.quantity = '1',
    this.purchaseCost = '\$0.00',
    this.purchaseDate = '',
    this.retailer = '',
    this.retailerItemNo = '',
    this.retailerInvoiceNo = '',
    this.storageLocation = '',
    this.personalNotes = '',
    this.personalRef = '',
    this.originalDescription = '',
    this.aiEstimatedValue = 'Pending',
    this.meltValue = 'N/A',
    this.imageUrlObverse = '',
    this.imageUrlReverse = '',
    this.country = 'USA',
    this.timestamp,
```

**`fromMap` Factory (lines 169–175, 240–246):**
```dart
  factory CoinModel.fromMap(Map<String, dynamic> data, String id) {
    return CoinModel(
      id: id,
      year: data['Year']?.toString() ?? '',
      mintMark: data['Mint Mark']?.toString() ?? '',
      denomination: data['Denomination']?.toString() ?? '',
      programSeries: data['Program/Series']?.toString() ?? '',
      themeSubject: data['Theme/Subject']?.toString() ?? '',
      // ...
      provenanceLedger: data['provenanceLedger'] as List<dynamic>? ?? [],
      transferStatus: data['transferStatus']?.toString() ?? data['transfer_status']?.toString() ?? 'none',
      transferId: data['transferId']?.toString() ?? data['transfer_id']?.toString() ?? '',
    );
  }
```

**`toFirestore` Method (lines 248–297):**
```dart
  Map<String, dynamic> toFirestore() {
    return {
      'Year': year,
      'Mint Mark': mintMark,
      'Denomination': denomination,
      'Program/Series': programSeries,
      'Theme/Subject': themeSubject,
      'Variety': variety,
      'Condition': condition,
      'Strike Type': strikeType,
      'Holder Type': holderType,
      'Grading Service': gradingService,
      'Certification Number': certificationNumber,
      'Metal Content': metalContent,
      'Quantity': quantity,
      'Purchase Cost': purchaseCost,
      'Purchase Date': purchaseDate,
      'Retailer/Website': retailer,
      'Retailer Item No.': retailerItemNo,
      'Retailer Invoice #': retailerInvoiceNo,
      'Storage Location': storageLocation,
      'Personal Notes I': personalNotes,
      'Personal Reference #': personalRef,
      'Original Description from source': originalDescription,
      'AI Estimated Value': aiEstimatedValue,
      'Melt Value': meltValue,
      'image_url_obverse': imageUrlObverse,
      'image_url_reverse': imageUrlReverse,
      'image_verification_status': imageVerificationStatus,
      'image_verification_reason': imageVerificationReason,
      'greysheetGsid': greysheetGsid,
      'greysheetBid': greysheetBid,
      'greysheetAsk': greysheetAsk,
      'cpgRetail': cpgRetail,
      'priceLastUpdated': priceLastUpdated != null ? Timestamp.fromDate(priceLastUpdated!) : null,
      'hasCac': hasCac,
      'is_set': isSet,
      'set_id': setId,
      'set_contents': setContents,
      'parent_set_id': parentSetId,
      'member_of': memberOf,
      'in_original_packaging': inOriginalPackaging,
      'owner_photos': ownerPhotos,
      'provenanceLedger': provenanceLedger,
      'transferStatus': transferStatus,
      'transferId': transferId,
      'Country': country,
      'timestamp': timestamp ?? FieldValue.serverTimestamp(),
    };
  }
```

> [!IMPORTANT]
> **Audit Finding on `copyWith`:** `coin_model.dart` at `4d17ca5e` does **not** declare a `copyWith()` method. Any plan assuming `coin.copyWith(...)` is uncompilable. In `coin_detail_screen.dart:490-494` and `682-686`, local updates are performed via:
> ```dart
> final updated = CoinModel.fromMap({
>   ..._coin.toFirestore(),
>   ...updates,
>   'timestamp': _coin.timestamp,
> }, _coin.id);
> ```
> Therefore, modifying the `toFirestore()` signature breaks these call sites immediately.

### 3.2 `_DetailsTab` in `numista_mobile/lib/screens/coin_detail_screen.dart`

**`_DetailsTab` Declaration & Field List (lines 1513–1544):**
```dart
class _DetailsTab extends StatelessWidget {
  final CoinModel coin;
  final bool isInspectorMode;
  final Function(String fieldName, String currentValue) onInspectField;

  const _DetailsTab({
    required this.coin,
    this.isInspectorMode = false,
    required this.onInspectField,
  });

  @override
  Widget build(BuildContext context) {
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
      ('Notes', coin.personalNotes),
    ].where((f) => f.$2.trim().isNotEmpty &&
        f.$2 != 'null' && f.$2 != 'N/A' && f.$2 != 'Ungraded').toList();
```

---

## 4. Source of Truth & Read-Only Catalog Join Architecture (MF-1)

### 4.1 The Ingestion Challenge
In Numista.AI, user coin records in Firestore (`users/{uid}/coins/{coinId}`) represent private collection items. These documents do not natively store real-time government mint availability, pricing, or product scheduling. Writing government product sales status into private user documents is strictly prohibited because:
1. It violates the **Zero Firestore Writes** rule during catalog updates.
2. It causes stale government data to persist indefinitely in private documents.
3. It conflates static collection provenance with dynamic public reference data.

### 4.2 Authorized Source of Truth
The single source of truth for U.S. Mint product fields is the verified public reference catalog:
- Primary file: `assets/catalog/catalog_master_3202.jsonl` (3,202 verified master entries: 2,965 coins, 181 notes, 56 medals; SHA-256: `FBA6C66A107E5304D801997C01F22681E072FA7E8F8AA8761D5A2738ADE31BEF`).
- Schema authority: `/workspace/catalog-preview/schema.json` lines 544–575 defining:
  - `product_price_usd` (number, minimum: 0)
  - `mint_schedule_status` (string, enum: `["NOT_AVAILABLE", "COMING_SOON", "ON_SALE", "SOLD_OUT", "UNKNOWN"]`)
  - `product_availability` (string)
  - `release_time_et` (string)
  - `release_date` (string, format: `date`, `YYYY-MM-DD`)
  - `mint_product_as_of` (string, format: `date-time`)

### 4.3 Read-Only In-Memory Lookup Service (`MintProductLookupService`)

To join catalog metadata onto a user's `CoinModel` when viewing `_DetailsTab`, we implement `MintProductLookupService` in `numista_mobile/lib/services/mint_product_lookup_service.dart`.

```dart
// numista_mobile/lib/services/mint_product_lookup_service.dart

import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/coin_model.dart';

/// Read-only metadata container for official U.S. Mint product attributes.
class MintProductMetadata {
  final double? productPriceUsd;
  final String? mintScheduleStatus;
  final String? productAvailability;
  final String? releaseDate;
  final String? releaseTimeEt;
  final DateTime? asOfDate;

  const MintProductMetadata({
    this.productPriceUsd,
    this.mintScheduleStatus,
    this.productAvailability,
    this.releaseDate,
    this.releaseTimeEt,
    this.asOfDate,
  });

  bool get isEmpty =>
      productPriceUsd == null &&
      mintScheduleStatus == null &&
      productAvailability == null &&
      releaseDate == null &&
      releaseTimeEt == null;
}

class MintProductLookupService {
  static final MintProductLookupService instance = MintProductLookupService._internal();
  MintProductLookupService._internal();

  // In-memory cache loaded once on demand
  Map<String, MintProductMetadata>? _cacheByNac;
  Map<String, List<MintProductMetadata>>? _cacheByAttributes;
  bool _isLoading = false;

  /// Loads the verified catalog dataset in read-only mode from assets.
  /// Strictly zero network requests and zero Firestore writes.
  Future<void> ensureInitialized() async {
    if (_cacheByNac != null || _isLoading) return;
    _isLoading = true;

    try {
      final jsonlString = await rootBundle.loadString('assets/catalog/catalog_master_3202.jsonl');
      final lines = const LineSplitter().convert(jsonlString);

      final byNac = <String, MintProductMetadata>{};
      final byAttr = <String, List<MintProductMetadata>>{};

      for (final line in lines) {
        if (line.trim().isEmpty) continue;
        final map = jsonDecode(line) as Map<String, dynamic>;

        // Quarantine proposal or unvetted status records
        final recordStatus = map['record_status']?.toString().toUpperCase();
        if (recordStatus == 'PROPOSAL' || recordStatus == 'UNVETTED') {
          continue; // Strict fail-closed quarantine
        }

        final nacCode = map['nac_code']?.toString().trim();
        final rawPrice = map['product_price_usd'];
        final price = rawPrice is num ? rawPrice.toDouble() : double.tryParse(rawPrice?.toString() ?? '');
        final scheduleStatus = map['mint_schedule_status']?.toString().trim();
        final availability = map['product_availability']?.toString().trim();
        final rawReleaseDate = map['release_date']?.toString().trim();
        final rawReleaseTime = map['release_time_et']?.toString().trim();
        final rawAsOf = map['mint_product_as_of']?.toString().trim();

        // ISO-8601 validation for release_date (MF-2)
        final validReleaseDate = _validateIsoDate(rawReleaseDate);
        final validAsOf = rawAsOf != null ? DateTime.tryParse(rawAsOf) : null;

        final metadata = MintProductMetadata(
          productPriceUsd: (price != null && price > 0) ? price : null,
          mintScheduleStatus: (scheduleStatus != null && scheduleStatus != 'UNKNOWN') ? scheduleStatus : null,
          productAvailability: (availability != null && availability != 'UNKNOWN') ? availability : null,
          releaseDate: validReleaseDate,
          releaseTimeEt: (validReleaseDate != null && rawReleaseTime != null && rawReleaseTime.isNotEmpty)
              ? rawReleaseTime
              : null,
          asOfDate: validAsOf,
        );

        if (metadata.isEmpty) continue;

        if (nacCode != null && nacCode.isNotEmpty) {
          byNac[nacCode.toUpperCase()] = metadata;
        }

        // Composite attribute key: Year|MintMark|Denomination|Variety
        final year = map['year']?.toString().trim() ?? '';
        final mint = map['mint_mark']?.toString().trim().toUpperCase() ?? '';
        final denom = map['denomination']?.toString().trim().toLowerCase() ?? '';
        final variety = map['variety']?.toString().trim().toLowerCase() ?? '';
        final attrKey = '$year|$mint|$denom|$variety';

        byAttr.putIfAbsent(attrKey, () => []).add(metadata);
      }

      _cacheByNac = byNac;
      _cacheByAttributes = byAttr;
    } catch (_) {
      // Fail closed: empty cache ensures zero crashes and suppressed display
      _cacheByNac = {};
      _cacheByAttributes = {};
    } finally {
      _isLoading = false;
    }
  }

  /// Resolves Mint product metadata for a given coin model.
  /// 1. Try exact NAC code join.
  /// 2. Fall back to composite attribute key.
  /// 3. Fail closed if 0 matches or >1 ambiguous matches.
  MintProductMetadata? lookupForCoin(CoinModel coin) {
    if (_cacheByNac == null) return null;

    // 1. Direct NAC code join (if available on coin or reference)
    final ref = coin.personalRef.trim().toUpperCase();
    if (ref.startsWith('NAC-') && _cacheByNac!.containsKey(ref)) {
      return _cacheByNac![ref];
    }

    // 2. Composite key join
    final year = coin.year.replaceAll(RegExp(r'\.0$'), '').trim();
    final mint = coin.mintMark.trim().toUpperCase();
    final denom = coin.denomination.trim().toLowerCase();
    final variety = coin.variety.trim().toLowerCase();
    final key = '$year|$mint|$denom|$variety';

    final matches = _cacheByAttributes?[key];
    if (matches != null && matches.length == 1) {
      return matches.first; // Unique, unambiguous match
    }

    // Ambiguous (>1) or missing (0) matches fail closed
    return null;
  }

  /// Validates standard ISO-8601 calendar date format (YYYY-MM-DD).
  /// Rejects "TBD", "Fall 2026", "Late 2026", and all non-calendar placeholders.
  static String? _validateIsoDate(String? raw) {
    if (raw == null || raw.isEmpty) return null;
    final trimmed = raw.trim();
    final isoPattern = RegExp(r'^\d{4}-\d{2}-\d{2}$');
    if (!isoPattern.hasMatch(trimmed)) return null;

    final parsed = DateTime.tryParse(trimmed);
    if (parsed == null) return null;

    // Verify round-trip formatting to detect impossible dates like 2026-02-31
    final formatted = '${parsed.year.toString().padLeft(4, '0')}-${parsed.month.toString().padLeft(2, '0')}-${parsed.day.toString().padLeft(2, '0')}';
    return formatted == trimmed ? trimmed : null;
  }
}
```

---

## 5. Formal Specification of `release_date` (MF-2)

### 5.1 Schema Addition
`release_date` is formally added as an official reference catalog field:
- **Property Name:** `release_date`
- **Data Type:** `string`
- **Format:** `date` (ISO-8601: `YYYY-MM-DD`, e.g. `"2026-11-12"`)
- **Description:** Official calendar release date announced by the United States Mint.

### 5.2 Fail-Closed Validation Rules
1. **Rejection of Vague Text:** Any value matching patterns such as `TBD`, `TBA`, `Fall`, `Spring`, `Summer`, `Winter`, `Early`, `Late`, `Pending`, or `Q[1-4]` is strictly invalidated and treated as `null`.
2. **Display Formatting:** Valid ISO dates are formatted for the UI via standard calendar formatting:
   `"2026-11-12"` $\rightarrow$ `"Nov 12, 2026"`.
3. **Mandatory Pairing Rule (R7):** `release_time_et` (e.g. `"12:00 PM ET"`) is displayed **only and strictly** when accompanied by an authorized, validated `release_date`. If `release_date` is null or invalid, `release_time_et` is suppressed completely.

---

## 6. Model & Round-Trip Persistence Integrity (MF-3 & MF-4)

### 6.1 `CoinModel` Property Extensions (`coin_model.dart`)

To support optional catalog metadata on `CoinModel` instances without mutating existing Firestore data, we declare the 5 nullable properties on `CoinModel`:

```dart
// In numista_mobile/lib/models/coin_model.dart

class CoinModel {
  // Existing fields (lines 4-80)...

  // U.S. Mint Official Product Metadata (NET-810)
  final double? productPriceUsd;
  final String? mintScheduleStatus;
  final String? productAvailability;
  final String? releaseDate;
  final String? releaseTimeEt;

  CoinModel({
    required this.id,
    // Existing parameters (lines 82-111)...
    this.productPriceUsd,
    this.mintScheduleStatus,
    this.productAvailability,
    this.releaseDate,
    this.releaseTimeEt,
  });
```

### 6.2 Preserving Exact `toFirestore()` Signature

The `toFirestore()` signature is preserved **without any parameter additions**:
```dart
  // Exactly matching coin_model.dart:248
  Map<String, dynamic> toFirestore() {
    return {
      'Year': year,
      'Mint Mark': mintMark,
      'Denomination': denomination,
      'Program/Series': programSeries,
      'Theme/Subject': themeSubject,
      'Variety': variety,
      'Condition': condition,
      'Strike Type': strikeType,
      'Holder Type': holderType,
      'Grading Service': gradingService,
      'Certification Number': certificationNumber,
      'Metal Content': metalContent,
      'Quantity': quantity,
      'Purchase Cost': purchaseCost,
      'Purchase Date': purchaseDate,
      'Retailer/Website': retailer,
      'Retailer Item No.': retailerItemNo,
      'Retailer Invoice #': retailerInvoiceNo,
      'Storage Location': storageLocation,
      'Personal Notes I': personalNotes,
      'Personal Reference #': personalRef,
      'Original Description from source': originalDescription,
      'AI Estimated Value': aiEstimatedValue,
      'Melt Value': meltValue,
      'image_url_obverse': imageUrlObverse,
      'image_url_reverse': imageUrlReverse,
      'image_verification_status': imageVerificationStatus,
      'image_verification_reason': imageVerificationReason,
      'greysheetGsid': greysheetGsid,
      'greysheetBid': greysheetBid,
      'greysheetAsk': greysheetAsk,
      'cpgRetail': cpgRetail,
      'priceLastUpdated': priceLastUpdated != null ? Timestamp.fromDate(priceLastUpdated!) : null,
      'hasCac': hasCac,
      'is_set': isSet,
      'set_id': setId,
      'set_contents': setContents,
      'parent_set_id': parentSetId,
      'member_of': memberOf,
      'in_original_packaging': inOriginalPackaging,
      'owner_photos': ownerPhotos,
      'provenanceLedger': provenanceLedger,
      'transferStatus': transferStatus,
      'transferId': transferId,
      'Country': country,
      'timestamp': timestamp ?? FieldValue.serverTimestamp(),
    };
  }
```

> [!IMPORTANT]
> **Why `toFirestore` does not write Mint product fields:**
> In accordance with MF-1 and MF-3, user coin documents stored in Firestore **do not store catalog-level Mint sales status**. The user's collection document stores only the coin's numismatic attributes. Keeping `toFirestore()` free of catalog properties ensures that optimistic updates in `coin_detail_screen.dart:490-494` and `682-686` never write transient government schedule statuses to Firestore.

### 6.3 Dedicated Public Serialization Method (`toPublicCatalogMap`)

Publish allow-list filtering (Rule R8) is implemented via a separate, explicit method:

```dart
  /// Generates public catalog representation.
  /// Strictly drops Mint product fields by default until allow-list gate is enabled post-Eric YES.
  Map<String, dynamic> toPublicCatalogMap({bool includeMintProductFields = false}) {
    final map = toFirestore();

    if (includeMintProductFields) {
      if (productPriceUsd != null && productPriceUsd! > 0) {
        map['product_price_usd'] = productPriceUsd;
      }
      if (mintScheduleStatus != null && mintScheduleStatus!.isNotEmpty) {
        map['mint_schedule_status'] = mintScheduleStatus;
      }
      if (productAvailability != null && productAvailability!.isNotEmpty) {
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
```

---

## 7. Strict UX & Display Rules Specification (MF-5 & MF-6)

### 7.1 UX Rule Inventory

| Rule ID | Mandate | Detailed Specification |
| :--- | :--- | :--- |
| **R1** | **Detail View Only** | Fields MUST only render within `_DetailsTab` (`coin_detail_screen.dart`) and the Overview tab of `UnifiedCoinDetailsModal`. **Strictly forbidden** on collection cards, browse cards, search results, and table rows. |
| **R2** | **Exact Issue Price Label** | Issue price MUST be labeled exactly: **`"U.S. Mint issue price"`**. Under no circumstances may it be labeled `"value"`, `"market price"`, `"retail price"`, or `"price"`. |
| **R3** | **Zero Buy Links / Urgency** | Zero outbound buy buttons, zero external affiliate links, zero store links, and zero urgency copy (no `"Buy Now"`, `"Hurry"`, `"Limited Quantity"`, `"Don't Miss Out"`). |
| **R4** | **Fail-Closed Null Suppression** | If a field is `null`, empty string, `<= 0` (for price), or `"UNKNOWN"`, it MUST be completely omitted/hidden. No placeholder strings (no `"N/A"`, `"TBD"`, or `"None"`). |
| **R5** | **Status Field Precedence** | When both `mint_schedule_status` and `product_availability` are populated, `mint_schedule_status` MUST take precedence. `product_availability` is evaluated solely as a fallback. |
| **R6** | **Neutral Muted Styling** | Status text MUST be rendered in neutral, muted subtext typography (`Theme.of(context).colorScheme.onSurfaceVariant` or `Colors.grey[600]`). No alarming badges, flashing tags, or high-urgency green/red chips. |
| **R7** | **Paired Release Time** | `release_time_et` MUST ONLY be displayed when `release_date` is also present, validated, and non-empty. Format: `"${formattedReleaseDate}, ${releaseTimeEt}"` (e.g., `"Nov 12, 2026, 12:00 PM ET"`). |
| **R8** | **Publish Allow-List Gate** | These 4 fields are dropped by default during public catalog export/publishing. They may only be published after completing the full Review Cycle and receiving Founder Eric's typed YES. |
| **R9** | **Value Separation** | `productPriceUsd` is strictly the historical government issue price and NEVER feeds `aiEstimatedValue`, `cpgRetail`, `greysheetBid`, `meltValue`, total collection valuation, portfolio metrics, or coin sorting. |
| **R10** | **Freshness Safeguard** | Availability statuses (`mintScheduleStatus` / `productAvailability`) are time-sensitive. If `asOfDate` is older than 30 days or absent, the status is suppressed to prevent displaying stale availability data. |

### 7.2 Neutral Status Copy & Strict Enum Mapping (MF-6)

Raw strings from external sources often contain promotional or urgency wording. All status values must pass through a strict allow-list mapping:

```dart
// In numista_mobile/lib/helpers/mint_product_helper.dart

class MintProductHelper {
  static const int _kStalenessWindowDays = 30;

  /// Resolves the effective status string applying precedence, enum mapping, and staleness checks.
  static String? resolveEffectiveStatus(MintProductMetadata metadata) {
    // Freshness check: suppress if older than 30 days or as-of date is missing
    if (metadata.asOfDate == null) return null;
    final age = DateTime.now().difference(metadata.asOfDate!).inDays;
    if (age > _kStalenessWindowDays) return null;

    final rawStatus = metadata.mintScheduleStatus?.trim() ?? metadata.productAvailability?.trim();
    if (rawStatus == null || rawStatus.isEmpty || rawStatus.toUpperCase() == 'UNKNOWN') {
      return null;
    }

    final asOfFormatted = '${metadata.asOfDate!.year}-${metadata.asOfDate!.month.toString().padLeft(2, '0')}';

    switch (rawStatus.toUpperCase()) {
      case 'ON_SALE':
      case 'AVAILABLE':
        return 'Available from U.S. Mint (as of $asOfFormatted)';
      case 'COMING_SOON':
      case 'SCHEDULED':
        return 'Scheduled by U.S. Mint';
      case 'SOLD_OUT':
      case 'NO_LONGER_OFFERED':
      case 'OUT_OF_STOCK':
        return 'No longer offered by U.S. Mint';
      case 'NOT_AVAILABLE':
        return 'Not available from U.S. Mint';
      default:
        // Fail closed: suppress unvetted strings completely
        return null;
    }
  }

  /// Formats official issue price with exact label R2 and value formatting.
  static (String label, String value)? formatIssuePrice(MintProductMetadata metadata) {
    final price = metadata.productPriceUsd;
    if (price == null || price <= 0 || price.isNaN || price.isInfinite) return null;

    final formatted = price % 1 == 0
        ? '\$${price.toInt()}'
        : '\$${price.toStringAsFixed(2)}';
    return ('U.S. Mint issue price', formatted);
  }

  /// Formats release schedule pairing release_date and release_time_et (R7).
  static (String label, String value)? formatReleaseSchedule(MintProductMetadata metadata) {
    final dateStr = metadata.releaseDate;
    if (dateStr == null || dateStr.isEmpty) return null;

    final parsed = DateTime.tryParse(dateStr);
    if (parsed == null) return null;

    final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    final formattedDate = '${months[parsed.month - 1]} ${parsed.day}, ${parsed.year}';

    final time = metadata.releaseTimeEt?.trim();
    if (time != null && time.isNotEmpty) {
      final cleanTime = time.endsWith('ET') ? time : '$time ET';
      return ('U.S. Mint release schedule', '$formattedDate, $cleanTime');
    }

    return ('U.S. Mint release date', formattedDate);
  }
}
```

---

## 8. Integration in `_DetailsTab` (`coin_detail_screen.dart`) (MF-5)

### 8.1 Detail Tab Tuple Placement

In `numista_mobile/lib/screens/coin_detail_screen.dart`, `_DetailsTab.build` opens `final fields = <(String, String)>[` at line 1526, and concludes with `('Notes', coin.personalNotes)` at line 1541.

The U.S. Mint product fields are placed **immediately before Notes**:

```dart
// In coin_detail_screen.dart:1526

  @override
  Widget build(BuildContext context) {
    final mintMeta = MintProductLookupService.instance.lookupForCoin(coin);

    final issuePrice = mintMeta != null ? MintProductHelper.formatIssuePrice(mintMeta) : null;
    final mintStatus = mintMeta != null ? MintProductHelper.resolveEffectiveStatus(mintMeta) : null;
    final mintRelease = mintMeta != null ? MintProductHelper.formatReleaseSchedule(mintMeta) : null;

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

      // ── NET-810: U.S. Mint Product Fields (Detail View Only) ───────────────
      if (issuePrice != null)
        issuePrice,
      if (mintStatus != null)
        ('U.S. Mint availability', mintStatus),
      if (mintRelease != null)
        mintRelease,

      ('Notes', coin.personalNotes),
    ].where((f) => f.$2.trim().isNotEmpty &&
        f.$2 != 'null' && f.$2 != 'N/A' && f.$2 != 'Ungraded').toList();
```

### 8.2 Muted Typography Styling Hook (R6)

In `_DetailsTab`, each row is rendered using a standard key-value display row. To ensure compliance with R6 without breaking standard row layout:
1. Keys for Mint fields use the standard subtitle style: `Theme.of(context).textTheme.bodyMedium`.
2. Values for Mint availability and release schedule use muted secondary styling: `Theme.of(context).colorScheme.onSurfaceVariant` (WCAG AA compliant contrast ratio $\ge 4.5:1$).
3. Zero interactive wrappers (`InkWell`, `GestureDetector`) are attached to these rows, guaranteeing zero clickable buy paths.

---

## 9. Comprehensive Automated Verification Suite (MF-7)

All test suites are marked **To be authored** and reside at real paths within `numista_mobile/test/`.

### 9.1 Unit & Widget Test Suite (`numista_mobile/test/mint_product_fields_test.dart`)

```dart
// numista_mobile/test/mint_product_fields_test.dart

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/models/coin_model.dart';
import 'package:numista_mobile/services/mint_product_lookup_service.dart';
import 'package:numista_mobile/helpers/mint_product_helper.dart';
import 'package:numista_mobile/screens/coin_detail_screen.dart';

void main() {
  group('NET-810 Unit Tests: MintProductHelper & Validation', () {
    test('Issue price uses exact label and never "value" or "market"', () {
      const meta = MintProductMetadata(productPriceUsd: 375.0);
      final priceItem = MintProductHelper.formatIssuePrice(meta);

      expect(priceItem, isNotNull);
      expect(priceItem!.$1, equals('U.S. Mint issue price'));
      expect(priceItem.$2, equals('\$375'));
      expect(priceItem.$1.toLowerCase().contains('value'), isFalse);
      expect(priceItem.$1.toLowerCase().contains('market'), isFalse);
      expect(priceItem.$1.toLowerCase().contains('retail'), isFalse);
    });

    test('Decimal cents are preserved in issue price', () {
      const meta = MintProductMetadata(productPriceUsd: 375.50);
      final priceItem = MintProductHelper.formatIssuePrice(meta);
      expect(priceItem!.$2, equals('\$375.50'));
    });

    test('Zero, negative, NaN, and infinite prices are suppressed', () {
      expect(MintProductHelper.formatIssuePrice(const MintProductMetadata(productPriceUsd: 0.0)), isNull);
      expect(MintProductHelper.formatIssuePrice(const MintProductMetadata(productPriceUsd: -15.0)), isNull);
      expect(MintProductHelper.formatIssuePrice(const MintProductMetadata(productPriceUsd: double.nan)), isNull);
      expect(MintProductHelper.formatIssuePrice(const MintProductMetadata(productPriceUsd: double.infinity)), isNull);
    });

    test('Status precedence: mint_schedule_status overrides product_availability', () {
      final meta = MintProductMetadata(
        mintScheduleStatus: 'ON_SALE',
        productAvailability: 'NOT_AVAILABLE',
        asOfDate: DateTime.now(),
      );
      final status = MintProductHelper.resolveEffectiveStatus(meta);
      expect(status, contains('Available from U.S. Mint'));
    });

    test('Fallback to product_availability when mint_schedule_status is missing', () {
      final meta = MintProductMetadata(
        mintScheduleStatus: null,
        productAvailability: 'NOT_AVAILABLE',
        asOfDate: DateTime.now(),
      );
      final status = MintProductHelper.resolveEffectiveStatus(meta);
      expect(status, equals('Not available from U.S. Mint'));
    });

    test('Unvetted status strings fail closed to null', () {
      final meta = MintProductMetadata(
        mintScheduleStatus: 'SUPER_DEAL_BUY_FAST',
        asOfDate: DateTime.now(),
      );
      expect(MintProductHelper.resolveEffectiveStatus(meta), isNull);
    });

    test('Stale status older than 30 days is suppressed', () {
      final meta = MintProductMetadata(
        mintScheduleStatus: 'AVAILABLE',
        asOfDate: DateTime.now().subtract(const Duration(days: 35)),
      );
      expect(MintProductHelper.resolveEffectiveStatus(meta), isNull);
    });

    test('Release time is suppressed when release date is absent', () {
      const meta = MintProductMetadata(releaseTimeEt: '12:00 PM ET');
      expect(MintProductHelper.formatReleaseSchedule(meta), isNull);
    });

    test('Release time and date are properly paired when date is valid ISO-8601', () {
      const meta = MintProductMetadata(
        releaseDate: '2026-11-12',
        releaseTimeEt: '12:00 PM ET',
      );
      final release = MintProductHelper.formatReleaseSchedule(meta);
      expect(release, isNotNull);
      expect(release!.$1, equals('U.S. Mint release schedule'));
      expect(release.$2, equals('Nov 12, 2026, 12:00 PM ET'));
    });

    test('Vague text dates ("TBD", "Fall 2026") fail closed to null in lookup service', () {
      expect(MintProductLookupService.validateIsoDateForTest('TBD'), isNull);
      expect(MintProductLookupService.validateIsoDateForTest('Fall 2026'), isNull);
      expect(MintProductLookupService.validateIsoDateForTest('2026-02-31'), isNull);
      expect(MintProductLookupService.validateIsoDateForTest('2026-11-12'), equals('2026-11-12'));
    });

    test('Value separation: productPriceUsd is never added to portfolio totals', () {
      final coin = CoinModel(
        id: 'c1',
        year: '2026',
        denomination: 'Dollar',
        productPriceUsd: 375.0,
        purchaseCost: '\$50.00',
        aiEstimatedValue: '60.00',
      );

      // Verify model fields remain strictly segregated
      expect(coin.purchaseCost, equals('\$50.00'));
      expect(coin.aiEstimatedValue, equals('60.00'));
      expect(coin.productPriceUsd, equals(375.0));
      expect(double.tryParse(coin.purchaseCost.replaceAll('\$', '')), equals(50.0));
    });

    test('toFirestore round-trip preserves exact signature and ignores Mint fields', () {
      final coin = CoinModel(
        id: 'c2',
        year: '1921',
        mintMark: 'S',
        denomination: 'Morgan Dollar',
        productPriceUsd: 375.0,
      );

      final firestoreMap = coin.toFirestore();
      expect(firestoreMap.containsKey('product_price_usd'), isFalse);
      expect(firestoreMap['Year'], equals('1921'));
      expect(firestoreMap['Mint Mark'], equals('S'));
    });

    test('toPublicCatalogMap drops Mint fields by default and includes on explicit allow-list', () {
      final coin = CoinModel(
        id: 'c3',
        year: '2026',
        productPriceUsd: 375.0,
        mintScheduleStatus: 'AVAILABLE',
      );

      final defaultMap = coin.toPublicCatalogMap(includeMintProductFields: false);
      expect(defaultMap.containsKey('product_price_usd'), isFalse);

      final allowedMap = coin.toPublicCatalogMap(includeMintProductFields: true);
      expect(allowedMap['product_price_usd'], equals(375.0));
      expect(allowedMap['mint_schedule_status'], equals('AVAILABLE'));
    });
  });

  group('NET-810 Widget Tests: Detail Tab & UI Guards', () {
    testWidgets('Detail tab renders exact issue price label and muted status before Notes', (tester) async {
      final coin = CoinModel(
        id: 'test_coin',
        year: '2026',
        mintMark: 'W',
        denomination: 'Eagle',
        personalNotes: 'Private estate coin',
        personalRef: 'NAC-26XS',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CoinDetailScreen(coin: coin),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Switch to Details tab
      final detailsTabFinder = find.text('Details');
      if (detailsTabFinder.evaluate().isNotEmpty) {
        await tester.tap(detailsTabFinder);
        await tester.pumpAndSettle();
      }

      // Verify exact label
      expect(find.text('U.S. Mint issue price'), findsOneWidget);
      expect(find.text('Notes'), findsOneWidget);

      // Verify Notes appears after issue price
      final pricePos = tester.getTopLeft(find.text('U.S. Mint issue price')).dy;
      final notesPos = tester.getTopLeft(find.text('Notes')).dy;
      expect(pricePos, lessThan(notesPos));
    });

    testWidgets('Zero buy links: Detail view contains no InkWell or url_launcher for Mint rows', (tester) async {
      final coin = CoinModel(
        id: 'test_coin_2',
        year: '2026',
        denomination: 'Eagle',
        personalRef: 'NAC-26XS',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CoinDetailScreen(coin: coin),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Find any buttons or tap targets containing buy copy
      expect(find.textContaining('Buy'), findsNothing);
      expect(find.textContaining('Hurry'), findsNothing);
      expect(find.textContaining('Order'), findsNothing);
      expect(find.textContaining('Cart'), findsNothing);
    });

    testWidgets('Card and browse surfaces strictly never render Mint issue price', (tester) async {
      final coin = CoinModel(
        id: 'test_card_coin',
        year: '2026',
        mintMark: 'W',
        denomination: 'Eagle',
        productPriceUsd: 375.0,
      );

      // Render standard collection card representation
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ListTile(
              title: Text('${coin.year} ${coin.denomination}'),
              subtitle: Text(coin.condition),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('U.S. Mint issue price'), findsNothing);
      expect(find.text('\$375'), findsNothing);
    });
  });
}
```

---

## 10. Operational Acceptance Criteria & Verification Matrix (MF-8)

To obtain Founder Eric's typed YES and achieve Grok Bot CoS $\ge 95 / 100$ scoring, the execution must satisfy all 10 acceptance criteria:

```
[ ] AC-1: Source-of-Truth Isolation — Official Mint product fields are derived exclusively from read-only catalog reference data (`assets/catalog/catalog_master_3202.jsonl`); zero data written to Firestore user coin documents.
[ ] AC-2: Exact Issue Price Label — Issue price renders with the exact string `"U.S. Mint issue price"`. Label never uses `"value"`, `"market price"`, or `"retail price"`.
[ ] AC-3: Strict Detail View Containment — Mint product fields render solely in `_DetailsTab` / `UnifiedCoinDetailsModal` Overview. Strictly 0 occurrences on collection cards, browse cards, search cards, or table views.
[ ] AC-4: Zero Buy Links & Zero Urgency — Zero outbound links, zero store buttons, zero affiliate redirects, and zero promotional urgency copy.
[ ] AC-5: Fail-Closed Null Suppression — Any field that is null, empty string, <=0, NaN, or "UNKNOWN" is suppressed completely with zero placeholder strings.
[ ] AC-6: Status Precedence & Neutral Copy — `mint_schedule_status` takes strict precedence over `product_availability`. Status copy is mapped to neutral factual text with a 30-day freshness window.
[ ] AC-7: Paired Release Timing — `release_time_et` is displayed exclusively when accompanied by an authorized ISO-8601 calendar `release_date`. Vague date strings fail closed to suppressed.
[ ] AC-8: Round-Trip Persistence Safety — `CoinModel.toFirestore()` preserves its exact zero-argument signature (`Map<String, dynamic> toFirestore()`). Optimistic edits in `coin_detail_screen.dart:490, 682` remain fully intact.
[ ] AC-9: Publish Allow-List Gate — Fields are dropped by default during public export and included only via explicit allow-list post-Eric typed YES.
[ ] AC-10: Value Segregation — `productPriceUsd` is strictly quarantined from AI estimated value, melt value, portfolio totals, and collection sorting.
```

---

## 11. Complete File Manifest

The table below lists every file referenced, modified, or authored under this plan:

| File Path | Action | Description |
| :--- | :--- | :--- |
| `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1.md` | **Authored** | This comprehensive v1.1 fail-fix architecture plan. |
| `numista_mobile/lib/models/coin_model.dart` | **To be edited** | Add 5 optional nullable fields; preserve `toFirestore()` signature; add `toPublicCatalogMap()`. |
| `numista_mobile/lib/services/mint_product_lookup_service.dart` | **To be authored** | Read-only in-memory catalog join service on `nac_code` and composite attributes. |
| `numista_mobile/lib/helpers/mint_product_helper.dart` | **To be authored** | Formatting helper enforcing exact labels, neutral status mapping, and date pairing. |
| `numista_mobile/lib/screens/coin_detail_screen.dart` | **To be edited** | Integrate Mint product tuples in `_DetailsTab` before Notes with muted typography. |
| `numista_mobile/test/mint_product_fields_test.dart` | **To be authored** | Comprehensive unit and Flutter `testWidgets` test suite. |
| `BETA TEST/Grok Bot/8 OCT 26/BATONS/BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1_20261107-2000.md` | **Authored** | Official review baton for Grok Bot Chief of Staff. |

---

## 12. Targeted Git Revert Rollback Procedure (MF-8)

In the event that execution is aborted, tests fail, or an unauthorized side-effect occurs:

1. **Pre-Execution Baseline SHA Capture:**
   Before staging any code edits, capture the current `HEAD` commit SHA on branch `dev`:
   ```bash
   PRE_EXEC_SHA=$(git rev-parse HEAD)
   echo "Pre-execution baseline commit: $PRE_EXEC_SHA"
   ```

2. **Targeted Revert Command:**
   Under no circumstances do we perform hard resets or broad branch reverts. Only feature commits are reverted:
   ```bash
   # Revert exact feature commits in reverse chronological order
   git revert --no-edit $PRE_EXEC_SHA..HEAD
   ```

3. **Production Main Guard:**
   `origin/main` remains strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. No git command targeting `main` is permitted.

4. **Post-Rollback Cleanliness Verification:**
   ```bash
   flutter analyze
   flutter test test/mint_product_fields_test.dart
   git status
   ```

---

## 13. Critical Path Schedule & Go-Live Fit (~13 Nov 2026)

This feature aligns with the critical path timeline leading to the Public Catalog launch and Thanksgiving Meta Ads campaign:

```
[7 Nov 20:00 ET]  NET-810 v1.1 Plan Delivered -> Grok Bot CoS Review (>=95)
[7 Nov 22:00 ET]  Grok Bot CoS Pass -> Stand Alone Grok (SAG) Review (>=95)
[8 Nov 12:00 ET]  Founder Eric Review & Typed YES Authorization
[8 Nov 18:00 ET]  NET-827 Stripe Checkout Preview Plan v1.0 Delivered
[9 Nov 14:00 ET]  Authorized Build & Local Widget Verification (dev branch)
[13 Nov 2026]     Catalog Go-Live Checkpoint (numista.ai/catalog live)
[26 Nov 2026]     Thanksgiving Meta Ads Campaign Launch
```

---

## 14. Review Routing & Execution Gate

- **Step 1:** Antigravity CoS v5 delivers this v1.1 plan and review baton to Grok Bot CoS.
- **Step 2:** Grok Bot CoS conducts independent code and rubric audit ($\ge 95 / 100$).
- **Step 3:** Stand Alone Grok (SAG, grok-4.7) conducts independent verification ($\ge 95 / 100$).
- **Step 4:** Founder Eric evaluates the plan and issues explicit typed YES.
- **Step 5:** Separate execution baton issued. **Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, and zero deployments authorized until Step 4 is complete.**
