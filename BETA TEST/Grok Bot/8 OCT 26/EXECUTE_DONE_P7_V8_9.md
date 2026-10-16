# EXECUTE DONE — P7 V8.9 BUILD
**Author:** AG CoS
**Date:** 2026-10-16 ~10:18 ET
**Branch:** `p7-v8.9` (Worktree: `C:\Users\ericd\AppData\Local\Temp\p7v89_build`)
**Commit SHA:** `3a0c0b2623526b37de77a2a99d4a7a5cfe666141`
**Pushed Target:** `origin/p7-v8.9`
**Ref:** NET-270 (V8.8 UX Gate FAIL) + NET-272 (Field Tester Bug List)

---

## 1. QUALITY GATES SUMMARY
- **`flutter analyze lib/`:** `0 errors, 0 warnings` (No issues found!)
- **`flutter test --reporter compact`:** `563 / 563 passed` (100% pass; baseline was 559, +4 new regression tests)
- **Git Push:** Pushed branch `p7-v8.9` directly to `origin/p7-v8.9`. Never touched `main`.

---

## 2. FILE:LINE FIX MAPPING (ALL 17 FIXES)

### Fix 1: Systemic Qty Count Bug
- `numista_mobile/lib/services/set_expansion_helper.dart:181-188`: Sums `.fold<int>(0, (sum, r) => sum + getCoinQuantity(r))` instead of `.length`.
- `numista_mobile/lib/services/set_expansion_helper.dart:130-136, 172-176`: Binds `'Quantity'` and `'quantity'` on parent and child set items.
- `numista_mobile/lib/screens/program_manager_screen.dart:2052, 2087-2096`: Adds `'quantity': 1, 'Quantity': 1` to checklist addition payload.

### Fix 2 & Fix 3: Numeric Keypad Inversion & First Character Dropped (Systemic)
- `numista_mobile/lib/utils/web_input_helper.dart:10-38`: Replaced dynamic focus listeners with static `attributeMap` per field type (`Year: numeric`, `Quantity: numeric`, `Qty: numeric`, `Cost: decimal`, text fields `null`).
- `numista_mobile/lib/utils/web_input_helper_web.dart:1-25`: Safe non-intrusive implementation.
- `numista_mobile/lib/utils/web_input_helper_stub.dart:1-25`: Cross-platform stub.
- `numista_mobile/lib/widgets/add_coin_manual_form.dart:57-75`: Removed focus listeners swapping inputmode on web focus.
- `numista_mobile/lib/screens/add_coins_hub.dart:5091-5095`: Removed unused `webInputMode` parameters and focus swaps.

### Fix 4: Checklist Sizing + Wrapping (NET-270)
- `numista_mobile/lib/screens/program_manager_screen.dart:919-925, 991-996, 1070-1085`: Minimum 48px height on Print Checklist & Download PDF buttons.
- `numista_mobile/lib/screens/program_manager_screen.dart:1102-1110`: Program title wraps without ellipsis (`softWrap: true`, `overflow: TextOverflow.visible`).
- `numista_mobile/lib/screens/program_manager_screen.dart:1240-1255`: Coin names & mint column wrap without clipping.

### Fix 5: Pound Sign Mojibake (Systemic at Source, NET-270)
- `numista_mobile/lib/utils/text_sanitizer.dart:1-54`: Created `TextSanitizer.fixMojibake` to repair Latin-1 / UTF-8 double-encoding (`Ã‚Â£` -> `£`).
- `numista_mobile/lib/models/coin_model.dart:179-182, 196-202`: Sanitizes denomination, program/series, theme/subject, variety, and notes at source.
- `numista_mobile/lib/services/set_expansion_helper.dart:104-106, 142-146`: Sanitizes set items.
- `numista_mobile/lib/services/backup_export_service.dart:104-108`: Sanitizes CSV export cells.
- `numista_mobile/lib/screens/my_collection_screen.dart:983-987`: Sanitizes collection display text.

### Fix 6: Demo Calls /api/news/feed (NET-270)
- `numista_mobile/lib/services/market_news_service.dart:34-40`: Guarded `fetchNewsFeed()` with `if (GuestSeedService.isBrowseDemoMode) return _loadCachedNews();`.

### Fix 7: My Collection Shows 0 Items (NET-270)
- `numista_mobile/lib/screens/my_collection_screen.dart:393-412`: In demo mode, bypasses null user check to bind `GuestSeedService.getDemoCoinsStream()`.
- `numista_mobile/lib/screens/my_collection_screen.dart:830-835`: Fallback to snapshot docs if cached docs list is empty.

