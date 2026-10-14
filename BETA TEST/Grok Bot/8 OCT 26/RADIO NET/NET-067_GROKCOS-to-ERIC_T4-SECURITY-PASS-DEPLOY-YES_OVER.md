# NET-067 GROKCOS -> ERIC: T4 SECURITY HOTFIX PASS - deploy YES when ready
13 Oct 2026 10:13 PM ET. Re: NET-066 (AGCOS) / commit `c80f4122` / baton T4_SECURITY.

## Score
**PASS** - see `8 OCT 26\COS_SCORE_T4_SECURITY.md`.

P0 portfolio snapshot IDOR sealed; estate reports owner-locked + valid_days capped [1,30]; valuation anon-blocked + 20/day cap; CSV formula escape; PyJWT 2.14.0 / urllib3 2.8.0; Admin Grade Flags gated; default-deny inventory test fixed. Grok re-ran security pytest pack: **30/30 PASS**. Live smoke OK.

Residual (not blocking): 21 Category-2 routes still take user_id/email without per-route ownership match (outer default-deny only) — follow-on track after this deploy if you want them tightened.

## Ask (Eric)
Typed YES to deploy the T4 security hotfix (`c80f4122` and its docs tip if needed) via cherry-pick onto a branch from `main` — not a full `dev` merge. No live apply until you type YES. Firestore rules change is part of this pack; say if you want rules deploy called out separately in the YES.

Baton: `BATON_T4_SECURITY_ERIC_OVER.md`

OVER
