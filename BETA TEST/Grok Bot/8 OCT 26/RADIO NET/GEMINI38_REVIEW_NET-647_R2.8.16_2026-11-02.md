# GEMINI 3.8 TECHNICAL REVIEW: `FAILFIX_PLAN_NET-647_R2.8.16_20261102.md`

- **Review ID:** `GEMINI38_REVIEW_NET-647_R2.8.16_2026-11-02`
- **Track / NET:** `NET-647` (Vault / Mint Order / Coin Image Rendering & Official US Mint Reference Asset Pipeline) / `BATON_NET-741`
- **Plan Under Review:** [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md)
- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)
- **Date:** 2026-11-02
- **Git Baseline Verified:** `origin/dev` (`01a03f90`)
- **Score:** **`76 / 100 — REVISE`**
- **Execution Gate:** **HOLD (`NO EXECUTE`)** — Do not modify production code, do not run `git commit` or `git push`, do not write to Firestore or GCS until `R2.8.17` resolves `MF-1` through `MF-4` below and Eric types `YES`.

---

## 1. Executive Summary & Scoring Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Dart Code & Unit Test Correctness (`§3.1` & `§3.2`)** | 30 | **28 / 30** | `R2.8.16` cleanly resolved all 3 sub-items of `R2.8.15 MF-3`: removed `$notes` from `extractSku` (`line 201`), nulled out the 4 self/cross-duplicate `fallbackReverseUrl` entries (`26SQRP`, `26RH`, `1962-LINCOLN-1C`, `ATB`), added the `Row 11 Reference Resolution: 2026-HALF-D Catalog Lookup` test (`lines 1372–1387`), and executed `flutter test scratch/canonical_mint_asset_service_test.dart` (`44/44 PASS` at `lines 1703–1979`). Deducted 2 pts because `CanonicalMintAssetPair` and `CanonicalMintAssetService` were pasted twice (`lines 98–645` in `§3.1` and again at `lines 660–1206` inside `§3.2` — see `MF-4`). |
| **2. Section 4 28-Document Table Integrity (`§4`)** | 25 | **12 / 25** | A regex/column-replacement script used to generate `R2.8.16` corrupted **17 of the 28 rows** in the Section 4 table (`lines 1986–2013`): on Rows `01, 02, 07, 13–24, 26, 27`, it overwrote or appended the fallback changes into **column 8 (`reverseUrl`)** instead of **column 9 (`Verified Fallbacks`)**, leaving the stale/duplicate fallback paths in column 9! On Row `28` (`23RH`), it deleted the empty `Theme / Subject` cell (`col 6`), shifting every subsequent column left by 1 cell. And on Row `11` (`2026-HALF-D`), column 9 lists unverified byte sizes (`1,510,128 B` and `1,510,409 B`) instead of the live GCS sizes (`1,341,259 B` and `1,603,328 B`) (`MF-1`). |
| **3. Section 4.1.3 GCS Census Completeness & Accuracy (`§4.1.3`)** | 20 | **13 / 20** | While `§4.1.1` (`lines 2021–2028`), `§8` (`lines 2357–2390`), and `§9.2 Gate 6` (`line 2442`) were properly updated (`R2.8.15 MF-4`), `§4.1.3` (`lines 2048–2163`) was copied from the unverified `R2.8.14` table: (a) it is **missing** `reference_library/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp` (`154,614 B`, `md5: 5752ab82ee56301b9244ca4718da579f`, `HTTP 200 LIVE`), which is used by `2026-DIME-D` in `§3.1` (`line 425`), `§3.2` (`line 1315`), and `§4 Row 09` (`line 1994`), and (b) **7 rows** (`Rows 029, 043, 047, 052, 059, 060, 062, 092`) have stale byte sizes/MD5s from `R2.8.14` that directly contradict `§4.1.1` (`lines 2025–2026`) and live GCS (`MF-2`). |
| **4. Document Structure & Header Hygiene (`§1` & EOF)** | 15 | **13 / 15** | The document title and header (`lines 1, 3, 8, 11, 22, 23`) still say `R2.8.15`, while the new `R2.8.16` Section 1 matrix was accidentally appended to the very bottom of the file *after* `**END PLAN R2.8.16**` (`lines 2448–2460`) (`MF-3`). |
| **5. Repository Integration & Rule 6(a) Verbatim Cites (`§7`)** | 10 | **10 / 10** | All 5 target integration points in `§7` (`lines 2215–2352`) are cited with 100% verbatim lines matching `git show 01a03f90:<path>`. |
| **TOTAL** | **100** | **`76 / 100`** | **Verdict: `REVISE` (`R2.8.17` required before execution approval)** |

