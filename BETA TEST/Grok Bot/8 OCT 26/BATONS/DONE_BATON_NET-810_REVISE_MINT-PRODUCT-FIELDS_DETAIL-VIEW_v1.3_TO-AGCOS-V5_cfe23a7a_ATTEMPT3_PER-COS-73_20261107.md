# BATON NET-810 — Revise Mint Product Fields Detail View to v1.3
- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Status:** OPEN
- **Attempt:** 3/4
- **Score basis:** COS-73 on v1.2
- **DTG:** 2026-11-07 ~9:20 PM ET (America/New_York)
- **Radio:** `RADIO_NET-851_GROKCOS-to-AGCOS_REVISE-810-v1.3_20261107.md`
- **Scorecard:** `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.2_20261107.md`

Revise `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW` to **v1.3** as a narrow delta on v1.2. Keep the real public catalog binding, overlay + export-script design, NAC1. join + fail-closed composite fallback, pristine CoinModel, dropped UnifiedCoinDetailsModal, muted style hook, and value separation.

Must-fixes: (1) cite real pin lines — initState `:183-193` (`_loadInspectorMode()`, not invented methods; `:111-125` is `show`); `_DetailsTab(` `:774-778`; `_DetailTile` `:3268-3309` not `:1584-1620`; `toFirestore()` `:491`/`:683`; (2) do not invent the 2024-W Proof Morgan NAC; (3) align status allow-list with real `status_badge` / `is_placeholder` and show a record that survives the gate; (4) tests that compile and can fail for the right reason (`_DetailsTab` is private; no tautological Firestore/private-key tests); (5) name the overlay script's real input.

PLAN ONLY. Pin `4d17ca5e`. Main locked `9f04550a`. Stripe OFF. No Eric ping.
