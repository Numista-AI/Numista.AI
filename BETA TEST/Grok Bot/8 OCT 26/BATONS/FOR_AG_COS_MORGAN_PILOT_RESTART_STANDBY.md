# FOR AG CoS — MORGAN PILOT RESTART (STANDBY)
**FROM:** Grok CoS  **TO:** AG CoS  **INFO:** FIN OPS, Desk, Eric
**DATE:** 26 Oct 2026 ~9:50 AM ET
**REF:** NET-522, `MORGAN_PILOT\RESTART_PLAN_V1.md`, Eric YES 26 Oct ~9:22 AM ET
**PRIORITY vs B4:** **B4 FAIL-FIX (NET-518/520) stays AG's primary.** This baton is standby only.

## BLUF
Eric wants the Agent Builder credit burning again on sandbox `numista-morgan-pilot`. Package and commands are filed. **Grok CoS owns the overnight run** (same as 13 Oct). AG picks this up **only if** CoS cannot run after Eric AUTH_OK and B4 is already EXECUTE_DONE / Argon-bound.

## If you must run (standby path)
1. Confirm AUTH: `gcloud auth print-access-token` works as `eric@numista.ai`.
2. `cd "…\8 OCT 26\MORGAN_PILOT\scripts"`
3. Follow `COMMANDS_RESTART_V1.md` steps 1–4 (Batch A only).
4. Set `MAXF=10` in `pilot.py` before run.
5. Output report-only CSVs under `MORGAN_PILOT\out\`. File `EXECUTE_DONE_MORGAN_PILOT_BATCH_A.md` + NET tip.
6. **Do not** touch Flutter, Firestore, prod project, V3Tees, Advanced Answers, Grounded Generation, main merge, or live deploy.

## Out of scope for AG tonight
- Building new Discovery Engine apps beyond existing `morgan-pilot-search`
- State Quarters batch (after Morgan Batch A results)
- Product code for Mint-pack / Upload Invoice

## Explicit
WAKE never authorizes deploy. No spend on non-credit SKUs. Kill switch in RESTART_PLAN_V1.md.
