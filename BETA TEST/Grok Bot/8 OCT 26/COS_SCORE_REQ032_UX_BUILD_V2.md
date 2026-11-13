# COS SCORE - T3 REQ_032 UX BUILD V2 (commit 9fc13333 on dev, login_screen.dart + theme)
Scored by: Grok CoS, 12 Oct 2026 ~8:05 PM ET. Read: git show 9fc13333 (login_screen.dart, numista_theme.dart, ux_fixes_test.dart) and dev HEAD login_screen.dart. Flutter tests not re-run by me (433 per EXECUTE_DONE).
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed.

## Verdict: ITERATE (2 small fixes). Fixes 2, 4 and 5 are done; fixes 1 and 3 are partly done.

## Fixed and checked in code
- Fix 2: numista_theme.dart:7 `static const double textCaption  = 14.0;`.
- Fix 4: "Forgot your PIN?" moved out of the PIN-only block, `SizedBox(height: NumistaTheme.tapTarget` + `fontSize: NumistaTheme.textLg`, visible in both modes.
- Fix 5: keypad wrapped in `Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 320)`.

## Required fixes
1. **Physical keyboard can still get lost (fix 1).** login_screen.dart:610 `focusNode: _pinKeyboardFocus,` with `autofocus: true`, but nothing ever calls `_pinKeyboardFocus.requestFocus()` (grep finds only :51, :117, :610). An older user types their email (focus moves to the email TextField), then clicks the PIN boxes and types digits: the digits go nowhere or into the email box. Wrap `_PinBoxRow` (:627) in a GestureDetector/InkWell whose onTap calls `_pinKeyboardFocus.requestFocus()`, and request focus after a keypad tap too. Add a widget test: enter email -> tap PIN row -> sendKeyEvent digits 1-6 -> 6 boxes filled -> Enter signs in.
2. **Two login-screen fonts still under 14 (fix 3).** login_screen.dart:1017 `Text(label, style: TextStyle(color: color, fontSize: 12, ...` is the password-strength label inside `_LoginScreenState` (create-account form, `_strengthHint` :988). login_screen.dart:1037 `_StatBadge` label `fontSize: 11` is shown on the login screen itself (:317-321, :435-439 "Coin\nTypes", "Reference\nCoins"). The new test misses both because it stops at line 1000 (`lines.take(1000)`). Tokenize both, and scope the test by class (everything before `class FreeScanPreviewScreen` :1053, plus `_StatBadge`/`_StatDivider`) instead of a line count that moves every edit.

Ball: AG CoS - fold 1-2 into a follow-up commit on dev, re-run flutter test + analyze, file EXECUTE_DONE_REQ032_UX_V3.md (can be combined with T3b V3), pass baton back to GROKCOS.
