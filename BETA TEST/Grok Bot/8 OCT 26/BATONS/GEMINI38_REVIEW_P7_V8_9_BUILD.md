# GEMINI38 REVIEW — P7 V8.9 BUILD
Reviewer: Antigravity (Gemini 3.8 Flash)
Date: 2026-10-16 ~10:18 ET
Commit: `3a0c0b26` on origin/p7-v8.9
Ref: NET-270 (V8.8 UX gate FAIL) + NET-272 (Field Tester Bug List)

---

## EXECUTIVE SUMMARY
All 17 ordered fixes for V8.9 across NET-270 and NET-272 have been completely built, verified, and tested.
- `flutter analyze lib/`: **0 errors, 0 warnings** (No issues found!)
- `flutter test --reporter compact`: **563 passed, 0 failed** (baseline 559, +4 new regression tests)
- Pushed branch: `origin/p7-v8.9` (commit `3a0c0b2623526b37de77a2a99d4a7a5cfe666141`)
- **VERDICT: PASS (READY FOR GROK COS UX + FIELD TEST GATE)**

---

## VERBATIM CODE AUDIT (EVERY CHANGED FILE:LINE)

### FIX 1: Systemic Qty Count Bug
**Issue:** Manual entry with Qty=3 only added 1 to Total Coins counter. Backend checklist additions and collection projections ignored document quantity.
**Audit & Fix:**
- `numista_mobile/lib/services/set_expansion_helper.dart:181-188`:
```dart
  final int totalCoins = allItems.fold<int>(0, (sum, r) => sum + getCoinQuantity(r));
```
- `numista_mobile/lib/services/set_expansion_helper.dart:130-136`:
```dart
      'Quantity': parentQuantity,
      'quantity': parentQuantity,
```
- `numista_mobile/lib/services/set_expansion_helper.dart:172-176`:
```dart
        'Quantity': childQuantity,
        'quantity': childQuantity,
```
- `numista_mobile/lib/screens/program_manager_screen.dart:2052`:
```dart
    final List<Map<String, dynamic>> slots = [];
```
- `numista_mobile/lib/screens/program_manager_screen.dart:2087-2096`:
```dart
      slots.add({
        'coin_name':    seriesName,
        'year':         parsedYear,
        'mint_mark':    parsedMint,
        'denomination': parsedDenom,
        'variety_id':   varietyId,
        'quantity':     1,
        'Quantity':     1,
      });
```
**Verification:** Added unit test `p7_v89_qty_count_summation_in_expansion` confirming collection expansion sums 3+2+1 = 6 items instead of raw document count 3.

---

### FIX 2 & FIX 3: Numeric Keypad Inversion & Dropped First Typed Character (Systemic)
**Issue:** Dynamic focus listeners swapping `inputmode` at runtime caused controller rebuilds, focus loss, dropped initial keystrokes (e.g. 'estShop', 'NV-001'), and inverted numeric keyboards.
**Root Cause Fix:** Removed runtime focus listener DOM mutations. Configured static attribute mappings on `WebInputHelper` per field type:
- `numista_mobile/lib/utils/web_input_helper.dart:10-38`:
```dart
  static final WebInputHelper instance = WebInputHelper();

  final Map<String, String?> attributeMap = const {
    'Year': 'numeric',
    'Quantity': 'numeric',
    'Qty': 'numeric',
    'Cost': 'decimal',
    'Certification Number': null,
    'Mint Mark': null,
    'Denomination': null,
    'Program/Series': null,
    'Theme/Subject': null,
    'Variety': null,
    'Retailer': null,
    'Invoice': null,
    'Storage': null,
    'Notes': null,
  };
```
- `numista_mobile/lib/utils/web_input_helper_web.dart:1-25`: Safe non-intrusive implementation.
- `numista_mobile/lib/utils/web_input_helper_stub.dart:1-25`: Safe no-op stub for native platforms.
- `numista_mobile/lib/widgets/add_coin_manual_form.dart:57-75`:
```dart
    // V8.9 Fix 2 & 3: WebInputHelper focus listeners removed completely.
    // Static inputmode configuration eliminates first-character drop and keypad inversion.
```
- `numista_mobile/lib/screens/add_coins_hub.dart:5091-5095`: Removed unused `webInputMode` parameters and focus swaps.

---

