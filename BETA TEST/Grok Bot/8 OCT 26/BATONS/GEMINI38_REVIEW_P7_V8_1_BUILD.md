# GEMINI38_REVIEW P7 V8.1 BUILD (COMPREHENSIVE)

Reviewer: Antigravity (Gemini 3.8) | 2026-10-15 ~11:53 ET
Commits: **667e0063** (7 files) + **b3fb9cc6** (20 files) on `origin/dev`
Scope: Systemic plain-English error sweep — Item 5 completion from COS_SCORE_P7_ADD-COINS-FLOW_V8.md

---

> [!NOTE] This corrects the premature partial review filed with 667e0063 only. Both commits together constitute V8.1. All ~50 user-visible raw-exception sites replaced. 0 remaining.

---

## Files Fixed — Verbatim Before/After

### Commit 667e0063 (7 files)

#### 1. `numista_mobile/lib/inventory_gallery.dart:45`
**Before:** `content: Text('Sync error: $e',`
**After:** `content: Text(NumistaErrorHelper.toUserFriendly(e),`
Import `utils/numista_error_helper.dart` added at line 4. ✅

#### 2. `numista_mobile/lib/screens/admin_grade_flags_screen.dart:368`
**Before:** `content: Text('Error: $e'),`
**After:** `content: Text(NumistaErrorHelper.toUserFriendly(e)),`
Import `../utils/numista_error_helper.dart` added at line 6. ✅

#### 3. `numista_mobile/lib/screens/base_layout.dart:188`
**Before:** `SnackBar(content: Text('Error opening coin: $e')),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e))),`
Import `../utils/numista_error_helper.dart` added at line 49. ✅

#### 4. `numista_mobile/lib/screens/coa_inspector_screen.dart:60`
**Before:** `SnackBar(content: Text('COA Inspection Error: ${e.toString()}'), backgroundColor: Colors.red),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e)), backgroundColor: Colors.red),`
Import `../utils/numista_error_helper.dart` added at line 7. ✅

#### 5. `numista_mobile/lib/screens/add_coins_hub.dart:4581`
**Before:** `_camError = 'Save failed with error: $e';`
**After:** `_camError = NumistaErrorHelper.toUserFriendly(e);`
Import already present from V8. ✅

#### 6. `numista_mobile/lib/widgets/morgan_guides.dart:271`
**Before:** `hint: "I'll save all selected coins directly to your Firestore collection tracker.",`
**After:** `hint: "I'll save all selected coins to your collection.",`
Removes "Firestore collection tracker" jargon as required by V8.1/NET-174. ✅

#### 7. `numista_mobile/lib/main.dart:16` + `:208`
Import restored:
```dart
import 'utils/numista_error_helper.dart';
```
Used at main.dart:208:
```dart
Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'The app could not start. Please reload the page or contact support@numista.ai.'),
```
✅

---

### Commit b3fb9cc6 (20 files)

#### 8. `numista_mobile/lib/screens/coin_detail_screen.dart` — 7 hits
**Before (e.g. line 507):** `SnackBar(content: Text('Save failed: $e'), backgroundColor: _kRed),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Save failed. Please try again.')), backgroundColor: _kRed),`
All 7 hits across lines ~507, ~656, ~693, ~1233, ~1963, ~2007, ~2133. Import added. ✅

#### 9. `numista_mobile/lib/screens/my_collection_screen.dart` — 8 hits
**Before (e.g. line 482):** `_coinsError = 'Error loading coins: $e';`
**After:** `_coinsError = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load your collection. Please try again.');`
All 8 hits across lines ~482, ~490, ~2827, ~4120, ~4314, ~5035, ~5511, ~6058. Import added. ✅
Note: `my_collection_screen.dart:5327` `setName.toString()` — LEFT UNCHANGED (data display, not an error). ✅

#### 10. `numista_mobile/lib/screens/lateral_transfer_screen.dart` — 7 hits
**Before (e.g. line 168):** `_fetchError = 'Error: $e';`
**After:** `_fetchError = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load inventory items. Please try again.');`
All 7 hits across lines ~168, ~255, ~311, ~1062, ~1149, ~1238, ~1290. Import added. ✅

#### 11. `numista_mobile/lib/screens/estate_planning_screen.dart` — 4 hits
**Before (e.g. line 582):** `SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'An error occurred. Please try again.')), backgroundColor: Colors.red),`
Lines ~582, ~1304, ~1791, ~2202. Import added. ✅

#### 12. `numista_mobile/lib/screens/settings_screen.dart` — 4 hits
**Before (e.g. line 228):** `content: Text('Export failed: $e'),`
**After:** `content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Export failed. Please try again.')),`
Lines ~228, ~567, ~1675, ~2620. Import added. ✅
Note: `settings_screen.dart:1806` `.map((e) => e.toString())` — LEFT UNCHANGED (data transform, not user-visible). ✅
Note: `settings_screen.dart:1963` `.map((e) => e.toString())` — LEFT UNCHANGED (data transform, not user-visible). ✅

#### 13. `numista_mobile/lib/screens/human_ai_trainer_screen.dart` — 4 hits
**Before (e.g. line 376):** `_error = 'Error: $e';`
**After:** `_error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load items. Please try again.');`
Lines ~376, ~528, ~1313, ~1587. Import added. ✅

#### 14. `numista_mobile/lib/screens/my_tickets_screen.dart` — 3 hits
**Before (e.g. line 47):** `_error = 'Failed to load tickets: $e';`
**After:** `_error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load tickets. Please try again.');`
Lines ~47, ~85, ~125. Import added. ✅

#### 15. `numista_mobile/lib/screens/support_portal_screen.dart` — 4 hits
**Before (e.g. line 54):** `_queueError = 'Error: $e';`
**After:** `_queueError = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load support queue. Please try again.');`
Lines ~54, ~66, ~89, ~108. Import added. ✅

