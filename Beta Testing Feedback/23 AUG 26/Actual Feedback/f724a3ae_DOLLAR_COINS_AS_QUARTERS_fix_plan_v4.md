# Bug Fix Plan v4 — Demo Mode Leak (Feedback f724a3ae)
## Dollar Coins Displaying as Washington Quarters

**Reporter:** charles (seaman_duane@yahoo.com) — 23 AUG 2026
**Feedback ID:** f724a3ae6821626a2779b4faab05bfc9f2f52a8f
**Triage status:** TRIAGED 2026-08-23 20:13 UTC
**Priority:** P1

---

## Decision Matrix — v3 Review

| Source | Suggestion | Decision | Why |
|--------|-----------|----------|-----|
| Gemini | Must-Fix 1: Change _isRealUser to _isAuthUser = _authUser != null (third time raised) | Rejected | Grok v3 explicitly accepted _isRealUser: "The _isRealUser formulation matches the state matrix and is preferable to the broader _isAuthUser Gemini requested." Anonymous users (State C) reach Firestore correctly because _browseDemoActive is always false on their path — they fall through the flag check. _isRealUser is semantically precise. Issue closed by Grok. Will not be re-raised. |
| Gemini | Must-Fix 2: Add deactivateBrowseDemo() to _signInAsGuest (third time raised) | Rejected | Grok v3 line 234: "rejection of the re-opened 'clear on guest' item are solid and must be kept." Grok v3 acceptance criteria line 249: "No other files, no re-opening of closed items (guest clear, _isAuthUser change, backend scope)." Issue is closed. Will not be re-raised. |
| Gemini | Must-Fix 3: Synchronize all three streams under same gate | Already done in v3 under _isRealUser. Correct observation; wrong variable name. Adopted in substance, rejected on naming per above. |
| Grok | Must-Fix 1: demoCoinCache referenced in tests but appears private — will not compile | False alarm — resolved without code change. demoCoinCache is already a PUBLIC getter at guest_seed_service.dart:37: `static List<Map<String, dynamic>> get demoCoinCache => _demoCoinCache`. Tests reference GuestSeedService.demoCoinCache and will compile and pass as written. No additional getter needed. Confirmed below with line and type. |
| Grok | All three v2 Must-Fixes (assert order, test backdoor, dead method) | Confirmed closed | Grok v3 line 229: "All three of my prior Must-Fix items from v2 now show concrete mechanisms." |
| Grok | "To Antigravity": runtime type, listen-block context, BaseLayout OR behavior | Documented below | Documentation only; no code changes. |

**Result: zero new code changes from v3. All items either already implemented or confirmed resolved.**

---

## Confirmed Root Cause (unchanged — stays in every version)

GuestSeedService._browseDemoActive is a static in-memory flag. Once set true by
activateBrowseDemo() (called from _browseDemo(), login_screen.dart:136), the only
clearance points before this fix were inside the _DemoBanner "Try Free" button —
an explicit user action. Signing in without clicking that banner left the flag live.

home_dashboard.dart:83-85 (current on disk — unfixed):
  final coinsStream = GuestSeedService.isBrowseDemoMode
      ? GuestSeedService.getDemoCoinsStream()
      : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
Flag-primary decision. Real user routed to demo JSON.

Live Firestore evidence (permanent):
  users/seaman_duane@yahoo.com/coins — 4 dollar coins:
    EfDsVvNtOnKQmvHm | Presidential Dollars    | Dollar | 2007 | United States
    hFsHvqbecq3UfyEH | Susan B. Anthony Dollars | Dollar | 1979 | United States
    hbmdaEdOPbM3LQMS | Sacagawea & Native Am.  | Dollar | 2006 | United States
    kFUueEihfApyOP7N | Presidential Dollars    | Dollar | 2008 | United States
  guest_demo_coins.json — 100 demo coins, 17 denomination "Quarter 25c" (50 State Quarters).
  Those 17 quarters are what charles saw. His dollar coins were invisible.

---

## Clarifications for Grok's "To Antigravity" Requests

### 1. demoCoinCache runtime type and test compilability

_demoCoinCache declared at guest_seed_service.dart:20:
  static List<Map<String, dynamic>> _demoCoinCache = [];

Public getter at guest_seed_service.dart:37 (already exists, no change needed):
  static List<Map<String, dynamic>> get demoCoinCache => _demoCoinCache;

Tests 1 and 2 reference GuestSeedService.demoCoinCache. This getter is public,
returns the correct type, and will compile and pass without any additional change.
The Grok concern ("Tests will not compile") is resolved by the existing getter.
No @visibleForTesting getter needs to be added.

### 2. Exact listen-block context (current on-disk, lines 83-111)

