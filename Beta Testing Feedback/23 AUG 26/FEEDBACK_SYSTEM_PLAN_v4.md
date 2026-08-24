# Numista.AI — Antigravity Feedback System: Implementation Plan v4
**Date:** 23 AUG 2026
**Tasker:** Beta Testing Feedback — Feedback System Redesign
**Status:** NOT EXECUTION-READY. Founder decides after next Gemini + Grok pass.
  Write-path is locked (Option A, Admin SDK). Scope is locked (3 files). No open design questions.

> **REVIEWER GROUND RULE — Execution Gate:**
> Execution-ready status is set by the founder only, never by an AI reviewer.
> Do NOT suggest changing the Status line to EXECUTION-READY in any review round.
> This is a standing project rule (Rule 6) that travels with every version of this plan.
> Raising it as a Must-Fix will result in REJECTED in the decision matrix.

---

## Reviewer Ground Rules (Permanent — Apply to All Rounds)

The following items are permanently closed or permanently out of scope.
Raising them as Must-Fix or Adopt in any future round will result in REJECTED.

**Out of scope for this plan (do not re-raise):**
- patch_beta_13aug_metadata.py — (does not exist in repo; not in scope)
- _LegislationTab widget — (UI refactor; separate plan required)
- Sheldon/Morgan grade hover tooltips — (UI feature; separate plan required)
- prod_account_audit_repair.py — (separate concern; not in scope)
- Playwright DOM readiness checks — (E2E concern; not in scope)
- Optional .eml parser — (scope creep; permanently rejected across all rounds)
- Any mobile (Flutter) screen or widget — (Desktop Web only; non-negotiable)

**tier_gatekeeper.py:** Listed as a protected file even though it does not currently exist
in the repo. Protection is a write-prohibition rule, not a file-existence guarantee.
It applies if and when the file is created in any future session. Do not flag its absence
as a contradiction or error.

**Execution gate:** Execution-ready status is set by the founder only (Rule 6).
Do not suggest changing the Status header to EXECUTION-READY.

---

## Prior Rounds Summary (Closed Items — Do Not Re-Raise)

| Round | Item | Resolution |
|-------|------|------------|
| v1→v2 | Write-path underspecified (callable vs Admin SDK) | RESOLVED: Option A (Admin SDK direct update in transaction). Founder confirmed. |
| v1→v2 | Idempotency / race protection missing | RESOLVED: Transaction asserts status==OPEN; SKIP message if already changed. |
| v1→v2 | Credentials incomplete | RESOLVED: ADC → key file → fail-closed chain. Key never logged. |
| v1→v2 | Fallback-form null safety | RESOLVED: All optional fields .get() with None default; renders as N/A. |
| v1→v2 | No audit trail | RESOLVED: triaged_by, triaged_at, triaged_by_agent stamped atomically in same transaction. |
| v2→v3 | Residual conflict language in header/Q1 | RESOLVED: Header neutral; Q1 removed; Option A is single source of truth in Section 2. |
| v2→v3 | --triage CLI contract incomplete | RESOLVED: Full contract in Deliverable 1 (flags, mutex, validation, exit codes, output lines). |
| v2→v3 | Non-race transaction failure modes | RESOLVED: PermissionDenied, Unavailable, missing status field, unhandled exception — all exit 1 with non-PII message. |
| v3→v4 | Gemini: mark plan EXECUTION-READY | REJECTED permanently: Rule 6 prohibits this. See Reviewer Ground Rules above. |
| v3→v4 | Gemini: tier_gatekeeper.py must-fix | NOTED as already done in v3; clarified in Reviewer Ground Rules above. |
| v3→v4 | --triage empty/malformed DOC_ID | RESOLVED: Two new validation cases added (empty string, non-hex/wrong-length). |
| v3→v4 | Verification step 4 risked live data | RESOLVED: Step 4 uses synthetic doc only; live items explicitly excluded by name. |

---

## Section 1 — Decision Matrix (v3 Reviews)

