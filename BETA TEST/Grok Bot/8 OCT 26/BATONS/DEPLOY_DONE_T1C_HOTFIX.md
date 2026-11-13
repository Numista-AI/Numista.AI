# DEPLOY_DONE_T1C_HOTFIX

- **Timestamp:** 2026-10-13 17:12:41 ET
- **PR:** #259 (https://github.com/Numista-AI/Numista.AI/pull/259)
- **Merge SHA:** d3f7a2cddbcc2b7f32ece5384317c7de73b324fc
- **Title:** fix(t1c-p0): add /api/spot_prices to _PUBLIC_PATHS
- **Status:** Completed / Success on numista.ai
- **Live Smoke Test:**
  - GET https://numista.ai/api/spot_prices -> HTTP 200 OK
  - Data returned: Gold, Silver, Platinum, Palladium spot prices
