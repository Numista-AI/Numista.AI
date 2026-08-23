# Antigravity Feedback Workflow
**File:** `.agents/FEEDBACK_WORKFLOW.md`
**Scope:** Beta feedback triage sessions only.
**Script:** `numista_qa_runner/fetch_open_feedback.py`

---

## When to Activate

When the founder says any of the following:
- "check feedback"
- "read feedback"
- "what is open in beta feedback"
- "triage feedback"

---

## The 6-Step Sequence

**Step 1 — Fetch**
Run the reader script (optionally with a date filter):
```
python numista_qa_runner/fetch_open_feedback.py [--date YYYY-MM-DD] [--limit N]
```

**Step 2 — Display**
Present the full formatted report in chat:
- Summary line per item (short ID, issue type, severity, intake method)
- Full detail block per item (page, user prefix, message, MORGAN summary, AI analysis)
- Full document ID on a secondary line for Firestore console reference

**Step 3 — Propose and Wait**
For each OPEN item, state the proposed action (triage / fix plan) and
**STOP**. Wait for explicit founder confirmation before writing anything.
Do not batch-propose multiple items without pausing for confirmation on each.

**Step 4 — Triage (on founder confirmation only)**
When the founder confirms a specific item:
```
python numista_qa_runner/fetch_open_feedback.py --triage {doc_id}
```

**Step 5 — Echo the confirmation**
The script will print the full confirmation line. Echo it in chat:
```
TRIAGED: {short_id}... | doc_id={full_id} | new_status=TRIAGED | triaged_at={timestamp}
```
This makes the chat itself part of the operational record.

**Step 6 — Fix plan (if needed)**
If the founder wants a fix for the triaged item, create an implementation
plan in this session. Do not proceed to RESOLVED — that is the founder's
action after the fix is verified.

---

## Hard Rules (Never Break These)

| Rule | Detail |
|------|--------|
| Never auto-triage | Agent never runs `--triage` without explicit per-item founder confirmation in the current session |
| Never RESOLVED | Agent only writes `TRIAGED`. `RESOLVED` is set by the founder after fix verification |
| Never callable | The `ADMIN_RESOLVE` callable is never invoked by this script. Admin SDK only. |
| Never .eml fallback | If Firestore is unreachable, print the error and stop. Do not parse .eml files. |
| Never combine flags | `--triage` and `--dry-run` are never used together in the same invocation |
| Never touch live items in tests | `f724a3ae...` and `253599ed...` are only triaged via this confirmed workflow |
| Never auto-close | Agent never proceeds from TRIAGED to RESOLVED autonomously |

---

## CLI Reference

```
python numista_qa_runner/fetch_open_feedback.py [OPTIONS]

  (no flags)          Read all OPEN feedback. Exit 0.
  --date YYYY-MM-DD   Filter by date (UTC). Read mode only.
  --limit N           Max results (default 50). Read mode only.
  --dry-run           Show what would be triaged. Zero writes. Exit 0.
  --triage DOC_ID     Triage one document. Mutual exclusive with --dry-run.
  --verbose           Show full UID and full transcript.

Exit 0: success, inbox-zero, or SKIP (already triaged)
Exit 1: any infrastructure, argument, or missing-document error
```

---

## What This Script Never Touches

- `users/{uid}/coins` — no reads, no writes, no imports
- `feedback_callable_route.py` — not modified
- `feedbackIntelligence.js` — not modified
- `admin_feedback_screen.dart` — not modified
- `passport_pdf_generator.py` — protected
- `numista_bq_loader_job` — protected
- `tier_gatekeeper.py` — protected (write-prohibition regardless of file presence)
- Any Flutter/mobile file — Desktop Web only
