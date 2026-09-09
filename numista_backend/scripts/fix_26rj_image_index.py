#!/usr/bin/env python3
"""
fix_26rj_image_index.py
=======================
Remediates 8 poisoned documents in the Firestore `coin_image_index` collection
that mistakenly mapped 2026 Uncirculated Set keys to Marine Corps 250th
commemorative images.

Project:
    studio-9101802118-8c9a8

Target Collection:
    coin_image_index

Target Documents:
    - 2026_semiquincentennial_obverse
    - 2026_semiquincentennial_reverse
    - 2026_set_obverse
    - 2026_set_reverse
    - 2026_uncirculated-set_obverse
    - 2026_uncirculated-set_reverse
    - 2026_uncirculated-sets_obverse
    - 2026_uncirculated-sets_reverse

Safety Controls:
    - WRONG_URL_FRAGMENT check: Requires 'marine-corps' in current public_url.
      Refuses update if missing (already corrected or mismatched doc).
    - Uses atomic batch writes with merge=True to preserve other nested/top-level fields.
    - Default mode is dry-run. Requires explicit --execute flag to write.

Usage:
    python fix_26rj_image_index.py             # Dry-run preview (default)
    python fix_26rj_image_index.py --dry-run   # Explicit dry-run
    python fix_26rj_image_index.py --execute   # Atomic Firestore update
"""

import argparse
from datetime import datetime, timezone
import io
import os
import sys
from typing import Dict, List, Optional, Tuple

# Ensure UTF-8 output formatting on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
elif sys.stdout and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

from google.cloud import firestore
from google.oauth2 import service_account
import google.auth

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
COLLECTION_NAME = "coin_image_index"

TARGET_DOCUMENTS: List[str] = [
    "2026_semiquincentennial_obverse",
    "2026_semiquincentennial_reverse",
    "2026_set_obverse",
    "2026_set_reverse",
    "2026_uncirculated-set_obverse",
    "2026_uncirculated-set_reverse",
    "2026_uncirculated-sets_obverse",
    "2026_uncirculated-sets_reverse",
]

OBVERSE_REPLACEMENT_URL = (
    "https://storage.googleapis.com/numista-reference-library/reference_library/"
    "user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_c.jpg"
)
REVERSE_REPLACEMENT_URL = (
    "https://storage.googleapis.com/numista-reference-library/reference_library/"
    "user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg"
)

ATTRIBUTION = "US Mint / Eric Admin Contribution"
WRONG_URL_FRAGMENT = "marine-corps"


def get_firestore_client(project_id: str = PROJECT_ID) -> firestore.Client:
    """
    Initializes and returns a Google Cloud Firestore client.
    Checks GOOGLE_APPLICATION_CREDENTIALS, local serviceAccountKey files,
    and falls back to Application Default Credentials (ADC).
    """
    env_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_creds and os.path.exists(env_creds):
        creds = service_account.Credentials.from_service_account_file(env_creds)
        return firestore.Client(project=project_id, credentials=creds)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    candidate_keys = [
        os.path.join(backend_dir, "serviceAccountKey.json"),
        os.path.join(backend_dir, "serviceAccountKey.json.json"),
        os.path.join(script_dir, "serviceAccountKey.json"),
        os.path.join(script_dir, "serviceAccountKey.json.json"),
        os.path.join(os.getcwd(), "serviceAccountKey.json"),
        os.path.join(os.getcwd(), "serviceAccountKey.json.json"),
    ]

    for key_path in candidate_keys:
        if os.path.exists(key_path):
            creds = service_account.Credentials.from_service_account_file(key_path)
            return firestore.Client(project=project_id, credentials=creds)

    creds, _ = google.auth.default()
    return firestore.Client(project=project_id, credentials=creds)


def determine_side_and_url(doc_id: str) -> Tuple[str, str]:
    """
    Determines coin side ('obverse' or 'reverse') and target replacement URL
    based on the document ID suffix.
    """
    if doc_id.endswith("_obverse"):
        return "obverse", OBVERSE_REPLACEMENT_URL
    elif doc_id.endswith("_reverse"):
        return "reverse", REVERSE_REPLACEMENT_URL
    else:
        raise ValueError(f"Document ID '{doc_id}' does not end with '_obverse' or '_reverse'.")


