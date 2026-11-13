# GEMINI 3.8 BUILD REVIEW — TRACK P7 V8 (UX, SAFETY, CORS, PHONE LAYOUT)
**Reviewer:** AG CoS (Gemini 3.8)
**Date:** 2026-10-15 ~11:10 ET
**Reviewed Branch:** `dev`
**Status:** **BUILD PASS (Dev Only)**

Per GEMINI REVIEW RULES (Eric 13 Oct 2026): Every `file:line` citation includes the verbatim changed code lines.

---

### Condition 1 — Safety: Confirm Card + Demo Guard + 401 Test
- **Inside `_addSelectedCoins` (Guard at write level):**
  `numista_mobile/lib/screens/program_manager_screen.dart:1795-1808`
  ```dart
    final authUser = FirebaseAuth.instance.currentUser;
    final isRealUser = authUser != null && !authUser.isAnonymous;
    if (!isRealUser || GuestSeedService.isBrowseDemoMode) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Sign in to add coins to your collection.'),
            backgroundColor: Color(0xFFF59E0B),
          ),
        );
      }
      return;
    }
  ```
- **Confirm Card Dialog before write:**
  `numista_mobile/lib/screens/program_manager_screen.dart:1747-1793`
  ```dart
  Future<void> _confirmAddSelectedCoins() async {
    final authUser = FirebaseAuth.instance.currentUser;
    final isRealUser = authUser != null && !authUser.isAnonymous;
    if (!isRealUser || GuestSeedService.isBrowseDemoMode) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Sign in to add coins to your collection.'),
            backgroundColor: Color(0xFFF59E0B),
          ),
        );
      }
      return;
    }

    if (_selectedToAdd.isEmpty) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text(
          'Add to Collection?',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
        ),
        content: Text(
          'Are you sure you want to add ${_selectedToAdd.length} selected coin${_selectedToAdd.length == 1 ? '' : 's'} to your collection?',
          style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 15),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 16)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            ),
            child: const Text('Add Coins', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      await _addSelectedCoins();
    }
  }
  ```
- **Button wired to confirm dialog:**
  `numista_mobile/lib/screens/program_manager_screen.dart:1483`
  ```dart
  onPressed: _isSavingCoins ? null : _confirmAddSelectedCoins,
  ```
- **Backend 401 unauthenticated default-deny test:**
  `numista_backend/tests/test_cors_public_paths.py:100-111`
  ```python
  def test_checklist_add_coins_unauthenticated_returns_401(client, monkeypatch):
      monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)
      response = client.post(
          "/api/checklist/add_coins",
          json={
              "idempotency_key": "test-key-401",
              "program_id": "50sq",
              "program_name": "50 State Quarters",
              "user_email": "unauth@example.com",
              "slots": [{"coin_name": "Delaware", "year": "1999", "mint_mark": "P"}],
          },
      )
      assert response.status_code == 401
  ```
- **Widget test proving zero HTTP calls on Cancel & in demo mode:**
  `numista_mobile/test/p7_v8_ux_safety_test.dart:121-209` (tests `p7_v8_confirm_dialog_cancel_makes_zero_http_calls` and `p7_v8_demo_mode_guard_makes_zero_http_calls` pass with `httpCallCount == 0`).

---

### Condition 2 — CORS: Preview Regex + Shared `_is_allowed_origin` + Negative Tests
- **Regex & Shared Helper:**
  `numista_backend/main.py:60-70`
  ```python
  ALLOWED_ORIGIN_REGEX = r"^https://numista-vault--[a-z0-9-]+\.web\.app$"
  _allowed_origin_re = re.compile(ALLOWED_ORIGIN_REGEX)

  def _is_allowed_origin(origin: str) -> bool:
      if not origin:
          return False
      if origin in ALLOWED_ORIGINS:
          return True
      if _allowed_origin_re.fullmatch(origin):
          return True
      return False
  ```
- **CORSMiddleware configuration:**
  `numista_backend/main.py:72-79`
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=ALLOWED_ORIGINS,
      allow_origin_regex=ALLOWED_ORIGIN_REGEX,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- **Hand-rolled CORS in `identify_group_photo` updated:**
  `numista_backend/main.py:5589-5593`
  ```python
      is_allowed = _is_allowed_origin(req_origin)
      cors_origin = req_origin if is_allowed else ("*" if not req_origin else ALLOWED_ORIGINS[0])
      cors_headers = {
          "Access-Control-Allow-Origin": cors_origin,
          "Access-Control-Allow-Credentials": "true" if is_allowed else "false",
  ```
- **Tests: 1 positive preview + 4 negative origin tests:**
  `numista_backend/tests/test_cors_public_paths.py:60-98`
  ```python
  def test_firebase_preview_origin_allowed(client):
      origin = "https://numista-vault--pr315-gk4b9x.web.app"
      response = client.options("/api/coins", headers={"Origin": origin, "Access-Control-Request-Method": "GET"})
      assert response.headers.get("access-control-allow-origin") == origin

  @pytest.mark.parametrize("evil_origin", [
      "https://numista-vault--x.web.app.evil.com",
      "https://evil-numista-vault--x.web.app",
      "http://numista-vault--x.web.app",
      "https://other-site--x.web.app",
  ])
  def test_negative_origins_rejected(client, evil_origin):
      response = client.options("/api/coins", headers={"Origin": evil_origin, "Access-Control-Request-Method": "GET"})
      assert response.headers.get("access-control-allow-origin") != evil_origin
  ```

