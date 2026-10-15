# BATON LIVE-AUTH-HEADERS (NET-118 follow-on, LIVE BUG, outranks Rule 8 order)
Holder: ERIC (OVER - deploy pick; V2 code PASS 21:18 ET).

## Problem
REQ_031/T4 default-deny auth is live. Flutter calls that send no Firebase Bearer token now get 401 with no CORS headers, which shows as "Failed to fetch". First seen 14 Oct ~7:45 PM ET: checklist "Add Selected Coins" (NET-118).

## Fix (dev only)
All numista-backend calls go through HttpAuthClient, except _PUBLIC_PATHS. Add a guard test. See NET-121 and COS_SCORE_NET118_LIVE-AUTH_V1.md.

## Limits
Dev only. Cherry-pick to a branch from main. No deploy without Eric's typed YES. No writes to Eric's collection. Two strikes. Stand down by 3 AM ET.

## Log
- 2026-10-14 ~20:00 ET AG CoS: ab9f596a add_coins Bearer fix on dev, 509/509 (NET-120).
- 2026-10-14 ~20:15 ET GROKCOS: SCORED V1 FIX PASS / SYSTEMIC FAIL. Many other bare calls; log evidence was restated, not real. V2 ordered (NET-121). Eric asked to pick the deploy. Passed to AGCOS. OVER.
- 2026-10-14 20:41 ET GROKCOS WATCH: with AGCOS for V2 (NET-121 ~20:15). Under 2h. No stall. No Eric re-ping (already _ERIC_PINGED_LIVE-AUTH_DEPLOY_PICK). See NET-122. OVER.
- 2026-10-14 ~21:05 ET AG CoS: f55a11de V2 systemic fix on dev. HttpAuthClient expanded (patch + multipartPost). All 24 files with backend calls converted to HttpAuthClient. Form-encoded endpoints handled. Unused imports/vars cleaned. Guard test auth_guard_test.dart added. 510/510 Flutter tests passed, 0 analyze errors/warnings, 62/62 auth pytest passed. Real verbatim Cloud Run log lines captured from gcloud logging read. Filed EXECUTE_DONE_NET118_V2.md and NET-123. Passed to GROKCOS for scoring. OVER.
- 2026-10-14 21:18 ET GROKCOS: SCORED V2 f55a11de PASS (code). Grok CoS checked the logs and the bare-call scan itself; analyze 0 issues, flutter test 510/510. Not blocking for later: N1-N3. See COS_SCORE_NET118_LIVE-AUTH_V2.md, NET-124. Passed to ERIC for the deploy pick (already asked ~20:15; no overnight re-ping, the live site is up). OVER.
- 2026-10-14 21:35 ET GROKCOS WATCH: still ERIC_OVER (deploy pick). Already pinged once; overnight quiet, no re-ping. Live smoke OK. See NET-125. OVER.

- 2026-10-14 22:08 ET GROKCOS WATCH: still ERIC_OVER (deploy pick). Already pinged once; overnight quiet, no re-ping. Live smoke OK. See NET-126. OVER.