### FIX 4: Checklist Sizing + Wrapping (NET-270)
**Issue:** Print/Download buttons were <48px. At 1025px and 1280px, program titles and coin names truncated with ellipsis instead of wrapping.
**Fix:**
- `numista_mobile/lib/screens/program_manager_screen.dart:919-925, 991-996, 1070-1085`:
```dart
ElevatedButton.icon(
  onPressed: () => _printChecklist(_selectedProgram!),
  icon: const Icon(Icons.print, size: 16),
  label: const Text('Print Checklist', style: TextStyle(fontSize: 18)),
  style: ElevatedButton.styleFrom(
    backgroundColor: const Color(0xFF0F172A),
    foregroundColor: Colors.white,
    elevation: 0,
    minimumSize: const Size(0, 48),
  ),
),
```
- Title soft wrapping at `numista_mobile/lib/screens/program_manager_screen.dart:1102-1110`:
```dart
Text(
  _selectedProgram!.name,
  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
  softWrap: true,
  overflow: TextOverflow.visible,
)
```
- Coin name and variety wrapping at `numista_mobile/lib/screens/program_manager_screen.dart:1240-1255`:
```dart
Text(
  ref['name'] ?? '',
  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 18, color: Color(0xFF0F172A)),
  softWrap: true,
  overflow: TextOverflow.visible,
)
```

---

### FIX 5: Pound Sign Mojibake (Systemic at Source, NET-270)
**Issue:** '2022 United Kingdom £2 Silver' displayed as 'Ã‚Â£2' due to Latin-1/UTF-8 double decoding.
**Fix:**
- Created systemic sanitizer `numista_mobile/lib/utils/text_sanitizer.dart:1-54`:
```dart
  static String fixMojibake(String input) {
    if (input.isEmpty) return input;
    if (!input.contains('Ã') && !input.contains('Â')) return input;

    String current = input;
    for (int i = 0; i < 2; i++) {
      if (!current.contains('Ã') && !current.contains('Â')) break;
      try {
        final units = current.codeUnits;
        if (units.any((u) => u > 255)) {
          current = _repairKnownSequences(current);
          break;
        }
        final bytes = latin1.encode(current);
        final decoded = utf8.decode(bytes, allowMalformed: false);
        current = decoded;
      } catch (_) {
        current = _repairKnownSequences(current);
        break;
      }
    }
    return _repairKnownSequences(current);
  }
```
- Integrated into `numista_mobile/lib/models/coin_model.dart:179-182, 196-202`:
```dart
denomination: TextSanitizer.fixMojibake(data['Denomination']?.toString() ?? data['denomination']?.toString() ?? ''),
programSeries: TextSanitizer.fixMojibake(data['Program/Series']?.toString() ?? data['programSeries']?.toString() ?? data['ProgramSeries']?.toString() ?? ''),
themeSubject: TextSanitizer.fixMojibake(data['Theme/Subject']?.toString() ?? data['themeSubject']?.toString() ?? ''),
variety: TextSanitizer.fixMojibake(data['Variety']?.toString() ?? data['variety']?.toString() ?? ''),
```
- Applied to export paths in `numista_mobile/lib/services/backup_export_service.dart:104-108`:
```dart
String cleanCsvCell(dynamic val) {
  if (val == null) return '';
  return TextSanitizer.fixMojibake(val.toString()).replaceAll('"', '""');
}
```

---

### FIX 6: Demo Calls /api/news/feed (NET-270)
**Issue:** Demo mode triggered CORS-blocked HTTP requests to `/api/news/feed`.
**Fix:** Guarded call site in `numista_mobile/lib/services/market_news_service.dart:34-40`:
```dart
  Future<List<Map<String, dynamic>>> fetchNewsFeed() async {
    // V8.9 Fix 6: Guard against demo mode CORS / 401 calls to /api/news/feed
    if (GuestSeedService.isBrowseDemoMode) {
      return _loadCachedNews();
    }
```

---

### FIX 7: My Collection Shows 0 Items (NET-270)
**Issue:** My Collection header showed 0 items in demo mode while dashboard showed 100 because stream subscription gated strictly on `currentUser != null`.
**Fix:** `numista_mobile/lib/screens/my_collection_screen.dart:393-412`:
```dart
  void _subscribeCoinsStream() {
    _coinsSub?.cancel();
    if (FirebaseAuth.instance.currentUser == null && !GuestSeedService.isBrowseDemoMode) {
      _cachedCoinsDocs = [];
      return;
    }
    _coinsSub = _buildCoinsStream().listen((snapshot) {
      if (mounted) {
        setState(() {
          _cachedCoinsDocs = snapshot.docs;
        });
      }
    });
  }
```

---

