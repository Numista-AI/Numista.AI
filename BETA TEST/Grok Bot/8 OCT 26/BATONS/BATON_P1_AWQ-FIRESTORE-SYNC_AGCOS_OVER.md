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
- 2026-10-14 ~10:50 ET — AG CoS: Dry-run complete. 62 docs would change. NO writes made. Apply on HOLD until separate Grok CoS GO. See EXECUTE_DONE_P1_AWQ_DRYRUN.md.
- 2026-10-14 14:17 ET GROKCOS WATCH: STALL FLAG. Unmoved since ~10:50 ET dry-run (~207m). Dry-run done; apply still ON HOLD awaiting Eric finish adding coins + Grok CoS separate GO (NET-072). Not an AG idle fault. No Eric ping this cycle. OVER.
- 2026-10-14 15:45 ET GROKCOS WATCH: still intentional HOLD (unmoved since ~10:50 ET dry-run). Awaiting Eric finish adding coins + Grok CoS separate GO. Not an AG fault; no Eric ping. See NET-097. OVER.
- 2026-10-14 17:40 ET GROKCOS WATCH: still intentional HOLD (dry-run ~10:50 ET). Awaiting Eric finish adding coins + Grok CoS separate GO. Not an AG fault; no Eric ping. See NET-110. OVER.

- 2026-10-14 19:41 ET GROKCOS WATCH: still intentional HOLD (dry-run ~10:50 ET). Awaiting Eric finish adding coins + Grok CoS separate GO. Not an AG fault; no Eric ping. See NET-117. OVER.

- 2026-10-14 20:41 ET GROKCOS WATCH: still intentional HOLD (dry-run ~10:50 ET). Awaiting Eric finish adding coins + Grok CoS separate GO. Not an AG fault; no Eric ping (overnight). See NET-122. OVER.
- 2026-10-14 22:08 ET GROKCOS WATCH: still intentional HOLD (dry-run ~10:50 ET). Awaiting Eric finish adding coins + Grok CoS separate GO. Not an AG fault; no Eric ping (overnight). See NET-126. OVER.

- 2026-10-15 19:45 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.7 (Rule 8). Not a stall. Overnight quiet. See NET-230. OVER.

- 2026-10-15 21:12 ET GROKCOS WATCH: hourly re-flag. Still intentional HOLD (await Eric coins + separate GO). Queued behind P7 V8.8 (Rule 8). Not a stall. Overnight quiet. See NET-234. OVER.


- 2026-10-15 22:15 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-238. OVER.

- 2026-10-15 23:38 ET GROKCOS WATCH: hourly re-flag. Still intentional HOLD (await Eric coins + separate GO). Queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-242. OVER.
