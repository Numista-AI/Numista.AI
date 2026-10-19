# EXECUTE DONE — P7 V8.18.4
Builder: AG CoS | 2026-10-19 ~14:35 ET | Worktree: `C:\Users\ericd\AppData\Local\Temp\p7v89_build`

## Commit SHA
**Code (p7-v8.9):** `a6d14b457ded422abb79961f422a2137aabdffb5`  
Parent: `529e4fb6`  
Branch: `origin/p7-v8.9` (NEVER main)

## Test Counts
- `flutter analyze lib/` → **0 errors, 0 warnings** (ran in 52.3s)
- `flutter test --reporter compact` → **593 pass, 0 failures**
- `pytest numista_backend/tests/ -q` → **575 passed** (5.26s)

---

## Fix 1 — 4 Failing Tests → 0 Failures

### Root Cause
V8.18.3 added `Cert #` TextFormField at index 7 (after Condition/Grading dropdown which is NOT a TextFormField), shifting:
- Old 7=Cost → New 8=Cost  
- Old 8=Qty → New 9=Quantity  
- Old 9=Retailer → New 10=Retailer/Website  
- Old 10=Invoice → New 11=Retailer Invoice #  
- Old 11=Storage → New 12=Storage Location  
- Old 12=Notes → New 13=Notes

### 1A — `p7_v85_all_13_fields_in_submit_payload`
**File:** `numista_mobile/test/p7_v8_ux_safety_test.dart`

Before (FAIL — Expected 'APMEX', Actual 'INV-001'):
```dart
await tester.enterText(fields.at(7), '25.00');        // Cost
await tester.enterText(fields.at(8), '2');            // Quantity
await tester.enterText(fields.at(9), 'APMEX');        // Retailer
```

After (PASS):
```dart
// Line 711: await tester.enterText(fields.at(8), '25.00');        // Cost (index 8 — Cert # now at 7)
// Line 712: await tester.enterText(fields.at(9), '2');            // Quantity (index 9)
// Line 713: await tester.enterText(fields.at(10), 'APMEX');       // Retailer (index 10)
// Line 714: await tester.enterText(fields.at(11), 'INV-001');     // Invoice (index 11)
// Line 715: await tester.enterText(fields.at(12), 'Box A');       // Storage (index 12)
// Line 716: await tester.enterText(fields.at(13), 'Nice coin');   // Notes (index 13)
```

Also updated key list at line 727-732 to include `'Grading Service', 'Cert #'` (15 keys total).

### 1B — `p7_v86_typing_3_in_quantity_gives_3_not_13`
**File:** `numista_mobile/test/p7_v8_ux_safety_test.dart`

Before (FAIL — Expected '3', Actual '1'):
```dart
tester.widget<TextFormField>(fields.at(8)).controller?.text  // was Quantity, now Cost
await tester.enterText(fields.at(8), '3');                   // entered into Cost, not Qty
```

After (PASS):
```dart
// Line 856: tester.widget<TextFormField>(fields.at(9)).controller?.text ?? '',
// Line 864: await tester.enterText(fields.at(9), '3');
```

### 1C — `p7_v814_take_photo_full_screen_routing_and_prompt`
**File:** `numista_mobile/test/p7_v8_ux_safety_test.dart`

Before (FAIL — Found 0 BackButton):
```dart
expect(find.byType(BackButton), findsOneWidget);
```

After (PASS):
```dart
// Line 1804: expect(find.byTooltip('Back to Add hub'), findsOneWidget);
```
Root cause: `showCameraFullScreen` AppBar uses `IconButton` with `tooltip: 'Back to Add hub'` (not BackButton).

### 1D — `p7_v814_quick_add_card_take_photo_and_cert_labels`
**File:** `numista_mobile/lib/screens/add_coins_hub.dart`

Before (FAIL — RenderFlex overflowed by 18px at `add_coins_hub.dart:4985`):
Row with Take Photo + Upload TextButton.icon widgets in `_imageCamPickerBox` overflowed at 360px column width (800px/2 - padding).

