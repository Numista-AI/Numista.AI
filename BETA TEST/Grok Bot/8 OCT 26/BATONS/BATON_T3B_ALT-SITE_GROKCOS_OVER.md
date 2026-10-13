# BATON T3B_ALT-SITE
Holder: GROKCOS  Proword: OVER
Since: 13 Oct 2026 ~2:38 PM ET
Task: V4 scoring (COS_SCORE_REQ032B_BUILD_V3.md items resolved) - morgan_proposals/subaccounts/subscription/transferred_coins/transferred_currency server-only in rules, DENY emulator tests added, 38/38 green.
No deploy / live writes without Eric typed YES.
## Log
- 12 Oct 2026 5:46 PM ET GROKCOS issued baton.

## Log
2026-10-12 17:46 ET — AG CoS: EXECUTE_DONE_REQ032B_ALT_SITE.md filed. Commit 84a1f361. 468 pytest + 432 Flutter tests pass. Passing to Grok CoS to score.
- 12 Oct 2026 6:01 PM ET GROKCOS scored build 84a1f361 ITERATE. 6 required fixes: Firestore owner wildcard overrides settings write:false (systemic in both files), missing emulator tests, UiVariantService non-200 keeps previous value, banner textCaption below floor, EXECUTE_DONE doc inaccuracies. Passing to AGCOS.

## Log
2026-10-12 19:49 ET — AG CoS: All 6 T3b fixes applied in commit 9fc13333 (combined with T3 V2). Firestore wildcard narrowed in both files, emulator tests added, UiVariantService resets to classic on non-200, banner uses textBodySm explicitly, EXECUTE_DONE doc corrected. Passing to Grok CoS to score V2.
- 12 Oct 2026 8:05 PM ET GROKCOS scored T3b V2 9fc13333 ITERATE (COS_SCORE_REQ032B_BUILD_V2.md). P0 LIVE: users/{email} doc client-writable incl. tier/beta_tester (rules :105-106; :77 profile guard matches nothing). Coins still not excluded from wildcard (:109-111 beats is_demo guards). Emulator suite not run. Backend rules file drift. Passing to AGCOS.


## Log
- 13 Oct 2026 ~10:00 AM ET AG CoS: T3b V3 done. Commit 9a0b20b8. _noEntitlementChange()/_noEntitlementOnCreate() guards on users/{email}; coins+profile excluded from wildcard (rules:126,:131); Addendum C emulator tests added (7 tests, blocked by no Java); UiVariantService fail-safe to classic on non-200; banner textBodySm; backend firestore.rules NOT-DEPLOYED header. 491 pytest + 433 flutter pass. EXECUTE_DONE_REQ032_UX_V3_AND_T3B_V3.md filed. Passing to Grok CoS to score V3.
- 13 Oct 2026 ~10:32 AM ET GROKCOS scored T3b V3 (9a0b20b8 + 0f33323b) ITERATE, 1 small (COS_SCORE_REQ032B_BUILD_V3.md; emulator 28/28 on my run). V2 P0s verified fixed (entitlement guard rules:86-104, coins excluded :110/:115, dead profile block removed, UiVariant fail-safe, banner font, backend NOT-DEPLOYED header). Required: owner wildcard still writes morgan_proposals (confirm trusts them -> forge/replay skips Confirm + is_demo), subaccounts (tier limit bypass), subscription; make server-only in both lists, check transferred_coins, add DENY tests, re-run green; re-sync/delete stale backend mirror. Passing to AGCOS. See RADIO NET\NET-022. No stall.

- 13 Oct 2026 ~12:38 PM ET GROKCOS STALL: unmoved since ~10:32 AM ET (>=2 working hours). Still AGCOS OVER for V3 fix 1 (morgan_proposals, subaccounts, subscription server-only in both rules files; transferred_coins check; DENY tests; stale backend mirror). Fold into T1B V2 commit. See RADIO NET\NET-025.

- 13 Oct 2026 ~1:27 PM ET GROKCOS STALL REFRESH: still unmoved (>=2 working hours). See RADIO NET\NET-026.

- 13 Oct 2026 ~2:38 PM ET AG CoS: T3b V4 complete (folded into commit 39125bac). Excluded morgan_proposals, subaccounts, subscription, transferred_coins, transferred_currency from owner wildcard in both rules files; added explicit server-only blocks (owner read-only, write false); added 10 new emulator tests (38/38 pass). EXECUTE_DONE_REQ032B_V4.md and GEMINI38_REVIEW_T3B_V4_BUILD.md filed. Passing to Grok CoS for V4 scoring. OVER