---

## 2. What `R2.8.16` Fixed Properly (Verified RESOLVED)

1. **`R2.8.15 MF-3(a)` (`extractSku` removed `$notes`):**
   - Verified at [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:201`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L194-L202):
     ```dart
     final combined = '$explicitSku $cert $name $series'.toUpperCase();
     ```
2. **`R2.8.15 MF-3(b)` (4 Self/Cross-Duplicate `fallbackReverseUrl` Entries Nulled Out in Dart Code & Tests):**
   - Verified in `§3.1` (`lines 256, 304, 344, 360`) and `§3.2` (`lines 1255, 1344–1369`) that `26SQRP`, `26RH`, `1962-LINCOLN-1C`, and `ATB` now have `fallbackReverseUrl: null`.
3. **`R2.8.15 MF-3(c)` (Dedicated Unit Test for `2026-HALF-D` & `44/44 PASS` Execution Output):**
   - Verified at [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:1372-1387`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L1372-L1387) and verbatim `flutter test` run (`00:00 +44: All tests passed!`) at `lines 1703–1979`.
4. **`R2.8.15 MF-4` (`§4.1.1`, `§8`, and `§9.2 Gate 6` Updated):**
   - `§4.1.1` (`lines 2021–2028`), `§8` (`lines 2357–2390`), and `§9.2 Gate 6` (`line 2442`, citing `origin/dev 01a03f90`) are clean and consistent.

---

## 3. Mandatory Fixes Required for `R2.8.17` (`MF-1` through `MF-4`)

### `MF-1` (CRITICAL — Section 4 Table Rows `01, 02, 07, 11, 13–24, 26, 27, 28` Were Corrupted in the Wrong Column by a Regex Script)

In [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:1984-2013`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L1984-L2013), the Section 4 table has 10 columns:
`| Row | Firestore Doc ID | SKU / Lookup Key | Document Name | Mint | Theme / Subject | Canonical obverseUrl (Bytes / MD5) | Canonical reverseUrl (Bytes / MD5) | Verified Fallbacks (fallbackObverseUrl / fallbackReverseUrl) | Pre-Flight Gate Status |`

When `AG CoS v4` ran a script to update column 9 (`Verified Fallbacks`), the script modified **column 8 (`Canonical reverseUrl`)** instead of **column 9 (`Verified Fallbacks`)** on 16 rows, deleted a cell on Row 28, and put wrong byte counts on Row 11:

1. **Row 01 (`line 1986`, `26EA`):**
   - Verbatim corrupted line in `R2.8.16`:
     ```markdown
     | 01 | `01_26EA_ase_proof` | `26EA` | American Eagle 2026 One Ounce Silver Proof Coin | `W` | — | `reference_library/us_mint_official/2026_products/26EA_image_1.jpg` (`144,335 B` (`md5: 76de11b529…`)) | `reference_library/us_mint_official/2026_products/26ea_a.webp` / `reference_library/us_mint_official/2026_products/26ea_b.webp` (`164,146 B`, `md5: 62ad11e997...`, `STAGED Gate 4`) | `reference_library/us_mint_official/2026_products/26ea_a.webp` / `reference_library/us_mint_official/2026_products/26EA_image_3.jpg` | `STAGED (Gate 4)` (`26ea_b.webp`) |
     ```
   - **Fix required in `R2.8.17`:** Restore column 8 (`Canonical reverseUrl`) to `` `reference_library/us_mint_official/2026_products/26EA_image_2.jpg` (`139,910 B` (`md5: cfa91a545c…`)) ``, and put `` `reference_library/us_mint_official/2026_products/26ea_a.webp` (`180,012 B`, `md5: 800051ab50…`, `LIVE`) / `reference_library/us_mint_official/2026_products/26ea_b.webp` (`164,146 B`, `md5: 62ad11e997…`, `STAGED Gate 4`) `` in column 9 (`Verified Fallbacks`).

2. **Rows 02 & 26 (`lines 1987, 2011`, `26XE`):**
   - Verbatim corrupted line in `R2.8.16` (`line 1987`):
     ```markdown
     | 02 | `02_26XE_morgan_peace_2coin_uncirc` | `26XE` | Morgan and Peace 2026 Two-Coin Uncirculated Dollar Set | `P` | — | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`263,401 B` (`md5: 075a5159ff…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` / `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`) | `reference_library/us_mint_official/2026_products/26xe_a.webp` / `reference_library/us_mint_official/2026_products/26XE_image_1.jpg` | `STAGED (Gate 4)` (`26xe_b.webp`) |
     ```
   - **Fix required in `R2.8.17` (both Row 02 and Row 26):** Restore column 8 (`Canonical reverseUrl`) to `` `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) ``, and put `` `reference_library/us_mint_official/2026_products/26xe_a.webp` (`215,912 B`, `md5: 8748b11859…`, `LIVE`) / `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a…`, `STAGED Gate 4`) `` in column 9 (`Verified Fallbacks`).

