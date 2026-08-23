# Bug Fix Plan v3 — Demo Mode Leak (Feedback f724a3ae)
## Dollar Coins Displaying as Washington Quarters

**Reporter:** charles (seaman_duane@yahoo.com) — 23 AUG 2026
**Feedback ID:** f724a3ae6821626a2779b4faab05bfc9f2f52a8f
**Triage status:** TRIAGED 2026-08-23 20:13 UTC
**Priority:** P1

---

## Decision Matrix — v2 Review

| Source | Suggestion | Decision | Why |
|--------|-----------|----------|-----|
| Gemini | Must-Fix 1: Change _isRealUser gate to _isAuthUser = _currentUser != null (include anonymous) | Rejected | AuthService.coinsPath already handles anonymous users via UID path (auth_service.dart:45). Anonymous users never activate Browse Demo; isBrowseDemoMode is always false for them, so they fall through to Firestore regardless. _isRealUser is semantically correct and more precise. Changing it adds nothing functional. |
| Gemini | Must-Fix 2: Synchronize currency and world_items streams to same auth-primary gate | Adopted | Correct. v2 Fix 1 only updated coinsStream (lines 83-85) and currencyStream (lines 91-93) but missed worldItemsStream (lines 99-101). All three must use the same _isRealUser gate. |
| Gemini | Must-Fix 3: Add @visibleForTesting backdoor in guest_seed_service.dart | Adopted | Required for unit test 2. Grok also required this. |
| Gemini | Must-Fix 4: Clear demo on _signInAsGuest | Rejected | Grok explicitly accepted the decision not to clear on guest sign-in (Grok v2 line 146: "Decision not to clear on _signInAsGuest is right and matches the matrix"). Anonymous users never activate Browse Demo; clearing is a no-op. Adding it violates Rule 5 (no extra features to look complete). Issue is closed. |
| Grok | Must-Fix 1: Assert/clear order inverted — assert fires before clearance in debug builds | Adopted | Correct. Clear + debugPrint first, then assert the postcondition. See Fix 2 BEFORE/AFTER below. |
| Grok | Must-Fix 2: @visibleForTesting backdoor referenced but absent from code changes | Adopted | Added to Fix 4 code in this plan. |
| Grok | Must-Fix 3: clearDemoOnSignIn() is dead code — call sites still use deactivateBrowseDemo() | Adopted | Decision: remove clearDemoOnSignIn(). deactivateBrowseDemo() is the permanent public API. Dead named methods are not contracts, they are confusion. |
| Grok | Note: BaseLayout(isDemoMode: true) reads constructor arg, not static | Confirmed / no action | Banner at base_layout:879 checks widget.isDemoMode || GuestSeedService.isBrowseDemoMode. User navigates away from demo BaseLayout(isDemoMode:true) to LoginScreen before signing in; new BaseLayout() from main.dart has isDemoMode=false. No lingering banner. |
| Grok | Note: getDemoCoinsStream() after clear emits empty snapshot to subscribers | Confirmed / no action needed in code | getDemoCoinsStream() builds from _demoCoinCache (line 93 of guest_seed_service.dart). After deactivateBrowseDemo() sets _demoCoinCache = [], a subsequent call returns Stream.value(DemoQuerySnapshot([])). Already-subscribed listeners see zero docs on next emission. Confirmed correct. |

---

## Confirmed Root Cause (unchanged — evidence stays in every version)

GuestSeedService._browseDemoActive is a static in-memory flag. Once set true
by activateBrowseDemo() (called from _browseDemo() in login_screen.dart:136),
the only clearance points before v3 were inside the _DemoBanner "Try Free"
UI button — an explicit user action. If the user signed in without clicking
that banner, the flag persisted.

home_dashboard.dart:83 (v2 state — still unfixed on disk):
  final coinsStream = GuestSeedService.isBrowseDemoMode
      ? GuestSeedService.getDemoCoinsStream()
      : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
This is flag-primary. A real signed-in user was routed to demo JSON.

