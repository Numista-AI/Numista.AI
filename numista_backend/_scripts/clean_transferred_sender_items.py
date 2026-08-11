"""
Database Maintenance CLI Tool — Clean Transferred Sender Items
Numista.AI

Scans active user subcollections ('coins', 'currency', 'banknotes') for residual documents
whose status is 'transferred' or 'claimed'.
In --dry-run mode (default), generates a CSV audit report without modifying data.
In live mode (--dry-run=false), performs batched atomic deletions of residual items.
"""

import sys
import io
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json"
PROJECT_ID = "studio-9101802118-8c9a8"


def init_firestore() -> firestore.Client:
    if not firebase_admin._apps:
        if Path(CRED_PATH).exists():
            cred = credentials.Certificate(CRED_PATH)
            firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
        else:
            firebase_admin.initialize_app()
    return firestore.client()


def clean_user_items(user_email: str, dry_run: bool = True, batch_size: int = 500):
    db = init_firestore()
    clean_email = user_email.strip().lower()
    user_ref = db.collection('users').document(clean_email)

    target_subcols = ['coins', 'currency', 'banknotes']
    terminal_statuses = {'transferred', 'claimed'}

    items_to_clean = []

    print(f"=== SCANNING USER: {clean_email} (dry_run={dry_run}) ===")
    for subcol_name in target_subcols:
        subcol = user_ref.collection(subcol_name)
        docs = list(subcol.stream())
        print(f"  Inspecting subcollection '{subcol_name}': {len(docs)} total documents")

        for doc in docs:
            data = doc.to_dict() or {}
            ts = str(data.get('transferStatus') or data.get('transfer_status') or '').lower()

            if ts in terminal_statuses:
                item_id = doc.id
                title = data.get('Title') or data.get('name') or data.get('Year') or data.get('Denomination') or 'N/A'
                val = data.get('estimated_value') or data.get('AI Estimated Value') or data.get('value') or 0.0
                transfer_id = data.get('transferId') or data.get('transfer_id') or 'N/A'

                # Check archive subcollection for provenance sanity
                archive_subcol = 'transferred_currency' if subcol_name in ['currency', 'banknotes'] else 'transferred_coins'
                archive_snap = user_ref.collection(archive_subcol).document(item_id).get()
                is_archived = archive_snap.exists

                items_to_clean.append({
                    'user_email': clean_email,
                    'subcollection': subcol_name,
                    'document_id': item_id,
                    'transfer_status': ts,
                    'transfer_id': transfer_id,
                    'title': str(title),
                    'value': str(val),
                    'is_archived': is_archived,
                    'doc_ref': doc.reference
                })

    print(f"\nFound {len(items_to_clean)} residual documents with terminal transfer status across '{clean_email}' collections.")

    if not items_to_clean:
        print("No residual items found. Database is clean!")
        return

    # Write CSV audit report
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_filename = f"cleanup_report_{clean_email.replace('@', '_at_')}_{timestamp_str}.csv"

    fieldnames = ['user_email', 'subcollection', 'document_id', 'transfer_status', 'transfer_id', 'title', 'value', 'is_archived']
    with open(report_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items_to_clean:
            row = {k: item[k] for k in fieldnames}
            writer.writerow(row)

    print(f"Audit report saved to: {report_filename}")

    if dry_run:
        print("\n[DRY RUN COMPLETE] No records were deleted. Run with --dry-run=false to execute deletions.")
        return

    # Execute batched atomic deletions
    print(f"\n[EXECUTING DELETIONS] Deleting {len(items_to_clean)} items in batches of {batch_size}...")

    deleted_count = 0
    batch = db.batch()
    batch_count = 0

    for item in items_to_clean:
        batch.delete(item['doc_ref'])
        batch_count += 1
        deleted_count += 1

        if batch_count >= batch_size:
            batch.commit()
            print(f"  Committed batch of {batch_count} deletions...")
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
        print(f"  Committed final batch of {batch_count} deletions.")

    print(f"\nSUCCESS: Deleted {deleted_count} residual documents from '{clean_email}'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clean residual transferred/claimed documents from active user collections.")
    parser.add_argument("--user_email", type=str, required=True, help="Target user email address (e.g. eric@numista.ai)")
    parser.add_argument("--dry-run", type=str, default="true", help="Set to 'false' to execute deletions")
    parser.add_argument("--batch-size", type=int, default=500, help="Firestore batch size limit (max 500)")

    args = parser.parse_args()
    is_dry_run = args.dry_run.lower() != "false"

    clean_user_items(
        user_email=args.user_email,
        dry_run=is_dry_run,
        batch_size=args.batch_size
    )
