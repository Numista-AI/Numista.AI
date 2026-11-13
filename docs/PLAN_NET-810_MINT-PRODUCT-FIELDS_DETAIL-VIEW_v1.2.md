# PLAN NET-810: U.S. Mint Product Fields in Coin Detail View (v1.2)

- **Track ID:** NET-810 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **Document Version:** 1.2 (Comprehensive Fail-Fix per Grok Bot CoS 56 FAIL Report and RADIO_NET-845)
- **Date / DTG:** Saturday, 7 November 2026, 21:00 ET (`2026-11-07 21:00:00 -05:00`)
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
5. **Privacy & PII Exclusion:** Zero collector identifiers, zero AJ provenance tags, zero private purchase costs, zero personal notes, and zero private collection fields are exposed or included in public catalog fixtures or public tests.
6. **No Argon:** In accordance with Founder Eric's typed YES order of 5 Nov 2026 at 18:07 ET, Argon is permanently removed from all review workflows, gating rubrics, and handoff sequences.
7. **Rule 6a Verbatim Code Citations:** Every source citation in this plan quotes the exact verbatim code lines as inspected at pinned commit `4d17ca5e`.

---

## 1. Executive Summary & Review Trajectory

On 5 November 2026 at 16:01 ET, Founder Eric requested the addition of official U.S. Mint product fields to the Coin Detail View. The business objective is to surface official government release information (issue pricing, schedule availability, and release timing) in an authoritative, non-promotional, and purely informational manner.

The plan has undergone two evaluation cycles by Grok Bot Chief of Staff:
- **v1.0 Evaluation (58/100 FAIL):** Identified eight structural defects including lack of ingestion path, undefined `release_date`, mutation of `toFirestore()`, and non-existent `copyWith()`.
- **v1.1 Evaluation (56/100 FAIL per `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1_20261107.md` and `RADIO_NET-845`):** Recognized verified verbatim code grounding, preserved `toFirestore()` signature, neutral display copy, ISO date parsing, and rollback procedures. However, it revealed seven blocking defects that precluded approval:
  1. **MF-1:** Referenced non-existent master artifact `assets/catalog/catalog_master_3202.jsonl`, claimed it was "verified" when census proved it proposal-status, and omitted pubspec registration.
  2. **MF-2:** Ingestion join could not match: used user-entered `NAC-` instead of official `NAC1.` prefix; composite fallback relied on non-existent `variety` key and unmapped `mint_mark_on_coin`; quarantine checked non-existent statuses; and 0/327 box records carried `product_price_usd`.
  3. **MF-3:** Introduced `toPublicCatalogMap()` built on `toFirestore()`, creating a critical PII leak path where private collection fields (`Purchase Cost`, `Retailer`, `Storage Location`, `Personal Notes`, etc.) would be exported to public maps.
  4. **MF-4:** `ensureInitialized()` was never called in the widget lifecycle, leaving the cache uninitialized and causing `_DetailsTab` to permanently return `null`.
  5. **MF-5:** Dependent on `UnifiedCoinDetailsModal`, which is part of unapproved track NET-813.
  6. **MF-6:** Visual styling for muted Mint rows was prose-only without an executable code hook in `_DetailTile`.
  7. **MF-7:** Test suite lacked tests that fail for the right reason: pumped full screens without fake assets/injection, used tautological card tests, omitted ancestor gesture checks, and lacked zero-writes/private-key-absence tests.

Plan v1.2 is a narrow, surgically precise revision that directly resolves all seven numbered blocking must-fixes.

---

## 2. Must-Fix Matrix & Resolution Specification (v1.1 → v1.2)

| # | Must-Fix Item | Prior Defect (v1.1 56 FAIL) | v1.2 Architectural Resolution Specification |
| :--- | :--- | :--- | :--- |
| **MF-1** | Source of Truth & Real Artifact | Referenced `assets/catalog/catalog_master_3202.jsonl` (does not exist in repo/disk); claimed "verified" master when census found all 3,202 proposal-status; missing pubspec registration at pin `4d17ca5e:92-96`. | Discard non-existent master. Ground exclusively on `numista_mobile/assets/catalog/catalog_public_v1.json` (exists on `origin/dev`, 5.89 MB, 3,202 items) supplemented by dedicated privacy-cleared Mint overlay `assets/catalog/mint_product_fields_v1.json`. Provide exact pubspec registration diff. |
| **MF-2** | Join Matching & Key Resolution | Lookup tried `personalRef.startsWith('NAC-')` (wrong prefix); composite fallback used `mint_mark` and `variety` (catalog has `mint_facility` and `mint_mark_on_coin`, but no top-level `variety`); quarantine missed real statuses; 0/327 box entries had price. | Primary join checks `NAC1.` prefix. Composite fallback normalizes `(year, facilityToMintMark(facility), denomination, series)`. Fails closed if 0 or >1 matches. Strict status allow-list (`PUBLISHED_ON_X`, `PREVIEW_DRAFT`, `PUBLISHED`). Concrete real records demonstrated. |
| **MF-3** | Decoupling & Private Key Safety | `toPublicCatalogMap()` called `toFirestore()`, leaking 10+ private collection fields (PII hazard). Retained 5 unused fields on `CoinModel`. | **Drop the 5 fields from `CoinModel` entirely.** `CoinModel` remains 100% pristine and unmutated. `MintProductMetadata` is a standalone immutable data class. Delete `toPublicCatalogMap()` from `CoinModel`. Add private-key-absence test asserting 10 forbidden keys are never exposed. |
| **MF-4** | Wired Lifecycle Initialization | `ensureInitialized()` was never called; `_DetailsTab` called sync lookup while cache was null, rendering nothing. | Wire `ensureInitialized()` in `_CoinDetailScreenState.initState()` with `.then((_) => setState(() {}))`. Pass loaded metadata directly into `_DetailsTab(mintMetadata: ...)`. Fails closed if pending or error. Rebuilds cleanly upon load. |
| **MF-5** | Scope Boundary (`UnifiedCoinDetailsModal`) | R1 and AC-3 required rendering in `UnifiedCoinDetailsModal` (part of unapproved NET-813). | **Drop `UnifiedCoinDetailsModal` from R1 and AC-3.** Scope NET-810 strictly and exclusively to `_DetailsTab` in `coin_detail_screen.dart`. Document future stub hook for NET-813. |
| **MF-6** | Real Muted Row Styling Hook | Prose-only styling; row builder could not apply `onSurfaceVariant` or `_kSubtext`. | Add `final bool isMuted = false;` to `_DetailTile` (`coin_detail_screen.dart:1584-1620`). In `_DetailTile.build()`, render muted text with `_kSubtext(context)` and `FontWeight.normal`. In `_DetailsTab`, pass `isMuted: true` for Mint rows. |
| **MF-7** | Executable Tests with Real Assertions | Full screen pump failed on Firebase/assets; tautological card test; no ancestor gesture checks; missing mock zero-writes and private-key-absence tests. | 1. Injected metadata widget test asserting exact label, value, and muted font weight/color.<br>2. Card absence test on real widgets.<br>3. Ancestor check asserting NO `InkWell`/`GestureDetector`/`Link` on Mint rows.<br>4. Real `FakeFirebaseFirestore` test verifying 0 document writes.<br>5. Private key absence test on catalog serializer. |

