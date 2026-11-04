# GEMINI 3.8 (ARGON) INDEPENDENT TECHNICAL REVIEW — FAIL-FIX PLAN NET-647 R2.8.8 (`NET-701`)

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Thinking, Planning & Review Jobs Only)
- **Date / Time:** 2026-11-01 ~01:02 AM EST / ~02:02 AM EDT (Well before 3 AM Stand-Down)
- **Artifact Reviewed:** [`FAILFIX_PLAN_NET-647_R2.8.8_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.8_20261101.md) (`1,097 lines`, `76,950 bytes`, filed under [`NET-701`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/RADIO_OVER_NET-701_AGCOS-to-ALL_R2.8.8-PLAN-FILED_20261101.md))
- **Grok CoS Baseline Checked:** [`COS_SCORE_NET-647_R2.8.7_89_REVISE_20261101-0120.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.7_89_REVISE_20261101-0120.md) (`NET-700`, `89/100 REVISE`)
- **Companion Firestore Dump Verified:** [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.md) & [`ERIC_ACCOUNT_28_DOCS_FIRESTORE_DUMP_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/For%20SAG/ERIC_ACCOUNT_28_DOCS_FIRESTORE_DUMP_20261101.md)
- **Operational Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero code edits, zero git commits of code, zero deploys, zero Firestore/GCS mutations.
- **Argon Score & Verdict:** **`86 / 100 — REVISE (Fix-Only R2.8.9 Required — Turnkey Code Provided Below)`**

---

## 1. Executive Summary & Empirical Simulation Findings

`AG CoS v4` addressed all 4 Must-Fix (`MF1`–`MF4`) and 5 Should-Fix (`SF1`–`SF5`) items from Grok CoS `NET-700` (`89/100 REVISE`):
- **Resolved in `R2.8.8`:**
  - **`MF1` (Row 11 / 2026-P Half Dollar Obverse):** Pointed `isP` half dollar obverse (line 260) and unit test (line 778) to live `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` (`200 OK`, `1,510,450 B`, `MD5=ec05347cabf3b134a262ac9f6631385b`).
  - **`MF2` (`23rh_c.webp` Staging):** Added `23rh_c.webp` (`161,734 B`, `MD5=08f5b5aaf698936913e2a24743dbdea5`) to Section 9.1 (4 staged files total: `26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`).
  - **`MF3` (Read-Only Firestore Field Dump):** Extracted all 28 documents from live Firestore (`ERIC_ACCOUNT_28_DOCS_FIRESTORE_DUMP_20261101.json` & `.md` and Argon's `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` & `.md`), proving SKU fields exist in Firestore on Rows 1–7 and 25–28.
  - **`MF4` (28-Row Standalone Resolver & Unit Tests):** Included `CanonicalMintAssetService`, `Canonical2026MintAssets`, `Atb50SqLincolnResolver`, and 28 row-by-row unit tests in Section 3.
  - **`SF1`–`SF5`:** Used full `reference_library/wikimedia_uscoin/...` paths (lines 818, 927–928), labeled Row 28 with both `eric@numista.ai` and `eric.seaman@yahoo.com` (line 834), gave `mint` field precedence in `isD` (lines 244, 257), added `!RegExp(r'\b(gold|platinum|palladium)\b')` to the Silver Eagle branch (line 209), and specified the penny-remainder rule (`unitCostCents + remainderCents` on final coin) and 11 intake fixtures in Sections 5–6.

**However, Argon executed a deterministic Python simulation of `R2.8.8`'s exact `CanonicalMintAssetService.resolveFromMap` code (`scratch/test_r288_sim.py`) against all 28 real Firestore documents and all 28 CSV audit rows, uncovering 4 defects (1 Critical control-flow bug, 2 Major field/branch bugs, and 1 Rule 6(a) citation regression) that MUST be fixed in `R2.8.9` before `p7-gate` execution:**

### Defect 1 (CRITICAL — Missing `if (year != '2026') return null;` Guard in `Canonical2026MintAssets.resolve` Hijacks All 12 Historical Quarters in Rows 12–17 & 19–24)
- **Where:** [`FAILFIX_PLAN_NET-647_R2.8.8_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.8_20261101.md#L118-L282) lines `118–125` and `206–282`:
  ```dart
  // Lines 118-125: Called unconditionally for ALL years:
  final mint2026 = Canonical2026MintAssets.resolve(
    sku: sku.isNotEmpty ? sku : null,
    title: title.isNotEmpty ? title : null,
    year: year.isNotEmpty ? year : null,
    mint: mint.isNotEmpty ? mint : null,
    denomination: denom.isNotEmpty ? denom : null,
  );
  if (mint2026 != null) return mint2026;
  ...
  // Lines 268-282 inside Canonical2026MintAssets.resolve (NO year == '2026' check!):
  if (RegExp(r'\bquarter\b').hasMatch(cleanTitle) || cleanDenom.contains('quarter')) {
    if (cleanTitle.contains('mayflower')) {
      return const CanonicalMintAsset(...);
    } else {
      return const CanonicalMintAsset(
        obverseUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_obverse.jpg',
        reverseUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_reverse.jpg',
        cardUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_obverse.jpg',
      );
    }
  }
  ```
- **What Happens at Runtime:**
  Because `Canonical2026MintAssets.resolve` does **not** check `if (year != '2026') return null;` before entering the 2026 title/denomination fallback branches (lines `206–300`), **every non-2026 Quarter** (`2005-D` Kansas in Row 12 and all 11 `2010–2020` ATB Quarters in Rows 13–17 and 19–24) has `cleanDenom.contains('quarter') == true`, matches line 268 (`else`), and returns `2026_quarter_dollar_declaration_of_independence_obverse.jpg`!
  - Execution **never reaches `Atb50SqLincolnResolver.resolve(...)` at line 128** for any quarter!
  - **12 of the 28 unit tests in Section 3.2 (`Row 12`–`Row 17`, `Row 19`–`Row 24`) plus `ATB Washington Undated Obverse Exemption on 2010-2021` fail at runtime!**
  - Furthermore, any historical Morgan Dollar (e.g., 1921), Peace Dollar (1922), Silver Eagle (1986–2025), Roosevelt Dime, or Kennedy Half Dollar in a user's collection would be overwritten with 2026 artwork!
- **Exact Fix for `R2.8.9`:**
  In `Canonical2026MintAssets.resolve`, immediately after the direct SKU / `23RH` checks (after line 204), add:
  ```dart
  // Guard all 2026 title/denomination fallback branches strictly to year == '2026'
  if (year != '2026') return null;
  ```

---

### Defect 2 (MAJOR — `resolveFromMap` Line 96 Misses Capital `'Year'` Key from Live Firestore Documents & `Program/Series` Fallback)
- **Where:** [`FAILFIX_PLAN_NET-647_R2.8.8_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.8_20261101.md#L96-L99) lines `96–99`:
  ```dart
  final year = (data['year'] ?? '').toString().trim();
  final mint = (data['mint'] ?? data['Mint Mark'] ?? data['mint_mark'] ?? '').toString().trim().toUpperCase();
  final title = (data['name'] ?? data['title'] ?? data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().trim();
  final denom = (data['denomination'] ?? data['Denomination'] ?? '').toString().trim();
  ```
- **What Happens at Runtime:**
  1. As proven by the live Firestore dump (`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.md` / `ERIC_ACCOUNT_28_DOCS_FIRESTORE_DUMP_20261101.json`), Firestore documents store the year under **`data['Year']`** (capital `'Y'`), NOT `data['year']`! Because line 96 only reads `data['year']`, `year` evaluates to `''` on all 28 live Firestore documents!
  2. In addition, on Rows 5, 6, 25, 27, and 28, `Theme/Subject` is empty in Firestore while `Program/Series` holds `'Uncirculated Coin Set'`, `'American Innovation'`, `'Semiquincentennial President'`, and `'Silver Proof Set'`. And if `resolveFromMap` is called on bare CSV rows (`ERIC_ACCOUNT_252_AUDIT_20261031.csv`) where SKU/notes columns are omitted, Row 6 (`year: '2026', denomination: '$1', mint: ''`) and Row 27 (`year: '2026', mint: 'D', denomination: 'Dollar'`) return `null` unless `Program/Series` and bare-CSV denomination/mint fallbacks are included.
- **Exact Fix for `R2.8.9`:**
  ```dart
  final year = (data['year'] ?? data['Year'] ?? '')
      .toString()
      .trim()
      .replaceAll(RegExp(r'\.0$'), '');
  final mint = (data['mint'] ?? data['Mint Mark'] ?? data['mint_mark'] ?? '')
      .toString()
      .trim()
      .toUpperCase();
  final title = [
    data['name'],
    data['title'],
    data['Theme/Subject'],
    data['theme_subject'],
    data['Program/Series'],
    data['program_series'],
  ].where((v) => v != null && v.toString().trim().isNotEmpty).map((v) => v.toString().trim()).join(' ');
  final denom = (data['denomination'] ?? data['Denomination'] ?? '').toString().trim();
  ```
  And in `Canonical2026MintAssets.resolve` (under `if (year == '2026')`), include bare-CSV fallbacks for Row 6 (`cleanDenom == r'$1' && cleanMint.isEmpty` $\rightarrow$ `26GC`) and Row 27 (`cleanMint == 'D' && (cleanDenom == 'dollar' || cleanDenom.isEmpty)` $\rightarrow$ `26SQRP`).

---

### Defect 3 (MAJOR — `Atb50SqLincolnResolver` Lines 322 & 331 Use `||` Instead of `&&` on `year`, Hijacking Any 2005 Coin or Any Lincoln Cent)
- **Where:** [`FAILFIX_PLAN_NET-647_R2.8.8_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.8_20261101.md#L321-L337) lines `321–337`:
  ```dart
  // 1. 2005-D Kansas State Quarter (Row 12)
  if (year == '2005' || cleanTitle.contains('kansas')) {
  ...
  // 2. 1962 Proof Lincoln Cent (Row 18)
  if (year == '1962' || cleanTitle.contains('lincoln')) {
  ```
- **What Happens at Runtime:**
  - `if (year == '2005' || cleanTitle.contains('kansas'))` matches **every 2005 coin** (e.g., 2005 Oregon Quarter, 2005 Bison Nickel, 2005 Silver Eagle) and assigns it Kansas State Quarter artwork!
  - `if (year == '1962' || cleanTitle.contains('lincoln'))` matches **every coin with `'lincoln'` in the title** regardless of year (e.g., 1909-S VDB Wheat Cent, 1943 Steel Cent, 2026 Shield Cent) and assigns it the 1962 Lincoln Memorial reverse!
- **Exact Fix for `R2.8.9`:**
  ```dart
  // 1. 2005-D Kansas State Quarter (Row 12)
  if (cleanTitle.contains('kansas')) {
    final isD = cleanMint.isEmpty || cleanMint == 'D';
    final obv = isD
        ? '$_50sqBase/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'
        : '$_atbBase/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg';
    return CanonicalMintAsset(
      obverseUrl: obv,
      reverseUrl: '$_50sqBase/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg',
      cardUrl: obv,
    );
  }

  // 2. 1962 Proof Lincoln Cent (Row 18)
  if (year == '1962' && (cleanTitle.contains('lincoln') || denomination.toLowerCase().contains('cent'))) {
    return CanonicalMintAsset(
      obverseUrl: storedObverse ?? '$_centBase/United_States_penny_2C_reverse.jpg',
      reverseUrl: '$_centBase/United_States_penny_2C_reverse.jpg',
      cardUrl: storedObverse ?? '$_centBase/United_States_penny_2C_reverse.jpg',
    );
  }
  ```

---

### Defect 4 (MINOR / GOVERNANCE — Section 7 Replaced Verbatim Repository Code Citations with Proposed Snippets, and Omitted `hasConflictingYearInBasename` + Live Fallback URLs on `CanonicalMintAsset`)
- **Where:** [`FAILFIX_PLAN_NET-647_R2.8.8_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.8_20261101.md#L1000-L1038) lines `1000–1038`:
  - Per `GEMINI.md` Rule 6(a), every `file:line` citation must paste the **actual verbatim code lines currently in the repository** alongside the proposed replacement. Section 7 of `R2.8.8` pasted only the proposed replacement snippets for `my_collection_screen.dart:6356-6402`, `coin_image_service.dart:535-570`, and `review_hub_screen.dart:2040-2059`. (We provide the exact verbatim repository blocks in Section 3 below so `AG CoS v4` can paste them straight back into Section 7 of `R2.8.9`.)
  - Also include `hasConflictingYearInBasename(String url, String coinYear)` (from `R2.8.7` lines `393–411`) in `canonical_mint_asset_service.dart` so the `ATB Washington Undated Obverse Exemption on 2010-2021 (SF-4)` unit test calls `hasConflictingYearInBasename` directly, and include `fallbackObverseUrl` / `fallbackReverseUrl` on `CanonicalMintAsset` so `23RH` (`23rh_b.webp` / `23rh_c.webp`) has a live HTTP 200 fallback (`2023_series/2023_american_women_quarters_five_honorees_composite.jpg` `711,501 B` and `2023_series/2023_american_innovation_four_states_composite.jpg` `584,055 B`) prior to Gate 4 upload (`NET-700` `MF2`).

---

## 2. Turnkey Drop-In Replacement for `R2.8.9` Section 3 (`canonical_mint_asset_service.dart` — Verified 28/28 on Live Firestore Dump AND Bare CSV Rows)

```dart
// lib/services/canonical_mint_asset_service.dart
// Complete standalone production resolver for branch p7-v8.9 (R2.8.9)

class CanonicalMintAsset {
  final String obverseUrl;
  final String reverseUrl;
  final String cardUrl;
  final String? fallbackObverseUrl;
  final String? fallbackReverseUrl;

  const CanonicalMintAsset({
    required this.obverseUrl,
    required this.reverseUrl,
    required this.cardUrl,
    this.fallbackObverseUrl,
    this.fallbackReverseUrl,
  });

  Map<String, String> toMap() => {
    'obverse': obverseUrl,
    'reverse': reverseUrl,
    'card': cardUrl,
    if (fallbackObverseUrl != null) 'fallback_obverse': fallbackObverseUrl!,
    if (fallbackReverseUrl != null) 'fallback_reverse': fallbackReverseUrl!,
  };
}

class CanonicalMintAssetService {
  /// Year-conflict basename check with ATB undated Washington obverse exemption (2010-2021).
  static bool hasConflictingYearInBasename(String url, String coinYear) {
    final uri = Uri.tryParse(url);
    final basename = (uri != null && uri.pathSegments.isNotEmpty)
        ? uri.pathSegments.last.toLowerCase()
        : url.split('/').last.toLowerCase();
    final cYear = int.tryParse(coinYear.trim());
    if (cYear != null &&
        cYear >= 2010 &&
        cYear <= 2021 &&
        basename.contains('america-the-beautiful-quarters-coin') &&
        basename.contains('obverse')) {
      return false;
    }
    final yearMatches = RegExp(r'(?:^|[^0-9])(19\d{2}|20\d{2})(?:[^0-9]|$)').allMatches(basename);
    for (final m in yearMatches) {
      final y = m.group(1);
      if (y != null && y != coinYear.trim()) {
        return true;
      }
    }
    return false;
  }

  /// Resolves canonical assets for any Eric account document (Firestore or CSV map).
  /// Returns null if authentic user photography is detected or item is outside catalog scope.
  static CanonicalMintAsset? resolveFromMap(Map<String, dynamic> data) {
    // 1. User upload guard (MUST-FIX 3): Never override authentic user microscope photography
    final storedObv = (data['image_url_obverse'] ?? '').toString();
    final storedRev = (data['image_url_reverse'] ?? '').toString();
    if (storedObv.contains('/microscope/') || storedRev.contains('/microscope/')) {
      return null;
    }

    // Dual-case read supporting both raw Firestore keys ('Year', 'Mint Mark', 'Theme/Subject', 'Program/Series')
    // and normalized/CSV keys ('year', 'mint', 'title', 'denomination').
    final year = (data['year'] ?? data['Year'] ?? '')
        .toString()
        .trim()
        .replaceAll(RegExp(r'\.0$'), '');
    final mint = (data['mint'] ?? data['Mint Mark'] ?? data['mint_mark'] ?? '')
        .toString()
        .trim()
        .toUpperCase();
    final title = [
      data['name'],
      data['title'],
      data['Theme/Subject'],
      data['theme_subject'],
      data['Program/Series'],
      data['program_series'],
    ]
        .where((v) => v != null && v.toString().trim().isNotEmpty && v.toString().trim() != 'None')
        .map((v) => v.toString().trim())
        .join(' ');
    final denom = (data['denomination'] ?? data['Denomination'] ?? '').toString().trim();

    // Extract SKU from explicit fields or notes
    String sku = (data['product_code'] ??
            data['retailer_item_num'] ??
            data['Retailer Item No.'] ??
            data['item_number'] ??
            '')
        .toString()
        .trim()
        .toUpperCase();
    if (sku.isEmpty) {
      final notes = (data['notes'] ??
              data['personal_notes'] ??
              data['Personal Notes'] ??
              data['description'] ??
              '')
          .toString();
      final m = RegExp(r'\b(?:Item\s*#?:?\s*|#\s*)([A-Za-z0-9]+)\b', caseSensitive: false)
          .firstMatch(notes);
      if (m != null) {
        sku = m.group(1)!.toUpperCase();
      } else if (notes.contains('26EA')) {
        sku = '26EA';
      } else if (notes.contains('26XE')) {
        sku = '26XE';
      } else if (notes.contains('26XL')) {
        sku = '26XL';
      } else if (notes.contains('26RJ')) {
        sku = '26RJ';
      } else if (notes.contains('26GC')) {
        sku = '26GC';
      } else if (notes.contains('26SQRP')) {
        sku = '26SQRP';
      } else if (notes.contains('23RH')) {
        sku = '23RH';
      }
    }

    // 2. Check 2026 catalog (and 2023 Silver Proof Set 23RH)
    final mint2026 = Canonical2026MintAssets.resolve(
      sku: sku.isNotEmpty ? sku : null,
      title: title.isNotEmpty ? title : null,
      year: year.isNotEmpty ? year : null,
      mint: mint.isNotEmpty ? mint : null,
      denomination: denom.isNotEmpty ? denom : null,
    );
    if (mint2026 != null) return mint2026;

    // 3. Check ATB / 50SQ / Lincoln Cent catalog (Rows 12-24)
    return Atb50SqLincolnResolver.resolve(
      year: year,
      mint: mint,
      title: title,
      denomination: denom,
      storedObverse: storedObv.isNotEmpty ? storedObv : null,
    );
  }
}

class Canonical2026MintAssets {
  static const String _mintBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official';
  static const String _bulkBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs';
  static const String _seriesBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/2026_series';
  static const String _series2023Base =
      'https://storage.googleapis.com/numista-reference-library/reference_library/2023_series';

  static CanonicalMintAsset? resolve({
    String? sku,
    String? title,
    String? year,
    String? mint,
    String? denomination,
  }) {
    final cleanSku = sku?.trim().toUpperCase();
    final cleanTitle = (title ?? '').toLowerCase().trim();
    final cleanMint = (mint ?? '').toUpperCase().trim();
    final cleanDenom = (denomination ?? '').toLowerCase().trim();

    // 1. Direct SKU Matches (and 2023 Silver Proof Set)
    if (cleanSku == '26EA') {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26ea_a.webp',
        reverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
        cardUrl: '$_mintBase/2026_products/26ea_a.webp',
        fallbackReverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
      );
    }
    if (cleanSku == '26XE') {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26xe_a.webp',
        reverseUrl: '$_bulkBase/morgan_dollar/Morgan_Dollar_Reverse.jpg',
        cardUrl: '$_mintBase/2026_products/26xe_a.webp',
        fallbackReverseUrl: '$_bulkBase/morgan_dollar/Morgan_Dollar_Reverse.jpg',
      );
    }
    if (cleanSku == '26XL') {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26xl___a.webp',
        reverseUrl: '$_bulkBase/peace_dollar/Peace_dollar_reverse.jpg',
        cardUrl: '$_mintBase/2026_products/26xl___a.webp',
      );
    }
    if (cleanSku == '26RJ') {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26rj_a.webp',
        reverseUrl: '$_mintBase/2026_products/26rj_a.webp',
        cardUrl: '$_mintBase/2026_products/26rj_a.webp',
      );
    }
    if (cleanSku == '26SQRP') {
      return const CanonicalMintAsset(
        obverseUrl: '$_seriesBase/2026_trump_presidential_dollar_obverse.jpg',
        reverseUrl: '$_seriesBase/2026_trump_presidential_dollar_reverse.jpg',
        cardUrl: '$_seriesBase/2026_trump_presidential_dollar_obverse.jpg',
      );
    }
    if (cleanSku == '26GC') {
      return const CanonicalMintAsset(
        obverseUrl: '$_seriesBase/2026_american_innovation_dollar_obverse.jpg',
        reverseUrl: '$_seriesBase/2026_american_innovation_dollar_reverse.jpg',
        cardUrl: '$_seriesBase/2026_american_innovation_dollar_obverse.jpg',
      );
    }
    if (cleanSku == '23RH' || (year == '2023' && cleanDenom.contains('set'))) {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2023_products/23rh_b.webp',
        reverseUrl: '$_mintBase/2023_products/23rh_c.webp',
        cardUrl: '$_mintBase/2023_products/23rh_b.webp',
        fallbackObverseUrl:
            '$_series2023Base/2023_american_women_quarters_five_honorees_composite.jpg',
        fallbackReverseUrl:
            '$_series2023Base/2023_american_innovation_four_states_composite.jpg',
      );
    }

    // CRITICAL YEAR GUARD: All fallback branches below apply strictly to 2026 items
    // so non-2026 coins (e.g. 2005 Kansas 50SQ, 2010-2020 ATB Quarters) fall through
    // to Atb50SqLincolnResolver.
    if (year != '2026') return null;

    // 2. 2026 Title & Denomination Fallback Branches
    // SF4: Silver guard on Eagle pattern
    final isSilverEagle =
        RegExp(r'\b(silver eagle|american eagle)\b').hasMatch(cleanTitle) ||
        (RegExp(r'\beagle\b').hasMatch(cleanTitle) &&
            !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(cleanTitle));
    if (isSilverEagle || (cleanTitle.contains('america250') && cleanMint == 'W')) {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26ea_a.webp',
        reverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
        cardUrl: '$_mintBase/2026_products/26ea_a.webp',
      );
    }

    if (RegExp(r'\bmorgan\b').hasMatch(cleanTitle)) {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26xe_a.webp',
        reverseUrl: '$_bulkBase/morgan_dollar/Morgan_Dollar_Reverse.jpg',
        cardUrl: '$_mintBase/2026_products/26xe_a.webp',
      );
    }

    if (RegExp(r'\bpeace\b').hasMatch(cleanTitle) ||
        (cleanTitle.contains('america250') && cleanMint == 'P')) {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26xl___a.webp',
        reverseUrl: '$_bulkBase/peace_dollar/Peace_dollar_reverse.jpg',
        cardUrl: '$_mintBase/2026_products/26xl___a.webp',
      );
    }

    if (RegExp(r'\b(trump|presidential|semiquincentennial president)\b').hasMatch(cleanTitle) ||
        (cleanMint == 'D' && (cleanDenom == 'dollar' || cleanDenom.isEmpty))) {
      return const CanonicalMintAsset(
        obverseUrl: '$_seriesBase/2026_trump_presidential_dollar_obverse.jpg',
        reverseUrl: '$_seriesBase/2026_trump_presidential_dollar_reverse.jpg',
        cardUrl: '$_seriesBase/2026_trump_presidential_dollar_obverse.jpg',
      );
    }

    // SF3: Mint field wins over title for Dime
    if (RegExp(r'\bdime\b').hasMatch(cleanTitle) ||
        cleanDenom.contains('dime') ||
        RegExp(r'\broosevelt\b').hasMatch(cleanTitle)) {
      final isD = cleanMint.isNotEmpty
          ? (cleanMint == 'D')
          : (cleanTitle.contains('-d') || cleanTitle.contains(' denver'));
      final obv = isD
          ? '$_bulkBase/roosevelt_dime/SemiQ-Dime-Obverse-Unc-D.jpg'
          : '$_bulkBase/roosevelt_dime/SemiQ-Dime-Obverse-Unc-P.jpg';
      return CanonicalMintAsset(
        obverseUrl: obv,
        reverseUrl: '$_bulkBase/roosevelt_dime/SemiQ-Dime-Reverse-Unc.jpg',
        cardUrl: obv,
      );
    }

    // SF3 & MF1: Mint field wins over title for Half Dollar; P obverse resolves live 2026 asset
    if (RegExp(r'\bhalf(\s+dollar)?\b').hasMatch(cleanTitle) ||
        cleanDenom.contains('half') ||
        cleanTitle.contains('250th anniversary of american independence')) {
      final isD = cleanMint.isNotEmpty
          ? (cleanMint == 'D')
          : (cleanTitle.contains('-d') || cleanTitle.contains(' denver'));
      final obv = isD
          ? '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'
          : '$_seriesBase/2026_half_dollar_enduring_liberty_obverse.jpg';
      return CanonicalMintAsset(
        obverseUrl: obv,
        reverseUrl: '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg',
        cardUrl: obv,
      );
    }

    if (RegExp(r'\bquarter\b').hasMatch(cleanTitle) || cleanDenom.contains('quarter')) {
      if (cleanTitle.contains('mayflower')) {
        return const CanonicalMintAsset(
          obverseUrl: '$_seriesBase/2026_quarter_dollar_mayflower_compact_obverse.jpg',
          reverseUrl: '$_seriesBase/2026_quarter_dollar_mayflower_compact_reverse.jpg',
          cardUrl: '$_seriesBase/2026_quarter_dollar_mayflower_compact_obverse.jpg',
        );
      } else {
        return const CanonicalMintAsset(
          obverseUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_obverse.jpg',
          reverseUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_reverse.jpg',
          cardUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_obverse.jpg',
        );
      }
    }

    if (RegExp(r'\binnovation\b').hasMatch(cleanTitle) ||
        ((cleanDenom == r'$1' || cleanDenom == '1 dollar') && cleanMint.isEmpty)) {
      return const CanonicalMintAsset(
        obverseUrl: '$_seriesBase/2026_american_innovation_dollar_obverse.jpg',
        reverseUrl: '$_seriesBase/2026_american_innovation_dollar_reverse.jpg',
        cardUrl: '$_seriesBase/2026_american_innovation_dollar_obverse.jpg',
      );
    }

    // Set check evaluated strictly after individual coins
    if (RegExp(r'\b(uncirculated set|mint set|coin set|uncirculated coin set)\b')
            .hasMatch(cleanTitle) ||
        cleanDenom.contains('set')) {
      return const CanonicalMintAsset(
        obverseUrl: '$_mintBase/2026_products/26rj_a.webp',
        reverseUrl: '$_mintBase/2026_products/26rj_a.webp',
        cardUrl: '$_mintBase/2026_products/26rj_a.webp',
      );
    }

    return null;
  }
}

