# GEMINI 3.8 TECHNICAL REVIEW — NET-647 FAIL-FIX PLAN R2.8.5 (2026 US MINT CATALOG, GCS PROVENANCE & 28-ITEM REMEDIATION)

- **Reviewer:** `Argon` (Gemini 3.8 — Thinking, Planning, & Review Only)
- **Date / Time:** 2026-11-01 00:10 EDT (Filing under 2026-10-31 sprint log series `NET-695` / `NET-696`)
- **Plan Under Review:** [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md) (`NET-695`)
- **Grok CoS Parallel Score:** [`COS_SCORE_NET-647_R2.8.5_82_REVISE_20261031-2350.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.5_82_REVISE_20261031-2350.md) (`82/100 REVISE -> R2.8.6`, `NET-696`)
- **Argon Independent Score:** **`82 / 100 — REVISE (Fix-Only R2.8.6 Required)`**
- **Governance & Locks:** `origin/main` = `9f04550a` (LOCKED) | `origin/dev` = `9b55f3d9` (FROZEN) | **NO EXECUTE** | **Stripe OFF**

---

## 1. Executive Summary & Rubric Breakdown

`AG CoS v4` (`NET-695`) cleanly resolved **100% of `NET-694` Must-Fixes `MF1` through `MF3`**:
1. **Review Attribution Integrity (`MF1` — PASS):** `FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:10` and `:14-15` accurately cite `NET-692A` (`90/100 REVISE`) and `NET-694A` (`93/100 REVISE`).
2. **`26EA` Live `reverseUrl` & Unified `_bulkBase` (`MF2` — PASS):** `FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:88-90` and `:167-178` define a single `_bulkBase` constant and map `26EA` `reverseUrl` to the live Type 2 landing eagle reverse (`'$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png'`, `HTTP 200 OK`, `612,740 B`) with `fallbackReverseUrl: '$_gcsBase/26ea_b.webp'` (`164,146 B`, staged for upload at `EXECUTE`).
3. **Pre-Flight Staging Manifest & Gate 4 (`MF3` — PASS):** `FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:57-61` and `:678-693` provide exact byte sizes, pixel dimensions (`1200x1200` / `1200x1049`), `MD5`, and `SHA256` hashes for `26ea_b.webp` (`164,146 B`), `23rh_b.webp` (`226,854 B`), and `26xe_b.webp` (`245,878 B`), and hard-block `p7-gate` preview deploy until `HTTP HEAD` returns `200 OK` with matching `MD5`.

**Why `R2.8.5` Drops to `82/100 REVISE` (`NET-696` `MF-A` through `MF-E`):**
When `AG CoS v4` regenerated Section 4 (`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:372-401`), it accidentally overwrote the real `ERIC_ACCOUNT_252_AUDIT_20261031.csv` rows (`20–28`) that were already present in `R2.8.4` (`FAILFIX_PLAN_NET-647_R2.8.4_20261031.md:382-390`) with synthetic/placeholder doc IDs (`a1b2c3d4`, `b2c3d4e5`, `c3d4e5f6`, `d4e5f6g7`), overwrote Row 19 (`UOBfFO2mqgLg86NSsyss`, `2019-W San Antonio Missions`) with a generic `"2019 Quarter | Washington (Phila)"` row, mapped Denver (`obverse-d`) obverses onto Philadelphia (`P`) ATB quarters, mapped a `1962-D` Denver circulation cent onto a `1962` (Philadelphia) Gem Proof cent, and mapped `2026` `26RH` images onto a `2023` `23RH` Silver Proof Set.

To ensure `R2.8.6` reaches $\ge 95/100$ `GO` on a single pass with zero hand-editing errors, **Section 3 of this review provides the complete, Python-generated, HTTP-verified 28-row Section 4 markdown table** tied 1-to-1 to [`ERIC_ACCOUNT_252_AUDIT_20261031.csv`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_ACCOUNT_252_AUDIT_20261031.csv).

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. `NET-694` Must-Fixes (`MF1–MF3`)** | 30 | **30 / 30** | Attribution fixed; `26EA` uses live `612,740 B` Type 2 reverse + `_bulkBase`; Section 2.1 manifest (`164,146 B`, `226,854 B`, `245,878 B`) + Gate 4 `MD5` check complete. |
| **2. Section 4 Audit Table Fidelity (`MF-A`–`MF-E`)** | 35 | **17 / 35** | **-6** (`MF-A`: 12 of 28 doc IDs in `R2.8.5` Section 4 are not in `ERIC_ACCOUNT_252_AUDIT_20261031.csv`); **-4** (`MF-B`: P-mint ATB quarters mapped to `obverse-d`/`obverse-denver`); **-3** (`MF-C`: Row 19 `UOBfFO2m` San Antonio Missions overwritten); **-2** (`MF-D`: Row 18 `Wq2UhSQN` 1962 Gem Proof mapped to `1962-D`); **-3** (`MF-E`: Row 28 2023 `23RH` mapped to 2026 `26RH` images). |
| **3. Backend & Frontend Architecture** | 20 | **20 / 20** | 3-tier `_pick_2026_us_mint_gcs_pair` (`main.py`), `us_mint_2026_catalog.dart`, and `coin_image.dart` fallback hierarchy are sound. |
| **4. Verification Gates & Governance** | 15 | **15 / 15** | Gate 4 hard-blocks `p7-gate` deploy on staged asset `HEAD`/`MD5`; 40 mobile test files enumerated; `NO EXECUTE` respected. |
| **TOTAL** | **100** | **82 / 100** | **REVISE (`R2.8.6` Fix-Only)** |

---

## 2. Rule 6(a) Verbatim Code & Plan Verification of `MF-A` through `MF-E`

### 2.1 Verification of `NET-694` Resolutions in `R2.8.5` (PASS)
- [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:88-90`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L88-L90):
  ```dart
    static const String _bulkBase =
        'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs';
  ```
