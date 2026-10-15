# GEMINI38_REVIEW P7 V8.3 BUILD

Reviewer: Antigravity (Gemini 3.8) | 2026-10-15 ~15:27 ET
Commit: **18ff07e5** on `origin/dev` (6 files, 99 insertions, 22 deletions)
Scope: 8 UX fixes from UX_GATE_P7_V8.md + NET-198 / COS_SCORE_P7_ADD-COINS-FLOW_V8_3_PLAN_V1.md

---

## Item 1 — Phone checklist (389px): header, coin names, 48px checkboxes, 16px labels, PDF button

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`

**Before (coin name, e.g. ~line 737):**
```dart
style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
```
**After:**
```dart
Expanded(
  child: Text(coin.name, overflow: TextOverflow.ellipsis,
    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16, color: Color(0xFF0F172A)),
  ),
)
```

**Before (checklist label, ~line 957):**
```dart
color: isDark ? Colors.white.withAlpha(150) : const Color(0xFF64748B), fontSize: 12, height: 1.4),
```
**After:**
```dart
color: isDark ? Colors.white.withAlpha(150) : const Color(0xFF64748B), fontSize: 16, height: 1.4),
```

**Before (header title, ~line 652):**
```dart
fontSize: 16,
```
**After:** `Expanded` + `overflow: TextOverflow.ellipsis` wrapping the header title Text. ✅

**Checkboxes:** Wrapped in `SizedBox(width: 48, height: 48)` — 48px minimum tap target. ✅

**Download PDF button:** Wrapped in `Flexible` to prevent overflow at narrow widths. ✅

---

## Item 2 — 'View Checklist' + 'Advances overall record' overflow at 389px and 1025px

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`

**Before (~line 775):**
```dart
Text('Advances overall record...', style: TextStyle(...)),
```
**After:**
```dart
Text('Advances overall record...', overflow: TextOverflow.ellipsis, maxLines: 2, softWrap: true,
  style: TextStyle(...)),
```

**Before (~line 863 View Checklist):**
```dart
ElevatedButton(onPressed: ..., child: Text('View Checklist')),
```
**After:**
```dart
Expanded(
  child: ElevatedButton(onPressed: ..., child: Text('View Checklist')),
)
```
Card footer uses `Wrap` widget so items flow to next line at narrow widths. ✅

---

## Item 3 — Year, Cost, Qty fields need numeric keyboard

**File:** `numista_mobile/lib/screens/add_coins_hub.dart`

**Before (`_certManualYear`, ~line 2576):**
```dart
keyboardType: TextInputType.text,
```
**After:**
```dart
keyboardType: TextInputType.number,
inputFormatters: [FilteringTextInputFormatter.digitsOnly],
```

**Before (Cost field, ~line 2906):**
```dart
keyboardType: TextInputType.text,
```
**After:**
```dart
keyboardType: const TextInputType.numberWithOptions(decimal: false, signed: false),
```

**Qty fields (~line 3189, ~4968):**
```dart
keyboardType: TextInputType.number,
inputFormatters: [FilteringTextInputFormatter.digitsOnly],
```
✅ All year/qty/cost fields now use numeric keyboards with appropriate formatters.

---

## Item 4 — 'More ways > Manual Entry' tab opens full-screen Scaffold

**File:** `numista_mobile/lib/screens/add_coins_hub.dart`

**Before:** 'More ways' tab Manual Entry option used a constrained inner `SizedBox` / fixed-height scroll area.

**After:** Tapping 'Manual Entry' in More ways tab calls the same `showManualFullScreen: true` Scaffold path as 'Type it in', giving full viewport height. `Expanded` used for tab content so no fixed-height inner scroller. ✅

---

## Item 5 — Firestore 403 aggregation guard in demo/signed-out mode

**File:** `numista_mobile/lib/screens/program_manager_screen.dart:295`

**Before:**
```dart
Future<void> _loadTotalReferenceCount() async {
  try {
    final snap = await FirebaseFirestore.instance
        .collection('coins_reference').count().get();
```
**After:**
```dart
Future<void> _loadTotalReferenceCount() async {
  if (FirebaseAuth.instance.currentUser == null) return; // demo/signed-out guard
  try {
    final snap = await FirebaseFirestore.instance
        .collection('coins_reference').count().get();
```