---

### Condition 3 — Phone Layout: Responsive Cards + 48px Touch Targets + 16px Labels
- **Responsive Program Cards Grid:**
  `numista_mobile/lib/screens/program_manager_screen.dart:464`
  ```dart
  final isNarrow = MediaQuery.of(context).size.width < 650;
  ```
  `numista_mobile/lib/screens/program_manager_screen.dart:550-552`
  ```dart
  crossAxisCount: isNarrow ? 1 : 3,
  childAspectRatio: isNarrow ? 2.6 : 1.4,
  ```
- **Responsive Goal Card:**
  `numista_mobile/lib/screens/program_manager_screen.dart:676-712`
  ```dart
  isNarrow
      ? Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ...
          ],
        )
      : Row(...)
  ```
- **Checklist Rows 48px touch target & 16px label floor:**
  `numista_mobile/lib/screens/program_manager_screen.dart:1367-1376` (Year label):
  ```dart
  SizedBox(
    width: 52,
    child: Text(
      slot.year.isEmpty ? '—' : slot.year,
      style: const TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: Color(0xFF0F172A),
      ),
    ),
  ),
  ```
  `numista_mobile/lib/screens/program_manager_screen.dart:1418-1445` (Missing checkbox chip with 48px target & 16px text):
  ```dart
  return ConstrainedBox(
    constraints: const BoxConstraints(minHeight: 48, minWidth: 48),
    child: InkWell(
      borderRadius: BorderRadius.circular(6),
      onTap: () { ... },
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 24,
              height: 24,
              child: Checkbox(
                value: isSelected,
                onChanged: (bool? value) { ... },
                activeColor: const Color(0xFF3B82F6),
              ),
            ),
            const SizedBox(width: 6),
            Text(
              chipLabel,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Color(0xFF0F172A),
              ),
            ),
          ],
        ),
      ),
    ),
  );
  ```

---

### Condition 4 — Manual Entry: Full Screen + Form Bug Fixes + Bottom Nav
- **Full-Screen Dedicated Scaffold:**
  `numista_mobile/lib/screens/add_coins_hub.dart:601-609`
  ```dart
    if (widget.showManualFullScreen) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Add Coin Manually'),
          leading: const BackButton(),
        ),
        body: _buildManualEntryTab(),
      );
    }
  ```
- **"Type it in" QuickAddCard routes directly to dedicated screen:**
  `numista_mobile/lib/screens/add_coins_hub.dart:636-646`
  ```dart
        _QuickAddCard(
          icon: Icons.keyboard_outlined,
          label: 'Type it in',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => AddCoinsHub(
                  showManualFullScreen: true,
                  initialCoinPreset: widget.initialCoinPreset,
                ),
              ),
            );
          },
        ),
  ```
- **Qty Bug Fix (hintText '1', default '1' on blank submit):**
  `numista_mobile/lib/widgets/add_coin_manual_form.dart:34`
  ```dart
  'Quantity': '',
  ```
  `numista_mobile/lib/widgets/add_coin_manual_form.dart:170-173`
  ```dart
      // Qty prefill bug fix: default to '1' if left blank
      final qtyStr = _formData['Quantity']?.toString().trim() ?? '';
      _formData['Quantity'] = qtyStr.isEmpty ? '1' : qtyStr;
  ```
- **Keyboards & Full-Width Denomination Row:**
  `numista_mobile/lib/widgets/add_coin_manual_form.dart:73-98`
  ```dart
          Row(children: [
            Expanded(
              child: _buildField(
                context,
                'Year',
                'e.g. 1921',
                isRequired: true,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMintMarkField(context),
            ),
          ]),
          const SizedBox(height: 12),
          _buildField(
            context,
            'Denomination',
            'e.g. Quarter Dollar, Dime, Cent',
            isRequired: true,
          ),
  ```
- **18px Bold Dark Labels with `*` Required Indicator:**
  `numista_mobile/lib/widgets/add_coin_manual_form.dart:223-247`
  ```dart
          RichText(
            text: TextSpan(
              text: key,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: labelColor,
              ),
              children: isRequired
                  ? const [
                      TextSpan(
                        text: ' *',
                        style: TextStyle(
                          color: Color(0xFFEF4444),
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ]
                  : null,
            ),
          ),
  ```
- **56px Save Button:**
  `numista_mobile/lib/widgets/add_coin_manual_form.dart:142-163`
  ```dart
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton.icon(
              onPressed: widget.isProcessing ? null : _submit,
              icon: widget.isProcessing
                  ? const SizedBox(
                      height: 20, width: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check_circle_outline, size: 20),
              label: Text(
                widget.isProcessing ? 'Saving…' : 'Save to My Collection',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _accent,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 56),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ),
  ```
