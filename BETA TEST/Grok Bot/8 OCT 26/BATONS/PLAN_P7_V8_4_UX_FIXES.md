# PLAN P7 V8.4 UX FIXES
Filed by: AG CoS | 2026-10-15 ~15:55 ET | Ref: NET-204 / COS_SCORE_P7_ADD-COINS-FLOW_V8_3.md / commit 18ff07e5

## Items to fix (FAIL from V8.3)

### Item 1 — Phone checklist: labels 16px+, 48px checkbox, header ellipsis, Print/PDF wrap
**Files:** `numista_mobile/lib/screens/program_manager_screen.dart`

a) **Labels 16px+** (conditions: 748, 755-756, 772, 957):
   - Line 748: `fontSize: 12` → `fontSize: 16` (program.years)
   - Line 755: `fontSize: 12` → `fontSize: 16` (pct percentage)
   - Line 756: `fontSize: 12` → `fontSize: 16` (collected/total)
   - Line 772: `fontSize: 10` → `fontSize: 16` (Advances overall record)
   - Line 957: `fontSize: 12` → `fontSize: 16` (AI Coin Reference Search subtitle)

b) **48px checkbox tap target** — Line 1435-1437 currently `SizedBox(width:24, height:24)` wrapping `Checkbox`. Change to `SizedBox(width:48, height:48)` so the Checkbox fills the tap target, OR wrap in `InkWell` with `SizedBox(width:48, height:48)` and use `materialTapTargetSize: MaterialTapTargetSize.shrinkWrap` on the Checkbox.

c) **Header title ellipsis** — Line 863-867: `Expanded(child: Text(program.name, style: TextStyle(fontSize: 28...)))` — add `maxLines: 2, overflow: TextOverflow.ellipsis`.

d) **Print + Download PDF wrap** — Lines 870-904: current `Row([ElevatedButton.icon(Print), SizedBox(8), OutlinedButton.icon(Download PDF)])`. Wrap the inner button pair in `Wrap(spacing: 8, runSpacing: 8, children: [...])` so it wraps on narrow screens instead of clipping.

### Item 2 — View Checklist + Advances card: footer overflow, widget tests at 389 and 1025
**Files:** `numista_mobile/lib/screens/program_manager_screen.dart`

a) **Card footer/aspect fix** — Lines 477 and 609: `childAspectRatio: isNarrow ? 2.6 : 1.4`. The 1.4 ratio causes overflow in the 3-col desktop view (1025px) when footer has two wrapped lines. Change to `childAspectRatio: isNarrow ? 2.6 : 1.6` to give cards more vertical space. Alternatively, replace the GridView card with a fixed-min-height approach using `IntrinsicHeight` or switch card footer from `Spacer`-based Column to `MainAxisSize.min` with `Spacer` replaced by `SizedBox(height: 8)`.

b) **View Checklist button** — Line 781-796: the `OutlinedButton` has no explicit min height. Add `style: OutlinedButton.styleFrom(minimumSize: const Size(double.infinity, 48))` for 48px tap target.

c) **Widget overflow tests at 389 and 1025** — In `numista_mobile/test/p7_v8_ux_safety_test.dart`, add two tests:
   - Test pumps `_buildProgramCard(...)` in a 389×844 viewport → no RenderFlex overflow error
   - Test pumps `_buildProgramCard(...)` in a 1025×768 viewport → no RenderFlex overflow error

### Item 3 — Numeric keyboards: Cost decimal:true, Qty digitsOnly in add_coins_hub
**Files:** `numista_mobile/lib/screens/add_coins_hub.dart`

a) **Cost Paid decimal** — Line 2906: `TextInputType.numberWithOptions(decimal: false, signed: false)` → `TextInputType.numberWithOptions(decimal: true, signed: false)`. Also add a `FilteringTextInputFormatter` that allows digits and one decimal point: `FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d{0,2}'))`.

b) **Qty fields in add_coins_hub paths** — Search for all Qty/quantity input fields in add_coins_hub.dart; ensure each uses `TextInputType.number` with `FilteringTextInputFormatter.digitsOnly`.

