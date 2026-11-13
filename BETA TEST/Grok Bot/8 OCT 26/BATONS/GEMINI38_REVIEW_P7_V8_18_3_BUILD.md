# GEMINI38 REVIEW — P7 V8.18.3 Build

**Reviewer:** Gemini 3.8 Flash (AG CoS automated review — one run per build version per Rule 9.3)
**Branch:** `p7-v8.9`
**Commit SHA:** `529e4fb6`
**Date:** 2026-10-19

---

## Files Changed

1. `numista_mobile/web/add_coins.html`
2. `numista_mobile/lib/screens/add_coins_hub.dart`
3. `numista_mobile/lib/widgets/add_coin_manual_form.dart`
4. `numista_mobile/lib/widgets/morgan_greeter.dart`
5. `numista_mobile/test/p7_v8_ux_safety_test.dart`

---

## Fix-by-Fix Review

### Fix 1A — Firebase Web apiKey
**File:line:** `numista_mobile/web/add_coins.html:546`
**Before:**
```js
apiKey: "AIzaSyDSM3pQl0oWdZgOw2vXCvhyRH899l-ZvcM",
```
**After:**
```js
apiKey: "AIzaSyCPGC879Tl1FaGucQmlw7qKL25b8v4ACF8",
```
**File:line:** `numista_mobile/web/add_coins.html:549`
**Before:**
```js
appId: "1:568985927038:web:bf2a6f690b59e2148b072f",
```
**After:**
```js
appId: "1:568985927038:web:9ea56548eed27d5a8b072f",
```

**Checklist:**
- [x] Web Firebase config now uses web app's key, not Android key
- [x] `authDomain`, `projectId`, `storageBucket`, `messagingSenderId` unchanged (were already correct)
- [x] `onAuthStateChanged` will now receive the correct Firebase Auth user object
- [x] Test `add_coins_html_uses_web_firebase_config` confirms key presence in source
- [ ] Live main still has Android key (documented; not fixed — cannot push to main)

**Verdict for Fix 1A:** ✅ PASS

---

### Fix 1B — No-user auth guard
**File:line:** `numista_mobile/web/add_coins.html` (onAuthStateChanged callback)
**After (verbatim):**
```js
if (!user) {
  const banner = document.getElementById('auth-required-banner') || document.createElement('div');
  banner.id = 'auth-required-banner';
  banner.textContent = 'Sign in required to add coins.';
  document.body.prepend(banner);
  const btn = document.getElementById('start-btn');
  if (btn) btn.disabled = true;
  return;
}
```

**Checklist:**
- [x] Null user → shows auth banner, disables start button
- [x] Does not throw if start-btn is absent (`if (btn)` guard)
- [x] Returns early — no further processing if unauthenticated

**Verdict for Fix 1B:** ✅ PASS

---

### Fix 2A — Cert scan junk guard
**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3201-3229`
**After (verbatim):**
```dart
final rawCert = (scanResult['cert_number'] ?? '').toString().toLowerCase().trim();
final junkCerts = {'blurred', 'unknown', 'none', ''};
final isJunkCert = junkCerts.contains(rawCert) ||
    !RegExp(r'^[a-zA-Z0-9\-]+$').hasMatch(rawCert);
if (isJunkCert) {
  setState(() => _certError = 'Could not read cert number — please enter manually.');
}
```

**Checklist:**
- [x] Rejects 'blurred', 'unknown', 'none', empty string
- [x] Rejects non-alphanumeric junk via regex
- [x] Shows user-visible message instead of silently accepting garbage
- [x] Test `cert_scan_guard_rejects_blurred_artifacts` confirms guard presence in source

**Verdict for Fix 2A:** ✅ PASS

---

### Fix 2B/2C — Low-confidence camera scan guard
**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:4709-4747`
**After (verbatim):**
```dart
final confidence = (result['confidence'] as num?)?.toDouble() ?? 1.0;
final year = result['year']?.toString() ?? '';
final denom = result['denomination']?.toString() ?? '';
final isLowConf = confidence < 0.4;
final isJunk = year.toLowerCase() == 'none' && denom.toLowerCase() == 'unknown';
if (isLowConf || isJunk) {
  setState(() => _camError = 'Scan result was unclear — please retake or enter manually.');
  return;
}
```

**Checklist:**
- [x] Confidence < 0.4 → shows retry message
- [x] year=None AND denom=Unknown → shows retry message
- [x] Returns early — does not show confirm form with junk data
- [x] Default confidence 1.0 if field absent (safe — only real low-confidence results blocked)

**Verdict for Fix 2B/2C:** ✅ PASS

---

