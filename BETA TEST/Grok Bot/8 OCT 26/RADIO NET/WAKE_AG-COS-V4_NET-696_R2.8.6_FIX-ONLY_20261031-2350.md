# WAKE — AG CoS v4 — NET-696 — R2.8.6 FIX-ONLY
**From:** Grok CoS | **Time:** 31 Oct 2026 ~11:50 PM ET
Grok CoS scored R2.8.5 **82/100 REVISE** (see COS_SCORE_NET-647_R2.8.5_82_REVISE_20261031-2350.md). MF1–MF3 from NET-694 are fixed and all URLs/bytes verified. Fix only these in R2.8.6:
1. **MF-A:** Replace the 12 doc IDs that don't exist (rows 7, 10, 11, 20–28) with real doc_ids from `ERIC_ACCOUNT_252_AUDIT_20261031.csv`. No placeholders like a1b2c3d4/d4e5f6g7.
2. **MF-B:** Effigy Mounds, Frederick Douglass, Ozark (2017) and Yellowstone (2010) are P-mint — use the P ATB obverse, not `obverse-d`.
3. **MF-C:** Row 19 `UOBfFO2m…` is San Antonio Missions 2019-W — correct title, obverse and reverse (not the 50-State Phila obverse on both sides).
4. **MF-D:** Row 18 1962 Gem Proof has no mint mark — not the 1962-D obverse.
5. **MF-E:** Row 28 — no 2026 26RH images on a 2023 item; tie to a real doc or drop; stage 23rh_b under a 2023 path.
Generate the table from the audit CSV and attach the script. Keep everything else unchanged. Stand down by ~3 AM ET; resume after 9 AM if not done.
