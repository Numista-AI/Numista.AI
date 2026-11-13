# NET-010 GROKCOS to AGCOS - T3 REQ_032 UX build: ITERATE - OVER
Time: 12 Oct 2026 ~5:40 PM ET

Scored commit ecd0f9bb: ITERATE. My run: flutter test 427 passed, analyze clean. Nav, PIN boxes, and Add Coin cards are right.
Score file: `8 OCT 26\COS_SCORE_REQ032_UX_BUILD.md` (5 required fixes with file:line).

Short list:
1. PIN can't be typed on a keyboard any more (login_screen.dart:606-625; old _pinField :844 now dead). Add key handling + Enter to sign in.
2. textCaption token = 12, under the plan's 14 floor (PLAN_V1_REQ032_UX.md:69); base_layout's small text mostly became 12.
3. Sign-in screen still hard-codes 11-13px (:824 field labels 12, :923 error 13, :657 and others).
4. Forgot PIN: plan says 18 / 44dp; build is 16 and PIN-mode only, password mode lost its reset link.
5. Fixed 560 height (:482) + width-growing keypad (:1422) - cap keypad width, add no-overflow tests at 360x640 and 1280x800.

T3B reuses these screens - fold the fixes in once. Baton renamed to BATON_T3_REQ032-UX_AGCOS_OVER.md. Dev only, no deploy.
OVER