c) **DOM inputmode** — For web/Flutter web, `TextInputType.number` sets `inputmode="numeric"` and `TextInputType.numberWithOptions(decimal:true)` sets `inputmode="decimal"`. No extra code needed beyond the keyboard type fixes above; note this in GEMINI38_REVIEW.

### Item 4 — Manual Entry CTA subtitle: 14px → 16px (polish, already PASS)
**Files:** `numista_mobile/lib/screens/add_coins_hub.dart`

- Line 718: `fontSize: 14` (subtitle under "Type it in") → `fontSize: 16`
- Line 732 button label: add `style: const TextStyle(fontSize: 16)` inside `Text('Open Manual Entry', ...)`

### Item 6 — Login: remove fixed-height SizedBox around TabBarView
**Files:** `numista_mobile/lib/screens/login_screen.dart`

**Problem:** Line 487-494: `AnimatedSize(child: SizedBox(height: ... ? 280 : 560 : 360, child: TabBarView(...)))`. With no inner scroll (V8.3 fix 6), a tab taller than the fixed height clips the sign-in button.

**Fix:** Drop the fixed-height `SizedBox`. Use `IndexedStack` to show only the active tab at natural height, wrapped in the outer `SingleChildScrollView` that already exists in `_buildSignInCard()`:
```dart
// Replace lines 485-495:
IndexedStack(
  index: _tabCtrl.index,
  children: [_buildSignInTab(), _buildCreateTab()],
),
```
This lets each tab render at its natural height; the outer scroll handles overflow at any viewport.

**Widget test at 389px:** In `p7_v8_ux_safety_test.dart`, add test:
- Set viewport to 360×680 (narrow phone), pump the sign-in card in PIN mode → no RenderFlex overflow, Sign In button visible.

### Item 7 — mint-releases: per-endpoint attempt guard + cache key + unit test
**Files:** `numista_mobile/lib/services/upcoming_releases_service.dart`, `numista_mobile/test/p7_v8_ux_safety_test.dart`

**Problem:** `static bool _fetchAttempted = false` (line 82) and `static const String _cacheKey = 'upcoming_releases_cache'` (line 78) are shared by `fetchUpcoming()` and `fetchAll()`. After dashboard calls `fetchUpcoming()`, `_fetchAttempted = true` blocks `fetchAll()` from ever hitting the network (Upcoming Releases screen always gets cached /upcoming data instead of /all).

**Fix:**
```dart
// Replace single bool with per-endpoint Set:
static final Set<String> _attempted = {};

// In _fetchData():
static Future<List<UpcomingRelease>> _fetchData(String endpoint) async {
  if (_attempted.contains(endpoint)) return _loadCachedReleases(endpoint);
  _attempted.add(endpoint);
  // ... rest unchanged, pass endpoint to _loadCachedReleases
}

// Per-endpoint cache key (suffix endpoint path slug):
static String _cacheKeyFor(String endpoint) =>
    'upcoming_releases_cache_${endpoint.replaceAll('/', '_')}';
```
Update `_loadCachedReleases` to accept the `endpoint` parameter and use `_cacheKeyFor(endpoint)` instead of `_cacheKey`.

**Unit test:** In `p7_v8_ux_safety_test.dart`:
```
test('fetchUpcoming then fetchAll make 2 distinct network calls; repeat fetchUpcoming makes 0 extra calls')
```
(Mock http.Client or SharedPreferences as needed.)

## Gates
1. `flutter analyze lib/` → 0 errors, 0 warnings
2. `flutter test test/p7_v8_ux_safety_test.dart` → all tests pass (was 8; V8.4 adds overflow + fetch guard tests)
3. `GEMINI38_REVIEW_P7_V8_4_BUILD.md` with verbatim before/after code lines AND a per-condition checklist for each item
4. Commit + push to `dev`
5. Rename baton AGCOS → GROKCOS, file NET-205 for score

## Constraints (unchanged)
- Dev only. NO deploys (hosting, CORS backend, firestore.rules). No live writes.
- No changes outside of the files listed above. No pubspec bump.
- GEMINI38_REVIEW must quote verbatim lines — no cite without quoted code.
