# COS SCORE - P7 ADD-COINS-FLOW V8 BUILD
Scorer: Grok CoS | 2026-10-15 ~11:20 ET | Reviewed: c3ca5ccb on origin/dev + GEMINI38_REVIEW_P7_V8_BUILD.md (code quoted) + direct spot-check on EDS_Laptop. Plan conditions from COS_SCORE_P7_ADD-COINS-FLOW_V8_PLAN_V1.md / NET-169.
Verdict: **FAIL V8 (close).** Items 1-4 and 6-7 mostly PASS. Item 5 (SYSTEMIC plain-English errors across all of `numista_mobile/lib`) is incomplete. Pass baton back to AGCOS for V8.1.

Grok CoS re-ran on EDS_Laptop: `python -m pytest numista_backend/tests/test_cors_public_paths.py numista_backend/tests/test_checklist_routes.py -q` -> **15 passed**. Working tree after c3ca5ccb has uncommitted polish on `program_manager_screen.dart`, `add_coins_hub.dart`, `p7_v8_ux_safety_test.dart` (spinner Save, dialog copy, two more NumistaErrorHelper sites, coins_reference count fallback) — **not scored**; fold into V8.1 or drop before next submit.

| # | NET-169 / Plan.v1 item | Score | Evidence |
|---|------|-------|----------|
| 1 | Safety: confirm + demo/signed-out guard inside `_addSelectedCoins`; Save disabled after first tap; 0 HTTP on Cancel + demo | **PASS (weak tests)** | Code: `_confirmAddSelectedCoins` + guard inside `_addSelectedCoins` (authUser / isAnonymous / GuestSeedService); `_isSavingCoins` early-return + UI replaces button with spinner (uncommitted) / null onPressed (committed). pytest `test_checklist_add_coins_unauthenticated_returns_401` green. Widget tests in `p7_v8_ux_safety_test.dart` are **harness replicas** (do not call ProgramManagerScreen) — pattern proven, same weakness as prior P7 rounds; not a blocker because guards are in production code. |
| 2 | CORS `allow_origin_regex` + shared `_is_allowed_origin` + 4 negative origins | **PASS** | main.py:60-75 regex + CORSMiddleware; identify_group_photo ~5589 uses `_is_allowed_origin`. ALLOWED_ORIGINS only list + helper + middleware + that hand-roll. Negative tests: evil.com suffix, evil-numista prefix, http://, other-site — all present; Grok re-run 15/15 green. NOTE: preview still hits LIVE Cloud Run until Eric YES on a CORS backend cherry-pick — do **not** ask for that YES until V8 code PASS. |
| 3 | Phone layout: 1-col <650, Goal vertical, 48px targets, **16px floor on checklist labels** | **PASS** | isNarrow <650; crossAxisCount 1; Goal Column; year label fontSize 16 #0F172A (~1276); missing chip ConstrainedBox min 48 + label 16; + Add another copy 48/16. Layout tests at 360x800 (manual/safety) and 320x640 (PIN) present; no dedicated checklist-layout widget test at both sizes — soft, not a fail. |
| 4 | Manual entry full screen + Qty hintText '1' + default 1 + nav index 2 | **PASS** | showManualFullScreen Scaffold; Quantity hint `'1'`; submit default `'1'` if blank; digits-only Year/Qty; Denom full-width; 18px labels with `*`; 56px Save; base_layout maps Add New Coins -> index 2. |
| 5 | Plain-English errors: SYSTEMIC grep all of `numista_mobile/lib` for user-visible `$e` / `e.toString()`; http.ClientException type-check; list sites | **FAIL** | NumistaErrorHelper exists and type-checks `http.ClientException` + status codes. Replaced sites in add_coins_hub + program_manager (committed ~6; uncommitted +2). **SYSTEMIC incomplete:** Grok grep still finds **43** user-visible `Text(...$e...)` / `e.toString()` hits across lib/ (top: review_hub 10, my_collection 5, lateral_transfer 5, coin_detail 5, estate_planning 3, settings 3, …). Plan.v1 / NET-169 required a full-lib pass, not P7 screens only. Also still showing jargon under Add Selected: "Safely adding items directly to your Firestore collection tracker." (program_manager ~1504) — replace with plain words in V8.1. |
| 6a | mint_mark_diagrams pubspec | **PASS** | pubspec.yaml assets/mint_mark_diagrams/ |
| 6b | firestore.rules coins_reference public read | **PASS (dev only)** | match allow get,list if true; write false. Catalog-only claim accepted for scoring. **No `firebase deploy --only firestore` without Eric typed YES.** |
| 6c | Dashboard FittedBox + NumberFormat | **PASS** | home_dashboard FittedBox + fmt.format(displayVal) |
| 6d | PIN FittedBox @ 320px | **PASS** | login_screen PinBoxRow in FittedBox; test p7_v8_pin_box_row_fits_320px_width_without_overflow |
| 7 | Tests + GEMINI38_REVIEW quoted | **PASS** | AG: flutter analyze 0, 8/8 p7_v8 tests, cors/checklist pytest. Grok: 15 pytest green. GEMINI38_REVIEW_P7_V8_BUILD.md filed with verbatim lines. No separate EXECUTE_DONE file (NET-172 AG body covers it) — OK this round. |

## V8.1 orders (AG — one job, Rule 8)
1. Finish SYSTEMIC plain-English: replace every remaining user-visible `$e` / `e.toString()` / raw exception string in SnackBar/dialog/errorText across `numista_mobile/lib` with `NumistaErrorHelper.toUserFriendly` (or equivalent plain message). List every file:line replaced in EXECUTE_DONE / NET.
2. Delete or rewrite the "Firestore collection tracker" helper line under Add Selected Coins to plain English (no Firestore/API jargon).
3. Commit the current uncommitted polish (or revert it) so the next score is against a clean `dev` tip — do not leave a dirty tree when renaming to GROKCOS_OVER.
4. Re-run flutter analyze (0), full flutter test at/above baseline, pytest at/above baseline. Refresh GEMINI38_REVIEW_P7_V8_BUILD.md (or V8_1) with quoted lines for the new error sites + helper-text fix.
5. Rename baton GROKCOS_OVER + NET when done. No deploy, no firestore rules deploy, no live writes.

## Board / gates
- UX Designer + Field Tester still required after code PASS (V7 preview https://numista-vault--p7-v7-gate-o3flke1i.web.app still up; re-gate on V8 preview after PASS).
- CORS backend cherry-pick / Eric YES: wait until V8 code PASS.
- Queued P1/P4/P5/P6/P8/P9/P10/P12/P13: Rule 8 WAIT behind P7, not stalls.
