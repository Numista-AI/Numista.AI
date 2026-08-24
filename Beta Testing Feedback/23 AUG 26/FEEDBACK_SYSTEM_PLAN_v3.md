# Numista.AI — Antigravity Feedback System: Implementation Plan v3
**Date:** 23 AUG 2026
**Tasker:** Beta Testing Feedback — Feedback System Redesign
**Status:** NOT EXECUTION-READY. Awaiting founder decision after next Gemini + Grok pass.

---

## Section 1 — Decision Matrix (v2 Reviews)

| Source | Suggestion | Adopted / Modified / Rejected | Why |
|--------|-----------|-------------------------------|-----|
| Gemini v2 | Adopt `fetch_open_feedback.py` | ADOPTED | Consistent with v1 and v2; no change. |
| Gemini v2 | Adopt `daily_feedback_test_miner.py` path fix | ADOPTED | One-line change; both reviewers agree across all rounds. |
| Gemini v2 | Adopt `.agents/FEEDBACK_WORKFLOW.md` with modification | ADOPTED | Modification already in v2 (6-step sequence, no-auto-close rule). |
| Gemini v2 | Adopt Admin SDK direct update write-path | ADOPTED | Option A, locked in v2 by founder decision. |
| Gemini v2 | Reject .eml parser | ADOPTED (reject) | Scope creep; consistent with Grok v1 and v2. |
| Gemini v2 Must-Fix #1 | Remove stale "FOUNDER MUST DECIDE" / "AWAITING" language from header and Q1 | ADOPTED | Real internal contradiction in v2 — header and Q1 were not updated when Option A was chosen. Proof below. |
| Gemini v2 Must-Fix #2 | Confirm snake_case for all output fields in fetch_open_feedback.py | ADOPTED | All output field names enumerated with explicit snake_case below. |
| Gemini v2 Must-Fix #3 | List tier_gatekeeper.py as protected regardless of local directory presence | MODIFIED | File does not exist in repo (confirmed). Listed as protected with note that absence means no action required; the protection is a write-prohibition, not a presence guarantee. |
| Grok v2 Must-Fix #1 | Purge all residual conflict language; lock Option A everywhere | ADOPTED | Same root issue as Gemini Must-Fix #1. Covered by same fix. Proof below. |
| Grok v2 Must-Fix #2 | --triage CLI contract is incomplete — define flags, mutual exclusion, validation, return values | ADOPTED | v2 referenced --triage only in the workflow prose. Full CLI contract added to Deliverable 1 below. Proof below. |
| Grok v2 Must-Fix #3 | Transaction failure modes beyond status race are underspecified | ADOPTED | v2 only covered the race case. Permission denied, network failure, and missing status field now explicitly fail-closed. Proof below. |
| Grok v2 Push-back | --triage and --dry-run must be mutually exclusive | ADOPTED | Added to CLI contract. |
| Grok v2 Push-back | Missing / non-OPEN document produces deterministic SKIP or error, not silent no-op | ADOPTED | Added to CLI contract and failure modes. |
| Grok v2 Push-back | stamped fields (triaged_by, triaged_at, triaged_by_agent) are acceptable SoR; no sub-collection needed | ADOPTED | Consistent with v2 decision; no change. |

---

## Section 2 — Write-Path: Option A (Locked, No Further Debate)

Founder selected Option A on 23 AUG 2026 during this session.

The triage write uses the Firebase Admin SDK directly. The ADMIN_RESOLVE callable
is never invoked by this script. This decision is final and appears nowhere else in
this document as open or provisional.

Write mechanism:
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

