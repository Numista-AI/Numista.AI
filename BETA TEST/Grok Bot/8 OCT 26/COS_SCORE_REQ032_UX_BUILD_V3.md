# COS SCORE - T3 REQ_032 UX BUILD V3 (commit 9a0b20b8 on dev, login_screen.dart)
Scored by: Grok CoS, 13 Oct 2026 ~10:30 AM ET. Read real code at dev HEAD 0f33323b: git show 9a0b20b8 (login_screen.dart, ux_fixes_test.dart) and the full lib/screens/login_screen.dart, plus numista_theme.dart. Ran flutter test myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed.

## Verdict: PASS (on dev), with 2 follow-ups. Both V2 items are fixed in the code. Deploy waits on T1B (one Eric YES for the bundle).

## Tests (run by Grok CoS)
flutter test --reporter compact: **+433, All tests passed!**

## V2 items - checked in code
1. **PIN focus re-requested on tap (required).** login_screen.dart:631-634 `GestureDetector(` / `behavior: HitTestBehavior.opaque,` / `onTap: () => _pinKeyboardFocus.requestFocus(),` / `child: _PinBoxRow(`. It sits inside the `KeyboardListener(focusNode: _pinKeyboardFocus, autofocus: true,` at :611-613. Keypad taps also re-grab focus: :53-55 `void _onKeypadDigit(String d) {` / `_pinKeyboardFocus.requestFocus();`. Typing an email, then clicking the boxes, now sends digits to the PIN. Good.
2. **Last two login fonts under 14 (required).** :1025 `Text(label, style: TextStyle(color: color, fontSize: NumistaTheme.textBodySm, fontWeight: FontWeight.w600)),` (_strengthHint). :1045 `Text(label, style: const TextStyle(fontSize: NumistaTheme.textBodySm, color: Color(0xFF64748B), height: 1.3), ...` (_StatBadge). numista_theme.dart:8 `static const double textBodySm   = 14.0;`. The test is now scoped by class: ux_fixes_test.dart `if (lines[i].contains('class FreeScanPreviewScreen')) {` / `boundaryLine = i;`. That covers _StatBadge (:1033) and _StatDivider (:1051), both before :1061 `class FreeScanPreviewScreen`. PinBoxRow (:1436 `fontSize: 24`) and NumKeypad (:1486 `fontSize: 22`) are past the boundary but already at least 14. Good.

## Decision on FreeScanPreviewScreen fonts: follow-up ticket, not ITERATE
That screen is outside the login-form scope I set in V2. But AG's count is wrong: there are **6** sizes under 14 left in it, not 2:
:1250 `fontSize: 11` ('Analyzing details & estimating value'), :1299 `fontSize: 13` (upload label), :1301 `fontSize: 11` ('Tap to upload'), :1360 `fontSize: 12`, :1394 `fontSize: 13` (label), :1395 `fontSize: 13` (value).
This is the free-scan page logged-out visitors see, and it has to meet Eric's 14px floor before Coin Club beta on 3 Nov. Ticket it, and extend the test to cover the whole file (or this class too).

## Follow-ups (do in the next T1B commit; not blockers)
- F1: the 6 FreeScanPreviewScreen fonts above, plus a test that covers them.
- F2: the widget test V2 asked for is still missing. No test does enter email -> tap PIN row -> sendKeyEvent 1-6 -> 6 boxes filled -> Enter signs in (grep finds no `sendKeyEvent` in test/). The code is right. Add the test so a regression can't come back.

Ball: AG CoS, WAIT-OUT (parked). Fold F1-F2 into the T1B V2 commit and pass this baton back to GROKCOS with T1B. Then it goes to Eric under one YES.