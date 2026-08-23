# Bug Fix Plan v2 — Demo Mode Leak (Feedback f724a3ae)
## Dollar Coins Displaying as Washington Quarters

**Reporter:** charles (seaman_duane@yahoo.com) — 23 AUG 2026
**Feedback ID:** f724a3ae6821626a2779b4faab05bfc9f2f52a8f
**Triage status:** TRIAGED 2026-08-23 20:13 UTC
**Priority:** P1

---

## Decision Matrix

| Source | Suggestion | Decision | Why |
|--------|-----------|----------|-----|
| Gemini | Adopt demo clearance hook (deactivateBrowseDemo on real auth) | Adopted — already in v1 | Correct mechanism; carried forward |
| Gemini | Must-Fix: normalize auth email paths in coinsPath getters | Rejected | AuthService.coinsPath line 46 already calls .toLowerCase() on email. No gap exists. |
| Gemini | Target files include passport_pdf_generator.py, numista_bq_loader_job, tier_gatekeeper.py | Rejected | Not touched by this bug fix. Gemini is bleeding scope from prior plan rounds. |
| Gemini | Segregate currency/world_items from coins in estate math | Rejected | Out of scope for this specific bug. No code path in this fix touches estate PDFs. |
| Grok | Must-Fix 1: stream selection must be auth-primary, not flag-primary | Adopted | Correct. home_dashboard.dart:83 now gates on real user presence, not flag state. |
| Grok | Must-Fix 2: explicit state matrix for demo/guest/real-user combinations | Adopted | Matrix written below. |
| Grok | Must-Fix 3: assert/debug log if demo active while real user present | Adopted | assert + debugPrint added at StreamBuilder decision point. |
| Grok | Must-Fix 4: at least one unit test for flag lifecycle | Adopted | Unit test spec written below. |
| Grok | Must-Fix 5: document SPA/navigation lifetime of static flag | Adopted | Documented in SPA section below. |
| Grok | Push-back: do not clear demo on _signInAsGuest | Adopted | Correct. Anonymous user routes to users/{uid}/coins (UID-based, isolated). Demo flag is never set during an anonymous session — clearDemoOnSignIn should NOT fire. |
| Grok | Push-back: treat flag as not merely "cleared" but stream as auth-primary | Adopted | Full architectural change applied (see Fix 1 below). |

---

## Confirmed Root Cause (unchanged from v1 — evidence stays)

GuestSeedService._browseDemoActive is a static in-memory flag. Once set true by
the Browse Demo path, the only clearance points are inside the _DemoBanner "Try Free"
UI button callback. If the user signs in without clicking that banner, the flag persists.

home_dashboard.dart:83 decides the coin stream by asking the flag first:
  GuestSeedService.isBrowseDemoMode ? getDemoCoinsStream() : FirebaseFirestore...

This is wrong even with clearance applied: the decision model is flag-primary, not
auth-primary. A real non-null non-anonymous Firebase user must always see Firestore.
The flag may only be consulted when there is no real user.

Live Firestore evidence (unchanged, stays in every future version):
  users/seaman_duane@yahoo.com/coins — 4 dollar coins:
    EfDsVvNtOnKQmvHm | Presidential Dollars    | Dollar | 2007 | United States
    hFsHvqbecq3UfyEH | Susan B. Anthony Dollars | Dollar | 1979 | United States
    hbmdaEdOPbM3LQMS | Sacagawea & Native Am.  | Dollar | 2006 | United States
    kFUueEihfApyOP7N | Presidential Dollars    | Dollar | 2008 | United States
  guest_demo_coins.json — 100 demo coins, 17 of denomination "Quarter 25c" (State Quarters)
  The 17 quarters are what the user saw. His dollar coins were invisible.

---

