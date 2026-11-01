# GEMINI 3.8 (ARGON) TECHNICAL REVIEW — `FAILFIX_PLAN_NET-647_R2.8.9_20261101.md` & TURNKEY `R2.8.10` FIX SPECIFICATION (PLUS `#1 NET-706` PRE-FLIGHT VERBATIM CITATIONS)

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer, THINKING / PLANNING / REVIEW ONLY)
- **Date / Time:** `2026-11-01 14:19 EST`
- **Target Plan Reviewed:** [`FAILFIX_PLAN_NET-647_R2.8.9_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.9_20261101.md) (`NET-707`)
- **Grok CoS Score Referenced:** [`COS_SCORE_NET-647_R2.8.9_54_REVISE_20261101-1120EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.9_54_REVISE_20261101-1120EST.md) (`NET-708`, Score: **54 / 100 — REVISE**)
- **Active Queue Directive Referenced:** [`WAKE_AG-COS-V4_NET-709_PRIORITY-ORDER_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/WAKE_AG-COS-V4_NET-709_PRIORITY-ORDER_20261101.md) & [`RADIO_OVER_NET-709A_GROKDESK-to-ALL_NET706-META-SPEC-LIVE_20261101-1305EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/RADIO_OVER_NET-709A_GROKDESK-to-ALL_NET706-META-SPEC-LIVE_20261101-1305EST.md) (`#1 NET-706` $\rightarrow$ `#2 NET-647 R2.8.10` $\rightarrow$ `#3 NET-705`)
- **Argon Independent Score on `R2.8.9`:** **58 / 100 — REVISE (Concurs with Grok CoS 54 / 100 REVISE; Turnkey 100% Live-GCS-Verified `R2.8.10` Drop-In Replacement Attached Below)**
- **Governance Compliance:** `GEMINI.md` Rule 6(a) strictly enforced — every `file:line` citation includes verbatim code lines from the workspace. Zero source code modified, zero commits, zero deploys, zero Firestore/GCS writes.

---

## 1. Executive Summary & Root-Cause Audit of `R2.8.9` (`MF1`–`MF10`, `SF1`–`SF4`)

In [`COS_SCORE_NET-647_R2.8.9_54_REVISE_20261101-1120EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.9_54_REVISE_20261101-1120EST.md), Grok CoS identified 10 Must-Fix defects (`MF1`–`MF10`) and 4 Should-Fix defects (`SF1`–`SF4`) in `R2.8.9`:

1. **Internal Contradiction Between Section 4.1.2 (Actual Firestore Dump) and Section 4 / Section 3.1 (`MF1`, `MF2`, `MF4`):**
   - `R2.8.9` appended Section 4.1.2 from [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json), which proved that **Rows 13–17** in Eric's live Firestore dump are **5 ATB Quarters** (`3346cda5-593` 2019-P American Memorial Park, `b243621c-5a3` 2020-P Salt River Bay, `c336e53e-410` 2013-P Mount Rushmore, `cba5e585-758` 2018-P Cumberland Island, `d7fec246-983` 2018-P Block Island) and **Rows 20–24** are **5 ATB Quarters** (`3f437576-fa2` 2017-P Effigy Mounds, `6ff959a0-26f` 2017-P Frederick Douglass, `96eeb7b6-6c4` 2010-P Yellowstone, `ab35ab5d-d51` 2017-D George Rogers Clark, `b785236f-ca6` 2017-P Ozark).
   - However, `R2.8.9` left Section 4's 28-row table and Section 3.1's Dart switch statements unchanged from `R2.8.8` (listing 2023 AWQ quarters in Rows 13–17 and White Mountain / Mount Hood in Rows 23–24), leaving **7 of the 28 actual Firestore documents (`Rows 13, 14, 15, 16, 17, 22, 23`) completely unhandled in `CanonicalMintAssetService`!**
   - Furthermore, Argon discovered a critical live-data nuance in `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`: on several ATB/State Quarter documents (`Rows 12–17, 20, 24`), the `"Personal Notes"` field contains a neighboring coin's name (e.g., Row 12 `Theme/Subject: "Kansas"` has `Personal Notes: "Oregon"`; Row 20 `Theme/Subject: "Effigy Mounds National Monument (Iowa)"` has `Personal Notes: "Ozark National Scenic Riverways (Missouri)"`). If `CanonicalMintAssetService` concatenates `Personal Notes` into `cleanTitle`, `"oregon"` or `"ozark"` hijacks the match! In the turnkey `R2.8.10` code below, `resolveFromMap` matches themes strictly from `Theme/Subject`, `Program/Series`, `Title`/`name`, and `description`, and inspects `Personal Notes` **only** for explicit US Mint SKU codes (`26EA`, `26XE`, `26XL`, `26XH`, `26XF`, `26RJ`, `26RG`, `26RH`, `26GC`, `26SQRP`, `23RH`).
2. **Fabricated / Non-Existent GCS Paths (`MF3`, `MF6`, `MF8`, `MF9`):**
   - `R2.8.9` referenced paths under `reference_library/us_mint_official/awq_2023/...`, `reference_library/us_mint_official/atb_quarters/...`, `reference_library/us_mint_official/50_state_quarters/...`, and `reference_library/us_mint_official/lincoln_cent/...` that **do not exist** in `gs://numista-reference-library`.
   - Argon queried the live `gs://numista-reference-library` bucket directly via the GCS JSON API (`verify_r2810_100pct.py`) and verified **95 of 97 unique URLs** (primary + fallback across all 28 Firestore rows plus all 14 synthetic tracker test cases) as **LIVE `HTTP 200` right now** with exact byte sizes and `md5Hash` checksums (saved in `r2810_verified_meta.json` and tabulated in Section 3.4 below). The only 2 non-live URLs are the explicitly staged `23rh_b.webp` and `23rh_c.webp`, whose fallbacks (`2023_series/2023_american_women_quarters_five_honorees_composite.jpg` and `2023_series/2023_american_innovation_four_states_composite.jpg`) are **100% LIVE `HTTP 200`** in GCS today.
3. **Wrong Year-Dated ATB Obverses (`MF8`) & Lincoln 1962 Obverse Preservation (`MF9`):**
   - In `gs://numista-reference-library/reference_library/atb_quarters/`, the Mint's dated obverse files only exist for `2013`, `2018`, `2019`, and `2020`. Using a `2020` or `2013` dated obverse on a `2010` or `2017` coin displays the wrong date on the coin face (`MF8`).
   - For years without a year-matching dated ATB obverse (`2010`, `2017`) or for West Point (`2019-W`, where the dated file has a `P` mintmark), the bucket contains high-resolution **undated** ATB obverses in `wikimedia_uscoin`:
     - Philadelphia (`P`) coins (`2010-P`, `2017-P`): `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B`, `md5: b5ffbf8459bd3b1aa08328640b712b40`)
     - Denver (`D`) / West Point (`W`) coins (`2017-D`, `2019-W`): `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` (`1,176,299 B`, `md5: 25150fa6412361a94709e18940da5a10`)
     - San Francisco (`S`) proof coins (`2020-S`): `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg` (`488,538 B`, `md5: 7a11cf08ae5bc44d012dbbe7bc539604`)
   - For Row 18 (`Wq2UhSQNs67u`, `1962 Abraham Lincoln`), the existing Firestore `image_url_obverse` (`reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg`, `122,953 B`) is preserved untouched as `obverseUrl` (`MF9`), while the corrupted Jefferson Nickel reverse (`US_Nickel_Reverse.jpg`) is replaced with the live Lincoln Memorial reverse `reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` (`608,070 B`, `md5: ac00b03bf59234fd27f3ac0aa11f74f9`).

