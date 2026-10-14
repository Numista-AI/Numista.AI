# BATON P2 COIN-COUNT MISMATCH FIX (priority 2 of 5)
Holder: AG CoS. Ref: NET-070.

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
