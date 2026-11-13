# COS SCORE - T3 REQ_032 UX F1+F2 BUILD (commit e6b808f7 on dev)
Scored by: Grok CoS, 13 Oct 2026 ~3:35 PM ET. Read real code at e6b808f7: git show login_screen.dart + ux_fixes_test.dart; numista_theme.dart textBodySm=14.0. Cross-checked GEMINI38_REVIEW_T3_F1F2_BUILD.md quotes against file lines. Ran flutter test myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed. No live writes.

## Verdict: PASS on dev. Both F1 and F2 from COS_SCORE_REQ032_UX_BUILD_V3.md / NET-029 are fixed.

## Tests (run by Grok CoS)
- flutter test --reporter compact: **434 passed, 0 failed**. Matches EXECUTE_DONE.
- ux_fixes_test.dart alone: all passed (F2 group included). F2 tap(find.byType(PinBoxRow)) prints a Flutter hit-test warning (offset hits the wrapping GestureDetector, not PinBoxRow itself); assertions still pass because HitTestBehavior.opaque on the GestureDetector receives the tap and requestFocus runs. Non-blocking.

## F1 - six FreeScanPreviewScreen fonts (required)
Verified in e6b808f7 login_screen.dart; all six call sites now use NumistaTheme.textBodySm (14.0):
- :1250 Analyzing details... textBodySm
- :1299 upload label textBodySm
- :1301 Tap to upload textBodySm
- :1360 (style) textBodySm
- :1394 label textBodySm
- :1395 value textBodySm
No hardcoded fontSize < 14 remains in the file (literals are all >=14). Test in ux_fixes_test.dart now scans the entire login_screen.dart (not class-boundary-limited). Good.

## F2 - email -> tap PIN -> keys (required)
Production still has KeyboardListener + GestureDetector onTap requestFocus at login_screen.dart ~611-633 (verified). Isolated widget test group 'F2: PIN keyboard survives email TextField focus steal' sends digit1 (captured), steals focus via email TextField (digit2 not captured), taps PinBoxRow/GestureDetector (reclaims), digits 3-6 captured. Full LoginScreen() pump skipped for Firebase async; mechanism matches production. Acceptable for this PASS.

## Gemini BUILD review
GEMINI38_REVIEW_T3_F1F2_BUILD.md has verbatim quotes that match the code. Verdict PASS agreed.

## Bundle YES (ready now)
T1B V2 PASS (CLOSED) + T2 V3 PASS + T3 F1+F2 PASS + T3b V4 PASS (CLOSED). One Eric typed YES deploys the bundle to live. Pre-deploy: confirm Eric Firebase admin:true claim read-only.

## Follow-ups (ticket, not blockers)
- F2 test: tap with warnIfMissed:false or find.byType(GestureDetector) / find the opaque hit target to silence the warning.
- F1 RERUN6 still AGCOS OVER (AWQ dry-run); CREDIT500 WAIT-OUT low-pri.

Ball: ERIC for one YES on the T1B+T2+T3+T3b deploy bundle. No deploy from this score.
