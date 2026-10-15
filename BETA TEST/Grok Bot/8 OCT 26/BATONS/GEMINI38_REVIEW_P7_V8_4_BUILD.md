# GEMINI38 REVIEW — P7 V8.4 BUILD
**Date:** 2026-10-15  
**Track:** P7 ADD-COINS-FLOW  
**Build:** V8.4  
**Plan:** COS_SCORE_P7_ADD-COINS-FLOW_V8_4_PLAN_V1.md (PLAN GO: NET-206)  
**Review type:** BUILT CODE (commit diff review, per Rule 6b)

---

## ITEM 1a — Font size 16px on program card labels

### Files reviewed
- `numista_mobile/lib/screens/program_manager_screen.dart`

### Condition
All body/label text in `_buildProgramCard` uses `fontSize: 16`.

### Verbatim before
```dart
// ~line 748
style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
// ~line 755
style: TextStyle(fontSize: 13, color: _sub),
// ~line 756 (advances text)
style: TextStyle(fontSize: 13, ...),
// ~line 772
style: TextStyle(fontSize: 14, color: _blue, fontWeight: FontWeight.bold),
// ~line 957
style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
```

### Verbatim after
```dart
// ~line 748
style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
// ~line 755
style: TextStyle(fontSize: 16, color: _sub),
// ~line 756
style: TextStyle(fontSize: 16, ...),
// ~line 772
style: TextStyle(fontSize: 16, color: _blue, fontWeight: FontWeight.bold),
// ~line 957
style: const TextStyle(fontSize: 16, color: Color(0xFF64748B)),
```

### Checklist
- [x] Title text uses `fontSize: 16`
- [x] Date/subtitle text uses `fontSize: 16`
- [x] Percentage text uses `fontSize: 16`
- [x] "X / Y Collected" text uses `fontSize: 16`
- [x] "Advances overall record" text uses `fontSize: 16`
- [x] No 13px or 14px font sizes remain in `_buildProgramCard` card body

---

## ITEM 1b — 48px checkbox tap target + shrinkWrap

### Files reviewed
- `numista_mobile/lib/screens/program_manager_screen.dart`

### Condition
Checkbox `SizedBox` is 48px min; `materialTapTargetSize: shrinkWrap`.

### Verbatim before
```dart
SizedBox(
  width: 24,
  height: 24,
  child: Checkbox(
    value: isChecked,
    onChanged: ...,
  ),
),
```

### Verbatim after
```dart
SizedBox(
  width: 48,
  height: 48,
  child: Checkbox(
    value: isChecked,
    onChanged: ...,
    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  ),
),
```

### Checklist
- [x] SizedBox width increased to 48
- [x] SizedBox height increased to 48
- [x] `materialTapTargetSize: MaterialTapTargetSize.shrinkWrap` added
- [x] Checkbox still functional (value/onChanged unchanged)

---

## ITEM 1c — Header title maxLines:2 + ellipsis

### Files reviewed
- `numista_mobile/lib/screens/program_manager_screen.dart`

### Condition
Program card header title has `maxLines: 2, overflow: TextOverflow.ellipsis`.

### Verbatim before
```dart
Text(
  program.name,
  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
),
```

### Verbatim after
```dart
Text(
  program.name,
  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
  maxLines: 2,
  overflow: TextOverflow.ellipsis,
),
```

### Checklist
- [x] `maxLines: 2` added to title Text
- [x] `overflow: TextOverflow.ellipsis` added
- [x] Long program names (e.g. "Washington Presidential Dollar Series 2007–2016") will truncate gracefully

---

## ITEM 1d — Print+PDF buttons wrapped in Wrap widget

### Files reviewed
- `numista_mobile/lib/screens/program_manager_screen.dart`

### Condition
Print and PDF buttons are wrapped in `Wrap(spacing: 8, runSpacing: 8)`.

### Verbatim before
```dart
Row(
  children: [
    ElevatedButton.icon(icon: ..., label: Text('Print'), onPressed: ...),
    const SizedBox(width: 8),
    ElevatedButton.icon(icon: ..., label: Text('PDF'), onPressed: ...),
  ],
),
```

### Verbatim after
```dart
Wrap(
  spacing: 8,
  runSpacing: 8,
  children: [
    ElevatedButton.icon(icon: ..., label: Text('Print'), onPressed: ...),
    ElevatedButton.icon(icon: ..., label: Text('PDF'), onPressed: ...),
  ],
),
```

### Checklist
- [x] Row replaced with `Wrap`
- [x] `spacing: 8` set
- [x] `runSpacing: 8` set (buttons stack vertically on narrow screens)
- [x] No fixed `SizedBox(width: 8)` spacer remaining between buttons

