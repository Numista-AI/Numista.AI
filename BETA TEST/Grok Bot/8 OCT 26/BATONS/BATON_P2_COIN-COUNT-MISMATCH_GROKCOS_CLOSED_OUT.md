# BATON P2 COIN-COUNT MISMATCH FIX (priority 2 of 5)
Holder: Eric. Ref: NET-078. Deploy YES decision.

## Task
Counts disagree across surfaces: 313 / 311 / 284 / 314. Find the single source of truth and fix the counting code on dev.
- Read-only diagnosis first: list every surface that shows a count, its query/filter, and why each differs (dupes, soft-deletes, sets vs items, paper vs coin, etc.).
- Fix in code only (dev). Do NOT edit, dedupe or delete any collection data. If data cleanup looks needed, write a proposal and stop.
- Counts will move today because Eric is adding coins; test against fixtures / read-only snapshots, not by writing.
- Tests + Gemini build review + EXECUTE_DONE, then pass to GROKCOS.
## HARD LIMITS (all tracks)
- Dev only. No deploy without Eric's own typed YES. Deploys = cherry-pick approved commits onto a branch from main. Never a full dev merge.
- Eric is adding new coin purchases to his collection TODAY. NOTHING writes to his collections or any user collection. No sync_canon. No Firestore writes.
- Never fake data. U.S. Mint/Treasury figures beat PCGS/NGC. No PII or collection values in prompts or files.
- Treat every error as systemic and check related features.
- Rule 7: keep your 25-min wake timer running. git mv the baton (one file per track).
## Log
- 2026-10-14 09:40 ET GROKCOS: issued. Passed to AGCOS. OVER.
- 2026-10-14 11:00 ET AGCOS: Code fix complete on dev. Root cause: home_dashboard passed totalItems (coins+currency+world) to coin cards (313/314), header_stats_bar rendered unexpanded parent docs (284). Single source of truth established via expandCollection/count_coins_and_lots (311 physical coins). Backend snapshot/count updated. Flutter tests (3/3), Pytest (27/27), flutter analyze (0 errors) all pass. Zero Firestore writes. Filed GEMINI38_REVIEW_P2_COIN_COUNT_BUILD.md and EXECUTE_DONE_P2_COIN_COUNT.md. Passed to GROKCOS for build review/scoring. OVER.
- 2026-10-14 11:15 ET GROKCOS: Scored PASS (COS_SCORE_P2_COIN_COUNT). GEMINI38 quotes verified; pytest 2/2. Mixed commits residual — do not whole-cherry-pick 0ddbdec2/b3b7c30f. Passed to ERIC for deploy YES. OVER.

