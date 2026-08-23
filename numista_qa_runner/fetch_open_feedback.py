"""
Numista.AI -- Antigravity Open Feedback Reader
===============================================
Queries Firestore beta_feedback collection for OPEN items and displays a
formatted report. Optionally triages a single item via Admin SDK transaction.

USAGE:
  python numista_qa_runner/fetch_open_feedback.py [OPTIONS]

OPTIONS:
  (no flags)          Read mode. Fetch and display all OPEN feedback.
  --date YYYY-MM-DD   Filter by submission date (UTC). Read mode only.
  --limit N           Max documents (default 50). Read mode only.
  --dry-run           Show what would be triaged. Zero writes. Exit 0.
                      Mutually exclusive with --triage.
  --triage DOC_ID     Triage one document. Mutually exclusive with --dry-run,
                      --date, --limit.
  --verbose           Show full UID and full transcript (no truncation).

EXIT CODES:
  0 -- success, inbox-zero, or SKIP (doc already triaged)
  1 -- infrastructure failure, argument error, or missing document

This script is OPERATOR-ONLY. Do not expose to untrusted sessions.
The service account key is never printed or logged.
"""

import sys
import os
import re
import argparse
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Numista.AI - Antigravity Open Feedback Reader",
        add_help=True,
    )
    parser.add_argument("--date", metavar="YYYY-MM-DD",
                        help="Filter OPEN items by submission date (UTC).")
    parser.add_argument("--limit", type=int, default=50, metavar="N",
                        help="Max documents to return (default 50).")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Show proposed triage set. Zero writes.")
    parser.add_argument("--triage", metavar="DOC_ID",
                        help="Triage one document by its Firestore document ID.")
    parser.add_argument("--verbose", action="store_true",
                        help="Show full UID and full transcript.")
    args = parser.parse_args()

    # Mutual exclusion: --triage vs --dry-run
    if args.triage is not None and args.dry_run:
        _fatal("--triage and --dry-run are mutually exclusive.")

    # --triage: validate DOC_ID
    if args.triage is not None:
        doc_id = args.triage
        if doc_id == "":
            _fatal("--triage document ID cannot be empty.")
        if not re.match(r'^[a-zA-Z0-9_-]{8,128}$', doc_id):
            _fatal("--triage document ID appears malformed. Expected alphanumeric Firestore ID.")
        # --triage is incompatible with --date and --limit (non-default)
        if args.date is not None or args.limit != 50:
            _fatal("--triage cannot be combined with --date or --limit.")

    # --date: validate format
    if args.date is not None:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', args.date):
            _fatal("--date must be YYYY-MM-DD.")
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            _fatal("--date is not a valid calendar date.")

    # --limit: validate positive integer
    if args.limit < 1:
        _fatal("--limit must be a positive integer.")

    return args


def _fatal(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Firebase Admin SDK initialisation
# ---------------------------------------------------------------------------

KEY_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "numista_backend", "serviceAccountKey.json"
))


def init_firebase():
    """
    Credential chain:
      1. GOOGLE_APPLICATION_CREDENTIALS env var set -> ADC
      2. numista_backend/serviceAccountKey.json present -> explicit file
      3. Neither -> fail-closed, exit 1
    Key is never printed or logged.
    """
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError:
        _fatal("firebase-admin is not installed. Run: pip install firebase-admin")

    if not firebase_admin._apps:
        adc_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if adc_env:
            cred = credentials.ApplicationDefault()
        elif os.path.isfile(KEY_PATH):
            cred = credentials.Certificate(KEY_PATH)
        else:
            _fatal(
                "No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS "
                "or ensure numista_backend/serviceAccountKey.json exists."
            )
        firebase_admin.initialize_app(cred)

    from firebase_admin import firestore as fs_module
    return fs_module.client()


# ---------------------------------------------------------------------------
# Firestore query
# ---------------------------------------------------------------------------