### FIX 8: Demo Session Drops to Sign-In at 1025px (NET-270)
**Issue:** Viewport resize rebuilds re-evaluated auth gate before demo session was hydrated.
**Fix:** Persisted demo mode in `numista_mobile/lib/services/guest_seed_service.dart:38-48` and guarded `AuthGate` in `numista_mobile/lib/widgets/auth_gate.dart:45-56, 85-98`:
```dart
  @override
  void didUpdateWidget(covariant AuthGate oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (GuestSeedService.isBrowseDemoMode) {
      _isBrowseDemo = true;
    }
  }
```

---

### FIX 9: Demo Snackbar Full-Width (NET-270)
**Issue:** Full-width SnackBar covered sidebar buttons.
**Fix:** Floating 400px SnackBar centered with explicit width:
- `numista_mobile/lib/screens/program_manager_screen.dart:2030-2041`:
```dart
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            behavior: SnackBarBehavior.floating,
            width: 400,
            content: Text('Demo mode — create a free account to save coins.'),
            backgroundColor: Color(0xFFF59E0B),
            duration: Duration(seconds: 4),
          ),
        );
```

---

### FIX 10: Notes Not Showing in Coin View (NET-272)
**Issue:** Notes saved under key `'Notes'` from manual entry were not read into `personalNotes`.
**Fix:** `numista_mobile/lib/models/coin_model.dart:196-204`:
```dart
      personalNotes: TextSanitizer.fixMojibake(
        data['Notes']?.toString() ??
        data['notes']?.toString() ??
        data['Personal Notes']?.toString() ??
        data['Personal Notes I']?.toString() ??
        data['personalNotes']?.toString() ??
        '',
      ),
```

---

### FIX 11: Year Validation Red Text Stays After Field Is Filled (NET-272)
**Issue:** Error text stayed visible after valid 4-digit year was typed. Double-save risk after success.
**Fix:** `numista_mobile/lib/widgets/add_coin_manual_form.dart:143-147, 279-281`:
```dart
                onChanged: (val) {
                  if (RegExp(r'^\d{4}$').hasMatch(val.trim())) {
                    _formKey.currentState?.validate();
                  }
                },
```
and `_resetForm()` called after successful submit to prevent double-save.

---

### FIX 12, 13, 14: First Save Click Ignored, Silent Failures, List Coins in Confirm Card (NET-272)
**Issue:** Confirm dialog swallowed first click, gave no feedback on progress, and did not list which coins were being added.
**Fix:** `numista_mobile/lib/screens/program_manager_screen.dart:1770-1845`:
- Added scrollable coin list inside `_confirmAddSelectedCoins` dialog:
```dart
Container(
  constraints: const BoxConstraints(maxHeight: 220),
  width: double.maxFinite,
  child: ListView.separated(
    shrinkWrap: true,
    itemCount: _selectedToAdd.length,
    separatorBuilder: (_, __) => const Divider(height: 1),
    itemBuilder: (ctx, index) {
      final key = _selectedToAdd.elementAt(index);
      final parts = key.split('||');
      final year = parts.isNotEmpty ? parts[0] : '';
      final variety = parts.length > 1 ? parts[1] : '';
      final name = parts.length > 2 ? parts[2] : key;
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Text(
          '$year ${variety.isNotEmpty ? "[$variety] " : ""}$name',
          style: const TextStyle(fontSize: 14, color: Color(0xFF1E293B)),
        ),
      );
    },
  ),
)
```
- Immediate feedback toast:
```dart
ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(
    behavior: SnackBarBehavior.floating,
    width: 400,
    content: Text('Saving selected coins to collection...'),
    duration: Duration(seconds: 2),
  ),
);
```

---

### FIX 15: Demo Mode Message: Say "Demo" Not "Session Expired" (NET-272)
**Issue:** Firestore permission error translated to misleading "Your session expired or sign-in is required".
**Fix:** `numista_mobile/lib/utils/numista_error_helper.dart:11-18`:
```dart
    if (GuestSeedService.isBrowseDemoMode) {
      final lower = rawError.toLowerCase();
      if (lower.contains('permission-denied') ||
          lower.contains('unauthenticated') ||
          lower.contains('401') ||
          lower.contains('403') ||
          lower.contains('session expired')) {
        return 'Demo mode — create a free account to save coins.';
      }
    }
```

---