## State Matrix — Browse Demo / Anonymous Guest / Real User

  State A: No Firebase user, _browseDemoActive = false
    -> Show LoginScreen (main.dart:369)
    -> Coin stream: N/A

  State B: No Firebase user, _browseDemoActive = true (Browse Demo path)
    -> BaseLayout(isDemoMode: true) via Navigator.pushReplacement (login_screen:141)
    -> Coin stream: getDemoCoinsStream() from in-memory JSON cache
    -> _DemoBanner visible; "Try Free" clears flag and returns to LoginScreen

  State C: Firebase Anonymous user, _browseDemoActive = false (normal guest path)
    -> BaseLayout() via main.dart:298/359
    -> Coin stream: Firestore users/{uid}/coins (UID-based, isolated per guest session)
    -> Demo flag is never set during an anonymous sign-in path; no clearance needed

  State D: Firebase Anonymous user, _browseDemoActive = true (INVALID / BUG CLASS)
    -> Cannot occur naturally: activateBrowseDemo() is only called from _browseDemo()
       which uses Navigator.pushReplacement (no Firebase auth). Anonymous auth
       sets _browseDemoActive = false because deactivateBrowseDemo is not called,
       but the flag would be false from the start of the anonymous path.
    -> If somehow reached: auth-primary gate (Fix 1) forces Firestore, flag ignored.

  State E: Real (non-anonymous, non-null) Firebase user, _browseDemoActive = false
    -> BaseLayout() via main.dart:298/359
    -> Coin stream: Firestore users/{email_lowercase}/coins

  State F: Real Firebase user, _browseDemoActive = true (THE BUG STATE)
    -> Before fix: getDemoCoinsStream() served; user sees demo quarters not dollar coins
    -> After fix: auth-primary gate catches real user; Firestore served regardless of flag;
       flag also cleared by StreamBuilder guard before BaseLayout is constructed

  Allowed terminal states: A, B, C, E.
  States D and F are invalid; Fix 1 makes F impossible and documents D as structurally unreachable.

---

## SPA / Navigation Lifetime of the Static Flag

Static fields in Dart web (Flutter Web) live in the Dart VM's single isolate
for the lifetime of the browser tab. They are NOT cleared by:
  - Flutter widget rebuilds or setState calls
  - Navigator pushReplacement or pop
  - Hot-reload in development (isolate persists; statics keep their values)
  - Back/forward browser navigation (stays in same isolate until hard refresh)

They ARE cleared by:
  - Hard browser refresh / page unload (VM reinitializes)
  - Service workers: Flutter Web does not expose the Dart VM across service worker
    boundaries. The service worker caches assets only; statics are per-tab. No leak.
  - Multiple browser tabs: each tab is its own isolate. Statics are independent.
    Two-tab race: acceptable. A demo tab and a real-user tab run in isolation.

Therefore: the leak path that produced this bug is entirely within a single tab's
lifetime. The auth-primary gate (Fix 1) closes it permanently for any session
where Firebase auth fires before the user sees their coin list.

---

## What Is Not Changing

- users/{uid}/coins — zero reads, zero writes, zero imports
- feedback_callable_route.py — not touched
- feedbackIntelligence.js — not touched
- guest_seed_service.dart seeding logic for anonymous users — not touched
- passport_pdf_generator.py — protected, not in scope
- numista_bq_loader_job — protected, not in scope
- tier_gatekeeper.py — protected (write-prohibition applies regardless of file presence)
- Any Flutter screen other than main.dart, home_dashboard.dart, login_screen.dart
- Demo mode user experience — Browse Demo still works exactly as before

---

## Proposed Changes — 4 Files (3 code + 1 test spec)

=================================================================
Fix 1 — home_dashboard.dart — Auth-primary stream selection
=================================================================

File: numista_mobile/lib/screens/home_dashboard.dart
Lines: 83–85 (current) and 91–93 (current)

This is the architectural change Grok required. The decision flips from flag-primary
to auth-primary. A real non-anonymous user ALWAYS gets Firestore; the flag is only
consulted when there is no authenticated user.

OLD (line 83–85):
  final coinsStream = GuestSeedService.isBrowseDemoMode
      ? GuestSeedService.getDemoCoinsStream()
      : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();

NEW:
  // Auth-primary stream selection.
  // A real non-anonymous Firebase user always reads from Firestore,
  // regardless of the in-memory demo flag. The demo stream is only
  // served when there is no authenticated user (Browse Demo path).
  final _currentUser = FirebaseAuth.instance.currentUser;
  final _isRealUser = _currentUser != null && !_currentUser.isAnonymous;
  final coinsStream = _isRealUser
      ? FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots()
      : GuestSeedService.isBrowseDemoMode
          ? GuestSeedService.getDemoCoinsStream()
          : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();

OLD (line 91–93):
  final currencyStream = GuestSeedService.isBrowseDemoMode
      ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
      : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();

NEW:
  final currencyStream = _isRealUser
      ? FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots()
      : GuestSeedService.isBrowseDemoMode
          ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
          : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();

Note: _isRealUser is computed once at the top of _getCombinedStream() and reused
for both the coins and currency stream selections. No double-call.


