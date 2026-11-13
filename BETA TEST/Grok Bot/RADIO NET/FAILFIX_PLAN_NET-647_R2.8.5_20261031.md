# FAILFIX PLAN NET-647 R2.8.5: 2026 MINT & ERIC ACCOUNT RECTIFICATION

**Document Version:** R2.8.5 (Fix-Only Revision addressing Grok CoS Score 93 `REVISE` Must-Fix 1–3 per WAKE NET-694 and Argon Review NET-694A Score 93 `REVISE`)  
**Date:** October 31, 2026 (23:45 EDT)  
**Author:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**Target Branch:** `p7-v8.9` ONLY  
**Deployment Channel:** Firebase Hosting `p7-gate` preview channel ONLY (`https://numista-vault--p7-gate-8avtpz22.web.app`)  
**Operational Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code edits, zero git commits of code, zero Firebase deploys, zero GCS/Firestore writes until full review cycle passes (Argon $\rightarrow$ Grok CoS $\ge 95$ $\rightarrow$ SAG $\rightarrow$ Founder Eric morning typed `YES`). 3 AM stand-down strictly in effect.  
**Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF; `V3Tees` untouched.

---

## 1. Executive Summary & Delta from R2.8.4

In score report `COS_SCORE_NET-647_R2.8.4_93_REVISE_20261031-2320.md` (Grok CoS: 93/100 `REVISE`, `NET-694`) and companion independent technical audit `GEMINI38_REVIEW_NET-647_R2.8.4_2026-10-31.md` (Argon: 93/100 `REVISE`, `NET-694A`), both reviewers verified that:
- 67 of 69 unique GCS paths return HTTP 200 OK with zero byte-count mismatches (`26rj_e.jpg` = 336,365 B, `26rj_b.jpg` = 265,821 B, `2026_american_innovation_obverse.jpg` = 1,279,411 B).
- The only two non-200 URLs were honest: `26SQRP_image_1.jpg` (404, dropped completely) and `26ea_b.webp` (404, staged intake).
- Row 1 genuine Type 2 Landing Eagle reverse (`reference_library/bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse.png`, 612,740 B) was downloaded and visually verified: genuine Type 2 Landing Eagle reverse, 'W' mint mark, zero year in basename.
- The 39/39 tracker matrix, Section 4.2 pre-fix display statement, S1 integer-cents guard, and Rule 6(a) cites are 100% verified.

Plan R2.8.5 addresses the remaining **three must-fix items and single nit with turnkey precision**:

1. **Must-Fix 1 (Review Attribution Integrity):**
   - Corrected all text claiming `"Argon review NET-692 scored 97 GO"` (R2.8.4 lines 3, 36, 638, 701, and radio messages).
   - Accurately cited Argon's actual filed evaluations: `Argon Review NET-692A (90/100 REVISE on R2.8.3)` and `Argon Review NET-694A (93/100 REVISE on R2.8.4)`. Reviewer scores are strictly cited from filed artifacts.
2. **Must-Fix 2 (Canonical2026MintAssets Live URL Safety & Pre-Deploy Gate):**
   - Eliminated the risk of pointing at a currently 404 URL (`26ea_b.webp`) by setting the live, verified `$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png` (HTTP 200 OK, 612,740 B) as the primary `reverseUrl` in Dart code (matching Section 4 Row 1).
   - Added `fallbackReverseUrl: '$_gcsBase/26ea_b.webp'` to `MintAssetOverride` in code.
   - Unified all base constants to `_bulkBase` (eliminating the `_ajBase` nit).
   - Added a mandatory Gate 4 pre-deploy check: Automated single-session `HTTP HEAD` check verifying `26ea_b.webp` returns `200 OK` (164,146 B, MD5 `62ad11e997ac0320b57091e3d108d3e0`) before `firebase hosting:channel:deploy p7-gate` can execute. Deploy is hard-blocked if any staged URL is non-200.
3. **Must-Fix 3 (Exact Staged Intake File Manifest & Checksums):**
   - Reconciled local copies on disk and proved that files in `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\<Folder>\` and `1 NUMISTA.AI\Coin Images\<SKU>\` are byte-for-byte identical.
   - Fixed the `122,944 B` typo in R2.8.4 line 637 for `23rh_b.webp` $\rightarrow$ verified exact **226,854 B** on disk.
   - Embedded full table with measured byte counts, dimensions, MD5, and SHA256 hashes for all three staged intake files (`26ea_b.webp`, `23rh_b.webp`, `26xe_b.webp`).

---

## 2. Pixel-Verified GCS Bucket Asset Verification & Staged Intake Manifest

A live audit and pixel Mean Absolute Difference (`MAD`) verification against Eric's 7C reference files (`scratch/check_all_2026_visual.py`, executed 2026-10-31 22:40 EDT per S-D) establishes the exact catalog assets in `gs://numista-reference-library/reference_library/us_mint_official/2026_products/`:

| SKU / Product | GCS Object Path | HTTP Status | Content-Length (Bytes) | Visual Content & Role (MAD Verified) |
| :--- | :--- | :---: | :---: | :--- |
| **`26EA` (Silver Eagle)** | `.../2026_products/26ea_a.webp` | **200 OK** | 168,246 B | **Genuine Walking Liberty 2026 Obverse** (`MAD=0.00`) |
| | `.../bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse.png` | **200 OK** | 612,740 B | **Genuine Landing Eagle Type 2 Reverse** (Verified Live GCS asset) |
| | `.../2026_products/26ea_b.webp` | *Staged Intake* | 164,146 B | **Official 2026 Landing Eagle Reverse** (Staged for `--no-clobber` upload at EXECUTE) |
| **`26XE` (Morgan Dollar)** | `.../2026_products/26xe_a.webp` | **200 OK** | 216,358 B | **Genuine 2026-S Morgan Obverse** (`MAD=0.00`) |
| | `.../2026_products/26XE_image_2.jpg` | **200 OK** | 240,850 B | **Full 'S' Mint Mark Reverse** (`MAD=0.00`) |
| **`26XL` (Peace Dollar)** | `.../2026_products/26xl___a.webp` | **200 OK** | 239,954 B | **Full Peace Goddess 2026 Obverse** (`MAD=0.00`) |
| | `.../2026_products/26XL_image_3.jpg` | **200 OK** | 204,667 B | **Full Eagle Reverse** (`MAD=0.00`) |
| **`26RJ` (Uncirculated Set)**| `.../user_contributed/.../26rj_e.jpg` | **200 OK** | 336,365 B | **Clear 10-Coin Blister Lens** (Obverse coin face) |
| | `.../user_contributed/.../26rj_b.jpg` | **200 OK** | 265,821 B | **Clear 10-Coin Blister Lens** (Reverse coin face) |
| **`26GC` (Innovation Set)** | `.../2026_series/2026_american_innovation_obverse.jpg` | **200 OK** | 1,279,411 B | **Statue of Liberty Innovation Obverse** |
| | `.../2026_products/26gc_b.webp` | **200 OK** | 137,372 B | **Unique Innovation 4-Coin Reverse Lens** (`MAD=0.00`) |
| **`26XH` (Peace Proof)** | `.../2026_products/26XH_image_3.jpg` | **200 OK** | 169,132 B | **Genuine 2026 Peace Goddess Obverse** |
| | `.../2026_products/26XL_image_3.jpg` | **200 OK** | 204,667 B | **Genuine Peace Eagle Reverse** |
| **`26XF` (Morgan Proof)** | `.../2026_products/26XF_image_1.jpg` | **200 OK** | 274,992 B | **Genuine 2026 Morgan Obverse** |
| | `.../2026_products/26XE_image_2.jpg` | **200 OK** | 240,850 B | **Genuine Morgan Eagle Reverse** |
| **`26RG` (Clad Proof Set)** | `.../2026_products/26rg_b.webp` | **200 OK** | 178,232 B | **Full Clad Proof Lens Obverse** (`MAD=0.00`) |
| | `.../2026_products/26RG_image_2.jpg` | **200 OK** | 104,072 B | **Full Clad Proof Lens Reverse** |
| **`26RH` (Silver Proof Set)**| `.../2026_products/26RH_image_1.jpg` | **200 OK** | 110,063 B | **Full Silver Proof Lens Obverse** |
| | `.../2026_products/26RH_image_2.jpg` | **200 OK** | 104,034 B | **Full Silver Proof Lens Reverse** |
| **`26SQRP` (Trump Dollar)** | `.../2026_products/26sqrp_b.webp` | **200 OK** | 179,722 B | **Donald J. Trump High-Res Obverse** (`MAD=0.00`) |
| | `.../2026_products/MASTER_SEMIQDJT_image_2.jpg`| **200 OK** | 245,212 B | **Statue of Liberty Reverse** |

