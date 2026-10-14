# EXECUTE_DONE P7 ADD-COINS FLOW V6
Date: 2026-10-14 ~18:38 ET
Agent: AG CoS (Antigravity / Gemini 3.8)
Commit: ae2b87bd on dev

## V6 Fixes — All 4 Fix Areas Applied & Verified

### FIX 1 — B1 DATA INTEGRITY: Add-another opens plain confirm card, not cert screen
- **Button navigation**: `numista_mobile/lib/screens/program_manager_screen.dart:1323–1338`
  - "+ Add another copy" navigates to `AddCoinsHub(showAddAnotherConfirm: true, initialCoinPreset: {name, year, mint})`.
- **AddCoinsHub route & flag**: `numista_mobile/lib/screens/add_coins_hub.dart:39, 55, 580–587`
  - Constructor takes `final bool showAddAnotherConfirm;` (default `false`).
  - `build()` intercepts `showAddAnotherConfirm` before cert fullscreen and displays clean `_buildAddAnotherConfirmCard()`.
- **Gated initState**: `numista_mobile/lib/screens/add_coins_hub.dart:139–159`
  - `_certPendingConfirm` preset logic only fires when `!widget.showAddAnotherConfirm` and `certNo.isNotEmpty`.
- **Plain confirm card**: `numista_mobile/lib/screens/add_coins_hub.dart:341–513`
  - Displays coin name (22px bold dark `Color(0xFF1E293B)`), year (18px), and mint mark prominently (18px).
  - Primary 56px `Save to My Collection` button (`Color(0xFF2563EB)`).
  - Secondary text button `Has a slab cert # instead` (`Color(0xFF2563EB)`) to switch to cert flow if needed.
- **Clean collection save**: `numista_mobile/lib/screens/add_coins_hub.dart:515–573`
  - `_saveAddAnotherCoin()` writes directly to `AuthService.coinsPath` with `source: 'manual'`, `Condition: 'Ungraded'`, and zero grader/cert metadata.
- **Empty cert guards**: `numista_mobile/lib/screens/add_coins_hub.dart:2992–2998, 3269–3274`
  - Both `_lookupCertUnified()` and `_saveManualCertEntry()` verify `certNo.trim().isNotEmpty`. If empty, shows warning SnackBar `'Enter a cert # before saving'` with `Color(0xFFD97706)` and immediately aborts.
  - Belt-and-suspenders verify link check: only constructs `verifyLink` if `certNo.trim().isNotEmpty` (`3277–3298`) and conditionally adds `'verify_link': verifyLink` (`3300`).

### FIX 2 — B3: 18px text, 16px+ chips, PCGS token section excised from cert lookup
- **Header subtitle**: `numista_mobile/lib/screens/add_coins_hub.dart:2656–2657`
  - Replaced `'Auto-detects grader...'` with `'Type the number on the slab label'` at 18px `Color(0xFF334155)`.
- **Filter chips**: `numista_mobile/lib/screens/add_coins_hub.dart:2684–2690`
  - Grader FilterChip labels upgraded from 14px to 16px.
- **Grader helper text**: `numista_mobile/lib/screens/add_coins_hub.dart:2718–2719`
  - Upgraded to 18px `Color(0xFF334155)`.
- **Detected cert result card**: `numista_mobile/lib/screens/add_coins_hub.dart:2798–2817`
  - Detected cert label upgraded to 18px `Color(0xFF065F46)`.
  - Subtext upgraded to 18px `Color(0xFF065F46)`.
  - 'Yes, look it up' button text upgraded to 18px bold.
- **Look Up button**: `numista_mobile/lib/screens/add_coins_hub.dart:2854–2856`
  - Look Up button label upgraded to 18px.
- **Excised PCGS advanced options**: `numista_mobile/lib/screens/add_coins_hub.dart:2884`
  - Removed "Advanced Options (PCGS Token & Bulk Import)" ExpansionTile block from the cert lookup view.
- **Manual entry instruction**: `numista_mobile/lib/screens/add_coins_hub.dart:3083–3088`
  - Upgraded from 14px to 18px `Color(0xFF1E3A8A)`.
- **Manual entry footer note**: `numista_mobile/lib/screens/add_coins_hub.dart:3192–3197`
  - Upgraded from 13px grey to 18px `Color(0xFF334155)`.

### FIX 3 — Verify button labels
- **Grader verify button**: `numista_mobile/lib/screens/add_coins_hub.dart:3112–3118`
  - Clean switch statement:
    - NGC: `'Check this slab on ngccoin.com'`
    - CAC: `'Check this slab on cacgrading.com'`
    - Default (PCGS): `'Check this slab on pcgs.com'`

### FIX 4 — Widget tests (7/7 in p7_v5 suite)
- **File**: `numista_mobile/test/p7_v5_ux_fixes_test.dart`
  - Test A (`blocker1AddAnotherPlainConfirm`, lines 165–182): verifies add-another on raw slot shows plain confirm card, displays coin name & AppBar 'Add another copy', no TabBar/cert screen, and contains 56px 'Save to My Collection' button.
  - Test B (`blocker1EmptyCertRefused`, lines 184–199): verifies empty cert lookup shows SnackBar 'Enter a cert # before saving' and refuses manual card generation.
  - All 5 previous tests pass with no regressions.

## Verification & Test Results
- `flutter analyze lib/`: **0 errors, 0 warnings** (No issues found!)
- `flutter test test/p7_v5_ux_fixes_test.dart test/cert_flow_test.dart`: **13/13 PASS**
- `flutter test --reporter compact`: **507/507 PASS**
- Git rebase & push: cleanly pushed `ae2b87bd` to `origin/dev`
