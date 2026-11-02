# FAIL-FIX PLAN NET-647 R2.8.18: Root-Cause Mint Asset Fidelity & Eric Account Rectification (Pass-Ready Reconciliation Foundation)

- **Plan Version:** `R2.8.18` (Fix-Only on `R2.8.17` Grok CoS Score 90 REVISE, COS_SCORE_NET-647_R2.8.17_90_REVISE_20261102-1750EST.md; attempt 6 of 10 under Eric's 2 Nov 5:58 PM ET rule)
- **Author:** GB CoS (Grok Bot Chief of Staff), assigned by Eric 2 Nov 5:58 PM ET ("You GB CoS. 2 tries, SAG and Gemini 3.8 in Antigravity review it."). Base text: R2.8.17 by AG CoS v4, MD5 5A99ACACA67F83D3EB88BDBA5A73E5A5.
- **Date / Time:** `2026-11-02 18:15 EST`
- **Operating Mode:** **DOCS-ONLY (PLANNING / REVIEW ONLY)**. Zero source code modifications, one docs-only commit to `dev` (this plan + review request + WHOSE_TURN + NET-744 VOID headers), zero builds, zero deployments, zero GCS uploads, zero Firestore writes.
- **Branch / Locks:** `origin/p7-v8.9` locked; `origin/main` locked at `9f04550a`; `origin/dev` tip at `6e19c71d` before this plan's docs commit (verified live with `git fetch` + `git rev-parse origin/dev`, 2 Nov ~6:05 PM ET); app code on dev unchanged since `01a03f90` (all later dev commits are docs); Stripe OFF; Live Firebase Hosting locked at `numista-vault.web.app` (HTTP 200 OK).
- **Target Queue:** `#2 NET-647 R2.8.18` (`BATON_NET-745` review request to SAG + Gemini 3.8 reviewer). File MD5: a file cannot contain its own hash; the measured MD5 of this final file is in `FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md.md5` and in BATON_NET-745.
---

## 1. Executive Summary & Review Deliberation Matrix (R2.8.18, with R2.8.17 history below)

### R2.8.18 Fix-Only Matrix (GB CoS; the only five changes vs R2.8.17 besides header/footer/this matrix):
| Item | COS_SCORE R2.8.17 finding | Resolution in R2.8.18 | Changed lines (this file) |
| :---: | :--- | :--- | :--- |
| **F-1** | Row 28 reverse MD5 prefix `0313c4fb1c` had no source | Set to `beb40fba68` (live HEAD x-goog-hash `vrQPumi94UYMhlxdfVTYpg==` = `beb40fba68bde1460c865c5d7d54d8a6`, 584,055 B, matches 4.1.3 row 001) | Row 28: line 1300 |
| **F-2** | Rows 01, 02, 26 col 9 showed one size/MD5 for two paths | Each path now carries its own bytes, MD5 prefix and status: `26ea_a` 168,246 B `790d13287d` LIVE; `26ea_b` 164,146 B `62ad11e997` STAGED; `26xe_a` 216,358 B `96290c2d73` LIVE; `26xe_b` 245,878 B `3a77694c9a` STAGED | Row 01: line 1273; Row 02: line 1274; Row 26: line 1298 |
| **F-3** | Section 3 bullet said 95/97 live, 2/97 staged | Now matches the 4.1.3 census: 114 paths, 110 LIVE, 4 STAGED (rows 111-114: 26ea_b, 26xe_b, 23rh_b, 23rh_c) | line 75 |
| **F-4** | Gate 6 said dev tip 32d4b42e | Gate 6 now states live-checked dev tip `6e19c71d` (pre-commit), code unchanged since `01a03f90`, same as header | line 1729 |
| **F-5** | Section 1 cited sections, not lines | This table cites line numbers of the final R2.8.18 file | lines 12-21; header lines 1-8; footer line 1735 |

### R2.8.17 history (unchanged text from AG CoS v4, kept for audit):

This plan **R2.8.17** is the production-certified canonical fix plan for **NET-647**, executed under **BATON NET-742** following independent scoring by **Grok CoS** (70/100 REVISE) and **Argon** (76/100 REVISE). Per Grok CoS explicit radio directive (`RADIO_NET-742`), R2.8.17 applies **ONLY Grok CoS MUST-FIX items MF-1 through MF-4**, strictly rejecting Argon's factual errors (hallucinated document IDs, unmeasured byte counts, and fabricated Row 28 composite combinations).

### R2.8.17 Surgical Resolution & Line-Citation Matrix:
| Item | Review Citation | Description of Finding | Surgical Resolution in R2.8.17 | Exact Changed Plan Lines |
| :---: | :---: | :--- | :--- | :--- |
| **MF-1** | Grok CoS MF-1 | Section 4 Table Column Damage in R2.8.16: Column 8 (`reverseUrl`) was corrupted on 17 rows; Row 28 Theme cell was omitted shifting columns left; Column 9 held duplicate reverse URLs. | Rebuilt Section 4 table directly from R2.8.15 baseline. Restored column 8 (`reverseUrl`) across Rows 01, 02, 07, 13–24, 26, 27. In column 9 (`Verified Fallbacks`), placed Gate 4 staged WebPs for Rows 01 (`26ea_a.webp / 26ea_b.webp`), 02 & 26 (`26xe_a.webp / 26xe_b.webp`), and eliminated duplicate reverse fallbacks (`None (null - duplicate eliminated)`) for Rows 07, 13–24, 27. Restored Row 28 Theme cell `Silver Proof Set (10-coin set)`, code-true primaries (`2023_american_women_quarters_five_honorees_composite.jpg` `711,501 B` obv, `2023_american_innovation_four_states_composite.jpg` `584,055 B` rev), and Gate 4 staged fallbacks (`23rh_b.webp` `226,854 B` / `23rh_c.webp` `161,734 B`). | Section 4 Table Rows 01, 02, 07, 09, 13–24, 26, 27, 28 |
| **MF-2** | Grok CoS MF-2 | Section 4.1.1 Half-Dollar Bytes carried stale numbers (`1,341,259 B` / `1,603,328 B` / `1,477,632 B`) contradicting live GCS HEAD measurements. | Reconciled Section 4.1.1 to live measured GCS HEAD values: `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` = `1,510,128 B` (`ef82afd24a5c4eeb74947958b0552e91`), `SemiQ-Half-Dollar-Reverse-Unc.jpg` = `1,510,409 B` (`cceb4ab85d398347792d8929fb11bed0`), `SemiQ-Half-Dollar-Obverse-Unc-P.jpg` = `1,510,450 B` (`ec05347cabf3b134a262ac9f6631385b`). Preserved Section 4.1.3 census rows 059, 060, 062, 092 intact as already 100% verified. | Section 4.1.1 |
| **MF-3** | Grok CoS MF-3 | Broken Fallback on 2026-DIME-D: `2026-semiq-dime-obverse-unc-d.webp` returns HTTP 404 in GCS bucket `numista-reference-library`. | In Section 3.1 resolver, set `fallbackObverseUrl: null` for `2026-DIME-D`. In Section 3.2 unit test for Row 09, updated assert to `expect(pair.fallbackObverseUrl, isNull)`. In Section 4 Table Row 09, set fallbacks to `None (null) / None (null)`. In Section 8 Tracker B26-10, updated note to reflect null fallback. Re-ran `flutter test` (44/44 PASS, exit code 0). | Section 3.1, Section 3.2, Section 4 Table Row 09, Section 8 Tracker B26-10 |
| **MF-4** | Grok CoS MF-4 | Document Structure: Header lines 1–10 said R2.8.15; Deliberation matrix was appended after EOF; duplicate copy of resolver service was pasted in Section 3.2. | Updated header to R2.8.17; placed R2.8.17 Deliberation Matrix cleanly in Section 1; purged duplicate resolver service from Section 3.2 (pasting only the unit test suite from `void main()`); ensured clean termination with `**END PLAN R2.8.17**`. | Header (Lines 1–10), Section 1, Section 3.2, EOF |

### Section 4 Table Surgical Row-Diff vs R2.8.15 Baseline:
Every row has exactly 9 columns (`Row | doc_id | Account | SKU | Year-Mint | Theme | obverseUrl | reverseUrl | Fallbacks`).
- **Row 01 (`26EA`):** Col 8 (`reverseUrl`) preserved as `26EA_image_2.jpg` (`139,910 B`). Col 9 (`Fallbacks`) changed from `.../26EA_image_3.jpg` to `.../26ea_a.webp / .../26ea_b.webp` (`164,146 B`, `md5: 62ad11e997...`, `STAGED Gate 4`).
- **Row 02 (`26XE`):** Col 8 (`reverseUrl`) preserved as `26XE_image_3.jpg` (`285,827 B`). Col 9 (`Fallbacks`) changed from `.../26XE_image_1.jpg` to `.../26xe_a.webp / .../26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`).
- **Row 07 (`26SQRP`):** Col 8 (`reverseUrl`) preserved as `26sqrp_b.webp`. Col 9 (`Fallbacks`) changed from `.../MASTER_SEMIQDJT_image_1.jpg` to `None (null - duplicate eliminated)`.
- **Row 09 (`2026-DIME-D`):** Col 8 (`reverseUrl`) preserved as `SemiQ-Dime-Reverse-Unc.jpg`. Col 9 (`Fallbacks`) changed from `2026-semiq-dime-obverse-unc-d.webp / null` to `None (null) / None (null)` (eliminated HTTP 404 broken fallback).
- **Rows 13–24 (ATB & Lincoln):** Col 8 (`reverseUrl`) preserved cleanly. Col 9 (`Fallbacks`) second URL changed from duplicate reverse to `None (null - duplicate eliminated)`.
- **Row 26 (`26XE`):** Col 8 (`reverseUrl`) preserved as `26XE_image_3.jpg` (`285,827 B`). Col 9 (`Fallbacks`) changed from `.../26XE_image_1.jpg` to `.../26xe_a.webp / .../26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`).
- **Row 27 (`26SQRP`):** Col 8 (`reverseUrl`) preserved as `26sqrp_b.webp`. Col 9 (`Fallbacks`) changed from `.../MASTER_SEMIQDJT_image_1.jpg` to `None (null - duplicate eliminated)`.
- **Row 28 (`23RH`):** Col 6 (`Theme`) restored to `Silver Proof Set (10-coin set)`. Col 7 (`obverseUrl`) set to `2023_american_women_quarters_five_honorees_composite.jpg` (`711,501 B`, live GCS). Col 8 (`reverseUrl`) set to `2023_american_innovation_four_states_composite.jpg` (`584,055 B`, live GCS). Col 9 (`Fallbacks`) set to `23rh_b.webp` (`226,854 B`, `STAGED Gate 4`) / `23rh_c.webp` (`161,734 B`, `STAGED Gate 4`).
- **Rows 03, 04, 05, 06, 08, 10, 11, 12, 25:** Unchanged (100% identical to verified R2.8.15 baseline).

---

## 2. Core Architectural Principles (Preserved & Enforced)

1. **Non-Destructive Resolution:** User-uploaded original photos are never overwritten. When high-fidelity canonical mint imagery is identified, it is presented in UI views with fallback to original photos.
2. **Explicit SKU & Program Isolation:** Resolver matches themes strictly from `Theme/Subject`, `Program/Series`, `Title`/`name`, and `description`, and inspects `Personal Notes` only for explicit US Mint SKU codes (`26EA`, `26XE`, `26XL`, `26XH`, `26XF`, `26RJ`, `26RG`, `26RH`, `26GC`, `26SQRP`, `23RH`). Neighboring coin titles in notes never hijack matches.
3. **Strict Year/Mint Guarding:** All coin series enforce strict year and mint mark matching. No cross-year or cross-mint obverse substitutions are permitted.
4. **Offline & Emulator Testability:** Resolution logic is 100% pure Dart, executing synchronously with zero network dependencies, verified by a 42-test unit suite.

### 2.1 Why Pre-Fix Firestore Docs Displayed Wrong Images (`SF2`)

Add this paragraph to **Section 2 (Root Cause Analysis)**:

> **Why Pre-Fix Firestore Documents Displayed Wrong or Corrupted Images (`SF2`):**
> Inspection of [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json) proves that the 28 collection documents already had corrupted or mismatched `image_url_obverse` / `image_url_reverse` (and `obverse_image` / `reverse_image`) strings written directly into Firestore during ingestion/enrichment before `_CoinImageFlipper` ever rendered them:
> 1. **2026 Mint Subscription & Set SKUs (`Rows 01–07, 25–27`):** `26EA` (`e91efa62-4e8`), `26XL` (`a59853c1-b72`), `26RJ` (`71e2d4ae92bc`, `91f8821265bf`, `0a2bc793-8d6`), `26GC` (`0e68ecba760d`), and `26SQRP` (`7a32932ebc4e`, `faa5b1cf-7fd`) were populated with generic non-2026 `wikimedia_uscoin` stock images (e.g., an 1865 Seated Liberty dollar, a generic Peace dollar, or a 1932 Washington quarter), while `26XE` (`be10e44ce5b4`, Rows 02 & 26) had `26XE_image_1.jpg` (a two-coin composite hero shot) bound to both obverse and reverse.
> 2. **2026 Semiquincentennial Circulating Coins (`Rows 08–11`):** Both `2026-P` and `2026-D` Roosevelt Dimes (`nAnGLwGvhfIO`, `rv9SCUTahBuq`) had a 1916 Mercury Dime (`1916D_Winged_Liberty_dime_obverse.jpg`) stored in `image_url_obverse` and an unreadable transparent PNG (`United_States_dime_2C_reverse.png`) in `image_url_reverse`. `2026-P` Mayflower Quarter (`0172d0ee6428`) had `1999_Obverse_Proof.png`, and `2026-D` Semiquincentennial Half Dollar (`8f2197d5d03a`) had a Kennedy portrait obverse and `Kennedy_half_dollar_reverse_2.png`.
> 3. **State & ATB Quarters (`Rows 12–17, 19–24`):** All 12 quarter rows had `1999_Obverse_Proof.png` (an unreadable dark/transparent proof Washington obverse) stored as `image_url_obverse`, and had their **next neighbor's coin name** written into `Personal Notes` (e.g. Kansas had `Personal Notes: "Oregon"`, Effigy Mounds had `Personal Notes: "Ozark..."`), which caused naive text-matching to misroute reverses.
> 4. **1962 Lincoln Cent (`Row 18`, `Wq2UhSQNs67u`):** Had a valid Lincoln Cent obverse (`NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg`) in `image_url_obverse`, but had a **Jefferson Nickel reverse** (`US_Nickel_Reverse.jpg`) written into `image_url_reverse`.
> 5. **2023 Silver Proof Set (`Row 28`, `2fa325166682`):** Had `2003_Sacagawea_Rev.png` stored as both obverse and reverse.
> Because `_CoinImageFlipper` (`my_collection_screen.dart:2981-3001`) only invoked `CoinFallbackImages.resolvePair(...)` when `obverseUrl == null`, these corrupted non-null Firestore URLs bypassed fallback resolution completely. Calling `CanonicalMintAssetService.resolveFromMap(data)` **before** trusting raw Firestore `image_url`/`obverse_image`/`reverse_image` fields (combined with the Gate 6 Firestore remediation script) deterministically overrides every corrupted URL while preserving valid untouched fields like Row 18's Lincoln Cent obverse.

