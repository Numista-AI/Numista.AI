# PLAN P7 V8 — UX, SAFETY, CORS & MOBILE LAYOUT (Plan.v1)
**Date:** 2026-10-15 ~10:15 ET  
**Author:** AG CoS  
**Ref:** `NET-167_GROKCOS-to-AGCOS_P7-V8-ORDERS_OVER.md` | `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`  
**Status:** PLAN.V1 SUBMITTED FOR GROK COS SCORE (DEV ONLY — NO DEPLOY WITHOUT ERIC'S TYPED YES)

---

## 1. Executive Summary & Root Cause Analysis

Following the P7 V7 preview deployment (`https://numista-vault--p7-v7-gate-o3flke1i.web.app`), Field Tester and UX Designer reported blockers across 6 key areas:
1. **Safety:** Bulk checklist `Add Selected Coins` executed a direct backend write without user confirmation, even in signed-out / demo mode.
2. **CORS:** FastAPI backend blocked all requests originating from Firebase Hosting preview channels due to lack of `allow_origin_regex`.
3. **Phone Layout:** Hardcoded 3-column GridView crushed program cards on phones; horizontal Row on Collection Goal card compressed text into 1 character per line; checkbox touch targets and labels were undersized.
4. **Manual Entry:** Form lacked a dedicated full-screen view; Denomination was squeezed into a 3-column row; Qty prefilled '1' caused '11' upon typing; 13px grey labels; missing 56px Save; bottom nav highlighted 'Home' instead of 'My Collection'.
5. **Errors:** Raw technical exceptions (`ClientException: XMLHttpRequest error., uri=...`) leaked into user SnackBars.
6. **Smaller Glitches:** Asset 404s for mint mark diagrams (missing `pubspec.yaml` declaration); Firestore aggregation 403 on `coins_reference` (omitted from `firestore.rules`); Dashboard portfolio value wrap (`$,904.0|2`); 6th PIN box clipped by card padding on narrow devices.

---

## 2. Item-by-Item Remediation Plan

### Item 1: SAFETY — Add Selected Coins Confirm Card & Demo Mode Client Guard
* **Root Cause:**
  - `numista_mobile/lib/screens/program_manager_screen.dart:1439` invokes `_addSelectedCoins` directly on tap.
  - `_addSelectedCoins` (line 1706) executes `HttpAuthClient.post` without checking demo mode (`GuestSeedService.isBrowseDemoMode`) or authentication status (`FirebaseAuth.instance.currentUser`).
* **Design & Changes:**
  1. **Confirm Modal Card:** Replace immediate POST with `_showAddSelectedCoinsConfirmDialog(BuildContext context, CoinProgram program, List<Map<String, String>> slots)`.
     - Displays program title, number of coins selected, and scrollable list/chips of selected slots (Year, Mint, Denomination).
     - Provides clear primary **"Save to Collection"** button and secondary **"Cancel"** button.
     - On "Cancel", dismisses dialog with no state change and zero network calls.
  2. **Client Guard for Demo Mode:**
     - Before opening confirm or making any POST, evaluate:
       ```dart
       final authUser = FirebaseAuth.instance.currentUser;
       final isRealUser = authUser != null && !authUser.isAnonymous;
       if (!isRealUser || GuestSeedService.isBrowseDemoMode) {
         ScaffoldMessenger.of(context).showSnackBar(
           const SnackBar(
             content: Text('Browse Demo Mode: Sign in to save coins to your collection.'),
             backgroundColor: Color(0xFFF59E0B),
           ),
         );
         return;
       }
       ```
     - Guarantee: Zero write requests are dispatched to `/api/checklist/add_coins` while signed out or in demo mode.
  3. **Backend Default-Deny Verification:**
     - Verify and prove via backend test that `/api/checklist/add_coins` requires a valid Bearer token and rejects unauthenticated requests with `401 Unauthorized`.
* **Tests Planned:**
  - Widget test: `testWidgets('Add Selected Coins shows confirm dialog with Save and Cancel')`.
  - Widget test: `testWidgets('Cancelling Add Selected Coins does not fire write')`.
  - Widget test: `testWidgets('Demo mode suppresses network write and shows informative message')`.
  - Backend test in `test_checklist_routes.py`: `test_checklist_add_coins_unauthenticated_returns_401()`.

---

### Item 2: CORS — Allow Preview Channels & spot_prices Explanation
* **Root Cause:**
  - `numista_backend/main.py:60-66` configures `CORSMiddleware` with `allow_origins=ALLOWED_ORIGINS` containing only static production and local domains.
  - Preview channels have dynamic subdomains (e.g. `https://numista-vault--p7-v7-gate-o3flke1i.web.app`). When missing `allow_origin_regex`, Starlette/FastAPI CORS middleware rejects the origin with `HTTP 400 Disallowed CORS origin`.
* **Design & Changes:**
  - In `numista_backend/main.py`:
    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_origin_regex=r"^https://numista-vault--[a-z0-9-]+\.web\.app$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```
* **Why live `spot_prices` appeared CORS-blocked to Field Tester:**
  - Direct live probe via `curl` against `https://numista-backend-568985927038.us-central1.run.app/api/spot_prices` with `Origin: https://numista.ai` returns `HTTP/1.1 200 OK` and `access-control-allow-origin: https://numista.ai`. Live production is **NOT** CORS-blocked.
  - The Field Tester opened the **preview channel**, where the browser sent `Origin: https://numista-vault--p7-v7-gate-o3flke1i.web.app`. Because the backend had no preview regex, **every single backend call from the preview site** (including `/api/spot_prices` and `/api/checklist/add_coins`) failed CORS. Once the regex is added, preview channels operate smoothly.
* **Tests Planned:**
  - Unit test in `numista_backend/tests/test_cors_public_paths.py`: Test OPTIONS and GET for `Origin: https://numista-vault--p7-v7-gate-o3flke1i.web.app` assert `access-control-allow-origin` matches origin and status is 200.

---

### Item 3: Phone Layout in `program_manager_screen.dart`
* **Root Cause:**
  - Lines 468 & 598: `crossAxisCount: 3` with `childAspectRatio: 1.4` hardcoded across all form factors.
  - Line 975: Goal card wraps Icon, Expanded Column, wide Dropdown, and Switch in a single horizontal `Row`. On 360-400px viewports, the column is crushed to under 40px width, causing 1-character-per-line vertical text wrapping.
  - Lines 1385-1415: Checkbox in `SizedBox(width: 20, height: 20)` with `12px` grey text (`Color(0xFF475569)`).
* **Design & Changes:**
  1. **Responsive Program Cards:**
     - Check `final isCompact = MediaQuery.of(context).size.width < 650;`
     - On compact: `crossAxisCount: 1`, `childAspectRatio: 2.6` (full width, single card per row), or vertical column list. On desktop: retain 3 columns.
  2. **Set Collection Goal Card:**
     - On compact viewports, replace horizontal `Row` with vertical `Column`:
       - Header row: Icon + Title + Subtitle.
       - Full-width dropdown container with `isExpanded: true`.
       - Clean bottom row for the Manual Complete toggle switch with label.
  3. **Check Targets & Labels:**
     - Wrap coin selection chips with `constraints: const BoxConstraints(minHeight: 48, minWidth: 48)` and padding `horizontal: 10, vertical: 8`.
     - Update chip label style to `fontSize: 16, fontWeight: FontWeight.w600, color: Color(0xFF0F172A)` (dark, readable text).
* **Tests Planned:**
  - Widget test with 375x812 viewport: verify program cards render 1 per row, goal card headers do not overflow/wrap 1-char, checkbox tap target is >= 48px.

---

### Item 4: Manual Entry Screen & Usability
* **Root Cause:**
  - `add_coins_hub.dart:631`: "Type it in" expands the tab bar into tab index 2 rather than presenting a dedicated full screen.
  - `add_coin_manual_form.dart:34, 186`: `Quantity` initialized to `'1'` in form data map and passed as `initialValue`; user typing '1' results in `'11'`.
  - `add_coin_manual_form.dart:66-73`: 3 fields (`Year`, `Mint Mark`, `Denomination`) crammed into one Row.
  - `add_coin_manual_form.dart:205`: Labels are 13px grey (`Color(0xFF64748B)`).
  - `add_coin_manual_form.dart:109-129`: Save button lacks fixed 56px height.
  - `base_layout.dart:561`: Active route `'Add New Coins'` is not in `mobileRoutes` list, so `indexOf` returns `-1`, which `clamp(0, 4)` forces to `0` (highlighting 'Home').
* **Design & Changes:**
  1. **Dedicated Full Screen:**
     - In `AddCoinsHub`, add `showManualFullScreen: true` (mirroring `showCertFullScreen: true`).
     - "Type it in" `_QuickAddCard` navigates to `AddCoinsHub(showManualFullScreen: true)` in a dedicated Scaffold with clean App Bar, back button, and zero distracting tabs.
  2. **Fix Qty Prefill Bug:**
     - Do not prefill `'1'` as `initialValue` text. Provide `hintText: '1'` and default to `1` upon submission if left blank, or manage with a dedicated `TextEditingController` that selects all text on focus.
  3. **Field Layout & Numeric Keyboards:**
     - Row 1: Year (flex 1) + Mint Mark (flex 1).
     - Row 2: Denomination (full width, never cut off).
     - Set `keyboardType: TextInputType.number` (or `numberWithOptions(decimal: true)` for Cost) to trigger numeric inputmode on mobile and web.
  4. **Form Labels & Required Fields:**
     - Labels: `fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)`.
     - Required indicators: Mark `Year *`, `Denomination *`, `Program/Series *` with distinct asterisk styling.
  5. **56px Save Button:**
     - Enforce `minimumSize: const Size(double.infinity, 56)` with `styleFrom(shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)))` labeled **"Save to My Collection"**.
  6. **Bottom Nav Highlight:**
     - In `base_layout.dart:561`: Map `'Add New Coins'` to index `2` (`'My Collection'`) instead of defaulting to `0` (`'Home'`).
* **Tests Planned:**
  - Widget test: verify `showManualFullScreen` renders bare Scaffold without TabBar.
  - Widget test: verify Qty typing '1' produces '1', not '11'.
  - Widget test: verify bottom nav selects index 2 when active route is `'Add New Coins'`.

---

### Item 5: Plain-English Errors
* **Root Cause:**
  - `program_manager_screen.dart:1828` catches network errors and shows `'Network error adding coins: $e'`.
  - `add_coins_hub.dart:4039` sets `_pcgsLookupError = e.toString().replaceFirst('Exception: ', '')`.
  - Flutter web `http.ClientException` exposes `XMLHttpRequest error., uri=https://numista-backend-...` to end users.
* **Design & Changes:**
  - Implement a clean error translation helper `NumistaErrorHelper.toUserFriendly(dynamic error)`:
    - If error contains `ClientException`, `XMLHttpRequest`, `SocketException`, `Failed host lookup`, or `Connection refused`:
      `"Unable to connect to the server. Please check your internet connection and try again."`
    - If HTTP 401: `"Your session expired. Please sign in again to continue."`
    - If HTTP 500/503: `"Server is temporarily unavailable. Please try again shortly."`
    - Strip all raw URIs, URLs, and stack traces.
* **Tests Planned:**
  - Unit test verifying `NumistaErrorHelper` maps `ClientException(uri=...)` to plain English without URLs.

---

### Item 6: Smaller Fixes
1. **Mint Mark Diagrams 404 (`/assets/assets/...`):**
   - **Root Cause:** `numista_mobile/assets/mint_mark_diagrams/` directory exists on disk, but was omitted from `pubspec.yaml` `assets:` section.
   - **Fix:** Add `- assets/mint_mark_diagrams/` to `numista_mobile/pubspec.yaml`.
2. **Firestore Aggregation 403:**
   - **Root Cause:** `program_manager_screen.dart:295` calls `FirebaseFirestore.instance.collection('coins_reference').count().get()`, but `coins_reference` was absent from `numista_mobile/firestore.rules`, hitting `match /{document=**} { allow read, write: if false; }`.
   - **Fix:** Add public read rule for reference data in `firestore.rules`:
     ```firestore
     match /coins_reference/{document=**} {
       allow read: if true;
       allow write: if false;
     }
     ```
     Also wrap `_loadTotalReferenceCount()` in a silent fallback guard so any read error defaults cleanly to the seeded 2834 count.
3. **Dashboard `,904.0|2` Portfolio Value Wrap:**
   - **Root Cause:** `home_dashboard.dart:1271` renders 36px font in an unconstrained flex column without `FittedBox` or single-line constraint.
   - **Fix:** Wrap value `Text` in `FittedBox(fit: BoxFit.scaleDown, alignment: Alignment.centerRight)` with `maxLines: 1`.
4. **Clipped 6th PIN Box:**
   - **Root Cause:** `login_screen.dart:1426`: 6 boxes of width 48px + 8px margin require 336px. On 360px phones with 24px left/right card padding (312px available), the 6th box overflows by 24px.
   - **Fix:** Wrap `_PinBoxRow` in `FittedBox(fit: BoxFit.scaleDown)` and adjust margins/widths responsively (`margin: EdgeInsets.symmetric(horizontal: 2.5)`).

---

## 3. Test & Verification Plan

1. **Backend Tests:**
   - `pytest numista_backend/tests/test_cors_public_paths.py` (CORS preview regex).
   - `pytest numista_backend/tests/test_checklist_routes.py` (401 unauthenticated check).
2. **Flutter Tests:**
   - `flutter test test/screens/program_manager_screen_test.dart`
   - `flutter test test/widgets/add_coin_manual_form_test.dart`
   - `flutter test test/screens/add_coins_hub_p7_v7_test.dart`
   - Full suite `flutter test`.
   - `flutter analyze` confirming 0 issues.
3. **Review & Gate:**
   - AG CoS files `GEMINI38_REVIEW_P7_V8_BUILD.md` with verbatim code lines before handing baton.
   - Preview re-deploy on Firebase channel for UX Designer + Field Tester gate.
   - Live deploy strictly gated on Eric's typed YES.

---
**END OF PLAN P7 V8**