Failure handling beyond status race:
  - result == "MISSING": print "ERROR: {short_id} — document not found.", exit 1
  - result == "SKIP": print "SKIP: {short_id} — status is {current}, not OPEN. No write made.", exit 0
  - google.api_core.exceptions.PermissionDenied: print "ERROR: Permission denied. Check service account roles.", exit 1
  - google.api_core.exceptions.Unavailable / network error: print "ERROR: Firestore unreachable.", exit 1
  - snapshot exists but status field absent (KeyError / None): treat as infrastructure failure, print "ERROR: {short_id} — missing status field. Manual review required.", exit 1
  - Any unhandled exception: print "ERROR: Unexpected failure: {type(e).__name__}. No write made.", exit 1
  In all error cases: no partial write is claimed, no .eml file is read, no fallback path is taken.

---

## Section 3 — Proof: Old vs New (All v2 Must-Fixes)

### Grok/Gemini Must-Fix #1 — Residual conflict language

OLD (v2 document header):
  "Status: NOT EXECUTION-READY. Awaiting founder resolution of one write-path conflict,
   then next Gemini + Grok pass."

NEW (v3 document header):
  "Status: NOT EXECUTION-READY. Awaiting founder decision after next Gemini + Grok pass."
  (No conflict reference. Option A locked in Section 2. No "AWAITING" language anywhere in document.)

OLD (v2 Section 7 / Open Questions Q1):
  "Q1 — Write-path conflict: FOUNDER MUST DECIDE (see Section 2)"

NEW (v3):
  Q1 is removed entirely. Write-path is decided. Section 2 is the single source of truth.

