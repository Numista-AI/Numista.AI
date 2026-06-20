"""
cleanup_aj_restore.py
──────────────────────────────────────────────────────────────────────────────
Post-restore cleanup for jseaman1204@gmail.com:

1. Delete orphan coin (9ab78fe0) — no year/program/denomination/image data
2. Fix 2 AI-generated coins with gs:// internal URLs:
     • 1954-S Franklin Half Dollar  (0002c0f9)
     • 2010-D Lincoln Cent          (001e17fe)
   Converts the gs:// GCS path to a public HTTPS storage URL and makes
   the GCS objects publicly readable if not already.

Usage:
    python _scripts/cleanup_aj_restore.py --dry-run
    python _scripts/cleanup_aj_restore.py
"""

import os, sys, re, argparse

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore, storage

PROJECT      = "studio-9101802118-8c9a8"
TARGET_EMAIL = "jseaman1204@gmail.com"

# ── IDs to act on ────────────────────────────────────────────────────────────
ORPHAN_ID  = "9ab78fe0-e4e3-41b0-ba3a-bba701a192a9"  # no data at all, delete

GS_FIX_IDS = [
    "0002c0f9-9ea5-42d7-8697-a31353ffcb6d",  # 1954-S Franklin Half Dollar
    "001e17fe-b783-417a-9897-f1593dc32a35",  # 2010-D Lincoln Cent
]

def gs_to_https(gs_url: str) -> str:
    """Converts gs://bucket/path to https://storage.googleapis.com/bucket/path"""
    if not gs_url.startswith("gs://"):
        return gs_url
    rest = gs_url[5:]  # strip "gs://"
    return f"https://storage.googleapis.com/{rest}"

def make_blob_public(gcs, gs_url: str) -> None:
    """Makes a GCS object publicly readable (idempotent)."""
    if not gs_url.startswith("gs://"):
        return
    rest = gs_url[5:]
    bucket_name, blob_path = rest.split("/", 1)
    try:
        blob = gcs.bucket(bucket_name).blob(blob_path)
        blob.make_public()
        print(f"    Made public: {blob_path[:70]}")
    except Exception as e:
        print(f"    Warning: could not make public ({e}) — URL may already be public")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print("⚠️  DRY RUN — no writes\n")

    credentials, _ = google.auth.default()
    db  = firestore.Client(credentials=credentials, project=PROJECT)
    gcs = storage.Client(credentials=credentials, project=PROJECT)

    col_ref = db.collection("users").document(TARGET_EMAIL).collection("coins")

    # ── 1. Delete orphan ──────────────────────────────────────────────────────
    print(f"1. Deleting orphan coin: {ORPHAN_ID}")
    if not args.dry_run:
        col_ref.document(ORPHAN_ID).delete()
        print("   ✅ Deleted")
    else:
        print("   (dry-run — would delete)")

    # ── 2. Fix gs:// URLs ─────────────────────────────────────────────────────
    print(f"\n2. Fixing gs:// image URLs ({len(GS_FIX_IDS)} coins):")
    for coin_id in GS_FIX_IDS:
        snap = col_ref.document(coin_id).get()
        if not snap.exists:
            print(f"   SKIP {coin_id[:20]}  (not found)")
            continue

        data = snap.to_dict() or {}
        obv_gs = str(data.get("image_url_obverse", "") or "")
        rev_gs = str(data.get("image_url_reverse", "") or "")

        year    = data.get("Year", "?")
        program = data.get("Program/Series", "?")
        print(f"   {year} {program} ({coin_id[:20]})")

        updates = {}

        if obv_gs.startswith("gs://"):
            print(f"   Obverse: {obv_gs[:65]}")
            if not args.dry_run:
                make_blob_public(gcs, obv_gs)
                updates["image_url_obverse"] = gs_to_https(obv_gs)

        if rev_gs.startswith("gs://"):
            print(f"   Reverse: {rev_gs[:65]}")
            if not args.dry_run:
                make_blob_public(gcs, rev_gs)
                updates["image_url_reverse"] = gs_to_https(rev_gs)

        if updates and not args.dry_run:
            col_ref.document(coin_id).update(updates)
            print(f"   ✅ URL updated to HTTPS format")

    print(f"\n{'DRY RUN ' if args.dry_run else ''}Cleanup complete.")

if __name__ == "__main__":
    main()