---

## ITEM 2a — childAspectRatio 1.6 at both grids

### Files reviewed
- `numista_mobile/lib/screens/program_manager_screen.dart`

### Condition
Both the live program grid and skeleton grid use `childAspectRatio: isNarrow ? 2.6 : 1.6` (changed from previous `1.4`).

### Verbatim before (live grid ~line 477)
```dart
childAspectRatio: isNarrow ? 2.6 : 1.4,
```

### Verbatim after (live grid ~line 477)
```dart
childAspectRatio: isNarrow ? 2.6 : 1.6,
```

### Verbatim before (skeleton grid ~line 609)
```dart
childAspectRatio: isNarrow ? 2.6 : 1.4,
```

### Verbatim after (skeleton grid ~line 609)
```dart
childAspectRatio: isNarrow ? 2.6 : 1.6,
```

### Checklist
- [x] Live grid `childAspectRatio` tablet value changed from `1.4` → `1.6`
- [x] Skeleton grid `childAspectRatio` tablet value changed from `1.4` → `1.6`
- [x] Narrow (isNarrow) value `2.6` left unchanged at both grids
- [x] Test `p7_v84_program_card_no_overflow_at_1025px` uses `childAspectRatio: 1.6` and passes

---

## ITEM 2b — View Checklist button full-width 48px

### Files reviewed
- `numista_mobile/lib/screens/program_manager_screen.dart`

### Condition
"View Checklist" OutlinedButton has `minimumSize: const Size(double.infinity, 48)`.

### Verbatim before
```dart
OutlinedButton(
  onPressed: ...,
  style: OutlinedButton.styleFrom(
    foregroundColor: _text,
    side: const BorderSide(color: _border),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
  ),
  child: const Text('View Checklist'),
),
```

### Verbatim after
```dart
OutlinedButton(
  onPressed: ...,
  style: OutlinedButton.styleFrom(
    foregroundColor: _text,
    side: const BorderSide(color: _border),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    minimumSize: const Size(double.infinity, 48),
  ),
  child: const Text('View Checklist'),
),
```

### Checklist
- [x] `minimumSize: const Size(double.infinity, 48)` added
- [x] Button is at least 48px tall (WCAG tap target)
- [x] Button stretches full card width

---

## ITEM 3a — Camera cost field decimal keyboard

### Files reviewed
- `numista_mobile/lib/screens/add_coins_hub.dart`

### Condition
`_camInputField('Cost Paid', _picCost)` call site uses `keyboardType: TextInputType.numberWithOptions(decimal: true)` and decimal `FilteringTextInputFormatter`.

### Verbatim before
```dart
_camInputField('Cost Paid', _picCost),
```

### Verbatim after
```dart
_camInputField(
  'Cost Paid',
  _picCost,
  keyboardType: const TextInputType.numberWithOptions(decimal: true),
  inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d{0,2}'))],
),
```

### Checklist
- [x] `keyboardType: TextInputType.numberWithOptions(decimal: true)` added
- [x] `FilteringTextInputFormatter` limits to `^\d*\.?\d{0,2}` (2 decimal places)
- [x] Mobile keyboard shows decimal point on cost field

---

## ITEM 3b — Purchase cost dialog decimal keyboard

### Files reviewed
- `numista_mobile/lib/screens/add_coins_hub.dart`

### Condition
In the purchase cost dialog, `costCtrl` TextField uses `numberWithOptions(decimal: true)` + decimal formatter.

### Verbatim before
```dart
TextField(
  controller: costCtrl,
  keyboardType: TextInputType.number,
  decoration: const InputDecoration(labelText: 'Cost Paid (\$)'),
),
```

### Verbatim after
```dart
TextField(
  controller: costCtrl,
  keyboardType: const TextInputType.numberWithOptions(decimal: true),
  inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d{0,2}'))],
  decoration: const InputDecoration(labelText: 'Cost Paid (\$)'),
),
```

### Checklist
- [x] `keyboardType` changed from `TextInputType.number` to `numberWithOptions(decimal: true)`
- [x] `FilteringTextInputFormatter` added with `^\d*\.?\d{0,2}` pattern
- [x] Decimal input (e.g. `19.99`) accepted
- [x] More than 2 decimal places rejected

---

## ITEM 3c — _mintSetField helper decimal keyboard

### Files reviewed
- `numista_mobile/lib/screens/add_coins_hub.dart`

### Condition
`_mintSetField` helper accepts `inputFormatters` param; call site for cost field uses decimal keyboard + formatter.

