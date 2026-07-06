# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
promote_user_photos.py
─────────────────────────────────────────────────────────────────────────────
Backend script that scans all user coin documents for `contribute_to_library: true`
and copies the user's photo to the reference GCS bucket, then updates the
coin_image_index as a Tier-1 (personal contribution) image.

Run manually or on a schedule (e.g., daily).

Usage:
    python _scripts/promote_user_photos.py --dry-run    # preview
    python _scripts/promote_user_photos.py              # apply

Design notes:
  • Copies the user photo to gs://numista-uploads-studio-9101802118-8c9a8/reference/
    at path: reference/{program_slug}/{year}_{program_slug}_{side}.jpg
  • Marks the coin_image_index doc with source_tier=1, attribution='User Contribution'
  • Sets contribute_to_library = 'PROMOTED' on the source coin to avoid re-processing
  • Only promotes if we don't already have a Tier-1 or Tier-2 image for that coin
"""

import os, re, sys, json, uuid
from datetime import datetime

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import argparse
import google.auth
from google.cloud import firestore, storage

PROJECT       = "studio-9101802118-8c9a8"
BUCKET_NAME   = "numista-uploads-studio-9101802118-8c9a8"
REF_PREFIX    = "reference"    # destination path prefix inside the bucket
PUBLIC_BASE   = "https://storage.googleapis.com"

PROGRAM_MAP = {
    "american silver eagle":          "american-eagle-silver",
    "american eagle silver dollar":   "american-eagle-silver",
    "morgan silver dollar":           "morgan-dollar",
    "morgan dollar":                  "morgan-dollar",
    "morgan silver dollar set":       "morgan-dollar",
    "peace dollar":                   "peace-dollar",
    "kennedy half dollar":            "kennedy-half-dollar",
    "50 state quarters":              "50-state-quarters",
    "state quarters":                 "50-state-quarters",
    "presidential dollar":            "presidential-dollars",
    "sacagawea dollar":               "native-american-dollar",
    "native american dollar":         "native-american-dollar",
    "american women quarters":        "american-women-quarters",
    "america the beautiful":          "america-the-beautiful",
    "american innovation":            "american-innovation",
    "eisenhower dollar":              "dollar",
    "lincoln cent":                   "lincoln-cent",
    "jefferson nickel":               "jefferson-nickel",
    "roosevelt dime":                 "dime",
    "walking liberty half dollar":    "walking-liberty",
    "buffalo nickel":                 "buffalo-nickel",
    "mercury dime":                   "mercury-dime",
    "saint-gaudens double eagle":     "saint-gaudens",
    "saint gaudens":                  "saint-gaudens",
    "american gold eagle":            "american-eagle-gold",
    "american eagle gold":            "american-eagle-gold",
    "franklin half dollar":           "franklin-half-dollar",
    "barber quarter":                 "quarter",
    "barber dime":                    "dime",
    "barber half dollar":             "kennedy-half-dollar",
}


def normalize_program(raw: str) -> str | None:
    lower = raw.lower().strip()
    for k, v in sorted(PROGRAM_MAP.items(), key=lambda x: -len(x[0])):
        if k in lower:
            return v
    return None


def get_existing_tier(db, doc_id: str, side: str) -> int:
    """Returns existing source_tier for a coin_image_index doc/side, or 99 if missing."""
    try:
        snap = db.collection("coin_image_index").document(doc_id).get()
        if not snap.exists:
            return 99
        data = snap.to_dict() or {}
        side_data = data.get(side, {})
        return side_data.get("source_tier", 99)
    except Exception:
        return 99


def copy_to_reference(gcs, src_url: str, dest_path: str) -> str:
    """Copies a Firebase Storage URL to the reference/ path and returns the public URL."""
    # Firebase download URLs contain a token; strip query string for GCS path
    # The actual GCS path is embedded in the URL path portion
    # URL format: https://firebasestorage.googleapis.com/v0/b/{bucket}/o/{encoded_path}?alt=media&token=...
    import urllib.parse, re as _re
    
    src_bucket = None
    src_blob_path = None
    
    if "firebasestorage.googleapis.com" in src_url:
        # Firebase Storage URL
        m = _re.search(r"/b/([^/]+)/o/(.+)\?", src_url)
        if m:
            src_bucket = urllib.parse.unquote(m.group(1))
            src_blob_path = urllib.parse.unquote(m.group(2))
    elif "storage.googleapis.com" in src_url:
        # Public GCS URL: https://storage.googleapis.com/{bucket}/{path}
        m = _re.match(r"https://storage\.googleapis\.com/([^/]+)/(.+)", src_url)
        if m:
            src_bucket = m.group(1)
            src_blob_path = m.group(2)
    
    if not src_bucket or not src_blob_path:
        raise ValueError(f"Cannot parse storage URL: {src_url[:80]}")
    
    # Download bytes from source
    src_blob = gcs.bucket(src_bucket).blob(src_blob_path)
    img_bytes = src_blob.download_as_bytes()
    
    # Upload to destination
    dest_blob = gcs.bucket(BUCKET_NAME).blob(dest_path)
    content_type = src_blob.content_type or "image/jpeg"
    dest_blob.upload_from_string(img_bytes, content_type=content_type)
    dest_blob.make_public()
    
    return f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-tier", type=int, default=3,
                    help="Only promote if existing ref image tier >= this value (default: 3)")
    args = ap.parse_args()

    credentials, _ = google.auth.default()
    db  = firestore.Client(credentials=credentials, project=PROJECT)
    gcs = storage.Client(credentials=credentials, project=PROJECT)

    # ── Find all user coins with contribute_to_library == True ────────────────
    print("Scanning all user coin subcollections...")
    promote_list = []

    users = list(db.collection("users").stream())
    print(f"  {len(users)} user docs found")

    for user_doc in users:
        email = user_doc.id
        coins = list(user_doc.reference.collection("coins")
                     .where(filter=firestore.FieldFilter("contribute_to_library", "==", True))
                     .stream())
        for coin in coins:
            data = coin.to_dict() or {}
            # Skip already-promoted
            if data.get("contribute_to_library") == "PROMOTED":
                continue
            promote_list.append((email, coin.reference, data))

    print(f"  {len(promote_list)} coins flagged for contribution\n")

    if not promote_list:
        print("Nothing to promote.")
        return

    promoted = 0
    skipped  = 0

    for email, coin_ref, data in promote_list:
        year       = str(data.get("Year", "") or data.get("year", "")).strip().replace(".0", "")
        program_raw = str(data.get("Program/Series", "") or "").strip()
        program_slug = normalize_program(program_raw)
        obv_url = data.get("image_url_obverse", "")
        rev_url = data.get("image_url_reverse", "")
        sides   = []
        if obv_url and obv_url.startswith("http"): sides.append(("obverse", obv_url))
        if rev_url and rev_url.startswith("http"): sides.append(("reverse", rev_url))

        if not year or not program_slug or not sides:
            print(f"  SKIP {coin_ref.id[:20]}  (missing year={year} slug={program_slug} sides={len(sides)})")
            skipped += 1
            continue

        for side, src_url in sides:
            doc_id      = f"{year}_{program_slug}_{side}"
            existing    = get_existing_tier(db, doc_id, side)

            if existing < args.min_tier:
                print(f"  SKIP {doc_id:45s}  already Tier {existing} (better than threshold {args.min_tier})")
                skipped += 1
                continue

            dest_path   = f"{REF_PREFIX}/{program_slug}/{doc_id}.jpg"
            print(f"  PROMOTE {doc_id:45s}  (replaces Tier {existing})")

            if not args.dry_run:
                try:
                    pub_url = copy_to_reference(gcs, src_url, dest_path)
                    # Update coin_image_index
                    db.collection("coin_image_index").document(doc_id).set({
                        "year":    year,
                        "mint":    str(data.get("Mint Mark", "") or "").strip(),
                        "program": program_slug,
                        side: {
                            "public_url":   pub_url,
                            "source_tier":  1,
                            "source_label": "user_contribution",
                            "attribution":  f"User Contribution ({email})",
                            "promoted_at":  datetime.now().isoformat(),
                            "promoted_from_user": email,
                        }
                    }, merge=True)
                    promoted += 1
                except Exception as e:
                    print(f"    ERROR: {e}")
                    skipped += 1

        if not args.dry_run:
            # Mark coin as PROMOTED so we don't re-process
            try:
                coin_ref.update({
                    "contribute_to_library": "PROMOTED",
                    "contribute_promoted_at": datetime.now().isoformat(),
                })
            except Exception:
                pass

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Results:")
    print(f"  Promoted : {promoted}")
    print(f"  Skipped  : {skipped}")


if __name__ == "__main__":
    main()