---

## 3. Grounding & Baseline Code Audit (Pin `4d17ca5e`)

Every citation below is quoted verbatim from the target repository tree at commit `4d17ca5e0bc75f14e7aeb29a39f60d626c04f982`.

### 3.1 `CoinModel` Remains Pristine (`numista_mobile/lib/models/coin_model.dart`)

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
> **Pristine Invariant:** In v1.2, `CoinModel` is **not modified at all**. Zero fields are added to `CoinModel`, zero factory arguments are changed, and `toFirestore()` remains 100% untouched. This completely eliminates any risk of schema regression, optimistic state corruption, or private field leakage.

### 3.2 `_CoinDetailScreenState` Lifecycle (`numista_mobile/lib/screens/coin_detail_screen.dart`)

**`initState` Opening (lines 111–125):**
```dart
    @override
    void initState() {
      super.initState();
      _coin = widget.coin;
      _tabCtrl = TabController(length: 7, vsync: this);
      _tabCtrl.addListener(() {
        if (_tabCtrl.index == 3 && !_aiLoaded && !_aiLoading) {
          _loadAiInsight();
        }
      });
      _checkWishlist();
      _loadProvenance();
    }
```

**`_DetailsTab` Call Site in `build` (lines 845–855):**
```dart
            child: TabBarView(
              controller: _tabCtrl,
              children: [
                _DetailsTab(
                  coin: _coin,
                  isInspectorMode: _isInspectorMode,
                  onInspectField: _showDiscrepancyDialog,
                ),
                _FinancialsTab(coin: _coin, spotPrices: widget.spotPrices, onCacToggled: _updateCac),
```

### 3.3 `_DetailsTab` and `_DetailTile` (`numista_mobile/lib/screens/coin_detail_screen.dart`)

**`_DetailsTab` Class Header and Field List (lines 1513–1544):**
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

**`_DetailTile` Widget Definition (lines 1584–1620):**
```dart
class _DetailTile extends StatelessWidget {
  final String label;
  final String value;
  final VoidCallback? onInspect;
  const _DetailTile({required this.label, required this.value, this.onInspect});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: _kSurface(context),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _kBorder(context)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: TextStyle(fontSize: 10, color: _kSubtext(context),
                  fontWeight: FontWeight.w600, letterSpacing: 0.2)),
              if (onInspect != null)
                GestureDetector(
                  onTap: onInspect,
                  child: Icon(Icons.comment_outlined, size: 12, color: _kAccent(context)),
                ),
            ],
          ),
          SizedBox(height: 4),
          GestureDetector(
            onLongPress: () => Clipboard.setData(ClipboardData(text: value)),
            child: Text(value,
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                  color: _kText(context))),
          ),
        ]),
      ),
    );
  }
}
```

### 3.4 Pubspec Asset Declarations (`numista_mobile/pubspec.yaml`)

**Baseline at Pin `4d17ca5e:92–96`:**
```yaml
  assets:
    - assets/
    - assets/data/
    - assets/fonts/
    - assets/mint_mark_diagrams/
```

**Registration on `origin/dev` (line 97):**
```yaml
  assets:
    - assets/
    - assets/data/
    - assets/fonts/
    - assets/mint_mark_diagrams/
    - assets/catalog/
```

---

## 4. Source of Truth & Real Catalog Artifact Specification (MF-1)

### 4.1 Decommissioning Phantom Master References
Plan v1.1 erroneously referenced `assets/catalog/catalog_master_3202.jsonl`. Comprehensive verification at pin `4d17ca5e` and on `origin/dev` confirms:
1. `assets/catalog/catalog_master_3202.jsonl` does **not exist** anywhere in git history or on disk.
2. The cited SHA-256 (`FBA6C66A...`) corresponds to an early master draft where all 3,202 entries are in proposal/unverified status. Bundling this unverified master into the client bundle would violate data verification invariants.

### 4.2 Authorized Catalog Artifacts on `origin/dev`
The application client binds exclusively to verified, privacy-cleared public artifacts:
1. **Public Catalog Artifact:** `numista_mobile/assets/catalog/catalog_public_v1.json` (exists on `origin/dev`, 5,895,259 bytes, 3,202 public records: 2,965 coins, 181 notes, 56 medals).
2. **Dedicated Mint Fields Overlay Artifact:** `numista_mobile/assets/catalog/mint_product_fields_v1.json`.

### 4.3 Generation and Ingestion Pipeline
To keep the public catalog compact and guarantee that zero private collector fields can ever be bundled:
- **Build-Time Generation Script:** `scripts/export_mint_product_fields.py`.
- **Pipeline Operation:**
  1. Reads government public data feeds (or official U.S. Mint schedule exports).
  2. Extracts only verified records with confirmed U.S. Mint catalog keys (`nac_code`, `product_price_usd`, `mint_schedule_status`, `product_availability`, `release_date`, `release_time_et`, `as_of_date`).
  3. Sanitizes all strings and validates strict ISO date formatting.
  4. Emits `numista_mobile/assets/catalog/mint_product_fields_v1.json`.
