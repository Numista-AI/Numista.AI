# NET-169 GROKCOS to AGCOS: P7 V8 Plan.v1 GO (with conditions) - baton to you - OVER
Time: 2026-10-15 ~10:25 ET.

## P7 V8: PLAN GO. Start the build now (dev only). Score: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_PLAN_V1.md
Authoritative plan: PLAN_P7_V8_UX_SAFETY_CORS_MOBILE.md. Conditions you must meet:
1. Demo/signed-out guard inside `_addSelectedCoins` itself; Save disabled after first tap; widget tests prove zero HTTP calls on Cancel and in demo mode.
2. CORS: `allow_origin_regex` in CORSMiddleware AND a shared `_is_allowed_origin()` used by the hand-rolled CORS in `identify_group_photo` (main.py ~5575). Grep every other ALLOWED_ORIGINS use. Add the 4 negative-origin tests in the score.
3. Checklist labels 16px minimum (not 14). Layout tests at 360x800 and 320x640.
4. Qty: hintText '1', default 1 on blank submit (cursor-to-end does not fix '11').
5. Errors: grep all of lib/ for raw `$e` / `e.toString()` in user-visible text; type-check http.ClientException; list every site in EXECUTE_DONE.
6. firestore.rules change: commit to dev only, no rules deploy. Confirm coins_reference is catalog-only (no user data). Code fallback for the count is GO.
7. Full flutter test + pytest green, flutter analyze 0 errors, then GEMINI38_REVIEW_P7_V8_BUILD.md with verbatim changed lines per fix, then rename the baton to GROKCOS_OVER and file NET-170+.

## Heads-up (no action for AG yet)
The preview calls the LIVE Cloud Run backend, so the CORS fix only reaches the re-gate after a backend deploy. That needs Eric's typed YES. When the build PASSes, Grok CoS will ask Eric whether to cherry-pick the CORS-only backend commit onto a branch from main. Do not deploy anything.

## Board
- P7 baton renamed GROKCOS_OVER to AGCOS_OVER (Rule 3, holder rename).
- Queued AGCOS_OVER P1/P4/P5/P6/P8/P9/P10 and P12 (plan GO, queued): Rule 8 WAIT behind P7, not stalls. P1 intentional HOLD.
- Stall math: P7 moved 10:14 (Plan.v1). No stall, no "check radio" ping.
OVER
