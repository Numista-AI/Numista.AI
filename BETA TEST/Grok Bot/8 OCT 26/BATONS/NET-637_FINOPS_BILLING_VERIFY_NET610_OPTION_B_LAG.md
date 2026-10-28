# NET-637 — FinOps billing verify: NET-610 Option B (LAG)

**Filed:** 27 Oct 2026 ~9:20 PM ET · **Billing account:** 010E3C · **Project claim:** numista-morgan-pilot only
**Source:** FinOps note `/workspace/roi/net610_option_b_billing_verify_20261027.md` (box); copy in DAY as `FINOPS_BILLING_VERIFY_NET610_OPTION_B_20261027.md`

## BLUF
- Option B evening burn (~8:10–8:51 PM ET) **NOT in BigQuery export yet** — cannot confirm AG $3.86 tonight.
- MAX(usage_end)=1:00 PM ET; morgan-pilot evening rows=0; export_time ~6:03 PM ET — classic lag.
- Landed daytime morgan-pilot (~11–1 PM, prior fold-gate shape, NOT Option B): ~$0.060578 gross / $0 net OOP (App Builder promo e87a9b98…).
- AG $3.86 is SKU math ≠ BQ (same pattern as NET-605 $3.86 vs ~$0.061 landed).
- No Advanced Generative Answers SKU in Oct export.
- Contamination (landed hours): NO Discovery/CG on studio or numista-qc; studio today ~$1.30 = SQL/Run/Artifact/Gemini; qc zero rows 26–27 Oct.
- Hard verify remains **Wed 28 Oct ~1:00–1:15 PM ET** Billing chase.

Do not treat $3.86 as billing-verified. No spend/execute/merge authorized by this note.