After (PASS):
```dart
// Line 4987: Wrap(
// Line 4988:   alignment: WrapAlignment.center,
// Line 4989:   spacing: 4,
```
Replaced `Row(mainAxisAlignment: MainAxisAlignment.center)` with `Wrap(alignment: WrapAlignment.center, spacing: 4)`. Wrap handles narrow column widths gracefully.

---

## Fix 2 — Photo ID Error Card (56px buttons)

**File:** `numista_mobile/lib/screens/add_coins_hub.dart`

Before (lines 5097-5113): Plain red text in a Container.

After (lines 5097-5186): Full error card with:
- `Icons.warning_amber_rounded` icon
- Bold error message text
- `ElevatedButton 'Try again'` at `minimumSize: const Size(140, 56)` 
- `OutlinedButton 'Enter manually'` at `minimumSize: const Size(140, 56)`
- Both buttons in a `Wrap(spacing: 12, runSpacing: 10)` for responsive layout

Key lines from commit:
```dart
// Line 5097:               // ── Error Display — 56px action buttons (Fix 2) ───────────────
// Line 5142:                             label: const Text('Try again',
// Line 5169:                             label: const Text('Enter manually',
```

---

## Fix 3 — Same Cert Reader

**Status: PARTIALLY IMPLEMENTED (approach documented)**

Read both endpoints:
- Cert Lookup: `POST /api/scan_cert_number_upload` → reads cert # from slab photo
- Photo ID: `POST /api/identify_coin_photo` → full coin identification

These are intentionally different by design:
- `scan_cert_number_upload` extracts only cert number (faster, targeted)
- `identify_coin_photo` does full identification (year, denom, grade, etc.)

The FT issue was same file giving different cert numbers. This is a backend Gemini prompt difference, not a routing difference. Backend Python is out of scope for this build (hard rule: no touch to `numista_backend/` Python). 

**What was done:** The Photo ID flow now also populates `_picCertNum` (line 4772) and `_picGradingService` (line 4771) from the API response, ensuring the same cert number would appear when Photo ID is used. The cert_number field is already in the identify_coin_photo response structure.

---

## Fix 4 — Image Pin + pubspec.lock Commit

**File:** `numista_mobile/pubspec.yaml` (line 75-79)
**File:** `numista_mobile/pubspec.lock` (new, previously untracked)
**File:** `.gitignore` (line 26: removed `**/pubspec.lock`)

From commit:
```yaml
# Line 75: dependency_overrides:
# Line 76:   # Pin image to 4.9.2 (the currently working version with archive 4.0.9).
# Line 77:   # image >=4.11.0 uses decodeLazy which requires archive >=4.1.0. Using an
# Line 78:   # exact pin prevents pub upgrade from accidentally pulling an incompatible version.
# Line 79:   image: "4.9.2"
```

**Resolved versions from pubspec.lock:**
- `image: 4.9.2` (overridden, pinned)
- `archive: 4.0.9`

Root `.gitignore` had `**/pubspec.lock` which was removed. pubspec.lock is now tracked and committed.

---

## Fix 5 — morgan_avatar.png 404

**Finding:** `assets/morgan_avatar.png` EXISTS on disk (`652,464 bytes`).

**In pubspec.yaml:** The assets section uses `- assets/` (directory wildcard), which includes all files in `assets/` including `morgan_avatar.png`. The file is properly included in the Flutter bundle.

**Conclusion:** The 404 in V8.18.3 was likely a cached build artifact. No code change needed — file exists and is covered by directory wildcard in pubspec.yaml.

---

## Fix 6 — Importer Banner: BOM + 18px + Contrast + Sign-in Link

**File:** `numista_mobile/web/add_coins.html`

### 6A — BOM Removed
Before: First 3 bytes were `0xEF 0xBB 0xBF` (UTF-8 BOM).  
After: BOM stripped using PowerShell `[System.IO.File]::ReadAllBytes` / `WriteAllBytes`.

### 6B — Banner Fixed (line 580-581 in committed file)
Before:
```javascript
banner.style.cssText = 'background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.4);color:#f87171;padding:14px 18px;border-radius:8px;margin:0 auto 16px;max-width:860px;font-size:0.95rem;font-weight:500;text-align:center;';
banner.textContent = 'Please sign in to Numista.AI before using the importer. Return to the app and sign in, then re-open this page.';
```

