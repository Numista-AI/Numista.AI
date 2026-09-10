#!/usr/bin/env python3
"""
fix_26rj_hero.py — Swap 26RJ hero to dual-pack shot (26rj_a.jpg)

Updates:
  1. Eric's parent doc image_url_obverse → 26rj_a.jpg (ERIC-ONLY)
  2. 4 global coin_image_index obverse keys → 26rj_a.jpg (GLOBAL)

Usage:
    python fix_26rj_hero.py --dry-run     # Preview (default)
    python fix_26rj_hero.py --execute     # Write to Firestore
"""
import argparse, datetime, io, os, sys
from google.cloud import firestore
from google.oauth2 import service_account
import google.auth

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ID = "studio-9101802118-8c9a8"
HERO_URL = (
    "https://storage.googleapis.com/numista-reference-library/reference_library/"
    "user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg"
)
ERIC_DOC_PATH = "users/eric.seaman@yahoo.com/coins/71e2d4ae92bc4312a4198a3a0cc21fcb"
INDEX_OBVERSE_DOCS = [
    "2026_uncirculated-sets_obverse",
    "2026_uncirculated-set_obverse",
    "2026_set_obverse",
    "2026_semiquincentennial_obverse",
]
ATTRIBUTION = "US Mint / Eric Admin Contribution"

def get_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    for p in [
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        os.path.join(backend_dir, "serviceAccountKey.json"),
        os.path.join(script_dir, "serviceAccountKey.json"),
        os.path.join(os.getcwd(), "numista_backend", "serviceAccountKey.json"),
    ]:
        if p and os.path.exists(p):
            creds = service_account.Credentials.from_service_account_file(p)
            return firestore.Client(project=PROJECT_ID, credentials=creds)
    creds, _ = google.auth.default()
    return firestore.Client(project=PROJECT_ID, credentials=creds)

def main():
    parser = argparse.ArgumentParser(description="Swap 26RJ hero to dual-pack 26rj_a.jpg")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--execute", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    execute = args.execute
    mode = "EXECUTE" if execute else "DRY-RUN"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    print("=" * 70)
    print(f"26RJ Dual-Pack Hero Swap ({mode})")
    print(f"Hero URL: ...26rj_a.jpg")
    print("=" * 70)

    db = get_db()

    # --- Action 1: Eric's doc ---
    print("\n--- Action 1: Eric's Parent Document ---")
    eric_ref = db.document(ERIC_DOC_PATH)
    eric_snap = eric_ref.get()
    if not eric_snap.exists:
        print("[ERROR] Eric's doc not found!")
        return 1
    ed = eric_snap.to_dict()
    cur_obv = ed.get("image_url_obverse", "N/A")
    cur_rev = ed.get("image_url_reverse", "N/A")
    print(f"  Current obverse: {cur_obv}")
    print(f"  Current reverse: {cur_rev}")
    eric_needs_update = "26rj_a" not in cur_obv
    if eric_needs_update:
        print(f"  [CHANGE] obverse → ...26rj_a.jpg")
    else:
        print("  [ALREADY DONE] Obverse is already dual-pack hero.")

    # --- Action 2: 4 global index keys ---
    print("\n--- Action 2: Global coin_image_index Obverse Keys ---")
    index_updates = []
    for doc_id in INDEX_OBVERSE_DOCS:
        ref = db.collection("coin_image_index").document(doc_id)
        snap = ref.get()
        if not snap.exists:
            print(f"  [{doc_id}] NOT FOUND — skip")
            continue
        cur = snap.to_dict().get("obverse", {}).get("public_url", "N/A")
        print(f"  [{doc_id}] Current: ...{cur.split('/')[-1] if '/' in cur else cur}")
        if "26rj_a" in cur:
            print(f"    [ALREADY DONE]")
        else:
            print(f"    [CHANGE] → ...26rj_a.jpg")
            index_updates.append((doc_id, ref))

    total = (1 if eric_needs_update else 0) + len(index_updates)
    print(f"\n{'=' * 70}")
    print(f"Summary: {total} document(s) to update.")
    print(f"{'=' * 70}")

    if not execute:
        print("\n[DRY-RUN] No writes. Use --execute to commit.")
        return 0
    if total == 0:
        print("\n[INFO] Nothing to update.")
        return 0

    batch = db.batch()
    if eric_needs_update:
        batch.set(eric_ref, {"image_url_obverse": HERO_URL}, merge=True)
        print(f"\n  [QUEUED] Eric obverse → 26rj_a.jpg")
    for doc_id, ref in index_updates:
        batch.set(ref, {
            "obverse": {
                "public_url": HERO_URL,
                "attribution": ATTRIBUTION,
                "indexed_at": now_iso,
            }
        }, merge=True)
        print(f"  [QUEUED] {doc_id} → 26rj_a.jpg")

    batch.commit()
    print(f"\n[SUCCESS] {total} document(s) updated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