OLD (v2 Decision Matrix for Grok Must-Fix #1):
  "SEE CONFLICT SECTION"

NEW (v3 Decision Matrix):
  "ADOPTED — Option A, locked in v2 by founder decision."

### Grok v2 Must-Fix #2 — --triage CLI contract

OLD (v2 Deliverable 1, triage write path line):
  "Triage write path: Admin SDK direct update in a Firestore transaction (Option A —
   see Must-Fix #1 proof in Section 3)."
  (No flag definition, no mutual exclusion, no validation, no exit codes for triage mode.)

NEW (v3 Deliverable 1 — full CLI contract):

  USAGE:
    python numista_qa_runner/fetch_open_feedback.py [OPTIONS]

  OPTIONS:
    (no flags)          Read mode. Fetch and display all OPEN feedback. Exit 0.
    --date YYYY-MM-DD   Filter by submission date. Read mode only.
    --limit N           Max documents to return (default 50). Read mode only.
    --dry-run           Show what would be triaged. Makes zero writes. Exit 0.
                        Mutually exclusive with --triage.
    --triage DOC_ID     Triage mode. Write TRIAGED + audit fields for one doc.
                        Mutually exclusive with --dry-run, --date, --limit.
    --verbose           Show full UID and full transcript (no truncation).

  MUTUAL EXCLUSION:
    --triage + --dry-run together: print "ERROR: --triage and --dry-run are mutually
    exclusive.", exit 1. No Firestore read or write performed.

  ARGUMENT VALIDATION:
    --triage with no DOC_ID: print "ERROR: --triage requires a document ID.", exit 1.
    --date with invalid format: print "ERROR: --date must be YYYY-MM-DD.", exit 1.
    --limit with non-integer: print "ERROR: --limit must be a positive integer.", exit 1.

  EXIT CODES:
    0 — success (read completed, inbox zero, or SKIP on already-triaged doc)
    1 — infrastructure failure (credentials, Firestore unreachable, permission denied,
        missing status field, unexpected exception, argument conflict)

  TRIAGE SUCCESS OUTPUT:
    "TRIAGED: {short_id} | doc_id={full_id} | new_status=TRIAGED | triaged_at={timestamp}"

  TRIAGE SKIP OUTPUT:
    "SKIP: {short_id} — status is {current_status}, not OPEN. No write made."

### Grok v2 Must-Fix #3 — Transaction failure modes

OLD (v2 Section 3, Must-Fix #2):
  "If the assertion fails (status already changed), the transaction aborts and prints:
  'SKIP: {short_id} — status is {current_status}, not OPEN. No write made.'
  then exits with code 0."
  (Only the race case was handled. Permission denied, network failure, missing field were not.)

NEW (v3 Section 2, failure handling):
  All failure modes listed with explicit exit codes:
  - MISSING document: exit 1
  - SKIP (status != OPEN): exit 0
  - PermissionDenied: exit 1, non-PII message
  - Unavailable / network error: exit 1, non-PII message
  - Missing status field: exit 1, "manual review required"
  - Any unhandled exception: exit 1, type name only (no stack trace in chat output)
  In all cases: no partial write claimed, no fallback to .eml or any client path.

### Gemini v2 Must-Fix #2 — snake_case output fields

OLD (v2 Deliverable 1 report format):
  Fields named in prose without explicit casing guarantee:
  "feedback_id", "issue_type", "severity_estimate", "page_title", "route",
  "intake_method", "morgan_summary", "ai_analysis", "full_transcript"
  (No explicit statement that output field names are snake_case.)

NEW (v3):
  All field keys written to stdout or used in --triage output are snake_case:
  feedback_id, created_at, issue_type, severity_estimate, page_title, route,
  user_id (truncated), intake_method, morgan_summary, ai_analysis,
  full_transcript, status, triaged_by, triaged_at, triaged_by_agent.
  No camelCase, no PascalCase, no mixed-case field names in any output or write.

### Gemini v2 Must-Fix #3 — tier_gatekeeper.py as protected

OLD (v2 Section 5):
  "tier_gatekeeper.py (file does not exist in repo; no action)"

NEW (v3):
  tier_gatekeeper.py is listed as a protected file. Protection means: this script
  will not write to, import from, or modify it. The file's current absence from the
  repo does not change this constraint — if it is created in a future session, the
  write-prohibition still applies to this plan's scope.

---

## Section 4 — Deliverable 1: fetch_open_feedback.py [NEW]

Scope: numista_qa_runner/fetch_open_feedback.py

Full CLI contract: see Section 3, Must-Fix #2 proof above.

Read mode behavior:
  Query: beta_feedback WHERE status == "OPEN" ORDER BY created_at DESC LIMIT {n}
  Optional date filter: WHERE created_at >= {date}T00:00:00Z AND < {date+1}T00:00:00Z

Per-item report block (read mode):
  Line 1:  [{i}] {feedback_id[:8]}... | {issue_type} | {severity_estimate} | {intake_method}
  Line 2:  Date:      {created_at formatted as YYYY-MM-DD HH:MM UTC}
  Line 3:  Page:      {page_title} ({route})
  Line 4:  User:      {user_id[:8]}...  (full UID on --verbose only)
  Line 5:  Message:   {first user transcript message, 200 chars max, "N/A" if absent}
  Line 6:  MORGAN:    {morgan_summary, 300 chars max, "N/A" if null}
  Line 7:  Root Cause:{ai_analysis.root_cause_hypothesis, "N/A" if absent}
  Line 8:  Fix Area:  {ai_analysis.suggested_fix_area, "N/A" if absent}
  Line 9:  Effort:    {ai_analysis.estimated_effort, "N/A" if absent}
  Line 10: Full ID:   {feedback_id}  (Firestore console link noted in workflow doc)

  Transcript truncation: 500 chars total. If truncated: append "(truncated — full doc: {feedback_id})"
  Inbox zero: "Inbox zero — no OPEN feedback found." Exit 0.

Null-safety guarantee: every field access uses .get() with a default of None.
  None renders as "N/A". No KeyError, AttributeError, or TypeError is possible
  from a missing or wrongly-typed Firestore field.

Validated against: feedback IDs f724a3ae... and 253599ed... (both 23-Aug-2026,
  fallback_form, morgan_summary=None, ai_analysis absent). Both must render without
  error and display "N/A" for all absent fields.

Credentials loading order (unchanged from v2):
  1. GOOGLE_APPLICATION_CREDENTIALS env var set → use ADC
  2. numista_backend/serviceAccountKey.json present → use that file
  3. Neither → "ERROR: No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS
     or ensure numista_backend/serviceAccountKey.json exists." Exit 1.
  Key path and contents are never printed or logged.
  serviceAccountKey.json is confirmed present in .gitignore before use.
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

Explicit 6-step agent sequence (same as v2, restated for completeness):

  Step 1: Run: python numista_qa_runner/fetch_open_feedback.py [--date YYYY-MM-DD] [--limit N]
  Step 2: Display the full report in chat (summary table + per-item detail blocks)
  Step 3: For each OPEN item, state the proposed action to the founder and WAIT for confirmation
  Step 4: On founder confirmation only — run: python numista_qa_runner/fetch_open_feedback.py --triage {doc_id}
  Step 5: Echo the TRIAGED confirmation line including triaged_at timestamp
  Step 6: If a fix is needed — create an implementation plan in this session; do not proceed to RESOLVED

Hard rules:
  - Agent NEVER runs --triage without explicit per-item founder confirmation
  - Agent NEVER marks status RESOLVED — only TRIAGED. RESOLVED is set by founder after fix verification.
  - Agent NEVER falls back to .eml parsing on any failure
  - Agent NEVER uses the ADMIN_RESOLVE callable — the script uses Admin SDK only
  - On any infrastructure error: print the error line and stop; do not guess or substitute
  - --triage and --dry-run are never combined in the same invocation

---

## Section 7 — What Is Not Changing

(All reviewers confirmed across v1 and v2):
  - MORGAN in-app interview system
  - feedback_callable_route.py
  - feedbackIntelligence.js
  - admin_feedback_screen.dart
  - passport_pdf_generator.py (protected)
  - numista_bq_loader_job (protected)
  - tier_gatekeeper.py (protected; file does not currently exist in repo —
    protection means this plan's scripts will not write to or import from it)

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
   Expected: exactly 2 OPEN items (f724a3ae..., 253599ed...)
   Expected: all absent fields render as "N/A" — no crash, no KeyError

2. Dry-run test:
   python numista_qa_runner/fetch_open_feedback.py --dry-run
   Expected: proposed triage list displayed, zero Firestore writes, exit 0

3. Mutual exclusion test:
   python numista_qa_runner/fetch_open_feedback.py --triage {doc_id} --dry-run
   Expected: "ERROR: --triage and --dry-run are mutually exclusive." exit 1

4. Triage write test (against a test doc or one of the two 23-Aug items):
   python numista_qa_runner/fetch_open_feedback.py --triage {doc_id}
   Expected: "TRIAGED: {short_id} | doc_id=... | new_status=TRIAGED | triaged_at=..."
   Expected: Firestore doc now has status=TRIAGED, triaged_by=antigravity-agent,
             triaged_by_agent=True, triaged_at set

5. Re-run same triage (idempotency):
   python numista_qa_runner/fetch_open_feedback.py --triage {same_doc_id}
   Expected: "SKIP: {short_id} — status is TRIAGED, not OPEN. No write made." exit 0

6. Credential fail-closed test:
   Run with no env var and serviceAccountKey.json renamed/absent
   Expected: "ERROR: No credentials found..." exit 1

7. Inbox-zero test:
   Run against a date with no OPEN items
   Expected: "Inbox zero — no OPEN feedback found." exit 0

8. Miner path test:
   python numista_qa_runner/daily_feedback_test_miner.py
   Expected: scans Beta Testing Feedback\23 AUG 26\ (not the old path)

9. Git hygiene:
   git status confirms: only 3 files modified/created
   serviceAccountKey.json does not appear in staged files

10. Push:
    git pull --rebase origin dev
    git push origin dev

---

## Section 10 — Open Questions

None. All questions from v1 and v2 are resolved:
  Q1 (write-path): RESOLVED — Option A, Admin SDK, Section 2
  Q2 (TRIAGED timing): RESOLVED — immediately on founder confirmation
  Q3 (.eml parser): RESOLVED — not implemented