- [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:167-178`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L167-L178):
  ```dart
      UsMint2026Product(
        sku: '26EA',
        name: 'American Eagle 2026 One Ounce Silver Proof Coin',
        denomination: r'$1',
        mintMark: 'W',
        finish: 'Proof',
        issuePrice: 95.00,
        obverseUrl: '$_gcsBase/26ea_a.webp',
        reverseUrl: '$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png',
        fallbackObverseUrl: '$_gcsBase/26EA_image_3.jpg',
        fallbackReverseUrl: '$_gcsBase/26ea_b.webp',
  ```
- **Target Codebase Context (`numista_backend/main.py` & `numista_mobile/lib/widgets/coin_image.dart`):**
  - [`numista_backend/main.py:2169-2177`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L2169-L2177):
    ```python
    def _pick_2026_us_mint_gcs_pair(
        blob_names: list[str],
        denom_l: str,
        series_l: str,
        subject_l: str,
        raw_text_l: str = "",
        mint_l: str = "",
    ) -> tuple[Optional[str], Optional[str]]:
        """Pick (obv_blob, rev_blob) from reference_library/2026_series/* based on denomination/subject."""
    ```
  - [`numista_mobile/lib/widgets/coin_image.dart:118-126`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/coin_image.dart#L118-L126):
    ```dart
      void _advanceOrFail() {
        if (_currentIndex + 1 < widget.urls.length) {
          setState(() {
            _currentIndex++;
          });
        } else {
          setState(() {
            _allFailed = true;
          });
    ```

### 2.2 Detailed Audit of `NET-696` Must-Fixes (`MF-A` through `MF-E`)

1. **`MF-A` — 12 of 28 Doc IDs in `R2.8.5` Section 4 Do Not Exist in `ERIC_ACCOUNT_252_AUDIT_20261031.csv`:**
   - [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:380`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L380), [`:383-384`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L383-L384), and [`:393-401`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L393-L401):
     ```markdown
     | **7** | `933df91f...` (`eric.seaman`) | 2026 Trump $1 | 2026 Trump $1 Coin Roll | ...
     | **10** | `3f7cd90b...` (`eric.seaman`) | 2026 Quarter | 2026 Semiquincentennial Quarter | ...
     | **11** | `b015e197...` (`eric.seaman`) | 2026 Half $ | 2026 Semiquincentennial Half $ | ...
     | **20** | `2233c46e...` (`eric.seaman`) | 2017 ATB Q | Effigy Mounds (Iowa) | ...
     | **21** | `532e8b1d...` (`eric.seaman`) | 2017 ATB Q | Frederick Douglass (DC) | ...
     | **22** | `7a1d13f9...` (`eric.seaman`) | 2010 ATB Q | Yellowstone (Wyoming) | ...
     | **23** | `3ccb26e0...` (`eric.seaman`) | 2017 ATB Q | George Rogers Clark (Indiana) | ...
     | **24** | `d4e5f6a7...` (`eric.seaman`) | 2017 ATB Q | Ozark Riverways (Missouri) | ...
     | **25** | `a1b2c3d4...` (`eric@numista`) | 2026 Mint Set | 2026 Uncirculated Coin Set | ...
     | **26** | `b2c3d4e5...` (`eric@numista`) | 2026 Morgan | 2026-S Morgan Enhanced Unc | ...
     | **27** | `c3d4e5f6...` (`eric@numista`) | 2026 Trump $1 | 2026 Semiquincentennial $1 | ...
     | **28** | `d4e5f6g7...` (`eric@numista`) | 2023 Proof Set | 2023 Silver Proof Set (23RH) | ...
     ```
   - **Exact CSV Mapping (`ERIC_ACCOUNT_252_AUDIT_20261031.csv`):**
     - Row 7 (`933df91f` in `R2.8.5`) $\rightarrow$ Real CSV doc is **`7a32932ebc4e94a586534e7180cd1c4372c4f17d`** (`eric.seaman@yahoo.com`, `yr=2026`, `mint=D`, `title=Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)`, `defect=Missing images`).
     - Row 10 (`3f7cd90b` in `R2.8.5`) $\rightarrow$ Real CSV 2026 Quarter doc is **`0172d0ee64284a12a8aa269ce805ec07`** (`eric.seaman@yahoo.com`, `yr=2026`, `mint=P`, `title=Mayflower Compact & Pilgrim Couple`, `defect=PASS`, with user-uploaded microscope images `241,359 B` / `252,870 B` which must be preserved, while reference catalog fallback is `2026_quarter_dollar_mayflower_compact_obverse.jpg` `1,446,894 B` / `..._reverse.jpg` `1,627,560 B`).
     - Row 11 (`b015e197` in `R2.8.5`) $\rightarrow$ Real CSV 2026 Half Dollar doc is **`8f2197d5d03a428db24486b4ee375a5e`** (`eric.seaman@yahoo.com`, `yr=2026`, `mint=D`, `title=250th Anniversary of American Independence`, currently storing a `1,510,450 B` copy of `SemiQ-Half-Dollar-Obverse-Unc-P.jpg` on a `mint=D` coin; remediated to `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` `1,510,128 B` + `SemiQ-Half-Dollar-Reverse-Unc.jpg` `1,510,409 B`).
     - Rows 20–24 $\rightarrow$ Real CSV docs (which were already in `R2.8.4`!) are **`3f437576-fa20-4ef1-95c0-01e10eaf43a8`**, **`6ff959a0-26f8-451f-aa4c-064b5ef68939`**, **`96eeb7b6-6c4e-4a62-bb8e-80b69706d915`**, **`ab35ab5d-d51f-4b9c-bc94-ff87def52bc6`**, and **`b785236f-ca64-4461-9ee4-01cad3a7d60e`**.
     - Rows 25–28 $\rightarrow$ Real CSV docs for `eric@numista.ai` (which were already in `R2.8.4`!) are **`0a2bc793-8d62-47c3-88cd-7a5b9be434ba`**, **`be10e44ce5b4ff4b46c92426cc7f59a254ed675c`**, **`faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c`**, and **`2fa325166682b70aa0d64da45786c94aa4742d21`** (plus `977b5ab2-06a3-41ce-b101-8b2ceee7e6b5`, `2025-D` Vera Rubin Quarter, which is `PASS` with user microscope photos).

2. **`MF-B` — Mint-Mark Accuracy on Philadelphia (`P`) ATB Quarters (Rows 13–17 AND Rows 20–22, 24):**
   - In `ERIC_ACCOUNT_252_AUDIT_20261031.csv`, **both** Rows 20–22 & 24 (`3f437576`, `6ff959a0`, `96eeb7b6`, `b785236f`) **AND** Rows 13–17 (`3346cda5` `2019-P`, `b243621c` `2020-P`, `c336e53e` `2013-P`, `cba5e585` `2018-P`, `d7fec246` `2018-P`) have **`mint = P`** (Philadelphia)! Only Row 23 (`ab35ab5d` `2017-D` George Rogers Clark) has **`mint = D`**.
   - In fact, in `ERIC_ACCOUNT_252_AUDIT_20261031.csv`, Rows 13–17 **already** store the exact Philadelphia (`P`) obverse URLs:
     - Row 13 (`3346cda5`, `2019-P`): `.../atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`200 OK`, `2,133,544 B`)
     - Row 14 (`b243621c`, `2020-P`): `.../atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`200 OK`, `1,340,722 B`)
     - Row 15 (`c336e53e`, `2013-P`): `.../atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` (`200 OK`, `1,867,830 B`)
     - Row 16 (`cba5e585`, `2018-P`): `.../atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`200 OK`, `2,309,513 B`)
     - Row 17 (`d7fec246`, `2018-P`): `.../atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` (`200 OK`, `2,309,513 B`)
   - And for Rows 20, 21, 22, and 24 (`3f437576` `2017-P`, `6ff959a0` `2017-P`, `96eeb7b6` `2010-P`, `b785236f` `2017-P`), the Philadelphia (`P`) ATB undated Washington obverse in `gs://numista-reference-library` is `.../atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` (`200 OK`, `712,711 B`). Never overwrite a `P`-mint quarter with `obverse-d.webp` or `obverse-denver.jpg`!

3. **`MF-C` — Row 19 (`UOBfFO2mqgLg86NSsyss`) Overwritten in `R2.8.5`:**
   - [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:392`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L392):
     ```markdown
     | **19** | `UOBfFO2m...` (`eric.seaman`) | 2019 Quarter | Washington (Phila) | `...1932-george-washington...` / `...` | `.../50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg`<br>*(200 OK, 650,906 B)* | `.../50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg`<br>*(200 OK, 650,906 B)* | `...quarter_obverse...Philadelphia...` | 2019 Washington obverse replaces 1932 |
     ```
   - In `ERIC_ACCOUNT_252_AUDIT_20261031.csv` (row 151), `UOBfFO2mqgLg86NSsyss` is **`2019-W` San Antonio Missions** (`mint=W`, `title=San Antonio Missions`, `stored_rev=.../bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg`). Restore the San Antonio Missions reverse (`.../atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg`, `200 OK`, `2,116,020 B`, or `.../bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg`, `200 OK`, `1,447,978 B`), and note that because `gs://numista-reference-library` has only `2019-...-obverse-philadelphia.jpg` (`2,133,544 B`) and `2019-...-obverse-denver.jpg` (`2,134,218 B`) (no `2019-W` West Point quarter obverse in GCS), the `2019-W` obverse is either staged or explicitly documented as using `2019-...-obverse-philadelphia.jpg` (`2,133,544 B`) pending a `2019-W` obverse upload.

4. **`MF-D` — Row 18 (`Wq2UhSQNs67u34VFJDaI`) `1962` Gem Proof Lincoln Cent Mapped to `1962-D`:**
   - [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:391`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L391):
     ```markdown
     | **18** | `Wq2UhSQN...` (`eric.seaman`) | 1962 Cent | Abraham Lincoln | `...1909-1C...` / `...2008-lincoln...` | `.../Obverses_of_United_States_cents/1962_D_Lincoln_Penny__28U.S._Coin.jpg`<br>*(200 OK, 782,727 B)* | `.../Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg`<br>*(200 OK, 608,070 B)* | `1962_D_Lincoln_Penny...jpg` | Authentic 1962-D Lincoln obverse; Memorial rev |
     ```
   - `Wq2UhSQNs67u34VFJDaI` has `yr=1962`, `mint=""` (Philadelphia), `grade=Gem Proof`. Putting `1962_D_Lincoln_Penny__28U.S._Coin.jpg` (a Denver business strike with a `D` mintmark) on a Philadelphia Gem Proof violates the date/mintmark accuracy rule. We checked all 192 blobs in `reference_library/wikimedia_uscoin/United_States_cents/` and `reference_library/bulk_programs/penny/`: there is **no** no-mintmark `1962` Proof Lincoln Cent obverse currently in GCS. Therefore, Row 18's obverse must be flagged **`MISSING IN GCS — Stage 1962 (no-mintmark) Proof Lincoln Cent obverse at EXECUTE (do NOT substitute 1962-D)`**, while the reverse uses `.../Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` (`200 OK`, `608,070 B`).

5. **`MF-E` — Row 28 (`2fa325166682b70aa0d64da45786c94aa4742d21`) `2023` Silver Proof Set (`23RH`) Mapped to `2026` `26RH` Images:**
   - [`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:401`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.5_20261031.md#L401):
     ```markdown
     | **28** | `d4e5f6g7...` (`eric@numista`) | 2023 Proof Set | 2023 Silver Proof Set (23RH) | `None` / `None` | `.../2026_products/26RH_image_1.jpg`<br>*(200 OK, 110,063 B)* | `.../2026_products/26RH_image_2.jpg`<br>*(200 OK, 108,365 B)* | `26RH_image_1.jpg` | Fallback live 200 OK; `23rh_b.webp` (226,854 B) staged for EXECUTE |
     ```
   - Mapping `26RH_image_1.jpg` / `26RH_image_2.jpg` (`2026` Silver Proof Set) onto a **`2023`** Silver Proof Set (`23RH`, real CSV doc `2fa325166682b70aa0d64da45786c94aa4742d21` in `eric@numista.ai` and `eric.seaman@yahoo.com`) puts a `2026` image on a `2023` item. Furthermore, in Section 2.1 (`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:60`), `23rh_b.webp` (`226,854 B`, `1200x1049`, `MD5 = 8a2060d0ca5987b0faf0d8828ece365f`) and `23rh_c.webp` (`161,734 B`, `1200x1050`, `MD5 = 08f5b5aaf698936913e2a24743dbdea5`) from `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\Silver Proof Set 2023\` must be staged under a **`2023`** GCS path (`reference_library/us_mint_official/2023_products/23rh_b.webp` and `23rh_c.webp`), NOT under `2026_products/`.

---

## 3. Turnkey Script-Generated Section 4 Table for `R2.8.6` (Copy-Paste Ready)

Every row below was generated directly from [`ERIC_ACCOUNT_252_AUDIT_20261031.csv`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_ACCOUNT_252_AUDIT_20261031.csv) and verified via Python `urllib.request.Request(..., method="HEAD")` (`build_turnkey_r286_section4.py`). `AG CoS v4` can drop this table directly into Section 4 of `FAILFIX_PLAN_NET-647_R2.8.6_20261031.md`:

| # | Real CSV Doc ID & Account | CSV Year, Mint & Denom | CSV Stored Title | Current Stored Obverse / Reverse in CSV | Post-Fix Obverse URL (HTTP 200, Measured Bytes) | Post-Fix Reverse URL (HTTP 200, Measured Bytes) | Post-Fix Card URL | Verification Criterion |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `e91efa62-4e8d-4920-a928-c0c97659bcdc` (`eric.seaman@yahoo.com`) | `2026-W` Dollar (`Proof`) | `America250` (2026-W Silver Eagle Proof) | `...American Eagle 2023...Obverse.jpg` / `...Reverse.jpg` | `.../us_mint_official/2026_products/26ea_a.webp`<br>*(200 OK, 168,246 B)* | `.../bulk_programs/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png`<br>*(200 OK, 612,740 B)*<br>*(Staged `26ea_b.webp` 164,146 B at EXECUTE)* | `26ea_a.webp` | 2026 Walking Liberty obverse + live Type 2 landing eagle rev (`26ea_b.webp` staged) |
| **2** | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` (`eric.seaman@yahoo.com`) | `2026` Dollar (`Enhanced Unc`) | `Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)` | `None` / `None` | `.../us_mint_official/2026_products/26xe_a.webp`<br>*(200 OK, 216,358 B)* | `.../us_mint_official/2026_products/26XE_image_2.jpg`<br>*(200 OK, 240,850 B)*<br>*(Staged `26xe_b.webp` 245,878 B at EXECUTE)* | `26xe_a.webp` | 1776~2026 Morgan obverse + 'S' mintmark eagle reverse |
| **3** | `a59853c1-b72b-414d-8b8e-de6813c29996` (`eric.seaman@yahoo.com`) | `2026-P` Dollar (`Reverse Proof`) | `America250` (2026-S Peace Reverse Proof) | `...Peace-Dollar-Reverse-Proof-Obverse.jpg` / `...Reverse.jpg` | `.../us_mint_official/2026_products/26xl___a.webp`<br>*(200 OK, 239,954 B)* | `.../us_mint_official/2026_products/26XL_image_3.jpg`<br>*(200 OK, 204,667 B)* | `26xl___a.webp` | Full Peace Liberty obverse & full eagle reverse (0 privy zoom crops) |
| **4** | `71e2d4ae92bc4312a4198a3a0cc21fcb` (`eric.seaman@yahoo.com`) | `2026` Set (`Uncirculated`) | `2026 United States Mint Uncirculated Coin Set` | `.../uncirculated-coin-set-2026/26rj_a.jpg` / `.../26rj_e.jpg` | `.../user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg`<br>*(200 OK, 336,365 B)* | `.../user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg`<br>*(200 OK, 265,821 B)* | `26rj_e.jpg` | Clear 10-coin P-lens (`26rj_e.jpg`) replaces outer box (`26rj_a.jpg`); D-lens (`26rj_b.jpg`) rev |
| **5** | `91f8821265bfe8a33fbd97e21f102c67fdf849fd` (`eric.seaman@yahoo.com`) | `2026` Set (`Uncirculated`) | `Untitled` (2026 Uncirculated Set) | `None` / `None` | `.../user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg`<br>*(200 OK, 336,365 B)* | `.../user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg`<br>*(200 OK, 265,821 B)* | `26rj_e.jpg` | Zero placeholders; P-lens (`26rj_e.jpg`) obverse & D-lens (`26rj_b.jpg`) reverse |
| **6** | `0e68ecba760df66bf824ec1ba2c86b32318d002d` (`eric.seaman@yahoo.com`) | `2026` `$1` (`Unspecified / Raw`) | `Untitled` (2026 Innovation Proof Set `26GC`) | `None` / `None` | `.../2026_series/2026_american_innovation_obverse.jpg`<br>*(200 OK, 1,279,411 B)* | `.../us_mint_official/2026_products/26gc_b.webp`<br>*(200 OK, 137,372 B)* | `26gc_b.webp` | Statue of Liberty obverse; 4-coin Proof lens (`26gc_b.webp`) on reverse & card |
| **7** | `7a32932ebc4e94a586534e7180cd1c4372c4f17d` (`eric.seaman@yahoo.com`) | `2026-D` Dollar (`Uncirculated`) | `Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)` | `None` / `None` | `.../us_mint_official/2026_products/26sqrp_b.webp`<br>*(200 OK, 179,722 B)* | `.../us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg`<br>*(200 OK, 245,212 B)* | `26sqrp_b.webp` | Real CSV doc `7a32932e...`: Trump portrait obverse & Liberty reverse (0 missing images) |
| **8** | `nAnGLwGvhfIOibf6kIft` (`eric.seaman@yahoo.com`) | `2026-P` Dime (`UNC`) | `Franklin D. Roosevelt` | `...2025-roosevelt-dime-uncirculated-obverse-philadelphia.jpg` / `...reverse.jpg` | `.../bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg`<br>*(200 OK, 1,224,376 B)* | `.../bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg`<br>*(200 OK, 1,336,791 B)* | `SemiQ-Dime-Obverse-Unc-P.jpg` | 2026-P Semiquincentennial Liberty obverse & torch reverse (replaces 2025 Dime) |
| **9** | `rv9SCUTahBuqJkkiJyga` (`eric.seaman@yahoo.com`) | `2026-D` Dime (`UNC`) | `Franklin D. Roosevelt` | `...2025-roosevelt-dime-uncirculated-obverse-denver.jpg` / `...reverse.jpg` | `.../bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg`<br>*(200 OK, 1,224,042 B)* | `.../bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg`<br>*(200 OK, 1,336,791 B)* | `SemiQ-Dime-Obverse-Unc-D.jpg` | 2026-D Semiquincentennial Liberty obverse & torch reverse (replaces 2025 Dime) |
| **10** | `0172d0ee64284a12a8aa269ce805ec07` (`eric.seaman@yahoo.com`) | `2026-P` Quarter Dollar (`UNC`) | `Mayflower Compact & Pilgrim Couple` | `...2026_semiquincentennial_mayflower_compact_quarter_p_Obverse_20260701_1731.jpg` / `...Reverse...` | Keep user microscope Obv (`200 OK, 241,359 B`)<br>*(Ref fallback: `.../2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg`, 200 OK, 1,446,894 B)* | Keep user microscope Rev (`200 OK, 252,870 B`)<br>*(Ref fallback: `.../2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg`, 200 OK, 1,627,560 B)* | `...mayflower_compact_quarter_p_Reverse_20260701_1731.jpg` | Real CSV doc `0172d0ee...`: user microscope photos preserved (`PASS`) + verified 2026 Mayflower ref fallback |
| **11** | `8f2197d5d03a428db24486b4ee375a5e` (`eric.seaman@yahoo.com`) | `2026-D` Half Dollar (`MS-66`) | `250th Anniversary of American Independence` | `.../b22f8905.../obverse.jpg` (`1,510,450 B`, P-mint copy) / `.../reverse.jpg` | `.../bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg`<br>*(200 OK, 1,510,128 B)* | `.../bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg`<br>*(200 OK, 1,510,409 B)* | `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` | Real CSV doc `8f2197d5...` (`2026-D`): Denver (`D`) Enduring Liberty obverse + eagle reverse |
| **12** | `5b424047-77e0-496e-a513-6ef180b515a6` (`eric.seaman@yahoo.com`) | `2005-D` Quarter (`Raw`) | `Kansas` | `...quarter_obverse__28Denver_29.jpg` / `...2003-50-state-quarters-coin-arkansas...` | `.../50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg`<br>*(200 OK, 572,791 B)* | `.../bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg`<br>*(200 OK, 546,742 B)* | `2005-...-kansas-uncirculated-reverse.jpg` | 2005-D Kansas: Denver (`D`) obverse + 2005 Kansas reverse (replaces 2003 Arkansas) |
| **13** | `3346cda5-5935-4303-bf62-de43041f3175` (`eric.seaman@yahoo.com`) | `2019-P` Quarter (`Raw`) | `American Memorial Park (Northern Mariana Islands)` | `...2019-...-obverse-philadelphia.jpg` / `...2015-...-blue-ridge-parkway...` | `.../atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg`<br>*(200 OK, 2,133,544 B)* | `.../atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg`<br>*(200 OK, 2,064,160 B)* | `2019-...-american-memorial-park-...-reverse.jpg` | 2019-P (`mint=P`): Philadelphia (`P`) obverse preserved + 2019 Memorial Park reverse (replaces 2015 Blue Ridge) |
| **14** | `b243621c-5a35-45f0-84bf-8786eb1547f9` (`eric.seaman@yahoo.com`) | `2020-P` Quarter (`Raw`) | `Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)` | `...2020-...-obverse-philadelphia.jpg` / `...2017-...-ozark-riverways...` | `.../atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg`<br>*(200 OK, 1,340,722 B)* | `.../atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg`<br>*(200 OK, 1,298,877 B)* | `2020-...-salt-river-bay-...-reverse.jpg` | 2020-P (`mint=P`): Philadelphia (`P`) obverse preserved + 2020 Salt River Bay reverse (replaces 2017 Ozark) |
| **15** | `c336e53e-4105-44bd-8c08-f30ae0328467` (`eric.seaman@yahoo.com`) | `2013-P` Quarter (`Raw`) | `Mount Rushmore National Memorial (South Dakota)` | `...2013-...-obverse-p.jpg` / `...2010-...-mount-hood...` | `.../atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg`<br>*(200 OK, 1,867,830 B)* | `.../atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg`<br>*(200 OK, 2,032,412 B)* | `2013-...-mount-rushmore-...-reverse.jpg` | 2013-P (`mint=P`): Philadelphia (`P`) obverse preserved + 2013 Mount Rushmore reverse (replaces 2010 Mt Hood) |
| **16** | `cba5e585-758f-4b10-be7a-1a59a1f4b2e6` (`eric.seaman@yahoo.com`) | `2018-P` Quarter (`Raw`) | `Cumberland Island National Seashore (Georgia)` | `...2018-...-obverse-philadelphia.jpg` / `...2016-...-cumberland-gap...` | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg`<br>*(200 OK, 2,309,513 B)* | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg`<br>*(200 OK, 2,157,454 B)* | `2018-...-cumberland-island-...-reverse.jpg` | 2018-P (`mint=P`): Philadelphia (`P`) obverse preserved + 2018 Cumberland Island reverse (replaces 2016 Gap) |
| **17** | `d7fec246-983f-40de-8b58-854f59460bce` (`eric.seaman@yahoo.com`) | `2018-P` Quarter (`Raw`) | `Block Island National Wildlife Refuge (Rhode Island)` | `...2018-...-obverse-philadelphia.jpg` / `...2017-...-ellis-island...` | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg`<br>*(200 OK, 2,309,513 B)* | `.../atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg`<br>*(200 OK, 2,242,129 B)* | `2018-...-block-island-...-reverse.jpg` | 2018-P (`mint=P`): Philadelphia (`P`) obverse preserved + 2018 Block Island reverse (replaces 2017 Ellis Island) |
| **18** | `Wq2UhSQNs67u34VFJDaI` (`eric.seaman@yahoo.com`) | `1962` (P) Cent (`Gem Proof`) | `Abraham Lincoln` | `...NNC-US-1909-1C...LEFT.jpg` / `...2008-lincoln-one-cent-reverse...` | **MISSING IN GCS** — Stage no-mintmark `1962` Proof Lincoln Cent obverse at EXECUTE *(do NOT use `1962-D` business strike)* | `.../Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg`<br>*(200 OK, 608,070 B)* | `United_States_penny_2C_reverse.jpg` | 1962 (P) Gem Proof: Memorial reverse (`608,070 B`); no-mintmark 1962 Proof obverse staged (0 `1962-D` substitution) |
| **19** | `UOBfFO2mqgLg86NSsyss` (`eric.seaman@yahoo.com`) | `2019-W` Quarter Dollar (`Circulated`) | `San Antonio Missions` | `...1932-george-washington-quarter-obverse.jpg` / `...2019-...-san-antonio-missions...reverse.jpg` | `.../atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg`<br>*(200 OK, 2,133,544 B; `2019-W` obverse not in GCS — flagged)* | `.../atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg`<br>*(200 OK, 2,116,020 B)* | `2019-...-san-antonio-missions-...-reverse.jpg` | 2019-W San Antonio Missions: restore San Antonio Missions reverse (`2,116,020 B`); replace 1932 obverse |
| **20** | `3f437576-fa20-4ef1-95c0-01e10eaf43a8` (`eric.seaman@yahoo.com`) | `2017-P` Quarter (`Raw`) | `Effigy Mounds National Monument (Iowa)` | `...2011-...-obverse-p.jpg` / `...2017-...-effigy-mounds...reverse.jpg` | `.../atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg`<br>*(200 OK, 712,711 B — undated ATB `P` obverse)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg`<br>*(200 OK, 2,062,235 B)* | `2017-...-effigy-mounds-...-reverse.jpg` | 2017-P (`mint=P`): keep Philadelphia (`P`) undated ATB obverse (`712,711 B`, never `obverse-d.webp`) + 2017 reverse |
| **21** | `6ff959a0-26f8-451f-aa4c-064b5ef68939` (`eric.seaman@yahoo.com`) | `2017-P` Quarter (`Raw`) | `Frederick Douglass National Historic Site (District of Columbia)` | `...2011-...-obverse-p.jpg` / `...2017-...-frederick-douglass...reverse.jpg` | `.../atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg`<br>*(200 OK, 712,711 B — undated ATB `P` obverse)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg`<br>*(200 OK, 2,127,779 B)* | `2017-...-frederick-douglass-...-reverse.jpg` | 2017-P (`mint=P`): keep Philadelphia (`P`) undated ATB obverse (`712,711 B`, never `obverse-d.webp`) + 2017 reverse |
| **22** | `96eeb7b6-6c4e-4a62-bb8e-80b69706d915` (`eric.seaman@yahoo.com`) | `2010-P` Quarter (`Raw`) | `Yellowstone National Park (Wyoming)` | `...2011-...-obverse-p.jpg` / `...2010-...-yellowstone...reverse.jpg` | `.../atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg`<br>*(200 OK, 712,711 B — undated ATB `P` obverse)* | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg`<br>*(200 OK, 592,295 B)* | `2010-...-yellowstone-...-reverse.jpg` | 2010-P (`mint=P`): keep Philadelphia (`P`) undated ATB obverse (`712,711 B`, never `obverse-d.webp`) + 2010 reverse |
| **23** | `ab35ab5d-d51f-4b9c-bc94-ff87def52bc6` (`eric.seaman@yahoo.com`) | `2017-D` Quarter (`Raw`) | `George Rogers Clark National Historical Park (Indiana)` | `...2010-...-obverse-d.webp` / `...2017-...-george-rogers-clark...reverse.jpg` | `.../atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`<br>*(200 OK, 166,278 B — undated ATB `D` obverse)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg`<br>*(200 OK, 2,118,832 B)* | `2017-...-george-rogers-clark-...-reverse.jpg` | 2017-D (`mint=D`): Denver (`D`) undated ATB obverse (`166,278 B`) + 2017 reverse |
| **24** | `b785236f-ca64-4461-9ee4-01cad3a7d60e` (`eric.seaman@yahoo.com`) | `2017-P` Quarter (`Raw`) | `Ozark National Scenic Riverways (Missouri)` | `...2011-...-obverse-p.jpg` / `...2017-...-ozark-riverways...reverse.jpg` | `.../atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg`<br>*(200 OK, 712,711 B — undated ATB `P` obverse)* | `.../atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg`<br>*(200 OK, 2,172,068 B)* | `2017-...-ozark-riverways-...-reverse.jpg` | 2017-P (`mint=P`): keep Philadelphia (`P`) undated ATB obverse (`712,711 B`, never `obverse-d.webp`) + 2017 reverse |
| **25** | `0a2bc793-8d62-47c3-88cd-7a5b9be434ba` (`eric@numista.ai`) | `2026` Set (`Uncirculated`) | `Untitled` (2026 Uncirculated Coin Set) | `None` / `None` | `.../user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg`<br>*(200 OK, 336,365 B)* | `.../user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg`<br>*(200 OK, 265,821 B)* | `26rj_e.jpg` | Real CSV doc `0a2bc793...` (`eric@numista.ai`): P-lens (`26rj_e.jpg`) obverse & D-lens (`26rj_b.jpg`) reverse |
| **26** | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` (`eric@numista.ai`) | `2026` Dollar (`Enhanced Unc`) | `Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)` | `None` / `None` | `.../us_mint_official/2026_products/26xe_a.webp`<br>*(200 OK, 216,358 B)* | `.../us_mint_official/2026_products/26XE_image_2.jpg`<br>*(200 OK, 240,850 B)*<br>*(Staged `26xe_b.webp` 245,878 B at EXECUTE)* | `26xe_a.webp` | Real CSV doc `be10e44c...` (`eric@numista.ai`): 2026-S Morgan obverse & eagle reverse |
| **27** | `faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c` (`eric@numista.ai`) | `2026-D` Dollar (`Ungraded`) | `Untitled` (2026-D Semiquincentennial $1) | `None` / `None` | `.../us_mint_official/2026_products/26sqrp_b.webp`<br>*(200 OK, 179,722 B)* | `.../us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg`<br>*(200 OK, 245,212 B)* | `26sqrp_b.webp` | Real CSV doc `faa5b1cf...` (`eric@numista.ai`): Trump portrait obverse & Liberty reverse |
| **28** | `2fa325166682b70aa0d64da45786c94aa4742d21` (`eric@numista.ai` & `eric.seaman@yahoo.com`) | `2023` Set (`Proof`) | `Untitled` (2023 Silver Proof Set `23RH`) | `None` / `None` | **MISSING IN GCS** — Stage `23rh_b.webp` (`226,854 B`, `1200x1049`, `MD5=8a2060d0ca5987b0faf0d8828ece365f`) to `.../us_mint_official/2023_products/23rh_b.webp` at EXECUTE | **MISSING IN GCS** — Stage `23rh_c.webp` (`161,734 B`, `1200x1050`, `MD5=08f5b5aaf698936913e2a24743dbdea5`) or `23rh_b.webp` to `.../us_mint_official/2023_products/` at EXECUTE | `23rh_b.webp` | Real CSV doc `2fa32516...`: 2023 Silver Proof Set lens staged under `2023_products/` (NEVER `2026_products/` or `26RH`) |

> **Accounting Note for `eric@numista.ai`'s 5th CSV Row (`977b5ab2-06a3-41ce-b101-8b2ceee7e6b5`):**
> `eric@numista.ai` has 5 total rows in `ERIC_ACCOUNT_252_AUDIT_20261031.csv`: Rows 25–28 above (`0a2bc793`, `be10e44c`, `faa5b1cf`, `2fa32516`) plus `977b5ab2-06a3-41ce-b101-8b2ceee7e6b5` (`2025-D` Quarter Dollar `Dr. Vera Rubin - Dark Matter`, `MS-65`, `defect_summary = PASS`), which already stores Eric's own microscope photos (`2025_Vera_Rubin_American_Women_Quarter_Obverse_20261001_1933.jpg` and `..._Reverse_20261001_1933.jpg`) and must NOT be overwritten.

---

## 4. Exact Fix-Only Checklist for `R2.8.6`

1. **Replace Section 4 (`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:372-401`)** with the 28-row script-generated table in Section 3 above (resolving `MF-A`, `MF-B`, `MF-C`, `MF-D`, and `MF-E` simultaneously).
2. **Update Section 2.1 (`FAILFIX_PLAN_NET-647_R2.8.5_20261031.md:60`) and Gate 4 (`:678-693`)** so `23rh_b.webp` (`226,854 B`, `MD5 = 8a2060d0ca5987b0faf0d8828ece365f`) is staged to `gs://numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp` (a `2023` path, not `2026_products/`).
3. **Include the generating script output in Section 4.1** confirming `0` missing doc IDs against `ERIC_ACCOUNT_252_AUDIT_20261031.csv` and `0` byte-count or mint-mark mismatches.