=================================================================
Fix 2 — main.dart — Clear demo flag + assert on real sign-in
=================================================================

File: numista_mobile/lib/main.dart
Lines: 293–298 (current)

Adds the StreamBuilder guard and the observability assert Grok required.
This is defence-in-depth: Fix 1 makes State F impossible; Fix 2 clears the
flag early so the home_dashboard _getCombinedStream call never even evaluates
the demo branch, and emits a debug assert + log if the invariant is violated.

OLD (lines 293–298):
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
    // Clear Browse Demo flag if it leaked from a prior session in this tab.
    // This is defence-in-depth; home_dashboard.dart already gates on auth.
    assert(
      !GuestSeedService.isBrowseDemoMode,
      'INTEGRITY VIOLATION: Browse Demo active while real user is signed in. '
      'User: ${snapshot.data!.uid}. Clearing flag.',
    );
    if (GuestSeedService.isBrowseDemoMode) {
      GuestSeedService.deactivateBrowseDemo();
      debugPrint('[AUTH] Demo mode cleared for real user ${snapshot.data!.uid}');
    }
    // If user already dismissed the welcome screen this session,
    // go straight to the main app without re-checking SharedPrefs.
    if (_welcomeDone) {
      return const BaseLayout();
    }

Note on assert behaviour: in Flutter web production builds, assert() statements
are stripped by the compiler (--release mode). The if (GuestSeedService.isBrowseDemoMode)
block handles the production clearance. The assert fires in debug/profile builds only.


=================================================================
Fix 3 — login_screen.dart — Deactivate before real sign-in only
=================================================================

File: numista_mobile/lib/screens/login_screen.dart
Lines: 79–93 (_signIn), 117–121 (_googleSignIn)

Grok's push-back: do NOT clear demo on _signInAsGuest (line 123).
Reason: anonymous users route to users/{uid}/coins (UID-based). The demo flag
is not set at any point during the anonymous sign-in path (activateBrowseDemo is
only called from _browseDemo which bypasses Firebase auth). Clearing it there
is a no-op at best and product-confusing at worst. Rejected per Grok.

Clear demo on real email sign-in (_signIn) and Google sign-in (_googleSignIn) only.

