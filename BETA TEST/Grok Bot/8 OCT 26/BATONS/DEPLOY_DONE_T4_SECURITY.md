# DEPLOY_DONE_T4_SECURITY

- **Timestamp:** 2026-10-14 06:01:08 ET
- **PR:** #262 (https://github.com/Numista-AI/Numista.AI/pull/262)
- **Merge SHA:** eee064879372076c91a2a7357ecaa24f4d56dadc (code commit 33f0e497 / c80f4122)
- **Title:** fix(security): T4 Security Hotfix — portfolio IDOR, estate cap, AI rate cap, CSV injection
- **Status:** Completed / Success on numista.ai
- **Live Smoke Tests:**
  - GET https://numista.ai/api/spot_prices -> 200 OK
  - POST https://numista.ai/api/portfolio/snapshot/daily -> 401 Unauthorized (IDOR sealed)
  - POST https://numista.ai/api/estate/generate-attorney-link -> 401 Unauthorized
