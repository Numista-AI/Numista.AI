# FAILFIX PLAN NET-748 v2 — Post-FT Fix for NET-746 / R2.8.19 (Commit `7c0eec8d`)

- **Author:** AG CoS v4 / Gemini 3.8 Code Reviewer (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai`)
- **Station:** AG CoS Desk / Grok CoS Net Control
- **Date & Time:** `2026-11-03T11:00:00-05:00` (ET)
- **Authorizing Batons:**
  - [`BATON_NET-748_AG_NET-746-FAILFIX-PLAN-ONLY_20261103-0950.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/BATON_NET-748_AG_NET-746-FAILFIX-PLAN-ONLY_20261103-0950.md)
  - [`BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md)
- **Review Predecessor:** [`GEMINI38_REVIEW_NET-748_AG_v1_2026-11-03.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/GEMINI38_REVIEW_NET-748_AG_v1_2026-11-03.md) (Argon, Score 78/100 REVISE)
- **Field Tester Failure Report:** [`FT_RESULT_NET746_R2.8.19_7c0eec8d_FAIL.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FT_RESULT_NET746_R2.8.19_7c0eec8d_FAIL.md)
- **Attempt Tracking:** Attempt 9 of 10 (AG CoS 2nd and Final Try)
- **Execution Mode:** **PLAN ONLY — STRICTLY NO CODE, COMMITS, OR DEPLOYS UNTIL ARGON/GROKCOS/SAG PASS (>=95) AND FOUNDER ERIC TYPES YES**
- **Preview Channel:** `https://numista-vault--p7-gate-8avtpz22.web.app` (`p7-gate` only)
- **Production Lock:** `origin/main` locked at `9f04550a`; live production site untouched; Stripe locked OFF.

---

## 1. Executive Summary & v1-to-v2 Change List

In `FAILFIX_PLAN_NET-748_AG_v1.md`, AG CoS diagnosed the two primary root causes from Field Tester report `FT_RESULT_NET746_R2.8.19_7c0eec8d_FAIL.md`:
1. `CanonicalMintAssetService` was built as a standalone service in commit `7c0eec8d` but never wired into the UI rendering flow (`my_collection_screen.dart`).
2. Add-by-SKU was blocked by `firestore.rules` denying read access to `global_metadata`, and `26SQRP` was unseeded in Firestore.

Argon's independent technical audit evaluated `v1` against all 331 live Firestore coin documents in `users/grokbot@numista.ai/coins` and flagged 5 Must-Fix defects (`MF-1` to `MF-5`). In addition, `BATON_NET-750` specified strict isolation for `firestore.rules` and full source citations for every SKU and image asset.

### v1-to-v2 Diff & Change List:
1. **`MF-1` (Eliminated Substring Matching Bug):** Replaced `cleanTitle.contains('cent')` (which matched `"semiquincentennial"`, converting all 2026 quarters/dimes/halves into pennies) and `cleanTitle.contains('bicentennial')` with strict denomination and regex word-boundary checks for Lincoln Cent (`2026-CENT-P`/`S`) and Jefferson Nickel (`2026-NICKEL-S`).
2. **`MF-2` (`extractSku` Normalization & Condition Inclusion):** Updated `CanonicalMintAssetService.extractSku()` to strip `.0` on `year`, include `Condition`, `Strike Type`, `Variety`, and `Denomination` in `combined`, add the `silver eagle` / `american eagle` -> `26EA` mapping, guard `26GC` with `!combined.contains('polly cooper')`, and read `'retailer_item_num'`.
3. **`MF-3` (Half Dollar Guarding & All 5 Semiquincentennial Quarters):** Guarded Half Dollar line 332 (`!isQuarter`) so `Declaration of Independence` Quarter (`LyV8gyNH`, `UtN8Kz1f`, `mAkJtb73`) is never hijacked as `2026-HALF-S`. Mapped all 5 2026 Semiquincentennial Quarters (`Mayflower Compact`, `Declaration of Independence`, `Gettysburg Address`, `Revolutionary War`, `U.S. Constitution`) and Polly Cooper Native American $1 (`2026_american_innovation_oneida_indian_nation_reverse.jpg`) using verified `HTTP 200` assets in `$_base/2026_series/`.
4. **`MF-4` (Complete UI & Service Wiring):** 
   - `my_collection_screen.dart:6357` (`_CollectionCardImage.build`): Checks `CanonicalMintAssetService.resolveFromMap(data)` first and retries `fallbackUrl` in `_buildCoinImage` `errorBuilder`.
   - `my_collection_screen.dart:3467` (`_showCoinInspectorDialog`): Checks `CanonicalMintAssetService.resolveFromMap(data)` for Table row clicks and Grid card clicks.
   - `coin_image_service.dart:489` (`fetchReferenceImages`): Checks `CanonicalMintAssetService.resolve(...)` at entry point so all 6 reference-image callers automatically bypass broken `coin_image_index` URLs.
5. **`MF-5` (SKU Field Stamping & Fallback Immunity):** 
   - `add_coins_hub.dart:2638` (`_addSkuToCollection`): Stamps `'sku'`, `'item_number'`, and `'Retailer Item No.'` on `coinDoc` for all added items.
   - `add_coins_hub.dart:2610-2627` (`_lookupSku`): Checks `_kFallbackUsMintSkus[docId]` in BOTH `if (!snap.exists)` AND `catch (e)` (ensuring complete immunity to Firestore rules errors).
   - Corrected `26SQRP` metadata to match US Mint catalog and `numista_backend/main.py:2200` ("2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll", `MASTER_SEMIQDJT_image_1.jpg`).
   - Seeded all 12 `_knownSkus` (`26SQRP`, `26EA`, `26XE`, `26XL`, `26XH`, `26XF`, `26RJ`, `26GC`, `26RG`, `23RG`, `26RH`, `23RH`) and `26RA`-`26RF` in both `_kFallbackUsMintSkus` and Firestore seed script.
6. **Isolated Step for `firestore.rules` (Per BATON NET-749 & NET-750):** Narrowed rule strictly to `/global_metadata/{dictionary}/skus/{skuId}` where `dictionary in ['usmint_sku_dictionary', 'littleton_sku_dictionary']`. Isolated into Step 1 with explicit requirement for Founder Eric's separate typed YES, since rules affect the production Firebase project.

---

## 2. Source Citations for Every SKU and Image Mapping (Zero Invented Data)

| Asset / SKU | Product Title / Description | Source Citation | Verified URL / GCS Asset | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`26SQRP`** | 2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll | US Mint 2026 Product Schedule / `numista_backend/main.py:2200` / `CanonicalMintAssetService:269` | `gs://numista-reference-library/reference_library/2026_series/MASTER_SEMIQDJT_image_1.jpg` / `26sqrp_b.webp` | `HTTP 200` |
| **`26EA`** | 2026 American Eagle One Ounce Silver Proof Coin | US Mint Catalog SKU 26EA / `CanonicalMintAssetService:205` | `gs://numista-reference-library/reference_library/2026_series/2026_american_eagle_silver_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`26XE`** | 2026 Morgan Silver Dollar Enhanced Uncirculated Coin | US Mint Catalog SKU 26XE / `CanonicalMintAssetService:214` | `gs://numista-reference-library/reference_library/2026_series/2026_morgan_dollar_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`26XL`** | 2026 Peace Silver Dollar Reverse Proof Coin | US Mint Catalog SKU 26XL / `CanonicalMintAssetService:223` | `gs://numista-reference-library/reference_library/2026_series/2026_peace_dollar_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`26XH`** | 2026 Peace Silver Dollar Uncirculated Coin | US Mint Catalog SKU 26XH / `CanonicalMintAssetService:232` | `gs://numista-reference-library/reference_library/2026_series/2026_peace_dollar_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`26XF`** | 2026 Morgan Silver Dollar Proof Coin | US Mint Catalog SKU 26XF / `CanonicalMintAssetService:241` | `gs://numista-reference-library/reference_library/2026_series/2026_morgan_dollar_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`26RJ`** | 2026 250th Anniversary Uncirculated Coin Set | US Mint Catalog SKU 26RJ / `CanonicalMintAssetService:250` | `gs://numista-reference-library/reference_library/2026_series/26rj_a.webp` & `26rj_b.webp` | `HTTP 200` |
| **`26GC`** | 2026 American Innovation $1 Coin Proof Set | US Mint Catalog SKU 26GC / `CanonicalMintAssetService:260` | `gs://numista-reference-library/reference_library/2026_series/26gc_a.webp` & `26gc_b.webp` | `HTTP 200` |
| **`26RG`** | 2026 Clad Proof Set | US Mint Catalog SKU 26RG / `CanonicalMintAssetService:280` | `gs://numista-reference-library/reference_library/2026_series/26rg_a.webp` & `26rg_b.webp` | `HTTP 200` |
| **`23RG`** | 2023 Clad Proof Set | US Mint Catalog SKU 23RG / `CanonicalMintAssetService:289` | `gs://numista-reference-library/reference_library/2026_series/23rg_a.webp` & `23rg_b.webp` | `HTTP 200` |
| **`26RH`** | 2026 Silver Proof Set | US Mint Catalog SKU 26RH / `CanonicalMintAssetService:298` | `gs://numista-reference-library/reference_library/2026_series/26rh_a.webp` & `26rh_b.webp` | `HTTP 200` |
| **`23RH`** | 2023 Silver Proof Set | US Mint Catalog SKU 23RH / `CanonicalMintAssetService:307` | `gs://numista-reference-library/reference_library/2026_series/23rh_a.webp` & `23rh_b.webp` | `HTTP 200` |
| **`2026-CENT`** | 2026 Lincoln Cent (1c / Penny) | US Mint 2026 Semiquincentennial Circulating Coin Program | `gs://numista-reference-library/reference_library/2026_series/2026_one_cent_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-NICKEL`** | 2026 Jefferson Nickel (5c) | US Mint 2026 Semiquincentennial Circulating Coin Program | `gs://numista-reference-library/reference_library/2026_series/2026_five_cent_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-DIME`** | 2026 Roosevelt Dime (10c) | US Mint 2026 Semiquincentennial Circulating Coin Program | `gs://numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg` & `SemiQ-Dime-Reverse-Unc.jpg` | `HTTP 200` |
| **`2026-HALF`** | 2026 Kennedy Half Dollar (50c) | US Mint 2026 Semiquincentennial Circulating Coin Program | `gs://numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg` & `SemiQ-Half-Dollar-Reverse-Unc.jpg` | `HTTP 200` |
| **`2026-QTR-1`** | 2026 Semiquincentennial Quarter: Mayflower Compact | Public Law 116-330 / US Mint 2026 Quarter Program | `gs://numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-QTR-2`** | 2026 Semiquincentennial Quarter: Declaration of Independence | Public Law 116-330 / US Mint 2026 Quarter Program | `gs://numista-reference-library/reference_library/2026_series/2026_quarter_dollar_declaration_of_independence_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-QTR-3`** | 2026 Semiquincentennial Quarter: Gettysburg Address | Public Law 116-330 / US Mint 2026 Quarter Program | `gs://numista-reference-library/reference_library/2026_series/2026_quarter_dollar_gettysburg_address_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-QTR-4`** | 2026 Semiquincentennial Quarter: Revolutionary War | Public Law 116-330 / US Mint 2026 Quarter Program | `gs://numista-reference-library/reference_library/2026_series/2026_quarter_dollar_revolutionary_war_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-QTR-5`** | 2026 Semiquincentennial Quarter: U.S. Constitution | Public Law 116-330 / US Mint 2026 Quarter Program | `gs://numista-reference-library/reference_library/2026_series/2026_quarter_dollar_us_constitution_obverse.jpg` & `_reverse.jpg` | `HTTP 200` |
| **`2026-NATIVE`** | 2026 Native American $1 Coin: Polly Cooper / Oneida | US Mint 2026 Native American $1 Coin Program | `gs://numista-reference-library/reference_library/2026_series/2026_american_innovation_obverse.jpg` & `2026_american_innovation_oneida_indian_nation_reverse.jpg` | `HTTP 200` |

---

## 3. Surgical 5-Gate Execution Plan

### Gate 1: Isolated Project-Wide Firestore Security Rules Patch (`numista_mobile/firestore.rules`)
> [!IMPORTANT]
> **SEPARATE EXPLICIT YES REQUIRED FROM FOUNDER ERIC FOR THIS STEP.**  
> Firestore rules are shared across the entire Firebase project (`studio-9101802118-8c9a8`) and reach the live production site. Therefore, this step is NOT preview-only and will be deployed ONLY after Eric provides an explicit separate YES.

#### Narrow, Read-Only Rule (Zero Wildcards, Zero Path to User Data):
In `numista_mobile/firestore.rules`, immediately before the catch-all deny rule at line 334:
```javascript
    // ── Global SKU Dictionaries (Narrow read-only for Add-by-SKU) ───────────
    match /global_metadata/{dictionary}/skus/{skuId} {
      allow read:  if request.auth != null && (dictionary == 'usmint_sku_dictionary' || dictionary == 'littleton_sku_dictionary');
      allow write: if false;  // backend admin SDK only
    }

    // ── Deny everything else ──────────────────────────────────────────────────
    match /{document=**} {
      allow read, write: if false;
    }
```
*Deployment Command:* `firebase deploy --only firestore:rules --project studio-9101802118-8c9a8`.

---

### Gate 2: Seed All 12 Canonical SKUs in Firestore (`scratch/seed_2026_skus.py`)
Run Python script with Application Default Credentials (ADC) to seed `global_metadata/usmint_sku_dictionary/skus/` with all 12 `_knownSkus` and Semiquincentennial SKUs:
1. `26SQRP`: `"2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll"`, program: `"Presidential $1 Coins"`, image: `"https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/MASTER_SEMIQDJT_image_1.jpg"`.
2. `26EA`: `"2026 American Eagle One Ounce Silver Proof Coin"`, program: `"American Eagle"`, year: `2026`.
3. `26XE`: `"2026 Morgan Silver Dollar Enhanced Uncirculated Coin"`, program: `"Morgan and Peace Dollars"`, year: `2026`.
4. `26XL`: `"2026 Peace Silver Dollar Reverse Proof Coin"`, program: `"Morgan and Peace Dollars"`, year: `2026`.
5. `26XH`: `"2026 Peace Silver Dollar Uncirculated Coin"`, program: `"Morgan and Peace Dollars"`, year: `2026`.
6. `26XF`: `"2026 Morgan Silver Dollar Proof Coin"`, program: `"Morgan and Peace Dollars"`, year: `2026`.
7. `26RJ`: `"2026 250th Anniversary Uncirculated Coin Set"`, program: `"Uncirculated Sets"`, year: `2026`, is_set: `true`.
8. `26GC`: `"2026 American Innovation $1 Coin Proof Set"`, program: `"American Innovation"`, year: `2026`, is_set: `true`.
9. `26RG`: `"2026 Clad Proof Set"`, program: `"Proof Sets"`, year: `2026`, is_set: `true`.
10. `23RG`: `"2023 Clad Proof Set"`, program: `"Proof Sets"`, year: `2023`, is_set: `true`.
11. `26RH`: `"2026 Silver Proof Set"`, program: `"Proof Sets"`, year: `2026`, is_set: `true`.
12. `23RH`: `"2023 Silver Proof Set"`, program: `"Proof Sets"`, year: `2023`, is_set: `true`.
13. `26RA`-`26RF`: 2026 Semiquincentennial individual rolls/sets.

---

### Gate 3: Comprehensive Fixes in `canonical_mint_asset_service.dart`

#### A. Key List in `extractSku` (`lines 73-83`):
```dart
    for (final k in const <String>[
      'mint_product_id',
      'sku',
      'product_code',
      'item_number',
      'Retailer Item No.',
      'retailer_item_no',
      'retailer_item_num',
    ]) {
      final val = (data[k] ?? '').toString().trim().toUpperCase();
      if (_knownSkus.contains(val)) return val;
    }
```

#### B. Normalization & Combined Extraction in `extractSku` (`lines 100-133`):
```dart
    final year = (data['year'] ?? data['Year'] ?? '')
        .toString()
        .trim()
        .replaceAll(RegExp(r'\.0$'), '');
    final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
    final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
    final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
    final denom = (data['Denomination'] ?? data['denomination'] ?? '').toString().toLowerCase();
    final cond = (data['Condition'] ?? data['condition'] ?? data['Strike Type'] ?? data['strike_type'] ?? '').toString().toLowerCase();
    final variety = (data['Variety'] ?? data['variety'] ?? '').toString().toLowerCase();
    final combined = '$prog $theme $title $denom $cond $variety';

    if (year == '2026') {
      if (combined.contains('silver eagle') || combined.contains('american eagle')) return '26EA';
      if (combined.contains('morgan') && combined.contains('enhanced')) return '26XE';
      if (combined.contains('morgan') && combined.contains('proof')) return '26XF';
      if (combined.contains('peace') && combined.contains('reverse proof')) return '26XL';
      if (combined.contains('peace') && (combined.contains('uncirculated') || combined.contains('dollar'))) return '26XH';
      if (combined.contains('uncirculated') && combined.contains('set')) return '26RJ';
      if (combined.contains('american innovation') && !combined.contains('polly cooper')) return '26GC';
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
            data['item_number'] ??
            data['Retailer Item No.'] ??
            data['retailer_item_no'] ??
            data['retailer_item_num'] ??
            '')
        .toString()
        .trim()
        .toUpperCase();
```

#### C. Year Normalization in `resolve()` (`line 184`):
```dart
    final cleanYear = (year ?? '').trim().replaceAll(RegExp(r'\.0$'), '');
```

#### D. Strict Lincoln Cent & Jefferson Nickel Mappings (MF-1):
```dart
      // 2026 Lincoln Cent (1c / Penny — e.g. 2026P cent swGtagWd, 2026S cent Ud8pJAq3)
      final isOneCentDenom = cleanDenom == '1c' ||
          cleanDenom == '1 cent' ||
          cleanDenom.contains('penny') ||
          RegExp(r'^1\b.*cent').hasMatch(cleanDenom);
      final isLincolnCentTitle = cleanTitle.contains('lincoln') ||
          cleanTitle.contains('penny') ||
          (RegExp(r'\b1\s*cent\b').hasMatch(cleanTitle) &&
              !cleanTitle.contains('5 cent') &&
              !cleanTitle.contains('10 cent') &&
              !cleanTitle.contains('25 cent') &&
              !cleanTitle.contains('50 cent'));
      if (isOneCentDenom || isLincolnCentTitle) {
        final effMint = cleanMint.isEmpty ? 'P' : cleanMint;
        return CanonicalMintAssetPair(
          sku: '2026-CENT-$effMint',
          obverseUrl: '$_base/2026_series/2026_one_cent_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_one_cent_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // 2026 Jefferson Nickel (5c — e.g. 2026S Bicentennial nickel 4w3cNG3P)
      final isNickelDenom = cleanDenom == '5c' ||
          cleanDenom.contains('5 cent') ||
          cleanDenom.contains('nickel');
      final isNickelTitle = cleanTitle.contains('nickel') ||
          cleanTitle.contains('jefferson') ||
          cleanTitle.contains('monticello');
      if (isNickelDenom || isNickelTitle) {
        final effMint = cleanMint.isEmpty ? 'S' : cleanMint;
        return CanonicalMintAssetPair(
          sku: '2026-NICKEL-$effMint',
          obverseUrl: '$_base/2026_series/2026_five_cent_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_five_cent_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
```

#### E. Quarter-Guarded Half Dollar & All 5 Semiquincentennial Quarters + Polly Cooper (MF-3):
```dart
      final isQuarter = cleanDenom.contains('25') ||
          cleanDenom.contains('quarter') ||
          cleanTitle.contains('quarter');

      // Half Dollar Guarded Against Quarters (line 332)
      if (!isQuarter &&
          (cleanTitle.contains('kennedy') ||
              cleanTitle.contains('half dollar') ||
              cleanDenom.contains('50c') ||
              cleanDenom.contains('half') ||
              cleanTitle.contains('enduring liberty') ||
              cleanTitle.contains('independence'))) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvUrl = effMint == 'D'
            ? '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'
            : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-HALF-$effMint',
          obverseUrl: obvUrl,
          reverseUrl: '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg',
          fallbackObverseUrl: effMint == 'P'
              ? '$_base/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg'
              : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg',
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // Quarter 1: Mayflower Compact
      if (cleanTitle.contains('mayflower')) {
        return CanonicalMintAssetPair(
          sku: '2026-QTR-MAYFLOWER',
          obverseUrl: '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // Quarter 2: Declaration of Independence
      if (cleanTitle.contains('declaration') || (isQuarter && cleanTitle.contains('independence'))) {
        return CanonicalMintAssetPair(
          sku: '2026-QTR-INDEPENDENCE',
          obverseUrl: '$_base/2026_series/2026_quarter_dollar_declaration_of_independence_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_quarter_dollar_declaration_of_independence_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // Quarter 3: Gettysburg Address
      if (cleanTitle.contains('gettysburg')) {
        return CanonicalMintAssetPair(
          sku: '2026-QTR-GETTYSBURG',
          obverseUrl: '$_base/2026_series/2026_quarter_dollar_gettysburg_address_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_quarter_dollar_gettysburg_address_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // Quarter 4: Revolutionary War
      if (cleanTitle.contains('revolutionary')) {
        return CanonicalMintAssetPair(
          sku: '2026-QTR-REVOLUTIONARY',
          obverseUrl: '$_base/2026_series/2026_quarter_dollar_revolutionary_war_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_quarter_dollar_revolutionary_war_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // Quarter 5: U.S. Constitution
      if (cleanTitle.contains('constitution')) {
        return CanonicalMintAssetPair(
          sku: '2026-QTR-CONSTITUTION',
          obverseUrl: '$_base/2026_series/2026_quarter_dollar_us_constitution_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_quarter_dollar_us_constitution_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }

      // Polly Cooper (Oneida Indian Nation Native American $1)
      if (cleanTitle.contains('polly cooper') || cleanTitle.contains('oneida')) {
        return CanonicalMintAssetPair(
          sku: '2026-NATIVE-POLLY-COOPER',
          obverseUrl: '$_base/2026_series/2026_american_innovation_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_american_innovation_oneida_indian_nation_reverse.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
```

---

### Gate 4: Complete UI & Service Wiring + Fallback Retry (MF-4 & MF-5)

#### A. Wire `my_collection_screen.dart:6357` (`_CollectionCardImage.build`):
```dart
  @override
  Widget build(BuildContext context) {
    // 1. Check Canonical Mint Assets first (returns null if user uploaded photos)
    final canonical = CanonicalMintAssetService.resolveFromMap(data);
    if (canonical != null) {
      final primaryUrl = canonical.reverseUrl.isNotEmpty
          ? canonical.reverseUrl
          : canonical.obverseUrl;
      final fallbackUrl = canonical.fallbackReverseUrl ??
          (primaryUrl != canonical.obverseUrl ? canonical.obverseUrl : canonical.fallbackObverseUrl);
      if (primaryUrl.isNotEmpty) {
        return _buildCoinImage(primaryUrl, fallbackUrl: fallbackUrl);
      }
    }

    final obv = _cleanUrl(data[_F.imageObverse]);
    final rev = _cleanUrl(data[_F.imageReverse]);
    final directUrl = rev.isNotEmpty ? rev : obv;

    if (directUrl.isNotEmpty) {
      return _buildCoinImage(directUrl);
    }
```

#### B. Update `_buildCoinImage` (`my_collection_screen.dart:6424`) with Fallback Retry:
```dart
  Widget _buildCoinImage(String url, {String? fallbackUrl}) {
    return Image.network(
      url,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) {
        if (fallbackUrl != null && fallbackUrl.isNotEmpty && fallbackUrl != url) {
          return Image.network(
            fallbackUrl,
            fit: BoxFit.contain,
            errorBuilder: (context, error, stackTrace) {
              return Center(
                child: Icon(
                  Icons.image_not_supported_outlined,
                  size: 40,
                  color: AppTheme.textSecondary.withOpacity(0.5),
                ),
              );
            },
          );
        }
        return Center(
          child: Icon(
            Icons.image_not_supported_outlined,
            size: 40,
            color: AppTheme.textSecondary.withOpacity(0.5),
          ),
        );
      },
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return const Center(child: CircularProgressIndicator(strokeWidth: 2));
      },
    );
  }
```

#### C. Wire `my_collection_screen.dart:3467` (`_showCoinInspectorDialog`):
```dart
    final canonical = CanonicalMintAssetService.resolveFromMap(data);
    final obvUrl = (!CanonicalMintAssetService.hasUserUploadedPhotos(data) && canonical != null && canonical.obverseUrl.isNotEmpty)
        ? canonical.obverseUrl
        : (data[_F.imageObverse] ?? '').toString().trim();
    final revUrl = (!CanonicalMintAssetService.hasUserUploadedPhotos(data) && canonical != null && canonical.reverseUrl.isNotEmpty)
        ? canonical.reverseUrl
        : (data[_F.imageReverse] ?? '').toString().trim();
```

#### D. Wire `coin_image_service.dart:489` (`fetchReferenceImages` Entry Point):
```dart
  static Future<CoinImageResult> fetchReferenceImages({
    required String year,
    String? mint,
    String? denomination,
    String? series,
    String? subject,
  }) async {
    try {
      final canonical = CanonicalMintAssetService.resolve(
        title: '${series ?? ''} ${subject ?? ''}'.trim(),
        year: year.replaceAll(RegExp(r'\.0$'), ''),
        mintMark: mint,
        denomination: denomination,
      );
      if (canonical != null) {
        return CoinImageResult(
          obverseUrl: canonical.obverseUrl,
          reverseUrl: canonical.reverseUrl,
          attribution: 'U.S. Mint / Numista Reference Library',
          label: canonical.sku,
          matchKey: canonical.sku,
        );
      }
```

#### E. Wire `add_coins_hub.dart:2638` (`_addSkuToCollection` Field Stamping):
```dart
      final resolvedSku = (data['sku'] ?? _skuCtrl.text.trim()).toString().trim().toUpperCase();
      final coinDoc = <String, dynamic>{
        'source': 'manual_sku',
        'sku': resolvedSku,
        'item_number': resolvedSku,
        'Retailer Item No.': resolvedSku,
        'Added': FieldValue.serverTimestamp(),
        'created_at': FieldValue.serverTimestamp(),
        'committed_at': FieldValue.serverTimestamp(),
        'deep_dive_status': 'PENDING',
        'is_demo': false,
        'is_demo_cleared': false,
      };
```

#### F. In-Memory Static SKU Fallback in `_lookupSku()` (`add_coins_hub.dart:2610-2627`):
```dart
      if (!snap.exists) {
        final fallback = _kFallbackUsMintSkus[docId];
        if (fallback != null) {
          setState(() {
            _skuResult = fallback;
            _skuLoading = false;
          });
          return;
        }
        ...
      }
    } catch (e) {
      final fallback = _kFallbackUsMintSkus[docId];
      if (fallback != null) {
        setState(() {
          _skuResult = fallback;
          _skuLoading = false;
        });
        return;
      }
      ...
    }
```
*Note:* Checking `_kFallbackUsMintSkus` in BOTH `!snap.exists` and `catch (e)` guarantees that permission errors and missing docs succeed gracefully.

---

### Gate 5: Verification & Deployment Gates (Upon Eric Typed YES)

1. **Unit Tests:**
   Add unit tests in `canonical_mint_asset_service_test.dart` covering:
   - Lincoln Cent with `1¢` denomination and title containing `Penny` / `Lincoln` (assert resolves `2026-CENT-P` / `2026-CENT-S`).
   - Semiquincentennial Quarter containing `"cent"` in `semiquincentennial` (assert resolves to Quarter, NOT Cent).
   - `Declaration of Independence` Quarter (assert resolves `2026-QTR-INDEPENDENCE`, NOT `2026-HALF-S`).
   - Float year `2026.0` / `2023.0` strings (assert stripped and resolved correctly).
   - `extractSku()` with `Condition: 'Reverse Proof'` and `Year: '2026.0'` (assert returns `26XL`).
   Run: `flutter test test/services/canonical_mint_asset_service_test.dart` (assert 100% pass).
2. **Static Analysis:**
   Run: `flutter analyze` (assert 0 issues).
3. **Firestore Security Rules Deploy (Subject to Separate Typed YES):**
   Run: `firebase deploy --only firestore:rules --project studio-9101802118-8c9a8`.
4. **Build & Deploy:**
   Run: `flutter build web --release`
   Update `version.json` with commit hash and timestamp.
   Deploy: `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`.
   Verify: HTTP 200 on `https://numista-vault--p7-gate-8avtpz22.web.app/version.json`.
5. **Git Push:**
   Commit and push exclusively to `origin/p7-v8.9`.
   `origin/main` remains strictly locked at `9f04550a`.

---

## 4. Acceptance Criteria Checklist for Field Tester

- [ ] Log in as `grokbot@numista.ai` on `https://numista-vault--p7-gate-8avtpz22.web.app`.
- [ ] In My Collection (Grid View & Table View Inspector):
  - [ ] 2026 Morgan Dollar shows genuine reverse asset (no grey placeholder).
  - [ ] 2026 Peace Dollar Reverse Proof renders HTTP 200 canonical image.
  - [ ] 2023 Edith Kanaka'ole Quarter renders HTTP 200 canonical image.
  - [ ] 2026 Lincoln Cent (1c) renders Lincoln Cent asset.
  - [ ] 2026 Semiquincentennial Quarters (including Declaration of Independence) render proper Quarter obverse/reverse.
  - [ ] 2026 Polly Cooper Oneida Indian Nation renders official reverse asset.
- [ ] In Add Coins Hub -> Add by SKU:
  - [ ] Input `26SQRP` -> Displays "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll" with image and metadata. Zero "Session expired" error.
  - [ ] Click "Add to Collection" -> Added successfully, renders canonical image in collection.

---

## 5. Next Action & Turn Protocol

- **Baton passed to:** Review Swarm (Argon / Grok CoS $\ge 95$ / SAG) $\rightarrow$ Founder Eric typed **YES**.
- **AG CoS Status:** Standing by in PLAN ONLY mode. AG's 2nd and final try complete.
