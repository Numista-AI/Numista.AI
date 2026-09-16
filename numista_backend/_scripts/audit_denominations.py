#!/usr/bin/env python3
"""
Denomination Audit & Normalization Tool (GI-NOM-01)
Read-only dry-run audit of coin denominations against formal US Mint nomenclature.

Safety Rails:
  - Defaults to dry-run (no DB writes).
  - Strictly locked to grokbot@numista.ai (never touches production users).
  - Uses canonical denomination normalizer from numista_backend/services/denomination_normalizer.py.

Usage:
  python _scripts/audit_denominations.py             # dry-run audit for grokbot@numista.ai
  python _scripts/audit_denominations.py --apply     # apply updates to grokbot only
"""

import os
import sys
import argparse
from typing import Dict, Any, List

# Ensure backend root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

import firebase_admin
from firebase_admin import credentials, firestore
from services.denomination_normalizer import (
    normalize_denomination,
    infer_denomination_from_program,
    get_canonical_us_denominations,
    is_valid_us_denomination,
    CANONICAL_US_CIRCULATING,
)

TARGET_EMAIL = "grokbot@numista.ai"
PROJECT_ID = "studio-9101802118-8c9a8"
SA_KEY_PATH = os.path.join(BACKEND_ROOT, "serviceAccountKey.json")


def init_db():
    if not firebase_admin._apps:
        if os.path.exists(SA_KEY_PATH):
            cred = credentials.Certificate(SA_KEY_PATH)
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": PROJECT_ID})
    return firestore.client()


def get_target_user_id(db, email: str = TARGET_EMAIL) -> str:
    """Resolve UID for target user while enforcing safety lock."""
    if email.lower() != TARGET_EMAIL.lower():
        raise ValueError(f"CRITICAL SAFETY VIOLATION: Target user '{email}' is NOT allowed. Only '{TARGET_EMAIL}' permitted.")
    
    users = list(db.collection("users").where("email", "==", email).limit(1).stream())
    if not users:
        # Fallback query users by document ID or search
        for doc in db.collection("users").stream():
            d = doc.to_dict() or {}
            if d.get("email", "").lower() == email.lower():
                return doc.id
        raise RuntimeError(f"Target test user {email} not found in Firestore.")
    return users[0].id


def audit_user_denominations(db, user_id: str, apply: bool = False):
    print(f"\n==================================================")
    print(f"  US Mint Denomination Audit (GI-NOM-01)")
    print(f"  User: {TARGET_EMAIL} ({user_id})")
    print(f"  Mode: {'APPLY CHANGES' if apply else 'DRY-RUN (READ-ONLY)'}")
    print(f"==================================================\n")

    coins_ref = db.collection("users").document(user_id).collection("coins")
    coins = list(coins_ref.stream())

    total = len(coins)
    canonical_count = 0
    normalized_count = 0
    inferred_count = 0
    blank_count = 0
    unrecognized_count = 0

    diffs: List[Dict[str, Any]] = []

    for doc in coins:
        data = doc.to_dict() or {}
        raw_denom = data.get("Denomination") or data.get("denomination") or ""
        program = data.get("Program/Series") or data.get("program_series") or ""
        theme = data.get("Theme/Subject") or data.get("theme_subject") or ""
        year = data.get("Year") or data.get("year") or ""
        item_type = data.get("item_type") or "coin"

        canonical, was_corrected, original = normalize_denomination(raw_denom, item_type=item_type)
        was_inferred = False

        if (not canonical or canonical.strip().lower() in ["denomination missing?", "unknown", "missing"]) and program:
            inferred = infer_denomination_from_program(program)
            if inferred:
                canonical = inferred
                was_corrected = True
                was_inferred = True

        raw_str = str(raw_denom).strip()
        target_denom = canonical

        if not raw_str:
            blank_count += 1
            if target_denom:
                diffs.append({
                    "id": doc.id,
                    "desc": f"{year} {program} ({theme})",
                    "from": "<blank>",
                    "to": target_denom,
                    "action": "INFERRED" if was_inferred else "NORMALIZED",
                    "doc_ref": doc.reference,
                })
        elif raw_str == target_denom:
            canonical_count += 1
        elif target_denom:
            if was_inferred:
                inferred_count += 1
                action = "INFERRED"
            else:
                normalized_count += 1
                action = "MODERNIZE"
            diffs.append({
                "id": doc.id,
                "desc": f"{year} {program} ({theme})",
                "from": raw_str,
                "to": target_denom,
                "action": action,
                "doc_ref": doc.reference,
            })
        else:
            unrecognized_count += 1
            diffs.append({
                "id": doc.id,
                "desc": f"{year} {program} ({theme})",
                "from": raw_str,
                "to": "<unrecognized>",
                "action": "FLAGGED",
                "doc_ref": doc.reference,
            })

    print(f"Total coins inspected:    {total}")
    print(f"Already Canonical:        {canonical_count}")
    print(f"Candidates to Modernize:  {normalized_count}")
    print(f"Inferred from Program:    {inferred_count}")
    print(f"Blank / Missing:          {blank_count}")
    print(f"Unrecognized / Foreign:   {unrecognized_count}\n")

    if diffs:
        print(f"{'ACTION':<12} {'CURRENT':<20} {'PROPOSED':<20} {'COIN':<35}")
        print("-" * 90)
        for d in diffs[:40]:  # Show first 40 for brevity
            print(f"{d['action']:<12} {d['from']:<20} {d['to']:<20} {d['desc'][:35]:<35}")
        if len(diffs) > 40:
            print(f"... and {len(diffs) - 40} more.")

    if apply and diffs:
        print(f"\nApplying updates to Firestore for {len(diffs)} coins...")
        batch = db.batch()
        count = 0
        for d in diffs:
            if d["to"] not in ("<unrecognized>", "<blank>"):
                batch.update(d["doc_ref"], {"Denomination": d["to"]})
                count += 1
                if count % 450 == 0:
                    batch.commit()
                    batch = db.batch()
        if count % 450 != 0:
            batch.commit()
        print(f"Successfully applied {count} denomination updates to {TARGET_EMAIL}.")
    else:
        print(f"\n[DRY-RUN COMPLETE] No database changes written.")


def main():
    parser = argparse.ArgumentParser(description="Audit and normalize denominations for grokbot")
    parser.add_argument("--apply", action="store_true", help="Apply updates to grokbot@numista.ai only")
    args = parser.parse_args()

    db = init_db()
    uid = get_target_user_id(db)
    audit_user_denominations(db, uid, apply=args.apply)


if __name__ == "__main__":
    main()
