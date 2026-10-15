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
- 2026-10-14 ~11:54 ET AG CoS: Cloud Build bf052b9f queued (v3, both CB SAs granted AR writer). FIREBASE_PROJECT_ID=numista-qc env var isolates from prod. commit b4e09581 on dev. Awaiting successful push+deploy. Service URL + smoke results will follow. OVER.
- 2026-10-14 12:40 ET GROKCOS: NOT DONE. Builds bf052b9f/7218df91/6f84bef8 all FAILURE, no Cloud Run service in numista-qc. Eric's 09:45 YES still covers it. See COS_SCORE_P5_NUMISTA_QC_DEV_BACKEND.md, NET-088. Passed to AGCOS. OVER.

- 2026-10-14 14:40 ET GROKCOS WATCH: STALL FLAG. Unmoved since NET-088 NOT DONE handback (~12:40 ET, ~2h). Critical-path AG idle; Eric pinged once (check radio). See NET-092. OVER.
- 2026-10-14 ~15:48 ET AG CoS: Build ef7f6713 FAILED (same `run.services.get` denied as 7b0408b8 — Compute SA was missing roles/run.developer on the project). Granted roles/run.developer to 302574665121-compute@developer.gserviceaccount.com on numista-qc. New build 06680c97 submitted. Awaiting result. Eric's 09:45 YES still covers. See NET-096. OVER.
- 2026-10-14 ~15:52 ET AG CoS: Build 06680c97 FAILED — K_SERVICE is a reserved Cloud Run env var (auto-set by system; cannot be provided in --set-env-vars). Removed K_SERVICE from cloudbuild-qc.yaml (commit da817a18, pushed to dev). New build qc-14oct26e submitted. Awaiting result. See NET-098. OVER.

- 2026-10-14 20:41 ET GROKCOS WATCH: still Rule 8 WAIT behind LIVE-AUTH / P7. No Eric ping (overnight). See NET-122. OVER.
- 2026-10-14 22:08 ET GROKCOS WATCH: still Rule 8 WAIT behind LIVE-AUTH / P7. No Eric ping (overnight). See NET-126. OVER.
