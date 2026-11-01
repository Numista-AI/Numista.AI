**RADIO OVER NET-682 (AGCOS to ALL, 31 Oct 8:15 PM ET):** AG CoS v4 FILED `FAILFIX_PLAN_NET-647_R2.7_20261031.md`. Addresses Q1-Q5, E1-E5, E6, and E7 with hard technical evidence:
- Q1 legacy null unit pricing diagnosed; read-time compute `rawCost / cleanQty` fallback planned; backfill script ready for YES.
- Q2 null image URL fields causing gold $ placeholder diagnosed; client catalog map fallback in `_buildCoinThumbnail` planned.
- Q3 missing SKUs from intake session mapped.
- Q4 set blister folder `26rj_a.jpg` vs set lens `26rj_set_lens.webp` diagnosed.
- Q5 preview environment verified clean: CORS contains `*` and `p7-gate`, HTTP 200s verified.
- Must-fixes E1-E7 for Eric's real account (`users/eric.seaman@yahoo.com/coins`, filter '2026', Cards view) fully diagnosed and planned:
  * E1 eagle duplicate fixed via obverse preference for Morgan/Peace.
  * E2 placeholders fixed via client catalog fallback + backfill.
  * E3 250th Uncirculated Set remapped to Set Lens.
  * E4 Valuation Pending fixed via purchase cost fallback & Unspecified grade normalized to Raw.
  * E5 card titles fixed via `maxLines: 2`.
  * E6 2026 dimes showing 2025 Roosevelt image remapped to Semiquincentennial Liberty Dime assets.
  * E7 26EA Inspector showing 2023 Walking Liberty on Rev remapped to 2026 official obv/rev assets.
  * Complete 11-coin read-only audit table and Year/Side Guards included.
All Firestore writes to Eric's account held for separate typed YES.
PLAN ONLY: 0 code edits, 0 commits of code, 0 deploys, 0 GCS/Firestore writes.
TURN: ARGON / GROK COS (R2.7 Review & Scoring) -> SAG -> Eric Typed YES -> Execution on p7-v8.9. Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF. OVER.
