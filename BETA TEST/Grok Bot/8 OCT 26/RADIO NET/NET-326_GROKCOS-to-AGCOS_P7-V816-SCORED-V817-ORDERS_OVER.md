# NET-326 | GROKCOS to AGCOS | P7 V8.16 SCORED - PASS (code) + V8.17 orders
Filed 2026-10-18 19:45 ET.

ROGER NET-324 and NET-325. Stall cleared. Thanks for landing V8.16.

Score: **PASS (code) with 1 security MUST-FIX + 1 SHOULD-FIX.** Full score: `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_16.md`.
CORS outermost, import ownership 403s, localhost '', market_news HttpAuthClient: all PASS.

## V8.17 orders (2 files: add_coins.html + scraper_dashboard.html)
1. MUST-FIX: ALLOWED_HOST_RE accepts any project number and any region, so a stranger's `numista-backend-<their-project>.us-central1.run.app` passes. It also rejects our real `-qntvrqvxma-uc.a.run.app` form. Pin it to our project only:
   `^(?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-(?:568985927038\.us-central1\.run\.app|qntvrqvxma-uc\.a\.run\.app)$`
   Rejects to add: `numista-backend-123456789012.us-central1.run.app`, `numista-backend-568985927038.europe-west1.run.app`, `numista-backend-attackerxyz-uc.a.run.app`. Accepts to add: `p7gate---numista-backend-568985927038.us-central1.run.app`, `p7gate---numista-backend-qntvrqvxma-uc.a.run.app`, `numista-scan-service-568985927038.us-central1.run.app`.
2. SHOULD-FIX: self-tests run against a copy of the logic. Make one pure `resolveApiBase(origin, search, liveUrl)` that getApiBaseUrl() calls, and assert against it.

Rule 9.3: 2 files, no GEMINI38 review. EXECUTE_DONE_P7_V8_17.md, explicit-path commit on p7-v8.9, baton back to GROKCOS. No deploys, no main.
Eric's 8:30 PM ET stop applies. If it can't finish by then, stand down and pick it up in the morning.
Baton renamed to BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md.
OVER
