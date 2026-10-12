# EXECUTE_DONE — REQ_032 UX V2 (T3) + REQ_032B Alt Site V2 (T3b)
Filed by: Antigravity CoS  
Date: 2026-10-12 ~7:48 PM ET  
Commit: `9fc13333` on `dev` (combined T3 + T3b V2 commit)

## T3 — UX V2 Result: DONE — All 5 ITERATE fixes applied

| Fix | Description | File:Line |
|---|---|---|
| Fix 1 | `KeyboardListener` (non-deprecated) wraps PIN box + keypad; handles digits, backspace, Enter | login_screen.dart:~607-660; FocusNode at :50, dispose at :119 |
| Fix 2 | `textCaption` raised from 12.0 → 14.0 in theme tokens; test assertion updated to 14.0 with floor assertion | numista_theme.dart:7; ux_fixes_test.dart:65-67 |
| Fix 3 | All hard-coded font sizes below 14 in login form (lines 1-1000) tokenized: `_label`, `_divider`, `_banner`, footer dots, footer links, subtitle tag, create tab toggle, terms/privacy RichText | login_screen.dart:multiple lines |
| Fix 4 | Forgot PIN: `textLg` (18) + `SizedBox(height:tapTarget)` + moved outside PIN-only block (visible in both modes) | login_screen.dart:~627-645 |
| Fix 5 | `_NumKeypad` wrapped in `Center(child: ConstrainedBox(maxWidth:320))` | login_screen.dart:~619-630 |

## T3b — Alt Site V2 Result: DONE — All 6 ITERATE fixes applied

| Fix | Description | File:Line |
|---|---|---|
| Fix 1+2 | Firestore owner wildcard narrowed: `{document=**}` → separate `{sub}/{docId}` rules with exclusion list for protected subcollections | numista_backend/firestore.rules:37-75; numista_mobile/firestore.rules:98-140 |
| Fix 3 | Firestore emulator rules tests added: 7 new test cases — deny write to settings/estate_reports/morgan_action_log/trash/audit_log; allow owner read; allow owner coins write | firestore.rules.test.js:232-300 |
| Fix 4 | `UiVariantService.refresh()` resets to `classic` on non-200 response (not just exceptions) | ui_variant_service.dart:17-24 |
| Fix 5 | `_AltSiteBanner` uses `textBodySm` (14) explicitly instead of `textCaption` | base_layout.dart:1337 |
| Fix 6 | EXECUTE_DONE doc corrected: `Eric + AJ` → actual emails; `main.py:247` → `main.py:225` | EXECUTE_DONE_REQ032B_ALT_SITE.md |

## Counts
- Pytest: **474 passed, 0 failed**
- Flutter test: **433 passed, 0 failed** (+1 new login_screen font test vs V1 432)
- flutter analyze: **No issues found**

## What's next
Grok CoS scores T2, T3, and T3b V2 builds.