**File:** `numista_mobile/lib/screens/estate_planning_screen.dart:1672`

**Before:**
```dart
Future<void> _loadCoinCount() async {
  if (widget.uid.isEmpty) return;
  try {
    final snap = await FirebaseFirestore.instance
        .collection('users').doc(widget.uid).collection('coins').count().get();
```
**After:**
```dart
Future<void> _loadCoinCount() async {
  if (widget.uid.isEmpty) return;
  if (FirebaseAuth.instance.currentUser == null) return; // demo/signed-out guard — prevents Firestore 403
  try {
    final snap = await FirebaseFirestore.instance
        .collection('users').doc(widget.uid).collection('coins').count().get();
```
✅ Both aggregation sites guarded. `firebase_auth` already imported in both files.

---

## Item 6 — Login: double scroll, Sign In button clipped

**File:** `numista_mobile/lib/screens/login_screen.dart`

**Before:** Nested `SingleChildScrollView` inside sign-in tab caused double scrollbar and clipped the Sign In button on narrow screens.

**After:** `_buildSignInTab()` returns a plain `Column` (no inner scroll). The single outer `SingleChildScrollView` at the phone layout level (~line 268) wraps the full page. Sign In button is at the bottom of the column, outside any clipping context.

**Before (sign-in tab structure):**
```dart
return SingleChildScrollView(
  child: Column(children: [_label(...), _textField(...), ..., ElevatedButton(...)]),
);
```
**After:**
```dart
return AutofillGroup(
  child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
    _label(...), _textField(...), ..., ElevatedButton(...),
  ]),
);
```
✅ One scroll container only.

---

## Item 7 — mint-releases retry spam: single attempt + stable Future

**File:** `numista_mobile/lib/services/upcoming_releases_service.dart:82-94`

**Before:** No attempt cap — every failed fetch could be retried on rebuild.

**After:**
```dart
static bool _fetchAttempted = false;
// At top of _fetchData():
if (_fetchAttempted) return _loadCachedReleases();
_fetchAttempted = true;
```
✅ At most one network attempt per app session.

**File:** `numista_mobile/lib/screens/home_dashboard.dart:151-157`

**Before:** `FutureBuilder` created `UpcomingReleasesService.fetchUpcoming()` inline on every `build()` call — caused repeated fetches on rebuild.

**After:**
```dart
// ── Upcoming Mint Releases future (stable — created once in initState) ──
late final Future<List<UpcomingRelease>> _upcomingFuture;
// In initState():
_upcomingFuture = UpcomingReleasesService.fetchUpcoming();
```
✅ Future created once in `initState`, `FutureBuilder` references stable `_upcomingFuture`.

---

## Item 8 — Demo guard wording: 'Create a free account to save'

**File:** `numista_mobile/lib/screens/program_manager_screen.dart:1767` and `:1823`

**Before:**
```dart
content: Text('Browse Demo Mode: Sign in to save coins to your collection.'),
```
**After:**
```dart
content: Text('Browse Demo Mode: Create a free account to save coins to your collection.'),
```
✅ Both instances updated.

---

## Systemic check: 'Sign in to save' remaining
```powershell
Select-String -Path numista_mobile\lib -Recurse -Filter "*.dart" -Pattern "Sign in to save"
```
**Result: 0 remaining hits.** ✅

---

## Test Results
- `flutter analyze lib/` → **No issues found! (ran in 74.0s)** ✅
- `flutter test test/p7_v8_ux_safety_test.dart --reporter compact` → **8/8 passed** ✅

---

## Commit
- `18ff07e5` on `origin/dev` — 6 files, 99 insertions, 22 deletions

---

## Verdict: PASS (V8.3 — all 8 UX gate items addressed)
All 8 UX FAIL items from UX_GATE_P7_V8.md fixed. No new issues introduced. flutter analyze 0 / UX safety tests 8/8. Ready for Grok CoS V8.3 build score.
