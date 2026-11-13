# COS SCORE - T3 REQ_032 UX BUILD (commit ecd0f9bb on dev)
Scored by: Grok CoS, 12 Oct 2026 ~5:40 PM ET. Read: git show ecd0f9bb (5 files, +731/-145), full login_screen.dart and base_layout.dart at that commit. Ran flutter test + analyze myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed.

## Verdict: ITERATE (5 required fixes - the sign-in screen, the first thing an older user sees, still misses the plan's size floor and lost keyboard entry)

## Tests (run by Grok CoS on EDS_Laptop)
`flutter test --reporter compact`: 427 passed ("All tests passed!"). `flutter analyze lib/`: "No issues found!". Matches EXECUTE_DONE.

## What is good (checked in code)
- Theme token file exists (numista_theme.dart) and base_layout.dart has no hard-coded fontSize under 14 left.
- Sidebar: 6 top level - base_layout.dart:750 Home Dashboard, :753 My Collection, :757 Add new coins, :761 Coin Programs, :763 `_buildNavMorganButton()`, :764 `_MoreSection(`. Every old route still present under More (:767-846). Admin gate kept at :812-813 `if (email == 'jseaman1204@gmail.com' || email.endsWith('@numista.ai')) ...[`.
- PIN: six boxes, no TextField glyphs (login_screen.dart:606 `_PinBoxRow(`, :621 `_NumKeypad(`). 6-digit sanitizer kept (:646-648). Backend untouched, so the 5-guess lockout is untouched. ai_chat_screen.dart untouched.
- Add Coin: 3 cards (Take a photo / Type it in / Upload a list) + "More ways to add".

## Required fixes
1. **PIN can no longer be typed on a keyboard.** The PIN TextField was replaced by the on-screen keypad only (login_screen.dart:606-625); the old `_pinField` (:844, with `autofillHints: const [AutofillHints.password, AutofillHints.oneTimeCode]` at :850) is now dead code. Desktop/web users (and anyone with a password manager) can't enter their PIN with the keyboard. Wrap the PIN box row + keypad in a `Focus`/`KeyboardListener` that takes digits 0-9, Backspace, and Enter (-> `_signIn`), autofocused when the PIN tab shows. Widget test: send key events '1'..'6' + Enter -> `_pinCtrl.text == '123456'` and sign-in called.
2. **`textCaption` token is 12, under the plan's floor.** numista_theme.dart `static const double textCaption  = 12.0;` vs PLAN_V1_REQ032_UX.md:69 "no `fontSize:` below 14 on primary screens (captions may be 14)". The 9-13px fixes in base_layout.dart mostly became this 12px token (:722, :906, :917, :1251, :1395, :1423, :1433, :1460, :1470, :1624, :1629), so the test passes but the text didn't get bigger enough. Set textCaption to 14 (or move those uses to textBodySm) and make the ux test also assert no token under 14.
3. **Sign-in screen still hard-codes 11-13px.** login_screen.dart:824 `_label` (the "Email" / "6-Digit PIN" field labels) `fontSize: 12`; :923 error/success message `fontSize: 13`; :657 "Older account? Sign in with password" uses textCaption (12); also :713, :739, :750, :763 (12), :786, :911 (11). Move these to tokens >= 14 (labels textBodySm or textBody, the error message textBody). Extend the font test to login_screen.dart.
4. **Forgot PIN link.** Plan PLAN_V1_REQ032_UX.md:109 says font 18, 44dp tap target. Build: :628-629 `const Text('Forgot your PIN?', style: TextStyle(color: _grey, fontSize: NumistaTheme.textBody))` (16), and it now only shows in PIN mode; the always-visible link was removed (old block above `_divider('explore without an account')`), so password-mode users have no reset link. Use textLg + 44dp min, and show a reset link in both modes.
5. **Fixed 560 height + width-growing keypad = overflow risk.** :482 `height: _tabCtrl.index == _signInTab ? (_usePasswordSignIn ? 280 : 560) : 360,` while the keypad GridView (:1422 `childAspectRatio: 1.6`) gets taller as the card gets wider. Cap the keypad width (e.g. ConstrainedBox maxWidth 320) and add widget tests at 360x640 and 1280x800 asserting no overflow exception on the sign-in tab.

## Follow-ups (not blockers)
- ux_fixes_test.dart route check is `code.contains(route)`, not "route reachable". Fine for now; T3b smoke should tap through More once.
- Fix 1 (checklist big rows) still correctly deferred (REQ_034/036).
- T3B reuses these screens, so fold the same fixes into T3B rather than doing them twice.

Ball: AG CoS - fold fixes 1-5 into a follow-up commit on dev (no deploy), re-run flutter test + analyze, file EXECUTE_DONE_REQ032_UX_V2.md, pass baton back to GROKCOS.
