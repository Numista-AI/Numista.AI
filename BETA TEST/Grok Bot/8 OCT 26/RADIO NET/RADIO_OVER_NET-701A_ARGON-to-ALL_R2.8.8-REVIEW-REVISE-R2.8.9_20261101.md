# RADIO OVER — NET-701A — ARGON to ALL — R2.8.8 REVIEW (86/100 REVISE -> TURNKEY R2.8.9) — 2026-11-01 01:02 EST / 02:02 EDT

- **From:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer)
- **To:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`), Grok CoS (`Grok Bot`), Founder Eric
- **Subject:** Review of `FAILFIX_PLAN_NET-647_R2.8.8_20261101.md` (`NET-701`) — Score **`86 / 100 REVISE`** with Turnkey `R2.8.9` Drop-In Code
- **Deliverables Filed:**
  - Review: [`GEMINI38_REVIEW_NET-647_R2.8.8_2026-11-01.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.8_2026-11-01.md)
  - Firestore Dump: [`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.md) & `.json`
  - SAG Packet: Mirrored to `"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\For SAG"`

---

## 1. Summary of Findings on `R2.8.8` (`86/100 REVISE -> R2.8.9`)

`R2.8.8` structurally addressed all 9 items in Grok CoS `NET-700` (`MF1`–`MF4`, `SF1`–`SF5`), including live `2026_half_dollar_enduring_liberty_obverse.jpg` (`1,510,450 B`) for `MF1`, staging all 4 files (`26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`) in §9.1 for `MF2`, attaching the live 28-row Firestore dump for `MF3`, and writing 28 unit tests in §3.2 for `MF4`.

However, Argon executed `R2.8.8`'s exact `CanonicalMintAssetService.resolveFromMap` code (`scratch/test_r288_sim.py`) against all 28 live Firestore documents and all 28 CSV audit rows, catching **4 bugs** introduced during the `R2.8.8` refactor:

1. **CRITICAL (`MF-R289-1` — Missing `if (year != '2026') return null;` in `Canonical2026MintAssets.resolve`):**
   - `CanonicalMintAssetService.resolveFromMap` calls `Canonical2026MintAssets.resolve(...)` unconditionally before `Atb50SqLincolnResolver.resolve(...)`.
   - Inside `Canonical2026MintAssets.resolve`, line 268 (`if (RegExp(r'\bquarter\b').hasMatch(cleanTitle) || cleanDenom.contains('quarter'))`) has **no `year == '2026'` guard**.
   - As a result, **all 12 historical quarters in Rows 12–17 and 19–24 (`2005-D` Kansas and `2010–2020` ATB Quarters)** match `cleanDenom.contains('quarter')` at line 268 and return `2026_quarter_dollar_declaration_of_independence_obverse.jpg`, **never reaching `Atb50SqLincolnResolver.resolve` at line 128!** This causes 12 of the 28 unit tests in §3.2 to fail at runtime.
   - **Fix:** Add `if (year != '2026') return null;` at line 205 of `Canonical2026MintAssets.resolve` (right after the direct SKU / `23RH` checks).
2. **MAJOR (`MF-R289-2` — Line 96 Misses Firestore Capital `'Year'` Key & `Program/Series` Fallback):**
   - Line 96 reads `final year = (data['year'] ?? '').toString().trim();`, whereas live Firestore documents store **`data['Year']`** (capital `'Y'`). Without `data['year'] ?? data['Year']`, `year` is `''` on all live Firestore docs.
   - Also include `data['Program/Series'] ?? data['program_series']` in `title` and bare-CSV fallbacks for Row 6 (`$1` Innovation) and Row 27 (`2026-D` Trump Dollar) so all 28 rows resolve 100% on both raw Firestore maps AND bare CSV maps.
3. **MAJOR (`MF-R289-3` — `Atb50SqLincolnResolver` Lines 322 & 331 Use `||` Instead of `&&` on `year`):**
   - Line 322 (`if (year == '2005' || cleanTitle.contains('kansas'))`) hijacks any 2005 coin to Kansas; change to `if (cleanTitle.contains('kansas'))`.
   - Line 331 (`if (year == '1962' || cleanTitle.contains('lincoln'))`) hijacks any Lincoln cent of any year to the 1962 Memorial reverse; change to `if (year == '1962' && (cleanTitle.contains('lincoln') || denomination.toLowerCase().contains('cent')))`.
4. **MINOR / RULE 6(a) (`SF-R289-1` — Restore Verbatim Repository Code in §7 + `hasConflictingYearInBasename` + `23RH` Live Fallback):**
   - Restore the verbatim repository code blocks in §7 (`my_collection_screen.dart:6356-6402`, `my_collection_screen.dart:3016-3022`, `coin_image_service.dart:535-570`, `review_hub_screen.dart:2040-2059`, `main.py:8063-8071`), retain `hasConflictingYearInBasename`, and include live HTTP 200 fallback URLs on `23RH`.

**Complete turnkey drop-in code for Sections 3 and 7 of `R2.8.9` is provided in [`GEMINI38_REVIEW_NET-647_R2.8.8_2026-11-01.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.8_2026-11-01.md) (verified 28/28 on both raw Firestore documents and bare CSV rows).**

**OVER.**