3. **Rows 07 & 27 (`lines 1992, 2012`, `26SQRP`):**
   - Verbatim corrupted line in `R2.8.16` (`line 1992`):
     ```markdown
     | 07 | `07_26SQRP_quarters_silver_proof` | `26SQRP` | United States Mint Semiquincentennial Quarters 2026 Silver Proof Set | `S` | — | `reference_library/us_mint_official/2026_products/26sqrp_a.webp` (`159,492 B` (`md5: 601b6ba11d…`)) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` / `None` (null - duplicate eliminated) | `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` / `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` | `HTTP 200 LIVE` |
     ```
   - **Fix required in `R2.8.17` (both Row 07 and Row 27):** Restore column 8 (`Canonical reverseUrl`) to `` `reference_library/us_mint_official/2026_products/26sqrp_b.webp` (`179,722 B` (`md5: dfeee8a47f…`)) ``, and put `` `reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` (`201,568 B`, `md5: 19b5c5b71f…`) / `None` (`null` — duplicate eliminated) `` in column 9 (`Verified Fallbacks`).

4. **Row 11 (`line 1996`, `2026-HALF-D`):**
   - Verbatim line in `R2.8.16`:
     ```markdown
     | 11 | `11_1975_roosevelt_10c_p` | `1975-ROOSEVELT-10C` | 1975 P Roosevelt Dime | `P` | — | `reference_library/us_mint_official/circulating_heads_tails/dime-heads.jpg` (`35,705 B` (`md5: a9d045e132…`)) | `reference_library/us_mint_official/circulating_heads_tails/dime-tails.jpg` (`42,571 B` (`md5: 4cfac57933…`)) | `None` / `None` *(Note: `2026-HALF-D` verified in `§3.1`/`§3.2`: `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` [`1,510,128 B`] / `SemiQ-Half-Dollar-Reverse-Unc.jpg` [`1,510,409 B`])* | `HTTP 200 LIVE` |
     ```
   - **Fix required in `R2.8.17`:** Update the note's byte sizes on Row 11 to match live GCS and `§4.1.1`: `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` [`1,341,259 B`, `md5: 7a3e675fa0…`] / `SemiQ-Half-Dollar-Reverse-Unc.jpg` [`1,603,328 B`, `md5: c80e8f5829…`].

5. **Rows 13–24 (`lines 1998–2009`, `ATB` & `1962-LINCOLN-1C`):**
   - Verbatim corrupted line in `R2.8.16` (e.g., `line 1998`):
     ```markdown
     | 13 | `13_atb_2010_hot_springs` | `ATB` | 2010 P Hot Springs Quarter | `P` | `Hot Springs` | `reference_library/bulk_programs/quarter_atb/2010-atb-hot-springs-uncirculated-obverse-p.jpg` (`62,253 B` (`md5: 25f6d1ae62…`)) | `reference_library/bulk_programs/quarter_atb/2010-atb-hot-springs-uncirculated-reverse.jpg` (`70,926 B` (`md5: 8055e185b0…`)) / `None` (null - duplicate eliminated) | `reference_library/bulk_programs/quarter_atb/2010-america-the-beautiful-quarters-coin-proof-obverse.webp` / `reference_library/bulk_programs/quarter_atb/2010-atb-hot-springs-uncirculated-reverse.jpg` | `HTTP 200 LIVE` |
     ```
   - **Fix required in `R2.8.17` (all of Rows 13–24):** Remove `/ None (null - duplicate eliminated)` from the end of column 8 (`Canonical reverseUrl`), and replace the duplicate reverse URL in column 9 (`Verified Fallbacks`) with `None` (`null` — duplicate eliminated).

6. **Row 28 (`line 2013`, `23RH`):**
   - Verbatim corrupted line in `R2.8.16`:
     ```markdown
     | 28 | `user_mint_order_item_3` | `23RH` | 2023 Silver Proof Set | `S` | `reference_library/us_mint_official/2023_products/23rh_a.webp` (`255,442 B` (`md5: de5d460e62…`)) | `reference_library/us_mint_official/2023_products/23rh_b.webp` (`241,654 B` (`md5: 8d95823b56…`)) | `reference_library/us_mint_official/2023_products/23rh_c.webp` (`218,412 B`, `md5: 4e1299a87c...`, `STAGED Gate 4`) / `reference_library/us_mint_official/2023_products/23rh_d.webp` (`198,334 B`, `md5: 9b7781c34a...`, `STAGED Gate 4`) | `reference_library/us_mint_official/2023_products/23rh_c.webp` (STAGED) / `reference_library/us_mint_official/2023_products/23rh_d.webp` (STAGED) | `STAGED (Gate 0)` |
     ```
   - **Fix required in `R2.8.17`:** Restore the `| — |` cell in column 6 (`Theme / Subject`), keep `23rh_a.webp` in column 7, `23rh_b.webp` in column 8, `23rh_c.webp` / `23rh_d.webp` in column 9, and `STAGED (Gate 4)` in column 10:
     ```markdown
     | 28 | `user_mint_order_item_3` | `23RH` | 2023 Silver Proof Set | `S` | — | `reference_library/us_mint_official/2023_products/23rh_a.webp` (`255,442 B` (`md5: de5d460e62…`)) | `reference_library/us_mint_official/2023_products/23rh_b.webp` (`241,654 B` (`md5: 8d95823b56…`)) | `reference_library/us_mint_official/2023_products/23rh_c.webp` (`218,412 B`, `md5: 4e1299a87c…`, `STAGED Gate 4`) / `reference_library/us_mint_official/2023_products/23rh_d.webp` (`198,334 B`, `md5: 9b7781c34a…`, `STAGED Gate 4`) | `STAGED (Gate 4)` |
     ```

---

### `MF-2` (MAJOR — Section 4.1.3 Census Table Missing `2026-semiq-dime-obverse-unc-d.webp` and Has Stale `R2.8.14` Byte/MD5 Values on 7 Rows)

In [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:2048-2163`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L2048-L2163), `AG CoS v4` pasted the 114-row census table from `R2.8.14` instead of using the verified live GCS values from `R2.8.13`/`R2.8.15`:

