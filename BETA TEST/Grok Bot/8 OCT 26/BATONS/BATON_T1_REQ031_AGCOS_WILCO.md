# BATON T1_REQ031
Holder: AGCOS  Proword: WILCO
Since: 12 Oct 2026 4:47 PM ET
Task: Build REQ_031 hotfix on dev with COS_SCORE_REQ031_HOTFIX.md fixes folded in. FIRST priority.
No deploy / live writes without Eric typed YES.
## Log
- 12 Oct 2026 4:47 PM ET GROKCOS issued baton.

## Log
2026-10-12 17:11 ET — AG CoS: EXECUTE_DONE_REQ031.md filed. Commit a774152f. 12 fixes, 447 tests pass. Passing to Grok CoS to score code.
- 12 Oct 2026 5:25 PM ET GROKCOS scored build a774152f PASS (COS_SCORE_REQ031_BUILD.md; 447/447 pytest). Passing to ERIC for typed YES to deploy.

- 12 Oct 2026 6:55 PM ET ERIC typed YES: DEPLOY a774152f (REQ_031 backend only) to production. AGCOS: deploy, write DEPLOY_DONE_REQ031.md with revision + time, then pass baton to GROKCOS OVER for Field Tester smoke (incl. scanned coins appear in Review Hub). Do NOT include T2/T3/T3B commits or firestore.rules changes.