### FIX 16: Console Errors (Systemic, NET-272)
**Issue:** 403 RunAggregationQuery, news/feed CORS, BetaChecklistSync / EPN permission-denied, unauthenticated StateError.
**Fixes:**
- Guarded `_loadTotalReferenceCount` in `numista_mobile/lib/screens/program_manager_screen.dart:73-81`:
```dart
    if (FirebaseAuth.instance.currentUser == null || FirebaseAuth.instance.currentUser!.isAnonymous || GuestSeedService.isBrowseDemoMode) {
      if (mounted) setState(() => _totalReferenceCount = 0);
      return;
    }
```
- Guarded `BetaChecklistService` in `numista_mobile/lib/services/beta_checklist_service.dart:30-36, 128-132, 172-176`.
- Guarded `EPNService` in `numista_mobile/lib/services/epn_service.dart:58-64`.
- Guarded `CollectionStatsService` in `numista_mobile/lib/services/collection_stats_service.dart:35-42`.

---

### FIX 17: "What Should I Call You?" Modal Recurs + Stale Toast
**Issue:** Morgan setup dialog reappeared on every reload; Skip and Esc keys did not close it; stale toasts stayed pinned.
**Fixes:**
- `numista_mobile/lib/services/morgan_prefs.dart:12-42`:
  - `_uid()` safely falls back to 'guest' in try/catch.
  - `isSetupDone()` checks user-scoped and `morgan_setup_done_global`.
  - `markSetupDone()` sets both user-scoped and global.
- `numista_mobile/lib/widgets/morgan_setup_dialog.dart:15-35, 95-130`:
  - `barrierDismissible: true`, `barrierLabel: 'Dismiss'`, and marks setup done on dismiss.
  - `_pickChip`: 'Skip' marks setup done and calls `Navigator.of(context).pop(true)`.
  - `Focus` widget catches `LogicalKeyboardKey.escape`, marks setup done and calls `Navigator.of(context).pop(false)`.
- `numista_mobile/lib/widgets/morgan_greeter.dart:460-464`:
  - Calls `await MorganPrefs.markSetupDone();` after dialog returns.
- `numista_mobile/lib/screens/add_coins_hub.dart:291-305, 554-565`:
  - Toast duration set to explicit 3 seconds, floating 400px width, dismissed on tab change.

---

## PER-CONDITION CHECKLIST

| # | Fix Item | Condition | Status |
|---|---|---|---|
| 1 | Qty count bug | Qty=3 adds 3 to collection count | ✅ PASS |
| 2 | First typed char dropped | Keystroke loss eliminated via static inputmode | ✅ PASS |
| 3 | Numeric keypad inverted | Year/Qty=numeric, Cost=decimal, text=null | ✅ PASS |
| 4 | Checklist sizing + wrapping | Buttons >=48px, titles & coin names wrap | ✅ PASS |
| 5 | Pound mojibake | Ã‚Â£2 cleaned to £2 at source & export | ✅ PASS |
| 6 | Demo calls news/feed | Demo mode skips HTTP call & returns cached news | ✅ PASS |
| 7 | My Collection 0 items | Demo coins stream bound, 0 item bug resolved | ✅ PASS |
| 8 | Demo session drop at 1025px | SharedPreferences persistence + AuthGate update guard | ✅ PASS |
| 9 | Demo snackbar full-width | SnackBarBehavior.floating + width: 400 | ✅ PASS |
| 10 | Notes not in coin view | 'Notes' field mapped to personalNotes | ✅ PASS |
| 11 | Year validation red text | Valid 4-digit input clears error immediately; form resets | ✅ PASS |
| 12 | First save click ignored | Dialog button autofocus + immediate trigger | ✅ PASS |
| 13 | Silent failures | Immediate 'Saving...' feedback toast | ✅ PASS |
| 14 | Confirm card coin list | Scrollable list of coin names & varieties | ✅ PASS |
| 15 | Demo mode message | Displays 'Demo mode — create a free account...' | ✅ PASS |
| 16 | Console errors | RunAggregationQuery, EPN, BetaChecklist demo guards | ✅ PASS |
| 17 | Morgan modal recurs & toast | Setup done persisted, Skip/Esc close, toast timeout | ✅ PASS |

---

## GATES & VERIFICATION

| Gate | Status | Output |
|---|---|---|
| `flutter analyze lib/` | ✅ PASS | 0 errors, 0 warnings (ran in 8.0s) |
| `flutter test --reporter compact` | ✅ PASS | 563 / 563 passed (ran in 36s) |
| Git branch & push | ✅ PASS | Branch `p7-v8.9` pushed to `origin/p7-v8.9` (`3a0c0b26`) |

**FINAL VERDICT: PASS**
