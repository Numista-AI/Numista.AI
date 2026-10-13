# BATON T3_REQ032-UX
Holder: AGCOS  Proword: WAIT-OUT
Since: 13 Oct 2026 ~10:32 AM ET
Task: V3 PASS on dev (COS_SCORE_REQ032_UX_BUILD_V3.md). Parked on T1B; fold follow-ups F1-F2 into T1B V2 commit, return to GROKCOS with T1B V2.
No deploy / live writes without Eric typed YES.
## Log
- 12 Oct 2026 4:47 PM ET GROKCOS issued baton.

## Log
2026-10-12 17:35 ET â€” AG CoS: EXECUTE_DONE_REQ032_UX.md filed. Commit ecd0f9bb. 5 UX fixes, 427 Flutter tests pass. Passing to Grok CoS to score.
- 12 Oct 2026 5:46 PM ET GROKCOS scored build ecd0f9bb ITERATE. 5 required fixes: PIN keyboard lost, textCaption below 14px floor, login_screen hardcoded fonts, Forgot PIN needs tapTarget + both modes, keypad overflow risk. Passing to AGCOS.

## Log
2026-10-12 19:49 ET â€” AG CoS: All 5 T3 ITERATE fixes applied + all 6 T3b ITERATE fixes applied. Commit 9fc13333. 433/433 Flutter tests pass. 474/474 pytest pass. analyze clean. EXECUTE_DONE filed. Passing to Grok CoS to score V2.
- 12 Oct 2026 8:05 PM ET GROKCOS scored T3 V2 9fc13333 ITERATE (COS_SCORE_REQ032_UX_BUILD_V2.md). 2 small: PIN focus never re-requested on tap; fontSize 12 (:1017) and 11 (:1037) past the test line-1000 cutoff. T3b scored separately. Passing to AGCOS.


## Log
- 13 Oct 2026 ~10:00 AM ET AG CoS: T3 V3 done. Commit 9a0b20b8. PIN focus requestFocus() on tap (GestureDetector on _PinBoxRow); _strengthHint label fontSize:12 → textBodySm (:1025); _StatBadge label fontSize:11 → textBodySm (:1045); test scoped by class boundary (class FreeScanPreviewScreen). 433 flutter tests pass; analyze clean. EXECUTE_DONE_REQ032_UX_V3_AND_T3B_V3.md filed. Passing to Grok CoS to score V3.
- 13 Oct 2026 ~10:32 AM ET GROKCOS scored T3 V3 (9a0b20b8) PASS on dev (COS_SCORE_REQ032_UX_BUILD_V3.md; flutter 433/433 on my run). PIN GestureDetector requestFocus (login_screen.dart:631-634), :1025/:1045 textBodySm, class-scoped test. WAIT-OUT: parked on T1B. Follow-ups to fold into T1B V2 commit: F1 six FreeScanPreviewScreen fonts <14 (:1250, :1299, :1301, :1360, :1394, :1395) + test; F2 email->tap PIN->keys widget test. Pass back to GROKCOS with T1B V2. See RADIO NET\NET-022. No stall.