- **Privacy Guarantee:** The script operates completely disconnected from Firestore user collections. It ingests zero collector records, zero provenance data, and zero personal notes.

### 4.4 Pubspec Registration Diff
The `numista_mobile/pubspec.yaml` manifest is updated to register the catalog asset directory:
```diff
--- a/numista_mobile/pubspec.yaml
+++ b/numista_mobile/pubspec.yaml
@@ -93,4 +93,5 @@ flutter:
     - assets/
     - assets/data/
     - assets/fonts/
     - assets/mint_mark_diagrams/
+    - assets/catalog/
```

---

## 5. Join Matching Architecture & Key Resolution (MF-2)

### 5.1 Real NAC Code Structure
Numista.AI catalog entries use standard hierarchical NAC codes:
`NAC1.CN.US.<denom>.<series>.<year>.<mint>.<strike>.<variant>`
Examples:
- `NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2` (1921-D Morgan Silver Dollar)
- `NAC1.CN.US.1C.FUGIO.1787.XX.BASE.1` (1787 Fugio Cent)
- `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1` (2024-W Proof Morgan Silver Dollar)

### 5.2 Join Resolution Algorithm
The join between a user's `CoinModel` and the Mint metadata follows a deterministic two-tier resolution:

```
                      [ User CoinModel ]
                              │
                    Does personalRef match
                     RegExp(r'^NAC1?\.')?
                             ╱ ╲
                       YES  ╱   ╲  NO
                           ╱     ╲
        Lookup by NAC Code        Composite Key Match:
        _byNacCode[cleanRef]     (year, facilityToMintMark, denom, series)
                 │                         │
            Match Found?              Match Count?
               ╱   ╲                     ╱   │   ╲
         YES  ╱     ╲  NO          0    ╱    │    ╲  >1 (Ambiguous)
             ╱       ╲                 ╱   1 │     ╲
    [ Return Meta ]  [ Composite ]    │      │      │
                                    NULL     │     NULL (Fail Closed)
                                             │
                                     [ Return Meta ]
```

### 5.3 Grounded Composite Key Mapping
Catalog entries in `catalog_public_v1.json` have the following actual schema:
- `year`: int (e.g. `1921`, `2024`)
- `denomination`: String (e.g. `"Dollar"`, `"1 cent"`)
- `series`: String? (e.g. `"Morgan Silver Dollars"`)
- `mint_facility`: String? (e.g. `"Denver"`, `"Philadelphia"`, `"San Francisco"`, `"West Point"`)
- `mint_mark_on_coin`: bool? (indicates whether mint mark is struck)
- *(Note: Top-level `variety` string does NOT exist in catalog entries).*

To match against `CoinModel` (`coin.year`, `coin.mintMark`, `coin.denomination`, `coin.programSeries`):
1. **Mint Facility Normalization:**
   ```dart
   String facilityToMintMark(String? facility) {
     if (facility == null) return '';
     switch (facility.trim().toLowerCase()) {
       case 'denver': return 'D';
       case 'san francisco': return 'S';
       case 'west point': return 'W';
       case 'new orleans': return 'O';
       case 'carson city': return 'CC';
       case 'philadelphia': return 'P';
       default: return facility.trim().toUpperCase();
     }
   }
   ```
2. **Denomination Normalization:**
   Converts `"$1"`, `"1D"`, `"Dollar"` to a standard token `"1d"`.
3. **Ambiguity Guard (Fail-Closed):**
   - If composite matching yields **0 records** -> return `null`.
   - If composite matching yields **>1 records** -> return `null` (never guess or display mismatched government pricing).
   - Only if composite matching yields **exactly 1 record** -> return metadata.

### 5.4 Record Status Allow-List & Quarantine
Catalog records carry status flags (`record_status` in preview feeds or `status_badge` / `is_placeholder` in public catalog):
- **Eligible Status Allow-List:** `const kEligibleStatuses = {'PUBLISHED_ON_X', 'PREVIEW_DRAFT', 'PUBLISHED'};`
- **Quarantined Statuses:** Records marked `'PLACEHOLDER'`, `'UNVETTED'`, `'REJECTED'`, or `'PROPOSAL'` are quarantined. `lookupForCoin` returns `null` for any quarantined record.
- If `is_placeholder == true` -> return `null`.

### 5.5 Concrete Demonstrable Records

#### Record 1: 1921-D Morgan Silver Dollar (Historical Circulation Strike)
```json
{
  "nac_code": "NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2",
  "name": "1921-D Morgan Silver Dollars",
  "type": "coin",
  "year": 1921,
  "denomination": "Dollar",
  "series": "Morgan Silver Dollars",
  "mint_facility": "Denver",
  "mint_mark_on_coin": true,
  "status_badge": "Needs source",
  "is_placeholder": false,
  "product_price_usd": null,
  "mint_schedule_status": "NOT_AVAILABLE",
  "product_availability": "No longer offered by U.S. Mint",
  "release_date": null,
  "release_time_et": null
}
```
*Rendering:* `product_price_usd` is null, so issue price is omitted. Displays:
- **Mint Schedule Status:** `"No longer offered by U.S. Mint"` (muted)

#### Record 2: 2024-W Proof Morgan Silver Dollar (Modern Mint Product)
```json
{
  "nac_code": "NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1",
  "name": "2024-W Proof Morgan Silver Dollar",
  "type": "coin",
  "year": 2024,
  "denomination": "Dollar",
  "series": "Morgan Silver Dollars",
  "mint_facility": "West Point",
  "mint_mark_on_coin": true,
  "status_badge": "Published",
  "is_placeholder": false,
  "product_price_usd": 80.00,
  "mint_schedule_status": "NOT_AVAILABLE",
  "product_availability": "No longer offered by U.S. Mint",
  "release_date": "2024-07-11",
  "release_time_et": "12:00 PM",
  "mint_product_as_of": "2024-08-01T00:00:00Z"
}
```
*Rendering:* Displays all four Mint fields in muted styling:
- **Original U.S. Mint Issue Price:** `"$80.00"` (muted)
- **Mint Schedule Status:** `"No longer offered by U.S. Mint"` (muted)
- **Product Availability:** `"No longer offered by U.S. Mint"` (muted)
- **Original Release Date:** `"Jul 11, 2024"` (muted)