### Verbatim before (_mintSetField signature)
```dart
Widget _mintSetField(String label, TextEditingController ctrl,
    {TextInputType keyboardType = TextInputType.text}) {
```

### Verbatim after (_mintSetField signature)
```dart
Widget _mintSetField(String label, TextEditingController ctrl,
    {TextInputType keyboardType = TextInputType.text,
     List<TextInputFormatter>? inputFormatters}) {
```

### Verbatim before (call site ~line 1690)
```dart
_mintSetField('Cost Paid', _mintCostCtrl, keyboardType: TextInputType.number),
```

### Verbatim after (call site ~line 1690)
```dart
_mintSetField('Cost Paid', _mintCostCtrl,
  keyboardType: const TextInputType.numberWithOptions(decimal: true),
  inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d{0,2}'))]),
```

### Checklist
- [x] `_mintSetField` signature extended with `inputFormatters` optional param
- [x] `inputFormatters` wired into the inner `TextField`
- [x] Call site for Cost Paid uses `numberWithOptions(decimal: true)`
- [x] DO NOT TOUCH: `add_coins_hub.dart:2906` (cert number field, `decimal: false` correct — NOT touched)

> **NOTE:** `TextInputType.numberWithOptions(decimal: true)` sets `inputmode="decimal"` on Flutter Web, ensuring a decimal-capable numeric keyboard on both mobile and web.

---

## ITEM 4 — CTA subtitle + button label 16px

### Files reviewed
- `numista_mobile/lib/screens/add_coins_hub.dart`

### Condition
CTA subtitle text and "Open Manual Entry" button label are both `fontSize: 16`.

### Verbatim before (subtitle ~line 718)
```dart
Text('...', style: TextStyle(fontSize: 14, color: _sub)),
```

### Verbatim after
```dart
Text('...', style: TextStyle(fontSize: 16, color: _sub)),
```

### Verbatim before (button label)
```dart
child: const Text('Open Manual Entry'),
```

### Verbatim after
```dart
child: const Text('Open Manual Entry', style: TextStyle(fontSize: 16)),
```

### Checklist
- [x] CTA subtitle `fontSize` changed from `14` → `16`
- [x] "Open Manual Entry" button label has explicit `fontSize: 16`

---

## ITEM 6 — Login screen IndexedStack replaces AnimatedSize+TabBarView

### Files reviewed
- `numista_mobile/lib/screens/login_screen.dart`

### Condition
- `AnimatedSize + fixed SizedBox + TabBarView` replaced by `IndexedStack(index: _tabCtrl.index, children: [_buildSignInTab(), _buildCreateTab()])`
- `_signInTab` unused field suppressed with `// ignore: unused_field`
- Stats badges Row wrapped in `FittedBox(fit: BoxFit.scaleDown)`
- Header Row text column wrapped in `Flexible` (prevents 187px overflow at 360px)
- `_divider` middle child wrapped in `Flexible(flex: 10)` + `overflow: TextOverflow.ellipsis` (prevents 83px overflow at 312px available)
- Both `_divider(...)` call sites wrapped in `SizedBox(width: double.infinity, child: _divider(...))`

### Verbatim before (tab content ~line 487)
```dart
AnimatedSize(
  duration: const Duration(milliseconds: 200),
  child: SizedBox(
    height: _tabCtrl.index == 0 ? _signInHeight : _createHeight,
    child: TabBarView(
      controller: _tabCtrl,
      children: [_buildSignInTab(), _buildCreateTab()],
    ),
  ),
),
```

### Verbatim after
```dart
IndexedStack(
  index: _tabCtrl.index,
  children: [ _buildSignInTab(), _buildCreateTab() ],
),
```

### Verbatim before (header Column ~line 290)
```dart
const Column(
  crossAxisAlignment: CrossAxisAlignment.start,
  children: [
    Text('NUMISTA.AI', style: TextStyle(...)),
    Text('AI-Powered Coin Collection Manager', style: TextStyle(...)),
  ],
),
```

### Verbatim after
```dart
const Flexible(
  child: Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text('NUMISTA.AI', style: TextStyle(...)),
      Text('AI-Powered Coin Collection Manager', style: TextStyle(...)),
    ],
  ),
),
```

### Verbatim before (_divider ~line 949)
```dart
Widget _divider(String label) => Row(children: [
      const Expanded(child: Divider(color: _border)),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Text(label, style: TextStyle(color: _grey.withAlpha(180), fontSize: NumistaTheme.textBodySm)),
      ),
      const Expanded(child: Divider(color: _border)),
    ]);
```