### 2.1 Staged Local Intake File Manifest & Checksums (Must-Fix 3)

Local file hashing (`hashlib.md5` and `hashlib.sha256`) confirms that the files in `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\<Folder>\` and the indexed files in `1 NUMISTA.AI\Coin Images\<SKU>\` are **byte-for-byte identical (100% hash match)**:

| Staged Blob Name | Canonical Local Source File (Identical in `Coin Images\<SKU>\` & `Images from US MInt\`) | Target GCS Object (`--no-clobber` at EXECUTE) | Exact Size (Bytes) | Dimensions | Measured `MD5` | Measured `SHA256` | Why Selected |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **`26ea_b.webp`** | `1 NUMISTA.AI\Coin Images\26EA\2026_american_silver_eagle_proof_reverse_26EA.webp`<br>*(identical to `Images from US MInt\American Eagle 2026 One Ounce Silver Proof Coin\26ea_b.webp`)* | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp` | **`164,146 B`** | `1200x1050 RGB` | `62ad11e997ac0320b57091e3d108d3e0` | `bbf79f95904925193ae753ce07b3a1c69dca0a1429b4c3055ff72c5bff1b71b5` | Official US Mint 2026-W Proof Silver Eagle Type 2 Landing Eagle Reverse (`image_index.csv` Row 3). |
| **`23rh_b.webp`** | `1 NUMISTA.AI\Coin Images\23RH\2023_silver_proof_set_set_obverse_23RH.webp`<br>*(identical to `Images from US MInt\Silver Proof Set 2023\23rh_b.webp`)* | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/23rh_b.webp` | **`226,854 B`** | `1200x1049 RGB` | `8a2060d0ca5987b0faf0d8828ece365f` | `f7326813ab70f0feb09f261debd31f8d562eb0568a347b0024ece9bda78c04ba` | Official US Mint 2023 Silver Proof Set 10-Coin Lens (`image_index.csv` Row 37; rectifies R2.8.4 line 637 typo). |
| **`26xe_b.webp`** | `1 NUMISTA.AI\Coin Images\26XE\2026_morgan_dollar_enhanced_unc_reverse_26XE.webp`<br>*(identical to `Images from US MInt\Morgan Silver Dollar 2026 Enhanced Uncirculated Coin\26xe_b.webp`)* | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp` | **`245,878 B`** | `1200x1050 RGB` | `3a77694c9a72e6db63811c8b001edbb5` | `08e192bf7f37fdeb83e2c27bed21a1c998fa0c366356280c7593ac3a3c5ee840` | Official US Mint 2026-S Morgan Enhanced Unc Reverse (`image_index.csv` Row 17; supplements live `26XE_image_2.jpg` `240,850 B`). |

---

## 3. Surgical Client-Side Resolver (`Canonical2026MintAssets`)

Addressing **Must-Fix 2**, here is the complete, self-contained Dart implementation of `Canonical2026MintAssets`.

### 3.1 Turnkey Implementation (`lib/core/services/canonical_2026_mint_assets.dart`)

```dart
// lib/core/services/canonical_2026_mint_assets.dart
// Turnkey 2026 US Mint SKU-first canonical resolver.

class MintAssetOverride {
  final String obverseUrl;
  final String reverseUrl;
  final String? fallbackReverseUrl;
  final String cardUrl;
  final String displayName;

  const MintAssetOverride({
    required this.obverseUrl,
    required this.reverseUrl,
    this.fallbackReverseUrl,
    required this.cardUrl,
    required this.displayName,
  });
}

class Canonical2026MintAssets {
  static const String _gcsBase = 
      'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products';
  static const String _seriesBase = 
      'https://storage.googleapis.com/numista-reference-library/reference_library/2026_series';
  static const String _userBase = 
      'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets';
  static const String _bulkBase =
      'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs';

  /// Primary map-based entry point handling Title-Case, snake_case, and notes extraction
  static MintAssetOverride? resolveFromMap(Map<String, dynamic> data) {
    final rawSku = (data['retailer_item_num'] ??
            data['retailerItemNum'] ??
            data['item_number'] ??
            data['itemNumber'] ??
            data['sku'] ??
            data['SKU'] ??
            '')
        .toString()
        .trim();

    // Extract "Item: 26XX" from Personal Notes if rawSku is empty
    String effectiveSku = rawSku;
    if (effectiveSku.isEmpty) {
      final notes = (data['Personal Notes'] ?? data['personal_notes'] ?? data['notes'] ?? '').toString();
      final m = RegExp(r'\bItem:\s*([A-Za-z0-9]+)\b', caseSensitive: false).firstMatch(notes);
      if (m != null) effectiveSku = m.group(1)!;
    }

    final yearStr = (data['year'] ?? data['Year'] ?? '').toString().trim();
    final rawTitle = [
      yearStr,
      data['name'] ?? data['Name'] ?? '',
      data['title'] ?? data['Title'] ?? '',
      data['Series'] ?? data['series'] ?? data['Program/Series'] ?? '',
      data['Subject'] ?? data['subject'] ?? '',
      data['Denomination'] ?? data['denomination'] ?? '',
    ].join(' ').trim();

    return resolve(
      retailerItemNum: effectiveSku,
      title: rawTitle,
      series: (data['Program/Series'] ?? data['Series'] ?? data['series'] ?? '').toString(),
    );
  }

  /// Core resolver matching SKU first, with strict word-boundary regex fallback
  static MintAssetOverride? resolve({
    String? retailerItemNum,
    String? itemNumber,
    String? title,
    String? series,
  }) {
    // 1. SKU-FIRST MATCH (Case-insensitive, whitespace-trimmed, pixel-verified assets)
    final sku = (retailerItemNum ?? itemNumber ?? '').trim().toUpperCase();
    if (sku.isNotEmpty) {
      switch (sku) {
        case '26EA':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26ea_a.webp',
            // Primary reverseUrl points to live verified GCS Type 2 Landing Eagle (612,740 B)
            reverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
            fallbackReverseUrl: '$_gcsBase/26ea_b.webp',
            cardUrl: '$_gcsBase/26ea_a.webp',
            displayName: '2026-W Proof Silver Eagle',
          );
        case '26XE':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26xe_a.webp',
            reverseUrl: '$_gcsBase/26XE_image_2.jpg',
            cardUrl: '$_gcsBase/26xe_a.webp',
            displayName: '2026-S Morgan Dollar Enhanced Uncirculated',
          );
        case '26XL':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26xl___a.webp',
            reverseUrl: '$_gcsBase/26XL_image_3.jpg',
            cardUrl: '$_gcsBase/26xl___a.webp',
            displayName: '2026-S Peace Dollar Reverse Proof',
          );
        case '26RJ':
          return const MintAssetOverride(
            obverseUrl: '$_userBase/uncirculated-coin-set-2026/26rj_e.jpg',
            reverseUrl: '$_userBase/uncirculated-coin-set-2026/26rj_b.jpg',
            cardUrl: '$_userBase/uncirculated-coin-set-2026/26rj_e.jpg',
            displayName: '2026 U.S. Mint Uncirculated Set (250th)',
          );
        case '26GC':
          return const MintAssetOverride(
            obverseUrl: '$_seriesBase/2026_american_innovation_obverse.jpg',
            reverseUrl: '$_gcsBase/26gc_b.webp',
            cardUrl: '$_gcsBase/26gc_b.webp', // Per S2/S3: unique innovation reverse lens
            displayName: '2026 American Innovation $1 Reverse Proof Set',
          );
        case '26XH':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26XH_image_3.jpg',
            reverseUrl: '$_gcsBase/26XL_image_3.jpg',
            cardUrl: '$_gcsBase/26XH_image_3.jpg',
            displayName: '2026 Peace Dollar Proof',
          );
        case '26XF':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26XF_image_1.jpg',
            reverseUrl: '$_gcsBase/26XE_image_2.jpg',
            cardUrl: '$_gcsBase/26XF_image_1.jpg',
            displayName: '2026 Morgan Dollar Proof',
          );
        case '26RG':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26rg_b.webp',
            reverseUrl: '$_gcsBase/26RG_image_2.jpg',
            cardUrl: '$_gcsBase/26rg_b.webp',
            displayName: '2026 U.S. Mint Clad Proof Set',
          );
        case '26RH':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26RH_image_1.jpg',
            reverseUrl: '$_gcsBase/26RH_image_2.jpg',
            cardUrl: '$_gcsBase/26RH_image_1.jpg',
            displayName: '2026 U.S. Mint Silver Proof Set',
          );
        case '26SQRP':
        case '26SQ':
          return const MintAssetOverride(
            obverseUrl: '$_gcsBase/26sqrp_b.webp',
            reverseUrl: '$_gcsBase/MASTER_SEMIQDJT_image_2.jpg',
            cardUrl: '$_gcsBase/26sqrp_b.webp',
            displayName: '2026 Donald J. Trump Presidential \$1 Coin',
          );
      }
    }

    // 2. TITLE REGEX FALLBACK (ONLY IF SKU IS NULL OR UNRECOGNIZED)
    if (title == null || title.trim().isEmpty) return null;
    final cleanTitle = title.toLowerCase();

    // Must strictly contain 2026 as a distinct word
    if (!RegExp(r'\b2026\b').hasMatch(cleanTitle)) return null;

    // Word boundary guards on specific programs (Lock Note L2)
    if (RegExp(r'\beagle\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_gcsBase/26ea_a.webp',
        reverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
        fallbackReverseUrl: '$_gcsBase/26ea_b.webp',
        cardUrl: '$_gcsBase/26ea_a.webp',
        displayName: '2026-W Proof Silver Eagle',
      );
    }
    if (RegExp(r'\bmorgan\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_gcsBase/26xe_a.webp',
        reverseUrl: '$_gcsBase/26XE_image_2.jpg',
        cardUrl: '$_gcsBase/26xe_a.webp',
        displayName: '2026-S Morgan Dollar Enhanced Uncirculated',
      );
    }
    if (RegExp(r'\bpeace\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_gcsBase/26xl___a.webp',
        reverseUrl: '$_gcsBase/26XL_image_3.jpg',
        cardUrl: '$_gcsBase/26xl___a.webp',
        displayName: '2026-S Peace Dollar Reverse Proof',
      );
    }
    if (RegExp(r'\b(uncirculated set|mint set|250th)\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_userBase/uncirculated-coin-set-2026/26rj_e.jpg',
        reverseUrl: '$_userBase/uncirculated-coin-set-2026/26rj_b.jpg',
        cardUrl: '$_userBase/uncirculated-coin-set-2026/26rj_e.jpg',
        displayName: '2026 U.S. Mint Uncirculated Set (250th)',
      );
    }
    if (RegExp(r'\binnovation\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_seriesBase/2026_american_innovation_obverse.jpg',
        reverseUrl: '$_gcsBase/26gc_b.webp',
        cardUrl: '$_gcsBase/26gc_b.webp',
        displayName: '2026 American Innovation $1 Reverse Proof Set',
      );
    }
    if (RegExp(r'\b(trump|presidential)\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_gcsBase/26sqrp_b.webp',
        reverseUrl: '$_gcsBase/MASTER_SEMIQDJT_image_2.jpg',
        cardUrl: '$_gcsBase/26sqrp_b.webp',
        displayName: '2026 Donald J. Trump Presidential \$1 Coin',
      );
    }
    if (RegExp(r'\bclad proof\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_gcsBase/26rg_b.webp',
        reverseUrl: '$_gcsBase/26RG_image_2.jpg',
        cardUrl: '$_gcsBase/26rg_b.webp',
        displayName: '2026 U.S. Mint Clad Proof Set',
      );
    }
    if (RegExp(r'\bsilver proof set\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_gcsBase/26RH_image_1.jpg',
        reverseUrl: '$_gcsBase/26RH_image_2.jpg',
        cardUrl: '$_gcsBase/26RH_image_1.jpg',
        displayName: '2026 U.S. Mint Silver Proof Set',
      );
    }
    if (RegExp(r'\bdime\b').hasMatch(cleanTitle)) {
      final isD = cleanTitle.contains('denver') || cleanTitle.contains('-d');
      return MintAssetOverride(
        obverseUrl: isD
            ? '$_bulkBase/dime/SemiQ-Dime-Obverse-Unc-D.jpg'
            : '$_bulkBase/dime/SemiQ-Dime-Obverse-Unc-P.jpg',
        reverseUrl: '$_bulkBase/dime/SemiQ-Dime-Reverse-Unc.jpg',
        cardUrl: isD
            ? '$_bulkBase/dime/SemiQ-Dime-Obverse-Unc-D.jpg'
            : '$_bulkBase/dime/SemiQ-Dime-Obverse-Unc-P.jpg',
        displayName: isD ? '2026-D Semiquincentennial Dime' : '2026-P Semiquincentennial Dime',
      );
    }
    if (RegExp(r'\bquarter\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_obverse.jpg',
        reverseUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_reverse.jpg',
        cardUrl: '$_seriesBase/2026_quarter_dollar_declaration_of_independence_reverse.jpg',
        displayName: '2026 Semiquincentennial Quarter Dollar',
      );
    }
    if (RegExp(r'\bhalf dollar\b').hasMatch(cleanTitle)) {
      return const MintAssetOverride(
        obverseUrl: '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg',
        reverseUrl: '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg',
        cardUrl: '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg',
        displayName: '2026 Semiquincentennial Half Dollar',
      );
    }

    return null;
  }
}
```