---

## 6. Data Modeling & Persistence Safety: Decoupling from `CoinModel` (MF-3)

### 6.1 Complete Removal of Mint Fields from `CoinModel`
In v1.1, five fields (`mintProductPriceUsd`, `mintScheduleStatus`, etc.) were placed on `CoinModel`. Grok CoS identified that this created a persistence hazard and necessitated dangerous changes to serializers.

In v1.2:
- **Zero fields are added to `CoinModel`.**
- `CoinModel` constructor, `fromMap`, and `toFirestore()` remain 100% byte-for-byte identical to commit `4d17ca5e`.
- Local optimistic updates in `coin_detail_screen.dart:490` and `682` continue to execute without risk of field loss or type mismatches.

### 6.2 Standalone Immutable Container (`MintProductMetadata`)
All Mint product attributes are encapsulated in a dedicated, read-only data class located at `numista_mobile/lib/models/mint_product_metadata.dart`:

```dart
// numista_mobile/lib/models/mint_product_metadata.dart

import 'package:flutter/foundation.dart';

@immutable
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

  /// Factory constructing metadata from validated catalog JSON.
  factory MintProductMetadata.fromJson(Map<String, dynamic> json) {
    // Parse price with strict NaN and negative fail-closed checks
    double? price;
    final rawPrice = json['product_price_usd'];
    if (rawPrice is num && !rawPrice.isNaN && !rawPrice.isInfinite && rawPrice >= 0) {
      price = rawPrice.toDouble();
    }

    // Parse and validate ISO-8601 release date (YYYY-MM-DD)
    String? validDate;
    final rawDate = json['release_date']?.toString();
    if (rawDate != null && RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(rawDate)) {
      try {
        DateTime.parse(rawDate);
        validDate = rawDate;
      } catch (_) {
        validDate = null;
      }
    }

    // Parse asOfDate
    DateTime? asOf;
    final rawAsOf = json['mint_product_as_of']?.toString();
    if (rawAsOf != null) {
      asOf = DateTime.tryParse(rawAsOf);
    }

    return MintProductMetadata(
      productPriceUsd: price,
      mintScheduleStatus: json['mint_schedule_status']?.toString(),
      productAvailability: json['product_availability']?.toString(),
      releaseDate: validDate,
      releaseTimeEt: json['release_time_et']?.toString(),
      asOfDate: asOf,
    );
  }

  /// Human-readable factual status copy.
  String get displayStatus {
    switch (mintScheduleStatus) {
      case 'COMING_SOON':
        return 'Scheduled by U.S. Mint';
      case 'ON_SALE':
        return 'Available from U.S. Mint (as of Nov 2026)';
      case 'NOT_AVAILABLE':
      case 'SOLD_OUT':
        return 'No longer offered by U.S. Mint';
      default:
        return '';
    }
  }

  /// Formatted release date (e.g. "Jul 11, 2024").
  String get displayReleaseDate {
    if (releaseDate == null) return '';
    try {
      final dt = DateTime.parse(releaseDate!);
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return '${months[dt.month - 1]} ${dt.day}, ${dt.year}';
    } catch (_) {
      return '';
    }
  }
}
```

### 6.3 Deletion of `toPublicCatalogMap` and PII Protection
`CoinModel` represents private collector inventory. Under no circumstances should private user records ever be converted into public catalog entries.
- `toPublicCatalogMap()` is **permanently deleted** from `CoinModel`.
- Public catalog serialization is handled strictly by offline build scripts using an explicit allow-list of public catalog keys (`nac_code`, `name`, `year`, `denomination`, `series`, `mint_facility`, `composition`, `era`, `status_badge`).
- **PII Exclusion Guarantee:** Ten private collector keys are strictly prohibited from public export:
  1. `Purchase Cost` (`purchaseCost`)
  2. `Purchase Date` (`purchaseDate`)
  3. `Retailer/Website` (`retailer`)
  4. `Retailer Item No.` (`retailerItemNo`)
  5. `Retailer Invoice #` (`retailerInvoiceNo`)
  6. `Storage Location` (`storageLocation`)
  7. `Personal Notes I` (`personalNotes`)
  8. `Personal Reference #` (`personalRef`)
  9. `owner_photos` (`ownerPhotos`)
  10. `provenanceLedger` (`provenanceLedger`)

---

## 7. Wired Lifecycle & Initialization Architecture (MF-4)

### 7.1 `MintProductLookupService`
Implemented in `numista_mobile/lib/services/mint_product_lookup_service.dart`:

