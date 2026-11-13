# PLAN A: Shorter, goal-based prompts and hard retry caps for Antigravity (AG)
Owner: Antigravity Desk | Status: v1.3 (GB CoS fold, 4 Nov 2026; approved by Eric 4 Nov 2026 5:01 PM ET) | Timing: PRE-LAUNCH (process only, no code)
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
- Each task has an attempt counter. Desk (never the writer) keeps it in the baton/RADIO file. ATTEMPT = the number of the submission now under review, starting at 1; it goes up by 1 each time a reviewer sends a submission back. WRITER TRY = the same count for the current writer only, and resets to 1 when the writer is replaced. A submission that comes back from two reviewers in the same round counts once. A DONE, BLOCKED or NEEDS-DECISION status does not add an attempt; only a reviewer send-back does.
- Writer cap: when submission WRITER TRY 4 is sent back by a reviewer, that writer is replaced. WRITER TRY 5 is never opened. ATTEMPT keeps counting across writers; only WRITER TRY resets (to 1) for the new writer.
- Task cap: when submission ATTEMPT 10 is sent back by a reviewer, all work on the task stops. ATTEMPT 11 is never opened. GB CoS notifies Eric and splits the task into smaller pieces, and each piece starts at ATTEMPT 1. If the writer cap and the task cap fall on the same send-back, the task cap wins (stop; no new writer).
- AG's own internal re-runs inside a single attempt are capped at 3. If it hits 3, it stops and reports "BLOCKED" with the reason, rather than looping (this mirrors the guide's capped Loop agents, p.16–17).
- The standing TWO STRIKES rule (00_BATON_RULES.md Rule 8, item 4) still applies inside the cap: if a build, deploy, test run or command fails twice in a row for the same reason, AG stops at 2 and files a NET message, even if it has re-runs left. The cap of 3 is a ceiling, never a licence to retry the same failure a third time.

## Prompt template (target: 25 lines or fewer)
```
TASK ID: NET-___   ATTEMPT: _ (max 10; stop if #10 is sent back)   WRITER TRY: _ (max 4; replace writer if #4 is sent back)
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
1. Baseline (week 1, read-only): FIN OPS pulls AG's daily cost for the last 10 workdays from the existing billing view. Desk records the prompt length (in characters) and attempt count for each task in that period. Nothing changes during the baseline. Desk also records quality for the same period: pass rate = tasks accepted by their first reviewer ÷ tasks submitted to a reviewer (Argon, GB CoS, SAG or Field Tester), taken from existing review files.
2. Desk drafts the standing-rules file and the template. Argon reviews.
3. Pilot for 5 workdays: all new AG tasks use the template and the counter.
4. Measure: the same numbers as step 1, including the pass rate, defined the same way.
5. Report to GB CoS, which reports to Eric.

## How to measure cost before and after
| Measure | Where it comes from | Target |
|---|---|---|
| AG $ per workday | FIN OPS billing view (same source both periods) | At least 40% below the MEASURED step-1 baseline (the ~$44 and $9 figures are unverified context only) |
| Average prompt length | Desk log of characters sent | Down by at least 50% |
| Attempts per task | Counter in the baton file | Down, or steady |
| Tasks whose ATTEMPT 10 was sent back | Counter | Report each one to Eric; counts as a cap breach, not a success |
| Quality | Field Tester / Argon pass rate | Not worse than the baseline |
Compare averages per workday. Ignore days with unusual one-off jobs, and list which days were left out.

## Success criteria
- Every AG task in the pilot uses the template and shows its attempt counter.
- AG's cost per workday falls by a meaningful amount (goal: at least 40% below the measured step-1 baseline; the unverified ~$44 → $9 figures are context, not the test), and the pass rate is not lower.
- No task ever opens ATTEMPT 11 or a WRITER TRY 5. Any task that does is a FAIL for the pilot, even if Eric was told; an overrun Eric was told about is not success.

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
1. [CLOSED] Is a 5-workday pilot OK, starting after your YES? (Answer: YES, Eric 10:36 AM / 5:01 PM ET)
2. [CLOSED] Is a cap of 3 internal re-runs per attempt OK? (Answer: YES, Eric 10:36 AM / 5:01 PM ET)


## Eric decisions (4 Nov 2026, 10:36 AM ET)
- 5-workday pilot, cap of 3 re-runs per attempt: YES.

## Change log v1 → v1.1 (GB CoS, 4 Nov 2026)
1. Success target (measure table + success criteria) is now relative to the measured baseline, not the unverified $44/$25/$9 figures (Argon advisory 1, confirmed).
2. Added how the 3-re-run cap interacts with the existing TWO STRIKES rule (Argon advisory 2; quote of 00_BATON_RULES.md:12 checked against the real file and matches).
No change to Eric's decisions.
4. (SAG round 1) Defined who keeps the counter, how it goes up, the WRITER TRY reset, and that statuses don't count. Added a measurable pass rate to the baseline and to the measure step.

## Eric decisions (second round)
- Eric's typed acceptance, 4 Nov 2026, 4:32 PM ET: second fix-and-rescore round approved.

## Change log v1.1 → v1.2 (GB CoS, 4 Nov 2026)
5. (SAG round 2) Removed the old "what counts as one attempt" line and rewrote the 4-tries line, so there is one counting rule (above) and one reset rule: ATTEMPT never resets within a task; WRITER TRY resets only when the writer is replaced.


## Change log v1.2 → v1.3 (GB CoS, 4 Nov 2026)
6. (SAG round 3 must-fix) Put both caps in the counter's own units (submission numbers). Writer is replaced when submission WRITER TRY 4 is sent back; WRITER TRY 5 is never opened. Task stops when submission ATTEMPT 10 is sent back; ATTEMPT 11 is never opened; GB CoS notifies Eric and splits the task. Updated the template header, the measure table and the success line to match, and stated that an overrun Eric was told about is not success. Advisories from round 3 not yet applied (Eric approved this one fix-and-rescore round only).
