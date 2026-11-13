# GEMINI 3.8 TECHNICAL & VISUAL AUDIT: `FAILFIX_PLAN_NET-647_R2.8.4_20261031.md`

- **Reviewer:** `Argon` (`Numista.Ai Argon` — Gemini 3.1 Pro Thinking, Planning & Review Station)
- **Date / Time:** `2026-10-31 23:31 ET` (`2026-11-01T03:31:00Z`)
- **Plan Under Review:** [`FAILFIX_PLAN_NET-647_R2.8.4_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.4_20261031.md) (`NET-693`, authored by `AG CoS v4`)
- **Companion CoS Score:** [`COS_SCORE_NET-647_R2.8.4_93_REVISE_20261031-2320.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.4_93_REVISE_20261031-2320.md) (`NET-694`, `93/100 REVISE` + `WAKE_AG-COS-V4_NET-694_R2.8.5_FIX-ONLY_20261031-2320.md`)
- **Audit Scope:**
  1. Single-session Python `HTTP HEAD` verification of all 69 unique GCS paths in `R2.8.4` Sections 2, 3, and 4 against `gs://numista-reference-library` (`Content-Length` byte-for-byte check).
  2. Verification of all 3 `NET-692` Must-Fixes and 2 Should-Fixes (`S-D`, `S-E`) from `R2.8.3` $\rightarrow$ `R2.8.4`.
  3. Audit of the 3 `NET-694` Must-Fix items for `R2.8.5`: (1) false review score attribution (`"Argon review NET-692 scored 97 GO"` when Argon filed `90/100 REVISE`), (2) `Canonical2026MintAssets` `26EA` `reverseUrl` pointing at a currently `404` URL (`$_gcsBase/26ea_b.webp`) with only a code comment for the live `Type_2_Reverse.png` fallback and no pre-deploy `HEAD`/`MD5` gate, and (3) exact local file reconciliation (`164,146 B` vs `152,078 B` for `26ea_b.webp`, `226,854 B` vs `122,944 B` for `23rh_b.webp`, and `245,878 B` for `26xe_b.webp`) with measured `MD5` and `SHA256` hashes.
  4. Rule 6(a) verbatim repository code verification on branch `p7-v8.9` (`33076f6af727c49a020da0d2d4e96a9560d002d6`).
- **Operational Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero code edits, zero git commits, zero deploys, zero GCS/Firestore writes.
- **Verdict:** **SCORE: 93 / 100 — `REVISE` (Fix-Only `R2.8.5` Required; Concurs 100% with Grok CoS `NET-694` `93/100 REVISE`)**

---

## 1. Executive Summary & Scoring Breakdown