#### 16. `numista_mobile/lib/screens/transfer_inbox_screen.dart` — 1 hit
**Before (line ~63):** `SnackBar(content: Text('Claim failed: $e'), backgroundColor: Colors.red),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Claim failed. Please try again.')), backgroundColor: Colors.red),`
Import added. ✅

#### 17. `numista_mobile/lib/screens/wishlist_screen.dart` — 1 hit
**Before (line ~201):** `SnackBar(content: Text('Error sharing: $e')),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not share wish list. Please try again.'))),`
Import added. ✅

#### 18. `numista_mobile/lib/screens/public_wishlist_view_screen.dart` — 1 hit
**Before (line ~58):** `_error = 'Error: $e';`
**After:** `_error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load wish list. Please try again.');`
Import added. ✅

#### 19. `numista_mobile/lib/screens/coin_search_screen.dart` — 1 hit
**Before (line ~1041):** `SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not add to wish list. Please try again.')), backgroundColor: Colors.red),`
Import added. ✅

#### 20. `numista_mobile/lib/screens/deals_screen.dart` — 1 hit
**Before (line ~92):** `_error = 'Error: $e';`
**After:** `_error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load deals. Please try again.');`
Import added. ✅

#### 21. `numista_mobile/lib/screens/family_settings_screen.dart` — 1 hit
**Before (line ~67):** `SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),`
**After:** `SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'An error occurred. Please try again.')), backgroundColor: Colors.red),`
Import added. ✅

#### 22. `numista_mobile/lib/screens/login_screen.dart` — 1 hit
**Before (line ~1105):** `setState(() => _error = 'Error: $e');`
**After:** `setState(() => _error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not pick image. Please try again.'));`
Import added. ✅
Note: `login_screen.dart:1176-1177` `e.toString().toLowerCase()` — LEFT UNCHANGED (logic check, not displayed). ✅

#### 23. `numista_mobile/lib/screens/program_manager_screen.dart` — 3 hits (incl. jargon fix)
**Before (line ~1621):** `content: Text('Error generating PDF: $e'),`
**After:** `content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Failed to generate PDF checklist. Please try again.')),`
Also `program_manager_screen.dart:1938` + `:1947` (response body errors). Import already present. ✅

#### 24. `numista_mobile/lib/screens/review_hub_screen.dart` — 10 hits
**Before (e.g. line 131):** `content: Text('Error committing items: $e'),`
**After:** `content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Error committing items. Please try again.')),`
Lines ~131, ~200, ~267, ~409, ~454, ~565, ~628, ~997, ~1076, ~1412. Import added. ✅

#### 25. `numista_mobile/lib/screens/attorney_portal_screen.dart` — 1 hit
**Before (line ~162):** `_error = 'Failed to load report: $e';`
**After:** `_error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load the estate report. Please try again.');`
Import added. ✅

#### 26. `numista_mobile/lib/widgets/coin_set_viewer.dart` — 1 hit
**Before (line ~149):** `_error = e.toString();`
**After:** `setState(() { _error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load coin set. Please try again.'); _loading = false; });`
Import added. ✅

#### 27. `numista_mobile/lib/widgets/grade_badge_widget.dart` — 1 hit
**Before (line ~216):** `_error = 'Failed to connect to server: $e';`
**After:** `_error = NumistaErrorHelper.toUserFriendly(e, fallback: 'Could not load grade badge. Please try again.');`
Import added. ✅

---

## Intentional Exclusions (NOT user-visible — confirmed)
- `batch_valuation_service.dart:324` — `'ai_value_error': e.toString()` (Firestore field key, internal data storage)
- `login_screen.dart:1176-1177` — `e.toString().toLowerCase()` (logic comparison, not displayed)
- `my_collection_screen.dart:5327` — `setName.toString()` (data display, not an error)
- `settings_screen.dart:1806, :1963` — `.map((e) => e.toString())` (data transform, not user-visible)
- All `debugPrint(...)` and `print(...)` calls

---

## Systemic Coverage Verification

PowerShell grep result (0 remaining user-visible hits):
```powershell
Get-ChildItem numista_mobile\lib -Recurse -Filter "*.dart" | Select-String -Pattern '\$e[^a-zA-Z_]|\$\{e\}|e\.toString\(\)' | Where-Object { $_.Line -match "SnackBar|showSnackBar|Text\(|_error\s*=|_feedback\s*=|errorText|subtitle:" }
```
**Result: 1 line returned — `my_collection_screen.dart:5327 setName.toString()` — confirmed data display, not an error. 0 actual error sites remaining.** ✅

---

## Test Results
- `flutter analyze lib/` → **No issues found! (ran in 21.3s)** ✅
- `flutter test --reporter compact` → **518/518 All tests passed!** ✅
- `pytest numista_backend/tests/ -q` → **566 passed in 44.06s** ✅

---

## Commits
- `667e0063` — 7 files (inventory_gallery, admin_grade_flags, base_layout, coa_inspector, add_coins_hub, morgan_guides, main.dart)
- `b3fb9cc6` — 20 files (coin_detail, my_collection, lateral_transfer, estate_planning, settings, human_ai_trainer, my_tickets, support_portal, transfer_inbox, wishlist, public_wishlist_view, coin_search, deals, family_settings, login, program_manager, review_hub, attorney_portal, coin_set_viewer, grade_badge_widget)

---

## Verdict: PASS (V8.1 systemic plain-English complete)
All user-visible raw exception strings replaced across 27 files in `numista_mobile/lib`. No new issues introduced. flutter analyze 0 / flutter test 518 / pytest 566. Ready for Grok CoS score.
