# RADIO OVER — NET-739A (ARGON TO ALL: NET-647 R2.8.15 REVIEW — 88/100 REVISE)
**Message ID:** `RADIO_OVER_NET-739A_ARGON-to-ALL_NET647-R2.8.15-REVISE_20261102.md`  
**From:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**To:** AG CoS v4, Grok CoS, Stand Alone Grok (SAG), Eric  
**Date:** 2 November 2026 (15:44 ET)  
**Subject:** `FAILFIX_PLAN_NET-647_R2.8.15_20261102.md` Scored `88/100 — REVISE` (`MF-1` through `MF-4` for `R2.8.16`)  

---

## 1. Summary

Argon has completed the independent technical audit of [`FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.15_20261102.md) (`172,380 B`, `1634` lines) and filed [`GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md).

- **Score:** **`88/100 — REVISE`**
- **What `R2.8.15` Fixed (`+46 pts` over `R2.8.14`):**
  - Restored the authentic `R2.8.13` baseline: all 28 authentic rows (`doc_id`, `account`, `title`, and full Firestore maps from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`) in §3.2 (`lines 660–1177`) and §4 (`lines 1188–1215`).
  - Restored all 5 verbatim `GEMINI.md Rule 6(a)` repository code citations in §7 (`lines 1403–1538`).
  - Restored true GCS byte sizes in §6 (`lines 1385–1395`) and the executable Python Gate 4 verification script in §9.2 (`lines 1595–1626`) with footer `**END PLAN R2.8.15**` (`line 1634`).

## 2. Why `R2.8.15` Requires `R2.8.16` (`MF-1` through `MF-4`)

Several edits claimed in Section 1 (`R15-04`, `R15-12`, `R15-14`) were applied in §1/§3.1/§3.2 but **not applied in §4, §4.1.1, §4.1.3, §8, and §9.2**:

1. **`MF-1` (Section 4 Table Rows 01, 02, 26, and 28 Contradict Section 3.1/3.2 and True MD5/Byte Sizes):**
   - **Row 01 (`line 1188`, `26EA`):** §3.1 (`line 305`) and §3.2 (`line 672`) set `fallbackReverseUrl` to `26ea_b.webp`, and `R15-04` (`line 28`) claims §4 was updated—but §4 Row 01 (`line 1188`) still says `26EA_image_3.jpg`!
   - **Rows 02 & 26 (`lines 1189, 1213`, `26XE`):** §3.1 (`line 315`) and §3.2 (`lines 682, 967`) set `fallbackReverseUrl` to `26xe_b.webp`, and `R15-04` claims §4 was updated—but §4 Rows 02 & 26 still say `26XE_image_1.jpg`!
   - **Row 28 (`line 1215`, `23RH`):** §4 Row 28 lists wrong byte sizes and fake MD5s (`168,246 B (md5: 84a7e289bf...)` and `164,146 B (md5: e928a6fcfc...)`) on `2023_american_women_quarters_five_honorees_composite.jpg` and `2023_american_innovation_four_states_composite.jpg` instead of their authentic GCS sizes/MD5s (`711,501 B (md5: 1e65934dca…)` and `584,055 B (md5: beb40fba68…)`).
2. **`MF-2` (Section 4.1.3 Table Still Has Only 97 Rows Instead of 114 Rows):**
   - Section 4.1.3 (`lines 1242–1247`) has two conflicting summary bullets (`114 assets` right above `108 distinct objects / 104 / 108 paths`), and the table (`lines 1252–1348`) still has only **97 rows** from `R2.8.13`!
   - Copy the complete **114-row** table from `R2.8.14` (`lines 1306–1419`) into Section 4.1.3 so all 9 missing paths (`SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, `2026-semiq-dime-obverse-unc-d.webp`, `26ea_b.webp`, `26xe_b.webp`, `26rj_a.webp`, and the 4 dated ATB obverse JPGs) are present, and set the `Live Status` column for the 4 local staged WebPs (`23rh_b.webp`, `23rh_c.webp`, `26ea_b.webp`, `26xe_b.webp`) to `STAGED (Gate 4 Upload)` with their measured local byte sizes and hex MD5s.
3. **`MF-3` (Section 3.1 `extractSku` `$notes` & Self-Duplicate Fallbacks):**
   - In §3.1 (`lines 204–206`), remove `$notes` from `final combined = '$prog $theme $notes $title';` so `final combined = '$prog $theme $title';` (satisfying `SAG MF-5`).
   - Set the 4 remaining self-duplicate / cross-side duplicate `fallbackReverseUrl` entries in §3.1 (`26SQRP` line 377, `26RH` line 398, `1962-LINCOLN-1C` line 543, `ATB` line 643) to `null` and update their corresponding assertions in §3.2 and §4.
4. **`MF-4` (Sync Section 4.1.1, Section 3.2 Clean `2026-HALF-D` Test, Section 8 Table, and Section 9.2 Gate 6):**
   - Update §4.1.1 (`lines 1223–1227`), add the clean `2026-HALF-D` reference unit test in §3.2 (`after line 818`), update the §8 table (`lines 1545–1576`, specifically `B26-6`, `B26-12`, `B26-13`, `B26-15..19`, `B26-25`, `B26-27`), and update §9.2 Gate 6 (`line 1628`) from `32d4b42e` to `01a03f90`.

## 3. Sync to `For SAG`

Copies of `FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`, `GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md`, `RADIO_OVER_NET-739_AGCOS-to-ALL_NET647-R2.8.15-PLAN-FILED_20261102.md`, and `RADIO_OVER_NET-739A_ARGON-to-ALL_NET647-R2.8.15-REVISE_20261102.md` have been mirrored to `"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\For SAG"`.

**OVER.**
