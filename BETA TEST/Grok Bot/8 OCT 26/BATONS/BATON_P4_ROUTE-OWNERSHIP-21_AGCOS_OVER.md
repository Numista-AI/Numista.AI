# BATON P4 TIGHTEN 21 ROUTES LACKING OWNERSHIP CHECKS (priority 4 of 5)
Holder: AG CoS. Ref: NET-070, NET-067 Category-2 residual, T4.

## Task
Add per-route ownership (caller uid == resource owner, or admin) to the 21 Category-2 routes from the T4 audit.
- List all 21 with file:line in the EXECUTE_DONE. Add an IDOR test per route (pytest -s). Re-run full pytest + flutter test.
- Check related routes systemically (same handler patterns). Keep CORS behavior on 401s in mind (outer default-deny middleware).
- Dev only. Deploy later only on Eric's typed YES via cherry-pick from main.
## HARD LIMITS (all tracks)
- Dev only. No deploy without Eric's own typed YES. Deploys = cherry-pick approved commits onto a branch from main. Never a full dev merge.
- Eric is adding new coin purchases to his collection TODAY. NOTHING writes to his collections or any user collection. No sync_canon. No Firestore writes.
- Never fake data. U.S. Mint/Treasury figures beat PCGS/NGC. No PII or collection values in prompts or files.
- Treat every error as systemic and check related features.
- Rule 7: keep your 25-min wake timer running. git mv the baton (one file per track).
## Log
- 2026-10-14 09:40 ET GROKCOS: issued. Passed to AGCOS. OVER.
- 2026-10-14 12:40 ET GROKCOS: SCORED FAIL. Full pytest 15 failed (receipts/identify routes) caused by P4; clean P4 commit needed; check attorney links. See COS_SCORE_P4_ROUTE_OWNERSHIP.md, NET-088. Passed to AGCOS. OVER.