| Source | Suggestion | Adopted / Modified / Rejected | Why |
|--------|-----------|-------------------------------|-----|
| Gemini v3 | Adopt all three deliverables | ADOPTED | Consistent across all rounds; no change. |
| Gemini v3 | Adopt write-path Option A | ADOPTED | Locked by founder in prior round; no change. |
| Gemini v3 | Reject .eml parser | ADOPTED (reject) | Consistent across all rounds; no change. |
| Gemini v3 Must-Fix #1 | Change header to EXECUTION-READY | REJECTED | Rule 6 explicitly prohibits this. "Do not mark the plan execution-ready. I will decide." Gemini's contradiction claim (header vs. Q1) is also false: process status and design resolution are different things. |
| Gemini v3 Must-Fix #2 | Validate --triage DOC_ID for empty or malformed string | ADOPTED | v3 covered missing DOC_ID argument but not empty string "" or non-hex input. Proof below. |
| Gemini v3 Must-Fix #3 | tier_gatekeeper.py listed as protected | NOTED — ALREADY DONE | v3 Section 7 already lists it with the no-action note. No change needed. |
| Grok v3 Must-Fix #1 | Fix header/proof inconsistency — "Awaiting" language in header vs. proof claim of no "Awaiting" | ADOPTED AS DOCUMENTATION HYGIENE ONLY | Header updated to neutral language that is accurate: write-path is decided, scope is locked, founder approval is pending. Does not mark plan execution-ready. Proof below. |
| Grok v3 Must-Fix #2 | Verification step 4 risks live production data | ADOPTED | v3 said "against a test doc or one of the two 23-Aug items." That allows marking real OPEN data during automated testing before founder confirmation. Proof below. |
| Grok v3 Push-back | No material architectural push-backs | N/A | Grok confirmed "none material." |

---

## Section 2 — Write-Path: Option A (Locked, Final)

Founder selected Option A on 23 AUG 2026. This section is the single source of truth.
No other section uses provisional or conflict language about the write-path.
The ADMIN_RESOLVE callable is never invoked by this script.

Write mechanism (unchanged from v3):

  @firestore.transactional
  def triage_in_transaction(transaction, doc_ref, doc_id_short):
      snapshot = doc_ref.get(transaction=transaction)
      if not snapshot.exists:
          return ("MISSING", None)
      current = snapshot.get("status")
      if current != "OPEN":
          return ("SKIP", current)
      transaction.update(doc_ref, {
          "status": "TRIAGED",
          "triaged_by": "antigravity-agent",
          "triaged_at": firestore.SERVER_TIMESTAMP,
          "triaged_by_agent": True,
      })
      return ("OK", "TRIAGED")

Failure handling (unchanged from v3 — all modes fail-closed):
  MISSING     → print "ERROR: {short_id} — document not found.", exit 1
  SKIP        → print "SKIP: {short_id} — status is {current}, not OPEN. No write made.", exit 0
  PermissionDenied → print "ERROR: Permission denied. Check service account roles.", exit 1
  Unavailable / network → print "ERROR: Firestore unreachable.", exit 1
  status field absent → print "ERROR: {short_id} — missing status field. Manual review required.", exit 1
  Unhandled exception → print "ERROR: Unexpected failure: {type(e).__name__}. No write made.", exit 1
  In all error cases: no partial write, no .eml fallback, no alternative auth path.

---

## Section 3 — Proof: Old vs New (v3 Must-Fixes)

### Gemini v3 Must-Fix #1 — REJECTED (Rule 6)

OLD (v3 header):
  "Status: NOT EXECUTION-READY. Awaiting founder resolution of one write-path conflict,
   then next Gemini + Grok pass."

The header in v4 reads:
  "Status: NOT EXECUTION-READY. Founder decides after next Gemini + Grok pass.
   Write-path is locked (Option A, Admin SDK). Scope is locked (3 files).
   No open design questions."

This is accurate, neutral, and does not violate Rule 6. I will not write EXECUTION-READY
in any version of this plan. Gemini's suggested text is refused.

### Gemini v3 Must-Fix #2 — --triage DOC_ID validation for empty/malformed string

