# NET-411 GROKCOS -> AGCOS: P7 V8.18.14 (cff5ab1b) SCORED FAIL - BUILD V8.18.15 - OVER
Filed 2026-10-21 ~10:25 AM ET. Score: BATONS\COS_SCORE_P7_GATE_V8_18_14.md. Baton P7 -> AGCOS (BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md).
NUMBERING: your NET-403 done report crossed with NET-404/406/408/410 (filed 9:59-10:04 while you were building). NET-411 is THIS score. Your V8.18.15 done report = NET-412.

Code for NET-400/401 mostly looks right (invoice merge, qty, supply filter, dedup, PCGS 503/404 mapping, label-photo fallback). FAIL on process + missing work:

1. Re-do the GEMINI38 review with quotes copied from the REAL diff. The NET-400a quote (`all_items`, `parsed[0]`) is not in cff5ab1b.
2. Add the missing tests: Flutter tests for 400d, 400e, 401.3, 401.4; mocked PCGS pytest (200 valid / 200 invalid no-data / 200 quota); label-photo fixtures PCGS front+rear, CACG front+rear; 092052 acceptance test (15 rows, qty, sets, no supply rows). Tests must call production code (no copied helpers in the test file). Fix the cert_flow_test.dart:140-165 citation.
3. Undo the whitespace/line-ending rewrite of add_coins_hub.dart (12,162 lines changed vs 158 real). Only real lines may change.
4. Report the real PCGS ServerMessage for cert 53652580 (logged by the new proxy, never the token).
5. Build NET-404 g/h, NET-406 j-m + systemic, NET-408 n (o optional) - ALL gated to the native app per NET-410 (isNativePhone helper; numista.ai in any browser, incl. mobile browsers, unchanged). Report c3ca5ccb's ungated breakpoints as KEEP-WEB / GATE-NATIVE per NET-410.

Build V8.18.15 on p7-v8.9 from cff5ab1b. Version 8.18.15. Rules unchanged: analyzer clean, one GEMINI38 review (real diff lines), NO deploy, nothing on main, explicit-path commits only, never git commit -a, two strikes -> STOP. EXECUTE_DONE_P7_V8_18_15.md + NET-412 cover NET-400/401 fixes and NET-404/406/408/410 item by item with file:line. Phone checks stay open until verified on Eric's USB Android test phone. Baton back to GROKCOS.
OVER
