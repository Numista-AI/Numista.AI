# -*- coding: utf-8 -*-
"""
auto_resolve_audit.py
---------------------
Reads the latest Numista.AI nightly audit from Firestore and automatically
triages each flagged item into one of three buckets:

  AUTO_FIXED      - Issue resolved directly (e.g. missing image filled from
                    the SQLite reference DB). Firestore record updated.
  NEEDS_REVIEW    - Conflicting or ambiguous data; sets review_needed=True on
                    the coin/currency doc so it surfaces in the Admin Review Hub.
  INFORMATIONAL   - Low-priority note (e.g. missing PCGS cert on a raw coin).
                    Logged in the audit doc but no Firestore record modified.

Nothing is deleted. Auto-fixes only add or correct missing fields.
The script writes a resolution_summary back to the audit Firestore document.

Scheduled to run at 2:30 AM (30 minutes after nightly_data_audit.py).
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone
from google.oauth2 import service_account
from google.cloud import firestore

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Configuration ───────────────────────────────────────────────────────────
PROJECT_ID       = "studio-9101802118-8c9a8"
CREDENTIALS_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
SQLITE_DB        = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"
MAX_AUTO_FIXES   = 200   # Safety cap: never auto-fix more than 200 records per run


def get_db_client():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return firestore.Client(project=PROJECT_ID, credentials=credentials)


def get_sqlite_conn():
    """Open the local SQLite reference DB if available."""
    if os.path.exists(SQLITE_DB):
        return sqlite3.connect(SQLITE_DB)
    return None


def lookup_reference_images(sqlite_conn, coin_id: str) -> dict:
    """Try to find reference image URLs for a coin_id in the local SQLite DB."""
    if sqlite_conn is None:
        return {}
    try:
        cur = sqlite_conn.cursor()
        # Try by document ID (Firestore doc ID often matches a catalog number)
        cur.execute(
            "SELECT obverse_img, reverse_img FROM coins WHERE id = ? OR catalog_id = ? LIMIT 1",
            (coin_id, coin_id)
        )
        row = cur.fetchone()
        if row and (row[0] or row[1]):
            return {"image_url_obverse": row[0] or "", "image_url_reverse": row[1] or ""}
    except Exception:
        pass
    return {}


def resolve_item(db, sqlite_conn, item: dict, auto_fix_count: list) -> str:
    """
    Evaluate a single flagged item and attempt resolution.
    Returns: "AUTO_FIXED" | "NEEDS_REVIEW" | "INFORMATIONAL"
    """
    issues   = item.get("issues", [])
    user     = item.get("user_email", "")
    item_id  = item.get("id", "")
    item_type = item.get("type", "coin")  # "coin" or "currency"

    if not issues or not user or not item_id:
        return "INFORMATIONAL"

    collection = "coins" if item_type == "coin" else "currency"
    doc_ref = db.collection("users").document(user).collection(collection).document(item_id)

    # ── Triage logic ────────────────────────────────────────────────────────

    has_missing_image = any("image" in i.lower() for i in issues)
    has_year_mismatch  = any("mismatch" in i.lower() for i in issues)
    has_missing_denom  = any("denomination" in i.lower() for i in issues)
    has_missing_year   = any("missing year" in i.lower() for i in issues)

    # 1. Year-mismatch in image URL → needs human judgement (cannot auto-fix safely)
    if has_year_mismatch:
        if auto_fix_count[0] < MAX_AUTO_FIXES:
            try:
                doc_ref.update({"review_needed": True, "review_reason": "Image URL year mismatch detected by nightly audit"})
            except Exception:
                pass
        return "NEEDS_REVIEW"

    # 2. Missing image → try to fill from SQLite reference DB
    if has_missing_image and not has_year_mismatch:
        if auto_fix_count[0] < MAX_AUTO_FIXES:
            ref_imgs = lookup_reference_images(sqlite_conn, item_id)
            if ref_imgs:
                try:
                    update_payload = {k: v for k, v in ref_imgs.items() if v}
                    if update_payload:
                        doc_ref.update(update_payload)
                        auto_fix_count[0] += 1
                        return "AUTO_FIXED"
                except Exception:
                    pass
        # Could not fix — flag for review
        try:
            doc_ref.update({"review_needed": True, "review_reason": "Missing coin images — reference images not found in catalog DB"})
        except Exception:
            pass
        return "NEEDS_REVIEW"

    # 3. Missing denomination or year on raw coin — informational (no safe auto-fill)
    if has_missing_denom or has_missing_year:
        return "INFORMATIONAL"

    # Fallback
    return "INFORMATIONAL"


def main():
    print("=" * 70)
    print("  NUMISTA.AI -- NIGHTLY AUDIT AUTO-RESOLVER")
    print("=" * 70)

    if not os.path.exists(CREDENTIALS_FILE):
        sys.exit(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")

    db = get_db_client()
    sqlite_conn = get_sqlite_conn()

    if sqlite_conn:
        print("  SQLite reference DB     : Connected")
    else:
        print("  SQLite reference DB     : NOT FOUND (image lookup disabled)")

    # Load the latest audit document
    today_key   = f"audit_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    report_ref  = db.collection("weekly_audits").document(today_key)
    report_snap = report_ref.get()

    if not report_snap.exists:
        print(f"\n  No audit document found for today ({today_key}). Run nightly_data_audit.py first.")
        sys.exit(0)

    report_data     = report_snap.to_dict()
    flagged_items   = report_data.get("flagged_items", [])
    total_flagged   = report_data.get("flagged_items_count", len(flagged_items))

    print(f"\n  Audit document          : {today_key}")
    print(f"  Total flagged items     : {total_flagged}")
    print(f"  Items in doc (capped)   : {len(flagged_items)}")
    print()

    auto_fixed    = []
    needs_review  = []
    informational = []
    auto_fix_count = [0]   # mutable counter

    for item in flagged_items:
        result = resolve_item(db, sqlite_conn, item, auto_fix_count)
        entry = {
            "id":         item.get("id"),
            "user_email": item.get("user_email"),
            "name":       item.get("name"),
            "issues":     item.get("issues"),
            "resolution": result
        }
        if result == "AUTO_FIXED":
            auto_fixed.append(entry)
            print(f"  ✅ AUTO_FIXED   : {item.get('name', item.get('id'))}")
        elif result == "NEEDS_REVIEW":
            needs_review.append(entry)
        else:
            informational.append(entry)

    # Write resolution summary back to the audit Firestore doc
    resolution_summary = {
        "resolution_run_at":    datetime.now(timezone.utc).isoformat(),
        "auto_fixed_count":     len(auto_fixed),
        "needs_review_count":   len(needs_review),
        "informational_count":  len(informational),
        "auto_fixed_items":     auto_fixed[:50],
        "needs_review_items":   needs_review[:50],
    }
    try:
        report_ref.update({"resolution_summary": resolution_summary, "status": "RESOLVED"})
        print(f"\n  [OK] Resolution summary written to Firestore: weekly_audits/{today_key}")
    except Exception as e:
        print(f"\n  [ERROR] Failed to write resolution summary: {e}")

    if sqlite_conn:
        sqlite_conn.close()

    print()
    print("=" * 70)
    print("  AUTO-RESOLVER SUMMARY")
    print("=" * 70)
    print(f"  Auto-Fixed (Firestore updated) : {len(auto_fixed)}")
    print(f"  Flagged for Review             : {len(needs_review)}")
    print(f"  Informational (no action)      : {len(informational)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
