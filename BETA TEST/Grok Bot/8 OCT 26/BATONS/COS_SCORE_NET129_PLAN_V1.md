# COS SCORE — NET-129 PLAN V1 (Manual Entry / Checklist / Program Names)
Scorer: Grok CoS | 2026-10-14 ~23:42 ET | Reviewed: PLAN_NET129_MANUAL-ENTRY-CHECKLIST-PROGRAM-NAMES_V1.md + AG NET-130 (plan-ready) + code spot-check `program_model.dart:173-175`
Verdict: **PLAN GO.** Code stays **WAIT** until P7 full PASS (preview + UX Designer + Field Tester) per Rule 8 and the plan's own queue line.

| # | Item | Score | Notes |
|---|------|-------|-------|
| 1 | Bug 1 root cause (coinDoc omits Notes/Purchase Date; no reset; weak validation) | **PASS** | Matches live symptoms from NET-129. Storage Location present-but-empty is a real silent-fail risk — confirm AddCoinManualForm returns it. |
| 2 | Bug 2 checklist missing fields + extra copies | **PASS** | Align Condition with Ungraded (P7 already chose this). Extra copies = Quantity on confirm (see Q2). |
| 3 | Bug 3 program-name split + systemic audit | **PASS** | Canonical confirmed below. Double-space "Presidential  Coin Program" is legacy junk — normalize away on Eric's YES only. Audit EVERY Coin Program write path (systemic rule). |
| 4 | Scope / limits (dev only, no deploy, no migration without YES) | **PASS** | Keep. |
| 5 | Tests planned | **PASS** | Add: Storage Location round-trip; Condition maps Raw→Ungraded; one systemic program-name constant test. |
| 6 | Queue discipline (after P7 gates) | **PASS** | Do not start code tonight. Stand down coding NET-129 until P7 gates clear. |

## Answers to open questions
**Q1 — Canonical program name:** Use **`Presidential Dollars`**. Confirmed in `program_model.dart:173-175` (alias matches `presidential dollars` → any DB string containing `presidential`). Normalize `"Presidential  Coin Program"` (and any other Presidential* variant) to that exact string. Systemic: list every other program with multiple stored names in EXECUTE_DONE; fix code paths in the same PR; data migration still needs Eric's typed YES.

**Q2 — Extra copies:** Quantity field on the checklist confirm card (default 1) is enough for V1. If the slot is already owned, prefer the same plain confirm card pattern as P7 V6/V7 add-another (Ungraded, no fake grader/cert). No separate "already owned" wizard in this PR.

**Q3 — Purchase Date:** Prefer a **date picker** (older-user friendly; avoids Monroe-style field bleed). Store ISO `YYYY-MM-DD` text. Free-text only if the picker is blocked by time — then validate `YYYY-MM-DD` before write.

**Q4 — Migration:** Stand-alone migration script (dry-run CSV first, then `--apply` only on Eric's typed YES) is the right shape. No auto backend migration route.

## Orders for AG (when P7 gates clear — not tonight)
1. Code per Plan.v1 + answers above. Dev only.
2. Gemini BUILD review + flutter tests green before GROKCOS score.
3. No deploy / no Firestore migration without Eric's typed YES.
4. Reminder: hard AG stand-down by ~3 AM ET so quota refreshes by 9 AM.

P7 remains GROKCOS_OVER AWAITING PREVIEW (AM Firebase). Overnight quiet — Eric not pinged.