OLD _signIn (lines 79–93):
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
    // Clear Browse Demo before real sign-in so the StreamBuilder
    // receives a clean flag state when auth fires.
    GuestSeedService.deactivateBrowseDemo();
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signIn(email, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

OLD _googleSignIn (lines 117–121):
  Future<void> _googleSignIn() async {
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

NEW _googleSignIn:
  Future<void> _googleSignIn() async {
    // Clear Browse Demo before real sign-in so the StreamBuilder
    // receives a clean flag state when auth fires.
    GuestSeedService.deactivateBrowseDemo();
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

_signInAsGuest (lines 123–132): NOT modified. See state matrix State C above.
_createAccount (lines 95–115): NOT modified. createAccount does not result in
  immediate BaseLayout navigation; the StreamBuilder handles routing after
  Firebase emits the new auth state, which will trigger the Fix 2 guard.


=================================================================
Fix 4 — guest_seed_service.dart — Named helper with null cache guarantee
=================================================================

File: numista_mobile/lib/services/guest_seed_service.dart

Add clearDemoOnSignIn() named helper after deactivateBrowseDemo() (line 34).
This helper is the callable hook from any future sign-in path. It adds nothing
deactivateBrowseDemo doesn't already do — it is a named contract that signals
intent and prevents future engineers from calling the wrong method.

Also: confirms isBrowseDemoMode is a pure getter (line 22) — no side effects.
deactivateBrowseDemo() (lines 31–34) fully nulls both _browseDemoActive and
_demoCoinCache. getDemoCoinsStream() reads from _demoCoinCache (line 93), so
once deactivated the stream returns an empty in-memory list; any subscribed
listener sees an empty snapshot and immediately switches to real data.

The demo banner (BaseLayout lines 496–502 and 879–885) checks isBrowseDemoMode
in the build method. After deactivateBrowseDemo(), the next widget rebuild
(triggered by setState in the StreamBuilder) will evaluate the getter as false
and stop rendering the banner. No lingering listener or UI artifact.

NEW method to add after line 34:
  /// Named hook for sign-in paths that transition a real user into the app.
  /// Identical to deactivateBrowseDemo() but expresses intent at the call site.
  /// Safe to call even if Browse Demo was never active (no-op).
  /// Do NOT call from _signInAsGuest; anonymous users have isolated UID paths.
  static void clearDemoOnSignIn() {
    _browseDemoActive = false;
    _demoCoinCache = [];
  }


---

## Unit Test Specification — Flag Lifecycle

File to create: numista_mobile/test/guest_seed_service_demo_flag_test.dart

Tests required (described so Gemini/Grok can verify the spec is complete):

  test 1: deactivateBrowseDemo is idempotent
    - Call deactivateBrowseDemo() three times on a fresh instance
    - Assert isBrowseDemoMode == false each time
    - Assert demoCoinCache is empty each time

  test 2: clearDemoOnSignIn clears an active demo
    - Manually set _browseDemoActive = true via a test-visible backdoor
      (add @visibleForTesting setter, or test via the public API:
       use activateBrowseDemo() via rootBundle mock, or expose a test-only reset)
    - Call clearDemoOnSignIn()
    - Assert isBrowseDemoMode == false
    - Assert demoCoinCache is empty

  test 3: isBrowseDemoMode is pure (no side effects)
    - Read isBrowseDemoMode 5 times
    - Assert _browseDemoActive is not mutated by the reads

  test 4: deactivateBrowseDemo followed by getDemoCoinsStream() emits empty snapshot
    - Call deactivateBrowseDemo()
    - Call getDemoCoinsStream().first
    - Assert snapshot.docs is empty

  Note: activateBrowseDemo() requires rootBundle; mock it via a test-scoped
  TestWidgetsFlutterBinding or inject a seed helper for test use.

---

## Verification Plan

Automated:
  flutter analyze
  flutter test test/guest_seed_service_demo_flag_test.dart

  Expected: zero errors/warnings, 4 tests pass.

Manual — Primary scenario (exact bug, must pass):
  1. Open app in fresh browser tab
  2. Click "Browse Demo" — verify demo coins appear, Washington Quarters visible
  3. Navigate back to login screen (back button or browser back)
  4. Sign in as charles (seaman_duane@yahoo.com) with real credentials
  5. EXPECTED: 4 dollar coins shown (Presidential x2, SBA, Sacagawea). No quarters.
  6. BEFORE FIX: Washington Quarters appear. Confirmed bug.

Manual — Auth-primary gate (Grok Must-Fix 1):
  1. Simulate _browseDemoActive = true in devtools console (or via debug assert)
  2. Sign in with a real account
  3. EXPECTED: Firestore stream selected (real collection shown); flag cleared.

Manual — Demo mode unaffected:
  1. Click "Browse Demo"
  2. Verify 100 demo coins, banner shown
  3. Click "Try Free" -> login screen
  4. EXPECTED: Demo deactivated, login screen shown. No regressions.

Manual — Anonymous guest unaffected:
  1. Click "Continue as Guest"
  2. EXPECTED: Anonymous user sees their UID-based Firestore coins. Demo flag unset. No change.

Git hygiene:
  git status confirms exactly these files modified:
    numista_mobile/lib/screens/home_dashboard.dart
    numista_mobile/lib/main.dart
    numista_mobile/lib/screens/login_screen.dart
    numista_mobile/lib/services/guest_seed_service.dart
    numista_mobile/test/guest_seed_service_demo_flag_test.dart  [NEW]

---

## Prior Rounds Summary

v1 (23 AUG 2026):
  - Three-file fix proposed: main.dart, guest_seed_service.dart, login_screen.dart
  - Gemini: adopted with minor scope contamination from prior plan context
  - Grok: rejected flag-primary architecture; required auth-primary decision,
    state matrix, observability, unit test, SPA documentation
  - Rejected: clearing demo on _signInAsGuest (Grok push-back, product decision)

v2 (this document):
  - Auth-primary stream selection implemented in home_dashboard.dart (new Fix 1)
  - State matrix written (6 states defined, 2 invalid explained)
  - Debug assert + production log added (Fix 2 addition)
  - Unit test spec written (4 tests)
  - SPA lifetime documented
  - _signInAsGuest NOT modified (Grok push-back adopted)
  - Gemini out-of-scope items rejected (passport_pdf, BQ, estate math)

---

## Open Questions

None. All 5 Grok Must-Fix items resolved. Gemini scope contamination rejected
with rationale. State matrix complete. Plan awaits Gemini + Grok v2 review.

Do not mark execution-ready. Owner decides after next review pass.