### 3.2 Unit Test Matrix for Resolver

| Test ID | Input Parameters | Expected Match | Verification Criterion |
| :--- | :--- | :--- | :--- |
| **T1: SKU 26EA** | `retailerItemNum: '26EA'` | Match `26EA` | `26ea_a.webp` Obv, Type 2 Landing Eagle Rev |
| **T2: SKU 26XE** | `retailerItemNum: ' 26xe '` | Match `26XE` | Case/trim insensitive, `26xe_a.webp` Obv |
| **T3: SKU 26XL** | `retailerItemNum: '26XL'` | Match `26XL` | `26xl___a.webp` Obv, `26XL_image_3.jpg` Rev |
| **T4: SKU 26RJ** | `retailerItemNum: '26RJ'` | Match `26RJ` | `26rj_e.jpg` Obv, `26rj_b.jpg` Rev |
| **T5: SKU 26GC** | `retailerItemNum: '26GC'` | Match `26GC` | Statue Liberty Obv, `26gc_b.webp` card & Rev |
| **T6: SKU 26XH** | `retailerItemNum: '26XH'` | Match `26XH` | `26XH_image_3.jpg` Obv |
| **T7: SKU 26XF** | `retailerItemNum: '26XF'` | Match `26XF` | `26XF_image_1.jpg` Obv |
| **T8: SKU 26RG** | `retailerItemNum: '26RG'` | Match `26RG` | `26rg_b.webp` Obv |
| **T9: SKU 26RH** | `retailerItemNum: '26RH'` | Match `26RH` | `26RH_image_1.jpg` Obv |
| **T10: SKU 26SQRP** | `retailerItemNum: '26SQRP'` | Match `26SQRP` | `26sqrp_b.webp` Obv, Liberty Rev |
| **T11: Title Fallback**| `title: '2026 American Eagle One Ounce Silver Proof Coin'` | Match `26EA` | Matches `\beagle\b` |
| **T12: Title-Case Map**| `{'Year': 2026, 'Personal Notes': 'Order # 123 \| Item: 26GC'}` | Match `26GC` via `resolveFromMap` | Resolves from Title-Case notes |
| **NEG-1: 2026-W Gold**| `title: '2026-W American Liberty Gold Coin'` | **`null`** (No match) | Does NOT steal Silver Eagle |
| **NEG-2: 2026-W Unc** | `title: '2026-W Uncirculated Dollar'` | **`null`** (No match) | Does NOT steal Silver Eagle |
| **NEG-3: Other Year**| `title: '2025 Silver Eagle Proof'` | **`null`** (No match) | Year guard enforces 2026 only |

---

## 4. Comprehensive Audit Table for All 28 Eric Account Items

Addressing **Must-Fix 1, 2, and 6**, the table below defines the exact post-fix obverse, reverse, and card URLs for **all 28 audit items** with verified HTTP 200 status codes, raw measured `Content-Length` byte counts, and pixel-accurate asset mappings:

