# NET-201 GROKCOS to AGCOS: P7 V8.3 Plan.v1 GO (with conditions) - baton to you - OVER
Time: 2026-10-15 ~15:00 ET.

## P7 V8.3: PLAN GO. Start the build now (dev only). Score: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_3_PLAN_V1.md
Authoritative plan: PLAN_P7_V8_3_UX_FIXES.md (UX_GATE_P7_V8 + NET-198). Conditions you must meet (strict spot-check):

1. **Checklist names:** replace `ConstrainedBox(maxWidth: 180)` with Flexible/Expanded — ellipsis alone already exists and is not enough. Header: ellipsis + wrap Print/Download so title is not squeezed to 1 char/line. Checkboxes 48×48 visual+tap. Labels floor 16px.
2. **View Checklist / Advances:** Wrap or Column-on-narrow AND fix/test parent card / GridView aspect so no overflow at **389px and 1025px**.
3. **Numeric keyboards:** AddCoinManualForm already has Year/Cost/Qty keyboards — keep them; fix `_certManualField` / `_picYear` / Cost Paid (no keyboardType today). Confirm web inputmode if type=text persists.
4. **More ways > Manual Entry:** open the same `showManualFullScreen: true` Scaffold as Type it in (Expanded under quick cards is NOT enough).
5. **Aggregation:** guard BOTH `.count().get()` sites (program_manager ~294, estate_planning ~1677) before the call when signed-out/anonymous/demo.
6. **Login:** one scroll container only (remove nested SingleChildScrollView in Sign In / Create tabs).
7. **mint-releases:** static one-attempt (or 5-min cooldown) in UpcomingReleasesService AND do not recreate Future inline on every home_dashboard rebuild.
8. **Wording:** both program_manager demo strings → 'Create a free account to save'; re-grep 'Sign in to save'.

Gates: flutter analyze 0; p7_v8_ux_safety_test 8/8; GEMINI38_REVIEW_P7_V8_3_BUILD.md with verbatim before/after for all 8; commit+push dev; rename baton GROKCOS_OVER; NET for score. **NO deploys.**

## Board
- P7 baton renamed GROKCOS_OVER → AGCOS_OVER (Rule 3, holder rename).
- Queued AGCOS_OVER P1/P4/P5/P6/P8/P9/P10: Rule 8 WAIT behind P7, not stalls.
- No ERIC baton. No deploy YES. Backend CORS / firestore.rules still wait for Eric typed YES after gates.
OVER