# NET-172 AGCOS to GROKCOS: P7 V8 Build Complete - Baton to You for Score - OVER
Time: 2026-10-15 ~11:15 ET.

## Track P7 V8 Build Complete (Dev Only)
All 7 conditions from `COS_SCORE_P7_ADD-COINS-FLOW_V8_PLAN_V1.md` and `NET-169` have been built and verified:

1. **Safety:**
   - Confirm card dialog before write (`_confirmAddSelectedCoins`).
   - Signed-out / demo mode client guard placed directly inside `_addSelectedCoins` (POST level).
   - Double-tap guard disabled upon first tap (`_isSavingCoins`).
   - `test_checklist_add_coins_unauthenticated_returns_401` in pytest (exit code 0).
   - Widget tests verify strictly 0 HTTP calls on Cancel and in demo mode.

2. **CORS:**
   - `ALLOWED_ORIGIN_REGEX = r"^https://numista-vault--[a-z0-9-]+\.web\.app$"` added in `main.py`.
   - Shared `_is_allowed_origin(origin)` helper created and used in both `CORSMiddleware(allow_origin_regex=...)` and `identify_group_photo` (line 5589).
   - 1 positive preview test + 4 negative origin tests (`evil.com`, `evil-numista`, `http://`, `other-site`) in `test_cors_public_paths.py` (14/14 passed).

3. **Phone Layout:**
   - Responsive Program Cards grid: 1-col on `< 650px`, 3-col on desktop.
   - Responsive Goal card: vertical Column on mobile, Row on desktop.
   - 48px touch targets for checkbox rows.
   - 16px minimum dark labels (`Color(0xFF0F172A)`) across all checklist rows.

4. **Manual Entry:**
   - Dedicated full-screen Scaffold (`showManualFullScreen: true`) in `AddCoinsHub` with clean AppBar and back button.
   - "Type it in" QuickAddCard routes directly to full-screen manual entry.
   - 18px dark bold labels with distinct `*` indicator on required fields (`Year`, `Denomination`, `Program/Series`).
   - Full-width row for Denomination; Year/Qty numeric keypad; Cost decimal keypad.
   - Qty prefill bug fixed: `hintText: '1'`, default `1` on blank submit, typing `1` yields `1` (never `11`).
   - 56px height Save button labeled "Save to My Collection".
   - Bottom nav maps `'Add New Coins'` to index 2 (`'My Collection'`).

5. **Plain-English Errors:**
   - Created `NumistaErrorHelper` type-checking `http.ClientException` (web-safe) and status codes 401/403/500, stripping internal URLs and technical jargon.
   - Replaced raw `$e`/`e.toString()` across user-visible SnackBars/dialogs in `program_manager_screen.dart` and `add_coins_hub.dart`.

6. **Smaller Fixes:**
   - 6a: `pubspec.yaml` added `- assets/mint_mark_diagrams/`.
   - 6b: `firestore.rules` added `match /coins_reference/{document=**} { allow get, list: if true; allow write: if false; }`. Confirmed catalog-only reference data (0 user info). Committed to dev only; NO firestore rules deploy without Eric's typed YES.
   - 6c: `home_dashboard.dart` portfolio values wrapped in `FittedBox` with `maxLines: 1` + `NumberFormat`.
   - 6d: `login_screen.dart` `PinBoxRow` wrapped in `FittedBox`, tested at 320px width (all 6 boxes visible, no overflow).

7. **Verification:**
   - `flutter analyze` -> `No issues found! (ran in 30.0s)`.
   - `flutter test test/p7_v8_ux_safety_test.dart` -> 8/8 passed.
   - `python -m pytest numista_backend/tests/test_cors_public_paths.py` -> 14 passed.
   - `python -m pytest numista_backend/tests/test_checklist_routes.py` -> 1 passed.

## Reviews & Baton
- `GEMINI38_REVIEW_P7_V8_BUILD.md` filed with verbatim code lines per file:line cite.
- Baton renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`.
- Dev branch pushed cleanly to `origin/dev`.

OVER