Live Firestore evidence (stays in every future version):
  users/seaman_duane@yahoo.com/coins — 4 dollar coins:
    EfDsVvNtOnKQmvHm | Presidential Dollars    | Dollar | 2007 | United States
    hFsHvqbecq3UfyEH | Susan B. Anthony Dollars | Dollar | 1979 | United States
    hbmdaEdOPbM3LQMS | Sacagawea & Native Am.  | Dollar | 2006 | United States
    kFUueEihfApyOP7N | Presidential Dollars    | Dollar | 2008 | United States
  guest_demo_coins.json — 100 demo coins, 17 of denomination "Quarter 25c" (State Quarters)
  The 17 quarters are what the user saw. His dollar coins were invisible.

---

## State Matrix (unchanged from v2 — confirmed correct by Grok)

  State A: No Firebase user, _browseDemoActive = false  -> LoginScreen. Coin stream: N/A.
  State B: No Firebase user, _browseDemoActive = true   -> BaseLayout(isDemoMode:true) via demo path. Coin stream: getDemoCoinsStream().
  State C: Anonymous Firebase user, _browseDemoActive = false -> BaseLayout() via main.dart. Coin stream: Firestore users/{uid}/coins. Flag never set in this path.
  State D: Anonymous user, _browseDemoActive = true     -> INVALID / structurally unreachable. activateBrowseDemo() bypasses Firebase auth. Auth-primary gate makes it safe if reached.
  State E: Real Firebase user, _browseDemoActive = false -> BaseLayout() via main.dart. Coin stream: Firestore users/{email_lowercase}/coins.
  State F: Real Firebase user, _browseDemoActive = true  -> THE BUG STATE. After v3: auth-primary gate forces Firestore; flag cleared by main.dart guard before BaseLayout. Structurally impossible post-fix.

---

## SPA / Navigation Lifetime (unchanged from v2 — confirmed correct by Grok)

Static fields in Dart web live in the isolate for the lifetime of the browser tab.
Not cleared by: widget rebuilds, Navigator pushReplacement, hot-reload, back/forward.
Cleared by: hard browser refresh / page unload.
Service workers: asset-only; statics are per-tab. No cross-boundary leak.
Multiple tabs: each is its own isolate. Independent, acceptable, documented.

---

## What Is Not Changing

- users/{uid}/coins — zero reads, zero writes, zero imports
- passport_pdf_generator.py — protected
- numista_bq_loader_job — protected
- tier_gatekeeper.py — protected (write-prohibition regardless of file presence)
- feedbackIntelligence.js, feedback_callable_route.py — not touched
- guest_seed_service.dart seeding logic for anonymous users (seedIfNeeded) — not touched
- Demo mode user experience — Browse Demo still works exactly as before
- Any Flutter screen other than main.dart, home_dashboard.dart, login_screen.dart

---

## Proposed Changes — 5 Files

=================================================================
Fix 1 — home_dashboard.dart — Auth-primary stream selection,
         all three streams (coins + currency + world_items)
=================================================================

File: numista_mobile/lib/screens/home_dashboard.dart
Method: _getCombinedStream() starting at line 63

v2 missed worldItemsStream (lines 99-101). All three streams must use _isRealUser.

OLD lines 83-101:
  final coinsStream = GuestSeedService.isBrowseDemoMode
      ? GuestSeedService.getDemoCoinsStream()
      : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
  subCoins = coinsStream.listen((snap) {
    coins = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
    emit();
  }, onError: (e) => controller.addError(e));

  final currencyStream = GuestSeedService.isBrowseDemoMode
      ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
      : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();
  subCurrency = currencyStream.listen((snap) {
    currency = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
    emit();
  }, onError: (e) => controller.addError(e));

  final worldItemsStream = GuestSeedService.isBrowseDemoMode
      ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
      : FirebaseFirestore.instance.collection(AuthService.coinsPath.replaceAll('/coins', '/world_items')).snapshots();