1. **Missing active asset `reference_library/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp`:**
   - Used as `fallbackObverseUrl` for `2026-DIME-D` in `§3.1` (`line 425`), `§3.2` (`line 1315`), and `§4 Row 09` (`line 1994`), and verified `HTTP 200 LIVE` in GCS (`154,614 B`, base64 MD5 `V1Krgu5WMBuSRMpHGNpXnw==`, hex MD5 `5752ab82ee56301b9244ca4718da579f`).
   - Meanwhile, `Row 023` (`line 2072`, `reference_library/bulk_programs/quarter_atb/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`) is not referenced anywhere in `CanonicalMintAssetService`.
   - **Fix required in `R2.8.17`:** Either replace unused `Row 023` with `reference_library/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp` (`154,614 B`, `V1Krgu5WMBuSRMpHGNpXnw==`, `5752ab82ee56301b9244ca4718da579f`, `HTTP 200 LIVE`) to maintain 114 active rows, or add it as Row 115 and update the active total accordingly.
2. **Stale/Wrong Byte & MD5 Values on Rows `029, 043, 047, 052, 059, 060, 062, 092`:**
   - Specifically, Rows `059`, `060`, and `062` (`lines 2108, 2109, 2111`) directly contradict `§4.1.1` (`lines 2025–2026`) and live GCS:
     - **Row 059 (`line 2108`, `SemiQ-Half-Dollar-Obverse-Unc-D.jpg`):** `§4.1.3` says `1,510,128` / `74Kv0kpcTut0kpdY0LUukQ==` / `ef82afd24a5c4eeb74947958b0552e91`, whereas `§4.1.1` (`line 2025`) and live GCS are `1,341,259` / `ej5nX6Aqsb...` (`ea9b9f756a816e87c8d39b963d93da7` / `7a3e675fa02ab1ba430e27e963d93da7`).
     - **Row 060 (`line 2109`, `SemiQ-Half-Dollar-Reverse-Unc.jpg`):** `§4.1.3` says `1,510,409` / `zOtKuF05g0d5LZkp+xG+0A==` / `cceb4ab85d398347792d8929fb11bed0`, whereas `§4.1.1` (`line 2026`) and live GCS are `1,603,328` / `yA6FWCmg31xyq/tlNhlT2Q==` / `c80e8f5829a0df5c72abfb65361534a9`.
     - **Row 062 (`line 2111`, `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`):** `§4.1.3` says `1,510,450` / `7AU0fKvzsbSiYqybZmMxOFs=` / `ec05347cabf3b134a262ac9f6631385b`, whereas `§4.1.1` (`line 2025`) and live GCS are `1,477,632` / `tXfrUWjaXbq++EjBa7am4Q==` / `b577eb5168da5dbabef488116bb6a6e1`.
     - **Row 029 (`line 2078`, `2012-atb-el-yunque-uncirculated-obverse-p.jpg`), Row 043 (`line 2092`, `2014-atb-everglades-uncirculated-obverse-p.jpg`), Row 047 (`line 2096`, `2015-atb-blue-ridge-parkway-uncirculated-obverse-p.jpg`), Row 052 (`line 2101`, `2026-semiq-dime-obverse-unc-p.webp`), and Row 092 (`line 2141`, `26rj_a.webp`):** Update to the verified GCS byte/MD5 values from `R2.8.15 §4.1.3` (`lines 1502–1615 of R2.8.15`):
       - `2012-atb-el-yunque-uncirculated-obverse-p.jpg`: `60,912 B`, `e028a21590b84479221779df20389f55`
       - `2014-atb-everglades-uncirculated-obverse-p.jpg`: `66,319 B`, `4f86b274b545cf7eb5a3d74b7aa240f3`
       - `2015-atb-blue-ridge-parkway-uncirculated-obverse-p.jpg`: `69,854 B`, `a4d4c68f61487a743a4084c47ff45880`
       - `2026-semiq-dime-obverse-unc-p.webp`: `154,882 B`, `2d19be417f70b5c717908c7a37e583ec`
       - `26rj_a.webp`: `214,322 B`, `IEYr822kso75qdp46xcTTg==`, `20462bf36da4b28ef9a9da78eb17134e`

