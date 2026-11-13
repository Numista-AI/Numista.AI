# EXECUTE_DONE: P7 V8.10 Build

**Date:** 2026-10-16 15:10 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `747f7051b1af7675a75d6c5728337c89f20f75e0`  
**Git Push Target:** `origin/p7-v8.9`  
**Flutter Analyze:** 0 errors, 0 warnings (`No issues found! (ran in 4.0s)`)  
**Flutter Test:** 566/566 passed (+3 new tests over baseline 563)  

---

## 1. Summary of Changes & Fixes

| Item | Problem Description | File & Line Cites | Status |
|---|---|---|---|
| 1 | Static `inputmode` on DOM inputs (`numeric` for Year/Qty, `decimal` for Cost) | `numista_mobile/lib/utils/web_input_helper_web.dart:12-19`<br>`numista_mobile/web/index.html:158-162`<br>`numista_mobile/lib/widgets/add_coin_manual_form.dart:98-100` | Fixed & Verified |
| 2 | Checklist Print & Download PDF buttons height >= 48px | `numista_mobile/lib/screens/program_manager_screen.dart:936-963`<br>`numista_mobile/lib/screens/program_manager_screen.dart:1669` | Fixed & Verified |
| 3 | Mint chips wrap text without ellipsis or cutoff at 1025/1280px | `numista_mobile/lib/screens/program_manager_screen.dart:1541-1555`<br>`numista_mobile/lib/screens/program_manager_screen.dart:1630-1640` | Fixed & Verified |
| 4 | Pound sign mojibake (`Â£`) resolved at source and in PDF/exports | `numista_mobile/lib/screens/coin_detail_screen.dart:69, 1004-1012`<br>`numista_mobile/lib/services/checklist_generator_service.dart:31-32` | Fixed & Verified |
| 5 | My Collection "All" Tab crash on demo/unauthenticated mode | `numista_mobile/lib/screens/my_collection_screen.dart:1391-1412` | Fixed & Verified |
| 6 | Demo mode session persists across resize breakpoints and reloads | `numista_mobile/lib/widgets/auth_gate.dart:61, 77-84`<br>`numista_mobile/lib/main.dart:227-233` | Fixed & Verified |
| 7 | Floating SnackBars positioned bottom-right with margin | `numista_mobile/lib/screens/program_manager_screen.dart:1952-1955`<br>`numista_mobile/lib/screens/add_coins_hub.dart:558-561` | Fixed & Verified |
| 8 | First-character dropped root cause: persistent dedicated `FocusNode`s | `numista_mobile/lib/widgets/add_coin_manual_form.dart:84-96, 419-421` | Fixed & Verified |
| 9 | Notes & Quantity rendered in coin detail views | `numista_mobile/lib/screens/coin_detail_screen.dart:1527-1528`<br>`numista_mobile/lib/screens/my_collection_screen.dart:3968, 3988` | Fixed & Verified |
| 10| 2026 Semiquincentennial slot matching isolated with discrete tokens | `numista_mobile/lib/utils/slot_resolver.dart:393-398, 412-414` | Fixed & Verified |
| 11| Form validation errors clear dynamically on keystroke & reset cleanly | `numista_mobile/lib/widgets/add_coin_manual_form.dart:178-182, 325` | Fixed & Verified |
| 12| Google Fonts Material Icons stylesheet linked in `index.html` | `numista_mobile/web/index.html:73` | Fixed & Verified |
| 13| Single source of truth count audit (Grokbot 311 vs 312 resolved) | Verified in `test/p7_v8_ux_safety_test.dart:1367-1372` | Audited: 312 |
| 14| Console 403 / permission-denied errors guarded in demo mode | `numista_mobile/lib/services/beta_checklist_service.dart:181-182, 346` | Fixed & Verified |
| 15| Morgan setup dialog close button ('X') and global flag persistence | `numista_mobile/lib/widgets/morgan_setup_dialog.dart:182-192`<br>`numista_mobile/lib/services/morgan_prefs.dart:39-40` | Fixed & Verified |

---

## 2. Grokbot Coin Count Mystery Reconciled
- Querying Firestore `users/grokbot@numista.ai/coins` directly:
  - Total documents: **314**
  - Set parent docs (`isPhysicalCoin == false`): **3** (`2026_clad_proof_set_parent`, `2026_silver_proof_set_parent`, `2026_uncirculated_coin_set_parent`)
  - Physical coin docs: **311**
  - Physical coins with `Quantity: 1`: **310**
  - Physical coins with `Quantity: 2`: **1** (`Hmq76a3zTbPlMMTZwHr2`, "2026 Morgan and Peace Silver Dollars Dollar", Denomination: Dollar, Year: 2026)
  - Calculation: `(310 * 1) + (1 * 2) = 312` physical coins.
- **Conclusion:** There are zero test coins. 312 is the true physical coin count. Both the dashboard header and Ask Morgan card use `totalCoins = expansion.totalCoins = 312`.

---

## 3. Verification Commands Run
1. `flutter analyze lib/` -> 0 issues
2. `flutter test --reporter compact` -> 566/566 passed (0 failures)
3. `git push origin p7-v8.9` -> Pushed to `https://github.com/Numista-AI/Numista.AI.git` commit `747f7051`.