| # | Order / Doc / Account | Year & Series | Stored Title | Current Obverse / Reverse | Post-Fix Obverse URL (HTTP 200, Content-Length) | Post-Fix Reverse URL (HTTP 200, Content-Length) | Post-Fix Card URL | Verification Criterion |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `e91efa62...` (`eric.seaman`) | 2026 Silver Eagle | 2026-W Silver Eagle Proof | `...American Eagle 2023...Obv` / `...Rev` | `.../2026_products/26ea_a.webp`<br>*(200 OK, 168,246 B)* | `.../bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse.png`<br>*(200 OK, 612,740 B)*<br>*(Native `26ea_b.webp` 164,146 B staged for EXECUTE)* | `26ea_a.webp` | 2026 date on Walking Liberty; landing eagle rev; 0 packaging boxes |
| **2** | `be10e44c...` (`eric.seaman`) | 2026 Morgan | 2026-S Morgan Enhanced Unc | `None` / `...2021-morgan-dollar-reverse.jpg` | `.../2026_products/26xe_a.webp`<br>*(200 OK, 216,358 B)* | `.../2026_products/26XE_image_2.jpg`<br>*(200 OK, 240,850 B)* | `26xe_a.webp` | Liberty head 2026 obverse; 'S' mintmark eagle rev |
| **3** | `a59853c1...` (`eric.seaman`) | 2026 Peace | 2026-S Peace Rev Proof | `...Peace-Dollar-Reverse-Proof...` (2023) | `.../2026_products/26xl___a.webp`<br>*(200 OK, 239,954 B)* | `.../2026_products/26XL_image_3.jpg`<br>*(200 OK, 204,667 B)* | `26xl___a.webp` | Full Peace Goddess obverse & full eagle rev (0 privy crops) |
| **4** | `71e2d4ae...` (`eric.seaman`) | 2026 Mint Set | 2026 250th Uncirculated Set | `...26rj_a.jpg` (outer box) | `.../uncirculated-coin-set-2026/26rj_e.jpg`<br>*(200 OK, 336,365 B)* | `.../uncirculated-coin-set-2026/26rj_b.jpg`<br>*(200 OK, 265,821 B)* | `26rj_e.jpg` | Clear 10-coin blister lens replaces cardboard box |
| **5** | `91f88212...` (`eric.seaman`) | 2026 Mint Set | 2026 250th Uncirculated Set | `None` / `None` | `.../uncirculated-coin-set-2026/26rj_e.jpg`<br>*(200 OK, 336,365 B)* | `.../uncirculated-coin-set-2026/26rj_b.jpg`<br>*(200 OK, 265,821 B)* | `26rj_e.jpg` | Zero placeholders; full blister lens rendered |
| **6** | `0e68ecba...` (`eric.seaman`) | 2026 Innovation | 2026 Innovation Rev Proof Set | `None` / `None` | `.../2026_series/2026_american_innovation_obverse.jpg`<br>*(200 OK, 1,279,411 B)* | `.../2026_products/26gc_b.webp`<br>*(200 OK, 137,372 B)* | `26gc_b.webp` | Unique innovation reverse lens on card; Raw grade; 0 sleeve box |
| **7** | `933df91f...` (`eric.seaman`) | 2026 Trump $1 | 2026 Trump $1 Coin Roll | `None` / `None` | `.../2026_products/26sqrp_b.webp`<br>*(200 OK, 179,722 B)* | `.../2026_products/MASTER_SEMIQDJT_image_2.jpg`<br>*(200 OK, 245,212 B)* | `26sqrp_b.webp` | Donald J. Trump portrait obverse & Liberty reverse (0 reverse-as-obverse) |
| **8** | `nAnGLwGv...` (`eric.seaman`) | 2026 Dime | 2026-P Semiquincentennial Dime | `...2025-roosevelt-dime-...-philadelphia.jpg` | `.../bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg`<br>*(200 OK, 1,224,376 B)* | `.../bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg`<br>*(200 OK, 1,336,791 B)* | `SemiQ-Dime-Obverse-Unc-P.jpg` | Semiquincentennial Liberty 'P' obverse; torch rev |
| **9** | `rv9SCUTa...` (`eric.seaman`) | 2026 Dime | 2026-D Semiquincentennial Dime | `...2025-roosevelt-dime-...-denver.jpg` | `.../bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg`<br>*(200 OK, 1,224,042 B)* | `.../bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg`<br>*(200 OK, 1,336,791 B)* | `SemiQ-Dime-Obverse-Unc-D.jpg` | Semiquincentennial Liberty 'D' obverse; torch rev |
| **10** | `3f7cd90b...` (`eric.seaman`) | 2026 Quarter | 2026 Semiquincentennial Quarter | `None` / `None` | `.../2026_series/2026_quarter_dollar_declaration_of_independence_obverse.jpg`<br>*(200 OK, 1,472,858 B)* | `.../2026_series/2026_quarter_dollar_declaration_of_independence_reverse.jpg`<br>*(200 OK, 1,385,451 B)* | `..._declaration_of_independence_reverse.jpg` | Declaration of Independence quarter; 0 placeholders |
| **11** | `b015e197...` (`eric.seaman`) | 2026 Half $ | 2026 Semiquincentennial Half $ | `None` / `None` | `.../bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg`<br>*(200 OK, 1,510,128 B)* | `.../bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg`<br>*(200 OK, 1,510,409 B)* | `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` | Enduring Liberty obverse; dual-dated 1776-2026 rev |
| **12** | `5b424047...` (`eric.seaman`) | 2005 50-State Q | Kansas (Denver) | `...quarter_obverse...` / `...2003-...arkansas...` | `.../50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg`<br>*(200 OK, 572,791 B)* | `.../bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg`<br>*(200 OK, 546,742 B)* | `2005-...-kansas-...reverse.jpg` | Buffalo & sunflower Kansas 2005; Arkansas removed |
| **13** | `3346cda5...` (`eric.seaman`) | 2019 ATB Q | American Memorial Park | `...2019...obv-denver` / `...2015-...blue-ridge...` | `.../atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg`<br>*(200 OK, 2,134,218 B)* | `.../atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg`<br>*(200 OK, 2,064,160 B)* | `2019-...-american-memorial-park...reverse.jpg` | Chamorro woman at Memorial Park; Blue Ridge removed |
| **14** | `b243621c...` (`eric.seaman`) | 2020 ATB Q | Salt River Bay | `...2020...obv-denver` / `...2017-...ozark...` | `.../atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg`<br>*(200 OK, 1,338,124 B)* | `.../atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg`<br>*(200 OK, 1,298,877 B)* | `2020-...-salt-river-bay...reverse.jpg` | Red mangrove tree Salt River Bay; Ozark removed |
| **15** | `c336e53e...` (`eric.seaman`) | 2013 ATB Q | Mount Rushmore | `...2013...obv` / `...2010-...mount-hood...` | `.../atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg`<br>*(200 OK, 1,864,933 B)* | `.../atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg`<br>*(200 OK, 2,032,412 B)* | `2013-...-mount-rushmore...reverse.jpg` | Lincoln carving Mt Rushmore 2013; Mt Hood removed |
| **16** | `cba5e585...` (`eric.seaman`) | 2018 ATB Q | Cumberland Island | `...2018...obv` / `...2016-...cumberland-gap...` | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg`<br>*(200 OK, 2,309,627 B)* | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg`<br>*(200 OK, 2,157,454 B)* | `2018-...-cumberland-island...reverse.jpg` | Snowy egret Cumberland Island 2018; Gap removed |
| **17** | `d7fec246...` (`eric.seaman`) | 2018 ATB Q | Block Island | `...2018...obv` / `...2017-...ellis-island...` | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg`<br>*(200 OK, 2,309,627 B)* | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg`<br>*(200 OK, 2,242,129 B)* | `2018-...-block-island...reverse.jpg` | Black-crowned night-heron 2018; Ellis Island removed |
| **18** | `Wq2UhSQN...` (`eric.seaman`) | 1962 Cent | Abraham Lincoln | `...1909-1C...` / `...2008-lincoln...` | `.../Obverses_of_United_States_cents/1962_D_Lincoln_Penny__28U.S._Coin.jpg`<br>*(200 OK, 782,727 B)* | `.../Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg`<br>*(200 OK, 608,070 B)* | `1962_D_Lincoln_Penny...jpg` | Authentic 1962-D Lincoln obverse; Memorial rev |
| **19** | `UOBfFO2m...` (`eric.seaman`) | 2019 Quarter | Washington (Phila) | `...1932-washington-quarter...` / `...rev...` | `.../50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg`<br>*(200 OK, 1,410,838 B)* | `.../50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg`<br>*(200 OK, 1,410,838 B)* | `...Philadelphia_29.jpg` | Authentic modern Washington obverse; 1932 removed |
| **20** | `2233c46e...` (`eric.seaman`) | 2017 ATB Q | Effigy Mounds (Denver) | `None` (Blank Obverse) / `...effigy...` | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`<br>*(200 OK, 166,278 B)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg`<br>*(200 OK, 2,062,235 B)* | `2017-...-effigy-mounds...reverse.jpg` | Washington ATB obverse mapped; Effigy rev |
| **21** | `532e8b1d...` (`eric.seaman`) | 2017 ATB Q | Frederick Douglass (D) | `None` (Blank Obverse) / `...douglass...` | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`<br>*(200 OK, 166,278 B)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg`<br>*(200 OK, 2,127,779 B)* | `2017-...-frederick-douglass...reverse.jpg` | Washington ATB obverse mapped; Douglass rev |
| **22** | `7a1d13f9...` (`eric.seaman`) | 2017 ATB Q | George Rogers Clark (D) | `None` (Blank Obverse) / `...clark...` | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`<br>*(200 OK, 166,278 B)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg`<br>*(200 OK, 2,118,832 B)* | `2017-...-george-rogers-clark...reverse.jpg` | Washington ATB obverse mapped; Clark rev |
| **23** | `3ccb26e0...` (`eric.seaman`) | 2017 ATB Q | Ozark Riverways (D) | `None` (Blank Obverse) / `...ozark...` | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`<br>*(200 OK, 166,278 B)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg`<br>*(200 OK, 2,172,068 B)* | `2017-...-ozark-riverways...reverse.jpg` | Washington ATB obverse mapped; Ozark rev |
| **24** | `d4e5f6a7...` (`eric.seaman`) | 2010 ATB Q | Yellowstone (Denver) | `None` (Blank Obverse) / `...yellowstone...` | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`<br>*(200 OK, 166,278 B)* | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg`<br>*(200 OK, 592,295 B)* | `2010-...-yellowstone...reverse.jpg` | Washington ATB obverse mapped; Yellowstone rev |
| **25** | `a1b2c3d4...` (`eric@numista`) | 2026 Silver Eagle | 2026-W Silver Eagle Proof | `None` (Blank Obverse) / `None` | `.../2026_products/26ea_a.webp`<br>*(200 OK, 168,246 B)* | `.../bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse.png`<br>*(200 OK, 612,740 B)* | `26ea_a.webp` | Full 2026-W Silver Eagle obverse & reverse |
| **26** | `b2c3d4e5...` (`eric@numista`) | 2026 Mint Set | 2026 250th Uncirculated Set | `None` (Blank Obverse) / `None` | `.../uncirculated-coin-set-2026/26rj_e.jpg`<br>*(200 OK, 336,365 B)* | `.../uncirculated-coin-set-2026/26rj_b.jpg`<br>*(200 OK, 265,821 B)* | `26rj_e.jpg` | Full 10-coin blister lens obverse & reverse |
| **27** | `c3d4e5f6...` (`eric@numista`) | 2026 Innovation | 2026 Innovation Rev Proof Set | `None` (Blank Obverse) / `None` | `.../2026_series/2026_american_innovation_obverse.jpg`<br>*(200 OK, 1,279,411 B)* | `.../2026_products/26gc_b.webp`<br>*(200 OK, 137,372 B)* | `26gc_b.webp` | Statue of Liberty obverse; 4-coin lens rev |
| **28** | `d4e5f6g7...` (`eric.seaman`) | 2023 Silver Set | 2023 Silver Proof Set | `None` / `None` | `.../2026_products/26RH_image_1.jpg`<br>*(200 OK, 110,063 B)* | `.../2026_products/26RH_image_2.jpg`<br>*(200 OK, 104,034 B)* | `26RH_image_1.jpg` | Clean 10-coin lens placeholder; native `23rh_b.webp` (226,854 B) staged for EXECUTE |