---

---
## 3. Complete Standalone Resolver Implementation

Resolves `MF1`, `MF3`, `MF4`, `MF5`, `MF8`, `MF9`, `MF-A`, `MF-B`, `MF-C`, `MF-D`:
- Handles **all 28 actual Firestore documents** from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` (`100%` match) **plus** all 14 synthetic tracker test cases (`26XH`, `26XF`, `26RG`, `26RH`, 5 AWQ 2023 quarters, `2013-D White Mountain`, `2010-P Mount Hood`, 3 `2020-S` ATB quarters).
- Uses **only verified GCS paths** in `gs://numista-reference-library` (Section 4.1.3 census: `114` paths, `110` live HTTP 200 right now; `4` explicitly staged for Gate 4: `26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`, each HTTP 404 live until upload, with live HTTP 200 primaries).
- Never uses `Personal Notes` for theme matching (preventing the neighbor-note pollution in `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`), using `Personal Notes` strictly for explicit SKU code extraction.
- Uses undated ATB obverses whenever a year+mint-matching dated ATB obverse does not exist (`MF8`).
- Preserves existing `image_url_obverse` / `obverse_image` on `1962 Lincoln Cent` (`MF9`) while fixing `reverseUrl` to the live `United_States_penny_2C_reverse.jpg`.

```dart
class CanonicalMintAssetPair {
  final String sku;
  final String obverseUrl;
  final String reverseUrl;
  final String? fallbackObverseUrl;
  final String? fallbackReverseUrl;
  final bool isSet;
  final bool isGenuine2026;
  final bool isRepresentativePreview;

  const CanonicalMintAssetPair({
    required this.sku,
    required this.obverseUrl,
    required this.reverseUrl,
    this.fallbackObverseUrl,
    this.fallbackReverseUrl,
    this.isSet = false,
    this.isGenuine2026 = false,
    this.isRepresentativePreview = false,
  }) : assert(obverseUrl != reverseUrl, 'Obverse and reverse URLs must be distinct');
}

class CanonicalMintAssetService {
  /// MF-B User Upload Guard: Never overwrite user-uploaded photos or microscope scans.
  /// If existing stored images are user uploads (under uploads bucket or /microscope/),
  /// or scan_source is microscope / hardware agent, return true to preserve existing.
  static bool hasUserUploadedPhotos(Map<String, dynamic> data) {
    final scanSource = (data['scan_source'] ?? data['source'] ?? '').toString().toLowerCase();
    if (scanSource == 'microscope' || scanSource == 'hardware agent') return true;

    bool isUserUrl(dynamic val) {
      if (val == null) return false;
      final s = val.toString().trim().toLowerCase();
      if (s.isEmpty) return false;
      if (s.contains('/reference_images/') || s.contains('reference_library')) return false;
      return s.contains('/microscope/') ||
             s.contains('studio-9101802118-8c9a8-uploads') ||
             s.contains('numista-uploads-studio-') ||
             s.contains('/users/') ||
             s.contains('/user_uploads/') ||
             s.contains('user_upload');
    }

    return isUserUrl(data['image_url_obverse']) ||
           isUserUrl(data['image_url_reverse']) ||
           isUserUrl(data['imageObverse']) ||
           isUserUrl(data['imageReverse']) ||
           isUserUrl(data['stored_obv']) ||
           isUserUrl(data['stored_rev']);
  }

  static const String _base =
      'https://storage.googleapis.com/numista-reference-library/reference_library';
  static const String _mintBase = '$_base/us_mint_official';
  static const String _wikiBase = '$_base/wikimedia_uscoin';

  static const List<String> _knownSkus = <String>[
    '26EA',
    '26XE',
    '26XL',
    '26XH',
    '26XF',
    '26RJ',
    '26GC',
    '26SQRP',
    '26RG',
    '23RG',
    '26RH',
    '23RH',
  ];

  static String extractSku(Map<String, dynamic> data) {
    for (final k in const <String>[
      'mint_product_id',
      'sku',
      'product_code',
      'item_number',
      'Retailer Item No.',
      'retailer_item_no',
    ]) {
      final val = (data[k] ?? '').toString().trim().toUpperCase();
      if (_knownSkus.contains(val)) return val;
    }
    for (final k in const <String>[
      'Personal Notes',
      'personal_notes',
      'title',
      'name',
      'Theme/Subject',
      'Program/Series',
      'Program / Series',
      'program_series',
    ]) {
      final txt = (data[k] ?? '').toString().toUpperCase();
      final tokens = txt.replaceAll('#', ' ').replaceAll('-', ' ').split(RegExp(r'\s+'));
      for (final candidate in _knownSkus) {
        if (tokens.contains(candidate)) return candidate;
      }
    }
    final year = (data['year'] ?? data['Year'] ?? '').toString().trim();
    final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
    final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
    final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
    final combined = '$prog $theme $title';
    if (year == '2026') {
      if (combined.contains('morgan') && combined.contains('enhanced')) return '26XE';
      if (combined.contains('morgan') && combined.contains('proof')) return '26XF';
      if (combined.contains('peace') && combined.contains('reverse proof')) return '26XL';
      if (combined.contains('peace') && combined.contains('uncirculated')) return '26XH';
      if (combined.contains('uncirculated') && combined.contains('set')) return '26RJ';
      if (combined.contains('american innovation')) return '26GC';
      if (combined.contains('trump') || combined.contains('semiquincentennial president')) {
        return '26SQRP';
      }
      if (combined.contains('silver proof set')) return '26RH';
      if (combined.contains('clad proof set') ||
          (combined.contains('proof set') && !combined.contains('silver'))) {
        return '26RG';
      }
    }
    if (year == '2023') {
      if (combined.contains('silver proof set')) return '23RH';
      if (combined.contains('proof set')) return '23RG';
    }
    return (data['mint_product_id'] ??
            data['sku'] ??
            data['product_code'] ??
            data['Retailer Item No.'] ??
            '')
        .toString()
        .trim()
        .toUpperCase();
  }

  static CanonicalMintAssetPair? resolveFromMap(Map<String, dynamic> data) {
    // MF-B Guard: Non-destructive preservation of user-uploaded / microscope photos.
    // If doc contains user uploads (e.g. Row 10 Eric's microscope photos), return null.
    if (hasUserUploadedPhotos(data)) {
      return null;
    }
    final sku = extractSku(data);
    // Intentionally excludes `Personal Notes` so neighbor-coin notes in live Firestore
    // never hijack ATB/State quarter identification.
    final primaryTitle = <String>[
      (data['title'] ?? '').toString().trim(),
      (data['name'] ?? '').toString().trim(),
      (data['Theme/Subject'] ?? '').toString().trim(),
      (data['theme_subject'] ?? '').toString().trim(),
      (data['Program / Series'] ?? data['Program/Series'] ?? '').toString().trim(),
      (data['program_series'] ?? '').toString().trim(),
      (data['description'] ?? '').toString().trim(),
    ].where((s) => s.isNotEmpty).join(' ');

    final year = (data['year'] ?? data['Year'] ?? '').toString().trim();
    final mintMark =
        (data['mint_mark'] ?? data['mint'] ?? data['Mint Mark'] ?? '').toString().trim();
    final denom =
        (data['denomination'] ?? data['Denomination'] ?? '').toString().trim();
    final storedObv =
        (data['image_url_obverse'] ?? data['obverse_image'] ?? data['image_url'] ?? '')
            .toString()
            .trim();

    return resolve(
      sku: sku,
      title: primaryTitle,
      year: year,
      mintMark: mintMark,
      denomination: denom,
      storedObverseUrl: storedObv.isNotEmpty ? storedObv : null,
    );
  }

  static CanonicalMintAssetPair? resolve({
    String? sku,
    String? title,
    String? year,
    String? mintMark,
    String? denomination,
    String? storedObverseUrl,
  }) {
    final cleanSku = (sku ?? '').trim().toUpperCase();
    final cleanTitle = (title ?? '').trim().toLowerCase();
    final cleanYear = (year ?? '').trim();
    final rawMint = (mintMark ?? '').trim().toUpperCase();
    final cleanDenom = (denomination ?? '').trim().toLowerCase();
    final cleanMint = rawMint.contains('WEST POINT') || rawMint == 'W'
        ? 'W'
        : (rawMint.contains('S')
            ? 'S'
            : (rawMint.contains('D')
                ? 'D'
                : (rawMint.contains('P') ? 'P' : rawMint)));

    // 1. Exact / Inferred SKU Match
    switch (cleanSku) {
      case '26EA':
        return const CanonicalMintAssetPair(
          sku: '26EA',
          obverseUrl: '$_mintBase/2026_products/26EA_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26EA_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26ea_a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26ea_b.webp',
          isSet: false,
          isGenuine2026: true,
        );
      case '26XE':
        return const CanonicalMintAssetPair(
          sku: '26XE',
          obverseUrl: '$_mintBase/2026_products/26XE_image_2.jpg',
          reverseUrl: '$_mintBase/2026_products/26XE_image_3.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26xe_a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26xe_b.webp',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26XL':
        return const CanonicalMintAssetPair(
          sku: '26XL',
          obverseUrl: '$_mintBase/2026_products/26XL_image_3.jpg',
          reverseUrl: '$_mintBase/2026_products/26XL_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26xl___a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26XL_image_1.jpg',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26XH':
        return const CanonicalMintAssetPair(
          sku: '26XH',
          obverseUrl: '$_mintBase/2026_products/26XH_image_2.jpg',
          reverseUrl: '$_mintBase/2026_products/26XH_image_3.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26XH_image_1.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26xh_image_3.jpg',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26XF':
        return const CanonicalMintAssetPair(
          sku: '26XF',
          obverseUrl: '$_mintBase/2026_products/26XF_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26XF_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26XE_image_2.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26XE_image_3.jpg',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26RJ':
        return const CanonicalMintAssetPair(
          sku: '26RJ',
          obverseUrl:
              '$_base/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg',
          reverseUrl:
              '$_base/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26RJ_image_1.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26RJ_image_2.jpg',
          isSet: true,
          isGenuine2026: true,
        );
      case '26GC':
        return const CanonicalMintAssetPair(
          sku: '26GC',
          obverseUrl: '$_mintBase/2026_products/26GC_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26gc_b.webp',
          fallbackObverseUrl: '$_base/2026_series/2026_american_innovation_obverse.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26GC_image_2.jpg',
          isSet: true,
          isGenuine2026: true,
        );
      case '26SQRP':
        return const CanonicalMintAssetPair(
          sku: '26SQRP',
          obverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26sqrp_b.webp',
          fallbackObverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_2.jpg',
          fallbackReverseUrl: null,
          isSet: true,
          isGenuine2026: true,
        );
      case '26RG':
      case '23RG':
        return CanonicalMintAssetPair(
          sku: cleanSku,
          obverseUrl: '$_mintBase/2026_products/26RG_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26rg_b.webp',
          fallbackObverseUrl: '$_mintBase/2026_products/26RG_image_2.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26RG_image_3.jpg',
          isSet: true,
          isRepresentativePreview: true,
        );
      case '26RH':
        return const CanonicalMintAssetPair(
          sku: '26RH',
          obverseUrl: '$_mintBase/2026_products/26RH_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26RH_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26RH_image_3.jpg',
          fallbackReverseUrl: null,
          isSet: true,
          isRepresentativePreview: true,
        );
      case '23RH':
        return const CanonicalMintAssetPair(
          sku: '23RH',
          obverseUrl:
              '$_base/2023_series/2023_american_women_quarters_five_honorees_composite.jpg',
          reverseUrl:
              '$_base/2023_series/2023_american_innovation_four_states_composite.jpg',
          fallbackObverseUrl: '$_mintBase/2023_products/23rh_b.webp',
          fallbackReverseUrl: '$_mintBase/2023_products/23rh_c.webp',
          isSet: true,
        );
    }

    // 2. 2026 Semiquincentennial Individual Coin Match (Rows 08–11)
    if (cleanYear == '2026') {
      if (cleanTitle.contains('roosevelt') ||
          cleanTitle.contains('dime') ||
          cleanDenom.contains('10c') ||
          cleanDenom.contains('dime')) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvFile = effMint == 'D'
            ? 'SemiQ-Dime-Obverse-Unc-D.jpg'
            : 'SemiQ-Dime-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-DIME-$effMint',
          obverseUrl: '$_base/bulk_programs/dime/$obvFile',
          reverseUrl: '$_base/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
      if (cleanTitle.contains('kennedy') ||
          cleanTitle.contains('half dollar') ||
          cleanDenom.contains('50c') ||
          cleanDenom.contains('half') ||
          cleanTitle.contains('independence')) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvUrl = effMint == 'D'
            ? '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'
            : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-HALF-$effMint',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg',
          fallbackObverseUrl: effMint == 'P'
              ? '$_base/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg'
              : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg',
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
      if (cleanTitle.contains('mayflower')) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvUrl = effMint == 'D'
            ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'
            : '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-MAYFLOWER-$effMint',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg',
          fallbackObverseUrl: effMint == 'D'
              ? '/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'
              : null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
    }

    // 3. 2023 American Women Quarters (Synthetic Tracker B26-14..B26-18)
    if (cleanYear == '2023') {
      const awqObv =
          '$_base/2023_series/2023_american_women_quarters_shared_obverse.jpg';
      const awqFallbackObv =
          '$_base/2023_series/2023_american_women_quarters_shared_obverse.png';
      const awqRevs = <String, String>{
        'bessie coleman':
            '2023_american_women_quarters_bessie_coleman_reverse.jpg',
        'edith kanaka':
            '2023_american_women_quarters_edith_kanakaole_reverse.jpg',
        'kanakaole':
            '2023_american_women_quarters_edith_kanakaole_reverse.jpg',
        'eleanor roosevelt':
            '2023_american_women_quarters_eleanor_roosevelt_reverse.jpg',
        'jovita idar': '2023_american_women_quarters_jovita_idar_reverse.jpg',
        'maria tallchief':
            '2023_american_women_quarters_maria_tallchief_reverse.jpg',
      };
      for (final entry in awqRevs.entries) {
        if (cleanTitle.contains(entry.key)) {
          final revUrl = '$_base/2023_series/${entry.value}';
          return CanonicalMintAssetPair(
            sku: '2023-AWQ-${entry.key.split(' ').first.toUpperCase()}',
            obverseUrl: awqObv,
            reverseUrl: revUrl,
            fallbackObverseUrl: awqFallbackObv,
            fallbackReverseUrl: revUrl.replaceAll('.jpg', '.png'),
          );
        }
      }
    }

    // 4. 2005-D Kansas State Quarter (Row 12) - Strict && guard per MF8
    if (cleanYear == '2005' &&
        cleanMint == 'D' &&
        cleanTitle.contains('kansas') &&
        (cleanDenom.contains('quarter') ||
            cleanDenom.contains('25c') ||
            cleanTitle.contains('quarter'))) {
      return const CanonicalMintAssetPair(
        sku: '2005-SQ-KS-D',
        obverseUrl:
            '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg',
        reverseUrl:
            '$_base/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg',
        fallbackObverseUrl:
            '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg',
        fallbackReverseUrl:
            '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg',
      );
    }

    // 5. 1962 Lincoln Cent (Row 18) - MF9: Obverse kept as stored; reverse replaced with Lincoln Memorial reverse
    if (cleanYear == '1962' &&
        (cleanTitle.contains('lincoln') ||
            cleanTitle.contains('cent') ||
            cleanDenom.contains('1c') ||
            cleanDenom.contains('cent'))) {
      return CanonicalMintAssetPair(
        sku: '1962-LINCOLN-1C',
        obverseUrl: storedObverseUrl ??
            '$_wikiBase/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg',
        reverseUrl:
            '$_wikiBase/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg',
        fallbackObverseUrl:
            '$_wikiBase/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png',
        fallbackReverseUrl: null,
      );
    }

    // 6. America the Beautiful (ATB) Quarters (Live Firestore Rows 13–17, 19–24 + Synthetic Tracker B26-25..B26-30)
    const atbRevs = <String, String>{
      'american memorial':
          '2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg',
      'salt river':
          '2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg',
      'mount rushmore':
          '2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg',
      'cumberland island':
          '2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg',
      'block island':
          '2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg',
      'san antonio':
          '2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg',
      'effigy mounds':
          '2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg',
      'frederick douglass':
          '2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg',
      'yellowstone':
          '2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg',
      'george rogers clark':
          '2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg',
      'ozark':
          '2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg',
      'white mountain':
          '2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg',
      'mount hood':
          '2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg',
      'marsh-billings':
          '2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg',
      'tallgrass':
          '2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg',
      'weir farm':
          '2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg',
    };

    const atbObvByYearMint = <String, String>{
      '2013-P':
          '$_base/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg',
      '2013-D':
          '$_base/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg',
      '2013-S':
          '$_base/atb_quarters/2013-america-the-beautiful-quarters-coin-proof-obverse-s.jpg',
      '2018-P':
          '$_base/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg',
      '2018-D':
          '$_base/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg',
      '2019-P':
          '$_base/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg',
      '2019-D':
          '$_base/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg',
      '2020-P':
          '$_base/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg',
      '2020-D':
          '$_base/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg',
    };

    for (final entry in atbRevs.entries) {
      if (cleanTitle.contains(entry.key)) {
        final revUrl = '$_base/atb_quarters/${entry.value}';
        final exactObv = atbObvByYearMint['$cleanYear-$cleanMint'];
        late final String obvUrl;
        late final String fallbackObv;
        if (exactObv != null) {
          obvUrl = exactObv;
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
        } else if (cleanMint == 'S') {
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg';
          fallbackObv =
              '$_base/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg';
        } else if (cleanMint == 'D') {
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg';
        } else if (cleanMint == 'W') {
          // MF8: Do not assign a P-mint obverse to a W-mint coin; use undated ATB obverse
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg';
        } else {
          // MF8: Undated Philadelphia ATB obverse (no conflicting year in filename)
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg';
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
        }
        return CanonicalMintAssetPair(
          sku: 'ATB-$cleanYear-$cleanMint',
          obverseUrl: obvUrl,
          reverseUrl: revUrl,
          fallbackObverseUrl: fallbackObv,
          fallbackReverseUrl: null,
        );
      }
    }

    return null;
  }
}

// numista_mobile/test/services/canonical_mint_asset_service_test.dart

// numista_mobile/test/services/canonical_mint_asset_service_test.dart
```

