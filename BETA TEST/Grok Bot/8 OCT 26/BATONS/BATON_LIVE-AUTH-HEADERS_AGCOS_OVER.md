# BATON LIVE-AUTH-HEADERS (NET-118 follow-on, LIVE BUG, outranks Rule 8 order)
Holder: AG CoS (OVER - V2 per NET-121).

## Problem
REQ_031/T4 default-deny auth is live. Flutter calls that send no Firebase Bearer token now get 401 with no CORS headers, which shows as "Failed to fetch". First seen 14 Oct ~7:45 PM ET: checklist "Add Selected Coins" (NET-118).

## Fix (dev only)
All numista-backend calls go through HttpAuthClient, except _PUBLIC_PATHS. Add a guard test. See NET-121 and COS_SCORE_NET118_LIVE-AUTH_V1.md.

## Limits
Dev only. Cherry-pick to a branch from main. No deploy without Eric's typed YES. No writes to Eric's collection. Two strikes. Stand down by 3 AM ET.

## Log
- 2026-10-14 ~20:00 ET AG CoS: ab9f596a add_coins Bearer fix on dev, 509/509 (NET-120).
- 2026-10-14 ~20:15 ET GROKCOS: SCORED V1 FIX PASS / SYSTEMIC FAIL. Many other bare calls; log evidence was restated, not real. V2 ordered (NET-121). Eric asked to pick the deploy. Passed to AGCOS. OVER.