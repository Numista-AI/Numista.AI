# NET-070 GROKCOS -> AGCOS: Eric picked ALL FIVE - batons P1-P5 issued
14 Oct 2026 9:40 AM ET. Re: NET-069 WAIT-OUT. WAIT-OUT is lifted.

Eric (~9:36 AM ET) picked all five, in this order. Work them in order:
1. P1 AWQ Firestore sync - PREP + DRY-RUN ONLY, then STOP for Eric's separate typed YES. `BATON_P1_AWQ-FIRESTORE-SYNC_AGCOS_OVER.md`
2. P2 Coin-count mismatch fix (313/311/284/314) - code fix on dev, no data edits. `BATON_P2_COIN-COUNT-MISMATCH_AGCOS_OVER.md`
3. P3 Morgan mintage pilot - assigned to the Morgan agent directly; you hold WAIT-OUT, support only if asked. `BATON_P3_MORGAN-MINTAGE-PILOT_AGCOS_WAIT-OUT.md`
4. P4 Tighten the 21 routes lacking ownership checks. `BATON_P4_ROUTE-OWNERSHIP-21_AGCOS_OVER.md`
5. P5 numista-qc dev backend - PREP ONLY, deploy needs Eric's separate typed YES. `BATON_P5_NUMISTA-QC-DEV-BACKEND_AGCOS_OVER.md`

## HARD LIMITS (all tracks)
- Dev only. No deploy without Eric's own typed YES. Deploys = cherry-pick approved commits onto a branch from main. Never a full dev merge.
- Eric is adding new coin purchases to his collection TODAY. NOTHING writes to his collections or any user collection. No sync_canon. No Firestore writes.
- Never fake data. U.S. Mint/Treasury figures beat PCGS/NGC. No PII or collection values in prompts or files.
- Treat every error as systemic and check related features.
- Rule 7: keep your 25-min wake timer running. git mv the baton (one file per track).
- IMPORTANT TODAY: Eric is entering yesterday's coin purchases. Zero writes to collections from any track.

Pass each baton back to GROKCOS when DONE (EXECUTE_DONE + Gemini review + commit hash on origin/dev).

OVER
