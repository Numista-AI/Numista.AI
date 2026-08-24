# Numista.AI — Antigravity Feedback System: Implementation Plan
**Date:** 23 AUG 2026
**Tasker:** Beta Testing Feedback — Feedback System Redesign
**Status:** Awaiting Founder Approval

---

## Problem Statement

Beta testers submit feedback via the MORGAN in-app interview or the fallback form. Firebase automatically processes and stores each submission in Firestore (`beta_feedback` collection) and sends an alert email to `eric@numista.ai`.

**The gap:** Antigravity cannot currently read, triage, or act on that feedback without the founder manually copy-pasting email content. The `.eml` files saved from Gmail are outbound notification emails — the real data is already in Firestore. We need Antigravity to go directly to the source.

---

## Design Decisions (Confirmed in /grill-me session)

| Question | Decision |
|---|---|
| Skip email pipeline? | YES — data is already in Firestore |
| Source of truth | Firestore `beta_feedback` collection |
| Default filter | `status == "OPEN"` only |
| Invocation | On demand — founder says "check feedback" |
| Auth method | Firebase Admin SDK + `serviceAccountKey.json` (existing pattern) |
| Output | Summary table + full transcript per item |
| Post-review actions | Mark as TRIAGED + create fix plan — all in same session |

---

## Proposed Changes

### Deliverable 1 — `numista_qa_runner/fetch_open_feedback.py` [NEW]

A standalone Python script that:

1. Initializes Firebase Admin SDK using `numista_backend/serviceAccountKey.json`
2. Queries Firestore `beta_feedback` collection where `status == "OPEN"`, ordered by `created_at` descending
3. Prints a formatted report to stdout with:
   - **Summary table** — Feedback ID (short), date, issue type, severity, page, user ID, intake method
   - **Full detail** per item — user message/transcript, MORGAN summary, AI analysis (root cause, suggested fix area, effort)
4. Accepts an optional `--limit N` flag (default: 50)
5. Accepts an optional `--date YYYY-MM-DD` flag to filter by a specific day

**Antigravity usage:** Run this script, read the output in chat, then discuss and act.

**Key fields extracted per document:**
- feedback_id       → short 8-char prefix for reference
- created_at        → formatted local time
- issue_type        → BUG | FEATURE | UX | PRAISE | CONFUSION | DATA_INTEGRITY | OTHER
- severity_estimate → LOW | MEDIUM | HIGH | CRITICAL
- page_title/route  → where in the app
- intake_method     → morgan_interview | fallback_form
- full_transcript   → all user messages, formatted
- morgan_summary    → MORGAN plain-English summary
- ai_analysis       → root_cause_hypothesis, suggested_fix_area, estimated_effort, pattern_tags
- status            → always OPEN (filtered)

---

### Deliverable 2 — Fix `daily_feedback_test_miner.py` [MODIFY]

File: numista_qa_runner/daily_feedback_test_miner.py

Current (wrong):
  BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING"

Fix:
  BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Beta Testing Feedback"

This makes the miner pick up .docx, .md, and .txt files from date-named subfolders
like "23 AUG 26\" — which is already the convention in use.

---

### Deliverable 3 — Antigravity Workflow Protocol [NEW]

File: .agents/FEEDBACK_WORKFLOW.md

Defines how Antigravity handles feedback sessions consistently across all sessions.

When the founder says "check feedback", "read feedback", or "what's new in beta feedback":
  1. Run: python numista_qa_runner/fetch_open_feedback.py
  2. Parse and display output as a formatted report in chat
  3. For each item, offer:
     (a) Triage it — mark TRIAGED or RESOLVED via ADMIN_RESOLVE callable
     (b) Fix it — create an implementation plan and push to dev
  4. After any triage action, confirm the Firestore status update was accepted

---

## Files To Be Created / Modified

| File                                              | Action | Description                              |
|---------------------------------------------------|--------|------------------------------------------|
| numista_qa_runner/fetch_open_feedback.py          | CREATE | Firestore open feedback reader script    |
| numista_qa_runner/daily_feedback_test_miner.py    | MODIFY | Fix BASE_FEEDBACK_DIR path (1 line)      |
| .agents/FEEDBACK_WORKFLOW.md                      | CREATE | Antigravity session protocol for feedback|

---

## What Is NOT Changing

- The MORGAN in-app interview system — no changes
- feedback_callable_route.py — no changes
- feedbackIntelligence.js (Firebase alert emails) — no changes
- admin_feedback_screen.dart — no changes
- The Beta Testing Feedback\{date}\ folder — still correct place to save .eml files
  as reference records, but Antigravity will read Firestore instead of parsing them

---

## Verification Plan

1. Script test: Run `python numista_qa_runner/fetch_open_feedback.py`
   - Confirm it connects to Firestore
   - Confirm it returns at least the 2 open MEDIUM Bug Report submissions from today
     (Feedback IDs: f724a3ae... and 253599ed...)
2. Miner path test: Run `python numista_qa_runner/daily_feedback_test_miner.py`
   - Confirm it scans Beta Testing Feedback\23 AUG 26\
3. No regressions: `git status` confirms only 3 target files are modified
4. Push: `git pull --rebase origin dev && git push origin dev`

---

## Open Questions for Founder Review

Q1 — Credentials path:
  The script will use numista_backend/serviceAccountKey.json. Do you want it to also
  support Application Default Credentials (ADC) as a fallback, or always use the
  service account key file explicitly?

Q2 — TRIAGED vs RESOLVED:
  After you read a feedback item and decide to fix it, should Antigravity mark it
  TRIAGED (work in progress) or leave it OPEN until the fix is confirmed?
  RECOMMENDATION: Mark TRIAGED immediately so the inbox stays clean.

Q3 — .eml parsing (optional):
  Do you want Antigravity to also be able to parse .eml files from the folder as a
  backup (for cases where Firestore is unreachable)? This is optional and adds complexity.
