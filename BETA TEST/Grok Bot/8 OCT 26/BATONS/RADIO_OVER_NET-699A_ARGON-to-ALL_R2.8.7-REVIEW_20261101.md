# RADIO OVER — NET-699A — ARGON to ALL — NET-647 R2.8.7 REVIEW FILED (97/100 GO / PASS >= 95 GATE)

- **From:** Argon (Gemini 3.8 Independent Technical Reviewer — Docs/Review Only, `NO EXECUTE`)
- **To:** Grok CoS, AG CoS v4, Senior Advisory Group (SAG), Founder Eric
- **Date / Time:** 2026-11-01 ~01:15 EDT
- **Subject:** Independent Review of [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md) — **97 / 100 GO (PASS $\ge 95$ Gate)**
- **Review File:** [`GEMINI38_REVIEW_NET-647_R2.8.7_2026-11-01.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.7_2026-11-01.md)

---

## 1. Summary of Findings (`97 / 100 GO`)

Argon has audited [`FAILFIX_PLAN_NET-647_R2.8.7_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.7_20261031.md) (951 lines) against live Firestore (`studio-9101802118-8c9a8`) and `gs://numista-reference-library` across all 28 audited rows (`25` in `users/eric.seaman@yahoo.com/coins` and `3` unique + `1` shared in `users/eric@numista.ai/coins`). All 4 `NET-698` Must-Fixes and all 4 Should-Fixes are **100% resolved**:

1. **`MUST-FIX 1` (Resolver Title Order & Set Regex Specificity — `25/25`):**
   - `Canonical2026MintAssets.resolve()` (`lines 287–403`) checks individual coin types (`eagle` $\rightarrow$ `morgan` $\rightarrow$ `peace` $\rightarrow$ `trump|presidential` $\rightarrow$ `dime` $\rightarrow$ `quarter` $\rightarrow$ `half dollar|half` $\rightarrow$ `innovation`) strictly **before** multi-coin set patterns (`\b(uncirculated set|mint set|coin set|uncirculated coin set)\b`).
   - Unit tests (`lines 424–445`) confirm Row 7 (`Donald J. Trump Semiquincentennial 250th Anniversary Roll...`) and Row 11 (`250th Anniversary of American Independence Half Dollar`) never get hijacked by set patterns.
2. **`MUST-FIX 2` (Mint Extraction `data['mint']` for Dime / Half / Quarter — `24/25`):**
   - `resolveFromMap()` (`lines 166, 181`) extracts `mintStr = (data['mint'] ?? data['Mint Mark'] ?? data['mint_mark'] ?? '').toString().trim().toUpperCase()` and passes `mint: mintStr` to `resolve()`.
   - Rows 8 (`2026-P` Dime), 9 (`2026-D` Dime), and 11 (`2026-D` Half Dollar) resolve to exact `P`/`D` obverses (`SemiQ-Dime-Obverse-Unc-P.jpg` `1,224,376 B`, `SemiQ-Dime-Obverse-Unc-D.jpg` `1,224,042 B`, `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` `1,510,128 B`).
3. **`MUST-FIX 3` (User-Upload `/microscope/` Guard, Row 11 Pixel Proof & 2026 Quarters — `25/25`):**
   - `_isProtectedUserUpload()` (`lines 126–142`) guards `/microscope/` URLs and returns `null`, preserving Row 10's (`0172d0ee64284a12a8aa269ce805ec07`) microscope photos (`241,359 B` / `252,870 B`).
   - Quarter fallback (`lines 338–353`) routes `mayflower` (`2026_quarter_dollar_mayflower_compact_obverse.jpg` / `_reverse.jpg`) vs `declaration`.
   - Section `4.1.1` (`lines 625–643`) documents the full MD5/pixel proof for Row 11 (`8f2197d5d03a428db24486b4ee375a5e`), proving the stored reverse (`1,510,409 B`, `MD5=cceb4ab85d398347792d8929fb11bed0`) and obverse (`1,510,450 B`, `MD5=ec05347cabf3b134a262ac9f6631385b`) are US Mint stock images (`2026-P` obverse) ingested via `Morgan AI Assistant Chat`, justifying replacement with the Denver (`D`) stock obverse `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`).
4. **`MUST-FIX 4` & `SF-1..4` (28-Row SKU Column, Unit Tests & Audit Fidelity — `23/25`):**
   - Section 4 (`lines 587–616`) includes the dedicated `SKU Field & Value in Doc / Title Branch Fired` column for all 28 rows; Section 3.2 (`lines 421–576`) includes 15 unit tests covering all audited branches plus the undated ATB obverse exemption (`SF-4`). `SF-1` (`Row 18` 1962 Proof Cent obverse kept as stored), `SF-2` (`Row 19` `2019-W` obverse flagged), and `SF-3` (`Row 26` shared doc & `977b5ab2` Vera Rubin `PASS` note) are all resolved.

---

## 2. Two Non-Blocking `EXECUTE`-Time Implementation Notes (Apply at Gate 4)

1. **Half Dollar `isP` Obverse URL (`R2.8.7` Line `360`):** Point `isP` on line `360` to the live GCS path `'$_seriesBase/2026_half_dollar_enduring_liberty_obverse.jpg'` (`1,510,450 B`, `200 OK`, `MD5=ec05347cabf3b134a262ac9f6631385b`) or stage a copy to `'$_bulkBase/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-P.jpg'` at Gate 4 (`Row 11` is `2026-D` and uses `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` `1,510,128 B` `200 OK`).
2. **Stage `23rh_c.webp` Alongside `23rh_b.webp` (`R2.8.7` Line `273` vs Section `9.1`):** Because line `273` sets `23RH` `reverseUrl: '$_official2023Base/23rh_c.webp'`, include `23rh_c.webp` (`161,734 B`, `MD5=08f5b5aaf698936913e2a24743dbdea5`) alongside `23rh_b.webp` (`226,854 B`, `MD5=8a2060d0ca5987b0faf0d8828ece365f`) in the Gate 4 upload to `gs://numista-reference-library/reference_library/us_mint_official/2023_products/` (or use `23rh_b.webp` for both sides).

---

## 3. Baton & Packet Mirror Status

- **Packet Mirrored To:** `"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\For SAG"`, `8 OCT 26\RADIO NET`, `8 OCT 26\BATONS`, `Grok Bot\RADIO NET`, `INBOX`, and `OUTBOX`.
- **Baton:** **Grok CoS (`R2.8.7` Final Scoring $\ge 95$) & SAG Concurrence $\rightarrow$ Founder Eric Morning `YES`**.
- **OVER.**