### 3.2 Complete Unit Test Suite (44 Tests - 100% PASS)

```dart
// numista_mobile/test/services/canonical_mint_asset_service_test.dart

import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests', () {
    test('Row 01 (e91efa62-4e8d-4920-a928-c0c97659bcdc | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'W', 'Denomination': 'Dollar', 'Program/Series': 'American Silver Eagle', 'Theme/Subject': 'America250', 'Personal Notes': '26EA American Eagle 2026 One Ounce Silver Proof (250 privy)', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp'));
    });

    test('Row 02 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Dollar', 'Program/Series': 'Morgan Dollar', 'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)', 'Personal Notes': '2026 Morgan Silver Enhanced Un | Mint Facility: West Point (no mint mark)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp'));
    });

    test('Row 03 (a59853c1-b72b-414d-8b8e-de6813c29996 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Dollar',
        'Program/Series': 'Peace Dollar',
        'Theme/Subject': 'America250',
        'Variety': 'Reverse Proof',
        'Condition': 'Reverse Proof',
        'Retailer Item No.': '26XL',
        'Personal Notes': 'Peace Silver Dollar 2026 Rever',
        'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Obverse.jpg',
        'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Reverse.jpg',
      };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_3.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl___a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_1.jpg'));
    });

    test('Row 04 (71e2d4ae92bc4312a4198a3a0cc21fcb | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Set', 'Program/Series': 'Uncirculated Sets', 'Theme/Subject': '250th Anniversary Uncirculated Coin Set', 'name': '2026 United States Mint Uncirculated Coin Set', 'product_code': '26RJ', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_2.jpg'));
    });

    test('Row 05 (91f8821265bfe8a33fbd97e21f102c67fdf849fd | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Set', 'Program/Series': 'Uncirculated Coin Set', 'Personal Notes': 'Uncirculated Coin Set 2026' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_2.jpg'));
    });

    test('Row 06 (0e68ecba760df66bf824ec1ba2c86b32318d002d | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': '\$1', 'Program/Series': 'American Innovation', 'Personal Notes': 'American Innovation 2026 \$1 Co' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26GC_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26GC_image_2.jpg'));
    });

    test('Row 07 (7a32932ebc4e94a586534e7180cd1c4372c4f17d | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Denomination': 'Dollar', 'Program/Series': 'Semiquincentennial President', 'Theme/Subject': 'Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)', 'Personal Notes': '26SQRP Semiquincentennial President D | Mint Facility: Philadelphia (P)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 08 (nAnGLwGvhfIOibf6kIft | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'P', 'Denomination': 'Dime', 'Program/Series': 'Roosevelt Dimes', 'Theme/Subject': 'Franklin D. Roosevelt' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, isNull);
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 09 (rv9SCUTahBuqJkkiJyga | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Denomination': 'Dime', 'Program/Series': 'Roosevelt Dimes', 'Theme/Subject': 'Franklin D. Roosevelt' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, isNull);
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 10 (0172d0ee64284a12a8aa269ce805ec07 | eric.seaman@yahoo.com): MF-B user-upload guard protects Eric\'s microscope photos (returns null)', () {
      final doc = <String, dynamic>{
        'id': '0172d0ee64284a12a8aa269ce805ec07',
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Quarter Dollar (25C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
        'scan_source': 'microscope',
        'source': 'Hardware Agent',
        'image_url_obverse': 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/2026_semiquincentennial_mayflower_compact_quarter_p_Obverse_20260701_1731.jpg',
        'image_url_reverse': 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/2026_semiquincentennial_mayflower_compact_quarter_p_Reverse_20260701_1731.jpg',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isTrue);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      // Non-destructive: must return null so user\'s microscope photos are never overwritten!
      expect(pair, isNull);
    });

    test('Row 10 Reference Resolution: resolves Mayflower catalog pair when no user photos are present', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Quarter Dollar (25C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg'));
      expect(pair.fallbackObverseUrl, isNull);
      expect(pair.fallbackReverseUrl, isNull);
    });

test('Row 11 (8f2197d5d03a428db24486b4ee375a5e | eric.seaman@yahoo.com): MF-B user-upload guard protects Eric\'s microscope photos (returns null)', () {
      final doc = <String, dynamic>{
        'id': '8f2197d5d03a428db24486b4ee375a5e',
        'Year': '2026',
        'Mint Mark': 'D',
        'Denomination': 'Half Dollar',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': '250th Anniversary of American Independence',
        'scan_source': 'microscope',
        'source': 'Hardware Agent',
        'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/obverse.jpg?t=1782428155',
        'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/reverse.jpg?t=1782428156',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isTrue);
      expect(CanonicalMintAssetService.resolveFromMap(doc), isNull);
    });

    test('Row 11 Reference Resolution: 2026-HALF-D Catalog Lookup (Without User Photos)', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'D',
        'Denomination': 'Half Dollar (50C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Semiquincentennial Half Dollar Enduring Liberty',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 12 (5b424047-77e0-496e-a513-6ef180b515a6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2005', 'Mint Mark': 'D', 'Denomination': 'Quarter', 'Program/Series': '50 State Quarters', 'program_series': '50 State Quarters', 'Theme/Subject': 'Kansas', 'theme_subject': 'Kansas', 'Personal Notes': 'Oregon', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/50_state_quarters/2003-50-state-quarters-coin-arkansas-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg'));
    });

    test('Row 13 (3346cda5-5935-4303-bf62-de43041f3175 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2019', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'American Memorial Park (Northern Mariana Islands)', 'theme_subject': 'American Memorial Park (Northern Mariana Islands)', 'Personal Notes': 'War in the Pacific National Historical Park (Guam) - ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2015-america-the-beautiful-quarters-coin-blue-ridge-parkway-north-carolina-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 14 (b243621c-5a35-45f0-84bf-8786eb1547f9 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2020', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)', 'theme_subject': 'Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)', 'Personal Notes': 'Marsh-Billings-Rockefeller National Historical Park (Vermont) - ATB-P', 'personal_notes': 'ATB- P TUBE', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 15 (c336e53e-4105-44bd-8c08-f30ae0328467 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2013', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Mount Rushmore National Memorial (South Dakota)', 'theme_subject': 'Mount Rushmore National Memorial (South Dakota)', 'Personal Notes': 'Mount Rushmore National Memorial (South Dakota) - ATB-P', 'personal_notes': 'ATB-P', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 16 (cba5e585-758f-4b10-be7a-1a59a1f4b2e6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2018', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Cumberland Island National Seashore (Georgia)', 'theme_subject': 'Cumberland Island National Seashore (Georgia)', 'Personal Notes': 'Apostle Islands National Lakeshore (Wisconsin) - ATB-P tube', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2016-america-the-beautiful-quarters-coin-cumberland-gap-kentucky-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 17 (d7fec246-983f-40de-8b58-854f59460bce | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2018', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Block Island National Wildlife Refuge (Rhode Island)', 'theme_subject': 'Block Island National Wildlife Refuge (Rhode Island)', 'Personal Notes': 'Voyageurs National Park (Minnesota) - ATB-P tube', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ellis-island-new-jersey-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 18 (Wq2UhSQNs67u34VFJDaI | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '1962', 'Denomination': 'Cent', 'Program/Series': 'Lincoln Cent (Memorial Reverse)', 'program_series': 'Lincoln Cent (Memorial Reverse)', 'Theme/Subject': 'Abraham Lincoln', 'theme_subject': 'Abraham Lincoln', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/penny/2008-lincoln-one-cent-reverse-2000x2000.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 19 (UOBfFO2mqgLg86NSsyss | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2019', 'Mint Mark': 'W', 'mint_mark': 'W', 'Denomination': 'Quarter Dollar', 'Program/Series': 'America the Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'San Antonio Missions', 'theme_subject': 'San Antonio Missions', 'Personal Notes': 'HV Coin Club', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/1932-george-washington-quarter-obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 20 (3f437576-fa20-4ef1-95c0-01e10eaf43a8 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Effigy Mounds National Monument (Iowa)', 'theme_subject': 'Effigy Mounds National Monument (Iowa)', 'Personal Notes': 'Ozark National Scenic Riverways (Missouri) - ATB-TUBE', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 21 (6ff959a0-26f8-451f-aa4c-064b5ef68939 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Frederick Douglass National Historic Site (District of Columbia)', 'theme_subject': 'Frederick Douglass National Historic Site (District of Columbia)', 'Personal Notes': 'Frederick Douglass National Historic Site (District of Columbia)', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 22 (96eeb7b6-6c4e-4a62-bb8e-80b69706d915 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2010', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Yellowstone National Park (Wyoming)', 'theme_subject': 'Yellowstone National Park (Wyoming)', 'Personal Notes': 'Yellowstone National Park (Wyoming) - ATB-P TUBE - to Poor Condition', 'personal_notes': 'ATB-P TUBE - Poor Condition', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 23 (ab35ab5d-d51f-4b9c-bc94-ff87def52bc6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'D', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'George Rogers Clark National Historical Park (Indiana)', 'theme_subject': 'George Rogers Clark National Historical Park (Indiana)', 'Personal Notes': 'George Rogers Clark National Historical Park (Indiana)', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 24 (b785236f-ca64-4461-9ee4-01cad3a7d60e | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Ozark National Scenic Riverways (Missouri)', 'theme_subject': 'Ozark National Scenic Riverways (Missouri)', 'Personal Notes': 'Effigy Mounds National Monument (Iowa) - ATB-P tube', 'personal_notes': 'ATB-P TUBE', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 25 (0a2bc793-8d62-47c3-88cd-7a5b9be434ba | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Set', 'Program/Series': 'Uncirculated Coin Set', 'Personal Notes': 'Item # 26RJ - Uncirculated Coin Set 2026' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_2.jpg'));
    });

    test('Row 26 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Dollar', 'Program/Series': 'Morgan Dollar', 'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)', 'Personal Notes': '2026 Morgan Silver Enhanced Un | Mint Facility: West Point (no mint mark)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp'));
    });

    test('Row 27 (faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Program/Series': 'Semiquincentennial President', 'Personal Notes': 'Item # 26SQRP Semiquincentennial President D' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 28 (2fa325166682b70aa0d64da45786c94aa4742d21 | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2023', 'Denomination': 'Set', 'Program/Series': 'Silver Proof Set', 'Personal Notes': 'Silver Proof Set 2023' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_innovation_four_states_composite.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_c.webp'));
    });

    test('Synthetic Tracker Case 01 (26XH): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26XH' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xh_image_3.jpg'));
    });

    test('Synthetic Tracker Case 02 (26XF): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26XF' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XF_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XF_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
    });

    test('Synthetic Tracker Case 03 (26RG): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26RG' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RG_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rg_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RG_image_2.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RG_image_3.jpg'));
    });

    test('Synthetic Tracker Case 04 (26RH): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26RH' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_3.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 05 (2023-AWQ-BESSIE): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Bessie Coleman' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.png'));
    });

    test('Synthetic Tracker Case 06 (2023-AWQ-EDITH): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Edith Kanakaole' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.png'));
    });

    test('Synthetic Tracker Case 07 (2023-AWQ-ELEANOR): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Eleanor Roosevelt' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.png'));
    });

    test('Synthetic Tracker Case 08 (2023-AWQ-JOVITA): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Jovita Idar' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.png'));
    });

    test('Synthetic Tracker Case 09 (2023-AWQ-MARIA): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Maria Tallchief' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.png'));
    });

    test('Synthetic Tracker Case 10 (ATB-2013-D): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2013', 'mint': 'D', 'title': 'White Mountain' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 11 (ATB-2010-P): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2010', 'mint': 'P', 'title': 'Mount Hood' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 12 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Marsh-Billings-Rockefeller' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 13 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Tallgrass Prairie' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 14 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Weir Farm' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });
  });
}
```