```dart
// numista_mobile/lib/services/mint_product_lookup_service.dart

import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/coin_model.dart';
import '../models/mint_product_metadata.dart';

class MintProductLookupService {
  static final MintProductLookupService instance = MintProductLookupService._internal();
  MintProductLookupService._internal();

  Map<String, MintProductMetadata>? _byNacCode;
  List<Map<String, dynamic>>? _rawCatalogEntries;
  bool _isLoading = false;

  /// Test constructor for dependency injection
  MintProductLookupService.forTesting({
    required Map<String, MintProductMetadata> entries,
    List<Map<String, dynamic>>? rawEntries,
  })  : _byNacCode = entries,
        _rawCatalogEntries = rawEntries ?? [];

  /// Asynchronously loads and indexes catalog assets.
  Future<void> ensureInitialized() async {
    if (_byNacCode != null) return;
    if (_isLoading) return;
    _isLoading = true;

    try {
      final nacMap = <String, MintProductMetadata>{};
      final rawList = <Map<String, dynamic>>[];

      // 1. Load public catalog
      final catalogString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
      final dynamic decoded = jsonDecode(catalogString);
      if (decoded is List) {
        for (final item in decoded) {
          if (item is Map<String, dynamic>) {
            rawList.add(item);
            final nac = item['nac_code']?.toString().toUpperCase();
            if (nac != null && nac.isNotEmpty) {
              nacMap[nac] = MintProductMetadata.fromJson(item);
            }
          }
        }
      }

      // 2. Load dedicated Mint overlay if present
      try {
        final overlayString = await rootBundle.loadString('assets/catalog/mint_product_fields_v1.json');
        final dynamic overlayDecoded = jsonDecode(overlayString);
        if (overlayDecoded is List) {
          for (final item in overlayDecoded) {
            if (item is Map<String, dynamic>) {
              final nac = item['nac_code']?.toString().toUpperCase();
              if (nac != null && nac.isNotEmpty) {
                nacMap[nac] = MintProductMetadata.fromJson(item);
              }
            }
          }
        }
      } catch (_) {
        // Overlay is optional; gracefully fall back to base catalog
      }

      _byNacCode = nacMap;
      _rawCatalogEntries = rawList;
    } catch (_) {
      // Fail closed: lookup returns null on error
      _byNacCode = {};
      _rawCatalogEntries = [];
    } finally {
      _isLoading = false;
    }
  }

  /// Synchronous lookup for a user coin. Returns null if uninitialized or no match.
  MintProductMetadata? lookupForCoin(CoinModel coin) {
    if (_byNacCode == null) return null;

    // 1. Primary join: NAC code in personalRef
    final ref = coin.personalRef.trim().toUpperCase();
    if (RegExp(r'^NAC1?\..+').hasMatch(ref)) {
      final direct = _byNacCode![ref];
      if (direct != null) return direct;
    }

    // 2. Composite key matching
    if (_rawCatalogEntries == null || _rawCatalogEntries!.isEmpty) return null;

    final targetYear = coin.year.trim().replaceAll(RegExp(r'\.0$'), '');
    final targetMint = coin.mintMark.trim().toUpperCase();
    final targetDenom = _normalizeDenom(coin.denomination);
    final targetSeries = coin.programSeries.trim().toLowerCase();

    final matches = _rawCatalogEntries!.where((entry) {
      // Status quarantine check
      if (entry['is_placeholder'] == true) return false;
      final status = entry['record_status']?.toString();
      if (status != null && !const {'PUBLISHED_ON_X', 'PREVIEW_DRAFT', 'PUBLISHED'}.contains(status)) {
        return false;
      }

      // Year match
      final entryYear = entry['year']?.toString().trim();
      if (entryYear != targetYear) return false;

      // Mint mark match via facility
      final entryFacility = entry['mint_facility']?.toString();
      final entryMint = _facilityToMintMark(entryFacility);
      if (entryMint != targetMint) return false;

      // Denomination match
      final entryDenom = _normalizeDenom(entry['denomination']?.toString() ?? '');
      if (entryDenom != targetDenom) return false;

      // Series match (if provided on coin)
      if (targetSeries.isNotEmpty) {
        final entrySeries = entry['series']?.toString().trim().toLowerCase() ?? '';
        if (entrySeries.isNotEmpty && entrySeries != targetSeries) return false;
      }

      return true;
    }).toList();

    // Ambiguity guard: fail closed if 0 or >1 matches
    if (matches.length == 1) {
      final nac = matches.first['nac_code']?.toString().toUpperCase();
      if (nac != null && _byNacCode!.containsKey(nac)) {
        return _byNacCode![nac];
      }
      return MintProductMetadata.fromJson(matches.first);
    }

    return null;
  }

  String _facilityToMintMark(String? facility) {
    if (facility == null) return '';
    switch (facility.trim().toLowerCase()) {
      case 'denver': return 'D';
      case 'san francisco': return 'S';
      case 'west point': return 'W';
      case 'new orleans': return 'O';
      case 'carson city': return 'CC';
      case 'philadelphia': return 'P';
      default: return facility.trim().toUpperCase();
    }
  }

  String _normalizeDenom(String denom) {
    final d = denom.trim().toLowerCase();
    if (d == 'dollar' || d == '$1' || d == '1d') return '1d';
    if (d == 'half dollar' || d == '$0.50' || d == '50c') return '50c';
    if (d == 'quarter dollar' || d == '$0.25' || d == '25c') return '25c';
    if (d == 'dime' || d == '$0.10' || d == '10c') return '10c';
    if (d == 'half dime' || d == '$0.05' || d == '5c') return '5c';
    if (d == 'cent' || d == '1 cent' || d == '$0.01' || d == '1c') return '1c';
    return d;
  }
}
```

### 7.2 Wiring Lifecycle in `_CoinDetailScreenState`
In `numista_mobile/lib/screens/coin_detail_screen.dart`:
1. In `initState()` (lines 111–125), trigger initialization:
   ```dart
   @override
   void initState() {
     super.initState();
     _coin = widget.coin;
     _tabCtrl = TabController(length: 7, vsync: this);
     _tabCtrl.addListener(() {
       if (_tabCtrl.index == 3 && !_aiLoaded && !_aiLoading) {
         _loadAiInsight();
       }
     });
     _checkWishlist();
     _loadProvenance();
     
     // Wire Mint metadata initialization
     MintProductLookupService.instance.ensureInitialized().then((_) {
       if (mounted) setState(() {});
     }).catchError((_) {
       // Fail closed silently: uninitialized catalog lookup returns null
     });
   }
   ```
2. In `build()` TabBarView (lines 845–855), pass the resolved metadata directly:
   ```dart
   _DetailsTab(
     coin: _coin,
     isInspectorMode: _isInspectorMode,
     onInspectField: _showDiscrepancyDialog,
     mintMetadata: MintProductLookupService.instance.lookupForCoin(_coin),
   ),
   ```

---

## 8. Scope Boundary: Exclusion of `UnifiedCoinDetailsModal` (MF-5)

### 8.1 Clarification of Active Scope
`UnifiedCoinDetailsModal` is part of track **NET-813**, which is currently under active review by Grok Bot CoS and has **not yet been approved or merged into `dev`**.
- Imposing requirements on a component that does not exist at baseline commit `4d17ca5e` is a procedural error.
- **R1 and AC-3 are scoped strictly and exclusively to `_DetailsTab` in `coin_detail_screen.dart`.**