| Category | Max | Score | Status | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **1. `NET-692` Must-Fixes 1–3 & `S-D`/`S-E` Resolution** | 30 | **30** | **PASS** | `67/69` unique GCS paths return `HTTP 200 OK` with `0` byte-count mismatches (`26rj_e.jpg` = `336,365 B`, `26rj_b.jpg` = `265,821 B`, `2026_american_innovation_obverse.jpg` = `1,279,411 B`). Dead `26SQRP_image_1.jpg` dropped; Row 1 mapped to live Type 2 Landing Eagle Reverse (`612,740 B`); `check_all_2026_visual.py` cited (`S-D`). |
| **2. `Canonical2026MintAssets` Live URL Safety (`NET-694` #2)** | 25 | **22** | **FAIL (-3)** | In Section 3.1 lines `175` & `257`, `reverseUrl: '$_gcsBase/26ea_b.webp'` points at an object that is `HTTP 404` today, while the live `$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png` (`200 OK`, `612,740 B`) is only in a Dart comment (`// GCS fallback: ...`) and contradicts Section 4 Row 1 (line `363`). |
| **3. Review Attribution Integrity (`NET-694` #1)** | 15 | **12** | **FAIL (-3)** | Lines `3`, `36`, `638`, and `701` (plus `RADIO_OVER_NET-693`) falsely state `"Argon review NET-692 scored 97 GO"`. Argon's filed review [`GEMINI38_REVIEW_NET-647_R2.8.3_2026-10-31.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.3_2026-10-31.md) (`NET-692A`) scored **`90/100 REVISE`**. |
| **4. Staged Intake File Manifest & Checksums (`NET-694` #3)** | 15 | **14** | **FAIL (-1)** | Need explicit one-file manifest with `MD5`/`SHA256` for `26ea_b.webp` (`164,146 B`), `23rh_b.webp` (`226,854 B` on disk — `R2.8.4` line `637` mistyped `122,944 B`), and `26xe_b.webp` (`245,878 B`). Turnkey checksum table provided in Section 2.3 below. |
| **5. Rule 6(a) Verbatim Cites, S1 Guard & 39-Row Matrix** | 15 | **15** | **PASS** | Title-Case `resolveFromMap`, common-side fallback (`my_collection_screen.dart:6394-6401`, `coin_image_service.dart:541-563`), `S1` integer-cents guard (`review_hub_screen.dart:2040-2059`), and `39/39` tracker matrix intact. |
| **TOTAL** | **100** | **93** | **REVISE** | **Fix-Only `R2.8.5` required (`WAKE_AG-COS-V4_NET-694_R2.8.5_FIX-ONLY_20261031-2320.md`).** |

---

## 2. Turnkey Fixes Required for `R2.8.5` (`NET-694` Must-Fixes 1–3)

### 2.1 MUST-FIX 1 (`-3 pts`): Remove False `"Argon 97 GO"` Attribution (`R2.8.4` Lines `3`, `36`, `638`, `701`)
- **Defect:** `R2.8.4` lines `3`, `36`, `638`, and `701` claim `"Argon review NET-692 scored 97 GO"`.
- **Fact:** Argon's filed review [`GEMINI38_REVIEW_NET-647_R2.8.3_2026-10-31.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.3_2026-10-31.md) (`NET-692A`) scored **`90/100 REVISE`**, and this `R2.8.4` review scores **`93/100 REVISE`**.
- **Required Fix in `R2.8.5`:** Replace all references to `"Argon NET-692 Score 97 GO"` with accurate citations: `Argon Review NET-692A (90/100 REVISE on R2.8.3)` and `Argon Review NET-694A (93/100 REVISE on R2.8.4)`. Never cite a review score that has not been filed by that reviewer.

---

### 2.2 MUST-FIX 2 (`-3 pts`): `Canonical2026MintAssets` `26EA` `reverseUrl` Must Not Point at Un-Uploaded `26ea_b.webp` Without a Real Code Fallback + Pre-Deploy `HEAD`/`MD5` Gate
- **Defect:** In `R2.8.4` Section 3.1 lines `175` and `257`:
  ```dart
  case '26EA':
    return const MintAssetOverride(
      obverseUrl: '$_gcsBase/26ea_a.webp',
      reverseUrl: '$_gcsBase/26ea_b.webp', // Staged in image-intake (164,146 B); GCS fallback: $_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png (612,740 B)
      cardUrl: '$_gcsBase/26ea_a.webp',
      displayName: '2026-W Proof Silver Eagle',
    );
  ```
  `$_gcsBase/26ea_b.webp` returns `HTTP 404` today, and the fallback `$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png` exists **only inside a code comment** (which also mixed `$_ajBase` at line `23` and `$_bulkBase` at line `175`). If `p7-gate` is deployed before or without `26ea_b.webp` being live in GCS, `26EA` Reverse will 404 in the Coin Inspector (repeating the `R2.6` failure mode).
- **Turnkey Fix for `R2.8.5` (Include BOTH in `R2.8.5`):**
  1. **Add `fallbackReverseUrl` to `MintAssetOverride` and wire it in `Canonical2026MintAssets` (using single constant `$_bulkBase`):**
     ```dart
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
     ```
     And in both `case '26EA':` (line `172`) and `if (RegExp(r'\beagle\b').hasMatch(cleanTitle))` (line `254`):
     ```dart
     return const MintAssetOverride(
       obverseUrl: '$_gcsBase/26ea_a.webp',
       reverseUrl: '$_gcsBase/26ea_b.webp',
       fallbackReverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
       cardUrl: '$_gcsBase/26ea_a.webp',
       displayName: '2026-W Proof Silver Eagle',
     );
     ```
     *(Or set `reverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png'` directly as primary until `26ea_b.webp` is verified HTTP 200).*
  2. **Add Mandatory Pre-Deploy `HEAD` + `MD5` Gate in Section 9 Gate 4:**
     Before `firebase hosting:channel:deploy p7-gate` is permitted to run, Gate 4 must execute an automated `HTTP HEAD` check verifying that `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp` (and `23rh_b.webp`, `26xe_b.webp`) returns **`HTTP 200 OK`** with exact `Content-Length` and `MD5` match (`26ea_b.webp` = `164,146 B`, `MD5 = 62ad11e997ac0320b57091e3d108d3e0`). **Deploy is hard-blocked if any staged URL returns non-200.**

---

### 2.3 MUST-FIX 3 (`-1 pt`): Exact Local File Reconciliation, Byte Counts, `MD5`, and `SHA256` for `26ea_b.webp`, `23rh_b.webp`, and `26xe_b.webp`

Argon ran a Python `hashlib` + `PIL` verification across every local copy in `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\` and `1 NUMISTA.AI\Coin Images\`.

**Key Finding:** For all three assets (`26EA`, `23RH`, `26XE`), the file in `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\<Folder>\` and the indexed file in `1 NUMISTA.AI\Coin Images\<SKU>\` (mapped in `1 NUMISTA.AI\Coin Images\_INDEX\image_index.csv` rows `3`, `17`, and `37`) are **byte-for-byte identical (`MD5` and `SHA256` match 100%)**:
- Why `152,078 B` appeared in Argon's `R2.8.3` review text: that was an earlier text transcription error by Argon; the actual file on disk at both `Images from US MInt\...\26ea_b.webp` and `Coin Images\26EA\2026_american_silver_eagle_proof_reverse_26EA.webp` is **`164,146 B`**.
- Why `122,944 B` appeared in `R2.8.4` line `637` for `23rh_b.webp`: that was an unmeasured typo in `R2.8.4`; the actual file on disk at both `Images from US MInt\Silver Proof Set 2023\23rh_b.webp` and `Coin Images\23RH\2023_silver_proof_set_set_obverse_23RH.webp` is **`226,854 B`**.

Paste this exact measured table into `R2.8.5` Section 2 / Section 7 (`S-A`) / Section 9 Gate 4:

| Staged Blob Name | Canonical Local Source File (Identical in `Coin Images\<SKU>\` & `Images from US MInt\`) | Target GCS Object (`--no-clobber` at EXECUTE) | Exact Size (Bytes) | Dimensions | Measured `MD5` | Measured `SHA256` | Why Selected |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **`26ea_b.webp`** | `1 NUMISTA.AI\Coin Images\26EA\2026_american_silver_eagle_proof_reverse_26EA.webp`<br>*(identical to `Images from US MInt\American Eagle 2026 One Ounce Silver Proof Coin\26ea_b.webp`)* | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp` | **`164,146 B`** | `1200x1050 RGB` | `62ad11e997ac0320b57091e3d108d3e0` | `bbf79f95904925193ae753ce07b3a1c69dca0a1429b4c3055ff72c5bff1b71b5` | Official US Mint 2026-W Proof Silver Eagle Type 2 Landing Eagle Reverse (`image_index.csv` Row 3). |
| **`23rh_b.webp`** | `1 NUMISTA.AI\Coin Images\23RH\2023_silver_proof_set_set_obverse_23RH.webp`<br>*(identical to `Images from US MInt\Silver Proof Set 2023\23rh_b.webp`)* | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/23rh_b.webp` | **`226,854 B`** | `1200x1049 RGB` | `8a2060d0ca5987b0faf0d8828ece365f` | `f7326813ab70f0feb09f261debd31f8d562eb0568a347b0024ece9bda78c04ba` | Official US Mint 2023 Silver Proof Set 10-Coin Lens (`image_index.csv` Row 37; fixes `122,944 B` typo in `R2.8.4` line 637). |
| **`26xe_b.webp`** | `1 NUMISTA.AI\Coin Images\26XE\2026_morgan_dollar_enhanced_unc_reverse_26XE.webp`<br>*(identical to `Images from US MInt\Morgan Silver Dollar 2026 Enhanced Uncirculated Coin\26xe_b.webp`)* | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp` | **`245,878 B`** | `1200x1050 RGB` | `3a77694c9a72e6db63811c8b001edbb5` | `08e192bf7f37fdeb83e2c27bed21a1c998fa0c366356280c7593ac3a3c5ee840` | Official US Mint 2026-S Morgan Enhanced Unc Reverse (`image_index.csv` Row 17; supplements live `26XE_image_2.jpg` `240,850 B`). |

---

## 3. Verbatim Code Citations Checked Against Branch `p7-v8.9` (`GEMINI.md` Rule 6a)

Every target file and line range cited in `R2.8.4` was verified directly against branch `p7-v8.9` (`33076f6af727c49a020da0d2d4e96a9560d002d6`):

### 3.1 [`numista_mobile/lib/screens/my_collection_screen.dart:6356-6402`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6356-L6402)
```dart
    // Priority 1: explicit per-coin Firestore image URL (if valid HTTP).
    // For multi-coin sets or coins with a specific design subject (e.g., State
    // Quarters, Innovation Dollars, ATB Quarters), prefer the REVERSE image
    // because the obverse is a shared portrait (Washington, Statue of Liberty)
    // while the reverse carries the unique state/commemorative design.
    final preferReverse = isMultiCoin || subject.isNotEmpty;
    final primaryUrl = preferReverse ? reverseUrl : obverseUrl;
    final secondaryUrl = preferReverse ? obverseUrl : reverseUrl;
    if (_isValidHttpUrl(primaryUrl) &&
        !_hasConflictingFilenameYear(primaryUrl!, year)) {
      return _buildNetworkImage(primaryUrl);
    }
    if (_isValidHttpUrl(secondaryUrl) &&
        !_hasConflictingFilenameYear(secondaryUrl!, year)) {
      return _buildNetworkImage(secondaryUrl);
    }

    // Priority 2: lookup in the canonical coin_image_index via CoinImageService
    return FutureBuilder<CoinImageResult?>(
      future: CoinImageService.instance.findCoinImage(
        year: year,
        denomination: denomination,
        series: series,
        subject: subject.isNotEmpty ? subject : null,
        mintMark: mintMark.isNotEmpty ? mintMark : null,
        isSet: isMultiCoin,
      ),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(
            child: SizedBox(
              width: 22,
              height: 22,
              child: CircularProgressIndicator(
                strokeWidth: 1.5,
                valueColor: AlwaysStoppedAnimation<Color>(
                   _gold.withValues(alpha: 0.45),
                ),
              ),
            ),
          );
        }
        final ref = snapshot.data;
        final refUrl = preferReverse
            ? (ref?.reverseUrl?.isNotEmpty == true
                  ? ref!.reverseUrl!
                  : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true
                        ? ref!.obverseUrl!
                        : (subject.isEmpty ? (ref?.url ?? '') : '')))
            : (ref?.obverseUrl?.isNotEmpty == true
                  ? ref!.obverseUrl!
                  : (ref?.url ?? ''));
        if (_isValidHttpUrl(refUrl) &&
            !_hasConflictingFilenameYear(refUrl, year)) {
```

### 3.2 [`numista_mobile/lib/services/coin_image_service.dart:535-570`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L570)
```dart
      for (final base in bases) {
        final isSubjectBase =
            subjectSlug.isNotEmpty && base.contains(subjectSlug);
        final needsObv = bestObvUrl == null;
        final needsRev = bestRevUrl == null;
        if (!needsObv && !needsRev) break;

        if (needsObv && (!hasSubject || isSubjectBase)) {
          final obvDoc = await _fetchIndexDoc('${base}_obverse');
          if (obvDoc != null) {
            final u = _pickSideFromDoc(obvDoc, 'obverse', mintMark: mint);
            if (u != null) {
              bestObvUrl = u;
              matchedDocData ??= obvDoc;
            }
          }
        }
        if (needsRev && (!hasSubject || isSubjectBase)) {
          final revDoc = await _fetchIndexDoc('${base}_reverse');
          if (revDoc != null) {
            final u = _pickSideFromDoc(revDoc, 'reverse', mintMark: mint);
            if (u != null) {
              bestRevUrl = u;
              matchedDocData ??= revDoc;
            }
          }
        }
```

### 3.3 [`numista_mobile/lib/screens/review_hub_screen.dart:2040-2059`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2040-L2059)
```dart
    // Format Cost & Quantity (Divide line-item cost by quantity when unit_cost is absent)
    final unitCostRaw = data['unit_cost'] ?? data['unitCost'];
    final rawCost =
        unitCostRaw ??
        data['purchase_price'] ??
        data['cost'] ??
        data['price'] ??
        data['estimated_value'] ??
        data['value'];
    String costDisplay = '—';
    if (rawCost != null && rawCost.toString().trim().isNotEmpty) {
      final cleanCost = rawCost.toString().replaceAll(RegExp(r'[^0-9.]'), '');
      final parsed = double.tryParse(cleanCost);
      if (parsed != null && parsed > 0) {
        final perUnit = (unitCostRaw == null && cleanQty > 1)
            ? (parsed / cleanQty)
            : parsed;
        costDisplay = '\$${perUnit.toStringAsFixed(2)}';
      }
    }
```

### 3.4 [`numista_mobile/lib/screens/my_collection_screen.dart:3000-3025`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3000-L3025)
```dart
    final condition = _conditionLabel(data);
    final certNum = (data[_F.certNum] ?? '').toString().trim();

    // Parse valuation
    final rawVal =
        data['estimated_value'] ??
        data['current_value'] ??
        data['market_value'] ??
        data[_F.retailValue] ??
        data['value'];
    double? numVal;
    if (rawVal is num) {
      numVal = rawVal.toDouble();
    } else if (rawVal != null) {
      numVal = double.tryParse(
        rawVal.toString().replaceAll(RegExp(r'[$,\s]'), ''),
      );
    }
    final rawCost =
        data['unit_cost'] ??
        data['purchase_price'] ??
        data['purchase_cost'] ??
        data['cost'] ??
        data['price'];
```

### 3.5 [`numista_backend/services/us_mint_catalog_service.py:235-248`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/us_mint_catalog_service.py#L235-L248)
```python
    "26RJ": {
        "sku": "26RJ",
        "name": "United States Mint Uncirculated Set 2026",
        "series": "U.S. Mint Uncirculated Coin Set",
        "year": 2026,
        "mint_mark": "P & D",
        "denomination": "Set",
        "condition": "Uncirculated",
        "unit_price_cents": 3975,
        "image_url_obverse": f"{_GCS_2026_PRODUCTS_BASE}/26rj_a.webp",
        "image_url_reverse": f"{_GCS_2026_PRODUCTS_BASE}/26RJ_image_2.jpg",
        "card_display_side": "obverse",
        "representative_image": False,
    },
```

---

## 4. Conclusion & Next Step (`WAKE NET-694`)

- **Score:** **`93 / 100 REVISE`** (concurring 100% with Grok CoS [`COS_SCORE_NET-647_R2.8.4_93_REVISE_20261031-2320.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.4_93_REVISE_20261031-2320.md)).
- **Turnkey Path to $\ge 95$ GO in `R2.8.5`:** Apply the 3 surgical fixes in Section 2 above (correct review attribution, add real code `fallbackReverseUrl` + Gate 4 pre-deploy `HEAD`/`MD5` block for `26ea_b.webp`, and paste the measured 3-file `MD5`/`SHA256` manifest fixing `23rh_b.webp` = `226,854 B`).
- **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` frozen at `9b55f3d9`; Stripe OFF; 3 AM stand-down in force.