- **Bottom Nav Highlight for 'Add New Coins' -> Index 2 (My Collection):**
  `numista_mobile/lib/screens/base_layout.dart:561-569`
  ```dart
    int effectiveIndex = mobileRoutes.indexOf(_activeRoute);
    if (effectiveIndex == -1) {
      if (_activeRoute == 'Add New Coins') {
        effectiveIndex = 2; // Map 'Add New Coins' to 'My Collection' tab
      } else {
        effectiveIndex = 0;
      }
    }
    final currentIndex = effectiveIndex.clamp(0, 4);
  ```

---

### Condition 5 — Plain-English Errors
- **`NumistaErrorHelper` Central Translation Utility:**
  `numista_mobile/lib/utils/numista_error_helper.dart:7-25`
  ```dart
  class NumistaErrorHelper {
    static String toUserFriendly(dynamic error, {int? statusCode, String? fallback}) {
      if (statusCode == 401) {
        return 'Your session expired or sign-in is required. Please sign in to continue.';
      }
      if (statusCode == 403) {
        return 'Access denied. You do not have permission to perform this action.';
      }
      if (statusCode != null && statusCode >= 500) {
        return 'Server is temporarily unavailable. Please try again in a few moments.';
      }

      if (error == null) {
        return fallback ?? 'An unexpected error occurred. Please try again.';
      }

      if (error is http.ClientException) {
        return 'Unable to connect to the server. Please check your internet connection and try again.';
      }
  ```
- **Sites Replaced with `NumistaErrorHelper`:**
  1. `numista_mobile/lib/screens/program_manager_screen.dart:1931`:
     `content: Text(NumistaErrorHelper.toUserFriendly(response.body, statusCode: response.statusCode)),`
  2. `numista_mobile/lib/screens/program_manager_screen.dart:1940`:
     `content: Text(NumistaErrorHelper.toUserFriendly(e)),`
  3. `numista_mobile/lib/screens/add_coins_hub.dart:571`:
     `content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Failed to save coin. Please try again.')),`
  4. `numista_mobile/lib/screens/add_coins_hub.dart:2445`:
     `content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Failed to add SKU. Please try again.')),`
  5. `numista_mobile/lib/screens/add_coins_hub.dart:3408`:
     `content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Couldn\'t save coin. Please try again.')),`
  6. `numista_mobile/lib/screens/add_coins_hub.dart:4059`:
     `_pcgsLookupError = NumistaErrorHelper.toUserFriendly(e, fallback: 'Cert lookup failed. Please verify the cert number and try again.');`

---

### Condition 6 — Smaller Fixes
- **6a: `pubspec.yaml` Mint Mark Diagrams:**
  `numista_mobile/pubspec.yaml:90`
  ```yaml
      - assets/mint_mark_diagrams/
  ```
- **6b: `firestore.rules` Public Read for Catalog-only `coins_reference`:**
  `numista_mobile/firestore.rules:165-170`
  ```firestore
    // ── Coins reference (reference library — public read, no writes from client) ─
    match /coins_reference/{document=**} {
      allow get, list: if true;
      allow write: if false;  // backend service account only
    }
  ```
  *Audit Confirmation:* `coins_reference` contains only public catalog reference data (program specifications, coin mintages, variety registry). Zero user emails, tokens, or collection records exist in this collection.
  *Note:* Deployed file is `numista_mobile/firestore.rules`. `numista_backend/firestore.rules` is legacy/stale. Changes are committed to dev only; NO firestore rules deployment without Eric's typed YES.
- **6c: `home_dashboard.dart` Value FittedBox & NumberFormat:**
  `numista_mobile/lib/screens/home_dashboard.dart:1271-1282`
  ```dart
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerRight,
            child: Text(
              fmt.format(displayVal),
              maxLines: 1,
              style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.w900,
                  color: _accent),
            ),
          ),
  ```
- **6d: `login_screen.dart` PIN Box Row FittedBox:**
  `numista_mobile/lib/screens/login_screen.dart:1423-1440`
  ```dart
    return FittedBox(
      fit: BoxFit.scaleDown,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(6, (i) {
          return Container(
            width: 44,
            height: 50,
            margin: const EdgeInsets.symmetric(horizontal: 3),
  ```

---

### Condition 7 — Automated Test Verification
- **Flutter Analyze:** `flutter analyze` -> `No issues found! (ran in 30.0s)`. Exit code 0.
- **Flutter Widget Tests:** `flutter test test/p7_v8_ux_safety_test.dart` -> `00:10 +8: All tests passed!`. Exit code 0.
- **Pytest Backend Tests:** `python -m pytest numista_backend/tests/test_cors_public_paths.py` -> `14 passed in 46.11s`. Exit code 0.

### Recommendation
Build is verified, compliant with all 7 conditions, dev-only, and ready for Grok CoS build scoring. Passing baton to `GROKCOS_OVER`.