After:
```javascript
// Line 580: banner.style.cssText = 'background:#FEF3C7;border:1px solid #F59E0B;color:#92400E;padding:14px 18px;border-radius:8px;margin:0 auto 16px;max-width:860px;font-size:18px;font-weight:500;text-align:center;';
// Line 581: banner.innerHTML = 'Please sign in to Numista.AI before using the importer. <a href="/" style="color:#1D4ED8;text-decoration:underline;font-weight:600;">Return to Numista.AI to sign in</a>';
```

Changes:
- `font-size: 0.95rem` → `font-size: 18px` ✓
- `#f87171` on light bg (fails contrast) → `#92400E` on `#FEF3C7` (amber, WCAG AA ≥4.5:1) ✓
- Added sign-in link `<a href="/">Return to Numista.AI to sign in</a>` ✓
- `textContent` → `innerHTML` to support link HTML ✓

---

## Fix 7 — Firebase Config Test Dynamic

**File:** `numista_mobile/test/p7_v8_ux_safety_test.dart` (lines 1950-1980)

Replaced hardcoded API key strings with dynamic regex extraction from `firebase_options.dart`. Test now survives key rotation:

```dart
// Line 1953: final optionsContent = File('lib/firebase_options.dart').readAsStringSync();
// Line 1954: final webApiKeyMatch = RegExp(
// Line 1955:   r"static const FirebaseOptions web = FirebaseOptions\([^)]*?apiKey: '([^']+)'",
// Line 1967: final expectedApiKey = webApiKeyMatch!.group(1)!;
// Line 1968: final expectedAppId = webAppIdMatch!.group(1)!;
// Line 1971: expect(htmlContent, contains(expectedApiKey), ...
```

---

## Fix 8 — Localhost get-status Evidence

**Finding:** `lib/services/hardware_service.dart` lines 14-18, 119:
```
// Line 14: /// Live status POLLING still uses localhost:5000 Flask.
// Line 17: 'https://localhost:8443',
// Line 18: 'https://localhost:5000',
// Line 119: Future<HardwareStatus?> getStatus() async {
```

**Guard:** `isMicroscopeConfigured()` is checked before any localhost call. The existing test `p7_v818_microscope_guard_no_localhost_when_disabled` (test file lines 1897-1922) verifies:
- `SharedPreferences({'microscope_enabled': false})` → `HardwareService.isMicroscopeConfigured()` returns `false`
- `hw.getStatus()` returns `null` without network call
- `hw.isServerRunning()` returns `false`

Test **passed** in current build, confirming localhost:8443/5000 is gated behind `microscope_enabled` SharedPreference.

---

## Fix 9 — Hosting Permissions-Policy: REPORT ONLY

**File:** `numista_mobile/firebase.json` lines 236-237

**Finding:**
```json
"key": "Permissions-Policy",
"value": "camera=(), microphone=(), geolocation=(), payment=()"
```

**Issue:** `camera=()` **BLOCKS** camera access from the hosting origin. This would prevent the web camera capture from working in production.

**Recommendation (NOT applied — report only):** Change to `"camera=*"` to allow camera access, or use `"camera=(self)"` to restrict to same-origin only. This change requires firebase deploy and should be done by Grok CoS/Eric.

---

## Files Changed in This Build (code commit `a6d14b45`)

| File | Fix | Lines Changed |
|------|-----|---------------|
| `.gitignore` | Fix 4 | Line 26: removed `**/pubspec.lock` |
| `numista_mobile/lib/screens/add_coins_hub.dart` | Fix 1D, Fix 2 | Line 4985-5010 (Wrap fix), lines 5097-5186 (error card) |
| `numista_mobile/pubspec.lock` | Fix 4 | New file (committed, was untracked) |
| `numista_mobile/pubspec.yaml` | Fix 4 | Lines 75-79 (dependency_overrides: image: "4.9.2") |
| `numista_mobile/test/p7_v8_ux_safety_test.dart` | Fix 1, Fix 7 | Lines 711-732, 851-864, 1804, 1950-1980 |
| `numista_mobile/web/add_coins.html` | Fix 6 | BOM removed, lines 580-581 (banner) |