NEW lines 83-101:
  // Auth-primary stream selection.
  // A real non-anonymous Firebase user always reads from Firestore,
  // regardless of the in-memory demo flag. The demo branch is only
  // reached when no authenticated user is present (Browse Demo path,
  // State B in the state matrix).
  // Anonymous users (State C) have _browseDemoActive = false by definition
  // (activateBrowseDemo only runs from _browseDemo, which bypasses Firebase auth),
  // so they also fall through to Firestore via AuthService.coinsPath -> users/{uid}/coins.
  final _authUser = FirebaseAuth.instance.currentUser;
  final _isRealUser = _authUser != null && !_authUser.isAnonymous;

  final coinsStream = _isRealUser
      ? FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots()
      : GuestSeedService.isBrowseDemoMode
          ? GuestSeedService.getDemoCoinsStream()
          : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
  subCoins = coinsStream.listen((snap) {
    coins = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
    emit();
  }, onError: (e) => controller.addError(e));

  final currencyStream = _isRealUser
      ? FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots()
      : GuestSeedService.isBrowseDemoMode
          ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
          : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();
  subCurrency = currencyStream.listen((snap) {
    currency = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
    emit();
  }, onError: (e) => controller.addError(e));

  final worldItemsStream = _isRealUser
      ? FirebaseFirestore.instance.collection(AuthService.coinsPath.replaceAll('/coins', '/world_items')).snapshots()
      : GuestSeedService.isBrowseDemoMode
          ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
          : FirebaseFirestore.instance.collection(AuthService.coinsPath.replaceAll('/coins', '/world_items')).snapshots();

_isRealUser is computed once at the top of _getCombinedStream() and reused
for all three stream selections. No double-call.

Note on Gemini Must-Fix 1 (rejected): _isAuthUser = _currentUser != null would
include anonymous users in the auth-primary path, which is functionally identical
because anonymous users never activate Browse Demo (_browseDemoActive is always
false for them). _isRealUser is retained because it is semantically precise and
matches the state matrix, where anonymous (State C) falls through correctly via
the flag check without any code change.


=================================================================
Fix 2 — main.dart — Clear-then-assert order (Grok Must-Fix 1)
=================================================================

File: numista_mobile/lib/main.dart
Lines: 293-298 (current on disk)

Grok v2 Must-Fix 1: assert fires before clearance in debug/profile builds,
causing an abort before deactivateBrowseDemo() runs. The assert message
says "Clearing flag" but the clear never executes in debug mode.
Order must be: clear + log first, then assert the postcondition.