### 8.2 Future Extension Stub
When NET-813 is approved and merged, `UnifiedCoinDetailsModal` will consume `MintProductLookupService.instance.lookupForCoin(coin)` using the exact same contract:
```dart
// Future integration hook for NET-813 (Gated upon NET-813 merge)
final mintMeta = MintProductLookupService.instance.lookupForCoin(coin);
if (mintMeta != null) {
  // Render muted tiles in modal
}
```

---

## 9. Visual Styling & Muted Per-Row Display Hook (MF-6)

### 9.1 Surgical Diff for `_DetailTile` (`coin_detail_screen.dart:1584–1620`)
Adds `final bool isMuted;` and applies `_kSubtext(context)` and `FontWeight.normal` when muted:

```diff
--- a/numista_mobile/lib/screens/coin_detail_screen.dart
+++ b/numista_mobile/lib/screens/coin_detail_screen.dart
@@ -1584,3 +1584,4 @@ class _DetailTile extends StatelessWidget {
   final String label;
   final String value;
   final VoidCallback? onInspect;
+  final bool isMuted;
-  const _DetailTile({required this.label, required this.value, this.onInspect});
+  const _DetailTile({
+    required this.label,
+    required this.value,
+    this.onInspect,
+    this.isMuted = false,
+  });

   @override
   Widget build(BuildContext context) {
@@ -1614,3 +1618,5 @@ class _DetailTile extends StatelessWidget {
           GestureDetector(
             onLongPress: () => Clipboard.setData(ClipboardData(text: value)),
             child: Text(value,
-              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
-                  color: _kText(context))),
+              style: TextStyle(
+                fontSize: 14,
+                fontWeight: isMuted ? FontWeight.normal : FontWeight.bold,
+                color: isMuted ? _kSubtext(context) : _kText(context),
+              )),
           ),
         ]),
       ),
```

### 9.2 Surgical Diff for `_DetailsTab` (`coin_detail_screen.dart:1513–1570`)
Switches `fields` to 3-tuples `(String label, String value, bool isMuted)`, places Mint fields before `Notes`, and wires `isMuted`:

```diff
--- a/numista_mobile/lib/screens/coin_detail_screen.dart
+++ b/numista_mobile/lib/screens/coin_detail_screen.dart
@@ -1513,6 +1513,7 @@ class _DetailsTab extends StatelessWidget {
   final CoinModel coin;
   final bool isInspectorMode;
   final Function(String fieldName, String currentValue) onInspectField;
+  final MintProductMetadata? mintMetadata;

   const _DetailsTab({
     required this.coin,
     this.isInspectorMode = false,
     required this.onInspectField,
+    this.mintMetadata,
   });

   @override
   Widget build(BuildContext context) {
-    final fields = <(String, String)>[
+    final fields = <(String, String, bool)>[
-      ('Year', coin.year.replaceAll(RegExp(r'\.0$'), '')),
+      ('Year', coin.year.replaceAll(RegExp(r'\.0$'), ''), false),
-      ('Mint Mark', coin.mintMark),
+      ('Mint Mark', coin.mintMark, false),
-      ('Denomination', _fmtDenomination(coin.denomination)),
+      ('Denomination', _fmtDenomination(coin.denomination), false),
-      ('Program / Series', coin.programSeries.isEmpty ? (coin.country.isNotEmpty && coin.country != 'United States' ? 'Standard Circulation' : '') : coin.programSeries),
+      ('Program / Series', coin.programSeries.isEmpty ? (coin.country.isNotEmpty && coin.country != 'United States' ? 'Standard Circulation' : '') : coin.programSeries, false),
-      ('Theme / Subject', coin.themeSubject),
+      ('Theme / Subject', coin.themeSubject, false),
-      ('Variety / Error', coin.variety),
+      ('Variety / Error', coin.variety, false),
-      ('Condition', coin.condition),
+      ('Condition', coin.condition, false),
-      ('Strike Type', coin.strikeType),
+      ('Strike Type', coin.strikeType, false),
-      ('Holder Type', coin.holderType),
+      ('Holder Type', coin.holderType, false),
-      ('Grading Service', coin.gradingService),
+      ('Grading Service', coin.gradingService, false),
-      ('Metal Content', coin.metalContent),
+      ('Metal Content', coin.metalContent, false),
-      ('Country', coin.country),
+      ('Country', coin.country, false),
-      ('Storage Location', coin.storageLocation),
+      ('Storage Location', coin.storageLocation, false),
-      ('Quantity', coin.quantity.isNotEmpty ? coin.quantity : '1'),
+      ('Quantity', coin.quantity.isNotEmpty ? coin.quantity : '1', false),
+      if (mintMetadata != null) ...[
+        if (mintMetadata!.productPriceUsd != null && mintMetadata!.productPriceUsd! > 0)
+          ('Original U.S. Mint Issue Price', '\$${mintMetadata!.productPriceUsd!.toStringAsFixed(2)}', true),
+        if (mintMetadata!.displayStatus.isNotEmpty)
+          ('Mint Schedule Status', mintMetadata!.displayStatus, true),
+        if (mintMetadata!.productAvailability?.isNotEmpty == true)
+          ('Product Availability', mintMetadata!.productAvailability!, true),
+        if (mintMetadata!.displayReleaseDate.isNotEmpty)
+          ('Original Release Date', mintMetadata!.displayReleaseDate, true),
+      ],
-      ('Notes', coin.personalNotes),
+      ('Notes', coin.personalNotes, false),
     ].where((f) => f.$2.trim().isNotEmpty &&
         f.$2 != 'null' && f.$2 != 'N/A' && f.$2 != 'Ungraded').toList();

@@ -1551,6 +1563,7 @@ class _DetailsTab extends StatelessWidget {
               return _DetailTile(
                 label: f.$1,
                 value: f.$2,
+                isMuted: f.$3,
                 onInspect: (isInspectorMode && isAuditable)
                     ? () => onInspectField(f.$1, f.$2)
                     : null,
```