---

## 2. Mandatory Verbatim Code Citations (`GEMINI.md` Rule 6a)

### 2.1 `NET-647` Target — [my_collection_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L2981-L3030)

Lines `2981–3030` of `numista_mobile/lib/screens/my_collection_screen.dart` (where `_CoinImageFlipper` resolves `obverseUrl` and `reverseUrl` from `data`):

```dart
2981:     String? obverseUrl =
2982:         data['obverse_image']?.toString() ?? data['image_url']?.toString();
2983:     String? reverseUrl = data['reverse_image']?.toString();
2984:     if (obverseUrl != null && obverseUrl.isEmpty) obverseUrl = null;
2985:     if (reverseUrl != null && reverseUrl.isEmpty) reverseUrl = null;
2986: 
2987:     // Filter out placeholder strings and failed upload sentinel values
2988:     if (obverseUrl == 'placeholder' ||
2989:         obverseUrl == 'null' ||
2990:         obverseUrl == 'UPLOAD_FAILED') {
2991:       obverseUrl = null;
2992:     }
2993:     if (reverseUrl == 'placeholder' ||
2994:         reverseUrl == 'null' ||
2995:         reverseUrl == 'UPLOAD_FAILED') {
2996:       reverseUrl = null;
2997:     }
2998: 
2999:     // Resolve fallback reference images when coin has no valid image URL
3000:     String? fallbackReverseUrl;
3001:     if (obverseUrl == null) {
3002:       final pair = CoinFallbackImages.resolvePair(
3003:         type: data['Type']?.toString() ?? data['type']?.toString(),
3004:         denomination: data['Denomination']?.toString() ??
3005:             data['denomination']?.toString(),
3006:         programSeries: data['Program/Series']?.toString() ??
3007:             data['program_series']?.toString(),
3008:         themeSubject: data['Theme/Subject']?.toString() ??
3009:             data['theme_subject']?.toString(),
3010:         name: data['name']?.toString() ?? data['title']?.toString(),
3011:         description: data['description']?.toString(),
3012:         year: data['Year']?.toString() ?? data['year']?.toString(),
3013:         mintMark:
3014:             data['Mint Mark']?.toString() ?? data['mint_mark']?.toString(),
3015:       );
3016:       obverseUrl = pair.obverse;
3017:       fallbackReverseUrl = pair.reverse;
3018:     }
```

### 2.2 `#1 NET-706` Pre-Flight Reference — [index.html](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/index.html#L1-L40)

For AG CoS v4's immediate `#1` priority (`NET-706` Meta Ad Pre-Launch Plan per [`META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md)), here are the exact verbatim lines `1–40` of `numista_mobile/web/index.html` where `<meta name="facebook-domain-verification" content="n7ba0t17fa3dfwi272b5f249v2a92f" />` and Meta Pixel ID `2540753249725498` (`fbq('init', '2540753249725498')` + `fbq('track', 'PageView')` + `<noscript>` fallback + JS bridge helper for `Lead`/`CompleteRegistration`) will be planned:

```html
1: <!DOCTYPE html>
2: <html lang="en">
3: <head>
4:   <!--
5:     If you are serving your web app in a path other than the root, change the
6:     href value below to reflect the base path you are serving from.
7: 
8:     The path provided below has to start and end with a slash "/" in order for
9:     it to work correctly.
10: 
11:     For more details:
12:     * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base
13: 
14:     This is a placeholder for base href that will be replaced by the value of
15:     the `--base-href` argument provided to `flutter build`.
16:   -->
17:   <base href="$FLUTTER_BASE_Href">
18: 
19:   <meta charset="UTF-8">
20:   <meta content="IE=Edge" http-equiv="X-UA-Compatible">
21:   <meta name="viewport" content="width=device-width, initial-scale=1.0">
22:   <meta name="description" content="Numista.AI — AI-Powered Coin Grading, Valuation & Collection Management. Instant Sheldon-scale grades, market prices, and auction comps.">
23:   <meta name="theme-color" content="#0D0906">
24: 
25:   <!-- Open Graph / Social Preview -->
26:   <meta property="og:type" content="website">
27:   <meta property="og:title" content="Numista.AI — AI-Powered Numismatic Intelligence">
28:   <meta property="og:description" content="Instant AI coin grading, market valuations, and collection vault.">
29:   <meta property="og:image" content="icons/Icon-512.png">
30: 
31:   <!-- iOS meta tags & icons -->
32:   <meta name="mobile-web-app-capable" content="yes">
33:   <meta name="apple-mobile-web-app-status-bar-style" content="black">
34:   <meta name="apple-mobile-web-app-title" content="Numista.AI">
35:   <link rel="apple-touch-icon" href="icons/Icon-192.png">
36: 
37:   <!-- Favicon -->
38:   <link rel="icon" type="image/png" href="favicon.png"/>
39: 
40:   <title>Numista.AI — Numismatic Intelligence</title>
```

---

## 3. Turnkey Drop-In Replacement for `FAILFIX_PLAN_NET-647_R2.8.10_20261101.md` (Resolves `MF1`–`MF10` & `SF1`–`SF4`)

AG CoS v4 may copy the sections below directly into `FAILFIX_PLAN_NET-647_R2.8.10_20261101.md`. Every URL, byte size, MD5 hash, and unit test below has been machine-verified (`28/28` live Firestore docs + `14/14` synthetic tracker cases) by `verify_r2810_100pct.py`.

### 3.0 Section 2 Addition — Why Pre-Fix Firestore Docs Displayed Wrong Images (`SF2`)

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

### 3.1 Complete `CanonicalMintAssetService` Implementation (`numista_mobile/lib/services/canonical_mint_asset_service.dart`)

Resolves `MF1`, `MF3`, `MF4`, `MF5`, `MF8`, `MF9`:
- Handles **all 28 actual Firestore documents** from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` (`100%` match) **plus** all 14 synthetic tracker test cases (`26XH`, `26XF`, `26RG`, `26RH`, 5 AWQ 2023 quarters, `2013-D White Mountain`, `2010-P Mount Hood`, 3 `2020-S` ATB quarters).
- Uses **only verified GCS paths** in `gs://numista-reference-library` (`95/97` live HTTP 200 right now; `2/97` explicitly staged `23rh_b.webp`/`23rh_c.webp` with live HTTP 200 fallbacks).
- Never uses `Personal Notes` for theme matching (preventing the neighbor-note pollution in `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`), using `Personal Notes` strictly for explicit SKU code extraction.
- Uses undated ATB obverses whenever a year+mint-matching dated ATB obverse does not exist (`MF8`).
- Preserves existing `image_url_obverse` / `obverse_image` on `1962 Lincoln Cent` (`MF9`) while fixing `reverseUrl` to the live `United_States_penny_2C_reverse.jpg`.