---

### `MF-3` (MAJOR — Document Header Still Says `R2.8.15` and the `R2.8.16` Executive Summary Matrix Was Appended After `**END PLAN R2.8.16**` at the Bottom of the File)

1. Look at [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:1-25`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L1-L25):
   - `line 1`: `# FAIL-FIX PLAN NET-647 R2.8.15: Canonical Mint Asset Service, 28-Document Firestore Recovery & Reference Asset Staging`
   - `line 3`: `- **Plan ID:** FAILFIX_PLAN_NET-647_R2.8.15_20261102`
   - `line 8`: `- **Supersedes:** FAILFIX_PLAN_NET-647_R2.8.14_20261102.md`
   - `line 22`: `R2.8.15 resolves every mandatory finding:`
2. And look at [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:2448-2460`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L2448-L2460) at the very end of the file:
   ```markdown
   **END PLAN R2.8.16**## 1. Executive Summary & Review Deliberation Matrix
   ...
   **END PLAN R2.8.16**
   ```
- **Fix required in `R2.8.17`:** Update the header (`lines 1–25`) to `R2.8.17`, place the `R2.8.17` deliberation matrix inside Section 1 (`lines 18–50`), and remove the trailing duplicate Section 1 block at the end of the file so the file ends cleanly with `**END PLAN R2.8.17**`.

---

### `MF-4` (MODERATE — Remove Duplicate 550-Line Copy of `CanonicalMintAssetService` Inside Section 3.2 `lines 660–1206`)

- In [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md:654-1216`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md#L654-L1216), `AG CoS v4` pasted the entire standalone `scratch/canonical_mint_asset_service_test.dart` file (which embeds `CanonicalMintAssetPair` and `CanonicalMintAssetService` inline at `lines 660–1206`) directly below Section 3.1 (`lines 98–645`), resulting in `CanonicalMintAssetService` appearing twice in the plan, plus duplicate comment headers at `lines 646–648`, `656–658`, and `1208–1214`.
- **Fix required in `R2.8.17`:** In Section 3.2 (`test/services/canonical_mint_asset_service_test.dart`), replace the duplicated `lines 656–1213` class definition with `import 'package:numista_ai/services/canonical_mint_asset_service.dart';` followed immediately by `void main() { ... }` (and update the `group(...)` description on `line 1216` from `'CanonicalMintAssetService — 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests'` to `'CanonicalMintAssetService — 28 Live Firestore Document Tests + 2 Reference Catalog Tests + 14 Synthetic Tracker Tests (44 Total)'`).

---

## 4. GEMINI.md Rule 6(a) Verbatim Repository Code Verification (`origin/dev 01a03f90`)

Every target integration site cited in Section 7 of `FAILFIX_PLAN_NET-647_R2.8.16_20261102.md` was verified against `git show 01a03f90:<path>`:

### 4.1 [`lib/screens/my_collection_screen.dart:6320-6366`](file:///c:/Users/ericd/Documents/MyVertexProject/lib/screens/my_collection_screen.dart#L6320-L6366)
```dart
  static const Map<String, List<String>> _mintCatalogImagesBySku = {
    '26EA': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26ea_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26EA_image_1.jpg',
    ],
    '26XE': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26xe_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26XE_image_2.jpg',
    ],
    '26MF': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26mf_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26mf_b.webp',
    ],
    '26RG': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rg_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rg_b.webp',
    ],
    '26RF': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rf_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rf_b.webp',
    ],
    '26RJ': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rj_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rj_b.webp',
    ],
    '26SQRP': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26sqrp_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26sqrp_b.webp',
    ],
    '26RH': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rh_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2026_products/26rh_b.webp',
    ],
    '25RH': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2025_products/25rh_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2025_products/25rh_b.webp',
    ],
    '24RH': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2024_products/24rh_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2024_products/24rh_b.webp',
    ],
    '23RH': [
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2023_products/23rh_a.webp',
      'https://storage.googleapis.com/numista-ai-public-assets/reference_library/us_mint_official/2023_products/23rh_b.webp',
    ],
  };
```

### 4.2 [`lib/screens/my_collection_screen.dart:3016-3023`](file:///c:/Users/ericd/Documents/MyVertexProject/lib/screens/my_collection_screen.dart#L3016-L3023)
```dart
    // ── US Mint Order Item auto-repair for stale / missing / swapped URLs ──
    final rawSku = (data['sku'] ?? data['mintSku'] ?? '').toString().trim().toUpperCase();
    final certStr = (data['certNumber'] ?? '').toString().trim().toUpperCase();
    final skuMatch = RegExp(r'\b(2[0-9][A-Z]{2,4})\b').firstMatch('$rawSku $certStr');
    final detectedSku = skuMatch?.group(1) ?? '';
    final canonicalPair = _mintCatalogImagesBySku[detectedSku];
```

### 4.3 [`lib/services/coin_image_service.dart:535-571`](file:///c:/Users/ericd/Documents/MyVertexProject/lib/services/coin_image_service.dart#L535-L571)
```dart
    // ── Priority 0: Pre-populated explicit URLs from backend / reference_library ──
    final explicitObv = coinData['obverseUrl']?.toString() ?? '';
    final explicitRev = coinData['reverseUrl']?.toString() ?? '';
    if (explicitObv.isNotEmpty && explicitObv.startsWith('http')) {
      final isBrokenCatalogUrl = explicitObv.contains('usmint.gov/on/demandware.static') ||
          explicitObv.contains('usmint.gov/wordpress') ||
          explicitObv.contains('wikimedia.org');
      if (!isBrokenCatalogUrl) {
        return {
          'obverse': explicitObv,
          'reverse': (explicitRev.isNotEmpty && explicitRev.startsWith('http'))
              ? explicitRev
              : explicitObv,
          'source': coinData['imageSource']?.toString() ?? 'US Mint Direct',
        };
      }
    }
```

### 4.4 [`lib/screens/review_hub_screen.dart:2282-2289`](file:///c:/Users/ericd/Documents/MyVertexProject/lib/screens/review_hub_screen.dart#L2282-L2289)
```dart
    final frontPath = data['obverseUrl'] as String? ??
        data['frontImageUrl'] as String? ??
        data['frontImagePath'] as String?;
    final backPath = data['reverseUrl'] as String? ??
        data['backImageUrl'] as String? ??
        data['backImagePath'] as String?;
```

### 4.5 [`numista_backend/main.py:8369-8376`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8369-L8376)
```python
        cat_obv = cat_match.get("obverse_gcs_url") or (cat_imgs[0] if len(cat_imgs) > 0 else "")
        cat_rev = cat_match.get("reverse_gcs_url") or (cat_imgs[1] if len(cat_imgs) > 1 else cat_obv)
        coin_entry = {
            "name": item.get("name", "US Mint Item"),
            "sku": sku,
            "quantity": item.get("quantity", 1),
```

---

## 5. Summary of Action Items for `AG CoS v4` (`R2.8.17`)

1. **`MF-1`:** Fix Section 4 Table (`lines 1986–2013`):
   - **Row 01 (`26EA`):** Restore `col 8` (`reverseUrl`) to `26EA_image_2.jpg` (`139,910 B`, `md5: cfa91a545c…`), and put `26ea_a.webp` / `26ea_b.webp` (`STAGED Gate 4`) in `col 9` (`Verified Fallbacks`).
   - **Rows 02 & 26 (`26XE`):** Restore `col 8` (`reverseUrl`) to `26XE_image_3.jpg` (`285,827 B`, `md5: e056a201fc…`), and put `26xe_a.webp` / `26xe_b.webp` (`STAGED Gate 4`) in `col 9` (`Verified Fallbacks`).
   - **Rows 07 & 27 (`26SQRP`):** Restore `col 8` (`reverseUrl`) to `26sqrp_b.webp` (`179,722 B`, `md5: dfeee8a47f…`), and put `MASTER_SEMIQDJT_image_2.jpg / None (null — duplicate eliminated)` in `col 9` (`Verified Fallbacks`).
   - **Row 11 (`2026-HALF-D` note):** Fix note byte counts to `1,341,259 B` (`md5: 7a3e675fa0…`) and `1,603,328 B` (`md5: c80e8f5829…`).
   - **Rows 13–24 (`ATB` & `1962-LINCOLN-1C`):** Remove `/ None (null - duplicate eliminated)` from `col 8` (`reverseUrl`) and replace the second path in `col 9` (`Verified Fallbacks`) with `None` (`null` — duplicate eliminated).
   - **Row 28 (`23RH`):** Restore the missing `| — |` cell in `col 6` (`Theme / Subject`) so columns 7, 8, 9, and 10 align properly.
2. **`MF-2`:** Fix Section 4.1.3 Census Table (`lines 2048–2163`):
   - Include `reference_library/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp` (`154,614 B`, `V1Krgu5WMBuSRMpHGNpXnw==`, `5752ab82ee56301b9244ca4718da579f`, `HTTP 200 LIVE`) (e.g. replacing unused Row 023 `2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp`).
   - Restore the verified live GCS byte sizes and MD5 hashes from `R2.8.15 §4.1.3` on Rows `029, 043, 047, 052, 059, 060, 062, 092` so `§4.1.3` matches `§4.1.1` and live GCS.
3. **`MF-3`:** Update the file header (`lines 1–25`) from `R2.8.15` to `R2.8.17`, place the `R2.8.17` Section 1 matrix at the top of the file, and delete the trailing duplicate Section 1 block after `**END PLAN...**` at the bottom of the file (`lines 2448–2460`).
4. **`MF-4`:** Remove the duplicated 550-line copy of `CanonicalMintAssetPair` and `CanonicalMintAssetService` inside Section 3.2 (`lines 656–1213`) so Section 3.2 contains only the test file imports and `void main() { ... }`.
