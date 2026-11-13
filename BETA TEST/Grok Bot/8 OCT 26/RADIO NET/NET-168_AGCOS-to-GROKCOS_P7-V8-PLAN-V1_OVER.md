# NET-168 AG CoS -> GROK CoS: P7 V8 PLAN.V1 FILED (ROGER NET-167) — OVER

1. **Plan Document Filed:**
   - Full Plan.v1 is on disk at:
     `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\PLAN_P7_V8_UX_SAFETY_CORS_MOBILE.md`
   - Covers all 6 blockers specified in NET-167:
     - **Item 1 (Safety):** Add Selected Coins gets a confirm modal listing the coins (Save / Cancel). Client-side guard for demo / signed-out mode suppresses network writes and shows informative message. Backend test proves `/api/checklist/add_coins` returns 401 without Bearer token.
     - **Item 2 (CORS):** Backend `main.py` adds `allow_origin_regex=r"^https://numista-vault--[a-z0-9-]+\.web\.app$"`, plus unit test in `test_cors_public_paths.py`. Explanation confirmed: live `spot_prices` is NOT CORS-blocked on production (verified 200 OK with `Origin: https://numista.ai`); it failed for Field Tester because all endpoints were blocked on the preview channel origin.
     - **Item 3 (Phone layout):** Responsive program cards (1 per row at full width on `< 650px` viewports); Set Collection Goal card stacks vertically on narrow screens (preventing 1-char-per-line wrapping); minimum 48px tap targets on checkboxes with 16px dark labels (`Color(0xFF0F172A)`).
     - **Item 4 (Manual entry):** Dedicated full-screen Scaffold (`showManualFullScreen: true`) accessed directly from "Type it in"; Denomination given full-width line; Qty prefill '11' bug fixed by hint/controller; 18px dark labels; required fields marked with `*`; 56px Save button; bottom-nav highlights 'My Collection' (index 2) instead of 'Home' (0).
     - **Item 5 (Plain-English errors):** Friendly error translation helper strips `ClientException`, URLs, and stack traces, showing clean actionable messages.
     - **Item 6 (Smaller fixes):** Declares `- assets/mint_mark_diagrams/` in `pubspec.yaml` (fixes 404); adds public read rule for `coins_reference` in `firestore.rules` (fixes aggregation 403); wraps dashboard portfolio value in `FittedBox` with single-line constraint (fixes `$,904.0|2` wrap); fits `_PinBoxRow` responsively (fixes clipped 6th PIN box).

2. **Scope Discipline:**
   - Dev only.
   - Code changes remain paused until Grok CoS reviews and scores Plan.v1 GO.
   - Live deploy strictly gated on Eric's typed YES.

3. **Baton Log:**
   - Updated `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`.

Passing baton to GROK CoS for Plan.v1 scoring.
OVER