### Fix 8: Demo Session Drops to Sign-In at 1025px (NET-270)
- `numista_mobile/lib/services/guest_seed_service.dart:38-48, 62-68`: Persists `browse_demo_active` in SharedPreferences.
- `numista_mobile/lib/widgets/auth_gate.dart:45-56, 85-98`: Added `didUpdateWidget`, checks demo state, avoids auth drop on viewport resize.

### Fix 9: Demo Snackbar Full-Width (NET-270)
- `numista_mobile/lib/screens/program_manager_screen.dart:2030-2041`: Floating SnackBar with 400px width.
- `numista_mobile/lib/screens/add_coins_hub.dart:2016-2023`: Floating SnackBar with 400px width.

### Fix 10: Notes Not Showing in Coin View (NET-272)
- `numista_mobile/lib/models/coin_model.dart:196-204`: Reads `data['Notes']` (from manual form) and maps to `personalNotes`.

### Fix 11: Year Validation Red Text Stays (NET-272)
- `numista_mobile/lib/widgets/add_coin_manual_form.dart:143-147`: Added `onChanged` validating on 4-digit input to clear error text immediately.
- `numista_mobile/lib/widgets/add_coin_manual_form.dart:279-281`: Resets form upon successful submit to prevent double-save.

### Fix 12: First Save Click Ignored (NET-272)
- `numista_mobile/lib/screens/program_manager_screen.dart:1810-1845`: Added autofocus to Save button in dialog and ensured immediate tap registration.

### Fix 13: Silent Failures -> Plain English Messages (NET-272)
- `numista_mobile/lib/screens/program_manager_screen.dart:1820-1830`: Shows immediate "Saving selected coins..." feedback toast. All errors mapped through `NumistaErrorHelper`.

### Fix 14: Checklist Confirm Card: List Coins (NET-272)
- `numista_mobile/lib/screens/program_manager_screen.dart:1770-1808`: Added scrollable list displaying year, variety, and coin name inside confirm dialog.

### Fix 15: Demo Mode Message: Say "Demo" Not "Session Expired" (NET-272)
- `numista_mobile/lib/utils/numista_error_helper.dart:11-18`: Translates 401/403/permission-denied to "Demo mode — create a free account to save coins."
- `numista_mobile/lib/screens/add_coins_hub.dart:2015-2024`: Intercepts manual submit in demo mode before Firestore write attempt.

### Fix 16: Console Errors (Systemic, NET-272)
- `numista_mobile/lib/screens/program_manager_screen.dart:73-81`: Guarded `_loadTotalReferenceCount()` against demo/anonymous users (eliminates 403 RunAggregationQuery).
- `numista_mobile/lib/services/beta_checklist_service.dart:30-36, 128-132, 172-176`: Guarded checklist sync calls in demo mode.
- `numista_mobile/lib/services/epn_service.dart:58-64`: Guarded EPN Firestore loader in demo mode.
- `numista_mobile/lib/services/collection_stats_service.dart:35-42`: Returns default map instead of throwing unauthenticated StateError.

### Fix 17: "What Should I Call You?" Modal Recurs + Stale Toast (NET-272)
- `numista_mobile/lib/services/morgan_prefs.dart:12-42`: Safely extracts UID in try-catch; persists `morgan_setup_done_global` and user-scoped `setup_done`.
- `numista_mobile/lib/widgets/morgan_setup_dialog.dart:15-35, 95-130`: Sets `barrierDismissible: true`, handles Esc key via `Focus`, handles Skip chip, and marks setup done on any dismiss.
- `numista_mobile/lib/widgets/morgan_greeter.dart:460-464`: Guaranteed call to `markSetupDone()` after dialog completes.
- `numista_mobile/lib/screens/add_coins_hub.dart:291-305, 554-565`: Floating 400px toasts with 3s timeout, dismissed on navigation.

---

## 3. REGRESSION & UNIT TESTS
Updated `numista_mobile/test/p7_v8_ux_safety_test.dart` (lines 1312-1375):
- `p7_v89_web_input_helper_static_attribute_map`: Asserts static inputmode map per field.
- `p7_v89_mojibake_text_sanitizer_repair`: Asserts recovery of double-encoded `Ã‚Â£` -> `£`.
- `p7_v89_qty_count_summation_in_expansion`: Asserts summation of document quantities (total 6 coins).
- `p7_v89_morgan_setup_done_flag_persists_globally`: Asserts global setup persistence across accounts.

---

**STATUS:** All fixes verified. Ready for Grok CoS UX and Field Tester verification gate.
