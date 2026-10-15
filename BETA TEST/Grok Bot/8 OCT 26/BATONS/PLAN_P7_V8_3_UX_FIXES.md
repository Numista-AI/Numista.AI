# PLAN: P7 V8.3 UX Fixes
Author: AG CoS | 2026-10-15 ~14:48 ET
Scope: Dev only. No deploys (no live hosting, no backend CORS, no firestore.rules). For GROKCOS score before execute.
Source: UX_GATE_P7_V8.md + NET-198 orders.

---

## Summary
8 UX fails from preview gate re-gate. All fixable in one commit on `dev`. Plan below item-by-item with file:line targets.

---

## Item 1 — Phone checklist (389px) layout: header wrap, coin names truncated, checkboxes 18px, labels 11-13px

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`
**Region:** `_buildCoinCard()` / checklist list item builder (~line 1177+)

**Fix:**
- Header title: wrap in `Flexible` + `overflow: TextOverflow.ellipsis` (single line, not char-per-line wrap). If title is long use `maxLines: 2` with ellipsis.
- Coin names: `overflow: TextOverflow.ellipsis` on the coin name `Text` widget.
- Checkboxes: ensure touch target is 48×48 min — wrap `Checkbox` in `SizedBox(width: 48, height: 48)` or use `CheckboxListTile` which provides 48px tap area by default.
- Card labels: minimum `fontSize: 16` on all user-facing label text in checklist cards (currently 11-13px). Use `Theme.of(context).textTheme.bodyMedium` (16px) as the floor.
- Download PDF button: wrap in `Flexible` so it doesn't overflow at narrow widths; use `FittedBox` or `ElevatedButton` with `minimumSize`.

---

## Item 2 — 'View Checklist' button + 'Advances overall record' caption overflow at 389px AND 1025px

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`
**Lines:** ~770 ('Advances overall record...'), ~791 ('View Checklist' button)

**Fix:**
- Wrap the entire card footer row in a `Column` instead of a `Row` if width < 500px, OR use `Wrap` widget so items flow to next line naturally.
- 'Advances overall record' `Text`: add `overflow: TextOverflow.ellipsis, maxLines: 2, softWrap: true`.
- 'View Checklist' `ElevatedButton`: ensure it has `constraints` with `maxWidth: double.infinity` so it expands to fill rather than overflow. Wrap in `Expanded` or `SizedBox(width: double.infinity)`.

---

## Item 3 — Year, Cost, Qty fields are type=text — need numeric keyboard

**File:** `numista_mobile/lib/screens/add_coins_hub.dart`
**Target fields:** `_certManualYear`, `_picYear`, cost field, qty field in manual entry full screen

**Fix:**
- Year field (`_certManualYear`, `_picYear`): `keyboardType: TextInputType.number`
- Cost/Value field: `keyboardType: const TextInputType.numberWithOptions(decimal: true)`
- Qty field: `keyboardType: TextInputType.number`
- Add `inputFormatters: [FilteringTextInputFormatter.digitsOnly]` for year/qty; allow decimal for cost.
- Also apply to any `TextField`/`TextFormField` for these three field types in the manual-entry full-screen scaffold (added in V8).

**Note:** `FilteringTextInputFormatter` requires `import 'package:flutter/services.dart'` — verify it's already imported in `add_coins_hub.dart`.

---

## Item 4 — 'More ways > Manual Entry' tab still small inner scroller on tablet

**File:** `numista_mobile/lib/screens/add_coins_hub.dart` (or `program_manager_screen.dart` if tab lives there)
**Context:** The 'More ways' tab panel that contains the Manual Entry option still uses a constrained `SingleChildScrollView` instead of expanding to full height like 'Type it in'.

**Fix:**
- Replace the inner `SizedBox(height: <fixed>)` / `ConstrainedBox` wrapper with `Expanded` inside a `Column` so the tab content fills the available parent height.
- Pattern to match: `showManualFullScreen: true` path (added V8) should already use full Scaffold. Verify the 'More ways' tab panel itself (`_buildMoreWaysTab()` or similar) also uses `Expanded` and not a fixed-height scroll area.
- If the tab view is inside a `TabBarView` → `Column` → `Expanded`, the child scroll view should use `physics: const AlwaysScrollableScrollPhysics()` and fill remaining space.

---

## Item 5 — Firestore 403 on runAggregationQuery in demo mode

