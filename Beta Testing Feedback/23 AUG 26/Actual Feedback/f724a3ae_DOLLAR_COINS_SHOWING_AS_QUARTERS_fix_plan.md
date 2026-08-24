# Bug Fix Plan — Demo Mode Leak (Feedback f724a3ae)

**Reporter:** charles (seaman_duane@yahoo.com) — 23 AUG 2026
**Symptom:** "I have 4 1 dollar coins. the list indicates I have washington quarters which is wrong."
**Triage status:** TRIAGED (20:13 UTC)
**Priority:** P1 — user sees entirely wrong collection; valuation is fabricated

---

## Confirmed Root Cause

`GuestSeedService._browseDemoActive` is a **static in-memory flag**. Once set to `true`
by the Browse Demo path, it is only cleared in two places — both require the user to
actively click the **"Try Free"** banner inside the demo app.

**The leak path:**
1. User (or a prior browser session) clicks "Browse Demo" on the login screen.
2. `activateBrowseDemo()` sets `_browseDemoActive = true`, loads JSON into `_demoCoinCache`.
3. User then signs in with their real account (email + PIN) in the same browser tab.
4. `main.dart` `StreamBuilder` sees a non-null `User?` and renders `BaseLayout()`.
5. **`_browseDemoActive` is still `true`** — it was never cleared on sign-in.
6. `home_dashboard.dart:83` picks the demo JSON stream instead of Firestore.
7. The user's 4 dollar coins are invisible. 100 demo coins (incl. 17 quarters) display instead.

**Why deactivate is never called:**
Both `deactivateBrowseDemo()` call sites are inside the `_DemoBanner` "Try Free" button
callback — an explicit UI action. If the user signs in without clicking that banner
(e.g. back button -> login -> sign in), the flag is never cleared.

---

## What Is Not Changing

- `users/{uid}/coins` — zero contact (data is correct, not a data bug)
- `feedback_callable_route.py`, `feedbackIntelligence.js` — not touched
- `guest_seed_service.dart` seeding logic for anonymous users — not touched
- Demo mode experience itself — Browse Demo still works exactly the same
- Any other screen or service

---

## Proposed Changes — 3 Files

### Fix 1 — main.dart — Clear demo flag on real sign-in (primary fix)

In the StreamBuilder at line 294, when snapshot.hasData && snapshot.data != null,
the user is confirmed signed in. Add a guard before routing to BaseLayout:

BEFORE (line 294-298):
  if (snapshot.hasData && snapshot.data != null) {
    if (_welcomeDone) {
      return const BaseLayout();
    }

AFTER:
  if (snapshot.hasData && snapshot.data != null) {
    // A real (non-null) Firebase user is present.
    // If Browse Demo was active from a prior session in this tab, clear it now
    // so the user's real Firestore collection is served, not the JSON seed data.
    if (GuestSeedService.isBrowseDemoMode) {
      GuestSeedService.deactivateBrowseDemo();
    }
    if (_welcomeDone) {
      return const BaseLayout();
    }

This fires every time authStateChanges emits a signed-in user, before BaseLayout
is constructed — flag is clear before any stream is opened.

---

### Fix 2 — guest_seed_service.dart — Named hook for defence-in-depth

Add a static helper callable from any future sign-in path:

  /// Call immediately after a real (non-anonymous) Firebase sign-in succeeds.
  /// Clears Browse Demo mode so the user's real Firestore collection is served.
  /// Safe to call even if Browse Demo was never active (no-op).
  static void clearDemoOnSignIn() {
    if (_browseDemoActive) {
      _browseDemoActive = false;
      _demoCoinCache = [];
    }
  }

---

### Fix 3 — login_screen.dart — Deactivate before real sign-in navigation

In _signIn() and _signInAsGuest(), add deactivateBrowseDemo() after result.ok is
confirmed, before handing control back to the StreamBuilder:

  // In _signIn(), after result.ok confirmed:
  GuestSeedService.deactivateBrowseDemo();

  // In _signInAsGuest(), after result.ok confirmed:
  GuestSeedService.deactivateBrowseDemo();

This adds a third clearance point at the exact moment the user logs in.

---

## Verification Plan

Automated:
  flutter analyze
  (zero new errors or warnings)

Manual — Primary scenario (the exact bug):
  1. Open app in fresh browser tab
  2. Click "Browse Demo" — verify demo coins appear (Washington Quarters visible)
  3. Navigate back to login screen any way (back button, etc.)
  4. Sign in with real account that has dollar coins
  5. EXPECTED: Real collection shows. Dollar coin labels show. No Washington Quarters.
  6. BEFORE FIX: Washington Quarters appear for real user. Confirmed bug.

Manual — Demo mode still works:
  1. Click "Browse Demo"
  2. Verify 100 demo coins load, banner shows
  3. Click "Try Free" banner -> login screen
  4. EXPECTED: Demo deactivated, login screen shown. No regressions.

Manual — Fresh login (no prior demo):
  1. Open app with no prior demo session
  2. Sign in directly
  3. EXPECTED: Real collection shown. No change in behaviour.

Git hygiene:
  git status confirms only 3 files modified:
    numista_mobile/lib/main.dart
    numista_mobile/lib/services/guest_seed_service.dart
    numista_mobile/lib/screens/login_screen.dart

---

## Open Questions

None. Root cause confirmed by code trace and live Firestore data.
The user's 4 dollar coins are correct in Firestore at users/seaman_duane@yahoo.com/coins.
The fix is entirely in the demo-mode flag lifecycle.

---

## Firestore Evidence

User: charles (HQ6o1EwlDKO5WLLKj7bhm3SvRUW2 / seaman_duane@yahoo.com)
Feedback ID: f724a3ae6821626a2779b4faab05bfc9f2f52a8f

Actual coins in Firestore (users/seaman_duane@yahoo.com/coins):
  EfDsVvNtOnKQmvHm | Presidential Dollars    | Dollar | 2007 | United States
  hFsHvqbecq3UfyEH | Susan B. Anthony Dollars | Dollar | 1979 | United States
  hbmdaEdOPbM3LQMS | Sacagawea & Native Am.  | Dollar | 2006 | United States
  kFUueEihfApyOP7N | Presidential Dollars    | Dollar | 2008 | United States

Demo coins served instead (from guest_demo_coins.json):
  17 coins with Denomination "Quarter 25c" (50 State Quarters series)
  — these are what the user saw labelled as "Washington Quarters"