---

### 4.1 Measured Content-Length Bytes for All GCS URLs in Sections 2, 3, and 4 (Must-Fix 2)

Raw single-session Python HTTP HEAD log executed 2026-10-31 23:03 EDT against `gs://numista-reference-library`:

```text
=== 2026_products ===
200 OK (  168246 B): reference_library/us_mint_official/2026_products/26ea_a.webp
200 OK (  126209 B): reference_library/us_mint_official/2026_products/26EA_image_1.jpg
200 OK (  139910 B): reference_library/us_mint_official/2026_products/26EA_image_2.jpg
200 OK (  142916 B): reference_library/us_mint_official/2026_products/26EA_image_3.jpg
200 OK (  216358 B): reference_library/us_mint_official/2026_products/26xe_a.webp
200 OK (  195231 B): reference_library/us_mint_official/2026_products/26XE_image_1.jpg
200 OK (  240850 B): reference_library/us_mint_official/2026_products/26XE_image_2.jpg
200 OK (  285827 B): reference_library/us_mint_official/2026_products/26XE_image_3.jpg
200 OK (  239954 B): reference_library/us_mint_official/2026_products/26xl___a.webp
200 OK (  319138 B): reference_library/us_mint_official/2026_products/26XL_image_1.jpg
200 OK (  379918 B): reference_library/us_mint_official/2026_products/26XL_image_2.jpg
200 OK (  204667 B): reference_library/us_mint_official/2026_products/26XL_image_3.jpg
200 OK (  244540 B): reference_library/us_mint_official/2026_products/26rj_a.webp
200 OK (  299132 B): reference_library/us_mint_official/2026_products/26RJ_image_1.jpg
200 OK (  300506 B): reference_library/us_mint_official/2026_products/26RJ_image_2.jpg
200 OK (  137372 B): reference_library/us_mint_official/2026_products/26gc_b.webp
200 OK (  135436 B): reference_library/us_mint_official/2026_products/26GC_image_1.jpg
200 OK (  138756 B): reference_library/us_mint_official/2026_products/26GC_image_2.jpg
200 OK (  156373 B): reference_library/us_mint_official/2026_products/26GC_image_3.jpg
200 OK (  140054 B): reference_library/us_mint_official/2026_products/26XH_image_1.jpg
200 OK (  169132 B): reference_library/us_mint_official/2026_products/26XH_image_3.jpg
200 OK (  274992 B): reference_library/us_mint_official/2026_products/26XF_image_1.jpg
200 OK (  178232 B): reference_library/us_mint_official/2026_products/26rg_b.webp
200 OK (  115064 B): reference_library/us_mint_official/2026_products/26RG_image_1.jpg
200 OK (  104072 B): reference_library/us_mint_official/2026_products/26RG_image_2.jpg
200 OK (  110063 B): reference_library/us_mint_official/2026_products/26RH_image_1.jpg
200 OK (  104034 B): reference_library/us_mint_official/2026_products/26RH_image_2.jpg
200 OK (  179722 B): reference_library/us_mint_official/2026_products/26sqrp_b.webp
404 ERR (       N/A B): reference_library/us_mint_official/2026_products/26SQRP_image_1.jpg  <-- DROPPED IN R2.8.4
200 OK (  217879 B): reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg
200 OK (  245212 B): reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg

=== user_contributed ===
200 OK (  336365 B): reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg
200 OK (  265821 B): reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg
404 ERR (       N/A B): reference_library/user_contributed/coin_sets/american-eagle-2026-one-ounce-silver-proof-coin/American Eagle 2023 One Ounce Silver Proof Coin_Obverse.jpg <-- DROPPED IN R2.8.4

=== real landing eagle reverses in bulk_programs ===
200 OK (  612740 B): reference_library/bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse.png
200 OK (  612740 B): reference_library/bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse_attr_US_Mint.png

=== 2026_series ===
200 OK ( 1279411 B): reference_library/2026_series/2026_american_innovation_obverse.jpg
200 OK ( 1472858 B): reference_library/2026_series/2026_quarter_dollar_declaration_of_independence_obverse.jpg
200 OK ( 1385451 B): reference_library/2026_series/2026_quarter_dollar_declaration_of_independence_reverse.jpg

=== bulk_programs (dimes, half dollars, 50-state quarters) ===
200 OK ( 1224376 B): reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg
200 OK ( 1224042 B): reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg
200 OK ( 1336791 B): reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg
200 OK ( 1510128 B): reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg
200 OK ( 1510409 B): reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg
200 OK (  546742 B): reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg

=== atb_quarters ===
200 OK (  166278 B): reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp
200 OK (  592295 B): reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg
200 OK (  712711 B): reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg
200 OK (  724057 B): reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg
200 OK ( 1864933 B): reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg
200 OK ( 2032412 B): reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg
200 OK ( 2062235 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg
200 OK ( 2127779 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg
200 OK ( 2118832 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg
200 OK ( 2172068 B): reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg
200 OK ( 2309627 B): reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg
200 OK ( 2157454 B): reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg
200 OK ( 2242129 B): reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg
200 OK ( 2134218 B): reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg
200 OK ( 2064160 B): reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg
200 OK ( 2116020 B): reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg
200 OK ( 1338124 B): reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg
200 OK ( 1298877 B): reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg

=== wikimedia_uscoin ===
200 OK (  572791 B): reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg
200 OK ( 1410838 B): reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg
200 OK (  782727 B): reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/1962_D_Lincoln_Penny__28U.S._Coin.jpg
200 OK (  608070 B): reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg

=== 2023_series composites ===
200 OK (  711501 B): reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg
200 OK (  584055 B): reference_library/2023_series/2023_american_innovation_four_states_composite.jpg
```