OLD (v3 Section 3, CLI contract):
  "--triage with no DOC_ID: print 'ERROR: --triage requires a document ID.', exit 1."
  (Empty string "" and non-hex inputs not covered.)

NEW (v4 Deliverable 1, CLI contract):
  "--triage DOC_ID validation:
    - No DOC_ID supplied: print 'ERROR: --triage requires a document ID.', exit 1.
    - DOC_ID is empty string '': print 'ERROR: --triage document ID cannot be empty.', exit 1.
    - DOC_ID contains characters outside [a-zA-Z0-9_-] or length outside [8, 128]:
      print 'ERROR: --triage document ID appears malformed. Expected alphanumeric Firestore ID.', exit 1.
      (Firestore auto-IDs are base62; SHA-256 MORGAN IDs are lowercase hex subset — both pass.)
    - Valid format: proceed to credential check, then Firestore transaction."

### Grok v3 Must-Fix #1 — Header/proof consistency (documentation hygiene only)

OLD (v3 header):
  "Status: NOT EXECUTION-READY. Awaiting founder resolution of one write-path conflict,
   then next Gemini + Grok pass."

OLD (v3 Section 3, Grok/Gemini Must-Fix #1 proof):
  "NEW (v3): ... (No conflict reference. Option A locked in Section 2.
   No 'AWAITING' language anywhere in document.)"

These were inconsistent — the header still contained "Awaiting" while the proof claimed
it was absent.

NEW (v4 header):
  "Status: NOT EXECUTION-READY. Founder decides after next Gemini + Grok pass.
   Write-path is locked (Option A, Admin SDK). Scope is locked (3 files).
   No open design questions."

The header no longer contains "Awaiting." The proof claim is now accurate.
The plan is not marked execution-ready.

### Grok v3 Must-Fix #2 — Verification step 4 safety

OLD (v3 Section 9, step 4):
  "Triage write test (against a test doc or one of the two 23-Aug items):
   python numista_qa_runner/fetch_open_feedback.py --triage {doc_id}
   Expected: 'TRIAGED: {short_id} | doc_id=... | new_status=TRIAGED | triaged_at=...'
   Expected: Firestore doc now has status=TRIAGED, triaged_by=antigravity-agent..."

The phrase "or one of the two 23-Aug items" allows an automated verification step
to mark live OPEN production data as TRIAGED before the founder has seen it in chat.

NEW (v4 Section 9, step 4):
  "Triage write test (synthetic document only):
   Before running this step, create a synthetic test document in beta_feedback with
   status='OPEN' and a known test_doc_id (e.g. by running the callable with a test
   fixture, or by manual Firestore console insert). Then:
     python numista_qa_runner/fetch_open_feedback.py --triage {test_doc_id}
   Expected: 'TRIAGED: {short_id} | doc_id=... | new_status=TRIAGED | triaged_at=...'
   The two live items (f724a3ae..., 253599ed...) are NOT used in this verification step.
   They are triaged only via the confirmed Step 4 workflow action in Section 6, after
   the founder has seen each item in chat and given explicit per-item confirmation."

---

## Section 4 — Deliverable 1: fetch_open_feedback.py [NEW]

Scope: numista_qa_runner/fetch_open_feedback.py