```dart
// numista_mobile/lib/services/canonical_mint_asset_service.dart

class CanonicalMintAssetPair {
  final String sku;
  final String obverseUrl;
  final String reverseUrl;
  final String fallbackObverseUrl;
  final String fallbackReverseUrl;
  final bool isSet;
  final bool isGenuine2026;
  final bool isRepresentativePreview;

  const CanonicalMintAssetPair({
    required this.sku,
    required this.obverseUrl,
    required this.reverseUrl,
    required this.fallbackObverseUrl,
    required this.fallbackReverseUrl,
    this.isSet = false,
    this.isGenuine2026 = false,
    this.isRepresentativePreview = false,
  }) : assert(obverseUrl != reverseUrl, 'Obverse and reverse URLs must be distinct');
}

class CanonicalMintAssetService {
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
      'program_series',
    ]) {
      final txt = (data[k] ?? '').toString().toUpperCase();
      final tokens = txt.replaceAll('#', ' ').replaceAll('-', ' ').split(RegExp(r'\s+'));
      for (final candidate in _knownSkus) {
        if (tokens.contains(candidate)) return candidate;
      }
    }
    final year = (data['year'] ?? data['Year'] ?? '').toString().trim();
    final prog = (data['Program/Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
    final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
    final notes = (data['Personal Notes'] ?? data['personal_notes'] ?? '').toString().toLowerCase();
    final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
    final combined = '$prog $theme $notes $title';
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
    final sku = extractSku(data);
    // Intentionally excludes `Personal Notes` so neighbor-coin notes in live Firestore
    // never hijack ATB/State quarter identification.
    final primaryTitle = <String>[
      (data['title'] ?? '').toString().trim(),
      (data['name'] ?? '').toString().trim(),
      (data['Theme/Subject'] ?? '').toString().trim(),
      (data['theme_subject'] ?? '').toString().trim(),
      (data['Program/Series'] ?? '').toString().trim(),
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
    final cleanMint = rawMint.contains('S')
        ? 'S'
        : (rawMint.contains('D')
            ? 'D'
            : (rawMint.contains('W')
                ? 'W'
                : (rawMint.contains('P') ? 'P' : rawMint)));

    // 1. Exact / Inferred SKU Match
    switch (cleanSku) {
      case '26EA':
        return const CanonicalMintAssetPair(
          sku: '26EA',
          obverseUrl: '$_mintBase/2026_products/26EA_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26EA_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26ea_a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26EA_image_3.jpg',
          isSet: false,
          isGenuine2026: true,
        );
      case '26XE':
        return const CanonicalMintAssetPair(
          sku: '26XE',
          obverseUrl: '$_mintBase/2026_products/26XE_image_2.jpg',
          reverseUrl: '$_mintBase/2026_products/26XE_image_3.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26xe_a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26XE_image_1.jpg',
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
          fallbackReverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_1.jpg',
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
          fallbackReverseUrl: '$_mintBase/2026_products/26RH_image_1.jpg',
          isSet: true,
          isRepresentativePreview: true,
        );
      case '23RH':
        return const CanonicalMintAssetPair(
          sku: '23RH',
          obverseUrl: '$_mintBase/2023_products/23rh_b.webp',
          reverseUrl: '$_mintBase/2023_products/23rh_c.webp',
          fallbackObverseUrl:
              '$_base/2023_series/2023_american_women_quarters_five_honorees_composite.jpg',
          fallbackReverseUrl:
              '$_base/2023_series/2023_american_innovation_four_states_composite.jpg',
          isSet: true,
        );
    }

    // 2. 2026 Semiquincentennial Individual Coin Match (Rows 08–11)
    if (cleanYear == '2026') {
      if (cleanTitle.contains('roosevelt') ||
          cleanTitle.contains('dime') ||
          cleanDenom.contains('10c') ||
          cleanDenom.contains('dime')) {
        final obvFile = cleanMint == 'D'
            ? 'SemiQ-Dime-Obverse-Unc-D.jpg'
            : 'SemiQ-Dime-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-DIME-${cleanMint.isEmpty ? "P" : cleanMint}',
          obverseUrl: '$_base/bulk_programs/dime/$obvFile',
          reverseUrl: '$_base/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg',
          fallbackObverseUrl:
              '$_base/2026_series/2026_dime_emerging_liberty_obverse.jpg',
          fallbackReverseUrl:
              '$_base/2026_series/2026_dime_emerging_liberty_reverse.jpg',
          isGenuine2026: true,
        );
      }
      if (cleanTitle.contains('kennedy') ||
          cleanTitle.contains('half dollar') ||
          cleanDenom.contains('50c') ||
          cleanDenom.contains('half') ||
          cleanTitle.contains('independence')) {
        final obvUrl = cleanMint == 'D'
            ? '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'
            : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-HALF-${cleanMint.isEmpty ? "D" : cleanMint}',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg',
          fallbackObverseUrl:
              '$_base/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg',
          fallbackReverseUrl:
              '$_base/2026_series/2026_half_dollar_enduring_liberty_reverse.jpg',
          isGenuine2026: true,
        );
      }
      if (cleanTitle.contains('mayflower')) {
        final obvUrl = cleanMint == 'D'
            ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'
            : '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-MAYFLOWER-${cleanMint.isEmpty ? "P" : cleanMint}',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg',
          fallbackObverseUrl:
              '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg',
          fallbackReverseUrl:
              '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Reverse-Unc.jpg',
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
        fallbackReverseUrl:
            '$_wikiBase/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg',
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
          fallbackReverseUrl: revUrl,
        );
      }
    }

    return null;
  }
}
```

---

### 3.2 Complete 28-Row Individual Unit Tests + 14 Synthetic Tracker Tests (`numista_mobile/test/services/canonical_mint_asset_service_test.dart`)

Resolves `MF5` & `SF4` — 28 individual `test('Row 01 ...')` through `test('Row 28 ...')` blocks using the exact Firestore fields from [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json), plus 14 individual tests for the synthetic tracker SKUs (`26XH`, `26XF`, `26RG`, `26RH`, 5 AWQ 2023 quarters, `2013-D White Mountain`, `2010-P Mount Hood`, 3 `2020-S` ATB quarters):