**Files:**
- `numista_mobile/lib/screens/program_manager_screen.dart` (~line 294): `_loadTotalReferenceCount()` calls `.count().get()`
- `numista_mobile/lib/screens/estate_planning_screen.dart` (~line 1677): `_loadCoinCount()` calls `.count().get()`

**Fix:**
- Add demo/signed-out guard before each `.count().get()` call:
  ```dart
  if (FirebaseAuth.instance.currentUser == null) return;
  ```
- Also check `_isDemoMode` bool if it exists in scope, or check `currentUser == null` as the canonical guard (same pattern used elsewhere in V8 for `_addSelectedCoins`).
- Both functions are called from `initState`/`didChangeDependencies` — the guard must be the very first line inside the async function body.

---

## Item 6 — Phone sign-in page: double scrollbar, inner scroller clips Sign In button

**File:** `numista_mobile/lib/screens/login_screen.dart`

**Fix:**
- Locate the outermost scroll container on the sign-in page. There should be ONE `SingleChildScrollView` wrapping the entire form column.
- Remove any inner `SingleChildScrollView` or `ListView` nested inside — Flutter renders double scrollbars when two scroll views are stacked.
- The `Sign In` button must be OUTSIDE any inner scroll, placed at the bottom of the top-level column (use `SafeArea` + bottom padding), not clipped by a constrained inner scroll area.
- Pattern: `Scaffold → SafeArea → SingleChildScrollView → Column → [...form fields, SizedBox(height:32), ElevatedButton]`. Remove any nested scroll widget.

---

## Item 7 — ~60 repeating CORS errors on /api/mint-releases/upcoming — add single-attempt or backoff cap

**File:** `numista_mobile/lib/services/upcoming_releases_service.dart`

**Current behavior:** `_fetchData()` is called by `FutureBuilder` on `home_dashboard.dart`; if CORS fails the future may be re-triggered by rebuilds. Also, `UpcomingReleasesScreen` may call `fetchAll()` separately.

**Fix:**
- In `_fetchData()`: add a static `_fetchAttempted` flag (or `_lastFetchAttempt` DateTime) so the service makes **at most one network attempt per session** (fall through to local cache on any failure, no retry loop).
  ```dart
  static bool _fetchAttempted = false;
  // At top of _fetchData():
  if (_fetchAttempted) return _localFallback();
  _fetchAttempted = true;
  ```
- OR add a minimum retry interval: `static DateTime? _lastAttempt;` and only fetch if `_lastAttempt == null || DateTime.now().difference(_lastAttempt!) > const Duration(minutes: 5)`.
- Catch CORS/network errors silently (already done via `debugPrint` + fallback at line 108) — ensure the catch block does NOT rethrow, so `FutureBuilder` gets the cached list, not an error widget that triggers rebuilds.

---

## Item 8 — Demo guard wording: must say 'Create a free account to save' (not 'Sign in')

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`
**Lines:** ~1764 and ~1820

**Current:**
```dart
content: Text('Browse Demo Mode: Sign in to save coins to your collection.'),
```
**Fix:**
```dart
content: Text('Browse Demo Mode: Create a free account to save coins to your collection.'),
```
Apply to BOTH instances (~1764 and ~1820). Also verify `add_coins_hub.dart` demo guard wording (the V8 confirm/demo guard added earlier) — it should already say 'Create a free account' per `base_layout.dart:1503`. If any `add_coins_hub` guard says 'Sign in', fix it there too.

---

## Files to touch (V8.3)
| File | Items |
|------|-------|
| `lib/screens/program_manager_screen.dart` | 1, 2, 4 (if tab lives here), 5, 8 |
| `lib/screens/add_coins_hub.dart` | 3, 4 (if tab lives here) |
| `lib/screens/login_screen.dart` | 6 |
| `lib/services/upcoming_releases_service.dart` | 7 |
| `lib/screens/estate_planning_screen.dart` | 5 (aggregation guard) |

## Gates after V8.3
1. `flutter analyze` → 0 issues
2. `flutter test test/p7_v8_ux_safety_test.dart` → 8/8 (must not regress)
3. GEMINI38_REVIEW_P7_V8_3_BUILD.md with verbatim before/after for all 8 items
4. Commit + push dev → GROKCOS score → UX re-gate on updated preview

## Not in scope (V8.3)
- Backend CORS fix (Eric's typed YES required — not asked until gates pass)
- Confirm card (needs Field Tester with test account)
- firestore.rules deploy
- Live hosting deploy