CLI contract (updated from v3 with empty/malformed DOC_ID validation):

  USAGE:
    python numista_qa_runner/fetch_open_feedback.py [OPTIONS]

  OPTIONS:
    (no flags)          Read mode. Fetch and display all OPEN feedback. Exit 0.
    --date YYYY-MM-DD   Filter by submission date. Read mode only.
    --limit N           Max documents to return (default 50). Read mode only.
    --dry-run           Show what would be triaged. Zero writes. Exit 0.
                        Mutually exclusive with --triage.
    --triage DOC_ID     Triage mode. Write TRIAGED + audit fields for one doc.
                        Mutually exclusive with --dry-run, --date, --limit.
    --verbose           Show full UID and full transcript (no truncation).

  MUTUAL EXCLUSION:
    --triage + --dry-run: print "ERROR: --triage and --dry-run are mutually exclusive.", exit 1.

  ARGUMENT VALIDATION (updated):
    --triage with no DOC_ID: "ERROR: --triage requires a document ID.", exit 1.
    --triage with DOC_ID = "": "ERROR: --triage document ID cannot be empty.", exit 1.
    --triage with DOC_ID outside [a-zA-Z0-9_-] or length outside [8, 128]:
      "ERROR: --triage document ID appears malformed. Expected alphanumeric Firestore ID.", exit 1.
    --date with invalid format: "ERROR: --date must be YYYY-MM-DD.", exit 1.
    --limit non-integer: "ERROR: --limit must be a positive integer.", exit 1.

  EXIT CODES:
    0 — success (read completed, inbox zero, or SKIP on already-triaged doc)
    1 — infrastructure failure, argument error, or missing document

  TRIAGE SUCCESS OUTPUT:
    "TRIAGED: {short_id} | doc_id={full_id} | new_status=TRIAGED | triaged_at={timestamp}"

  TRIAGE SKIP OUTPUT:
    "SKIP: {short_id} — status is {current_status}, not OPEN. No write made."

Read mode per-item report block (unchanged from v3):
  Line 1:  [{i}] {feedback_id[:8]}... | {issue_type} | {severity_estimate} | {intake_method}
  Line 2:  Date:      {created_at formatted YYYY-MM-DD HH:MM UTC}
  Line 3:  Page:      {page_title} ({route})
  Line 4:  User:      {user_id[:8]}...  (full on --verbose)
  Line 5:  Message:   {first user transcript message, 200 chars, "N/A" if absent}
  Line 6:  MORGAN:    {morgan_summary, 300 chars, "N/A" if null}
  Line 7:  Root Cause:{ai_analysis.root_cause_hypothesis, "N/A" if absent}
  Line 8:  Fix Area:  {ai_analysis.suggested_fix_area, "N/A" if absent}
  Line 9:  Effort:    {ai_analysis.estimated_effort, "N/A" if absent}
  Line 10: Full ID:   {feedback_id}

  Transcript truncation at 500 chars: append "(truncated — full doc: {feedback_id})"
  Inbox zero: "Inbox zero — no OPEN feedback found." Exit 0.

Null-safety: every field access uses .get() with default None. None renders as "N/A".
  No KeyError, AttributeError, or TypeError from any missing Firestore field.
  Validated against f724a3ae... and 253599ed... (both fallback_form, morgan_summary=None,
  ai_analysis absent).

Output field names (all snake_case):
  feedback_id, created_at, issue_type, severity_estimate, page_title, route,
  user_id, intake_method, morgan_summary, ai_analysis, full_transcript,
  status, triaged_by, triaged_at, triaged_by_agent.

Credentials (unchanged from v3):
  1. GOOGLE_APPLICATION_CREDENTIALS set → ADC
  2. numista_backend/serviceAccountKey.json present → use file
  3. Neither → "ERROR: No credentials found...", exit 1.
  Key never printed or logged. File confirmed in .gitignore.
  Script is operator-only. Must not be exposed to untrusted sessions.

---

## Section 5 — Deliverable 2: daily_feedback_test_miner.py [MODIFY — 1 line]

File: numista_qa_runner/daily_feedback_test_miner.py

OLD:
  BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING"

NEW:
  BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Beta Testing Feedback"

No other changes to this file.

---

## Section 6 — Deliverable 3: .agents/FEEDBACK_WORKFLOW.md [NEW]

6-step sequence (unchanged from v3):

  Step 1: Run: python numista_qa_runner/fetch_open_feedback.py [--date YYYY-MM-DD] [--limit N]
  Step 2: Display the full report in chat (summary table + per-item detail blocks)
  Step 3: For each OPEN item, state the proposed action to the founder and WAIT for confirmation
  Step 4: On founder confirmation only — run: python numista_qa_runner/fetch_open_feedback.py --triage {doc_id}
  Step 5: Echo the TRIAGED confirmation line including triaged_at timestamp
  Step 6: If a fix is needed — create an implementation plan in this session; do not proceed to RESOLVED

