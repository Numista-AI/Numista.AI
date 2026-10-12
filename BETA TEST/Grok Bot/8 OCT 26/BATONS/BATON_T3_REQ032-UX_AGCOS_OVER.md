# BATON T3_REQ032-UX
Holder: AGCOS  Proword: OVER
Since: 12 Oct 2026 4:47 PM ET
Task: Fix file paths + menu count, then build on dev. See COS_SCORE_REQ032_UX.md.
No deploy / live writes without Eric typed YES.
## Log
- 12 Oct 2026 4:47 PM ET GROKCOS issued baton.
- 12 Oct 2026 5:15 PM ET GROKCOS scored PLAN V1.1 PASS (COS_SCORE_REQ032_UX_V1_1.md). AGCOS: build on dev, no deploy. PIN field is login_screen.dart:580-582/794, not 32-104.

## Log
2026-10-12 17:34 ET — AG CoS: EXECUTE_DONE_REQ032_UX.md filed. Commit ecd0f9bb. 4 fixes, 427 tests pass, analyze clean. Passing to Grok CoS.
- 12 Oct 2026 5:40 PM ET GROKCOS scored build ecd0f9bb ITERATE (COS_SCORE_REQ032_UX_BUILD.md; flutter test 427 passed, analyze clean on my run). 5 required fixes: PIN keyboard entry, textCaption 12 under 14 floor, login screen 11-13px text, Forgot PIN size/both modes, 560 height overflow risk. Passing to AGCOS. See RADIO NET\NET-010.
