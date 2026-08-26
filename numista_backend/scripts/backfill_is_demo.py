#!/usr/bin/env python3
"""
backfill_is_demo.py
===================
ADDENDUM A — ITEM 6 prerequisite backfill job
Run this ONCE on dev before shipping the client WHERE is_demo == false display filter.

What it does
------------
Sets is_demo: false and is_demo_cleared: false on every users/{uid}/coins document that:
  (a) does NOT have the is_demo field, OR
  (b) has is_demo == None (field exists but is null)

What it NEVER touches
---------------------
  - Documents where is_demo == True (live or soft-archived demo coins)
  - Any other collection

Idempotency
-----------
A second run updates 0 documents (predicate: skip when field exists and is bool).

Usage
-----
  python numista_backend/scripts/backfill_is_demo.py --dry-run   # preview
  python numista_backend/scripts/backfill_is_demo.py             # execute

Output
------
  backfill_is_demo_<timestamp>.log (also stdout)
  Final line: BACKFILL COMPLETE: N updated, M skipped (demo), K already-set
  Place this log in the sprint folder as the deploy gate evidence.
"""

import argparse
import datetime
import logging
import sys
import os

_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
_log_file = f"backfill_is_demo_{_ts}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger("backfill_is_demo")


def get_firestore_client():
    import firebase_admin
    from firebase_admin import credentials, firestore as admin_firestore

    key_candidates = [
        os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "serviceAccountKey.json"),
        "serviceAccountKey.json",
    ]
    key_file = None
    for candidate in key_candidates:
        if os.path.exists(candidate):
            key_file = os.path.abspath(candidate)
            break

    if not firebase_admin._apps:
        if key_file:
            cred = credentials.Certificate(key_file)
            firebase_admin.initialize_app(cred)
            log.info(f"Initialized Firebase Admin SDK from: {key_file}")
        else:
            firebase_admin.initialize_app()
            log.info("Initialized Firebase Admin SDK via Application Default Credentials")

    return admin_firestore.client()


def run_backfill(dry_run: bool = False) -> dict:
    """
    Scan all users/{uid}/coins documents via collection-group query.
    Patch only docs where is_demo is missing or None.
    Skip docs where is_demo is True (demo/soft-archived) — NEVER overwrite.
    Skip docs where is_demo is already False (already set).
    """
    db = get_firestore_client()

    updated = 0
    skipped_demo = 0
    already_set = 0
    errors = 0

    BATCH_SIZE = 400
    batch = db.batch()
    batch_count = 0

    mode = "DRY-RUN" if dry_run else "EXECUTE"
    log.info(f"=== Backfill starting [{mode}] ===")

    coins_group = db.collection_group("coins")

    doc_count = 0
    for doc_ref in coins_group.stream():
        doc_count += 1
        if doc_count % 500 == 0:
            log.info(f"  Scanned {doc_count} docs (updated={updated}, "
                     f"skipped_demo={skipped_demo}, already_set={already_set})")

        try:
            data = doc_ref.to_dict()
            if data is None:
                continue

            is_demo_val = data.get("is_demo", "__MISSING__")

            if is_demo_val is True:
                skipped_demo += 1
                continue

            if is_demo_val is False:
                already_set += 1
                continue

            # Missing or None: needs backfill
            if not dry_run:
                batch.update(doc_ref.reference, {
                    "is_demo": False,
                    "is_demo_cleared": False,
                })
                batch_count += 1

                if batch_count >= BATCH_SIZE:
                    batch.commit()
                    log.info(f"  Committed batch of {batch_count} docs")
                    batch = db.batch()
                    batch_count = 0

            updated += 1

        except Exception as e:
            log.error(f"  ERROR on {doc_ref.reference.path}: {e}")
            errors += 1

    if not dry_run and batch_count > 0:
        batch.commit()
        log.info(f"  Committed final batch of {batch_count} docs")

    result = dict(updated=updated, skipped_demo=skipped_demo,
                  already_set=already_set, errors=errors,
                  total_scanned=doc_count, dry_run=dry_run)

    log.info("=" * 60)
    log.info(f"BACKFILL {'[DRY-RUN]' if dry_run else 'COMPLETE'}:")
    log.info(f"  Total docs scanned : {doc_count}")
    log.info(f"  Updated            : {updated}")
    log.info(f"  Skipped (demo)     : {skipped_demo}  (is_demo==True - NOT touched)")
    log.info(f"  Already set        : {already_set}  (is_demo==False - no change)")
    log.info(f"  Errors             : {errors}")
    log.info("=" * 60)
    log.info(f"Log: {os.path.abspath(_log_file)}")
    log.info("DEPLOY GATE: place this log in the sprint folder before shipping "
             "the client WHERE is_demo == false display filter.")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill is_demo: false on pre-sprint coins")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing to Firestore")
    args = parser.parse_args()

    result = run_backfill(dry_run=args.dry_run)
    sys.exit(0 if result["errors"] == 0 else 1)