Hard rules (unchanged from v3):
  - Agent NEVER runs --triage without explicit per-item founder confirmation
  - Agent NEVER marks status RESOLVED — only TRIAGED. RESOLVED is set by founder after fix verification.
  - Agent NEVER falls back to .eml parsing on any failure
  - Agent NEVER uses the ADMIN_RESOLVE callable — Admin SDK only
  - Agent NEVER combines --triage and --dry-run in the same invocation
  - On any infrastructure error: print the error line, stop, do not guess or substitute

---

## Section 7 — What Is Not Changing

  - MORGAN in-app interview system
  - feedback_callable_route.py
  - feedbackIntelligence.js
  - admin_feedback_screen.dart
  - passport_pdf_generator.py (protected)
  - numista_bq_loader_job (protected)
  - tier_gatekeeper.py (protected — file does not currently exist in repo;
    protection means this plan's scripts will not write to, import from, or modify it)

---

## Section 8 — Files To Be Created / Modified

| File | Action | Blocked? |
|------|--------|---------|
| numista_qa_runner/fetch_open_feedback.py | CREATE | No |
| numista_qa_runner/daily_feedback_test_miner.py | MODIFY (1 line) | No |
| .agents/FEEDBACK_WORKFLOW.md | CREATE | No |

---

## Section 9 — Verification Plan

1. Read mode test:
   python numista_qa_runner/fetch_open_feedback.py --date 2026-08-23
   Expected: 2 OPEN items (f724a3ae..., 253599ed...), all absent fields show "N/A", no crash.

2. Dry-run test:
   python numista_qa_runner/fetch_open_feedback.py --dry-run
   Expected: proposed triage list shown, zero Firestore writes, exit 0.

3. Mutual exclusion test:
   python numista_qa_runner/fetch_open_feedback.py --triage abc123 --dry-run
   Expected: "ERROR: --triage and --dry-run are mutually exclusive." exit 1.

4. Triage write test (SYNTHETIC DOCUMENT ONLY — not live items):
   Before this step, insert a synthetic test document in beta_feedback via Firestore
   console or fixture: { status: "OPEN", feedback_id: "test0000...", ... }
   Then run: python numista_qa_runner/fetch_open_feedback.py --triage {test_doc_id}
   Expected: "TRIAGED: test0000... | doc_id=... | new_status=TRIAGED | triaged_at=..."
   Expected: Firestore doc has status=TRIAGED, triaged_by=antigravity-agent,
             triaged_by_agent=True, triaged_at set.
   NOTE: Live items f724a3ae... and 253599ed... are NOT touched by this step.
         They are only triaged after founder per-item confirmation in Section 6, Step 4.

5. Idempotency test (re-run --triage on the same synthetic doc):
   python numista_qa_runner/fetch_open_feedback.py --triage {same_test_doc_id}
   Expected: "SKIP: test0000... — status is TRIAGED, not OPEN. No write made." exit 0.

6. Malformed DOC_ID tests:
   python numista_qa_runner/fetch_open_feedback.py --triage ""
   Expected: "ERROR: --triage document ID cannot be empty." exit 1.
   python numista_qa_runner/fetch_open_feedback.py --triage "not valid!!"
   Expected: "ERROR: --triage document ID appears malformed. Expected alphanumeric Firestore ID." exit 1.

7. Credential fail-closed test:
   Run with no env var and serviceAccountKey.json absent.
   Expected: "ERROR: No credentials found..." exit 1.

8. Inbox-zero test:
   Run against a date with no OPEN items.
   Expected: "Inbox zero — no OPEN feedback found." exit 0.

9. Miner path test:
   python numista_qa_runner/daily_feedback_test_miner.py
   Expected: scans Beta Testing Feedback\23 AUG 26\ (not the old path).

10. Git hygiene:
    git status: only 3 files modified/created.
    serviceAccountKey.json absent from staged files.

11. Push:
    git pull --rebase origin dev
    git push origin dev

---

## Section 10 — Open Questions

None. All design questions resolved in prior rounds.
  Write-path: Option A, Admin SDK, Section 2.
  TRIAGED timing: immediately on founder confirmation.
  .eml parser: not implemented.