### Verbatim after (_divider ~line 949)
```dart
Widget _divider(String label) => Row(children: [
      const Expanded(child: Divider(color: _border)),
      Flexible(
        flex: 10,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text(
            label,
            style: TextStyle(color: _grey.withAlpha(180), fontSize: NumistaTheme.textBodySm),
            overflow: TextOverflow.ellipsis,
            softWrap: false,
          ),
        ),
      ),
      const Expanded(child: Divider(color: _border)),
    ]);
```

### Verbatim before (divider call sites ~lines 496/503)
```dart
_divider('or'),
...
_divider('explore without an account'),
```

### Verbatim after
```dart
SizedBox(width: double.infinity, child: _divider('or')),
...
SizedBox(width: double.infinity, child: _divider('explore without an account')),
```

### Checklist
- [x] `TabBarView` removed — `find.byType(TabBarView)` → `findsNothing` in test ✅
- [x] `IndexedStack` present — `find.byType(IndexedStack)` → `findsOneWidget` in test ✅
- [x] `AnimatedSize` removed
- [x] `_signInTab` unused field suppressed (`// ignore: unused_field`)
- [x] Stats badges Row wrapped in `FittedBox(fit: BoxFit.scaleDown)` — no overflow
- [x] Header Row text Column wrapped in `Flexible` — 187px overflow at 360px fixed
- [x] `_divider` middle child is `Flexible(flex: 10)` — 83px overflow at 312px fixed
  - Root cause: `textBodySm = 14.0`, "explore without an account" (26 chars × 14px = 364px + 24px padding = 388px) exceeded 312px available
- [x] Both `_divider(...)` call sites wrapped in `SizedBox(width: double.infinity)` for tight constraints
- [x] Login test `p7_v84_login_sign_in_button_visible_at_360x680` PASSES ✅

---

## ITEM 7 — Per-endpoint fetch guard (UpcomingReleasesService)

### Files reviewed
- `numista_mobile/lib/services/upcoming_releases_service.dart`

### Condition
Replaced single `static bool _fetchAttempted` with `static final Set<String> _attempted = {}` + `_cacheKeyFor(endpoint)` per-endpoint method. Added `resetForTest()` and `wasAttempted()` test helpers.

### Verbatim before
```dart
static bool _fetchAttempted = false;
static const String _cacheKey = 'upcoming_releases_cache';

Future<void> fetchAndCache() async {
  if (_fetchAttempted) return;
  _fetchAttempted = true;
  // ...
}
```

### Verbatim after
```dart
static final Set<String> _attempted = {};

static String _cacheKeyFor(String endpoint) =>
    'upcoming_releases_cache_${endpoint.replaceAll('/', '_')}';

@visibleForTesting
static void resetForTest() => _attempted.clear();

@visibleForTesting
static bool wasAttempted(String endpoint) => _attempted.contains(endpoint);

Future<void> fetchAndCache(String endpoint) async {
  if (_attempted.contains(endpoint)) return;
  _attempted.add(endpoint);
  // ...
}
```

### Checklist
- [x] `static bool _fetchAttempted` removed
- [x] `static final Set<String> _attempted = {}` added
- [x] `_cacheKeyFor(endpoint)` generates per-endpoint cache key
- [x] `resetForTest()` clears set; `wasAttempted(endpoint)` checks membership
- [x] Unit test `per-endpoint _attempted Set guards each endpoint independently` PASSES ✅
- [x] Two distinct endpoints (ep1 ≠ ep2) verified independently guarded

---

## TEST GATE SUMMARY

| Test | Status |
|---|---|
| p7_v8_manual_entry_full_screen_scaffold | ✅ PASS |
| p7_v8_manual_entry_qty_prefill_fix_and_labels | ✅ PASS |
| p7_v8_confirm_dialog_cancel_makes_zero_http_calls | ✅ PASS |
| p7_v8_demo_mode_guard_makes_zero_http_calls | ✅ PASS |
| converts http.ClientException to plain English | ✅ PASS |
| converts HTTP status codes 401, 403, 500 cleanly | ✅ PASS |
| p7_v8_pin_box_row_fits_320px_width_without_overflow | ✅ PASS |
| maps Add New Coins route to index 2 (My Collection) | ✅ PASS |
| p7_v84_program_card_no_overflow_at_389px | ✅ PASS |
| p7_v84_program_card_no_overflow_at_1025px | ✅ PASS |
| p7_v84_login_sign_in_button_visible_at_360x680 | ✅ PASS |
| per-endpoint _attempted Set guards each endpoint independently | ✅ PASS |
| **TOTAL** | **12 / 12 PASS** |

`flutter analyze --no-pub` → **No issues found** (confirmed separately)

**V8.4 BUILD REVIEW: PASS — READY FOR GROK CoS SCORE**
