"""
Numista.AI Legacy Collection Document Migration Script
Idempotently backfills legacy coin documents with structured `cost_basis`, `acquisition_cost_display`,
and append-only `provenance_ledger` arrays.

SAFETY CONTRACT:
1. SKIP document if provenance_ledger array exists and is non-empty.
2. NEVER overwrite cost_basis if it is already a numeric float/int.
3. PRESERVE true null cost_basis for UKN/unpriced items without coercing to 0.00.
4. ALWAYS use SetOptions(merge=True) / merge updates.
5. OUTPUT structured JSON audit log to numista_backend/migration_audit_log.json.
"""

import sys
import os
import json
import argparse
import re
from datetime import datetime, timezone
from uuid import uuid4

# Add parent dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("[WARNING] firebase_admin not installed; dry-run mode only.")
    firebase_admin = None


def parse_legacy_cost(raw_cost_val) -> tuple[Optional[float], str]:
    """
    Parses legacy cost fields into (cost_basis float/None, acquisition_cost_display str).
    """
    if raw_cost_val is None:
        return None, "UKN"
    
    if isinstance(raw_cost_val, (int, float)):
        return float(raw_cost_val), f"${raw_cost_val:.2f}"
    
    raw_str = str(raw_cost_val).strip().upper()
    if raw_str in ["$0.00", "0", "0.00", "FREE", "GIFT", "FOUND", "COIN JAR"]:
        return 0.0, "$0.00"
    elif raw_str in ["UKN", "UNKNOWN", "N/A", "NONE", ""]:
        return None, "UKN"
    else:
        cleaned = re.sub(r'[^\d.]', '', raw_str)
        if cleaned:
            try:
                val = float(cleaned)
                return val, f"${val:.2f}"
            except ValueError:
                pass
        return None, "UKN"


def migrate_collection(dry_run: bool = True):
    audit_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "total_documents_scanned": 0,
        "documents_migrated": 0,
        "documents_skipped": 0,
        "audit_entries": []
    }

    if not firebase_admin:
        print("[MIGRATION] Firebase SDK unavailable. Dry-run completed with 0 remote updates.")
        with open("numista_backend/migration_audit_log.json", "w") as f:
            json.dump(audit_log, f, indent=2)
        return

    # Initialize Firebase if not initialized
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    print(f"[MIGRATION] Scanning users collections (dry_run={dry_run})...")

    users_ref = db.collection("users")
    for user_doc in users_ref.stream():
        uid = user_doc.id
        coins_ref = db.collection("users").document(uid).collection("coins")
        
        for coin_doc in coins_ref.stream():
            audit_log["total_documents_scanned"] += 1
            data = coin_doc.to_dict() or {}
            
            # Safety Rule 1: Skip if ledger exists and non-empty
            existing_ledger = data.get("provenance_ledger")
            if existing_ledger and isinstance(existing_ledger, list) and len(existing_ledger) > 0:
                audit_log["documents_skipped"] += 1
                audit_log["audit_entries"].append({
                    "doc_id": coin_doc.id,
                    "uid": uid,
                    "status": "skipped",
                    "reason": "provenance_ledger_already_exists"
                })
                continue

            updates = {}
            
            # Safety Rule 2 & 3: Cost basis parsing preserving true nulls
            existing_cost_basis = data.get("cost_basis")
            if isinstance(existing_cost_basis, (int, float)):
                cost_basis_val = float(existing_cost_basis)
                display_val = f"${cost_basis_val:.2f}"
            else:
                raw_cost = data.get("Cost") or data.get("acquisition_cost") or data.get("purchase_price")
                cost_basis_val, display_val = parse_legacy_cost(raw_cost)
                updates["cost_basis"] = cost_basis_val
                updates["acquisition_cost_display"] = display_val

            # Construct initial legacy provenance ledger entry
            legacy_prov = data.get("Provenance") or data.get("provenance") or "Initial Ingestion"
            raw_ts = data.get("Purchase Date") or data.get("created_at") or datetime.now(timezone.utc).isoformat()
            if hasattr(raw_ts, 'isoformat'):
                ts_str = raw_ts.isoformat()
            else:
                ts_str = str(raw_ts)

            ledger_entry = {
                "event_id": f"prov_migrated_{uuid4().hex[:8]}",
                "timestamp": ts_str,
                "event_type": "legacy_migration",
                "source_description": str(legacy_prov),
                "raw_user_utterance": f"Migrated from legacy catalog record: {legacy_prov}",
                "cost_basis": cost_basis_val,
                "recorded_by": "System Migration Script"
            }
            updates["provenance_ledger"] = [ledger_entry]

            # Denomination title sanitization
            raw_denom = data.get("denomination") or data.get("Denomination") or "Quarter Dollar"
            sanitized_denom = re.sub(r'\b(Dollar|Cent|Nickel|Dime)\s+\1\b', r'\1', str(raw_denom), flags=re.IGNORECASE).strip()
            if sanitized_denom != raw_denom:
                updates["denomination"] = sanitized_denom

            audit_log["documents_migrated"] += 1
            audit_log["audit_entries"].append({
                "doc_id": coin_doc.id,
                "uid": uid,
                "status": "migrated" if not dry_run else "dry_run_candidate",
                "updates": updates
            })

            if not dry_run and updates:
                coin_doc.reference.set(updates, merge=True)

    print(f"[MIGRATION] Done. Scanned {audit_log['total_documents_scanned']}, Migrated {audit_log['documents_migrated']}, Skipped {audit_log['documents_skipped']}.")
    
    with open("numista_backend/migration_audit_log.json", "w") as f:
        json.dump(audit_log, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate legacy coin documents to V4 schema")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without writing changes")
    args = parser.parse_args()
    migrate_collection(dry_run=args.dry_run)