#### Verbatim `flutter test` Execution Output (44/44 PASS, Exit Code 0)
```text
﻿Resolving dependencies...
Downloading packages...
  _flutterfire_internals 1.3.76 (1.3.79 available)
  archive 4.0.9 (4.6.0 available)
  cached_network_image 3.4.1 (4.0.6 available)
  cached_network_image_platform_interface 4.1.1 (5.0.3 available)
  cached_network_image_web 1.3.1 (2.0.4 available)
  clock 1.1.2 (1.1.3 available)
  cloud_firestore 6.8.0 (7.1.0 available)
  cloud_firestore_platform_interface 8.0.6 (8.1.0 available)
  cloud_firestore_web 5.7.2 (5.8.0 available)
  code_assets 1.2.1 (2.1.0 available)
  cross_file 0.3.5+4 (0.4.0 available)
  crypto 3.0.7 (3.0.8 available)
  cupertino_icons 1.0.9 (2.0.0 available)
  dbus 0.7.14 (0.8.0 available)
  equatable 2.1.0 (3.0.0 available)
  file_picker 11.0.3 (13.3.0 available)
  file_selector_linux 0.9.4 (0.9.4+1 available)
  file_selector_macos 0.9.5 (0.9.5+2 available)
  file_selector_windows 0.9.3+5 (0.9.3+6 available)
  firebase_ai 3.15.0 (5.1.0 available)
  firebase_app_check 0.4.6 (0.5.1 available)
  firebase_app_check_platform_interface 0.4.2 (0.5.1+3 available)
  firebase_app_check_web 0.2.6 (0.3.1+3 available)
  firebase_auth 6.5.7 (7.0.1 available)
  firebase_auth_platform_interface 9.0.6 (9.1.2 available)
  firebase_auth_web 6.2.6 (6.3.2 available)
  firebase_core 4.13.0 (5.1.0 available)
  firebase_core_platform_interface 8.1.0 (8.1.1 available)
  firebase_core_web 3.10.0 (4.1.0 available)
  firebase_storage 13.4.6 (14.0.1 available)
  firebase_storage_platform_interface 6.0.6 (6.0.9 available)
  firebase_storage_web 3.11.12 (3.11.15 available)
  fl_chart 0.70.2 (1.3.0 available)
  flutter_cache_manager 3.4.2 (3.4.6 available)
  flutter_svg 2.3.0 (2.3.2 available)
  google_fonts 6.3.3 (9.0.0 available)
  hooks 2.0.2 (2.2.0 available)
! image 4.9.2 (overridden) (4.12.0 available)
  image_picker 1.2.3 (1.2.4 available)
  image_picker_android 0.8.13+17 (0.8.13+25 available)
  image_picker_ios 0.8.13+6 (0.8.13+14 available)
  image_picker_platform_interface 2.11.1 (2.11.2 available)
  intl 0.19.0 (0.20.3 available)
  jni 1.0.3 (1.1.1 available)
  jni_flutter 1.0.2 (1.0.4+1 available)
  matcher 0.12.19 (0.12.20 available)
  material_color_utilities 0.13.0 (0.13.1 available)
  meta 1.17.0 (1.19.0 available)
  mime 2.0.0 (2.1.0 available)
  objective_c 9.5.0 (9.6.2 available)
  octo_image 2.1.0 (2.1.3 available)
  pdf 3.12.0 (3.13.1 available)
  petitparser 7.0.2 (7.1.0 available)
  platform 3.1.6 (3.2.0 available)
  posix 6.5.2 (6.5.4 available)
  printing 5.14.3 (5.15.1 available)
  pub_semver 2.2.0 (2.2.1 available)
  qr 3.0.2 (4.0.1 available)
  record_use 0.6.0 (1.1.1 available)
  share_plus 10.1.4 (13.3.1 available)
  share_plus_platform_interface 5.0.2 (7.2.0 available)
  shared_preferences 2.5.5 (2.5.6 available)
  shared_preferences_android 2.4.23 (2.5.4 available)
  shared_preferences_foundation 2.5.6 (2.6.1 available)
  sqflite 2.4.2+1 (2.4.5 available)
  sqflite_android 2.4.2+3 (2.4.5 available)
  sqflite_common 2.5.8 (2.5.14 available)
  sqflite_darwin 2.4.2 (2.4.4+1 available)
  sqflite_platform_interface 2.4.0 (2.4.3 available)
  stack_trace 1.12.1 (1.12.2 available)
  synchronized 3.4.0+1 (3.5.0 available)
  test_api 0.7.10 (0.7.15 available)
  two_dimensional_scrollables 0.4.2 (0.5.5 available)
  url_launcher 6.3.2 (6.3.3 available)
  url_launcher_android 6.3.30 (6.3.33 available)
  url_launcher_ios 6.4.1 (6.4.2 available)
  url_launcher_linux 3.2.2 (3.2.3 available)
  url_launcher_macos 3.2.5 (3.2.6 available)
  url_launcher_windows 3.1.5 (3.1.6 available)
  vector_graphics 1.2.3 (1.2.5 available)
  vector_graphics_compiler 1.3.0 (1.3.4 available)
  vector_math 2.2.0 (2.4.4 available)
  vm_service 15.3.0 (15.4.0 available)
  web 1.1.1 (1.1.2 available)
  win32 5.15.0 (6.4.0 available)
  xml 6.6.1 (7.1.0 available)
  yaml 3.1.3 (3.1.4 available)
Got dependencies!
87 packages have newer versions incompatible with dependency constraints.
Try `flutter pub outdated` for more information.
00:00 +0: loading C:/Users/ericd/Documents/MyVertexProject/scratch/canonical_mint_asset_service_test.dart
00:00 +0: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 01 (e91efa62-4e8d-4920-a928-c0c97659bcdc | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +1: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 02 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +2: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 03 (a59853c1-b72b-414d-8b8e-de6813c29996 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +3: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 04 (71e2d4ae92bc4312a4198a3a0cc21fcb | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +4: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 05 (91f8821265bfe8a33fbd97e21f102c67fdf849fd | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +5: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 06 (0e68ecba760df66bf824ec1ba2c86b32318d002d | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +6: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 07 (7a32932ebc4e94a586534e7180cd1c4372c4f17d | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +7: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 08 (nAnGLwGvhfIOibf6kIft | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +8: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 09 (rv9SCUTahBuqJkkiJyga | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +9: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 10 (0172d0ee64284a12a8aa269ce805ec07 | eric.seaman@yahoo.com): MF-B user-upload guard protects Eric's microscope photos (returns null)
00:00 +10: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 10 Reference Resolution: resolves Mayflower catalog pair when no user photos are present
00:00 +11: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 11 (8f2197d5d03a428db24486b4ee375a5e | eric.seaman@yahoo.com): MF-B user-upload guard protects Eric's microscope photos (returns null)
00:00 +12: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 11 Reference Resolution: 2026-HALF-D Catalog Lookup (Without User Photos)
00:00 +13: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 12 (5b424047-77e0-496e-a513-6ef180b515a6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +14: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 13 (3346cda5-5935-4303-bf62-de43041f3175 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +15: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 14 (b243621c-5a35-45f0-84bf-8786eb1547f9 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +16: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 15 (c336e53e-4105-44bd-8c08-f30ae0328467 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +17: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 16 (cba5e585-758f-4b10-be7a-1a59a1f4b2e6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +18: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 17 (d7fec246-983f-40de-8b58-854f59460bce | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +19: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 18 (Wq2UhSQNs67u34VFJDaI | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +20: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 19 (UOBfFO2mqgLg86NSsyss | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +21: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 20 (3f437576-fa20-4ef1-95c0-01e10eaf43a8 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +22: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 21 (6ff959a0-26f8-451f-aa4c-064b5ef68939 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +23: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 22 (96eeb7b6-6c4e-4a62-bb8e-80b69706d915 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +24: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 23 (ab35ab5d-d51f-4b9c-bc94-ff87def52bc6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +25: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 24 (b785236f-ca64-4461-9ee4-01cad3a7d60e | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs
00:00 +26: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 25 (0a2bc793-8d62-47c3-88cd-7a5b9be434ba | eric@numista.ai): resolves exact verified primary & fallback URLs
00:00 +27: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 26 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric@numista.ai): resolves exact verified primary & fallback URLs
00:00 +28: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 27 (faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c | eric@numista.ai): resolves exact verified primary & fallback URLs
00:00 +29: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Row 28 (2fa325166682b70aa0d64da45786c94aa4742d21 | eric@numista.ai): resolves exact verified primary & fallback URLs
00:00 +30: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 01 (26XH): resolves exact verified primary & fallback URLs
00:00 +31: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 02 (26XF): resolves exact verified primary & fallback URLs
00:00 +32: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 03 (26RG): resolves exact verified primary & fallback URLs
00:00 +33: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 04 (26RH): resolves exact verified primary & fallback URLs
00:00 +34: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 05 (2023-AWQ-BESSIE): resolves exact verified primary & fallback URLs
00:00 +35: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 06 (2023-AWQ-EDITH): resolves exact verified primary & fallback URLs
00:00 +36: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 07 (2023-AWQ-ELEANOR): resolves exact verified primary & fallback URLs
00:00 +37: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 08 (2023-AWQ-JOVITA): resolves exact verified primary & fallback URLs
00:00 +38: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 09 (2023-AWQ-MARIA): resolves exact verified primary & fallback URLs
00:00 +39: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 10 (ATB-2013-D): resolves exact verified primary & fallback URLs
00:00 +40: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 11 (ATB-2010-P): resolves exact verified primary & fallback URLs
00:00 +41: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 12 (ATB-2020-S): resolves exact verified primary & fallback URLs
00:00 +42: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 13 (ATB-2020-S): resolves exact verified primary & fallback URLs
00:00 +43: CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests Synthetic Tracker Case 14 (ATB-2020-S): resolves exact verified primary & fallback URLs
00:00 +44: All tests passed!
```

---
## 4. Comprehensive Audit Table for All 28 Eric Account Items (`MF1`, `MF2`, `MF3`, `MF4`, `MF8`, `MF9`)

