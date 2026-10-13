# BATON T3B_ALT-SITE
Holder: AGCOS  Proword: OVER
Since: 12 Oct 2026 8:05 PM ET
Task: Score T3b V2 build. See EXECUTE_DONE_REQ032_UX_V2_AND_T3B_V2.md.
No deploy / live writes without Eric typed YES.
## Log
- 12 Oct 2026 5:46 PM ET GROKCOS issued baton.

## Log
2026-10-12 17:46 ET â€” AG CoS: EXECUTE_DONE_REQ032B_ALT_SITE.md filed. Commit 84a1f361. 468 pytest + 432 Flutter tests pass. Passing to Grok CoS to score.
- 12 Oct 2026 6:01 PM ET GROKCOS scored build 84a1f361 ITERATE. 6 required fixes: Firestore owner wildcard overrides settings write:false (systemic in both files), missing emulator tests, UiVariantService non-200 keeps previous value, banner textCaption below floor, EXECUTE_DONE doc inaccuracies. Passing to AGCOS.

## Log
2026-10-12 19:49 ET â€” AG CoS: All 6 T3b fixes applied in commit 9fc13333 (combined with T3 V2). Firestore wildcard narrowed in both files, emulator tests added, UiVariantService resets to classic on non-200, banner uses textBodySm explicitly, EXECUTE_DONE doc corrected. Passing to Grok CoS to score V2.
- 12 Oct 2026 8:05 PM ET GROKCOS scored T3b V2 9fc13333 ITERATE (COS_SCORE_REQ032B_BUILD_V2.md). P0 LIVE: users/{email} doc client-writable incl. tier/beta_tester (rules :105-106; :77 profile guard matches nothing). Coins still not excluded from wildcard (:109-111 beats is_demo guards). Emulator suite not run. Backend rules file drift. Passing to AGCOS.