OLD (lines 293-305, current on disk):
  // Signed in -> show welcome screen on first launch, then main app
  if (snapshot.hasData && snapshot.data != null) {
    // If user already dismissed the welcome screen this session,
    // go straight to the main app without re-checking SharedPrefs.
    if (_welcomeDone) {
      return const BaseLayout();
    }

NEW:
  // Signed in -> show welcome screen on first launch, then main app
  if (snapshot.hasData && snapshot.data != null) {
    // INVARIANT: a real Firebase user must never see demo data.
    // Step 1: clear the flag and log (runs in all build modes).
    if (GuestSeedService.isBrowseDemoMode) {
      GuestSeedService.deactivateBrowseDemo();
      debugPrint('[AUTH] Demo mode cleared for real user ${snapshot.data!.uid}');
    }
    // Step 2: assert the postcondition (debug/profile only; stripped in release).
    // Fires AFTER clearance, so the assert message is truthful.
    assert(!GuestSeedService.isBrowseDemoMode,
        'INTEGRITY VIOLATION: Browse Demo still active after clearance attempt. '
        'User: ${snapshot.data!.uid}. This should never fire.');
    // If user already dismissed the welcome screen this session,
    // go straight to the main app without re-checking SharedPrefs.
    if (_welcomeDone) {
      return const BaseLayout();
    }

Why this is correct:
  - In production (--release): assert is stripped. The if-block handles clearance.
  - In debug/profile: if-block clears first, then assert checks the postcondition.
    If deactivateBrowseDemo() somehow fails to clear the flag, the assert fires
    and reports a genuine logic error. The message is now truthful.
  - isBrowseDemoMode is a pure getter (guest_seed_service.dart:22 ->
    static bool get isBrowseDemoMode => _browseDemoActive). No side effects.
  - deactivateBrowseDemo() sets both _browseDemoActive = false and _demoCoinCache = [].
    No listeners to cancel (getDemoCoinsStream() returns Stream.value(), not a live stream).


=================================================================
Fix 3 — login_screen.dart — Deactivate on real sign-in paths only
=================================================================

File: numista_mobile/lib/screens/login_screen.dart

Same as v2 with one addition: _googleSignIn documented.
_signInAsGuest NOT modified (Grok v2 accepted; Gemini Must-Fix 4 rejected above).

OLD _signIn (lines 79-93, current on disk):
  Future<void> _signIn() async {
    final email = _emailCtrl.text.trim();
    final pin   = _pinCtrl.text.trim();
    if (email.isEmpty || pin.isEmpty) {
      setState(() => _error = 'Please enter your email and PIN.');
      return;
    }
    if (pin.length != 6) {
      setState(() => _error = 'Your PIN must be exactly 6 digits.');
      return;
    }
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signIn(email, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

NEW _signIn:
  Future<void> _signIn() async {
    final email = _emailCtrl.text.trim();
    final pin   = _pinCtrl.text.trim();
    if (email.isEmpty || pin.isEmpty) {
      setState(() => _error = 'Please enter your email and PIN.');
      return;
    }
    if (pin.length != 6) {
      setState(() => _error = 'Your PIN must be exactly 6 digits.');
      return;
    }
    // Clear Browse Demo before real sign-in. This is the third clearance
    // point (after main.dart and home_dashboard); it fires before the
    // StreamBuilder receives the auth-state-changed event.
    GuestSeedService.deactivateBrowseDemo();
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signIn(email, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

OLD _googleSignIn (lines 117-121, current on disk):
  Future<void> _googleSignIn() async {
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

NEW _googleSignIn:
  Future<void> _googleSignIn() async {
    GuestSeedService.deactivateBrowseDemo(); // same clearance as _signIn
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

_signInAsGuest (lines 123-132): NOT modified. State C in state matrix; demo flag
  is never set during anonymous sign-in; clearing is a product-incorrect no-op.
  Decision recorded in state matrix and decision table above; closed.

_createAccount (lines 95-115): NOT modified. Routing is handled by StreamBuilder
  after Firebase emits auth state; main.dart Fix 2 guard fires on that event.


=================================================================
Fix 4 — guest_seed_service.dart — Remove dead method, add test backdoor
=================================================================

File: numista_mobile/lib/services/guest_seed_service.dart

Grok Must-Fix 3: clearDemoOnSignIn() is dead code — call sites use deactivateBrowseDemo().
Decision: REMOVE clearDemoOnSignIn(). Do not add it. deactivateBrowseDemo() is the
permanent public API. A named method no call site uses is not a contract, it is confusion.

Grok Must-Fix 2 + Gemini Must-Fix 3: add @visibleForTesting backdoor for unit tests.

OLD (lines 31-34, current on disk):
  static void deactivateBrowseDemo() {
    _browseDemoActive = false;
    _demoCoinCache = [];
  }

NEW (same deactivateBrowseDemo, plus one new method below it):
  static void deactivateBrowseDemo() {
    _browseDemoActive = false;
    _demoCoinCache = [];
  }

  /// FOR TESTS ONLY. Sets the internal demo flag to the given value
  /// so unit tests can exercise clearance logic without requiring
  /// rootBundle (Flutter asset loading) infrastructure.
  @visibleForTesting
  static void setDemoActiveForTest(bool value) {
    _browseDemoActive = value;
    if (!value) _demoCoinCache = [];
  }

Note: clearDemoOnSignIn() from v2 is NOT added. deactivateBrowseDemo() remains
the single public clearance API. No dead code in the committed change set.


=================================================================
Fix 5 — test/guest_seed_service_demo_flag_test.dart [NEW FILE]
=================================================================

File: numista_mobile/test/guest_seed_service_demo_flag_test.dart

Four tests. Uses setDemoActiveForTest() as the backdoor.

  import 'package:flutter_test/flutter_test.dart';
  import 'package:flutter/foundation.dart';
  import 'package:numista_mobile/services/guest_seed_service.dart';

  void main() {
    setUp(() => GuestSeedService.setDemoActiveForTest(false));

    test('1: deactivateBrowseDemo is idempotent', () {
      GuestSeedService.setDemoActiveForTest(true);
      GuestSeedService.deactivateBrowseDemo();
      GuestSeedService.deactivateBrowseDemo();
      GuestSeedService.deactivateBrowseDemo();
      expect(GuestSeedService.isBrowseDemoMode, isFalse);
      expect(GuestSeedService.demoCoinCache, isEmpty);
    });

    test('2: setDemoActiveForTest then deactivate clears both fields', () {
      GuestSeedService.setDemoActiveForTest(true);
      expect(GuestSeedService.isBrowseDemoMode, isTrue);
      GuestSeedService.deactivateBrowseDemo();
      expect(GuestSeedService.isBrowseDemoMode, isFalse);
      expect(GuestSeedService.demoCoinCache, isEmpty);
    });

    test('3: isBrowseDemoMode is a pure getter — no side effects on repeated reads', () {
      GuestSeedService.setDemoActiveForTest(true);
      final r1 = GuestSeedService.isBrowseDemoMode;
      final r2 = GuestSeedService.isBrowseDemoMode;
      final r3 = GuestSeedService.isBrowseDemoMode;
      expect(r1, isTrue);
      expect(r2, isTrue);
      expect(r3, isTrue);
      // Flag must still be true (reads had no side effects)
      expect(GuestSeedService.isBrowseDemoMode, isTrue);
    });

    test('4: getDemoCoinsStream after deactivate emits empty snapshot', () async {
      // After clear, _demoCoinCache = []. getDemoCoinsStream() builds from cache.
      GuestSeedService.deactivateBrowseDemo();
      final snap = await GuestSeedService.getDemoCoinsStream().first;
      expect(snap.docs, isEmpty);
    });
  }

---

## Verification Plan

Automated:
  flutter analyze
  flutter test test/guest_seed_service_demo_flag_test.dart
  Expected: 0 errors, 4 tests pass.

Manual — Primary scenario (must pass):
  1. Open app in fresh browser tab
  2. Click "Browse Demo" — confirm demo coins visible (Washington Quarters in list)
  3. Navigate back to login screen (back button)
  4. Sign in as charles (seaman_duane@yahoo.com) with real credentials
  EXPECTED: 4 dollar coins shown — Presidential x2, Susan B. Anthony, Sacagawea.
  No Washington Quarters. BEFORE FIX: Washington Quarters shown. Confirmed bug.

Manual — Auth-primary gate holds against console manipulation:
  1. Sign in with real account
  2. In browser devtools, attempt to set GuestSeedService._browseDemoActive = true
  3. EXPECTED: home_dashboard sees _isRealUser = true, serves Firestore regardless.

Manual — Demo mode unaffected:
  1. Click "Browse Demo" — 100 demo coins, banner visible
  2. Click "Try Free" banner — returns to LoginScreen
  3. EXPECTED: Demo deactivated, login screen shown. No regression.

Manual — Anonymous guest unaffected:
  1. Click "Continue as Guest"
  2. EXPECTED: Firestore users/{uid}/coins served. Demo flag never set. No change.

Git hygiene:
  git status confirms exactly these files:
    numista_mobile/lib/screens/home_dashboard.dart     (modified)
    numista_mobile/lib/main.dart                       (modified)
    numista_mobile/lib/screens/login_screen.dart       (modified)
    numista_mobile/lib/services/guest_seed_service.dart (modified)
    numista_mobile/test/guest_seed_service_demo_flag_test.dart (new)

---

## Prior Rounds Summary

v1 (23 AUG 2026): 3-file flag-clearance plan. Grok: flag-primary architecture rejected.
v2 (23 AUG 2026): Auth-primary gate added (home_dashboard Fix 1), state matrix, assert,
  4 unit tests spec, SPA docs. Grok: assert order inverted; dead named method; test
  backdoor missing. Gemini: missed worldItemsStream; re-raised closed _signInAsGuest issue.
v3 (this document):
  - worldItemsStream now covered by auth-primary gate (Gemini Must-Fix 2, adopted)
  - Assert/clear order fixed: clear first, assert postcondition (Grok Must-Fix 1, adopted)
  - @visibleForTesting setDemoActiveForTest() added to guest_seed_service.dart (Grok/Gemini)
  - clearDemoOnSignIn() removed — was dead code (Grok Must-Fix 3, adopted)
  - Gemini Must-Fix 1 (_isAuthUser vs _isRealUser) rejected with rationale
  - Gemini Must-Fix 4 (clear on _signInAsGuest) rejected again — issue is closed

---

## Open Questions

None. All Grok Must-Fix items from v1 and v2 resolved. Gemini scope contamination
and re-raised closed items rejected with inline rationale.

Do not mark execution-ready. Owner decides after next Gemini + Grok review pass.