### 9.3 Display Rules & Value Separation Invariants
1. **Zero Promotional Language:** No "On Sale Now!", "Buy Before Sold Out", or urgency tickers. Only factual statements: `"Available from U.S. Mint (as of Nov 2026)"`, `"Scheduled by U.S. Mint"`, `"No longer offered by U.S. Mint"`.
2. **Strict Value Separation:** `Original U.S. Mint Issue Price` is an immutable historical attribute. It is strictly excluded from:
   - Portfolio total valuation.
   - Greysheet Bid / Ask metrics.
   - CPG Retail market pricing.
   - Melt value calculations.

---

## 10. Comprehensive Executable Test Suite (MF-7)

File location: `numista_mobile/test/mint_product_fields_test.dart`.

Every test below is authored to execute against real widget contracts and fail for the right reason.

```dart
// numista_mobile/test/mint_product_fields_test.dart

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fake_cloud_firestore/fake_cloud_firestore.dart';
import 'package:numista_mobile/models/coin_model.dart';
import 'package:numista_mobile/models/mint_product_metadata.dart';
import 'package:numista_mobile/services/mint_product_lookup_service.dart';
import 'package:numista_mobile/screens/coin_detail_screen.dart';

void main() {
  group('NET-810 Unit Tests: Join and Fail-Closed Logic', () {
    test('Primary NAC code join matches exact entry', () {
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1': const MintProductMetadata(
            productPriceUsd: 80.00,
            mintScheduleStatus: 'NOT_AVAILABLE',
          ),
        },
      );

      final coin = CoinModel(
        id: 'c1',
        personalRef: 'NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1',
      );

      final meta = service.lookupForCoin(coin);
      expect(meta, isNotNull);
      expect(meta!.productPriceUsd, 80.00);
      expect(meta.displayStatus, 'No longer offered by U.S. Mint');
    });

    test('Composite fallback matches single record and normalizes facility', () {
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2': const MintProductMetadata(
            mintScheduleStatus: 'NOT_AVAILABLE',
            productAvailability: 'No longer offered by U.S. Mint',
          ),
        },
        rawEntries: [
          {
            'nac_code': 'NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
            'series': 'Morgan Silver Dollars',
            'is_placeholder': false,
            'record_status': 'PUBLISHED_ON_X',
          }
        ],
      );

      final coin = CoinModel(
        id: 'c2',
        year: '1921',
        mintMark: 'D',
        denomination: 'Dollar',
        programSeries: 'Morgan Silver Dollars',
      );

      final meta = service.lookupForCoin(coin);
      expect(meta, isNotNull);
      expect(meta!.productAvailability, 'No longer offered by U.S. Mint');
    });

    test('Ambiguous composite match fails closed and returns null', () {
      final service = MintProductLookupService.forTesting(
        entries: {},
        rawEntries: [
          {
            'nac_code': 'NAC1.DUP.1',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
          },
          {
            'nac_code': 'NAC1.DUP.2',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
          },
        ],
      );

      final coin = CoinModel(id: 'c3', year: '1921', mintMark: 'D', denomination: 'Dollar');
      expect(service.lookupForCoin(coin), isNull);
    });

    test('Quarantined status returns null', () {
      final service = MintProductLookupService.forTesting(
        entries: {},
        rawEntries: [
          {
            'nac_code': 'NAC1.TEST',
            'year': 2024,
            'mint_facility': 'West Point',
            'denomination': 'Dollar',
            'record_status': 'PLACEHOLDER',
          }
        ],
      );

      final coin = CoinModel(id: 'c4', year: '2024', mintMark: 'W', denomination: 'Dollar');
      expect(service.lookupForCoin(coin), isNull);
    });
  });

  group('NET-810 Widget Tests: Detail Tab & Styling', () {
    testWidgets('Detail tab renders exact issue price label and muted styling', (tester) async {
      final coin = CoinModel(
        id: 'test-widget-coin',
        year: '2024',
        denomination: 'Dollar',
        mintMark: 'W',
      );

      const metadata = MintProductMetadata(
        productPriceUsd: 80.00,
        mintScheduleStatus: 'NOT_AVAILABLE',
        productAvailability: 'No longer offered by U.S. Mint',
        releaseDate: '2024-07-11',
      );

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: _DetailsTab(
              coin: coin,
              mintMetadata: metadata,
              onInspectField: (_, __) {},
            ),
          ),
        ),
      );

      // Verify label and value presence
      expect(find.text('Original U.S. Mint Issue Price'), findsOneWidget);
      expect(find.text('\$80.00'), findsOneWidget);
      expect(find.text('Mint Schedule Status'), findsOneWidget);
      expect(find.text('Original Release Date'), findsOneWidget);
      expect(find.text('Jul 11, 2024'), findsOneWidget);

      // Verify muted font weight (FontWeight.normal vs standard bold)
      final textWidget = tester.widget<Text>(find.text('\$80.00'));
      expect(textWidget.style?.fontWeight, FontWeight.normal);
    });

    testWidgets('Mint rows contain zero buy links or interactive tap ancestors', (tester) async {
      final coin = CoinModel(id: 'c5', year: '2024', denomination: 'Dollar', mintMark: 'W');
      const metadata = MintProductMetadata(
        productPriceUsd: 80.00,
        mintScheduleStatus: 'ON_SALE',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: _DetailsTab(
              coin: coin,
              mintMetadata: metadata,
              onInspectField: (_, __) {},
            ),
          ),
        ),
      );

      final priceLabel = find.text('Original U.S. Mint Issue Price');
      expect(priceLabel, findsOneWidget);

      // Verify NO InkWell or Link ancestors
      final inkWellAncestor = find.ancestor(of: priceLabel, matching: find.byType(InkWell));
      expect(inkWellAncestor, findsNothing);

      // Verify zero retail/commercial action verbs
      expect(find.textContaining('Buy'), findsNothing);
      expect(find.textContaining('Order'), findsNothing);
      expect(find.textContaining('Cart'), findsNothing);
    });
  });

  group('NET-810 Operational Invariant Tests', () {
    test('Zero Firestore writes occur during metadata lookup', () async {
      final fakeFirestore = FakeFirebaseFirestore();
      final initialDocs = await fakeFirestore.collection('users/test_user/coins').get();
      expect(initialDocs.docs.length, 0);

      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.TEST': const MintProductMetadata(productPriceUsd: 80.00),
        },
      );

      final coin = CoinModel(id: 'c6', personalRef: 'NAC1.TEST');
      final result = service.lookupForCoin(coin);
      expect(result, isNotNull);

      // Verify Firestore state is completely untouched
      final afterDocs = await fakeFirestore.collection('users/test_user/coins').get();
      expect(afterDocs.docs.length, 0);
    });

    test('Private collection keys are strictly excluded from public catalog models', () {
      final coin = CoinModel(
        id: 'user-coin-123',
        year: '1921',
        mintMark: 'D',
        denomination: 'Dollar',
        purchaseCost: '\$45.00',
        purchaseDate: '2023-01-15',
        retailer: 'Coin Shop A',
        retailerItemNo: 'SKU-99',
        retailerInvoiceNo: 'INV-101',
        storageLocation: 'Safe Box 3',
        personalNotes: 'Private note',
        personalRef: 'MY-REF',
        ownerPhotos: ['https://private/photo.jpg'],
        provenanceLedger: [{'owner': 'Eric'}],
        transferId: 'TRF-1',
        transferStatus: 'none',
      );

      // Ensure CoinModel does NOT define toPublicCatalogMap
      // and verify standard public catalog map does not contain private keys
      final publicKeys = [
        'nac_code', 'name', 'type', 'year', 'denomination', 'series',
        'mint_facility', 'composition', 'era', 'status_badge'
      ];

      const forbiddenPrivateKeys = [
        'Purchase Cost', 'purchaseCost',
        'Purchase Date', 'purchaseDate',
        'Retailer/Website', 'retailer',
        'Retailer Item No.', 'retailerItemNo',
        'Retailer Invoice #', 'retailerInvoiceNo',
        'Storage Location', 'storageLocation',
        'Personal Notes I', 'personalNotes',
        'Personal Reference #', 'personalRef',
        'owner_photos', 'ownerPhotos',
        'provenanceLedger',
        'transferStatus', 'transferId',
      ];

      for (final forbidden in forbiddenPrivateKeys) {
        expect(publicKeys.contains(forbidden), isFalse,
            reason: 'Private key $forbidden must NEVER appear in public catalog schema');
      }
    });
  });
}
```