### Fix 5 — Camera error permissions-policy guard
**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3165-3177`
**After (verbatim):**
```dart
} catch (e) {
  final msg = e.toString().toLowerCase();
  if (msg.contains('permissions-policy') || msg.contains('not allowed')) {
    _camError = 'Camera blocked by browser permissions policy. '
        'Please allow camera access in site settings.';
  } else if (msg.contains('notfound') || msg.contains('no camera')) {
    _camError = 'No camera found. Please use Upload instead.';
  } else {
    _camError = 'Camera not available. Please use Upload instead.';
  }
}
```

**Checklist:**
- [x] `permissions-policy` string caught and given plain-English message
- [x] `not allowed` string caught (browser DOMException variant)
- [x] Generic fallback still present
- [x] Test `camera_error_guard_includes_permissions_policy` confirms guard in source

**Verdict for Fix 5:** ✅ PASS

---

### Fix 6 — Text sizes and touch targets
**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart` (multiple lines)

**Before/After (verbatim samples):**

Photo ID subtitle (~line 5021):
```dart
// Before:
Text('Identify a coin from a photo', style: TextStyle(fontSize: 13, ...))
// After:
Text('Identify a coin from a photo', style: TextStyle(fontSize: 18, ...))
```

"Take Photo" button (~line 4974):
```dart
// Before:
ElevatedButton(style: ElevatedButton.styleFrom(textStyle: TextStyle(fontSize: 11)),
// After:
ElevatedButton(style: ElevatedButton.styleFrom(
  textStyle: const TextStyle(fontSize: 18),
  minimumSize: const Size(48, 48),
),
```

"Scan Coin Now" (~line 5131):
```dart
// Before:
ElevatedButton(style: ElevatedButton.styleFrom(...),
// After:
ElevatedButton(style: ElevatedButton.styleFrom(
  minimumSize: const Size(200, 56),
  ...
),
```

**Checklist:**
- [x] Photo ID subtitle: 13px → 18px
- [x] Info banner text: 12.5px → 18px
- [x] Take Photo button: 11px → 18px, touch target 48px
- [x] Upload button: same fix
- [x] Scan Coin Now: 56px height minimum
- [x] Bulk page subtitle: 16px → 18px
- [x] All targets meet 48px minimum (WCAG AA touch target)

**Verdict for Fix 6:** ✅ PASS

---

### Fix 7A — Light mode CSS
**File:line:** `numista_mobile/web/add_coins.html` (`@media (prefers-color-scheme: light)` block)
**After (verbatim):**
```css
@media (prefers-color-scheme: light) {
  .morgan-guide-card { background: #f8fafc !important; color: #0f172a !important; }
  .morgan-guide-card .card-title { color: #1e293b !important; }
  .morgan-guide-card .card-body { color: #334155 !important; }
}
```

**Checklist:**
- [x] Light mode no longer shows dark card backgrounds in Morgan guide section
- [x] Uses `!important` to override inline styles from JS template literals
- [x] Does not affect dark mode (`prefers-color-scheme: dark` block unchanged)

**Verdict for Fix 7A:** ✅ PASS

---

### Fix 7B — Favicon 404
**File:line:** `numista_mobile/web/add_coins.html:<head>`
**After (verbatim):**
```html
<link rel="icon" type="image/png" href="favicon.png">
```

**Checklist:**
- [x] favicon.ico 404 eliminated by explicit favicon link
- [x] `morgan_avatar.png` has no explicit references in web dir — not fixable (browser auto-request); documented finding
- [x] `favicon.png` exists in `numista_mobile/web/` per project structure

**Verdict for Fix 7B:** ✅ PASS

---

### Fix 8A — Microscope tile removed
**File:line:** `numista_mobile/lib/widgets/morgan_greeter.dart:193-201`
**Before (verbatim):**
```dart
_AddTile(tileId: 'microscope', icon: Icons.biotech, label: 'Identify with Microscope',
    onTap: () => widget.onNavigate?.call('Microscope')),
```
**After:** Tile removed entirely. The block no longer exists.

**Checklist:**
- [x] Microscope tile absent from Welcome-path add menu
- [x] No other `'microscope'` tile references in morgan_greeter.dart
- [x] Test `microscope_tile_removed_from_morgan_greeter` confirms absence in source
- [x] `isMicroscopeConfigured()` guard in `hardware_service.dart` retained (belt-and-suspenders)

**Verdict for Fix 8A:** ✅ PASS

---

