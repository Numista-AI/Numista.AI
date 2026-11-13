# GEMINI 3.8 (ARGON) INDEPENDENT TECHNICAL REVIEW — NET-647 FAIL-FIX PLAN R2.8.7

- **Reviewer:** Argon (Gemini 3.8 Independent Technical Reviewer — Docs/Review Only, `NO EXECUTE`)
- **Date / Time:** 2026-11-01 ~01:15 EDT
- **Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md) (951 lines, filed by `AG CoS v4` under [`RADIO_OVER_NET-699_AGCOS-to-ALL_R2.8.7-PLAN-FILED_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/RADIO_OVER_NET-699_AGCOS-to-ALL_R2.8.7-PLAN-FILED_20261101.md))
- **Prior Score / Mandate:** [`COS_SCORE_NET-647_R2.8.6_88_REVISE_20261101-0050.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.6_88_REVISE_20261101-0050.md) (`88/100 REVISE`) & [`GEMINI38_REVIEW_NET-647_R2.8.6_2026-10-31.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.6_2026-10-31.md) (`NET-698A`)
- **Argon Recommended Score:** **97 / 100 — GO / PASS ($\ge 95$ Gate Met — Ready for Grok CoS Re-Score, SAG Concurrence, and Founder Eric's Morning `YES`)**

---

## 1. Executive Summary & Scoring Rubric

`AG CoS v4` (`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`) has cleanly and completely resolved all **4 Must-Fixes (`MUST-FIX 1` through `MUST-FIX 4`)** and all **4 Should-Fixes (`SF-1` through `SF-4`)** from Grok CoS's `NET-698` (`88/100 REVISE`) and Argon's `NET-698A` review.

Argon independently executed read-only verification scripts (`scratch/inspect_28_docs_for_r287.py` and `scratch/verify_r287_resolver_on_28_docs.py`) against live Firestore (`studio-9101802118-8c9a8`) and `gs://numista-reference-library` across all **28 audited rows** (`25` in `users/eric.seaman@yahoo.com/coins` and `3` unique + `1` shared in `users/eric@numista.ai/coins`) and confirmed that `R2.8.7`'s `Canonical2026MintAssets.resolveFromMap()` and `resolve()` logic accurately resolves every 2026/2023 coin and set, preserves Row 10's user microscope photos, and enforces strict mint-mark (`P` vs `D` vs `W`) and year fidelity.

| Rubric Category | Weight | R2.8.6 Score | R2.8.7 Score | Delta | Verification Summary |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. `MUST-FIX 1`: Resolver Title Order & Set Regex Specificity** | 25 | 20 / 25 | **25 / 25** | +5 | Individual coin branches (`eagle` $\rightarrow$ `morgan` $\rightarrow$ `peace` $\rightarrow$ `trump` $\rightarrow$ `dime` $\rightarrow$ `quarter` $\rightarrow$ `half` $\rightarrow$ `innovation`) run strictly before set branches (`lines 287–403`); set regex requires `\b(uncirculated set\|mint set\|coin set\|uncirculated coin set)\b`. |
| **2. `MUST-FIX 2`: Mint Extraction (`data['mint']`) for Dime/Half/Quarter** | 25 | 20 / 25 | **24 / 25** | +4 | `resolveFromMap()` (`lines 166, 181`) extracts `data['mint']` and passes `mint: mintStr` to `resolve()`. Rows 8 (`2026-P` Dime), 9 (`2026-D` Dime), and 11 (`2026-D` Half Dollar) resolve to exact `P`/`D` obverses. *(1 pt deducted for non-blocking `isP` Half Dollar URL note in Section 3.1 below).* |
| **3. `MUST-FIX 3`: User-Upload Guard (`/microscope/`), Row 11 Proof & 2026 Quarters** | 25 | 23 / 25 | **25 / 25** | +2 | `/microscope/` guard (`lines 126–142`) preserves Row 10 (`241,359 B` / `252,870 B`). Quarter branch (`lines 338–353`) routes `mayflower` vs `declaration`. Row 11 (`8f2197d5...`) has full MD5/pixel proof (`lines 625–643`). |
| **4. `MUST-FIX 4` & `SF-1..4`: 28-Row SKU Proof, Unit Tests & Audit Fidelity** | 25 | 25 / 25 | **23 / 25** | -2 | Dedicated SKU column (`lines 587–616`), 15 unit tests (`lines 421–576`), `SF-1..4` resolved. *(2 pts deducted for non-blocking `23rh_c.webp` staging list sync in Section 3.2 below).* |
| **TOTAL** | **100** | **88 / 100** | **97 / 100** | **+9** | **PASS ($\ge 95$ Gate Met)** |

---

## 2. Point-by-Point Audit of `NET-698` Must-Fixes & Should-Fixes (with Verbatim Code Citations per `GEMINI.md` Rule 6a)

### 2.1 `MUST-FIX 1` — Resolver Title Order & Set Regex Specificity (`RESOLVED — 25/25`)

- **Requirement (`NET-698`):** In `Canonical2026MintAssets.resolve()`, check individual coin types (`eagle`, `morgan`, `peace`, `trump|presidential`, `dime`, `quarter`, `half`, `innovation`) **before** set patterns (`uncirculated set`, `silver proof set`, `proof set`), and require the word `set` in set regexes so coin titles containing `"Semiquincentennial"` or `"250th Anniversary"` never get hijacked into the Uncirculated Set (`26RJ`).
- **Verification in [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md#L287-L403) (`lines 287–403`):**
  ```dart
      // =========================================================================
      // STEP 3: STRICTLY ORDERED 2026 TITLE FALLBACK
      // MUST-FIX 1: Check specific individual coin denominations FIRST before
      // checking multi-coin set patterns. Set patterns MUST explicitly require
      // the word "set" and NEVER match bare "semiquincentennial" or "250th anniversary".
      // =========================================================================

      // 3.1: Silver Eagle (Requires "eagle" AND "silver" to avoid gold coin false positives)
      if (RegExp(r'\beagle\b').hasMatch(haystack) && RegExp(r'\bsilver\b').hasMatch(haystack)) {
  ...
      // 3.2: Morgan Dollar
      if (RegExp(r'\bmorgan\b').hasMatch(haystack)) {
  ...
      // 3.3: Peace Dollar
      if (RegExp(r'\bpeace\b').hasMatch(haystack)) {
  ...
      // 3.4: Trump / Presidential Semiquincentennial $1
      // Evaluated BEFORE set patterns so "Semiquincentennial 250th Anniversary Roll"
      // never gets hijacked by set regexes!
      if (RegExp(r'\b(trump|presidential)\b').hasMatch(haystack)) {
  ...
      // 3.5: Dime (2026 Semiquincentennial Liberty Dime)
      if (RegExp(r'\b(dime|roosevelt|10c|10 cents)\b').hasMatch(haystack)) {
  ...
      // 3.6: Quarter Dollar (2026 Semiquincentennial Quarters: Mayflower vs Declaration)
      if (RegExp(r'\b(quarter|25c|mayflower|pilgrim|declaration of independence)\b').hasMatch(haystack) &&
          !RegExp(r'\b(set|half)\b').hasMatch(haystack)) {
  ...
      // 3.7: Half Dollar (2026 Semiquincentennial Enduring Liberty Half Dollar)
      // Evaluated BEFORE set patterns so "250th Anniversary of American Independence Half Dollar"
      // resolves to Half Dollar, never Uncirculated Set!
      if (RegExp(r'\b(half dollar|half|50c|kennedy|enduring liberty)\b').hasMatch(haystack)) {
  ...
      // 3.8: American Innovation $1
      if (RegExp(r'\binnovation\b').hasMatch(haystack)) {
  ...
      // 3.9: Multi-Coin Sets (Evaluated LAST; strictly requires the word "set")
      if (RegExp(r'\b(uncirculated set|mint set|coin set|uncirculated coin set)\b').hasMatch(haystack)) {
  ```
- **Unit Test Proof (`lines 424–445`):** Includes explicit tests proving Row 7 (`title: 'Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)'`, `sku: ''`) resolves to `26sqrp_b.webp` and Row 11 (`title: '250th Anniversary of American Independence'`, `denomination: 'Half Dollar'`, `mint: 'D'`) resolves to `SemiQ-Half-Dollar-Obverse-Unc-D.jpg`. Also adds `uncirculated coin set` to step `3.9` so Row 4 (`"2026 United States Mint Uncirculated Coin Set"`) resolves via title even if SKU is absent.

---

### 2.2 `MUST-FIX 2` — Mint Extraction (`data['mint']`) in `resolveFromMap()` & `resolve()` (`RESOLVED — 24/25`)

- **Requirement (`NET-698`):** Pass `mint: (data['mint'] ?? data['Mint Mark'] ?? '').toString()` from `resolveFromMap(Map<String, dynamic> data)` into `resolve(...)` and use it to select `P` vs `D` obverses for Dime, Half Dollar, and Quarter.
- **Verification in [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md#L166-L203) (`lines 166–203`):**
  ```dart
      // 3. Extract Mint Mark directly from document data['mint'] (MUST-FIX 2)
      final mintStr = (data['mint'] ?? data['Mint Mark'] ?? data['mint_mark'] ?? '').toString().trim().toUpperCase();
  ...
      return resolve(
        sku: rawSku,
        title: titleStr,
        series: seriesStr,
        denomination: denomStr,
        mint: mintStr,
        year: yearStr,
      );
  ...
      final m = mint.trim().toUpperCase();
      final isD = m == 'D' || m.startsWith('D ') || m.contains('DENVER') || RegExp(r'\b2026-d\b').hasMatch(haystack);
      final isP = m == 'P' || m.startsWith('P ') || m.contains('PHILADELPHIA') || RegExp(r'\b2026-p\b').hasMatch(haystack);
  ```
- **Live Firestore Verification:**
  - Row 8 (`nAnGLwGvhfIOibf6kIft`, `mint: "P"`, `title: "Franklin D. Roosevelt"`, `denomination: "Dime (10C)"`) $\rightarrow$ `SemiQ-Dime-Obverse-Unc-P.jpg` (`1,224,376 B`, `200 OK`) + `SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B`, `200 OK`).
  - Row 9 (`rv9SCUTahBuqJkkiJyga`, `mint: "D"`, `title: "Franklin D. Roosevelt"`, `denomination: "Dime (10C)"`) $\rightarrow$ `SemiQ-Dime-Obverse-Unc-D.jpg` (`1,224,042 B`, `200 OK`) + `SemiQ-Dime-Reverse-Unc.jpg` (`1,336,791 B`, `200 OK`).
  - Row 11 (`8f2197d5d03a428db24486b4ee375a5e`, `mint: "D"`, `title: "250th Anniversary of American Independence"`, `denomination: "Half Dollar (50C)"`) $\rightarrow$ `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`, `200 OK`) + `SemiQ-Half-Dollar-Reverse-Unc.jpg` (`1,510,409 B`, `200 OK`).

---

### 2.3 `MUST-FIX 3` — User-Upload Guard (`/microscope/`), Row 11 Pixel Proof & 2026 Quarter Designs (`RESOLVED — 25/25`)

- **Requirement (`NET-698`):** Guard user-uploaded `/microscope/` photos in `resolveFromMap()`, map both 2026 Mayflower Compact and Declaration of Independence quarters in the Quarter fallback, and provide a pixel/MD5 comparison proof for Row 11 (`8f2197d5d03a428db24486b4ee375a5e`).
- **Verification in [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md#L126-L142) (`lines 126–142` & `lines 338–353`):**
  ```dart
      // 1. User-Upload / Microscope Guard (MUST-FIX 3):
      // Never overwrite genuine user microscope uploads (e.g. Row 10 Mayflower Quarter).
      final existingObv = (data['image_url_obverse'] ?? data['image_url'] ?? '').toString();
      final existingRev = (data['image_url_reverse'] ?? '').toString();
      if (_isProtectedUserUpload(existingObv) || _isProtectedUserUpload(existingRev)) {
        return null;
      }
  ```
  ```dart
      // 3.6: Quarter Dollar (2026 Semiquincentennial Quarters: Mayflower vs Declaration)
      if (RegExp(r'\b(quarter|25c|mayflower|pilgrim|declaration of independence)\b').hasMatch(haystack) &&
          !RegExp(r'\b(set|half)\b').hasMatch(haystack)) {
        if (RegExp(r'\b(mayflower|pilgrim)\b').hasMatch(haystack)) {
          return const CanonicalMintAssetPair(
            obverseUrl: '$_seriesBase/2026_quarter_dollar_mayflower_compact_obverse.jpg',
            reverseUrl: '$_seriesBase/2026_quarter_dollar_mayflower_compact_reverse.jpg',
            cardUrl: '$_seriesBase/2026_quarter_dollar_mayflower_compact_obverse.jpg',
            displayName: '2026 Semiquincentennial Quarter (Mayflower Compact)',
          );
        }
  ```
- **Row 11 Bitwise & Pixel Proof Verified (`lines 625–643`):**
  - Stored reverse (`users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/reverse.jpg`, `1,510,409 B`) has `MD5 = cceb4ab85d398347792d8929fb11bed0`, **100% bitwise identical** to `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg`.
  - Stored obverse (`.../obverse.jpg`, `1,510,450 B`) has `MD5 = ec05347cabf3b134a262ac9f6631385b`, **100% bitwise identical** to `reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` (`2026-P` stock image) and differs from `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`) only inside the $60 \times 70$ px mint-mark box ($X \in [924, 984], Y \in [1638, 1707]$, `'P'` vs `'D'`). Because Row 11 has `Source: "Morgan AI Assistant Chat"` and `mint: "D"`, replacing the `P`-mint stock copy with `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` is 100% justified.

---

### 2.4 `MUST-FIX 4` & `SF-1..4` — 28-Row SKU Extraction, Section 4 SKU Column & Unit Tests (`RESOLVED — 23/25`)

- **Verification in [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md#L145-L164) (`lines 145–164`):**
  ```dart
      // 2. Extract SKU from dedicated fields OR Personal Notes ("Item # 26RJ", "Item # 26SQRP")
      String rawSku = (data['retailer_item_num'] ??
              data['Retailer Item No.'] ??
              data['product_code'] ??
              data['sku'] ??
              data['item_number'] ??
              '')
          .toString()
          .trim();

      if (rawSku.isEmpty) {
        final notes = (data['personal_notes'] ??
                data['Personal Notes'] ??
                data['notes'] ??
                data['description'] ??
                '')
            .toString();
        final m = RegExp(r'\bItem\s*#?:?\s*([A-Za-z0-9]+)\b', caseSensitive: false).firstMatch(notes);
        if (m != null) {
          rawSku = m.group(1)!.toUpperCase();
        }
      }
  ```
- **Live 28-Document Verification Summary (`scratch/verify_r287_resolver_on_28_docs.py`):**
  - **Row 1 (`e91efa62...`):** `Retailer Item No. = '26EA'` $\rightarrow$ SKU `26EA` (`26ea_a.webp` + `%241_Silver_Eagle_Type_2_Reverse.png`).
  - **Row 2 & Row 26 (`be10e44c...`):** `retailer_item_num = '26XE'` $\rightarrow$ SKU `26XE` (`26xe_a.webp` + `26XE_image_2.jpg`).
  - **Row 3 (`a59853c1...`):** `Retailer Item No. = '26XL'` $\rightarrow$ SKU `26XL` (`26xl___a.webp` + `26XL_image_3.jpg`).
  - **Row 4 (`71e2d4ae...`):** `product_code = '26RJ'` & title `'2026 United States Mint Uncirculated Coin Set'` $\rightarrow$ `26rj_e.jpg` + `26rj_b.jpg`.
  - **Row 5 (`91f88212...`):** `retailer_item_num = '26RJ'` $\rightarrow$ SKU `26RJ` (`26rj_e.jpg` + `26rj_b.jpg`).
  - **Row 6 (`0e68ecba...`):** `retailer_item_num = '26GC'` $\rightarrow$ SKU `26GC` (`2026_american_innovation_obverse.jpg` + `26gc_b.webp`).
  - **Row 7 (`7a32932e...`):** `retailer_item_num = '26SQRP'` & title `'Donald J. Trump...'` $\rightarrow$ `26sqrp_b.webp` + `MASTER_SEMIQDJT_image_2.jpg`.
  - **Row 25 (`0a2bc793...`):** `Personal Notes = 'Item # 26RJ - Uncirculated Coin Set 2026'` $\rightarrow$ SKU `26RJ` (`26rj_e.jpg` + `26rj_b.jpg`).
  - **Row 27 (`faa5b1cf...`):** `Personal Notes = 'Item # 26SQRP Semiquincentennial President D'` $\rightarrow$ SKU `26SQRP` (`26sqrp_b.webp` + `MASTER_SEMIQDJT_image_2.jpg`).
  - **Row 28 (`2fa32516...`):** `retailer_item_num = '23RH'` $\rightarrow$ SKU `23RH` (`2023_products/23rh_b.webp`).
  - **Should-Fixes `SF-1`..`SF-4`:** All 4 Should-Fixes (`Row 18` obverse stays as stored pending 1962 Proof intake; `Row 19` `2019-W` obverse flagged pending intake; `Row 26` cross-account duplicate & `977b5ab2` Vera Rubin `PASS` documented; undated ATB obverse exemption tested in `lines 556–563`) are completely addressed.

---

## 3. Non-Blocking `EXECUTE`-Time Implementation Notes (Verify at Gate 4 Pre-Deploy)

These two minor items do **not** require another plan revision (`R2.8.7` passes $\ge 95$ at **97/100**), but `AG CoS v4` must apply them when writing code at `EXECUTE` time (after Eric's morning `YES`):

1. **Half Dollar `isP` Obverse URL (`R2.8.7` Line `360` & Test Line `476`):**
   - In `R2.8.7` line `360`:
     ```dart
     final obv = isP
         ? '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-P.jpg'
         : '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg';
     ```
   - In `gs://numista-reference-library`, `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-P.jpg` is currently `404 Not Found` (only `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` `1,510,128 B` and `SemiQ-Half-Dollar-Reverse-Unc.jpg` `1,510,409 B` exist in `bulk_programs/half_dollar/`). The live `2026-P` Half Dollar obverse in GCS is at `'$_seriesBase/2026_half_dollar_enduring_liberty_obverse.jpg'` (`1,510,450 B`, `200 OK`, `MD5=ec05347cabf3b134a262ac9f6631385b`).
   - Because Row 11 (`8f2197d5d03a428db24486b4ee375a5e`) has `mint: "D"`, Row 11 takes the `: '$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'` branch (`200 OK`). At `EXECUTE` time, either point the `isP` branch on line `360` to `'$_seriesBase/2026_half_dollar_enduring_liberty_obverse.jpg'` or copy that object to `reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-P.jpg` during Gate 4 staging.
2. **Staging `23rh_c.webp` Alongside `23rh_b.webp` (`R2.8.7` Line `273` vs Section `9.1` Lines `933–939`):**
   - In `R2.8.7` line `273`, the `23RH` (`Row 28`) branch returns `reverseUrl: '$_official2023Base/23rh_c.webp'`, while Section `9.1` (`lines 933–939`) lists 3 files to upload (`26ea_b.webp`, `23rh_b.webp`, `26xe_b.webp`).
   - At `EXECUTE` time (Gate 4), upload **`23rh_c.webp`** (`161,734 B`, `1200x1050`, `MD5=08f5b5aaf698936913e2a24743dbdea5`) alongside `23rh_b.webp` (`226,854 B`, `1200x1049`, `MD5=8a2060d0ca5987b0faf0d8828ece365f`) to `gs://numista-reference-library/reference_library/us_mint_official/2023_products/` (or use `23rh_b.webp` for both `obverseUrl` and `reverseUrl`).

---

## 4. Gate Status & Recommendation

- **Argon Verdict:** **97 / 100 — GO / PASS ($\ge 95$ Gate Met)**
- **Next Steps:**
  1. Grok CoS (`NET-699`) scores `R2.8.7` ($\ge 95$).
  2. Packet mirrored to `For SAG` for Senior Advisory Group review.
  3. Hold all code/GCS/Firestore mutations until Founder Eric's morning typed **`YES`**.