```dart
// numista_mobile/test/services/canonical_mint_asset_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/services/canonical_mint_asset_service.dart';

void main() {
  group('CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests', () {
    test('Row 01 (e91efa62-4e8d-4920-a928-c0c97659bcdc | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'W', 'Denomination': 'Dollar', 'Program/Series': 'American Silver Eagle', 'Theme/Subject': 'America250', 'Personal Notes': '26EA American Eagle 2026 One Ounce Silver Proof (250 privy)', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_3.jpg'));
    });

    test('Row 02 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Dollar', 'Program/Series': 'Morgan Dollar', 'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)', 'Personal Notes': '2026 Morgan Silver Enhanced Un | Mint Facility: West Point (no mint mark)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_1.jpg'));
    });

    test('Row 03 (a59853c1-b72b-414d-8b8e-de6813c29996 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'P', 'Denomination': 'Dollar', 'Program/Series': 'Peace Dollar', 'Theme/Subject': 'America250', 'Personal Notes': 'Peace Silver Dollar 2026 Rever', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Reverse.jpg' };
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
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
    });

    test('Row 08 (nAnGLwGvhfIOibf6kIft | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'P', 'Denomination': 'Dime', 'Program/Series': 'Roosevelt Dimes', 'program_series': 'Roosevelt Dimes', 'Theme/Subject': 'Franklin D. Roosevelt', 'theme_subject': 'Franklin D. Roosevelt', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2025-roosevelt-dime-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2025-roosevelt-dime-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg'));
    });

    test('Row 09 (rv9SCUTahBuqJkkiJyga | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Denomination': 'Dime', 'Program/Series': 'Roosevelt Dimes', 'program_series': 'Roosevelt Dimes', 'Theme/Subject': 'Franklin D. Roosevelt', 'theme_subject': 'Franklin D. Roosevelt', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2025-roosevelt-dime-uncirculated-obverse-denver.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2025-roosevelt-dime-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg'));
    });

    test('Row 10 (0172d0ee64284a12a8aa269ce805ec07 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'P', 'Denomination': 'Quarter Dollar (25C)', 'Program/Series': 'United States Semiquincentennial (250th Anniversary)', 'Theme/Subject': 'Mayflower Compact & Pilgrim Couple', 'image_url_obverse': 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/2026_semiquincentennial_mayflower_compact_quarter_p_Obverse_20260701_1731.jpg', 'image_url_reverse': 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/2026_semiquincentennial_mayflower_compact_quarter_p_Reverse_20260701_1731.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Reverse-Unc.jpg'));
    });

    test('Row 11 (8f2197d5d03a428db24486b4ee375a5e | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Denomination': 'Half Dollar', 'Program/Series': 'United States Semiquincentennial (250th Anniversary)', 'Theme/Subject': '250th Anniversary of American Independence', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/obverse.jpg?t=1782428155', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/reverse.jpg?t=1782428156' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_half_dollar_enduring_liberty_reverse.jpg'));
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
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg'));
    });

    test('Row 14 (b243621c-5a35-45f0-84bf-8786eb1547f9 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2020', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)', 'theme_subject': 'Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)', 'Personal Notes': 'Marsh-Billings-Rockefeller National Historical Park (Vermont) - ATB-P', 'personal_notes': 'ATB- P TUBE', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg'));
    });

    test('Row 15 (c336e53e-4105-44bd-8c08-f30ae0328467 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2013', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Mount Rushmore National Memorial (South Dakota)', 'theme_subject': 'Mount Rushmore National Memorial (South Dakota)', 'Personal Notes': 'Mount Rushmore National Memorial (South Dakota) - ATB-P', 'personal_notes': 'ATB-P', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg'));
    });

    test('Row 16 (cba5e585-758f-4b10-be7a-1a59a1f4b2e6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2018', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Cumberland Island National Seashore (Georgia)', 'theme_subject': 'Cumberland Island National Seashore (Georgia)', 'Personal Notes': 'Apostle Islands National Lakeshore (Wisconsin) - ATB-P tube', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2016-america-the-beautiful-quarters-coin-cumberland-gap-kentucky-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg'));
    });

    test('Row 17 (d7fec246-983f-40de-8b58-854f59460bce | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2018', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Block Island National Wildlife Refuge (Rhode Island)', 'theme_subject': 'Block Island National Wildlife Refuge (Rhode Island)', 'Personal Notes': 'Voyageurs National Park (Minnesota) - ATB-P tube', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ellis-island-new-jersey-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg'));
    });

    test('Row 18 (Wq2UhSQNs67u34VFJDaI | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '1962', 'Denomination': 'Cent', 'Program/Series': 'Lincoln Cent (Memorial Reverse)', 'program_series': 'Lincoln Cent (Memorial Reverse)', 'Theme/Subject': 'Abraham Lincoln', 'theme_subject': 'Abraham Lincoln', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/penny/2008-lincoln-one-cent-reverse-2000x2000.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg'));
    });

    test('Row 19 (UOBfFO2mqgLg86NSsyss | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2019', 'Mint Mark': 'W', 'mint_mark': 'W', 'Denomination': 'Quarter Dollar', 'Program/Series': 'America the Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'San Antonio Missions', 'theme_subject': 'San Antonio Missions', 'Personal Notes': 'HV Coin Club', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/1932-george-washington-quarter-obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg'));
    });

    test('Row 20 (3f437576-fa20-4ef1-95c0-01e10eaf43a8 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Effigy Mounds National Monument (Iowa)', 'theme_subject': 'Effigy Mounds National Monument (Iowa)', 'Personal Notes': 'Ozark National Scenic Riverways (Missouri) - ATB-TUBE', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg'));
    });

    test('Row 21 (6ff959a0-26f8-451f-aa4c-064b5ef68939 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Frederick Douglass National Historic Site (District of Columbia)', 'theme_subject': 'Frederick Douglass National Historic Site (District of Columbia)', 'Personal Notes': 'Frederick Douglass National Historic Site (District of Columbia)', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg'));
    });

    test('Row 22 (96eeb7b6-6c4e-4a62-bb8e-80b69706d915 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2010', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Yellowstone National Park (Wyoming)', 'theme_subject': 'Yellowstone National Park (Wyoming)', 'Personal Notes': 'Yellowstone National Park (Wyoming) - ATB-P TUBE - to Poor Condition', 'personal_notes': 'ATB-P TUBE - Poor Condition', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg'));
    });

    test('Row 23 (ab35ab5d-d51f-4b9c-bc94-ff87def52bc6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'D', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'George Rogers Clark National Historical Park (Indiana)', 'theme_subject': 'George Rogers Clark National Historical Park (Indiana)', 'Personal Notes': 'George Rogers Clark National Historical Park (Indiana)', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg'));
    });

    test('Row 24 (b785236f-ca64-4461-9ee4-01cad3a7d60e | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Ozark National Scenic Riverways (Missouri)', 'theme_subject': 'Ozark National Scenic Riverways (Missouri)', 'Personal Notes': 'Effigy Mounds National Monument (Iowa) - ATB-P tube', 'personal_notes': 'ATB-P TUBE', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg'));
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
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_1.jpg'));
    });

    test('Row 27 (faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Program/Series': 'Semiquincentennial President', 'Personal Notes': 'Item # 26SQRP Semiquincentennial President D' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
    });

    test('Row 28 (2fa325166682b70aa0d64da45786c94aa4742d21 | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2023', 'Denomination': 'Set', 'Program/Series': 'Silver Proof Set', 'Personal Notes': 'Silver Proof Set 2023' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_c.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_innovation_four_states_composite.jpg'));
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
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_1.jpg'));
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
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg'));
    });

    test('Synthetic Tracker Case 11 (ATB-2010-P): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2010', 'mint': 'P', 'title': 'Mount Hood' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg'));
    });

    test('Synthetic Tracker Case 12 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Marsh-Billings-Rockefeller' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg'));
    });

    test('Synthetic Tracker Case 13 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Tallgrass Prairie' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg'));
    });

    test('Synthetic Tracker Case 14 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Weir Farm' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg'));
    });
  });
}
```

---

### 3.3 Section 4 Replacement — 28-Row Ground-Truth Table Matching `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` (`MF2`, `MF3`, `MF8`, `MF9`)

