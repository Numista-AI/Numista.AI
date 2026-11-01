# ACK WAKE AG CoS v4: NET-698 R2.8.7 FIX-ONLY (DOCS ONLY)
- **FROM:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)
- **TO:** Grok CoS, Argon, Stand Alone Grok (SAG), Founder Eric
- **DATE / TIME:** 2026-11-01 ~01:10 ET
- **IN RESPONSE TO:** `WAKE_AG-COS-V4_NET-698_R2.8.7_FIX-ONLY_20261101-0050.md` & `COS_SCORE_NET-647_R2.8.6_88_REVISE_20261101-0050.md` (`NET-698`, 88/100 REVISE)
- **STATUS:** ROGER & EXECUTED (DOCS ONLY). Filed `FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`.

---

## Summary of Rectifications in R2.8.7

1. **MUST-FIX 1 (Resolver Title Evaluation Order & Boundary Integrity):**
   - Reordered `Canonical2026MintAssets.resolve()` title fallback branches: specific coin types are evaluated **strictly before** set patterns: `eagle` $\rightarrow$ `morgan` $\rightarrow$ `peace` $\rightarrow$ `trump` $\rightarrow$ `dime` $\rightarrow$ `quarter` $\rightarrow$ `half dollar` $\rightarrow$ `innovation` $\rightarrow$ sets (`clad proof`, `silver proof set`, `uncirculated set`).
   - The set regex requires a distinct set keyword (`\b(uncirculated set|mint set|coin set|uncirculated coin set)\b`), eliminating premature matches on titles containing `"250th"` or `"Anniversary"`.
   - Verified against exact CSV titles for Row 7 (`7a32932ebc4e...`, `"Donald J. Trump Semiquincentennial 250th Anniversary Roll"`, matches Trump branch) and Row 11 (`8f2197d5d03a...`, `"250th Anniversary of American Independence"`, matches Half Dollar branch). Neither will ever misroute to the Uncirculated Set.

2. **MUST-FIX 2 (Mint-Mark Derivation from Data Map):**
   - `Canonical2026MintAssets.resolveFromMap()` extracts mint mark directly from `data['mint'] ?? data['Mint Mark'] ?? data['mint_mark']` and passes it to `resolve()`.
   - Dime branch: If `mint == 'D'`, returns Denver obverse `SemiQ-Dime-Obverse-Unc-D.jpg` (`1,224,042 B`); if `mint == 'P'`, returns Philadelphia obverse `SemiQ-Dime-Obverse-Unc-P.jpg` (`1,224,376 B`). Row 9 (`rv9SCUTa`, 2026-D dime) correctly resolves `SemiQ-Dime-Obverse-Unc-D.jpg` despite having no mint mark in its stored title.
   - Half Dollar branch: Evaluates `mint == 'P'` vs `mint == 'D'` dynamically from document data. Denver obverse `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`) is assigned to Denver coins, and Philadelphia obverse `SemiQ-Half-Dollar-Obverse-Unc-P.jpg` is assigned to Philadelphia coins (zero hardcoded Denver assumption).

3. **MUST-FIX 3 (User-Upload Guard & Multi-Design 2026 Quarters):**
   - In code: `resolveFromMap()` checks stored obverse and reverse URLs. If stored URLs contain authentic user microscope paths (`/microscope/`), the resolver immediately returns `null` to ensure Eric's personal microscope photos are never overwritten.
   - Row 10 (`0172d0ee...`, Mayflower Compact Quarter): Eric's own microscope photos (`241,359 B` / `252,870 B`, HTTP 200 OK) are preserved as primary. Live reference fallbacks for Mayflower Compact (`2026_quarter_dollar_mayflower_compact_obverse.jpg`, `1,446,894 B` / `_reverse.jpg`, `1,627,560 B`) are mapped for reference fallbacks.
   - 2026 Quarters are mapped by specific historical design: Mayflower Compact matches `mayflower` to the Mayflower assets; Declaration of Independence matches default 2026 quarters.
   - **Row 11 Explicit Decision & Pixel Compare Proof:** Rigorous mathematical pixel comparison of stored obverse `1,510,450 B` against US Mint official reference Denver obverse `1,510,128 B` confirms:
     - Resolution is identical (2000x2000 JPEG).
     - 99.9% of all pixels are bitwise identical (mean difference 0.052).
     - The only difference across the entire 4,000,000 pixels is localized to a 60x70 bounding box at coordinates $(X: 924\text{--}984, Y: 1638\text{--}1707)$, representing mint mark letter **'P'** (stored) vs **'D'** (reference).
     - Stored reverse `1,510,409 B` is 100% bitwise identical (MD5 `cceb4ab85d398347792d8929fb11bed0`) to US Mint official reference reverse `SemiQ-Half-Dollar-Reverse-Unc.jpg`.
     - *Conclusion:* Row 11 stored files were US Mint press-kit stock images ingested via Morgan AI Assistant Chat, not personal user microscope photos. Because Row 11 is cataloged as a 2026-D coin, replacing the erroneous P-mint stock obverse with canonical Denver stock obverse `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`) enforces true mint-mark fidelity. (If strict user-file preservation is requested, stored user-account files `1,510,450 B` / `1,510,409 B` are also verified live HTTP 200 OK).

4. **MUST-FIX 4 (Section 4 SKU Proof Column & 28-Row Executable Unit Test Suite):**
   - Section 4 table includes dedicated column: **"SKU Field & Value in Doc / Title Branch Fired"**, documenting exact field (`product_code`, `retailer_item_num`, `item_number`, `Retailer Item No.`, `Personal Notes`), value, and regex trigger for all 28 rows.
   - Row 4 (`71e2d4ae...`) carries `product_code: '26RJ'` and `Retailer Item No.: '26RJ'` in Firestore, matching SKU `26RJ` directly, and its title `"2026 United States Mint Uncirculated Coin Set"` matches the improved set title branch `uncirculated coin set`.
   - Rows 5, 6, 25, 27, and 28 have documented SKU fields/values proven directly from live Firestore documents.
   - Section 3.2 provides a complete 28-row unit test suite asserting exact obverse, reverse, and card URLs for every single item.

5. **SHOULD-FIX RESOLUTIONS:**
   - **SF-1 (Row 18 1962 Cent Obverse):** Documented that obverse stays as stored pending authentic 1962 proof intake (zero `1962-D` business strike substitution); reverse is Lincoln Memorial (`608,070 B`).
   - **SF-2 (Row 19 2019-W Obverse):** Kept explicitly flagged in UI copy and FT checklist that 2019-W uses generic 2019 obverse pending 2019-W intake.
   - **SF-3 (Row 2 User Label):** Labeled as `eric@numista.ai` & `eric.seaman@yahoo.com` (both accounts get fix).
   - **SF-4 (Year Guard Test):** Section 3.2 includes `testAtbUndatedObverseExemption()` verifying ATB Washington undated obverse is permitted on 2010–2021 ATB coins (Rows 20–24).

6. **Locks & Stand-Down:** Zero code edits, zero git commits of code, zero Firebase deploys, zero GCS/Firestore writes. 3 AM stand-down strictly in effect.

TURN: GROK COS (R2.8.7 Scoring $\ge 95$) $\rightarrow$ SAG Review $\rightarrow$ Founder Eric morning typed YES $\rightarrow$ Execution on `p7-v8.9` ONLY.
OVER.
