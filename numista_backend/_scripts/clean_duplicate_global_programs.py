"""
numista_backend/_scripts/clean_duplicate_global_programs.py

Purges 0-coin ghost program documents and duplicate program entries from Firestore
'global_programs' collection in project studio-9101802118-8c9a8.

Usage:
  python clean_duplicate_global_programs.py --dry-run
  python clean_duplicate_global_programs.py --execute
"""

import sys
import argparse
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    parser = argparse.ArgumentParser(description="Clean duplicate and 0-coin ghost programs from Firestore.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Perform dry run without deleting docs (default)")
    parser.add_argument("--execute", action="store_true", help="Perform actual deletion in Firestore")
    args = parser.parse_args()

    is_dry_run = not args.execute

    print("==================================================================")
    print(f"  Firestore Program Cleanup Script {'[DRY RUN]' if is_dry_run else '[LIVE EXECUTION]'}")
    print("==================================================================")

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    
    db = firestore.client()
    collection_ref = db.collection("global_programs")
    docs = list(collection_ref.stream())

    print(f"Total documents in 'global_programs': {len(docs)}\n")

    # Group by title / display name
    grouped = {}
    for doc in docs:
        d = doc.to_dict()
        title = (d.get("name") or d.get("Name") or "").strip()
        coins = d.get("coins") or d.get("Coins") or []
        doc_info = {
            "id": doc.id,
            "title": title,
            "coins_count": len(coins),
            "ref": doc.reference
        }
        grouped.setdefault(title, []).append(doc_info)

    to_delete = []

    for title, doc_list in grouped.items():
        if not title:
            # Document without title
            for d in doc_list:
                print(f"[Ghost] Doc ID: '{d['id']}' has no title. Marked for deletion.")
                to_delete.append(d)
            continue

        # Sort docs: highest coins_count first, then lexicographically smallest ID
        doc_list.sort(key=lambda x: (-x["coins_count"], x["id"]))

        canonical = doc_list[0]
        if canonical["coins_count"] == 0:
            print(f"[WARNING] Program '{title}' (ID: {canonical['id']}) has 0 coins across all docs.")

        print(f"Program: '{title}'")
        print(f"  -> Keep Canonical: ID '{canonical['id']}' ({canonical['coins_count']} coins)")

        for duplicate in doc_list[1:]:
            print(f"  -> Duplicate Delete: ID '{duplicate['id']}' ({duplicate['coins_count']} coins)")
            to_delete.append(duplicate)

        # Also purge any document whose coin count is 0 if a canonical document with >0 coins exists
        for d in doc_list:
            if d != canonical and d["coins_count"] == 0 and d not in to_delete:
                print(f"  -> Ghost Delete: ID '{d['id']}' (0 coins)")
                to_delete.append(d)

    print("\n------------------------------------------------------------------")
    print(f"Total documents marked for deletion: {len(to_delete)}")
    for d in to_delete:
        print(f"  - {d['id']} ('{d['title']}', {d['coins_count']} coins)")
    print("------------------------------------------------------------------")

    if is_dry_run:
        print("\n[DRY RUN COMPLETE] No documents were deleted. Pass --execute to apply changes.")
    else:
        print("\n[EXECUTING DELETIONS] Deleting marked documents from Firestore...")
        deleted_count = 0
        for d in to_delete:
            try:
                collection_ref.document(d["id"]).delete()
                deleted_count += 1
                print(f"  Successfully deleted doc: {d['id']}")
            except Exception as e:
                print(f"  ERROR deleting doc {d['id']}: {e}")
        print(f"\n[COMPLETE] Deleted {deleted_count} ghost/duplicate documents.")

if __name__ == "__main__":
    main()