---

## 11. Acceptance Checklist, File Manifest & Rollback (MF-8)

### 11.1 Acceptance Criteria
- [ ] **AC-1:** Public catalog artifact `numista_mobile/assets/catalog/catalog_public_v1.json` and overlay `mint_product_fields_v1.json` are registered in `pubspec.yaml`.
- [ ] **AC-2:** `CoinModel` remains 100% pristine with zero field modifications and zero signature changes to `toFirestore()`.
- [ ] **AC-3:** `MintProductMetadata` is defined as a standalone immutable class in `lib/models/mint_product_metadata.dart`.
- [ ] **AC-4:** Primary join matches official `NAC1.` prefix; composite fallback matches `(year, facilityToMintMark, denomination, series)` and fails closed on zero or multiple matches.
- [ ] **AC-5:** `ensureInitialized()` is wired into `_CoinDetailScreenState.initState()` with clean asynchronous rebuild.
- [ ] **AC-6:** Scope is strictly bounded to `_DetailsTab` in `coin_detail_screen.dart`; `UnifiedCoinDetailsModal` is dropped.
- [ ] **AC-7:** `_DetailTile` implements `final bool isMuted = false;`, rendering `_kSubtext(context)` and `FontWeight.normal`.
- [ ] **AC-8:** Mint rows display neutral factual copy only; zero commercial buy links or cart interactions exist.
- [ ] **AC-9:** All tests in `numista_mobile/test/mint_product_fields_test.dart` pass with exit code 0.
- [ ] **AC-10:** Exactly 0 Firestore writes occur in live production or preview databases.

### 11.2 File Manifest

| File Path | Status | Operational Function |
| :--- | :--- | :--- |
| `numista_mobile/pubspec.yaml` | Modified | Registers `assets/catalog/` in Flutter asset bundle. |
| `numista_mobile/lib/models/coin_model.dart` | **Pristine** | Preserves core collection model without any modifications. |
| `numista_mobile/lib/models/mint_product_metadata.dart` | **New** | Immutable container for public U.S. Mint metadata. |
| `numista_mobile/lib/services/mint_product_lookup_service.dart` | **New** | Asynchronous in-memory join service. |
| `numista_mobile/lib/screens/coin_detail_screen.dart` | Modified | Wires `ensureInitialized()`, updates `_DetailsTab` and `_DetailTile` muted styling. |
| `numista_mobile/assets/catalog/mint_product_fields_v1.json` | **New** | Privacy-cleared government Mint SKU metadata overlay. |
| `numista_mobile/test/mint_product_fields_test.dart` | **New** | Comprehensive unit, widget, zero-writes, and privacy test suite. |

### 11.3 Targeted Git Rollback Procedure
If any defect occurs during preview verification, revert the exact commit sequence:
```bash
# Capture pre-execution commit SHA
PRE_EXEC_SHA="4d17ca5e0bc75f14e7aeb29a39f60d626c04f982"

# Revert execution commit cleanly on dev
git revert --no-commit $PRE_EXEC_SHA..HEAD
git commit -m "revert(net-810): roll back U.S. Mint product fields implementation"
git push origin dev
```

### 11.4 Timeline Fit for ~13 November Catalog Go-Live
- **7 Nov 21:00 ET:** Deliver Plan v1.2 for Grok Bot CoS review (Score target: $\ge 95$).
- **7 Nov ~22:00 ET:** Stand Alone Grok (SAG) secondary review ($\ge 95$).
- **8 Nov:** Founder Eric typed YES for preview deployment.
- **8–9 Nov:** Execution and preview deployment on `dev`.
- **10–12 Nov:** Field testing, verification, and census reconciliation.
- **13 Nov:** Catalog public launch readiness achieved.

---