def fetch_open_items(db, date_str=None, limit=50):
    """Return list of (doc_id, doc_data) for OPEN beta_feedback docs.

    Uses a single-field query (status == 'OPEN') to avoid requiring a
    composite Firestore index. Sorting and date filtering are done in Python.
    """
    try:
        col = db.collection("beta_feedback")
        # Single-field filter only — no composite index required
        docs = [(d.id, d.to_dict() or {}) for d in
                col.where("status", "==", "OPEN").stream()]

        # Date filter in Python
        if date_str:
            day_start = datetime.strptime(date_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            day_end = day_start + timedelta(days=1)
            def _in_range(data):
                ts = data.get("created_at")
                if ts is None:
                    return False
                if hasattr(ts, "tzinfo") and ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                return day_start <= ts < day_end
            docs = [(doc_id, data) for doc_id, data in docs if _in_range(data)]

        # Sort by created_at descending in Python
        def _sort_key(item):
            ts = item[1].get("created_at")
            if ts is None:
                return datetime.min.replace(tzinfo=timezone.utc)
            if hasattr(ts, "tzinfo") and ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts

        docs.sort(key=_sort_key, reverse=True)
        return docs[:limit]

    except Exception as e:
        _fatal("Firestore query failed: " + type(e).__name__ + ": " + str(e)[:200])



# ---------------------------------------------------------------------------
# Report formatting helpers
# ---------------------------------------------------------------------------

TRANSCRIPT_LIMIT = 500
MSG_LIMIT = 200
MORGAN_LIMIT = 300
UID_SHORT = 8
ID_SHORT = 8


def _safe(data, *keys, default="N/A", limit=None):
    """Safely traverse nested dict; returns default if any key is missing/None."""
    val = data
    for k in keys:
        if not isinstance(val, dict):
            return default
        val = val.get(k)
        if val is None:
            return default
    s = str(val).strip()
    if not s:
        return default
    if limit and len(s) > limit:
        s = s[:limit] + "..."
    return s


def _fmt_ts(ts):
    if ts is None:
        return "N/A"
    try:
        if hasattr(ts, "strftime"):
            return ts.strftime("%Y-%m-%d %H:%M UTC")
        return str(ts)
    except Exception:
        return "N/A"


def _first_user_message(transcript):
    if not isinstance(transcript, list):
        return "N/A"
    for entry in transcript:
        if not isinstance(entry, dict):
            continue
        # Actual schema: {"ts": "...", "message": "..."}
        text = (entry.get("message") or entry.get("text") or entry.get("content") or "").strip()
        if text:
            return text[:MSG_LIMIT] + ("..." if len(text) > MSG_LIMIT else "")
    return "N/A"


def _render_transcript(transcript, verbose=False):
    if not isinstance(transcript, list):
        return "N/A"
    lines = []
    for entry in transcript:
        if not isinstance(entry, dict):
            continue
        # Actual schema: {"ts": "...", "message": "..."}
        role = entry.get("role", "user")
        text = (entry.get("message") or entry.get("text") or entry.get("content") or "").strip()
        ts = entry.get("ts", "")
        if text:
            lines.append("  [" + role + ((" @" + str(ts)[:16]) if ts else "") + "] " + text)
    full = "\n".join(lines)
    if not full:
        return "N/A"
    if not verbose and len(full) > TRANSCRIPT_LIMIT:
        return full[:TRANSCRIPT_LIMIT] + "\n  ...(truncated - full doc: see Full ID below)"
    return full



# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(items, verbose=False, dry_run=False):
    if not items:
        print("Inbox zero - no OPEN feedback found.")
        return

    sep = "=" * 70
    print("\n" + sep)
    print("  OPEN FEEDBACK REPORT - " + str(len(items)) + " item(s)")
    if dry_run:
        print("  DRY-RUN MODE - no writes will be made")
    print(sep + "\n")

    for i, (doc_id, data) in enumerate(items, 1):
        short_id = doc_id[:ID_SHORT]
        uid_raw = (data.get("uid") or data.get("user_id") or "").strip()
        uid_display = (uid_raw[:UID_SHORT] + "...") if uid_raw else "N/A"
        ai = data.get("ai_analysis") or {}
        transcript = data.get("full_transcript") or data.get("transcript") or []

        print("[" + str(i) + "] " + short_id + "... | " +
              _safe(data, "issue_type") + " | " +
              _safe(data, "severity_estimate") + " | " +
              _safe(data, "intake_method"))
        print("  Date:       " + _fmt_ts(data.get("created_at")))
        print("  Page:       " + _safe(data, "page_title") +
              " (" + _safe(data, "route") + ")")
        uid_line = "  User:       " + uid_display
        if verbose and uid_raw:
            uid_line += "  [full: " + uid_raw + "]"
        print(uid_line)
        print("  Message:    " + _first_user_message(transcript))
        print("  MORGAN:     " + _safe(data, "morgan_summary", limit=MORGAN_LIMIT))
        print("  Root Cause: " + _safe(ai, "root_cause_hypothesis"))
        print("  Fix Area:   " + _safe(ai, "suggested_fix_area"))
        print("  Effort:     " + _safe(ai, "estimated_effort"))
        if verbose:
            print("  Transcript:")
            print(_render_transcript(transcript, verbose=True))
        print("  Full ID:    " + doc_id)
        print()


# ---------------------------------------------------------------------------
# Triage write (transactional Admin SDK - callable never invoked)
# ---------------------------------------------------------------------------

def triage_document(db, doc_id):
    """
    Transactional triage. Asserts status == 'OPEN' before writing.
    Stamps triaged_by, triaged_at, triaged_by_agent atomically.
    The ADMIN_RESOLVE callable is NOT used by this function.
    """
    try:
        from firebase_admin import firestore as fs_module
        from google.cloud import firestore
        from google.api_core.exceptions import PermissionDenied, ServiceUnavailable
    except ImportError as e:
        _fatal("Import error: " + str(e))

    short_id = doc_id[:ID_SHORT]
    doc_ref = db.collection("beta_feedback").document(doc_id)

    @firestore.transactional
    def _run(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if not snapshot.exists:
            return ("MISSING", None)
        data = snapshot.to_dict() or {}
        if "status" not in data:
            return ("NO_STATUS", None)
        current = data["status"]
        if current != "OPEN":
            return ("SKIP", current)
        transaction.update(doc_ref, {
            "status": "TRIAGED",
            "triaged_by": "antigravity-agent",
            "triaged_at": fs_module.SERVER_TIMESTAMP,
            "triaged_by_agent": True,
        })
        return ("OK", "TRIAGED")

    try:
        transaction = db.transaction()
        result, detail = _run(transaction)
    except PermissionDenied:
        _fatal("Permission denied. Check service account roles for beta_feedback.")
    except ServiceUnavailable:
        _fatal("Firestore unreachable. Check network and project configuration.")
    except Exception as e:
        _fatal("Unexpected failure: " + type(e).__name__ + ". No write made.")

    if result == "MISSING":
        print("ERROR: " + short_id + "... - document not found.", file=sys.stderr)
        sys.exit(1)
    elif result == "NO_STATUS":
        print("ERROR: " + short_id + "... - missing status field. Manual review required.",
              file=sys.stderr)
        sys.exit(1)
    elif result == "SKIP":
        print("SKIP: " + short_id + "... - status is " + str(detail) + ", not OPEN. No write made.")
        sys.exit(0)

    # OK - fetch triaged_at back and echo it
    try:
        updated = doc_ref.get().to_dict() or {}
        triaged_at = _fmt_ts(updated.get("triaged_at"))
    except Exception:
        triaged_at = "(timestamp unavailable)"

    print("TRIAGED: " + short_id + "... | doc_id=" + doc_id +
          " | new_status=TRIAGED | triaged_at=" + triaged_at)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    db = init_firebase()

    if args.triage:
        triage_document(db, args.triage)
        return

    items = fetch_open_items(db, date_str=args.date, limit=args.limit)
    print_report(items, verbose=args.verbose, dry_run=args.dry_run)

    if args.dry_run and items:
        print("DRY-RUN: " + str(len(items)) + " item(s) eligible for --triage. No writes made.")


if __name__ == "__main__":
    main()
