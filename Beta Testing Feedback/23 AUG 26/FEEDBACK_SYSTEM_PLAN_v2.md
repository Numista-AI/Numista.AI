# Numista.AI — Antigravity Feedback System: Implementation Plan v2
**Date:** 23 AUG 2026
**Tasker:** Beta Testing Feedback — Feedback System Redesign
**Status:** NOT EXECUTION-READY. Awaiting founder resolution of one write-path conflict, then next Gemini + Grok pass.

---

## Section 1 — Decision Matrix

| Source | Suggestion | Adopted / Modified / Rejected | Why |
|--------|-----------|-------------------------------|-----|
| Gemini | Adopt `fetch_open_feedback.py` | ADOPTED | Was in v1; Grok also accepts; no change needed. |
| Gemini | Adopt `daily_feedback_test_miner.py` path fix | ADOPTED | One-line fix, both reviewers agree. |
| Gemini | Adopt `.agents/FEEDBACK_WORKFLOW.md` protocol | ADOPTED WITH MODIFICATION | Grok requires explicit sequence and no-silent-close rule added; content updated below. |
| Gemini | Adopt `patch_beta_13aug_metadata.py` | REJECTED | This file does not exist in the repo (confirmed). Gemini reviewed a file outside the scope of v1. Rule 5: no new architecture. |
| Gemini | Adopt standalone `_LegislationTab` widget | REJECTED | Not in v1 scope. Rule 5: do not add new features to look complete. |
| Gemini | Adopt Sheldon/Morgan grade hover tooltips | REJECTED | Not in v1 scope. Rule 5. |
| Gemini | Adopt `prod_account_audit_repair.py` | REJECTED | File exists but was not in v1 scope. Gemini reviewed a broader plan than was submitted. Rule 5. |
| Gemini | Adopt Playwright DOM readiness checks | REJECTED | Not in v1 scope. Rule 5. |
| Gemini Must-Fix #1 | Revert blanket merge=True in patch script | REJECTED AS STATED | The named script (`patch_beta_13aug_metadata.py`) does not exist. The underlying principle (merge=True only for in-place repairs, not new-record creates) is valid and carried into the write-path spec below for the scripts that DO exist. |
| Gemini Must-Fix #2 | Verify currency/world_items isolation from coins | NOTED, NOT IN SCOPE | Non-negotiable confirms the existing design. No change to `passport_pdf_generator.py` or estate math is in this plan. |
| Gemini Must-Fix #3 | Enforce snake_case across all repair scripts | ADOPTED AS CONSTRAINT | All new fields in `fetch_open_feedback.py` output will be snake_case. No other scripts are being modified in this plan. |
| Gemini Must-Fix #4 | Update `BASE_FEEDBACK_DIR` in miner | ADOPTED | One-line change; both reviewers agree. |
| Gemini Must-Fix #5 | No mutations in protected files | ADOPTED | `passport_pdf_generator.py`, `numista_bq_loader_job`, `tier_gatekeeper.py` (note: tier_gatekeeper.py does not exist in repo) are not touched by this plan. |
| Grok Must-Fix #1 | Write-path is underspecified — choose Admin SDK direct update or callable | SEE CONFLICT SECTION | Gemini implicitly accepted the callable path (adopted workflow protocol as-is). Grok explicitly requires Admin SDK. This changes who writes data. Founder decision required. |
| Grok Must-Fix #2 | Add idempotency, race protection, audit fields | ADOPTED | Added to write-path spec regardless of which path is chosen (both require it). |
| Grok Must-Fix #3 | Credentials fail-closed, ADC fallback, never logged | ADOPTED | v1 sentence "Initializes Firebase Admin SDK using serviceAccountKey.json" is replaced with explicit credential chain. |
| Grok Must-Fix #4 | Fallback-form fields graceful (null-safe) | ADOPTED | v1 assumed full MORGAN data. Both 23-Aug items have morgan_summary=None and empty ai_analysis. Field extraction is now explicitly null-safe. |
| Grok Must-Fix #5 | Audit trail — every triage action leaves immutable record | ADOPTED | Stamped fields on same transaction as status write. |
| Grok Push-back | Admin SDK direct update preferred over callable for agent path | SEE CONFLICT SECTION | Cannot resolve without founder input. |
| Grok Push-back | Mark TRIAGED immediately after agent reads and accepts | ADOPTED | Matches v1 recommendation; now explicitly in workflow sequence. |
| Grok Push-back | Add `--dry-run` flag | ADOPTED | Shows proposed triage set before any write. |
| Grok Push-back | Workflow protocol: agent never auto-closes without founder confirmation | ADOPTED | Added as explicit rule in workflow doc. |
| Grok Edge Cases | Firestore unreachable → exit non-zero, no .eml fallback | ADOPTED | Exit code 1, clear non-PII message. Never silently falls back to .eml parsing. |
| Grok Edge Cases | Empty result → "inbox zero" message, not error | ADOPTED | Clean message, exit code 0. |
| Grok Edge Cases | Large transcripts → truncate with clear marker | ADOPTED | Truncate at 500 chars with "...(truncated, full_id: {doc_id})" |
| Grok Edge Cases | PII surface — UIDs as short prefix | ADOPTED | UID shown as first 8 chars + "..." in table. Full UID on secondary line only if requested. |
| Grok Note | Optional .eml parser is scope creep | ADOPTED (reject the feature) | Grok's own words. Not implemented. |
| Grok Note | Surface 8-char feedback ID prefix + full ID on secondary line | ADOPTED | Matches readability intent from v1. |

