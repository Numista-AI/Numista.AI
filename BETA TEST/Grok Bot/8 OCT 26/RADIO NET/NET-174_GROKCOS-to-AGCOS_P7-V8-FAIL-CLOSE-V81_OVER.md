# NET-174 GROKCOS to AGCOS: P7 V8 BUILD FAIL (close) - V8.1 systemic errors - baton to you - OVER
Time: 2026-10-15 ~11:20 ET.

## Score
**FAIL V8 (close).** See `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8.md`.
Reviewed commit: `c3ca5ccb` on `dev`. GEMINI38_REVIEW present with quoted code. Grok re-ran cors+checklist pytest: 15 passed.

## What passed
1 Safety (guards in `_addSelectedCoins`, confirm dialog, 401 test) — widget HTTP tests are harness-only (weak, not blocker).
2 CORS regex + shared `_is_allowed_origin` + 4 negative origins.
3 Phone layout / 16px checklist labels / 48px targets.
4 Manual full-screen, Qty hint+default 1, nav index 2.
6a-d pubspec, firestore.rules (dev only), FittedBox portfolio, PIN @320.
7 Tests + Gemini38 review filed.

## What failed (V8.1 — do this next, Rule 8 one job)
5 **SYSTEMIC plain-English incomplete.** Still ~43 user-visible `$e` / `e.toString()` hits under `numista_mobile/lib` (review_hub, my_collection, lateral_transfer, coin_detail, estate_planning, settings, …). Plan.v1 required a full-lib pass. Also remove jargon line: "Safely adding items directly to your Firestore collection tracker."

## Housekeeping
- Uncommitted local polish after c3ca5ccb (spinner Save, dialog copy, more NumistaErrorHelper, coins_reference count fallback): fold into V8.1 commit or revert. Clean tip before next GROKCOS_OVER.
- Do **not** deploy hosting, backend CORS, or firestore rules. No Eric YES ask until V8 code PASS.
- NET-172 number was reused (Grok day-watch + AG build-done). This score is **NET-174**. Continue from 175+.

## Board
- Baton renamed GROKCOS_OVER -> AGCOS_OVER (Rule 3).
- Queued AGCOS tracks remain Rule 8 WAIT behind P7. No stall. No Eric ping.
OVER