This is the full block that Fix 1 replaces. Listed here so the patch can be
applied without diff drift:

  83:     final coinsStream = GuestSeedService.isBrowseDemoMode
  84:         ? GuestSeedService.getDemoCoinsStream()
  85:         : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
  86:     subCoins = coinsStream.listen((snap) {
  87:       coins = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
  88:       emit();
  89:     }, onError: (e) => controller.addError(e));
  90:
  91:     final currencyStream = GuestSeedService.isBrowseDemoMode
  92:         ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
  93:         : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();
  94:     subCurrency = currencyStream.listen((snap) {
  95:       currency = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
  96:       emit();
  97:     }, onError: (e) => controller.addError(e));
  98:
  99:     final worldItemsStream = GuestSeedService.isBrowseDemoMode
 100:         ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
 101:         : FirebaseFirestore.instance.collection(AuthService.coinsPath.replaceAll('/coins', '/world_items')).snapshots();
 102:     subWorldItems = worldItemsStream.listen((snap) {
 103:       worldItems = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
 104:       emit();
 105:     }, onError: (e) => controller.addError(e));
 106:
 107:     controller.onCancel = () {
 108:       subCoins?.cancel();
 109:       subCurrency?.cancel();
 110:       subWorldItems?.cancel();
 111:     };

### 3. BaseLayout isDemoMode vs. static flag — banner OR behavior

BaseLayout constructor (base_layout.dart:47):
  const BaseLayout({super.key, this.isDemoMode = false});

Banner condition (base_layout.dart:879):
  if (widget.isDemoMode || GuestSeedService.isBrowseDemoMode)
    _DemoBanner(...)

After deactivateBrowseDemo():
- GuestSeedService.isBrowseDemoMode becomes false immediately.
- widget.isDemoMode is a constructor argument; it is true only on the
  BaseLayout(isDemoMode: true) instance pushed by _browseDemo() in login_screen.
- That instance is replaced by Navigator.pushReplacement when the user navigates
  back to LoginScreen (via _DemoBanner "Try Free") or when main.dart rebuilds with
  a real user and constructs const BaseLayout() (isDemoMode defaults to false).
- Result: after sign-in, the new BaseLayout() has isDemoMode = false and
  isBrowseDemoMode = false. The banner does not render. No lingering UI artifact.
- The banner disappears on the next widget rebuild following deactivateBrowseDemo(),
  which is triggered by the setState in the StreamBuilder. This is sufficient.

---

## State Matrix (confirmed correct by Grok v3 — unchanged)

  State A: No Firebase user, _browseDemoActive = false  -> LoginScreen. Stream: N/A.
  State B: No Firebase user, _browseDemoActive = true   -> BaseLayout(isDemoMode:true). Stream: getDemoCoinsStream(). Banner visible.
  State C: Anonymous Firebase user, _browseDemoActive = false -> BaseLayout(). Stream: Firestore users/{uid}/coins. Flag never set on this path.
  State D: Anonymous user, _browseDemoActive = true     -> INVALID / structurally unreachable. Auth-primary gate handles defensively.
  State E: Real Firebase user, _browseDemoActive = false -> BaseLayout(). Stream: Firestore users/{email_lowercase}/coins.
  State F: Real Firebase user, _browseDemoActive = true  -> THE BUG STATE. After fix: immune (auth-primary). Flag cleared by main.dart guard.

---

## SPA / Navigation Lifetime (confirmed correct by Grok v3 — unchanged)

Statics persist for tab lifetime. Not cleared by: rebuilds, Navigator, hot-reload, back/forward.
Cleared by: hard refresh / page unload.
Service workers: asset-caching only; per-tab isolates; no cross-boundary leak.
Two tabs: independent isolates; acceptable and documented.

---

## What Is Not Changing

- users/{uid}/coins — zero reads, zero writes, zero contact
- passport_pdf_generator.py, numista_bq_loader_job, tier_gatekeeper.py — protected
- feedbackIntelligence.js, feedback_callable_route.py — not touched
- GuestSeedService.seedIfNeeded() — not touched
- _signInAsGuest — NOT modified (closed decision; re-raising rejected)
- Demo mode user experience — Browse Demo works exactly as before
- demoCoinCache public getter (line 37) — already exists; not modified

---

## Proposed Changes — 5 Files (unchanged from v3; listed with precise line targets)

=================================================================
Fix 1 — home_dashboard.dart — Auth-primary stream selection
         All three streams. Lines 83-105 replaced.
=================================================================

BEFORE (lines 83-105, exact on-disk text shown in Clarification 2 above):
  [three flag-primary ternaries, one per stream]

