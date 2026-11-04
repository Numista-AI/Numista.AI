# PLAN A: Shorter, goal-based prompts and hard retry caps for Antigravity (AG)
Owner: Antigravity Desk | Status: DRAFT v1, not approved | Timing: PRE-LAUNCH (process only, no code)
Source: Google "Startup guide to AI agents": p.22 ("Goldilocks" intent-level prompts), p.16–17 (Loop agents with a set maximum number of tries), p.21 (human as manager and approver), p.3 ("tokenomics").

## Goal
Cut AG's cost from about $44 per workday toward the $9 target by:
1. sending AG short prompts that state a goal instead of long, rigid ones, and
2. enforcing our retry rule as a hard stop.
The $44 and $9 figures come from the brief. They have not been re-checked against billing.

## Scope
- The wording of every task AG receives from GB CoS, Desk, Argon and the other writers.
- One shared prompt template (below).
- A written retry counter for each task, kept in the baton/RADIO file.
- Measuring AG's cost before and after the change.

## Out of scope
- No code, app, Firestore or deploy changes.
- No change to AG's model, account or billing settings.
- No change to the 3 AM stand-down or the review chain.
- Overnight automation and "autonomous agents on timers" (p.3) are out. They conflict with our rules.

## The retry rule (unchanged, now enforced on paper)
- Each task has an attempt counter, starting at 1.
- After 4 failed tries by the same writer, that writer is replaced. The counter keeps going; it does not reset.
- At 10 total attempts, all work stops. GB CoS notifies Eric and breaks the task into smaller pieces, and each piece starts at attempt 1.
- What counts as one attempt: one submitted plan/fix that a reviewer (Argon, GB CoS, SAG or Field Tester) sends back.
- AG's own internal re-runs inside a single attempt are capped at 3. If it hits 3, it stops and reports "BLOCKED" with the reason, rather than looping (this mirrors the guide's capped Loop agents, p.16–17).

## Prompt template (target: 25 lines or fewer)
```
TASK ID: NET-___   ATTEMPT: _ of 10   WRITER TRY: _ of 4
GOAL (1–2 sentences): what "done" looks like for the user.
WHY: one line.
INPUTS: file paths only (no pasted file contents).
MUST: up to 5 hard rules (e.g. no PII, no deploy, no Firestore writes without Eric's YES).
MUST NOT: up to 3 items.
DONE WHEN: up to 3 checks a reviewer can verify.
OUTPUT: one file at <path>, plus a status line: DONE / BLOCKED (reason) / NEEDS-DECISION (question).
LIMITS: max 3 internal retries; stop at 3 AM; spend cap $__.
```
Rules for using it:
- Point to files instead of pasting them. Pasted batons are the main source of long prompts.
- Do not repeat the standing rules in full each time. Keep them in one standing-rules file and reference it.
- Ask for one result per task.

## Steps
1. Baseline (week 1, read-only): FIN OPS pulls AG's daily cost for the last 10 workdays from the existing billing view. Desk records the prompt length (in characters) and attempt count for each task in that period. Nothing changes during the baseline.
2. Desk drafts the standing-rules file and the template. Argon reviews.
3. Pilot for 5 workdays: all new AG tasks use the template and the counter.
4. Measure: the same numbers as step 1.
5. Report to GB CoS, which reports to Eric.

## How to measure cost before and after
| Measure | Where it comes from | Target |
|---|---|---|
| AG $ per workday | FIN OPS billing view (same source both periods) | Down from ~$44, heading to $9 |
| Average prompt length | Desk log of characters sent | Down by at least 50% |
| Attempts per task | Counter in the baton file | Down, or steady |
| Tasks that hit 10 attempts | Counter | Report each one to Eric |
| Quality | Field Tester / Argon pass rate | Not worse than the baseline |
Compare averages per workday. Ignore days with unusual one-off jobs, and list which days were left out.

## Success criteria
- Every AG task in the pilot uses the template and shows its attempt counter.
- AG's cost per workday falls by a meaningful amount (goal: under $25 in the pilot, then toward $9), and the pass rate is not lower.
- No task goes past 10 attempts without Eric being told.

## Rollback
Go back to the old prompts. It's a process change, so rollback is immediate and costs nothing. The counter stays, because it's an existing rule.

## Cost estimate
$0 to set up. The pilot costs AG's normal daily spend. Savings are UNVERIFIED until the baseline is measured.

## Risks
- Prompts that are too short can lose critical rules. The fix is the standing-rules file, which is referenced every time.
- Quality could drop. The pass-rate check catches that.
- Counting "attempts" differently from agent to agent. The fix is the definition above.
- PII: the template forbids pasting user data. Never put AJ's name, nickname, address, collection value, item count or anything similar into prompts or logs. Never put coin storage locations in them either.
- An agent saying "done" is not approval. Only Eric's typed YES approves.

## Review chain
Desk draft → Argon → GB CoS score 95+ → SAG → Eric's typed YES → pilot.

## Open questions for Eric
1. Is a 5-workday pilot OK, starting after your YES?
2. Is a cap of 3 internal re-runs per attempt OK?


## Eric decisions (4 Nov 2026, 10:36 AM ET)
- 5-workday pilot, cap of 3 re-runs per attempt: YES.