---

## Section 2 — OPEN CONFLICT (Founder Decision Required)

### CONFLICT — [Gemini: ADMIN_RESOLVE callable is acceptable] vs [Grok: Admin SDK direct update required]

**What Gemini says (implicit):**
Gemini adopted `.agents/FEEDBACK_WORKFLOW.md` as-is. v1 of that protocol read:
  "Mark TRIAGED or RESOLVED via ADMIN_RESOLVE callable"
By adopting without comment, Gemini accepted the callable as the write mechanism.

**What Grok says (explicit):**
  "A local script running under a service-account key cannot safely 'call the callable'
   the way a Flutter client does. Next version must choose one privileged path
   (preferred: Admin SDK direct update inside a transaction)."

**Why this matters:**
The callable (`POST /api/feedback/callable` mode=ADMIN_RESOLVE) is designed for
authenticated end-users hitting Cloud Run over HTTP with a Firebase ID Token.
A Python script running locally with a service account key is a different trust model.
Using Admin SDK directly avoids the extra HTTP hop, uses the same SDK already required
for the read, and allows a proper Firestore transaction. Using the callable from the
agent would require the agent to obtain and refresh a Firebase ID Token, which is not
the same as the service account key — it is a different authentication flow.

**The two options:**

OPTION A — Admin SDK direct update (Grok's preference):
  doc_ref.update({
    "status": "TRIAGED",
    "triaged_by": "antigravity-agent",
    "triaged_at": firestore.SERVER_TIMESTAMP,
    "triaged_by_agent": True
  })
  Wrapped in a transaction that reads and checks status == "OPEN" first.
  Pro: one credential, one SDK, transactional, no extra HTTP auth.
  Con: bypasses the callable's audit logic and DATA_INTEGRITY enforcement.

OPTION B — Call ADMIN_RESOLVE callable via HTTP (Gemini accepted):
  Agent obtains a custom token or uses the REST API with a signed JWT,
  then POST /api/feedback/callable with mode=ADMIN_RESOLVE.
  Pro: reuses existing callable logic, consistent with admin_feedback_screen.
  Con: requires a second auth flow (ID token, not service account key),
       extra network hop, not transactional in the Firestore sense.

RESOLVED: Option A selected by founder. Admin SDK direct update in a Firestore transaction. The ADMIN_RESOLVE callable is NOT used by the agent script.

---

## Section 3 — Proof: Old vs New (Grok Must-Fix Items)

Per the requirement: every Grok Must-Fix must show the old plan sentence
and the new plan sentence. If the new mechanism cannot be quoted, the item is not done.

### Must-Fix #1 — Write path (RESOLVED: Option A — Admin SDK direct update)
OLD: "Antigravity can mark items TRIAGED or RESOLVED via ADMIN_RESOLVE callable"
NEW: "The triage write uses the Firebase Admin SDK directly. The script opens a
Firestore transaction, reads the document, asserts status == 'OPEN', then writes:
  status: 'TRIAGED', triaged_by: 'antigravity-agent',
  triaged_at: SERVER_TIMESTAMP, triaged_by_agent: True.
If the assertion fails, the transaction aborts and prints:
  'SKIP: {short_id} - status is {current_status}, not OPEN. No write made.'
The ADMIN_RESOLVE callable is NOT invoked by this script."

### Must-Fix #2 — Idempotency and race protection
OLD: (not specified in v1)
NEW: "The triage write is wrapped in a Firestore transaction. The transaction reads
the document, checks that status == 'OPEN', then writes the new status and audit fields
atomically. If the status has already changed (e.g., founder updated it in
admin_feedback_screen), the transaction aborts and the script prints:
'SKIP: {short_id} — status changed to {current_status} externally. No write made.'
then exits with code 0. Running the same feedback ID twice produces the same abort."

### Must-Fix #3 — Credentials
OLD: "Initializes Firebase Admin SDK using numista_backend/serviceAccountKey.json"
NEW: "Script loads credentials in this order:
  1. If GOOGLE_APPLICATION_CREDENTIALS env var is set → use ADC (gcloud auth application-default)
  2. Else if numista_backend/serviceAccountKey.json exists → use that file
  3. Else → print 'ERROR: No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS
     or ensure numista_backend/serviceAccountKey.json exists.' and exit with code 1.
The key file path and contents are never printed or logged. The key file is confirmed
present in .gitignore. This script is operator-only and must not be exposed to
untrusted sessions."

### Must-Fix #4 — Fallback-form null safety
OLD: "Key fields extracted per document: morgan_summary → MORGAN's plain-English summary,
ai_analysis → root_cause_hypothesis, suggested_fix_area, estimated_effort, pattern_tags"
NEW: "All optional fields are null-safe. Missing fields render as 'N/A' in the report.
Specific guarantees:
  - morgan_summary is None → prints 'MORGAN Summary: N/A'
  - ai_analysis is absent or empty → prints 'AI Analysis: N/A (fallback-form submission)'
  - full_transcript is empty or absent → prints 'Transcript: N/A'
  - Script never raises KeyError or AttributeError on any Firestore field.
Validated against both 23-Aug-2026 IDs (f724a3ae, 253599ed) which both have
morgan_summary=None and empty ai_analysis (fallback_form intake method)."

### Must-Fix #5 — Audit trail
OLD: (not specified in v1)
NEW: "Every successful triage write stamps these fields in the same transaction
as the status change:
  triaged_by: 'antigravity-agent'
  triaged_at: firestore.SERVER_TIMESTAMP
  triaged_by_agent: True
These fields are write-once. The transaction does not overwrite them if already present
(enforced by the status==OPEN check — if status is not OPEN, the transaction aborts,
so these fields cannot be silently overwritten). After a successful write, the script
echoes: 'TRIAGED: {short_id} | new_status=TRIAGED | triaged_at={timestamp}'"

---

## Section 4 — Modified Deliverables

### Deliverable 1 — `numista_qa_runner/fetch_open_feedback.py` [NEW — unchanged scope]

Querying behavior (unchanged from v1):
  - Firestore beta_feedback where status == "OPEN", ordered by created_at descending
  - Optional --limit N (default 50)
  - Optional --date YYYY-MM-DD

New additions to v1:
  - --dry-run flag: shows proposed triage set, makes zero writes
  - Null-safe field extraction (all optional fields default to "N/A")
  - Credentials chain: ADC first, then serviceAccountKey.json, then fail-closed
  - Transcript truncation at 500 chars with "(truncated — full doc: {doc_id})"
  - UID display: first 8 chars in table, full UID on secondary line if --verbose
  - Exit codes: 0 = success or inbox-zero, 1 = infrastructure failure

Report output format per item:
  ┌─ [{i}] {short_id}... | {issue_type} | {severity} | {intake_method} ─┐
  │ Date:      {created_at}
  │ Page:      {page_title} ({route})
  │ User:      {uid[:8]}...
  │ Message:   {first user transcript message, 200 chars max}
  │ MORGAN:    {morgan_summary or "N/A"}
  │ Root Cause:{ai_analysis.root_cause_hypothesis or "N/A"}
  │ Fix Area:  {ai_analysis.suggested_fix_area or "N/A"}
  │ Effort:    {ai_analysis.estimated_effort or "N/A"}
  │ Full ID:   {doc_id}
  └─────────────────────────────────────────────────────────────────────┘

Triage write path: Admin SDK direct update in a Firestore transaction (Option A — see Must-Fix #1 proof in Section 3).

### Deliverable 2 — `numista_qa_runner/daily_feedback_test_miner.py` [MODIFY]

One-line change only. No other modifications.

OLD:
  BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING"

NEW:
  BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Beta Testing Feedback"

### Deliverable 3 — `.agents/FEEDBACK_WORKFLOW.md` [NEW — content updated from v1]

Explicit agent sequence (replaces the vague v1 version):

  Step 1: Run: python numista_qa_runner/fetch_open_feedback.py [--date YYYY-MM-DD]
  Step 2: Display the full report in chat (summary table + per-item detail)
  Step 3: For each OPEN item, state the proposed action to the founder and WAIT
  Step 4: On founder confirmation only — run with --triage {doc_id} to write TRIAGED status
  Step 5: Echo the confirmed audit timestamp from the write response
  Step 6: If a fix is needed — create an implementation plan in this session

Rules:
  - Agent NEVER auto-closes or auto-resolves any item without explicit founder confirmation
  - Agent NEVER marks RESOLVED — only TRIAGED. RESOLVED is set by the founder after fix verification.
  - Agent NEVER falls back to parsing .eml files if Firestore is unreachable
  - On any infrastructure error: print the error, exit, do not guess or substitute

---

## Section 5 — What Is Not Changing

(Unchanged from v1 — both reviewers confirmed)
- MORGAN in-app interview system
- feedback_callable_route.py
- feedbackIntelligence.js
- admin_feedback_screen.dart
- passport_pdf_generator.py (protected)
- numista_bq_loader_job (protected)
- tier_gatekeeper.py (file does not exist in repo; no action)

---

## Section 6 — Gemini Items Rejected (Out-of-Scope Explanation)

Gemini reviewed a broader set of items than were in v1. These are not rejected as bad
ideas — they are rejected because rule 5 prohibits adding new architecture to look complete.
They belong in a separate plan if the founder wants them:

  - patch_beta_13aug_metadata.py: file does not exist in repo. Cannot adopt.
  - _LegislationTab widget: UI refactor not related to feedback system.
  - Sheldon/Morgan tooltips: UI feature not related to feedback system.
  - prod_account_audit_repair.py: exists in repo but is a separate concern.
  - Playwright DOM readiness: E2E testing concern, not feedback system.

---

## Section 7 — Files To Be Created / Modified

| File | Action | Blocked on conflict? |
|------|--------|---------------------|
| numista_qa_runner/fetch_open_feedback.py | CREATE | No |
| numista_qa_runner/daily_feedback_test_miner.py | MODIFY (1 line) | No |
| .agents/FEEDBACK_WORKFLOW.md | CREATE | No |

---

## Section 8 — Verification Plan (Unchanged + Additions)

1. Script test:
   python numista_qa_runner/fetch_open_feedback.py --date 2026-08-23
   Must return exactly 2 OPEN items (f724a3ae, 253599ed)
   Must not crash on null morgan_summary or empty ai_analysis
   Must display "N/A" for all missing fields on both items

2. Dry-run test:
   python numista_qa_runner/fetch_open_feedback.py --dry-run
   Must show triage proposal, make zero Firestore writes

3. Credential fail-closed test:
   Run with no env var and no key file present
   Must print error message and exit with code 1

4. Inbox-zero test:
   Run against a date with no OPEN items
   Must print "Inbox zero — no OPEN feedback found." and exit with code 0

5. Miner path test:
   python numista_qa_runner/daily_feedback_test_miner.py
   Must scan Beta Testing Feedback\23 AUG 26\ (not the old path)

6. Git hygiene:
   git status confirms only 3 files modified/created
   serviceAccountKey.json does not appear in staged files

7. Push: git pull --rebase origin dev && git push origin dev

---

## Open Questions Carried Forward

Q1 — Write-path conflict: FOUNDER MUST DECIDE (see Section 2)
Q2 — TRIAGED timing: RESOLVED — mark TRIAGED immediately (Grok + v1 recommendation confirmed)
Q3 — .eml parser: RESOLVED — do not implement (Grok confirmed scope creep)