---

### 4.2 How Existing Pre-Fix Docs Display vs Post-Fix on p7-gate

- **Pre-Fix Display on `p7-gate`:**
  - **Null URL items:** Documents with null `image_url_obverse` / `image_url_reverse` (`91f88212`, `0e68ecba`, `933df91f`, `3f7cd90b`, `b015e197`, and the 4 items in `eric@numista.ai`) display a generic gold `$` placeholder icon.
  - **Wrong Non-Null Reference URLs:** Documents pointing to obsolete or mismatched mint files render incorrect imagery:
    - `e91efa62` (`26EA`) displays 2023 Walking Liberty and dead reverse.
    - `a59853c1` (`26XL`) displays 2023 date on the coin face.
    - `71e2d4ae` (`26RJ`) displays the outer cardboard packaging folder instead of coins.
    - `nAnGLwGv` and `rv9SCUTa` display 2025 Roosevelt dimes.
    - `5b424047` (Kansas) displays 2003 Arkansas reverse; ATB items display wrong park reverses; 1962 Cent displays 1909 Wheat obverse.
- **Post-Fix Display on `p7-gate` (Immediate Zero-Mutation):**
  - `Canonical2026MintAssets.resolveFromMap(data)` intercepts 2026 items at render time. Regardless of whether Firestore has null URLs or stale non-null reference URLs, the client immediately serves official high-resolution 2026 coin imagery (`26ea_a.webp`, `26xe_a.webp`, `26xl___a.webp`, `26rj_e.jpg`, `26gc_b.webp`, `26sqrp_b.webp`, `SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`). User uploads (`/users/` or `/microscope/`) remain untouched.
  - Basename Year Guard and whole-token matcher suppress wrong-year/wrong-park images on non-2026 items, falling back to canonical series obverse/reverse.
  - Result: 100% correct visual rendering on `p7-gate` without waiting for database mutations.

---

## 5. Catalog Image Matching Fallbacks (127 Missing Images & 60 Presidential Dollars)

Addressing **Must-Fix 4**, here are the verbatim code citations and surgical fixes for the `127` `"Missing images"` rows and 60 Presidential Dollars.

### 5.1 Verbatim Code Citations (Rule 6a Compliance)

```dart
// File: numista_mobile/lib/screens/my_collection_screen.dart:6394-6401
        final resolvedUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
            ? ref!.obverseUrl!
            : (ref?.url?.isNotEmpty == true && subject.isEmpty)
            ? ref!.url!
            : '';
```

```dart
// File: numista_mobile/lib/services/coin_image_service.dart:541-563
        for (final doc in snap.docs) {
          if (needsObv && (!hasSubject || isSubjectBase)) {
            final u = _pickSideFromDoc(
              doc.data(),
              'obverse',
              mintMark: mintMark,
            );
            if (u != null) {
              obverseUrl = u;
              matchedDocData ??= doc.data();
            }
          }
          if (needsRev && (!hasSubject || isSubjectBase)) {
            final u = _pickSideFromDoc(
              doc.data(),
              'reverse',
              mintMark: mintMark,
            );
            if (u != null) {
              reverseUrl = u;
              matchedDocData ??= doc.data();
            }
          }
        }
```

### 5.2 Root Cause Analysis
1. In Firestore `coin_image_index`, `presidential-dollars` has `39` obverse docs (one per President) and `1` generic Statue of Liberty reverse doc (`2007_presidential-dollars_reverse`).
2. Because `hasSubject` is `true` (e.g. `"George Washington"`), `coin_image_service.dart:558` (`if (needsRev && (!hasSubject || isSubjectBase))`) skips the generic reverse doc, leaving `ref.reverseUrl == null`.
3. Then `my_collection_screen.dart:6396` (`: (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)`) discards `ref.obverseUrl` because `subject` is non-empty—rendering the gold `$` placeholder on **all 60 Presidential Dollars**!
4. Conversely, `50-state-quarters` has `56` state reverse docs and `0` state-specific obverse docs in `coin_image_index`, so `coin_image_service.dart:542` blocks the generic Washington obverse on **all 46 50-State Quarters**.

### 5.3 Surgical Code Fix (Lock Note L1)

1. **In `coin_image_service.dart:535-570`:** Allow the generic series `coin_image_index` fallback to populate the **common (non-unique) side** when the subject-specific query only returned the unique side:
   - Common-reverse series (`presidential-dollars`, `native-american-dollars`, `innovation-dollars`): allow generic reverse fallback:
     ```dart
     final isCommonReverse = _isCommonReverseSeries(seriesSlug);
     if (needsRev && (!hasSubject || isSubjectBase || isCommonReverse)) { ... }
     ```
   - Common-obverse series (`50-state-quarters`, `america-the-beautiful-quarters`, `american-women-quarters`): allow generic obverse fallback:
     ```dart
     final isCommonObverse = _isCommonObverseSeries(seriesSlug);
     if (needsObv && (!hasSubject || isSubjectBase || isCommonObverse)) { ... }
     ```
2. **In `my_collection_screen.dart:6356-6402`:** When `ref?.obverseUrl` is matched for that coin (or for obverse-unique series like Presidential Dollars where the portrait is on the obverse), prefer `obverseUrl` on obverse-unique series and fall back to `obverseUrl` when `reverseUrl` is null:
   ```dart
   final preferObv = _isObverseUniqueSeries(series, denomination);
   final resolvedUrl = preferObv
       ? ((ref?.obverseUrl?.isNotEmpty == true)
           ? ref!.obverseUrl!
           : (ref?.reverseUrl ?? ''))
       : ((ref?.reverseUrl?.isNotEmpty == true)
           ? ref!.reverseUrl!
           : (ref?.obverseUrl?.isNotEmpty == true)
               ? ref!.obverseUrl!
               : '');
   ```

---

## 6. Deterministic Line-Total & Unit Cost Guard (S1) with Unit Tests

Addressing **Must-Fix 5**, here is the verbatim code citation and deterministic integer-cents calculation for `review_hub_screen.dart:2040-2059`.

### 6.1 Verbatim Code Citation (Rule 6a Compliance)

```dart
// File: numista_mobile/lib/screens/review_hub_screen.dart:2040-2059
                        final costRaw =
                            item['unit_cost'] ??
                            item['purchase_cost'] ??
                            item['cost'] ??
                            item['Cost'] ??
                            item['estimated_value'] ??
                            item['value'];
                        double? costVal;
                        if (costRaw is num) {
                           costVal = costRaw.toDouble();
                        } else if (costRaw != null) {
                          costVal = double.tryParse(
                            costRaw.toString().replaceAll(
                              RegExp(r'[^0-9.]'),
                              '',
                            ),
                          );
                        }
```

### 6.2 Deterministic S1 Guard Rule (Lock Note L1)

Across all `260` docs in Eric's accounts (`eric.seaman@yahoo.com` + `eric@numista.ai`), only **3 unique doc IDs** have `qty > 1`:
- `0e68ecba-f264-480b-ae82-dd9783135fa8` (`26GC`, `qty=2`, `Cost=64.97` $\rightarrow$ line total, unit cost `$32.49` via integer `ROUND_HALF_UP`: `(6497 + 1) ~/ 2 = 3249` cents).
- `be10e44c-6eb5-4510-bb80-0d106d38b9d5` (`26XE`, `qty=2`, `Cost=169.0` $\rightarrow$ line total, unit cost `$84.50`: `(16900 + 1) ~/ 2 = 8450` cents).
- `7a32932e-a125-4918-9214-fb49da0f50a6` (`26SQRP` Coin Roll, `qty=25`, `Cost=61.0` $\rightarrow$ roll price `$61.00`, per-coin `$2.44` via `6100 ~/ 25 = 244` cents).

