# BATON P5 DEPLOY numista-qc DEV BACKEND (priority 5 of 5)
Holder: AG CoS. Ref: NET-070, NET-064 CREDIT500 Cloud Run step 2.

## Task
Prepare the numista-qc dev backend Cloud Run deploy. PREP ONLY:
- Write the exact gcloud command, project (Numista.Ai billing, NOT gen-lang-client-0504730428), region, service account, env (no secrets in files; masked input only), estimated cost.
- Confirm it cannot read/write the live Firebase project studio-9101802118-8c9a8 collections.
- Pass to GROKCOS. Grok CoS takes it to Eric for a SEPARATE typed YES. Do NOT run the deploy until that YES is relayed on RADIO NET.
## HARD LIMITS (all tracks)
- Dev only. No deploy without Eric's own typed YES. Deploys = cherry-pick approved commits onto a branch from main. Never a full dev merge.
- Eric is adding new coin purchases to his collection TODAY. NOTHING writes to his collections or any user collection. No sync_canon. No Firestore writes.
- Never fake data. U.S. Mint/Treasury figures beat PCGS/NGC. No PII or collection values in prompts or files.
- Treat every error as systemic and check related features.
- Rule 7: keep your 25-min wake timer running. git mv the baton (one file per track).
## Log
- 2026-10-14 09:40 ET GROKCOS: issued. Passed to AGCOS. OVER.
- 2026-10-14 09:47 ET GROKCOS: Eric typed YES 09:45 ET. AGCOS CLEARED TO DEPLOY numista-qc dev backend NOW, to the numista-qc service on the Numista.Ai billing only. NEVER gen-lang-client-0504730428 (V3Tees). Secrets via masked input only; no live collection access. Report the service URL + smoke results (health 200, an auth route 401 unauth) in EXECUTE_DONE, then pass to GROKCOS. See NET-072. OVER.
- CORRECTION 2026-10-14 09:48 ET (GROKCOS): numista-qc deploys on **My Billing Account** (the $500 Developer Program credit, CREDIT500), NOT the Numista.Ai billing account. It must NEVER go in the V3Tees project gen-lang-client-0504730428, even though that project shares My Billing Account. Everything else in the P5 GO is unchanged.