def run_fix(execute: bool = False) -> int:
    """
    Reads target documents, verifies preconditions, and performs dry-run inspection
    or atomic batch write to Firestore.
    
    Returns exit code (0 for success, non-zero on critical errors).
    """
    mode_str = "EXECUTE" if execute else "DRY-RUN"
    print("=" * 80)
    print(f"Numista.AI - Fix 2026 Uncirculated Set Image Index ({mode_str} MODE)")
    print(f"Project:    {PROJECT_ID}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents:  {len(TARGET_DOCUMENTS)} target IDs")
    print(f"Safety:     WRONG_URL_FRAGMENT = '{WRONG_URL_FRAGMENT}'")
    print("=" * 80)

    try:
        db = get_firestore_client(PROJECT_ID)
    except Exception as e:
        print(f"[FATAL] Failed to initialize Firestore client: {e}")
        return 1

    col_ref = db.collection(COLLECTION_NAME)

    docs_to_update: List[Dict] = []
    skipped_count = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    print("\n--- Inspecting Target Documents ---")
    for doc_id in TARGET_DOCUMENTS:
        try:
            side, replacement_url = determine_side_and_url(doc_id)
        except ValueError as err:
            print(f"[ERROR] Invalid document ID format for {doc_id}: {err}")
            skipped_count += 1
            continue

        doc_ref = col_ref.document(doc_id)
        doc_snap = doc_ref.get()

        if not doc_snap.exists:
            print(f"[WARN] Document '{doc_id}' DOES NOT EXIST in Firestore! Skipping.")
            skipped_count += 1
            continue

        doc_data = doc_snap.to_dict() or {}
        side_data = doc_data.get(side, {})
        current_url = side_data.get("public_url", "")
        current_attribution = side_data.get("attribution", "N/A")

        print(f"\nDocument:    {doc_id}")
        print(f"  Side:        {side}")
        print(f"  Current URL: {current_url}")
        print(f"  Current Att: {current_attribution}")

        # Safety Check: Current URL must contain WRONG_URL_FRAGMENT
        if WRONG_URL_FRAGMENT not in current_url:
            print(
                f"  [SAFETY REFUSAL] Current URL does NOT contain '{WRONG_URL_FRAGMENT}'. "
                f"Document may already be fixed or unrelated. Skipping write."
            )
            skipped_count += 1
            continue

        print(f"  [CONFIRMED] Contains '{WRONG_URL_FRAGMENT}'. Eligible for remediation.")
        print(f"  Proposed Changes:")
        print(f"    - {side}.public_url  -> {replacement_url}")
        print(f"    - {side}.attribution -> {ATTRIBUTION}")
        print(f"    - {side}.indexed_at  -> {now_iso}")

        docs_to_update.append({
            "doc_id": doc_id,
            "doc_ref": doc_ref,
            "side": side,
            "replacement_url": replacement_url,
            "current_url": current_url,
        })

    print("\n" + "=" * 80)
    print(f"Inspection Summary: {len(docs_to_update)} to update, {skipped_count} skipped.")
    print("=" * 80)

    if not execute:
        print("\n[DRY-RUN] No writes performed. Use --execute to commit these changes to Firestore.")
        return 0

    if not docs_to_update:
        print("\n[INFO] No documents require updates. Exiting.")
        return 0

    print(f"\n--- Executing Atomic Batch Write for {len(docs_to_update)} Documents ---")
    batch = db.batch()

    for item in docs_to_update:
        doc_ref = item["doc_ref"]
        side = item["side"]
        replacement_url = item["replacement_url"]

        # Prepare nested map update with merge=True
        update_data = {
            side: {
                "public_url": replacement_url,
                "attribution": ATTRIBUTION,
                "indexed_at": now_iso,
            }
        }
        batch.set(doc_ref, update_data, merge=True)

    try:
        batch.commit()
    except Exception as e:
        print(f"[FATAL] Failed to commit Firestore batch write: {e}")
        return 1

    print("\n--- Update Confirmations ---")
    for item in docs_to_update:
        print(f"  [UPDATED] {item['doc_id']}")
        print(f"    New URL:     {item['replacement_url']}")
        print(f"    Attribution: {ATTRIBUTION}")
        print(f"    Timestamp:   {now_iso}")

    print("\n" + "=" * 80)
    print(f"Execution Complete: {len(docs_to_update)} docs updated successfully.")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Fix poisoned 2026 Uncirculated Set image index entries in Firestore coin_image_index."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--execute",
        action="store_true",
        help="Commit image URL and attribution updates to Firestore (atomic batch).",
    )
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate changes without writing (default).",
    )

    args = parser.parse_args()

    # Dry-run is default unless --execute is explicitly passed
    is_execute = bool(args.execute)
    exit_code = run_fix(execute=is_execute)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