### Fix 8B — Microscope Station text removed
**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:5046-5048`
**Before (verbatim):**
```dart
'For high-resolution coin grading, please use the Microscope Station.'
```
**After (verbatim):**
```dart
'For high-resolution coin grading, use the Desktop Agent with a high-res camera.'
```

**Checklist:**
- [x] "Microscope Station" language removed from camera tab
- [x] Replacement text is accurate (Desktop Agent, not localhost hardware)
- [x] Test `microscope_station_text_removed_from_camera_tab` confirms absence

**Verdict for Fix 8B:** ✅ PASS

---

### Fix 8D — Photo ID back button
**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:638-656`
**Before (verbatim):**
```dart
const BackButton(),
```
**After (verbatim):**
```dart
IconButton(
  icon: const Icon(Icons.arrow_back),
  onPressed: () {
    if (widget.onNavigate != null) {
      widget.onNavigate!('Add New Coins');
    } else {
      Navigator.pop(context);
    }
  },
),
```

**Checklist:**
- [x] Back navigates to 'Add New Coins' hub instead of arbitrary stack pop
- [x] Falls back to `Navigator.pop` if `onNavigate` is null (safe for standalone use)
- [x] Uses `IconButton` — 48px touch target by default in Material 3

**Verdict for Fix 8D:** ✅ PASS

---

### Fix 10A/B/C — Manual form grading service + cert
**File:line:** `numista_mobile/lib/widgets/add_coin_manual_form.dart:56, 87, 102, 125, 140, 219-270, 350-368`

State var (line 56, verbatim):
```dart
String _gradingService = 'None';
```

Controller init (line 87, verbatim):
```dart
_certCtrl = TextEditingController(text: _formData['Cert #'] as String? ?? '');
```

Dropdown (line 235-236, verbatim):
```dart
DropdownButtonFormField<String>(
  initialValue: _gradingService,
```
*(Note: `value` → `initialValue` — Flutter 3.33+ deprecation fix applied)*

Cert field (line 269, verbatim):
```dart
_buildField(context, 'Cert #', 'e.g. 8321797-003',
    controller: _certCtrl, focusNode: _certFocus),
```

Submit map additions (line ~360, verbatim):
```dart
'Grading Service': _formData['Grading Service'] ?? _gradingService,
'grading_service': _formData['Grading Service'] ?? _gradingService,
'Cert #': _certCtrl.text.trim(),
'cert_number': _certCtrl.text.trim(),
```

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:2050-2080`
Hub coinDoc additions (verbatim):
```dart
'grading_service': data['grading_service'] ?? data['Grading Service'] ?? '',
'cert_number': data['cert_number'] ?? data['Cert #'] ?? data['certNo'] ?? '',
```

**Checklist:**
- [x] `_gradingService` state variable declared and initialized
- [x] `_certCtrl` controller created, initialized, disposed
- [x] `_certFocus` focus node created and disposed
- [x] `DropdownButtonFormField` with 7 options (None/NGC/PCGS/CAC/CACG/ANACS/ICG)
- [x] `initialValue` used (not deprecated `value`)
- [x] Cert # field uses `_buildField` → `ValueKey('manual_field_Cert #')`
- [x] `_submit()` includes both human-readable and snake_case keys
- [x] `_resetForm()` resets cert controller and grading service
- [x] Hub coinDoc includes grading_service and cert_number
- [x] `decimal: false` on cert number field NOT changed (per hard rule)
- [x] Widget test uses `find.byKey(const ValueKey('manual_field_Cert #'))` — correct for RichText labels
- [x] Tests: `manual_form_has_grading_service_and_cert`, `manual_form_submit_includes_grading_service_and_cert`, `manual_hub_coinDoc_includes_grading_cert` — all pass

**Verdict for Fix 10:** ✅ PASS

---

## Deprecation Fix
**File:line:** `numista_mobile/lib/widgets/add_coin_manual_form.dart:236`
**Before:** `value: _gradingService,`
**After:** `initialValue: _gradingService,`
Required by Flutter 3.33+ — `DropdownButtonFormField.value` deprecated in favor of `initialValue`.
This was the sole cause of `flutter analyze` reporting 1 issue. Fixed. `flutter analyze` now reports **0 issues**.

---

## Gate Summary

| Gate | Result |
|---|---|
| `flutter analyze lib/` | ✅ **0 issues** (after deprecation fix) |
| `flutter test` | ✅ **588 pass**, 4 pre-existing failures (unchanged from baseline) |
| `python -m pytest numista_backend/tests/` | ✅ **575 passed** |
| `git push origin p7-v8.9` | ✅ `529e4fb6` |

---

## FINAL VERDICT: ✅ PASS

All 10 fixes applied. `flutter analyze` clean. `flutter test` meets baseline (588 > 585). pytest meets baseline (575). No new test failures introduced. Push succeeded. Branch `p7-v8.9` at `529e4fb6` is ready for Grok CoS UX+FT gate.
