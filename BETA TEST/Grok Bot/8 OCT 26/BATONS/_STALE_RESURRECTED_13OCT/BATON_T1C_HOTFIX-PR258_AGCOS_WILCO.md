# BATON T1C HOTFIX PR258
Holder: ERIC  Proword: OVER
Since: 13 Oct 2026 ~4:48 PM ET
Task: Typed YES (or hold) to cherry-pick deploy P0 fix `d689223f` (`/api/spot_prices` onto `_PUBLIC_PATHS`) onto a branch from main. Backend `main.py` (+ tests) only — not a full `dev` merge. See NET-041 / NET-042.
No deploy / live writes without Eric typed YES.

## Log
- 13 Oct 2026 ~16:42 ET - AG CoS: NET-039 received. T1C HOTFIX P0 (CORS + smoke issues). Working now. F1 ITERATE noted.
- 13 Oct 2026 ~16:49 ET - AG CoS: P0 fixed (spot_prices in PUBLIC_PATHS), 7/7 tests, Gemini BUILD review filed, pushed d689223f. Passing to Grok CoS for score. P1-P3 pending.
- 13 Oct 2026 ~16:50 ET - Grok CoS: SCORE = PASS (NET-041). Verified 3-line allowlist + reran 39/39 cors/auth tests. Baton -> ERIC for cherry-pick YES. AG holds P1-P3 on dev after YES/smoke.
- 13 Oct 2026 ~4:54 PM ET - Grok CoS watch: ERIC still holds YES decision; NET-042 filed; Eric pinged once this stall.

- 13 Oct 2026 ~4:55 PM ET - Grok CoS: AG filed CLOSED_OUT while ERIC still holds YES — moved premature CLOSED_OUT to _STALE. ERIC_OVER remains until typed YES + cherry-pick deploy.
- 13 Oct 2026 ~5:04 PM ET - ERIC: Typed YES. Authorizing cherry-pick deploy of d689223f (main.py + tests only, NOT full dev merge). Baton → AG CoS WILCO to coordinate deploy conversation 7485fc0a.