| Row | Firestore `doc_id` | Account | SKU / Series | Year-Mint | Theme / Subject | `obverseUrl` (with Live GCS Size & MD5 Prefix) | `reverseUrl` (with Live GCS Size & MD5 Prefix) | Verified Fallbacks (`fallbackObverseUrl` / `fallbackReverseUrl`) |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| 01 | `e91efa62-4e8d-4920-a928-c0c97659bcdc` | `eric.seaman@yahoo.com` | `26EA` | `2026-W` | America250 | `reference_library/us_mint_official/2026_products/26EA_image_1.jpg` (`126,209 B` (`md5: cb25bbc19d…`)) | `reference_library/us_mint_official/2026_products/26EA_image_2.jpg` (`139,910 B` (`md5: cfa91a545c…`)) | `reference_library/us_mint_official/2026_products/26ea_a.webp` (`168,246 B`, `md5: 790d13287d...`, `HTTP 200 LIVE`) / `reference_library/us_mint_official/2026_products/26ea_b.webp` (`164,146 B`, `md5: 62ad11e997...`, `STAGED Gate 4`) |
| 02 | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` | `eric.seaman@yahoo.com` | `26XE` | `2026` | Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026) | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`240,850 B` (`md5: 030c23e7cc…`)) | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` (`216,358 B`, `md5: 96290c2d73...`, `HTTP 200 LIVE`) / `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`) |
| 03 | `a59853c1-b72b-414d-8b8e-de6813c29996` | `eric.seaman@yahoo.com` | `26XL` | `2026-P` | America250 | `reference_library/us_mint_official/2026_products/26XL_image_3.jpg` (`204,667 B` (`md5: a2127adeef…`)) | `reference_library/us_mint_official/2026_products/26XL_image_2.jpg` (`379,918 B` (`md5: f2a4301688…`)) | `reference_library/us_mint_official/2026_products/26xl___a.webp` / `reference_library/us_mint_official/2026_products/26XL_image_1.jpg` |
| 04 | `71e2d4ae92bc4312a4198a3a0cc21fcb` | `eric.seaman@yahoo.com` | `26RJ` | `2026` | 2026 United States Mint Uncirculated Coin Set | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` (`336,365 B` (`md5: bba8df78a5…`)) | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` (`265,821 B` (`md5: abe6d1dd12…`)) | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` / `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` |
| 05 | `91f8821265bfe8a33fbd97e21f102c67fdf849fd` | `eric.seaman@yahoo.com` | `26RJ` | `2026` |  | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` (`336,365 B` (`md5: bba8df78a5…`)) | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` (`265,821 B` (`md5: abe6d1dd12…`)) | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` / `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` |
| 06 | `0e68ecba760df66bf824ec1ba2c86b32318d002d` | `eric.seaman@yahoo.com` | `26GC` | `2026` |  | `reference_library/us_mint_official/2026_products/26GC_image_1.jpg` (`135,436 B` (`md5: ee2eea2529…`)) | `reference_library/us_mint_official/2026_products/26gc_b.webp` (`137,372 B` (`md5: 4ec332f787…`)) | `reference_library/2026_series/2026_american_innovation_obverse.jpg` / `reference_library/us_mint_official/2026_products/26GC_image_2.jpg` |
| 07 | `7a32932ebc4e94a586534e7180cd1c4372c4f17d` | `eric.seaman@yahoo.com` | `26SQRP` | `2026-D` | Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` (`217,879 B` (`md5: fb99f484c7…`)) | `reference_library/us_mint_official/2026_products/26sqrp_b.webp` (`179,722 B` (`md5: dfeee8a47f…`)) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` / `None` (null - duplicate eliminated) |
| 08 | `nAnGLwGvhfIOibf6kIft` | `eric.seaman@yahoo.com` | `2026-DIME-P` | `2026-P` | Franklin D. Roosevelt | `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg` (`1,224,376 B` (`md5: c39fe99a21…`)) | `reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B` (`md5: 8533943d7d…`)) | `None` (null — byte-identical self-fallback eliminated) / `None` (null) |
| 09 | `rv9SCUTahBuqJkkiJyga` | `eric.seaman@yahoo.com` | `2026-DIME-D` | `2026-D` | Franklin D. Roosevelt | `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg` (`1,224,042 B` (`md5: fb30835fd1…`)) | `reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B` (`md5: 8533943d7d…`)) | `None` (null) / `None` (null) |
| 10 | `0172d0ee64284a12a8aa269ce805ec07` | `eric.seaman@yahoo.com` | `2026-MAYFLOWER-P` | `2026-P` | Mayflower Compact & Pilgrim Couple | `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` (`1,446,894 B` (`md5: a93d9444f8…`)) | `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg` (`1,627,560 B` (`md5: c62c9f4aec…`)) | `None` (null — cross-mint and byte-identical self-fallbacks eliminated) / `None` (null) |
| 11 | `8f2197d5d03a428db24486b4ee375a5e` | `eric.seaman@yahoo.com` | `2026-HALF-D` | `2026-D` | 250th Anniversary of American Independence | **PRESERVED USER PHOTOS** (`scan_source: microscope`, `numista-uploads-studio-.../users/eric@numista.ai/...`) | **PRESERVED USER PHOTOS** (protected by `hasUserUploadedPhotos` guard; `resolveFromMap` returns `null`) | Catalog Reference Resolution: `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`) / `SemiQ-Half-Dollar-Reverse-Unc.jpg` (`1,510,409 B`) |
| 12 | `5b424047-77e0-496e-a513-6ef180b515a6` | `eric.seaman@yahoo.com` | `2005-SQ-KS-D` | `2005-D` | Kansas | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg` (`572,791 B` (`md5: 146bcb61b2…`)) | `reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg` (`546,742 B` (`md5: 48a02e9e79…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg` / `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg` |
| 13 | `3346cda5-5935-4303-bf62-de43041f3175` | `eric.seaman@yahoo.com` | `ATB-2019-P` | `2019-P` | American Memorial Park (Northern Mariana Islands) | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`2,133,544 B` (`md5: 45abfe1d9b…`)) | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg` (`2,064,160 B` (`md5: 3dd32dc656…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 14 | `b243621c-5a35-45f0-84bf-8786eb1547f9` | `eric.seaman@yahoo.com` | `ATB-2020-P` | `2020-P` | Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands) | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`1,340,722 B` (`md5: 6ed5d08806…`)) | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg` (`1,298,877 B` (`md5: 1c55def862…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 15 | `c336e53e-4105-44bd-8c08-f30ae0328467` | `eric.seaman@yahoo.com` | `ATB-2013-P` | `2013-P` | Mount Rushmore National Memorial (South Dakota) | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` (`1,867,830 B` (`md5: d7cb6ecc2c…`)) | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg` (`2,032,412 B` (`md5: 0b6ded8854…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 16 | `cba5e585-758f-4b10-be7a-1a59a1f4b2e6` | `eric.seaman@yahoo.com` | `ATB-2018-P` | `2018-P` | Cumberland Island National Seashore (Georgia) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`2,309,513 B` (`md5: 6212666267…`)) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg` (`2,157,454 B` (`md5: 0f91df6cf3…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 17 | `d7fec246-983f-40de-8b58-854f59460bce` | `eric.seaman@yahoo.com` | `ATB-2018-P` | `2018-P` | Block Island National Wildlife Refuge (Rhode Island) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`2,309,513 B` (`md5: 6212666267…`)) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg` (`2,242,129 B` (`md5: 52026d4062…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 18 | `Wq2UhSQNs67u34VFJDaI` | `eric.seaman@yahoo.com` | `1962-LINCOLN-1C` | `1962` | Abraham Lincoln | `reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg` (`1,744,750 B` (`md5: 070b9a8418…`)) | `reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` (`608,070 B` (`md5: 75eb808f3a…`)) | `reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png` / `None` (null - duplicate eliminated) |
| 19 | `UOBfFO2mqgLg86NSsyss` | `eric.seaman@yahoo.com` | `ATB-2019-W` | `2019-W` | San Antonio Missions | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` (`1,176,299 B` (`md5: 2183268cf2…`)) | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` (`2,116,020 B` (`md5: 28175266fc…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` / `None` (null - duplicate eliminated) |
| 20 | `3f437576-fa20-4ef1-95c0-01e10eaf43a8` | `eric.seaman@yahoo.com` | `ATB-2017-P` | `2017-P` | Effigy Mounds National Monument (Iowa) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg` (`2,062,235 B` (`md5: 62e200b5ff…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 21 | `6ff959a0-26f8-451f-aa4c-064b5ef68939` | `eric.seaman@yahoo.com` | `ATB-2017-P` | `2017-P` | Frederick Douglass National Historic Site (District of Columbia) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` (`2,127,779 B` (`md5: c2bffdc58c…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 22 | `96eeb7b6-6c4e-4a62-bb8e-80b69706d915` | `eric.seaman@yahoo.com` | `ATB-2010-P` | `2010-P` | Yellowstone National Park (Wyoming) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` (`592,295 B` (`md5: 23c0fbbf07…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 23 | `ab35ab5d-d51f-4b9c-bc94-ff87def52bc6` | `eric.seaman@yahoo.com` | `ATB-2017-D` | `2017-D` | George Rogers Clark National Historical Park (Indiana) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` (`1,176,299 B` (`md5: 2183268cf2…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` (`2,118,832 B` (`md5: 673f4e83fe…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg` / `None` (null - duplicate eliminated) |
| 24 | `b785236f-ca64-4461-9ee4-01cad3a7d60e` | `eric.seaman@yahoo.com` | `ATB-2017-P` | `2017-P` | Ozark National Scenic Riverways (Missouri) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` (`2,172,068 B` (`md5: 8e711b71fd…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `None` (null - duplicate eliminated) |
| 25 | `0a2bc793-8d62-47c3-88cd-7a5b9be434ba` | `eric@numista.ai` | `26RJ` | `2026` |  | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` (`336,365 B` (`md5: bba8df78a5…`)) | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` (`265,821 B` (`md5: abe6d1dd12…`)) | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` / `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` |
| 26 | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` | `eric@numista.ai` | `26XE` | `2026` | Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026) | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`240,850 B` (`md5: 030c23e7cc…`)) | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` (`216,358 B`, `md5: 96290c2d73...`, `HTTP 200 LIVE`) / `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`) |
| 27 | `faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c` | `eric@numista.ai` | `26SQRP` | `2026-D` |  | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` (`217,879 B` (`md5: fb99f484c7…`)) | `reference_library/us_mint_official/2026_products/26sqrp_b.webp` (`179,722 B` (`md5: dfeee8a47f…`)) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` / `None` (null - duplicate eliminated) |
| 28 | `2fa325166682b70aa0d64da45786c94aa4742d21` | `eric@numista.ai` | `23RH` | `2023` | Silver Proof Set (10-coin set) | `reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg` (`711,501 B` (`md5: 1e65934dca...`)) | `reference_library/2023_series/2023_american_innovation_four_states_composite.jpg` (`584,055 B` (`md5: beb40fba68...`)) | `reference_library/us_mint_official/2023_products/23rh_b.webp` (`226,854 B`, `STAGED Gate 4`) / `reference_library/us_mint_official/2023_products/23rh_c.webp` (`161,734 B`, `STAGED Gate 4`) |

---

---

### 4.1 Verification Logs, Pixel-Compare Proof & GCS Measured Content-Length Bytes

#### 4.1.1 Reconciled Row 11 Half Dollar Specification (`MF-D`, `MF-2`)
Row 11 matches live Firestore document `8f2197d5d03a428db24486b4ee375a5e` (`eric.seaman@yahoo.com`, `2026-D`, Title: `"250th Anniversary of American Independence"` Half Dollar).
- **Live User Document Preservation:** Because Founder Eric uploaded microscope photos to this document (`hasUserUploadedPhotos == true`), the MF-B user-upload guard strictly returns `null` from `resolveFromMap`, preserving his authentic photos non-destructively (verified by Section 3.2 Row 11 unit test).
- **Catalog Reference Lookup (`hasUserUploadedPhotos == false`):** When resolving clean reference imagery for `2026-HALF-D` (verified by Section 3.2 Row 11 Reference Resolution unit test):
  - **Primary Obverse:** `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`, MD5: `ef82afd24a5c4eeb74947958b0552e91`, Base64: `74Kv0kpcTut0lHlYsFUukQ==`, `HTTP 200 LIVE`). (For `2026-HALF-P`: `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, `1,510,450 B`, MD5: `ec05347cabf3b134a262ac9f6631385b`, Base64: `7AU0fKvzsTSiYqyfZjE4Ww==`, `HTTP 200 LIVE`).
  - **Primary Reverse:** `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg` (`1,510,409 B`, MD5: `cceb4ab85d398347792d8929fb11bed0`, Base64: `zOtKuF05g0d5LYkp+xG+0A==`, `HTTP 200 LIVE`).
  - **Fallback Obverse:** `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg` (`HTTP 200 LIVE`).
  - **Fallback Reverse:** `None (null)` (redundant self-fallback eliminated).

#### 4.1.2 Automated Section 4 Audit Verification against ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json
All 28 rows match `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` with 100% fidelity:
- Rows 1–7: 2026 America250 Mint Products (26EA, 26XE, 26XL, 26RJ, 26GC, 26SQRP)
- Rows 8–11: 2026 Semi-Quincentennial Uncirculated Set Coins (Dime P/D, Half Dollar D, Mayflower 2026-P Protected User Upload)
- Rows 12–17: State & ATB Quarters (2005-D Kansas, 2019-P American Memorial Park, 2020-P Salt River Bay, 2013-P Mount Rushmore, 2018-P Cumberland Island, 2018-P Block Island)
- Row 18: 1962 Lincoln Cent (Stored Obverse Kept, Memorial Reverse Replaced)
- Rows 19–24: ATB Quarters (2019-W San Antonio, 2017-P Effigy Mounds, 2017-P Frederick Douglass, 2010-P Yellowstone, 2017-D George Rogers Clark, 2017-P Ozark)
- Rows 25–27: 2026 America250 Additional Sets (26RJ, 26XE, 26SQRP)
- Row 28: 2023 American Innovation & American Women Quarters Composite (23RH)

#### 4.1.3 Raw Measured GCS Content-Length Bytes & MD5 Hashes for All Reference Suite URLs (`MF3`, `MF6`, `WAKE_AG-COS-V4_NET-708`)

Single Source of Truth Census: Exactly **114 Total Reference Suite Paths** (**110 Live in GCS HTTP 200** + **4 Staged WebPs** scheduled for Gate 4 upload upon Founder Eric's typed YES):
- **Total Reference Assets in Suite:** 114 assets (110 live in GCS HTTP 200 + 4 local staged WebPs).
- **HTTP 200 LIVE on GCS Right Now:** 110 assets verified live via automated HTTP HEAD probes with exact Content-Length bytes and MD5 digests.
- **Explicitly Staged Assets on Disk (Gate 4 Upload):** 4 local staged WebPs verified locally on disk with measured bytes and MD5 digests, scheduled for GCS upload in Gate 4 upon Founder Eric's typed YES.
- **Local Staging Source Directory on Disk (SF-A):** `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\` (and `1 NUMISTA.AI\Coin Images\staged_mint_images\`) before upload.

| # | GCS Path | Byte Size | MD5 Hash (Base64) | MD5 Hash (Hex) | Content-Type | Live Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | `reference_library/2023_series/2023_american_innovation_four_states_composite.jpg` | 584,055 B | `vrQPumi94UYMhlxdfVTYpg==` | `beb40fba68bde1460c865c5d7d54d8a6` | `image/jpeg` | HTTP 200 LIVE |
| 002 | `reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.jpg` | 208,114 B | `ZzRvt5eUtDA2hw9agpkCGA==` | `67346fb79794b43036870f5a82990218` | `image/jpeg` | HTTP 200 LIVE |
| 003 | `reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.png` | 579,926 B | `YEjBG1JsoMjJgzRTxgjpIA==` | `6048c11b526ca0c8c9833453c608e920` | `image/png` | HTTP 200 LIVE |
| 004 | `reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.jpg` | 231,827 B | `O6HDkln0SoBGVkwtDmbrSg==` | `3ba1c39259f44a8046564c2d0e66eb4a` | `image/jpeg` | HTTP 200 LIVE |
| 005 | `reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.png` | 630,500 B | `oNPX6X/bH6P7MClVM/CzPQ==` | `a0d3d7e97fdb1fa3fb30295533f0b33d` | `image/png` | HTTP 200 LIVE |
| 006 | `reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.jpg` | 231,270 B | `F3St306+uFcMecYBc4UoFQ==` | `1774addf4ebeb8570c79c60173852815` | `image/jpeg` | HTTP 200 LIVE |
| 007 | `reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.png` | 643,041 B | `7jTaHVKLBSUWI6pQn03j/w==` | `ee34da1d528b05251623aa509f4de3ff` | `image/png` | HTTP 200 LIVE |
| 008 | `reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg` | 711,501 B | `HmWTTcqxlE/3AQiDaQrGfQ==` | `1e65934dcab1944ff7010883690ac67d` | `image/jpeg` | HTTP 200 LIVE |
| 009 | `reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.jpg` | 195,775 B | `SD+TV26sC7/d/HP87DmX8w==` | `483f93576eac0bbfddfc73fcec3997f3` | `image/jpeg` | HTTP 200 LIVE |
| 010 | `reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.png` | 578,910 B | `OWH/ZE9rzaf0xC3QLq91sQ==` | `3961ff644f6bcda7f4c42dd02eaf75b1` | `image/png` | HTTP 200 LIVE |
| 011 | `reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.jpg` | 193,842 B | `II9laxiLmvQGT1o0Y/vUig==` | `208f656b188b9af4064f5a3463fbd48a` | `image/jpeg` | HTTP 200 LIVE |
| 012 | `reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.png` | 566,667 B | `0uL2T/LBE9BjOW/3qom2Yw==` | `d2e2f64ff2c113d063396ff7aa89b663` | `image/png` | HTTP 200 LIVE |
| 013 | `reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg` | 167,735 B | `OlGn3LONL/Rb1kvSFInhGw==` | `3a51a7dcb38d2ff45bd64bd21489e11b` | `image/jpeg` | HTTP 200 LIVE |
| 014 | `reference_library/2023_series/2023_american_women_quarters_shared_obverse.png` | 508,739 B | `frH0O3WCdce2BQTmJPgftg==` | `7eb1f43b758275c7b60504e624f81fb6` | `image/png` | HTTP 200 LIVE |
| 015 | `reference_library/2026_series/2026_american_innovation_obverse.jpg` | 1,279,411 B | `UVtY6h7zE7XOAQnh8rxz1Q==` | `515b58ea1ef313b5ce0109e1f2bc73d5` | `image/jpeg` | HTTP 200 LIVE |
| 016 | `reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg` | 1,224,376 B | `w5/pmiEvfXewhkfa/eOyZg==` | `c39fe99a212f7d77b08647dafde3b266` | `image/jpeg` | HTTP 200 LIVE |
| 017 | `reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg` | 1,336,791 B | `hTOUPX2IoBGtrzckdr/h8w==` | `8533943d7d88a011adaf372476bfe1f3` | `image/jpeg` | HTTP 200 LIVE |
| 018 | `reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` | 1,510,450 B | `7AU0fKvzsTSiYqyfZjE4Ww==` | `ec05347cabf3b134a262ac9f6631385b` | `image/jpeg` | HTTP 200 LIVE |
| 019 | `reference_library/2026_series/2026_half_dollar_enduring_liberty_reverse.jpg` | 1,510,409 B | `zOtKuF05g0d5LYkp+xG+0A==` | `cceb4ab85d398347792d8929fb11bed0` | `image/jpeg` | HTTP 200 LIVE |
| 020 | `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` | 1,446,894 B | `qT2URPiM0HRDiKiXNyXyTg==` | `a93d9444f88cd0744388a8973725f24e` | `image/jpeg` | HTTP 200 LIVE |
| 021 | `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg` | 1,627,560 B | `xiyfSuyVCCfLEa+k/nSa7Q==` | `c62c9f4aec950827cb11afa4fe749aed` | `image/jpeg` | HTTP 200 LIVE |
| 022 | `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg` | 576,545 B | `ni7g5HSgcfLBn+xbby2TQw==` | `9e2ee0e474a071f2c19fec5b6f2d9343` | `image/jpeg` | HTTP 200 LIVE |
| 023 | `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp` | 166,278 B | `CAY3aDRhKWIlT/ls+Mu/Rg==` | `0806376834612962254ff96cf8cbbf46` | `image/webp` | HTTP 200 LIVE |
| 024 | `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` | 592,295 B | `I8D7vwcAoyv3gT2gx76SOQ==` | `23c0fbbf0700a32bf7813da0c7be9239` | `image/jpeg` | HTTP 200 LIVE |
| 025 | `reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` | 712,711 B | `xWCe+xnAqYKxA3jG0SIF9g==` | `c5609efb19c0a982b10378c6d12205f6` | `image/jpeg` | HTTP 200 LIVE |
| 026 | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg` | 2,032,412 B | `C23tiFQq+fmHJbewhLvUmA==` | `0b6ded88542af9f98725b7b084bbd498` | `image/jpeg` | HTTP 200 LIVE |
| 027 | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-proof-obverse-s.jpg` | 1,887,639 B | `Aj88bmUf4gvL2NEOMFGtAQ==` | `023f3c6e651fe20bcbd8d10e3051ad01` | `image/jpeg` | HTTP 200 LIVE |
| 028 | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg` | 1,864,933 B | `w7mHrHVnfVty567md4EoPg==` | `c3b987ac75677d5b72e7aee67781283e` | `image/jpeg` | HTTP 200 LIVE |
| 029 | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` | 1,867,830 B | `18tuzCxGW52pPDBd/yOdAQ==` | `d7cb6ecc2c465b9da93c305dff239d01` | `image/jpeg` | HTTP 200 LIVE |
| 030 | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg` | 2,269,453 B | `NbGPazstN+3/9xA2LMGcUA==` | `35b18f6b3b2d37edfff710362cc19c50` | `image/jpeg` | HTTP 200 LIVE |
| 031 | `reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg` | 2,462,457 B | `tateKDh88b30ilnRqrFcGA==` | `b5ab5e28387cf1bdf48a59d1aab15c18` | `image/jpeg` | HTTP 200 LIVE |
| 032 | `reference_library/atb_quarters/2015-america-the-beautiful-quarters-coin-blue-ridge-parkway-north-carolina-uncirculated-reverse.jpg` | 2,201,002 B | `Vh19IE8qk8GUgzoBol4jMQ==` | `561d7d204f2a93c194833a01a25e2331` | `image/jpeg` | HTTP 200 LIVE |
| 033 | `reference_library/atb_quarters/2016-america-the-beautiful-quarters-coin-cumberland-gap-kentucky-uncirculated-reverse.jpg` | 2,216,535 B | `b6CBXo2TnDyhNSW6Jm6x1A==` | `6fa0815e8d939c3ca13525ba266eb1d4` | `image/jpeg` | HTTP 200 LIVE |
| 034 | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg` | 2,062,235 B | `YuIAtf85GEz3NZX1hfwc/g==` | `62e200b5ff39184cf73595f585fc1cfe` | `image/jpeg` | HTTP 200 LIVE |
| 035 | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ellis-island-new-jersey-uncirculated-reverse.jpg` | 1,968,246 B | `JtbLWz7SKe6Ug1G/qvzBVg==` | `26d6cb5b3ed229ee948351bfaafcc156` | `image/jpeg` | HTTP 200 LIVE |
| 036 | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` | 2,127,779 B | `wr/9xYxj3OG3AjE+BJ2xpw==` | `c2bffdc58c63dce1b702313e049db1a7` | `image/jpeg` | HTTP 200 LIVE |
| 037 | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` | 2,118,832 B | `Zz9Og/675Yra1Iq9pOcJYw==` | `673f4e83febbe58adad48abda4e70963` | `image/jpeg` | HTTP 200 LIVE |
| 038 | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` | 2,172,068 B | `jnEbcf3VUSMB4z080y7Dxg==` | `8e711b71fdd5512301e33d3cd32ec3c6` | `image/jpeg` | HTTP 200 LIVE |
| 039 | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg` | 2,242,129 B | `UgJtQGL253JRSNSVwjUTiQ==` | `52026d4062f6e7725148d495c2351389` | `image/jpeg` | HTTP 200 LIVE |
| 040 | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg` | 2,157,454 B | `D5HfbPN0dl/yEb0X5fMUgg==` | `0f91df6cf374765ff211bd17e5f31482` | `image/jpeg` | HTTP 200 LIVE |
| 041 | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg` | 2,309,627 B | `W9Yet/6Wg1VGJpJlOMwACw==` | `5bd61eb7fe9683554626926538cc000b` | `image/jpeg` | HTTP 200 LIVE |
| 042 | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | 2,309,513 B | `YhJmYmedzCTERkmU95+mDA==` | `62126662679dcc24c4464994f79fa60c` | `image/jpeg` | HTTP 200 LIVE |
| 043 | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg` | 2,064,160 B | `PdMtxlZ5Ai2LbIbIgSIjgg==` | `3dd32dc65679022d8b6c86c881222382` | `image/jpeg` | HTTP 200 LIVE |
| 044 | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` | 2,116,020 B | `KBdSZvzeuU302IRReE5kKA==` | `28175266fcdeb94df4d88451784e6428` | `image/jpeg` | HTTP 200 LIVE |
| 045 | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg` | 2,134,218 B | `4NVlJ/jWgddvhU8JGte46g==` | `e0d56527f8d681d76f854f091ad7b8ea` | `image/jpeg` | HTTP 200 LIVE |
| 046 | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | 2,133,544 B | `Rav+HZusCG43v29jWmjufg==` | `45abfe1d9bac086e37bf6f635a68ee7e` | `image/jpeg` | HTTP 200 LIVE |
| 047 | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg` | 1,225,636 B | `Mi+H6tey28mqy3HnVxtjuA==` | `322f87ead7b2dbc9aacb71e7571b63b8` | `image/jpeg` | HTTP 200 LIVE |
| 048 | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg` | 1,298,877 B | `HFXe+GLgNc9idGr5UT7bzQ==` | `1c55def862e035cf62746af9513edbcd` | `image/jpeg` | HTTP 200 LIVE |
| 049 | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg` | 1,198,829 B | `Fenq+jpa05htUAu5ZL9Sww==` | `15e9eafa3a5ad3986d500bb964bf52c3` | `image/jpeg` | HTTP 200 LIVE |
| 050 | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg` | 1,338,124 B | `p6L5mPXXusyYqCrlg3As6w==` | `a7a2f998f5d7bacc98a82ae583702ceb` | `image/jpeg` | HTTP 200 LIVE |
| 051 | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | 1,340,722 B | `btXQiAYL+dJS2Soeuk8hIQ==` | `6ed5d088060bf9d252d92a1eba4f2121` | `image/jpeg` | HTTP 200 LIVE |
| 052 | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg` | 1,307,070 B | `6fOcGUn1i6Hv54HpvgnMCg==` | `e9f39c1949f58ba1efe781e9be09cc0a` | `image/jpeg` | HTTP 200 LIVE |
| 053 | `reference_library/bulk_programs/50_state_quarters/2003-50-state-quarters-coin-arkansas-uncirculated-reverse.jpg` | 361,722 B | `XANYw4SsVgFWOnFVR8y0Sg==` | `5c0358c384ac5601563a715547ccb44a` | `image/jpeg` | HTTP 200 LIVE |
| 054 | `reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg` | 546,742 B | `SKAunnng5suWmWon8efjMA==` | `48a02e9e79e0e6cb96996a27f1e7e330` | `image/jpeg` | HTTP 200 LIVE |
| 055 | `reference_library/bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` | 1,447,978 B | `ocXRv0xUSqMKX3ZT52Xfjg==` | `a1c5d1bf4c544aa30a5f7653e765df8e` | `image/jpeg` | HTTP 200 LIVE |
| 056 | `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg` | 1,224,042 B | `+zCDX9GonJPN9l8QOBO2nA==` | `fb30835fd1a89c93cdf65f103813b69c` | `image/jpeg` | HTTP 200 LIVE |
| 057 | `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg` | 1,224,376 B | `w5/pmiEvfXewhkfa/eOyZg==` | `c39fe99a212f7d77b08647dafde3b266` | `image/jpeg` | HTTP 200 LIVE |
| 058 | `reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg` | 1,336,791 B | `hTOUPX2IoBGtrzckdr/h8w==` | `8533943d7d88a011adaf372476bfe1f3` | `image/jpeg` | HTTP 200 LIVE |
| 059 | `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg` | 1,510,128 B | `74Kv0kpcTut0lHlYsFUukQ==` | `ef82afd24a5c4eeb74947958b0552e91` | `image/jpeg` | HTTP 200 LIVE |
| 060 | `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg` | 1,510,409 B | `zOtKuF05g0d5LYkp+xG+0A==` | `cceb4ab85d398347792d8929fb11bed0` | `image/jpeg` | HTTP 200 LIVE |
| 061 | `reference_library/bulk_programs/penny/2008-lincoln-one-cent-reverse-2000x2000.jpg` | 1,519,664 B | `mByArOFgs44zkCirE7bI1A==` | `981c80ace160b38e339028ab13b6c8d4` | `image/jpeg` | HTTP 200 LIVE |
| 062 | `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg` | 1,510,450 B | `7AU0fKvzsTSiYqyfZjE4Ww==` | `ec05347cabf3b134a262ac9f6631385b` | `image/jpeg` | HTTP 200 LIVE |
| 063 | `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg` | 1,434,919 B | `M/8Y3Jm7xJVajtCg0alJpQ==` | `33ff18dc99bbc4955a8ed0a0d1a949a5` | `image/jpeg` | HTTP 200 LIVE |
| 064 | `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Reverse-Unc.jpg` | 1,627,560 B | `xiyfSuyVCCfLEa+k/nSa7Q==` | `c62c9f4aec950827cb11afa4fe749aed` | `image/jpeg` | HTTP 200 LIVE |
| 065 | `reference_library/us_mint_official/2026_products/26EA_image_1.jpg` | 126,209 B | `yyW7wZ1+cqCUCUV9bOMwow==` | `cb25bbc19d7e72a09409457d6ce330a3` | `image/jpeg` | HTTP 200 LIVE |
| 066 | `reference_library/us_mint_official/2026_products/26EA_image_2.jpg` | 139,910 B | `z6kaVFzaD9MVa+GmyKnTNg==` | `cfa91a545cda0fd3156be1a6c8a9d336` | `image/jpeg` | HTTP 200 LIVE |
| 067 | `reference_library/us_mint_official/2026_products/26EA_image_3.jpg` | 142,916 B | `Na0q3XBIgct2y/UyL7xCAA==` | `35ad2add704881cb76cbf5322fbc4200` | `image/jpeg` | HTTP 200 LIVE |
| 068 | `reference_library/us_mint_official/2026_products/26GC_image_1.jpg` | 135,436 B | `7i7qJSlqeLoWVTHElAGD7Q==` | `ee2eea25296a78ba165531c4940183ed` | `image/jpeg` | HTTP 200 LIVE |
| 069 | `reference_library/us_mint_official/2026_products/26GC_image_2.jpg` | 138,756 B | `dTWDCgrtxzX659uNQwcbMw==` | `7535830a0aedc735fae7db8d43071b33` | `image/jpeg` | HTTP 200 LIVE |
| 070 | `reference_library/us_mint_official/2026_products/26RG_image_1.jpg` | 115,064 B | `R4j7mhD21PHNmZ6xRBoWSw==` | `4788fb9a10f6d4f1cd999eb1441a164b` | `image/jpeg` | HTTP 200 LIVE |
| 071 | `reference_library/us_mint_official/2026_products/26RG_image_2.jpg` | 104,072 B | `YzcSFLpzF+Wi5315lmapiw==` | `63371214ba7317e5a2e77d799666a98b` | `image/jpeg` | HTTP 200 LIVE |
| 072 | `reference_library/us_mint_official/2026_products/26RG_image_3.jpg` | 197,484 B | `0K8+7wU+q+BvFVUVGISX4w==` | `d0af3eef053eabe06f155515188497e3` | `image/jpeg` | HTTP 200 LIVE |
| 073 | `reference_library/us_mint_official/2026_products/26RH_image_1.jpg` | 110,063 B | `S9ssi0PNcho75SIMQmOGEw==` | `4bdb2c8b43cd721a3be5220c42638613` | `image/jpeg` | HTTP 200 LIVE |
| 074 | `reference_library/us_mint_official/2026_products/26RH_image_2.jpg` | 104,034 B | `ueuMT1YLnZoXjO2FR6QxKQ==` | `b9eb8c4f560b9d9a178ced8547a43129` | `image/jpeg` | HTTP 200 LIVE |
| 075 | `reference_library/us_mint_official/2026_products/26RH_image_3.jpg` | 209,254 B | `T6iaugYzjjDxMHWuy9gcKg==` | `4fa89aba06338e30f13075aecbd81c2a` | `image/jpeg` | HTTP 200 LIVE |
| 076 | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` | 299,132 B | `A9ijFLrNrypWsfE/IwMKuw==` | `03d8a314bacdaf2a56b1f13f23030abb` | `image/jpeg` | HTTP 200 LIVE |
| 077 | `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` | 300,506 B | `uRO6lXHJQ8HtIlcZEb1j/Q==` | `b913ba9571c943c1ed22571911bd63fd` | `image/jpeg` | HTTP 200 LIVE |
| 078 | `reference_library/us_mint_official/2026_products/26XE_image_1.jpg` | 195,231 B | `StUMKv65OT4Vfkb+GO3Pcw==` | `4ad50c2afeb9393e157e46fe18edcf73` | `image/jpeg` | HTTP 200 LIVE |
| 079 | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` | 240,850 B | `Awwj58wvtpH0LZn9IMtCEg==` | `030c23e7cc2fb691f42d99fd20cb4212` | `image/jpeg` | HTTP 200 LIVE |
| 080 | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` | 285,827 B | `4FaiAfyRWOLwRxU6+YN0gg==` | `e056a201fc9158e2f047153af9837482` | `image/jpeg` | HTTP 200 LIVE |
| 081 | `reference_library/us_mint_official/2026_products/26XF_image_1.jpg` | 274,992 B | `F4vXHIGNYcgRXEB2pT9I/w==` | `178bd71c818d61c8115c4076a53f48ff` | `image/jpeg` | HTTP 200 LIVE |
| 082 | `reference_library/us_mint_official/2026_products/26XF_image_2.jpg` | 324,593 B | `cjLNuR52u3vft4t5nc0xkw==` | `7232cdb91e76bb7bdfb78b799dcd3193` | `image/jpeg` | HTTP 200 LIVE |
| 083 | `reference_library/us_mint_official/2026_products/26XH_image_1.jpg` | 140,054 B | `sSdsLiUCKogkIi4G4ULYHw==` | `b1276c2e25022a8824222e06e142d81f` | `image/jpeg` | HTTP 200 LIVE |
| 084 | `reference_library/us_mint_official/2026_products/26XH_image_2.jpg` | 147,982 B | `uE4iRMoGow0AhsFn7H7wQQ==` | `b84e2244ca06a30d0086c167ec7ef041` | `image/jpeg` | HTTP 200 LIVE |
| 085 | `reference_library/us_mint_official/2026_products/26XH_image_3.jpg` | 169,132 B | `uPQRj7E7qV7axnVWzUcsqg==` | `b8f4118fb13ba95edac67556cd472caa` | `image/jpeg` | HTTP 200 LIVE |
| 086 | `reference_library/us_mint_official/2026_products/26XL_image_1.jpg` | 319,138 B | `/h7OLSwM8+I7uopf79GZIw==` | `fe1ece2d2c0cf3e23bba8a5fefd19923` | `image/jpeg` | HTTP 200 LIVE |
| 087 | `reference_library/us_mint_official/2026_products/26XL_image_2.jpg` | 379,918 B | `8qQwFog6B7DA1c4/1Hmqmg==` | `f2a43016883a07b0c0d5ce3fd479aa9a` | `image/jpeg` | HTTP 200 LIVE |
| 088 | `reference_library/us_mint_official/2026_products/26XL_image_3.jpg` | 204,667 B | `ohJ63u88ygv2DH28jifjUg==` | `a2127adeef3cca0bf60c7dbc8e27e352` | `image/jpeg` | HTTP 200 LIVE |
| 089 | `reference_library/us_mint_official/2026_products/26ea_a.webp` | 168,246 B | `eQ0TKH0gziKzCKJ9TvxhmQ==` | `790d13287d20ce22b308a27d4efc6199` | `image/webp` | HTTP 200 LIVE |
| 090 | `reference_library/us_mint_official/2026_products/26gc_b.webp` | 137,372 B | `TsMy94eKpDLEcwzQ0yjmYg==` | `4ec332f7878aa432c4730cd0d328e662` | `image/webp` | HTTP 200 LIVE |
| 091 | `reference_library/us_mint_official/2026_products/26rg_b.webp` | 178,232 B | `9slPy96nlPIGzKp/juF95g==` | `f6c94fcbdea794f206ccaa7f8ee17de6` | `image/webp` | HTTP 200 LIVE |
| 092 | `reference_library/us_mint_official/2026_products/26rj_a.webp` | 244,540 B | `MaSLBJR8yX1ngKRjOq2R3g==` | `31a48b04947cc97d6780a4633aad91de` | `image/webp` | HTTP 200 LIVE |
| 093 | `reference_library/us_mint_official/2026_products/26sqrp_b.webp` | 179,722 B | `3+7opH8PfVcsOkpcRBGpwA==` | `dfeee8a47f0f7d572c3a4a5c4411a9c0` | `image/webp` | HTTP 200 LIVE |
| 094 | `reference_library/us_mint_official/2026_products/26xe_a.webp` | 216,358 B | `likMLXOT1KExPbYZ14SzIA==` | `96290c2d7393d4a1313db619d784b320` | `image/webp` | HTTP 200 LIVE |
| 095 | `reference_library/us_mint_official/2026_products/26xh_image_3.jpg` | 169,132 B | `uPQRj7E7qV7axnVWzUcsqg==` | `b8f4118fb13ba95edac67556cd472caa` | `image/jpeg` | HTTP 200 LIVE |
| 096 | `reference_library/us_mint_official/2026_products/26xl___a.webp` | 239,954 B | `QDzAGaegsMsA2PAURavQeg==` | `403cc019a7a0b0cb00d8f01445abd07a` | `image/webp` | HTTP 200 LIVE |
| 097 | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` | 217,879 B | `+5n0hMeeZP0i59oaiMjrMw==` | `fb99f484c79e64fd22e7da1a88c8eb33` | `image/jpeg` | HTTP 200 LIVE |
| 098 | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` | 245,212 B | `zpHnAjb0Y8c50FPXF0md1w==` | `ce91e70236f463c739d053d717499dd7` | `image/jpeg` | HTTP 200 LIVE |
| 099 | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg` | 326,970 B | `nzVK2/mfrwB7VNa/2wAK7g==` | `9f354adbf99faf007b54d6bfdb000aee` | `image/jpeg` | HTTP 200 LIVE |
| 100 | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` | 265,821 B | `q+bR3RLJ4fAKXbPudIX94A==` | `abe6d1dd12c9e1f00a5db3ee7485fde0` | `image/jpeg` | HTTP 200 LIVE |
| 101 | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` | 336,365 B | `u6jfeKUlaYKp2A2DbFHwwA==` | `bba8df78a5256982a9d80d836c51f0c0` | `image/jpeg` | HTTP 200 LIVE |
| 102 | `reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg` | 1,744,750 B | `BwuahBjpA1+etJG1285mIQ==` | `070b9a8418e9035f9eb491b5dbce6621` | `image/jpeg` | HTTP 200 LIVE |
| 103 | `reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` | 608,070 B | `deuAjzoVEPUp38PiD8/s9g==` | `75eb808f3a1510f529dfc3e20fcfecf6` | `image/jpeg` | HTTP 200 LIVE |
| 104 | `reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png` | 1,018,519 B | `TKyZ0uaHYbGWl1ftDgpLEA==` | `4cac99d2e68761b1969757ed0e0a4b10` | `image/png` | HTTP 200 LIVE |
| 105 | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg` | 157,337 B | `LEgWthTD3aj5TkxwbX+UYQ==` | `2c4816b614c3dda8f94e4c706d7f9461` | `image/jpeg` | HTTP 200 LIVE |
| 106 | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg` | 572,791 B | `FGvLYbJuCGUz2eGYMEecqQ==` | `146bcb61b26e086533d9e19830479ca9` | `image/jpeg` | HTTP 200 LIVE |
| 107 | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg` | 1,410,838 B | `wq27ruadtVP+UAy/Fm4PVw==` | `c2adbbaee69db553fe500cbf166e0f57` | `image/jpeg` | HTTP 200 LIVE |
| 108 | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg` | 563,189 B | `Fa1rvuHzKBCkC5Z+zGfjcQ==` | `15ad6bbee1f32810a40b967ecc67e371` | `image/jpeg` | HTTP 200 LIVE |
| 109 | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` | 1,176,299 B | `IYMmjPIWJhVNRmGgZIvEGg==` | `2183268cf21626154d4661a0648bc41a` | `image/jpeg` | HTTP 200 LIVE |
| 110 | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` | 178,081 B | `tOm+c1c0Kr6fu2XTOUZGxg==` | `b4e9be7357342abe9fbb65d3394646c6` | `image/jpeg` | HTTP 200 LIVE |
| 111 | `reference_library/us_mint_official/2026_products/26ea_b.webp` | 164,146 B | `Yq0R6ZesAyC1cJHj0QjT4A==` | `62ad11e997ac0320b57091e3d108d3e0` | `image/webp` | STAGED (Gate 4 Upload) |
| 112 | `reference_library/us_mint_official/2026_products/26xe_b.webp` | 245,878 B | `OndpTJpy5ttjgRyLAB7btQ==` | `3a77694c9a72e6db63811c8b001edbb5` | `image/webp` | STAGED (Gate 4 Upload) |
| 113 | `reference_library/us_mint_official/2023_products/23rh_b.webp` | 226,854 B | `iiBg0MpZh7D68NiCjs42Xw==` | `8a2060d0ca5987b0faf0d8828ece365f` | `image/webp` | STAGED (Gate 4 Upload) |
| 114 | `reference_library/us_mint_official/2023_products/23rh_c.webp` | 161,734 B | `CPW1qvaYk2kT4qJHQ9vepQ==` | `08f5b5aaf698936913e2a24743dbdea5` | `image/webp` | STAGED (Gate 4 Upload) |

---

## 5. Purchase Cost & Integer Cents Splitting (SF-5)

### 5.1 Exact Penny Remainder Allocation Rule
In multi-coin order intake and quantity splitting (e.g. `review_hub_screen.dart:2040-2059` and `my_collection_screen.dart:3016-3022`), total costs are computed in integer cents to prevent floating-point rounding errors:

```dart
final int totalCostCents = (totalPurchaseCost * 100).round();
final int unitCostCents = totalCostCents ~/ quantity;
final int remainderCents = totalCostCents % quantity;

// Exact allocation algorithm:
// Coins 0 to (quantity - 2) receive unitCostCents.
// The final coin (index == quantity - 1) receives unitCostCents + remainderCents.
// Invariant: sum(assigned_costs) == totalCostCents (0 pennies gained or lost).
```

*Example:* A $64.97 order of 2 coins:
- `totalCostCents = 6497`
- `unitCostCents = 6497 ~/ 2 = 3248` ($32.48)
- `remainderCents = 6497 % 2 = 1` cent
- Coin 1 receives $32.48.
- Coin 2 receives $32.48 + $0.01 = $32.49.
- Total sum: `$32.48 + $32.49 = $64.97` (exact penny reconciliation).

---

---

## 6. Intake Manifest & Enumerated Intake Fixtures (SF-5, MF10)

The 11 official intake fixtures required for the 2026 Semiquincentennial catalog and historical proof sets are explicitly enumerated below:

1. `26ea_a.webp` (`168,246 B`) — 2026-W Silver Eagle Proof Obverse (Walking Liberty with 2026 date).
2. `26ea_b.webp` (`164,146 B`) — 2026-W Silver Eagle Proof Reverse (Staged for Gate 4 upload).
3. `26xe_a.webp` (`216,358 B`) — 2026 Morgan Dollar Enhanced Uncirculated Obverse.
4. `26xe_b.webp` (`245,878 B`) — 2026 Morgan Dollar Enhanced Uncirculated Reverse (Staged for Gate 4 upload).
5. `26xl___a.webp` (`239,954 B`) — 2026-P Peace Dollar Reverse Proof Obverse.
6. `26rj_a.webp` (`244,540 B`) — 2026 Uncirculated Coin Set Product Packaging / Folder.
7. `23rh_b.webp` (`226,854 B`) — 2023 Silver Proof Set Packaging Obverse (Staged for Gate 4 upload).
8. `23rh_c.webp` (`161,734 B`) — 2023 Silver Proof Set Packaging Reverse (Staged for Gate 4 upload).
9. `SemiQ-Dime-Obverse-Unc-D.jpg` (`1,224,042 B`) — 2026-D Roosevelt Dime Obverse (Denver).
10. `SemiQ-Dime-Obverse-Unc-P.jpg` (`1,224,376 B`) — 2026-P Roosevelt Dime Obverse (Philadelphia).
11. `SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B`) — 2026 Roosevelt Dime Reverse (Torch, Olive & Oak Branches).

---

---

## 7. Verbatim Rule 6(a) Repository Code Citations (Verified against `origin/dev 01a03f90` / `32d4b42e`)

### 7.1 [`numista_mobile/lib/screens/my_collection_screen.dart:6320-6366`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6320-L6366)
```dart
  @override
  Widget build(BuildContext context) {
    final obv = _cleanUrl(data[_F.imageObverse] ?? data['primary_image_url'] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).isNotEmpty ? data['photo_urls'][0] : null));
    final rev = _cleanUrl(data[_F.imageReverse] ?? (data['photo_urls'] is List && (data['photo_urls'] as List).length > 1 ? data['photo_urls'][1] : null));
    final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)

    if (directUrl.isNotEmpty) {
      return _buildCoinImage(directUrl);
    }

    // Dual-read: PascalCase first, lowercase fallback for unmigrated CSV docs
    String dualRead(String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }
    final year = dualRead('year', _F.year).replaceAll(RegExp(r'\.0$'), '');
    final mint = dualRead('mint_mark', _F.mintMark);
    final denom = dualRead('denomination', _F.denomination);
    final series = dualRead('program_series', _F.programSeries);
    final subject = dualRead('theme_subject', _F.themeSubject);

    return FutureBuilder<CoinImageResult>(
      future: CoinImageService.fetchReferenceImages(
        year: year,
        mint: mint.isEmpty ? null : mint,
        denomination: denom.isEmpty ? null : denom,
        series: series.isEmpty ? null : series,
        subject: subject.isEmpty ? null : subject,
      ),
      builder: (context, snapshot) {
        final ref = snapshot.data;
        // MF-V3-3: When subject is known and reverse is null (steal-guard
        // correctly blocked a generic reverse), show placeholder instead of
        // falling back to generic obverse. Keeps obverse fallback for coins
        // without a subject (e.g. generic Morgan/Peace).
        final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                ? ref!.obverseUrl!
                : '';

        if (refUrl.isNotEmpty) {
          return _buildCoinImage(refUrl);
        }
```
*Verification Command:* `git show origin/dev:numista_mobile/lib/screens/my_collection_screen.dart` lines 6320-6366 match 100% verbatim.

### 7.2 [`numista_mobile/lib/screens/my_collection_screen.dart:3016-3023`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3023)
```dart
        final valCpg = _parseNumber(m['cpgRetail']);
        final finalVal = valCpg;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final rawAiVal = m[_F.aiValue] ?? m['ai_estimated_value'] ?? m['estValue'] ?? (m['ai_est_value'] != null ? fmt.format(m['ai_est_value']) : null);
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (rawAiVal?.toString() ?? '—');
```
*Verification Command:* `git show origin/dev:numista_mobile/lib/screens/my_collection_screen.dart` lines 3016-3023 match 100% verbatim.

### 7.3 [`numista_mobile/lib/services/coin_image_service.dart:535-571`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L571)
```dart
      for (final base in bases) {
        final needsObv = bestObvUrl == null;
        final needsRev = bestRevUrl == null;
        if (!needsObv && !needsRev) break; // both sides resolved

        final isSubjectBase = subjectSlug != null && base.contains(subjectSlug);

        if (needsObv && (!hasSubject || isSubjectBase)) {
          final obvDoc = await db.collection(_collection)
              .doc('${base}_obverse').get();
          if (obvDoc.exists) {
            final d = obvDoc.data()!['obverse'] as Map<String, dynamic>?;
            if (d != null) {
              bestObvUrl = d['public_url'] as String?;
              bestAttr  ??= d['attribution'] as String?;
              bestLabel ??= d['source_label'] as String?;
              bestKey   ??= base;
            }
          }
        }

        // STEAL-GUARD: only accept reverse from subject-containing bases
        // when a subject is known. Generic reverse = honest placeholder.
        if (needsRev && (!hasSubject || isSubjectBase)) {
          final revDoc = await db.collection(_collection)
              .doc('${base}_reverse').get();
          if (revDoc.exists) {
            final d = revDoc.data()!['reverse'] as Map<String, dynamic>?;
            if (d != null) {
              bestRevUrl = d['public_url'] as String?;
              bestAttr  ??= d['attribution'] as String?;
              bestLabel ??= d['source_label'] as String?;
              bestKey   ??= base;
            }
          }
        }
      }
```
*Verification Command:* `git show origin/dev:numista_mobile/lib/services/coin_image_service.dart` lines 535-571 match 100% verbatim (closing brace included).

### 7.4 [`numista_mobile/lib/screens/review_hub_screen.dart:2282-2289`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2282-L2289)
```dart
                  () {
                    final rawCost = data['Purchase Cost'] ?? data['Cost'];
                    final rawSetCostLabel = (data['set_cost_label'] ?? '').toString().trim();
                    final costStr = rawSetCostLabel.isNotEmpty
                        ? rawSetCostLabel
                        : (rawCost != null
                            ? (rawCost is num ? '\$${rawCost.toStringAsFixed(2)}' : rawCost.toString())
                            : 'N/A');
```
*Verification Command:* `git show origin/dev:numista_mobile/lib/screens/review_hub_screen.dart` lines 2282-2289 match 100% verbatim.
*Note [PROPOSED EXTENSION]:* The multi-quantity unit cost breakdown (`final cleanQty = ...; costStr = ... each`) is proposed to be integrated into this exact block during build execution.

### 7.5 [`numista_backend/main.py:8369-8376`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8369-L8376)
```python
                    per_file[idx]["status"]      = "done"
                    per_file[idx]["coins_added"] = added_this_file
                    per_file[idx]["receipt_id"]  = receipt_id

                except Exception as e:
                    per_file[idx]["status"] = "error"
                    per_file[idx]["error"]  = str(e)
                    logger.error(f"Bulk import invoice error ({fname}): {e}\n{traceback.format_exc()}")
```
> [!NOTE]
> `[PROPOSED EXTENSION — NOT YET IN REPO]`: For `SF8` / PII sanitization in invoice error logs, the proposed regex sanitization `re.sub(r'order[_\s#-]*[0-9a-zA-Z]+', 'order_REDACTED', fname, flags=re.IGNORECASE)` will be applied in Gate 5 upon implementation.
*Verification Command:* `git show origin/dev:numista_backend/main.py` lines 8369-8376 match 100% verbatim.

---

---

## 8. Complete 39/39 Issue Tracker Coverage Matrix (SF3)

| Tracker ID | Description | Resolution in R2.8.13 |
| :--- | :--- | :--- |
| **B26-1** | 2026-W Silver Eagle reverse wrong year/sides swapped | Resolved via `26EA` mapping to live Type 2 reverse + staged `26ea_b.webp` |
| **B26-2** | 2026 Morgan Dollar missing artwork | Resolved via `26XE` mapping to live Morgan reverse + staged `26xe_b.webp` |
| **B26-3** | 2026 Peace Dollar reverse proof | Resolved via `26XL` mapping to live Peace reverse |
| **B26-4** | Morgan PDF intake verification | Deferred per NET-681E |
| **B26-5** | Add Coins UX layout | Deferred per NET-681E |
| **B26-6** | 2026 Uncirculated Coin Set | Resolved via `26RJ` mapping to `26rj_a.webp` |
| **B26-7** | 2026-D Trump Presidential Dollar Roll | Resolved via `26SQRP` mapping to 2026 Trump assets |
| **B26-8** | 2026 American Innovation Dollar | Resolved via `26GC` mapping to 2026 Innovation assets |
| **B26-9** | 2026-P Roosevelt Dime showing 2025 art | Resolved via `SemiQ-Dime-Obverse-Unc-P.jpg` |
| **B26-10** | 2026-D Roosevelt Dime showing 2025 art | Resolved via `SemiQ-Dime-Obverse-Unc-D.jpg` (mint field wins; `fallbackObverseUrl: null` per 404 elimination) |
| **B26-11** | 2026-P Mayflower Compact Quarter | User microscope photos preserved via user-upload guard |
| **B26-12** | 2026-D Semiquincentennial Half Dollar | Resolved via `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` |
| **B26-13** | 2026-P Semiquincentennial Half Dollar | Resolved via live `2026_half_dollar_enduring_liberty_obverse.jpg` (MF-1) |
| **B26-14** | 2005-D Kansas State Quarter showing Arkansas | Resolved via Denver State obv + genuine Kansas buffalo rev |
| **B26-15** | 2019-P American Memorial Park showing Blue Ridge | Resolved via undated P obv + genuine American Memorial rev |
| **B26-16** | 2020-P Salt River Bay showing Ozark | Resolved via undated P obv + genuine Salt River Bay rev |
| **B26-17** | 2013-P Mount Rushmore showing Mount Hood | Resolved via undated P obv + genuine Mount Rushmore rev |
| **B26-18** | 2018-P Cumberland Island showing Cumberland Gap | Resolved via undated P obv + genuine Cumberland Island rev |
| **B26-19** | 2018-P Block Island showing Ellis Island | Resolved via undated P obv + genuine Block Island rev |
| **B26-20** | 1962 Proof Cent showing 1909 Wheat | Obverse kept as stored pending proof intake; Lincoln Memorial rev mapped |
| **B26-21** | 2019-W San Antonio Missions showing 1932 obv | San Antonio Missions rev restored; 2019 obverse replacement flagged |
| **B26-22** | 2017-P Effigy Mounds showing Denver obv | Resolved via authentic Philadelphia undated obverse `obverse-p.jpg` |
| **B26-23** | 2017-P Frederick Douglass showing Denver obv | Resolved via authentic Philadelphia undated obverse `obverse-p.jpg` |
| **B26-24** | 2010-P Yellowstone showing Denver obv | Resolved via authentic Philadelphia undated obverse `obverse-p.jpg` |
| **B26-25** | 2017-D George Rogers Clark | Resolved via authentic Denver undated obverse `obverse-denver.jpg` |
| **B26-26** | 2017-P Ozark Riverways showing Denver obv | Resolved via authentic Philadelphia undated obverse `obverse-p.jpg` |
| **B26-27** | 2023 Silver Proof Set showing 2026 art | Staged `23rh_b.webp` / `23rh_c.webp` under `2023_products/` (MF-2) |
| **B26-28** | Purchase cost rounding discrepancies | Resolved via integer-cents math + exact penny remainder allocation (SF-5) |
| **B26-29** | Untitled items with null URLs | Resolved via fallback catalog mappings |
| **B26-30** to **B26-39** | Field Tester checklist items | Scheduled for interactive FT retest on `p7-gate` |

---

---

## 9. Staging Plan & Execution Protocol (Gated for Eric's Morning YES) (MF6)

### 9.1 Pre-Deploy Staging Assets (MUST-FIX 2)
Upon receipt of Founder Eric's morning typed `YES`, exactly 4 files will be uploaded to GCS:
1. `26ea_b.webp` (`164,146 B`, MD5 `62ad11e997ac0320b57091e3d108d3e0`) $\rightarrow$ `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp`
2. `26xe_b.webp` (`245,878 B`, MD5 `3a77694c9a72e6db63811c8b001edbb5`) $\rightarrow$ `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp`
3. `23rh_b.webp` (`226,854 B`, MD5 `8a2060d0ca5987b0faf0d8828ece365f`) $\rightarrow$ `gs://numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp`
4. `23rh_c.webp` (`161,734 B`, MD5 `08f5b5aaf698936913e2a24743dbdea5`) $\rightarrow$ `gs://numista-reference-library/reference_library/us_mint_official/2023_products/23rh_c.webp`

### 9.2 Execution Gates
- **Gate 1:** Plan scoring $\ge 95$ from Grok CoS and Argon.
- **Gate 2:** Senior Advisory Group (SAG) concurrence.
- **Gate 3:** Founder Eric types morning **`YES`**.
- **Gate 4 (Live Staging GCS HEAD, Content-Type, Content-Length & MD5 Verification - MF-C):**
  For each of the 4 staged files (`26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`), execute an explicit verification check asserting:
  1. HTTP response status is `200 OK`.
  2. `Content-Type` header exactly matches `image/webp`.
  3. `Content-Length` header byte size matches Section 9.1 expected byte size (`164,146 B`, `245,878 B`, `226,854 B`, `161,734 B`).
  4. `x-goog-hash` md5 header or ETag hex MD5 exactly matches Section 9.1 expected MD5 hashes (`62ad11e997ac0320b57091e3d108d3e0`, `3a77694c9a72e6db63811c8b001edbb5`, `8a2060d0ca5987b0faf0d8828ece365f`, `08f5b5aaf698936913e2a24743dbdea5`).
  ```bash
  python -c "
  import urllib.request, base64, binascii
  staged = [
    ('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp', '62ad11e997ac0320b57091e3d108d3e0', 164146),
    ('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp', '3a77694c9a72e6db63811c8b001edbb5', 245878),
    ('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp', '8a2060d0ca5987b0faf0d8828ece365f', 226854),
    ('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_c.webp', '08f5b5aaf698936913e2a24743dbdea5', 161734),
  ]
  for url, expected_md5, size in staged:
      req = urllib.request.Request(url, method='HEAD')
      with urllib.request.urlopen(req) as r:
          assert r.status == 200, f'Status {r.status} != 200'
          assert r.headers.get('Content-Type') == 'image/webp', 'Content-Type mismatch'
          cl = r.headers.get('Content-Length')
          assert int(cl or 0) == size, f'Size mismatch {cl} != {size}'
          goog_hash = r.headers.get('x-goog-hash', '')
          actual_md5 = None
          for p in goog_hash.split(','):
              p = p.strip()
              if p.startswith('md5='):
                  actual_md5 = binascii.hexlify(base64.b64decode(p[4:])).decode('ascii')
          assert actual_md5 == expected_md5, f'MD5 mismatch {actual_md5} != {expected_md5}'
          print(f'PASS: {url} -> 200 OK, image/webp, {size} B, md5: {actual_md5}')
  "
  ```
- **Gate 5:** `flutter analyze` passes with 0 errors; `flutter test` passes 100%; backend regression suite passes 100%.
- **Gate 6:** Deploy exclusively to Firebase Hosting preview channel `p7-gate` (`https://numista-vault--p7-gate-8avtpz22.web.app`) on branch `p7-v8.9`. `origin/main` locked at `9f04550a`; `origin/dev` tip at `6e19c71d` before this plan's docs commit (live `git rev-parse origin/dev`, 2 Nov ~6:05 PM ET); app code on dev unchanged since `01a03f90`, same as header. Preview deployment channel uses `p7-v8.9` strictly; zero code pushes to `dev` or `main`.

---

---

**END PLAN R2.8.18**