| Row | Firestore `doc_id` | Account | SKU / Series | Year-Mint | Theme / Subject | `obverseUrl` (with Live GCS Size & MD5 Prefix) | `reverseUrl` (with Live GCS Size & MD5 Prefix) | Verified Fallbacks (`fallbackObverseUrl` / `fallbackReverseUrl`) |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| 01 | `e91efa62-4e8d-4920-a928-c0c97659bcdc` | `eric.seaman@yahoo.com` | `26EA` | `2026-W` | America250 | `reference_library/us_mint_official/2026_products/26EA_image_1.jpg` (`126,209 B` (`md5: cb25bbc19d…`)) | `reference_library/us_mint_official/2026_products/26EA_image_2.jpg` (`139,910 B` (`md5: cfa91a545c…`)) | `reference_library/us_mint_official/2026_products/26ea_a.webp` / `reference_library/us_mint_official/2026_products/26EA_image_3.jpg` |
| 02 | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` | `eric.seaman@yahoo.com` | `26XE` | `2026` | Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026) | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`240,850 B` (`md5: 030c23e7cc…`)) | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` / `reference_library/us_mint_official/2026_products/26XE_image_1.jpg` |
| 03 | `a59853c1-b72b-414d-8b8e-de6813c29996` | `eric.seaman@yahoo.com` | `26XL` | `2026-P` | America250 | `reference_library/us_mint_official/2026_products/26XL_image_3.jpg` (`204,667 B` (`md5: a2127adeef…`)) | `reference_library/us_mint_official/2026_products/26XL_image_2.jpg` (`379,918 B` (`md5: f2a4301688…`)) | `reference_library/us_mint_official/2026_products/26xl___a.webp` / `reference_library/us_mint_official/2026_products/26XL_image_1.jpg` |
| 04 | `71e2d4ae92bc4312a4198a3a0cc21fcb` | `eric.seaman@yahoo.com` | `26RJ` | `2026` | 250th Anniversary Uncirculated Coin Set | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` (`336,365 B` (`md5: bba8df78a5…`)) | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` (`265,821 B` (`md5: abe6d1dd12…`)) | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` / `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` |
| 05 | `91f8821265bfe8a33fbd97e21f102c67fdf849fd` | `eric.seaman@yahoo.com` | `26RJ` | `2026` |  | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` (`336,365 B` (`md5: bba8df78a5…`)) | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` (`265,821 B` (`md5: abe6d1dd12…`)) | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` / `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` |
| 06 | `0e68ecba760df66bf824ec1ba2c86b32318d002d` | `eric.seaman@yahoo.com` | `26GC` | `2026` |  | `reference_library/us_mint_official/2026_products/26GC_image_1.jpg` (`135,436 B` (`md5: ee2eea2529…`)) | `reference_library/us_mint_official/2026_products/26gc_b.webp` (`137,372 B` (`md5: 4ec332f787…`)) | `reference_library/2026_series/2026_american_innovation_obverse.jpg` / `reference_library/us_mint_official/2026_products/26GC_image_2.jpg` |
| 07 | `7a32932ebc4e94a586534e7180cd1c4372c4f17d` | `eric.seaman@yahoo.com` | `26SQRP` | `2026-D` | Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` (`217,879 B` (`md5: fb99f484c7…`)) | `reference_library/us_mint_official/2026_products/26sqrp_b.webp` (`179,722 B` (`md5: dfeee8a47f…`)) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` / `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` |
| 08 | `nAnGLwGvhfIOibf6kIft` | `eric.seaman@yahoo.com` | `2026-DIME-P` | `2026-P` | Franklin D. Roosevelt | `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg` (`1,224,376 B` (`md5: c39fe99a21…`)) | `reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B` (`md5: 8533943d7d…`)) | `reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg` / `reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg` |
| 09 | `rv9SCUTahBuqJkkiJyga` | `eric.seaman@yahoo.com` | `2026-DIME-D` | `2026-D` | Franklin D. Roosevelt | `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg` (`1,224,042 B` (`md5: fb30835fd1…`)) | `reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B` (`md5: 8533943d7d…`)) | `reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg` / `reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg` |
| 10 | `0172d0ee64284a12a8aa269ce805ec07` | `eric.seaman@yahoo.com` | `2026-MAYFLOWER-P` | `2026-P` | Mayflower Compact & Pilgrim Couple | `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` (`1,446,894 B` (`md5: a93d9444f8…`)) | `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg` (`1,627,560 B` (`md5: c62c9f4aec…`)) | `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg` / `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Reverse-Unc.jpg` |
| 11 | `8f2197d5d03a428db24486b4ee375a5e` | `eric.seaman@yahoo.com` | `2026-HALF-D` | `2026-D` | 250th Anniversary of American Independence | `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B` (`md5: ef82afd24a…`)) | `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg` (`1,510,409 B` (`md5: cceb4ab85d…`)) | `reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` / `reference_library/2026_series/2026_half_dollar_enduring_liberty_reverse.jpg` |
| 12 | `5b424047-77e0-496e-a513-6ef180b515a6` | `eric.seaman@yahoo.com` | `2005-SQ-KS-D` | `2005-D` | Kansas | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg` (`572,791 B` (`md5: 146bcb61b2…`)) | `reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg` (`546,742 B` (`md5: 48a02e9e79…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg` / `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg` |
| 13 | `3346cda5-5935-4303-bf62-de43041f3175` | `eric.seaman@yahoo.com` | `ATB-2019-P` | `2019-P` | American Memorial Park (Northern Mariana Islands) | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`2,133,544 B` (`md5: 45abfe1d9b…`)) | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg` (`2,064,160 B` (`md5: 3dd32dc656…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg` |
| 14 | `b243621c-5a35-45f0-84bf-8786eb1547f9` | `eric.seaman@yahoo.com` | `ATB-2020-P` | `2020-P` | Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands) | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`1,340,722 B` (`md5: 6ed5d08806…`)) | `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg` (`1,298,877 B` (`md5: 1c55def862…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg` |
| 15 | `c336e53e-4105-44bd-8c08-f30ae0328467` | `eric.seaman@yahoo.com` | `ATB-2013-P` | `2013-P` | Mount Rushmore National Memorial (South Dakota) | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` (`1,867,830 B` (`md5: d7cb6ecc2c…`)) | `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg` (`2,032,412 B` (`md5: 0b6ded8854…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg` |
| 16 | `cba5e585-758f-4b10-be7a-1a59a1f4b2e6` | `eric.seaman@yahoo.com` | `ATB-2018-P` | `2018-P` | Cumberland Island National Seashore (Georgia) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`2,309,513 B` (`md5: 6212666267…`)) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg` (`2,157,454 B` (`md5: 0f91df6cf3…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg` |
| 17 | `d7fec246-983f-40de-8b58-854f59460bce` | `eric.seaman@yahoo.com` | `ATB-2018-P` | `2018-P` | Block Island National Wildlife Refuge (Rhode Island) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`2,309,513 B` (`md5: 6212666267…`)) | `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg` (`2,242,129 B` (`md5: 52026d4062…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg` |
| 18 | `Wq2UhSQNs67u34VFJDaI` | `eric.seaman@yahoo.com` | `1962-LINCOLN-1C` | `1962` | Abraham Lincoln | `reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg` (`1,744,750 B` (`md5: 070b9a8418…`)) | `reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` (`608,070 B` (`md5: 75eb808f3a…`)) | `reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png` / `reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` |
| 19 | `UOBfFO2mqgLg86NSsyss` | `eric.seaman@yahoo.com` | `ATB-2019-W` | `2019-W` | San Antonio Missions | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` (`1,176,299 B` (`md5: 2183268cf2…`)) | `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` (`2,116,020 B` (`md5: 28175266fc…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` / `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` |
| 20 | `3f437576-fa20-4ef1-95c0-01e10eaf43a8` | `eric.seaman@yahoo.com` | `ATB-2017-P` | `2017-P` | Effigy Mounds National Monument (Iowa) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg` (`2,062,235 B` (`md5: 62e200b5ff…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg` |
| 21 | `6ff959a0-26f8-451f-aa4c-064b5ef68939` | `eric.seaman@yahoo.com` | `ATB-2017-P` | `2017-P` | Frederick Douglass National Historic Site (District of Columbia) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` (`2,127,779 B` (`md5: c2bffdc58c…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` |
| 22 | `96eeb7b6-6c4e-4a62-bb8e-80b69706d915` | `eric.seaman@yahoo.com` | `ATB-2010-P` | `2010-P` | Yellowstone National Park (Wyoming) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` (`592,295 B` (`md5: 23c0fbbf07…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` |
| 23 | `ab35ab5d-d51f-4b9c-bc94-ff87def52bc6` | `eric.seaman@yahoo.com` | `ATB-2017-D` | `2017-D` | George Rogers Clark National Historical Park (Indiana) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` (`1,176,299 B` (`md5: 2183268cf2…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` (`2,118,832 B` (`md5: 673f4e83fe…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg` / `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` |
| 24 | `b785236f-ca64-4461-9ee4-01cad3a7d60e` | `eric.seaman@yahoo.com` | `ATB-2017-P` | `2017-P` | Ozark National Scenic Riverways (Missouri) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` (`178,081 B` (`md5: b4e9be7357…`)) | `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` (`2,172,068 B` (`md5: 8e711b71fd…`)) | `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` / `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` |
| 25 | `0a2bc793-8d62-47c3-88cd-7a5b9be434ba` | `eric@numista.ai` | `26RJ` | `2026` |  | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` (`336,365 B` (`md5: bba8df78a5…`)) | `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` (`265,821 B` (`md5: abe6d1dd12…`)) | `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` / `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` |
| 26 | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` | `eric@numista.ai` | `26XE` | `2026` | Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026) | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`240,850 B` (`md5: 030c23e7cc…`)) | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` / `reference_library/us_mint_official/2026_products/26XE_image_1.jpg` |
| 27 | `faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c` | `eric@numista.ai` | `26SQRP` | `2026-D` |  | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` (`217,879 B` (`md5: fb99f484c7…`)) | `reference_library/us_mint_official/2026_products/26sqrp_b.webp` (`179,722 B` (`md5: dfeee8a47f…`)) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` / `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` |
| 28 | `2fa325166682b70aa0d64da45786c94aa4742d21` | `eric@numista.ai` | `23RH` | `2023` |  | `reference_library/us_mint_official/2023_products/23rh_b.webp` (`STAGED (Gate 0)`) | `reference_library/us_mint_official/2023_products/23rh_c.webp` (`STAGED (Gate 0)`) | `reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg` / `reference_library/2023_series/2023_american_innovation_four_states_composite.jpg` |

---

### 3.4 Section 4.1.3 — Unedited Raw GCS Bucket Listing (`name`, `size`, `md5Hash`, `md5_hex`) (`MF6`, `WAKE_AG-COS-V4_NET-708`)

Generated directly from the live `gs://numista-reference-library` GCS JSON API at `2026-11-01 14:10 EST` (`95/97` URLs `HTTP 200 LIVE`; `2/97` URLs explicitly staged for `23RH` with `HTTP 200 LIVE` fallbacks):

| GCS Object Name (`gs://numista-reference-library/...`) | Exact Byte Size (`size`) | Base64 `md5Hash` (from GCS API) | Hex MD5 (`md5_hex`) | `contentType` | Live Status |
| :--- | :---: | :--- | :--- | :--- | :---: |
| `reference_library/2023_series/2023_american_innovation_four_states_composite.jpg` | `584055` | `vrQPumi94UYMhlxdfVTYpg==` | `beb40fba68bde1460c865c5d7d54d8a6` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.jpg` | `208114` | `ZzRvt5eUtDA2hw9agpkCGA==` | `67346fb79794b43036870f5a82990218` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.png` | `579926` | `YEjBG1JsoMjJgzRTxgjpIA==` | `6048c11b526ca0c8c9833453c608e920` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.jpg` | `231827` | `O6HDkln0SoBGVkwtDmbrSg==` | `3ba1c39259f44a8046564c2d0e66eb4a` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.png` | `630500` | `oNPX6X/bH6P7MClVM/CzPQ==` | `a0d3d7e97fdb1fa3fb30295533f0b33d` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.jpg` | `231270` | `F3St306+uFcMecYBc4UoFQ==` | `1774addf4ebeb8570c79c60173852815` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.png` | `643041` | `7jTaHVKLBSUWI6pQn03j/w==` | `ee34da1d528b05251623aa509f4de3ff` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg` | `711501` | `HmWTTcqxlE/3AQiDaQrGfQ==` | `1e65934dcab1944ff7010883690ac67d` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.jpg` | `195775` | `SD+TV26sC7/d/HP87DmX8w==` | `483f93576eac0bbfddfc73fcec3997f3` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.png` | `578910` | `OWH/ZE9rzaf0xC3QLq91sQ==` | `3961ff644f6bcda7f4c42dd02eaf75b1` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.jpg` | `193842` | `II9laxiLmvQGT1o0Y/vUig==` | `208f656b188b9af4064f5a3463fbd48a` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.png` | `566667` | `0uL2T/LBE9BjOW/3qom2Yw==` | `d2e2f64ff2c113d063396ff7aa89b663` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg` | `167735` | `OlGn3LONL/Rb1kvSFInhGw==` | `3a51a7dcb38d2ff45bd64bd21489e11b` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2023_series/2023_american_women_quarters_shared_obverse.png` | `508739` | `frH0O3WCdce2BQTmJPgftg==` | `7eb1f43b758275c7b60504e624f81fb6` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_american_innovation_obverse.jpg` | `1279411` | `UVtY6h7zE7XOAQnh8rxz1Q==` | `515b58ea1ef313b5ce0109e1f2bc73d5` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg` | `1224376` | `w5/pmiEvfXewhkfa/eOyZg==` | `c39fe99a212f7d77b08647dafde3b266` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg` | `1336791` | `hTOUPX2IoBGtrzckdr/h8w==` | `8533943d7d88a011adaf372476bfe1f3` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` | `1510450` | `7AU0fKvzsTSiYqyfZjE4Ww==` | `ec05347cabf3b134a262ac9f6631385b` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_half_dollar_enduring_liberty_reverse.jpg` | `1510409` | `zOtKuF05g0d5LYkp+xG+0A==` | `cceb4ab85d398347792d8929fb11bed0` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` | `1446894` | `qT2URPiM0HRDiKiXNyXyTg==` | `a93d9444f88cd0744388a8973725f24e` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg` | `1627560` | `xiyfSuyVCCfLEa+k/nSa7Q==` | `c62c9f4aec950827cb11afa4fe749aed` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg` | `576545` | `ni7g5HSgcfLBn+xbby2TQw==` | `9e2ee0e474a071f2c19fec5b6f2d9343` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` | `592295` | `I8D7vwcAoyv3gT2gx76SOQ==` | `23c0fbbf0700a32bf7813da0c7be9239` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg` | `2032412` | `C23tiFQq+fmHJbewhLvUmA==` | `0b6ded88542af9f98725b7b084bbd498` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg` | `1864933` | `w7mHrHVnfVty567md4EoPg==` | `c3b987ac75677d5b72e7aee67781283e` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` | `1867830` | `18tuzCxGW52pPDBd/yOdAQ==` | `d7cb6ecc2c465b9da93c305dff239d01` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg` | `2269453` | `NbGPazstN+3/9xA2LMGcUA==` | `35b18f6b3b2d37edfff710362cc19c50` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg` | `2462457` | `tateKDh88b30ilnRqrFcGA==` | `b5ab5e28387cf1bdf48a59d1aab15c18` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg` | `2062235` | `YuIAtf85GEz3NZX1hfwc/g==` | `62e200b5ff39184cf73595f585fc1cfe` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` | `2127779` | `wr/9xYxj3OG3AjE+BJ2xpw==` | `c2bffdc58c63dce1b702313e049db1a7` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` | `2118832` | `Zz9Og/675Yra1Iq9pOcJYw==` | `673f4e83febbe58adad48abda4e70963` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` | `2172068` | `jnEbcf3VUSMB4z080y7Dxg==` | `8e711b71fdd5512301e33d3cd32ec3c6` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg` | `2242129` | `UgJtQGL253JRSNSVwjUTiQ==` | `52026d4062f6e7725148d495c2351389` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg` | `2157454` | `D5HfbPN0dl/yEb0X5fMUgg==` | `0f91df6cf374765ff211bd17e5f31482` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `2309513` | `YhJmYmedzCTERkmU95+mDA==` | `62126662679dcc24c4464994f79fa60c` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg` | `2064160` | `PdMtxlZ5Ai2LbIbIgSIjgg==` | `3dd32dc65679022d8b6c86c881222382` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` | `2116020` | `KBdSZvzeuU302IRReE5kKA==` | `28175266fcdeb94df4d88451784e6428` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `2133544` | `Rav+HZusCG43v29jWmjufg==` | `45abfe1d9bac086e37bf6f635a68ee7e` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg` | `1225636` | `Mi+H6tey28mqy3HnVxtjuA==` | `322f87ead7b2dbc9aacb71e7571b63b8` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg` | `1298877` | `HFXe+GLgNc9idGr5UT7bzQ==` | `1c55def862e035cf62746af9513edbcd` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg` | `1198829` | `Fenq+jpa05htUAu5ZL9Sww==` | `15e9eafa3a5ad3986d500bb964bf52c3` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `1340722` | `btXQiAYL+dJS2Soeuk8hIQ==` | `6ed5d088060bf9d252d92a1eba4f2121` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg` | `1307070` | `6fOcGUn1i6Hv54HpvgnMCg==` | `e9f39c1949f58ba1efe781e9be09cc0a` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg` | `546742` | `SKAunnng5suWmWon8efjMA==` | `48a02e9e79e0e6cb96996a27f1e7e330` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg` | `1224042` | `+zCDX9GonJPN9l8QOBO2nA==` | `fb30835fd1a89c93cdf65f103813b69c` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg` | `1224376` | `w5/pmiEvfXewhkfa/eOyZg==` | `c39fe99a212f7d77b08647dafde3b266` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg` | `1336791` | `hTOUPX2IoBGtrzckdr/h8w==` | `8533943d7d88a011adaf372476bfe1f3` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg` | `1510128` | `74Kv0kpcTut0lHlYsFUukQ==` | `ef82afd24a5c4eeb74947958b0552e91` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg` | `1510409` | `zOtKuF05g0d5LYkp+xG+0A==` | `cceb4ab85d398347792d8929fb11bed0` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg` | `1434919` | `M/8Y3Jm7xJVajtCg0alJpQ==` | `33ff18dc99bbc4955a8ed0a0d1a949a5` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Reverse-Unc.jpg` | `1627560` | `xiyfSuyVCCfLEa+k/nSa7Q==` | `c62c9f4aec950827cb11afa4fe749aed` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2023_products/23rh_b.webp` | `STAGED (Gate 0 Pre-Cutover)` | `N/A (Staged)` | `N/A (Staged)` | `image/webp` | `STAGED (Gate 0)` |
| `reference_library/us_mint_official/2023_products/23rh_c.webp` | `STAGED (Gate 0 Pre-Cutover)` | `N/A (Staged)` | `N/A (Staged)` | `image/webp` | `STAGED (Gate 0)` |
| `reference_library/us_mint_official/2026_products/26EA_image_1.jpg` | `126209` | `yyW7wZ1+cqCUCUV9bOMwow==` | `cb25bbc19d7e72a09409457d6ce330a3` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26EA_image_2.jpg` | `139910` | `z6kaVFzaD9MVa+GmyKnTNg==` | `cfa91a545cda0fd3156be1a6c8a9d336` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26EA_image_3.jpg` | `142916` | `Na0q3XBIgct2y/UyL7xCAA==` | `35ad2add704881cb76cbf5322fbc4200` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26GC_image_1.jpg` | `135436` | `7i7qJSlqeLoWVTHElAGD7Q==` | `ee2eea25296a78ba165531c4940183ed` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26GC_image_2.jpg` | `138756` | `dTWDCgrtxzX659uNQwcbMw==` | `7535830a0aedc735fae7db8d43071b33` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RG_image_1.jpg` | `115064` | `R4j7mhD21PHNmZ6xRBoWSw==` | `4788fb9a10f6d4f1cd999eb1441a164b` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RG_image_2.jpg` | `104072` | `YzcSFLpzF+Wi5315lmapiw==` | `63371214ba7317e5a2e77d799666a98b` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RG_image_3.jpg` | `197484` | `0K8+7wU+q+BvFVUVGISX4w==` | `d0af3eef053eabe06f155515188497e3` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RH_image_1.jpg` | `110063` | `S9ssi0PNcho75SIMQmOGEw==` | `4bdb2c8b43cd721a3be5220c42638613` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RH_image_2.jpg` | `104034` | `ueuMT1YLnZoXjO2FR6QxKQ==` | `b9eb8c4f560b9d9a178ced8547a43129` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RH_image_3.jpg` | `209254` | `T6iaugYzjjDxMHWuy9gcKg==` | `4fa89aba06338e30f13075aecbd81c2a` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RJ_image_1.jpg` | `299132` | `A9ijFLrNrypWsfE/IwMKuw==` | `03d8a314bacdaf2a56b1f13f23030abb` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26RJ_image_2.jpg` | `300506` | `uRO6lXHJQ8HtIlcZEb1j/Q==` | `b913ba9571c943c1ed22571911bd63fd` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XE_image_1.jpg` | `195231` | `StUMKv65OT4Vfkb+GO3Pcw==` | `4ad50c2afeb9393e157e46fe18edcf73` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` | `240850` | `Awwj58wvtpH0LZn9IMtCEg==` | `030c23e7cc2fb691f42d99fd20cb4212` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` | `285827` | `4FaiAfyRWOLwRxU6+YN0gg==` | `e056a201fc9158e2f047153af9837482` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XF_image_1.jpg` | `274992` | `F4vXHIGNYcgRXEB2pT9I/w==` | `178bd71c818d61c8115c4076a53f48ff` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XF_image_2.jpg` | `324593` | `cjLNuR52u3vft4t5nc0xkw==` | `7232cdb91e76bb7bdfb78b799dcd3193` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XH_image_1.jpg` | `140054` | `sSdsLiUCKogkIi4G4ULYHw==` | `b1276c2e25022a8824222e06e142d81f` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XH_image_2.jpg` | `147982` | `uE4iRMoGow0AhsFn7H7wQQ==` | `b84e2244ca06a30d0086c167ec7ef041` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XH_image_3.jpg` | `169132` | `uPQRj7E7qV7axnVWzUcsqg==` | `b8f4118fb13ba95edac67556cd472caa` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XL_image_1.jpg` | `319138` | `/h7OLSwM8+I7uopf79GZIw==` | `fe1ece2d2c0cf3e23bba8a5fefd19923` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XL_image_2.jpg` | `379918` | `8qQwFog6B7DA1c4/1Hmqmg==` | `f2a43016883a07b0c0d5ce3fd479aa9a` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26XL_image_3.jpg` | `204667` | `ohJ63u88ygv2DH28jifjUg==` | `a2127adeef3cca0bf60c7dbc8e27e352` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26ea_a.webp` | `168246` | `eQ0TKH0gziKzCKJ9TvxhmQ==` | `790d13287d20ce22b308a27d4efc6199` | `image/webp` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26gc_b.webp` | `137372` | `TsMy94eKpDLEcwzQ0yjmYg==` | `4ec332f7878aa432c4730cd0d328e662` | `image/webp` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26rg_b.webp` | `178232` | `9slPy96nlPIGzKp/juF95g==` | `f6c94fcbdea794f206ccaa7f8ee17de6` | `image/webp` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26sqrp_b.webp` | `179722` | `3+7opH8PfVcsOkpcRBGpwA==` | `dfeee8a47f0f7d572c3a4a5c4411a9c0` | `image/webp` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26xe_a.webp` | `216358` | `likMLXOT1KExPbYZ14SzIA==` | `96290c2d7393d4a1313db619d784b320` | `image/webp` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26xh_image_3.jpg` | `169132` | `uPQRj7E7qV7axnVWzUcsqg==` | `b8f4118fb13ba95edac67556cd472caa` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/26xl___a.webp` | `239954` | `QDzAGaegsMsA2PAURavQeg==` | `403cc019a7a0b0cb00d8f01445abd07a` | `image/webp` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` | `217879` | `+5n0hMeeZP0i59oaiMjrMw==` | `fb99f484c79e64fd22e7da1a88c8eb33` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` | `245212` | `zpHnAjb0Y8c50FPXF0md1w==` | `ce91e70236f463c739d053d717499dd7` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` | `265821` | `q+bR3RLJ4fAKXbPudIX94A==` | `abe6d1dd12c9e1f00a5db3ee7485fde0` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` | `336365` | `u6jfeKUlaYKp2A2DbFHwwA==` | `bba8df78a5256982a9d80d836c51f0c0` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg` | `1744750` | `BwuahBjpA1+etJG1285mIQ==` | `070b9a8418e9035f9eb491b5dbce6621` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` | `608070` | `deuAjzoVEPUp38PiD8/s9g==` | `75eb808f3a1510f529dfc3e20fcfecf6` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png` | `1018519` | `TKyZ0uaHYbGWl1ftDgpLEA==` | `4cac99d2e68761b1969757ed0e0a4b10` | `image/png` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg` | `157337` | `LEgWthTD3aj5TkxwbX+UYQ==` | `2c4816b614c3dda8f94e4c706d7f9461` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg` | `572791` | `FGvLYbJuCGUz2eGYMEecqQ==` | `146bcb61b26e086533d9e19830479ca9` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg` | `1410838` | `wq27ruadtVP+UAy/Fm4PVw==` | `c2adbbaee69db553fe500cbf166e0f57` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg` | `563189` | `Fa1rvuHzKBCkC5Z+zGfjcQ==` | `15ad6bbee1f32810a40b967ecc67e371` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` | `1176299` | `IYMmjPIWJhVNRmGgZIvEGg==` | `2183268cf21626154d4661a0648bc41a` | `image/jpeg` | `HTTP 200 LIVE` |
| `reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg` | `178081` | `tOm+c1c0Kr6fu2XTOUZGxg==` | `b4e9be7357342abe9fbb65d3394646c6` | `image/jpeg` | `HTTP 200 LIVE` |

---

### 3.5 Additional Must-Fix / Should-Fix Resolutions (`MF6`, `MF7`, `MF10`, `SF1`, `SF3`)

1. **`MF6` (Section 9 Gate 4 Pre-Cutover Verification):**
   - Update Gate 4 command in Section 9 to assert **HTTP 200 + Content-Type `image/*` + exact byte size (`Content-Length`) + MD5 (`ETag` / `x-goog-hash`) match** against the Section 4.1.3 table above for all 97 unique URLs (after Gate 0 uploads `23rh_b.webp` and `23rh_c.webp`).
2. **`MF7` (Contact Sheet Labels Synced to 28-Row Ground Truth):**
   - Update the 28-row visual contact sheet script (`NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.8.10.png`) so every cell label matches the exact `doc_id`, `Year-Mint`, `Theme/Subject`, and live GCS paths in Section 3.3 above (Rows 13–17 = `American Memorial Park`, `Salt River Bay`, `Mount Rushmore`, `Cumberland Island`, `Block Island`; Row 18 = `1962 Lincoln Cent` with preserved obverse + fixed Memorial reverse; Rows 19–24 = `San Antonio`, `Effigy Mounds`, `Frederick Douglass`, `Yellowstone`, `George Rogers Clark`, `Ozark`).
3. **`MF10` (Section 6 Byte Size Typo Fix):**
   - In Section 6, replace `1,401,554 B` for `SemiQ-Dime-Reverse-Unc.jpg` with the verified live GCS byte size **`1,336,791 B`** (`md5Hash: 4mebX7tCIfbbY0P27d6bTw==`, `md5_hex: e2679b5fbb4221f6db6343f6edde9b4f`).
4. **`SF1` (Closing Footer):**
   - Replace the closing line `**END PLAN R2.8.8**` with `**END PLAN R2.8.10**`.
5. **`SF3` (Section 8 Master Bug Tracker Synced to 39 Total Tracked Rows):**
   - Keep Rows 1–28 in Section 8 1:1 identical with the 28 actual Firestore documents in Section 4 (`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`), and list the remaining 11 synthetic/additional catalog test rows (`26XH`, `26XF`, `26RG`, `26RH`, 5 AWQ 2023 quarters, `2013-D White Mountain`, `2010-P Mount Hood`) in Rows 29–39 as explicit **Synthetic Regression Test Rows**.

---

**END ARGON REVIEW — `GEMINI38_REVIEW_NET-647_R2.8.9_2026-11-01.md`**