class Atb50SqLincolnResolver {
  static const String _atbBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters';
  static const String _50sqBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters';
  static const String _centBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/Lincoln_Memorial_cent';

  static CanonicalMintAsset? resolve({
    required String year,
    required String mint,
    required String title,
    required String denomination,
    String? storedObverse,
  }) {
    final cleanTitle = title.toLowerCase().trim();
    final cleanMint = mint.toUpperCase().trim();

    // 1. 2005-D Kansas State Quarter (Row 12)
    if (cleanTitle.contains('kansas')) {
      final isD = cleanMint.isEmpty || cleanMint == 'D';
      final obv = isD
          ? '$_50sqBase/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'
          : '$_atbBase/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg';
      return CanonicalMintAsset(
        obverseUrl: obv,
        reverseUrl: '$_50sqBase/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg',
        cardUrl: obv,
      );
    }

    // 2. 1962 Proof Lincoln Cent (Row 18)
    if (year == '1962' &&
        (cleanTitle.contains('lincoln') || denomination.toLowerCase().contains('cent'))) {
      return CanonicalMintAsset(
        obverseUrl: storedObverse ?? '$_centBase/United_States_penny_2C_reverse.jpg',
        reverseUrl: '$_centBase/United_States_penny_2C_reverse.jpg',
        cardUrl: storedObverse ?? '$_centBase/United_States_penny_2C_reverse.jpg',
      );
    }

    // 3. America the Beautiful (ATB) Quarters (Rows 13-17, 19, 20-24)
    const Map<String, String> atbParks = {
      'american memorial':
          '2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg',
      'salt river':
          '2020-america-the-beautiful-quarters-coin-salt-river-bay-national-historical-park-and-ecological-preserve-u-s--virgin-islands-uncirculated-reverse.jpg',
      'mount rushmore':
          '2013-america-the-beautiful-quarters-coin-mount-rushmore-national-memorial-south-dakota-uncirculated-reverse.jpg',
      'cumberland island':
          '2018-america-the-beautiful-quarters-coin-cumberland-island-national-seashore-georgia-uncirculated-reverse.jpg',
      'block island':
          '2018-america-the-beautiful-quarters-coin-block-island-national-wildlife-refuge-rhode-island-uncirculated-reverse.jpg',
      'san antonio':
          '2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg',
      'effigy mounds':
          '2017-america-the-beautiful-quarters-coin-effigy-mounds-national-monument-iowa-uncirculated-reverse.jpg',
      'frederick douglass':
          '2017-america-the-beautiful-quarters-coin-frederick-douglass-national-historic-site-district-of-columbia-uncirculated-reverse.jpg',
      'yellowstone':
          '2010-america-the-beautiful-quarters-coin-yellowstone-national-park-wyoming-uncirculated-reverse.jpg',
      'george rogers clark':
          '2017-america-the-beautiful-quarters-coin-george-rogers-clark-national-historical-park-indiana-uncirculated-reverse.jpg',
      'ozark':
          '2017-america-the-beautiful-quarters-coin-ozark-national-scenic-riverways-missouri-uncirculated-reverse.jpg',
    };

    for (final entry in atbParks.entries) {
      if (cleanTitle.contains(entry.key)) {
        final String obvFile;
        if (cleanMint == 'D') {
          obvFile = '2011-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg';
        } else if (cleanMint == 'W') {
          obvFile =
              '2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-obverse.jpg';
        } else {
          obvFile = '2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg';
        }
        return CanonicalMintAsset(
          obverseUrl: '$_atbBase/$obvFile',
          reverseUrl: '$_atbBase/${entry.value}',
          cardUrl: '$_atbBase/$obvFile',
        );
      }
    }

    return null;
  }
}
```

---

## 3. Verbatim Repository Code Citations (`GEMINI.md` Rule 6a) — Drop-In Replacement for Section 7 of `R2.8.9`

### 3.1 [`numista_mobile/lib/screens/my_collection_screen.dart:6356-6402`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6356-L6402)
```dart
  @override
  Widget build(BuildContext context) {
    final obv = _cleanUrl(data[_F.imageObverse]);
    final rev = _cleanUrl(data[_F.imageReverse]);
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

### 3.2 [`numista_mobile/lib/screens/my_collection_screen.dart:3016-3022`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3022)
```dart
        final valCpg = _parseNumber(m['cpgRetail']);
        final finalVal = valCpg;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (m[_F.aiValue]?.toString() ?? '—');
```

### 3.3 [`numista_mobile/lib/services/coin_image_service.dart:535-570`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L570)
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

### 3.4 [`numista_mobile/lib/screens/review_hub_screen.dart:2040-2059`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2040-L2059)
```dart
                    final rawCost = data['Purchase Cost'] ?? data['Cost'];
                    final qtyVal = data['Quantity'] ?? data['qty'];
                    final cleanQty = qtyVal != null ? int.tryParse(qtyVal.toString()) ?? 1 : 1;

                    String costStr;
                    if (cleanQty > 1) {
                      if (data['unit_cost_cents'] != null) {
                        costStr = '\$${((data['unit_cost_cents'] as num) / 100.0).toStringAsFixed(2)} each';
                      } else if (data['unit_cost'] != null && data['unit_cost'] is num) {
                        costStr = '\$${formatCurrency(data['unit_cost'] as num)} each';
                      } else if (data['line_total'] != null && data['line_total'] is num) {
                        costStr = '\$${formatCurrency((data['line_total'] as num) / cleanQty)} each';
                      } else if (rawCost != null && rawCost is num) {
                        costStr = '\$${formatCurrency(rawCost)} each';
                      } else if (rawCost != null && num.tryParse(rawCost.toString()) != null) {
                        costStr = '\$${formatCurrency(num.parse(rawCost.toString()))} each';
                      } else {
                        costStr = rawCost != null ? '$rawCost each' : 'N/A';
                      }
                    } else {
```

### 3.5 [`numista_backend/main.py:8063-8071`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8063-L8071)
```python
                    per_file[idx]["status"]      = "done"
                    per_file[idx]["coins_added"] = added_this_file
                    per_file[idx]["receipt_id"]  = receipt_id

                except Exception as e:
                    per_file[idx]["status"] = "error"
                    per_file[idx]["error"]  = str(e)
                    logger.error(f"Bulk import invoice error ({fname}): {e}\n{traceback.format_exc()}")
```

---

## 4. Scoring Breakdown (`R2.8.8`)

| Dimension | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. `NET-700` Must-Fix & Should-Fix Coverage (`MF1`–`MF4`, `SF1`–`SF5`)** | 30 | **28 / 30** | All 9 items addressed structurally; live Firestore dump attached (`MF3`); 4 staged files in §9.1 (`MF2`); `isP` half dollar pointed to live `1,510,450 B` asset (`MF1`). |
| **2. Resolver Control-Flow & Runtime Correctness** | 30 | **19 / 30** | Missing `if (year != '2026') return null;` in `Canonical2026MintAssets.resolve` causes Rows 12–17 & 19–24 to return `2026_quarter_dollar_declaration_of_independence_obverse.jpg` instead of reaching `Atb50SqLincolnResolver` (-7); missing `data['Year']` capital key on line 96 (-2); `||` instead of `&&` on lines 322 & 331 (-2). |
| **3. 28-Row Audit Table & GCS HTTP 200 / Byte Integrity** | 25 | **25 / 25** | All 28 rows in §4 and all 39 live assets + 4 staged assets in §4.1.3 verified. |
| **4. Governance & Rule 6(a) Citation Compliance** | 15 | **14 / 15** | Zero code/Firestore/GCS mutations; Section 7 needs actual verbatim repository code lines restored alongside proposed diff (-1). |
| **TOTAL** | **100** | **`86 / 100`** | **`REVISE (Fix-Only R2.8.9 — Turnkey Code Provided in §2 & §3)`** |

**OVER.**
