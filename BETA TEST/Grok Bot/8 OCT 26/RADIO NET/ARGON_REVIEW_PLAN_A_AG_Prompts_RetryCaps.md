# ARGON REVIEW — `PLAN_A_AG_Prompts_RetryCaps.md` (BATON NET-763)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)  
**Date:** 2026-11-04 15:46 ET  
**Baton:** `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-763_ARGON_REVIEW_PLAN_A_AG_Prompts_RetryCaps_20261104-1040.md`  
**Target Plan:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md` (91 lines)  
**Mode:** PLAN REVIEW ONLY (`NO EXECUTE` — `main` stays `9f04550a`, live site untouched, Stripe OFF, no spend)  
**Verdict:** **PASS — `96 / 100` (0 Blocking Must-Fixes; 2 Non-Blocking Advisories)**

---

## 1. Executive Summary & Scoring Breakdown

`PLAN_A_AG_Prompts_RetryCaps.md` translates Google's *"Startup guide to AI agents"* recommendations on intent-level ("Goldilocks") prompts (p.22) and capped loop agents (p.16–17) into a zero-code, pre-launch process pilot with a 25-line baton template, explicit attempt counters (`ATTEMPT: _ of 10`, `WRITER TRY: _ of 4`), an internal retry cap (`max 3 internal retries`), and a 10-workday FIN OPS billing baseline followed by a 5-workday pilot (approved by Eric at `PLAN_A_AG_Prompts_RetryCaps.md:90-91`).

| Category | Weight | Score | Notes |
|---|---|---|---|
| **1. Scope, Safety & Zero-Spend Boundaries** | 25 | **25 / 25** | Explicitly process-only; forbids code, Firestore, deploy, or model/billing changes (`lines 17–21`). Rejects autonomous timer loops that conflict with standing rules (`line 21`). |
| **2. Audit of Unverified `$44/day` & `$9/day` Claims (`NET-763` Mandate)** | 25 | **23 / 25** | `lines 9` and `73` properly caveat `$44` and `$9` as unverified, but `lines 6, 57, 66` tie pilot targets (`Down from ~$44, heading to $9`; `goal: under $25 in the pilot`) to those unverified numbers. Flagged below with a relative-percentage target recommendation. |
| **3. Prompt Template & Retry Cap Design** | 25 | **23 / 25** | Clean 25-line template (`lines 30–41`) and attempt counter (`lines 23–28`). Minor reconciliation needed between `line 28` (`capped at 3`) and `00_BATON_RULES.md:12` (`TWO STRIKES`). |
| **4. PII Guardrails & Review Chain** | 25 | **25 / 25** | Strict zero-PII rule (`line 79`), human approval gate (`line 80`), and full review chain (`line 83`). |
| **TOTAL** | **100** | **96 / 100** | **PASS (Ready for GB CoS 95+ -> SAG -> Eric YES)** |

---

## 2. Verbatim File Quotes Checked in This Turn

### 2.1 `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-763_ARGON_REVIEW_PLAN_A_AG_Prompts_RetryCaps_20261104-1040.md:1-5`
```markdown
1: # BATON NET-763 - ARGON: review INBOX\PLAN_A_AG_Prompts_RetryCaps.md (PLAN ONLY, ideas from Google's 'Startup guide to AI agents')
2: Filed by Antigravity Desk, 4 Nov 2026 10:40 AM ET, on GB CoS's request. MD5 D60919A4DFEF180E66F8E0AB7AC4CBFC. Eric's 4 Nov 10:36 AM decisions are appended to Plans A, B and D.
3: The $44/day AG burn and the $9 target are UNVERIFIED; flag any claim that relies on them.
4: Write INBOX\ARGON_REVIEW_PLAN_A_AG_Prompts_RetryCaps.md with a score out of 100 and any must-fixes.
5: Chain: Argon, then GB CoS 95+, then SAG, then Eric's typed YES. NOTHING EXECUTES. Main stays 9f04550a. The live site stays untouched. Stripe stays OFF. No spend.
```

### 2.2 Claims Relying on the Unverified `$44/day` Burn and `$9` Target (`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md`)

Per `BATON_NET-763:3` (*"The $44/day AG burn and the $9 target are UNVERIFIED; flag any claim that relies on them"*), every reference in `PLAN_A_AG_Prompts_RetryCaps.md` is quoted verbatim below:

* **`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md:5-9`**:
```markdown
5: ## Goal
6: Cut AG's cost from about $44 per workday toward the $9 target by:
7: 1. sending AG short prompts that state a goal instead of long, rigid ones, and
8: 2. enforcing our retry rule as a hard stop.
9: The $44 and $9 figures come from the brief. They have not been re-checked against billing.
```
* **`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md:54-62`**:
```markdown
54: ## How to measure cost before and after
55: | Measure | Where it comes from | Target |
56: |---|---|---|
57: | AG $ per workday | FIN OPS billing view (same source both periods) | Down from ~$44, heading to $9 |
58: | Average prompt length | Desk log of characters sent | Down by at least 50% |
59: | Attempts per task | Counter in the baton file | Down, or steady |
60: | Tasks that hit 10 attempts | Counter | Report each one to Eric |
61: | Quality | Field Tester / Argon pass rate | Not worse than the baseline |
62: Compare averages per workday. Ignore days with unusual one-off jobs, and list which days were left out.
```
* **`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md:64-67`**:
```markdown
64: ## Success criteria
65: - Every AG task in the pilot uses the template and shows its attempt counter.
66: - AG's cost per workday falls by a meaningful amount (goal: under $25 in the pilot, then toward $9), and the pass rate is not lower.
67: - No task goes past 10 attempts without Eric being told.
```
* **`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md:72-73`**:
```markdown
72: ## Cost estimate
73: $0 to set up. The pilot costs AG's normal daily spend. Savings are UNVERIFIED until the baseline is measured.
```

### 2.3 Retry Cap Rules & Eric's Decision (`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_A_AG_Prompts_RetryCaps.md:23-41, 85-91`)
```markdown
23: ## The retry rule (unchanged, now enforced on paper)
24: - Each task has an attempt counter, starting at 1.
25: - After 4 failed tries by the same writer, that writer is replaced. The counter keeps going; it does not reset.
26: - At 10 total attempts, all work stops. GB CoS notifies Eric and breaks the task into smaller pieces, and each piece starts at attempt 1.
27: - What counts as one attempt: one submitted plan/fix that a reviewer (Argon, GB CoS, SAG or Field Tester) sends back.
28: - AG's own internal re-runs inside a single attempt are capped at 3. If it hits 3, it stops and reports "BLOCKED" with the reason, rather than looping (this mirrors the guide's capped Loop agents, p.16–17).
29: 
30: ## Prompt template (target: 25 lines or fewer)
31: ```
32: TASK ID: NET-___   ATTEMPT: _ of 10   WRITER TRY: _ of 4
33: GOAL (1–2 sentences): what "done" looks like for the user.
34: WHY: one line.
35: INPUTS: file paths only (no pasted file contents).
36: MUST: up to 5 hard rules (e.g. no PII, no deploy, no Firestore writes without Eric's YES).
37: MUST NOT: up to 3 items.
38: DONE WHEN: up to 3 checks a reviewer can verify.
39: OUTPUT: one file at <path>, plus a status line: DONE / BLOCKED (reason) / NEEDS-DECISION (question).
40: LIMITS: max 3 internal retries; stop at 3 AM; spend cap $__.
41: ```
```
```markdown
85: ## Open questions for Eric
86: 1. Is a 5-workday pilot OK, starting after your YES?
87: 2. Is a cap of 3 internal re-runs per attempt OK?
88: 
89: 
90: ## Eric decisions (4 Nov 2026, 10:36 AM ET)
91: - 5-workday pilot, cap of 3 re-runs per attempt: YES.
```

### 2.4 Existing Standing Rule Comparison (`BETA TEST\Grok Bot\8 OCT 26\BATONS\00_BATON_RULES.md:9-13`)
```markdown
9: ## Rule 8 - QUOTA SAVER (Eric, 14 Oct 2026 3:57 PM)
10: 1. ONE JOB AT A TIME. Work one baton until it reaches a scored checkpoint. No parallel tracks or background builds. Order: P7 fix (per NET-099/100), then P5, then P6 rerun, P4, P8, P10, P9.
11: 2. READ ONLY RECENT RADIO. Old messages are in RADIO NET\ARCHIVE. Don't open ARCHIVE unless a current message names a file there. On each wake, read only the files that are new since your last ACK.
12: 4. TWO STRIKES. If a build, deploy, test run or command fails twice in a row for the same reason, STOP. File a NET message with the error and your best guess, and wait. No retry loops.
```

---

## 3. Must-Fixes & Advisories

* **Blocking Must-Fixes:** **None (0).**
* **Non-Blocking Advisories (2):**
  1. **Flagged Unverified Dollar Claims (`lines 6, 57, 66`):** While `lines 9` and `73` explicitly state that `$44/day` and `$9/day` have not been verified against billing, `line 57` (`Down from ~$44, heading to $9`) and `line 66` (`goal: under $25 in the pilot, then toward $9`) use fixed dollar thresholds derived from the unverified `$44/day` figure. Once FIN OPS completes Step 1 (10-workday baseline pull from billing at `line 48`), Desk/FIN OPS should evaluate pilot success against **both** the relative percentage reduction from the measured Step 1 baseline (e.g. `>= 40% reduction from measured baseline $/workday`) and the dollar target, so the pilot metric remains valid regardless of whether actual baseline spend is above or below `$44/workday`.
  2. **Standing-Rules Alignment in Step 2 (`line 28, 40, 91` vs. `00_BATON_RULES.md:12`):** When Desk drafts the standing-rules file in Step 2 (`line 49`), explicitly state how `PLAN_A` (`max 3 internal retries` per attempt, approved by Eric at `line 91`) interacts with `00_BATON_RULES.md:12` (`TWO STRIKES. If a build, deploy, test run or command fails twice in a row for the same reason, STOP`): i.e., max 3 internal retries total per attempt, with an immediate stop at 2 strikes if a command fails twice in a row for the *exact same reason*.
