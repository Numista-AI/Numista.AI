"""
purge_test_nicknames.py
=======================
One-shot admin script: deletes all junk TestCoin_XXXX nickname entries
that were inserted by run_overnight_tests.py during API smoke-tests.

Run from the numista_backend directory:
    python scripts/purge_test_nicknames.py

Safe to run multiple times — it is idempotent.
"""

import os
import sys

# ── Resolve paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
VENV_PY     = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")

# Re-execute inside the venv if available
if os.path.exists(VENV_PY) and sys.executable.lower() != os.path.abspath(VENV_PY).lower():
    if "RUNNING_IN_VENV" not in os.environ:
        os.environ["RUNNING_IN_VENV"] = "1"
        import subprocess
        rc = subprocess.call([VENV_PY] + sys.argv)
        sys.exit(rc)

import firebase_admin
from firebase_admin import credentials, firestore

# ── Firebase init ──────────────────────────────────────────────────────────────
KEY_FILE = os.path.join(BACKEND_DIR, "serviceAccountKey.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()
COLLECTION = "coin_nickname_suggestions"

# ── Deletion logic ─────────────────────────────────────────────────────────────
def purge_test_entries() -> int:
    """
    Delete documents that match ANY of:
      1. nickname_lower starts with 'testcoin_'
         (range query: >= 'testcoin_'  AND  < 'testcoin~')
      2. maps_to == 'Test Coin Dollar'  (belt-and-suspenders sweep)
    Returns the total number of documents deleted.
    """
    deleted_ids: set = set()

    # ── Pass 1: nickname_lower prefix scan ────────────────────────────────────
    col = db.collection(COLLECTION)
    docs_pass1 = list(
        col.where("nickname_lower", ">=", "testcoin_")
           .where("nickname_lower", "<",  "testcoin~")
           .stream()
    )
    for doc in docs_pass1:
        if doc.id not in deleted_ids:
            d = doc.to_dict()
            print(f"  [PASS-1] Deleting: '{d.get('nickname')}' -> '{d.get('maps_to')}' "
                  f"(submitted_by={d.get('submitted_by')}, id={doc.id})")
            doc.reference.delete()
            deleted_ids.add(doc.id)

    # ── Pass 2: maps_to == 'Test Coin Dollar' ─────────────────────────────────
    docs_pass2 = list(
        col.where("maps_to", "==", "Test Coin Dollar").stream()
    )
    for doc in docs_pass2:
        if doc.id not in deleted_ids:
            d = doc.to_dict()
            print(f"  [PASS-2] Deleting: '{d.get('nickname')}' -> '{d.get('maps_to')}' "
                  f"(submitted_by={d.get('submitted_by')}, id={doc.id})")
            doc.reference.delete()
            deleted_ids.add(doc.id)

    return len(deleted_ids)


if __name__ == "__main__":
    print("=" * 60)
    print("  Numista.AI - Purge Test Nickname Entries")
    print("=" * 60)
    print(f"\nTarget collection: {COLLECTION}")
    print("Patterns: nickname_lower starts with 'testcoin_'")
    print("          OR maps_to == 'Test Coin Dollar'\n")

    count = purge_test_entries()

    print(f"\n{'=' * 60}")
    print(f"  Done. {count} document(s) deleted.")
    print("=" * 60)