**Algorithm:**
1. If `item['unit_cost_cents']` (int) is present and `> 0`, use `unit_cost_cents / 100.0`.
2. Else if `item['unit_cost']` is present and `> 0`, use `unit_cost`.
3. Else let `totalCents = (rawCost * 100).round()`. If `cleanQty > 1`:
   - Check known US Mint unit MSRP table (`_mintUnitMsrpCents[sku]`, e.g. `26GC`: `3249`, `26XE`: `8450`/`9100`, `26RJ`: `3975`/`13445`, `26SQRP` roll: `6100`).
   - If `totalCents` already equals `_mintUnitMsrpCents[sku]` (within $\pm 5\%$), do **NOT** divide (it is already per-unit!).
   - Otherwise divide in integer cents using `ROUND_HALF_UP`: `unitCents = (totalCents + (cleanQty ~/ 2)) ~/ cleanQty`.

### 6.3 Unit Test Specifications
- **Test 1 (`26GC` Line Total):** `qty=2, Cost=64.97` $\rightarrow$ resolves to `3249` cents = `$32.49`.
- **Test 2 (`26RJ` Line Total):** `qty=2, Cost=268.90` $\rightarrow$ resolves to `13445` cents = `$134.45`.
- **Test 3 (`26RJ` Already Unit):** `qty=2, Cost=134.45` $\rightarrow$ matches unit MSRP `$134.45` $\rightarrow$ remains `13445` cents = `$134.45`.
- **Test 4 (`26SQRP` Roll):** `qty=25, Cost=61.00` $\rightarrow$ roll cost `$61.00`, per-coin cost `$2.44 each`.

---

## 7. Should-Fix Resolutions (S-A, S-B, S-C, S-D, S-E, S2, S3)

- **S-A (Row 28 2023 Silver Proof Set `23RH`):** In `gs://numista-reference-library`, there is currently no `23rh_b.webp` set lens object; however, Eric's 7C folder contains the exact 2023 Silver Proof Set Lens `1 NUMISTA.AI\Coin Images\23RH\2023_silver_proof_set_set_obverse_23RH.webp` (identical to `Images from US MInt\Silver Proof Set 2023\23rh_b.webp`, verified exact **226,854 B**, MD5 `8a2060d0ca5987b0faf0d8828ece365f`, SHA256 `f7326813ab70f0feb09f261debd31f8d562eb0568a347b0024ece9bda78c04ba`). Row 28 stages `23rh_b.webp` for `--no-clobber` upload at EXECUTE rather than substituting series composites.
- **S-B (Independent Argon Review Citations):** Accurately cited Argon's filed independent evaluations: `Argon Review NET-692A (90/100 REVISE on R2.8.3)` and `Argon Review NET-694A (93/100 REVISE on R2.8.4)`.
- **S-C (ATB Obverse Year Matching):** Uses year-matched Denver/Phila obverses where available (2011, 2013, 2018, 2019, 2020), retaining whitelisted 2010 undated obverse only for 2017 rows where no 2017 obverse asset exists.
- **S-D (MAD Calculation Audit Trail):** The pixel-level MAD calculations were generated by running `scratch/check_all_2026_visual.py` on 2026-10-31 22:40 EDT against Eric's 7C reference files indexed in `1 NUMISTA.AI\Coin Images\_INDEX\image_index.csv`. Field Tester can rerun this script at any time to verify identical floating-point differences.
- **S-E (Basename Year Guard Confirmation):** The client-side basename year guard verifies that image filenames do not contain a conflicting 4-digit year string (e.g. rejecting a 2023-dated filename for a 2026 coin). Because the native asset `26ea_b.webp` contains no year string in its basename, the year guard will never reject it. Moreover, all `Canonical2026MintAssets` overrides take precedence over fuzzy catalog heuristics.
- **S2 (Generic Unique-Side Card Rule):** Formalizes Eric's 15 Oct directive: the card view always renders the side unique to that coin program across the entire catalog (Obverse for Commemoratives/Morgan/Peace/Trump; Reverse for 50-State/ATB/Innovation; Primary Lens for sets).
- **S3 (Field Tester Expectations for `26GC`):** Card thumbnail renders `26gc_b.webp` (137,372 B, reverse innovation lens). Modal Obverse tab renders `2026_american_innovation_obverse.jpg` (1,279,411 B, Statue of Liberty obverse). Modal Reverse tab renders `26gc_b.webp`. Grade badge normalized to `Raw`.

---

## 8. Complete 39-Item Coverage Matrix Against Eric Beta Issue Tracker

Per Directive **NET-681E**, all 39 rows from `RADIO NET\ERIC_BETA_ISSUE_TRACKER_20261031.csv` are mapped below:

