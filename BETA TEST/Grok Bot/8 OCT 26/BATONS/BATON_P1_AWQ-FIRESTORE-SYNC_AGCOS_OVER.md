# BATON P1 AWQ FIRESTORE SYNC (priority 1 of 5)
Holder: AG CoS. Ref: NET-070.

## Task
Prepare the AWQ (F1 slot fix, PR #260 / 7782fb20) Firestore sync and run a DRY-RUN ONLY.
- Build the sync script/plan; no --apply, no write.
- Dry-run output to a CSV/MD in this folder: docs that WOULD change, field before/after, counts. Exclude any user collection paths entirely.
- Gemini build review + EXECUTE_DONE file as usual.
- Then pass baton to GROKCOS for score. Grok CoS takes it to Eric for a SEPARATE typed YES. STOP there.
- Note: Eric is adding coins today; the live apply must not run until he says his entries are done AND types YES.
## HARD LIMITS (all tracks)
- Dev only. No deploy without Eric's own typed YES. Deploys = cherry-pick approved commits onto a branch from main. Never a full dev merge.
- Eric is adding new coin purchases to his collection TODAY. NOTHING writes to his collections or any user collection. No sync_canon. No Firestore writes.
- Never fake data. U.S. Mint/Treasury figures beat PCGS/NGC. No PII or collection values in prompts or files.
- Treat every error as systemic and check related features.
- Rule 7: keep your 25-min wake timer running. git mv the baton (one file per track).
## Log
- 2026-10-14 09:40 ET GROKCOS: issued per Eric's pick (all five, this order). Passed to AGCOS. OVER.
- 2026-10-14 09:47 ET GROKCOS: Eric typed YES 09:45 ET for the P1 live apply. YES RECORDED, APPLY ON HOLD. AGCOS finishes the dry-run only. Do NOT apply until Grok CoS posts a separate GO on RADIO NET after Eric finishes adding coins (he starts ~noon). See NET-072. OVER.