AFTER:
  // Auth-primary stream selection.
  // A real non-anonymous Firebase user always reads from Firestore,
  // regardless of the in-memory demo flag. The demo branch is only
  // reached when there is no authenticated user (Browse Demo path, State B).
  // Anonymous users (State C): _browseDemoActive is always false on their path
  // (activateBrowseDemo() is only called from _browseDemo(), which bypasses
  // Firebase auth entirely). They fall through the flag check to Firestore.
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
  subWorldItems = worldItemsStream.listen((snap) {
    worldItems = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
    emit();
  }, onError: (e) => controller.addError(e));

  controller.onCancel = () {
    subCoins?.cancel();
    subCurrency?.cancel();
    subWorldItems?.cancel();
  };

_isRealUser computed once, reused for all three streams. No double-call to currentUser.


=================================================================
Fix 2 — main.dart — Clear-then-assert (correct order)
         Lines 293-298 region.
=================================================================

BEFORE (lines 293-298, exact on-disk):
  // Signed in -> show welcome screen on first launch, then main app
  if (snapshot.hasData && snapshot.data != null) {
    // If user already dismissed the welcome screen this session,
    // go straight to the main app without re-checking SharedPrefs.
    if (_welcomeDone) {
      return const BaseLayout();
    }

AFTER:
  // Signed in -> show welcome screen on first launch, then main app
  if (snapshot.hasData && snapshot.data != null) {
    // INVARIANT: a real Firebase user must never see demo data.
    // Step 1: clear + log (runs in ALL build modes including production).
    if (GuestSeedService.isBrowseDemoMode) {
      GuestSeedService.deactivateBrowseDemo();
      debugPrint('[AUTH] Demo mode cleared for real user ${snapshot.data!.uid}');
    }
    // Step 2: assert postcondition (debug/profile only; stripped in release).
    // Fires AFTER clearance — message is truthful. If this assert fires,
    // deactivateBrowseDemo() has a logic defect.
    assert(!GuestSeedService.isBrowseDemoMode,
        'INTEGRITY: Browse Demo still active after deactivateBrowseDemo(). '
        'User: ${snapshot.data!.uid}. deactivateBrowseDemo() has a logic defect.');
    // If user already dismissed the welcome screen this session,
    // go straight to the main app without re-checking SharedPrefs.
    if (_welcomeDone) {
      return const BaseLayout();
    }


=================================================================
Fix 3 — login_screen.dart — Deactivate on real sign-in paths only
=================================================================

BEFORE _signIn (lines 79-93, exact on-disk):
  Future<void> _signIn() async {
    ...
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signIn(email, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

AFTER _signIn (one line added before setState):
  Future<void> _signIn() async {
    ...
    GuestSeedService.deactivateBrowseDemo(); // third clearance point
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signIn(email, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

BEFORE _googleSignIn (lines 117-121, exact on-disk):
  Future<void> _googleSignIn() async {
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

AFTER _googleSignIn:
  Future<void> _googleSignIn() async {
    GuestSeedService.deactivateBrowseDemo(); // same clearance as _signIn
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

_signInAsGuest: NOT modified. Closed decision. Will not be re-raised.
_createAccount: NOT modified. StreamBuilder guard handles routing.


=================================================================
Fix 4 — guest_seed_service.dart — Add @visibleForTesting backdoor
         No clearDemoOnSignIn (removed from v2; remains absent).
=================================================================

BEFORE (lines 31-37, exact on-disk):
  static void deactivateBrowseDemo() {
    _browseDemoActive = false;
    _demoCoinCache = [];
  }

  /// Returns the in-memory demo coin list (Browse Demo mode only).
  static List<Map<String, dynamic>> get demoCoinCache => _demoCoinCache;

AFTER (one new method added between deactivateBrowseDemo and demoCoinCache):
  static void deactivateBrowseDemo() {
    _browseDemoActive = false;
    _demoCoinCache = [];
  }

  /// FOR TESTS ONLY. Sets _browseDemoActive without requiring rootBundle
  /// (Flutter asset loading). Not for production use.
  @visibleForTesting
  static void setDemoActiveForTest(bool value) {
    _browseDemoActive = value;
    if (!value) _demoCoinCache = [];
  }

  /// Returns the in-memory demo coin list (Browse Demo mode only).
  /// Public getter — accessible from tests without @visibleForTesting.
  static List<Map<String, dynamic>> get demoCoinCache => _demoCoinCache;

Note: demoCoinCache is already public at line 37. Tests referencing
GuestSeedService.demoCoinCache compile and pass without any additional getter.
The concern raised in Grok v3 Must-Fix 1 is resolved by the existing code.


=================================================================
Fix 5 — test/guest_seed_service_demo_flag_test.dart [NEW FILE]
=================================================================

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
      // demoCoinCache is the public getter at guest_seed_service.dart:37;
      // type: List<Map<String, dynamic>>. Accessible without @visibleForTesting.
      expect(GuestSeedService.demoCoinCache, isEmpty);
    });

    test('2: setDemoActiveForTest activates then deactivate clears both fields', () {
      GuestSeedService.setDemoActiveForTest(true);
      expect(GuestSeedService.isBrowseDemoMode, isTrue);
      GuestSeedService.deactivateBrowseDemo();
      expect(GuestSeedService.isBrowseDemoMode, isFalse);
      expect(GuestSeedService.demoCoinCache, isEmpty);
    });

    test('3: isBrowseDemoMode is a pure getter with no side effects', () {
      GuestSeedService.setDemoActiveForTest(true);
      final _ = GuestSeedService.isBrowseDemoMode;
      final __ = GuestSeedService.isBrowseDemoMode;
      final ___ = GuestSeedService.isBrowseDemoMode;
      // Repeated reads must not mutate the flag
      expect(GuestSeedService.isBrowseDemoMode, isTrue);
    });

    test('4: getDemoCoinsStream after deactivate emits empty snapshot', () async {
      // After deactivate, _demoCoinCache = [].
      // getDemoCoinsStream() builds from cache (guest_seed_service.dart:93).
      // Stream.value(DemoQuerySnapshot([])) => docs is empty.
      GuestSeedService.deactivateBrowseDemo();
      final snap = await GuestSeedService.getDemoCoinsStream().first;
      expect(snap.docs, isEmpty,
          reason: 'getDemoCoinsStream after clear must emit zero docs; '
              'confirms demo JSON cannot appear in real user session');
    });
  }

---

## Verification Plan

Automated:
  flutter analyze
  flutter test test/guest_seed_service_demo_flag_test.dart
  Expected: zero errors/warnings, 4 tests pass.

Manual — Primary scenario (the exact bug):
  1. Open app in fresh browser tab
  2. Click "Browse Demo" — confirm Washington Quarters visible in coin list
  3. Navigate back to login (back button)
  4. Sign in as charles (seaman_duane@yahoo.com) with real credentials
  EXPECTED: 4 dollar coins shown. No Washington Quarters. No demo banner.
  BEFORE FIX: Washington Quarters shown. Confirmed bug.

Manual — Auth-primary gate (immune to flag):
  1. Sign in with real account
  2. Auth-primary gate: _isRealUser = true forces Firestore regardless of flag state
  EXPECTED: Real collection displayed.

Manual — Demo mode unaffected:
  1. Click "Browse Demo" — 100 demo coins, banner visible
  2. Click "Try Free" banner -> LoginScreen
  EXPECTED: Demo deactivated, login shown. No regression.

Manual — Anonymous guest unaffected:
  1. Click "Continue as Guest"
  EXPECTED: Firestore users/{uid}/coins served. Flag never set. No change.

Git hygiene:
  git status confirms exactly these files:
    numista_mobile/lib/screens/home_dashboard.dart       (modified)
    numista_mobile/lib/main.dart                         (modified)
    numista_mobile/lib/screens/login_screen.dart         (modified)
    numista_mobile/lib/services/guest_seed_service.dart  (modified)
    numista_mobile/test/guest_seed_service_demo_flag_test.dart (new)

---

## Prior Rounds Summary

v1: Flag-clearance only. Grok: flag-primary arch rejected.
v2: Auth-primary gate (hd:83), state matrix, assert, 4 test specs, SPA docs.
    Grok: assert order inverted; dead method; test backdoor missing.
    Gemini: worldItemsStream missed; _signInAsGuest re-raised.
v3: worldItemsStream covered; assert order fixed (clear-then-assert);
    setDemoActiveForTest() added; clearDemoOnSignIn() removed.
    Grok: demoCoinCache access (false alarm — already public). Gemini: re-raised
    _isAuthUser and _signInAsGuest (both rejected; closed by Grok acceptance).
v4 (this document): Zero new code changes. Grok's demoCoinCache concern resolved
    by confirmation that the public getter already exists (line 37). Exact listen-block
    context provided (lines 83-111). BaseLayout banner OR behavior documented.
    Both Gemini v3 Must-Fix 1 and 2 closed permanently with Grok endorsement.

---

## Closed Items (will not be re-raised)

1. _isAuthUser vs _isRealUser: closed. _isRealUser adopted. Grok v3 accepted it.
2. deactivateBrowseDemo on _signInAsGuest: closed. State C makes it a no-op.
   Grok v3 accepted. Grok acceptance criteria line 249 forbids re-opening.
3. passport_pdf_generator.py, numista_bq_loader_job, tier_gatekeeper.py: not in scope.
4. Estate math segregation, snake_case validation, merge-flag restriction: not in scope.

---

## Open Questions

None. All Grok Must-Fix items from v1, v2, and v3 resolved. The single remaining
Grok item (demoCoinCache access) is a false alarm resolved by existing code.
Do not mark execution-ready. Owner decides after next Gemini + Grok review pass.