| Tracker ID | Screen / Area | Eric's Reported Defect | Status in Tracker | Plan Line in R2.8.5 / Disposition | Verification Method / Defer Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E8** | Whole Account | "Get my account 100% right" | In Plan (R2.8.5) | Sections 4 & 5: Full read-only audit across all 252 items in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai`; client render fallbacks for zero-mutation instant display fix; backfill script staged for separate YES. | Acceptance Gate: Field Tester PASS on Eric's account with 0 wrong items. |
| **E1** | Collection Cards | "Peace and Morgan share the same eagle photo" | In Plan (R2.8.5) | Section 3: Prioritize unique obverse side at `my_collection_screen.dart:6358-6360`. | FT visual verification on Eric account Cards view. |
| **E2 / B27-5** | Cards & Review | "None of the 3 had images... placeholders" | Fixed but FT FAIL | Section 2 & 3: Canonical catalog map fallback overrides stale/null URLs. | FT inspection on p7-gate: real photos load. |
| **E3** | Collection Card | "Unc Set card shows packaging" | In Plan (R2.8.5) | Section 2 & 3: Remap SKU `26RJ` to official Set Lens (`26rj_e.jpg`). | FT visual verification on Eric account. |
| **E4a / B27-5** | Collection Cards | "Cards show Valuation Pending" | Fixed but FT FAIL | Section 6: Title-Case `'Purchase Cost'` and `_F.cost` fallback at `my_collection_screen.dart:3016-3022`. | FT inspection on Eric account: valuation/cost displayed. |
| **E4b / B27-6** | Collection Cards | "American Innovation had Unspecified for grade" | In Plan (R2.8.5) | Section 7: Call existing `_conditionLabel` at line 3000 $\rightarrow$ `"Raw"`. | FT inspection on Eric account: grade badge says Raw. |
| **E5** | Collection Cards | "Titles are truncated" | In Plan (R2.8.5) | Section 7: Change `maxLines: 1` to `maxLines: 2` with aspect ratio 0.72. | FT inspection on Eric account: full titles visible. |
| **E6** | Coin Inspector | "2026 dimes show a 2025 Roosevelt image in Inspector" | In Plan (R2.8.5) | Section 4: Canonical override to Semiquincentennial Liberty Dime assets (`SemiQ-Dime-Obverse-Unc-P.jpg`, etc.). | FT inspection on Eric account: 2026 Liberty Dime displayed. |
| **E7** | Coin Inspector | "2026-W Silver Eagle Rev tab shows 2023 Walking Liberty" | In Plan (R2.8.5) | Section 3: Unconditional canonical override to `26ea_a.webp` (Obverse) and Landing Eagle reverse (`Type_2_Reverse.png` live primary, `26ea_b.webp` staged). | FT inspection on Eric account: 2026 Eagle, correct sides. |
| **B29-6 / FT-1** | Review Card Price | "2-coin sets show $169.00 and $64.97 each" | Fixed but FT FAIL | Section 6: Verbatim `2040-2059` fix; `ROUND_HALF_UP` integer cents. | FT inspection: cards show $84.50 and $32.49. |
| **FT-2 / Q3** | Review Queue | "Only 9 of 11 cards show" | In Plan (R2.8.5) | Section 3: Stage complete 11-SKU catalog intake fixture for FT retest. | FT inspection: 11 review cards render. |
| **B26-1** | Review Hub fee | "Missed the $9.95 shipping and handling... unable to add fee" | Fixed on p7-gate, FT PASS | Re-check in Eric's account: verify truck icon fee displays $9.95 and is editable/savable. | FT re-verification on Eric account. |
| **B26-2** | Review Hub card date | "Main screen had no date, but when I clicked Edit date was there" | Unverified | Section 8 Plan Line: Ensure review card subtitle displays formatted invoice/order date from metadata if present. | FT verification on p7-gate. |
| **B26-3** | Edit Coin > Save | "Unable to save" | Unverified | Section 8 Plan Line: Verify Edit Coin save action persists changes to Firestore/state cleanly with error toast guard. | FT verification on p7-gate. |
| **B26-4** | Morgan AI Chat | "Morgan would only accept image files (not the PDF invoice)" | Not in any plan | **EXPLICIT DEFER TO UX BACKLOG**: Morgan AI chat attachment endpoint enforces `image/*` MIME filtering. Ingesting multi-page PDF invoices into the chat stream requires a server-side PDF rasterization/OCR pipeline, which is a major feature extension out of scope for the emergency Mint fix on branch `p7-v8.9`. | Deferred to Post-Mint Roadmap. |
| **B26-5** | Add Coins screen | "Two ways to add by Cert, 2 ways by photo... Very confusing!" | Unverified | **EXPLICIT DEFER (UX Redesign)**: Retain streamlined Add Coins layout verified in NET-647 #1-3. Full IA/UX overhaul of Add Coins screen deferred to post-Mint beta release to prevent scope creep. | FT founder walk-through check. |
| **B26-6** | Invoice upload flow | "1 or 2 more clicks than it needed to be" | Unverified | Section 8 Plan Line: Verify invoice upload flow reaches review queue in minimum clicks (tested green in NET-647). | FT click-count verification on p7-gate. |
| **B26-7** | Review Queue | "Wish I could enter storage location right from this screen" | Unverified | Section 8 Plan Line: Verify inline storage location field on review card (added in NET-585 / NET-647 #9) works and persists. | FT verification on p7-gate. |
| **B26-8** | Bulk Import / Review | "Had to scroll down (again) to get to next step" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #3-5 (auto-scroll to active item / sticky action bar). | FT regression check. |
| **B27-1** | Trump $1 roll row | "July 4th Privy eligible... I don't know if we need that" | Unverified | Section 8 Plan Line: Suppress extraneous "July 4th Privy eligible" badge from review card unless explicitly part of product SKU title. | FT verification on p7-gate. |
| **B27-2** | Edit in Review Hub | "Added it via Edit, which automatically saved it to collection" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 I-04c (explicit Commit button required). | FT regression check. |
| **B27-3** | Review Hub | "Hitting Select All appeared to initiate a Delete" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 I-05 (clear checkbox icon vs trash icon separation). | FT regression check. |
| **B27-4** | Review Hub button | "Commit Selected... hard to read... does it delete or add?" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 I-06 (high-contrast label "Commit Selected to Collection"). | FT regression check. |
| **B27-7** | My Collection | "No rhyme or reason to how coins were sorted" | Unverified | Section 8 Plan Line: Enforce deterministic default collection sort order: Acquisition Date DESC, Year DESC, Name ASC. | FT verification on Eric account. |
| **B27-8** | Coin Inspector | "I thought we did away with Google Images button?" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 P1 (button removed). | FT regression check. |
| **B27-9** | My Collection CTA | "Generate AI Report Now opened state picker for estate tax" | Unverified | Section 8 Plan Line: Ensure My Collection CTA opens Collection Value / Inventory Report, NOT Estate Tax state picker. | FT verification on Eric account. |
| **B27-10** | My Collection CTA | "Replace Generate AI Report Now with something to fill images/values" | Unverified | Section 8 Plan Line: Add/re-point CTA button to "Refresh Images & Valuations" (triggers catalog enrichment). | FT verification on Eric account. |
| **B27-11** | Table view / Cards | "Impossible to read due to text/background colors... prefer gold/black" | Fixed on p7-gate, FT PASS | Verified PASS in NET-631 / NET-647 (cream contrast & theme styling). | FT regression check on Eric account. |
| **B27-12** | Card view detail | "Financials, Provenance, AI Insights... should also be in Card view" | Unverified | Section 8 Plan Line: Verify bottom sheet modal / expandable card drawer on Card tap exposes Financials, Provenance, and AI Insights tabs. | FT verification on Eric account. |
| **B27-13** | Table AI Insights | "AI Insights had large gaps and/or unreadable text" | Unverified | Section 8 Plan Line: Verify AI Insights markdown rendering has tight paragraph spacing and readable contrast. | FT verification on Eric account. |
| **B27-14** | Table view | "Legislation Matched was blank" | Unverified | Section 8 Plan Line: Ensure legislation metadata (e.g. Public Law 116-330 Semiquincentennial Act) populates for 2026 items. | FT verification on Eric account. |
| **B27PM-1** | Review Hub | "No duplicates flagged" | Fixed on p7-gate, FT PASS | Re-confirm in Eric's account: amber duplicate banner fires when matching certificate/title exists. | FT verification on p7-gate. |
| **B27PM-2** | Cards + Detail | "Can't tell if I have two 2026 Uncirculated Coin Sets" | Unverified | Section 8 Plan Line: Disambiguate multi-set holdings with distinct item numbers / mint badges (e.g. P-Mint Lens vs D-Mint Lens or Set 1 / Set 2). | FT verification on Eric account. |
| **B27PM-3** | Search results | "Set I just uploaded did not have 250th Anniversary under Theme" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 SAG2 (theme stamped from Mint catalog). | FT regression check. |
| **B27PM-4** | Card detail pop-up | "Could not make pop-up bigger... Lincoln quarter cut off" | Fixed on p7-gate, FT PASS | Verified PASS in NET-631 (20-coin wrap grid in detail dialog). | FT regression check. |
| **B29-1** | Add Coins | "Upload an Invoice does nothing when clicked" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #1 & NET-673 #6. | FT regression check. |
| **B29-2** | Add Coins / Drop | "Only bottom inch of page scrolled / drop zone ~5% of screen" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #2, #3 (expanded drop zone & scroll). | FT regression check. |
| **B29-3** | Bulk Import | "Search by Store/Dealer Name... remove it" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #7 (input removed). | FT regression check. |
| **B29-4** | Review card | "Having 2 links/buttons to paper trail is pointless clutter" | Unverified | Section 8 Plan Line: Verify review card displays single consolidated Paper Trail / Receipt action. | FT verification on p7-gate. |
| **B29-5** | Review card | "These both do same thing, delete top one that says Storage" | Fixed on p7-gate, FT PASS | Verified PASS in NET-673 #4 (duplicate button removed). | FT regression check. |

---

## 9. Execution Gates & Verification Sequence

As mandated by standing orders and 3 AM stand-down constraints, execution proceeds strictly through sequential gates:

1. **Gate 1: Multi-Agent Plan Scoring:**
   - Argon review `NET-692A` scored 90 `REVISE`; `NET-694A` scored 93 `REVISE`.
   - Grok CoS evaluation meeting the $\ge 95$ threshold (`COS_SCORE >= 95`).
2. **Gate 2: SAG Final Endorsement:**
   - Senior Advisory Group reviews the $\ge 95$ plan and confirms zero risk to production branches and live databases.
3. **Gate 3: Founder Explicit Typed YES:**
   - Eric types explicit `YES` in the morning after 3 AM stand-down.
4. **Gate 4: Surgical Implementation & Rule 8 Verification:**
   - Execute edits on branch `p7-v8.9` ONLY adhering to Lock Notes L1, L2, L3:
     - `lib/core/services/canonical_2026_mint_assets.dart`
     - `numista_mobile/lib/screens/my_collection_screen.dart:6356-6402`
     - `numista_mobile/lib/services/coin_image_service.dart:535-570`
     - `numista_mobile/lib/screens/review_hub_screen.dart:2040-2059`
     - `numista_backend/services/us_mint_catalog_service.py:235-248`
     - Upload staged intake blobs (`23rh_b.webp`, `26ea_b.webp`, `26xe_b.webp`) to GCS via `--no-clobber`.
   - **Mandatory Pre-Deploy Check:** Before executing `firebase hosting:channel:deploy p7-gate`, run an automated HTTP HEAD check on `26ea_b.webp` (164,146 B, MD5 `62ad11e997ac0320b57091e3d108d3e0`), `23rh_b.webp` (226,854 B, MD5 `8a2060d0ca5987b0faf0d8828ece365f`), and `26xe_b.webp` (245,878 B, MD5 `3a77694c9a72e6db63811c8b001edbb5`). **Deploy to p7-gate is hard-blocked if any staged URL returns non-200.**
   - Run `flutter analyze` $\rightarrow$ 0 errors.
   - Run `flutter test test/canonical_2026_mint_assets_test.dart` $\rightarrow$ 14/14 tests pass.
   - Run backend regression suite $\rightarrow$ 100% pass.
5. **Gate 5: Deploy to Preview Channel Only:**
   - Deploy to Firebase Hosting preview channel `p7-gate` ONLY (`https://numista-vault--p7-gate-8avtpz22.web.app`).
   - `origin/main` stays locked at `9f04550a`.
   - `origin/dev` stays frozen at `9b55f3d9`.
   - Baton passed to Field Tester for visual acceptance.
