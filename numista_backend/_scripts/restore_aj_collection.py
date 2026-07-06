# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
restore_aj_collection.py
──────────────────────────────────────────────────────────────────────────────
Restores jseaman1204@gmail.com's coin collection from the CSV backup taken
on 2026-06-19 before the collection was wiped.

Source : "AJ's Coins/numista_export_2026-06-19 AJ Back up GOOD.csv"
Target : Firestore  users/jseaman1204@gmail.com/coins/{id}

Features:
  • Uses the existing 'id' field as the Firestore document ID
  • Converts Timestamp() strings back to Firestore server timestamps
  • Preserves ALL image_url_obverse / image_url_reverse GCS links
  • Batch writes (500 docs per batch) for speed and rate-limit safety
  • Dry-run mode: prints stats without writing

Usage:
    python _scripts/restore_aj_collection.py --dry-run   # preview
    python _scripts/restore_aj_collection.py             # apply
"""

import os, sys, re, csv, uuid, argparse
from datetime import datetime, timezone

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore

# ── Config ─────────────────────────────────────────────────────────────────
PROJECT        = "studio-9101802118-8c9a8"
TARGET_EMAIL   = "jseaman1204@gmail.com"
BACKUP_CSV     = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins\numista_export_2026-06-19 AJ Back up GOOD.csv"
BATCH_SIZE     = 400   # Firestore max is 500; keep headroom

# Fields we SKIP when writing (handled separately or not needed)
SKIP_FIELDS = {"user_email"}  # email is implicit in the collection path

# Fields that contain Firestore Timestamp strings
TIMESTAMP_FIELDS = {"created_at", "normalized_at", "image_updated_at", "last_researched"}

# Fields that should be stored as numbers (int or float)
NUMERIC_FIELDS = {
    "grade_review_count", "confidence_score",
}

# ── Timestamp parser ────────────────────────────────────────────────────────
_TS_RE = re.compile(r"Timestamp\(seconds=(\d+),\s*nanoseconds=(\d+)\)")

def parse_value(field: str, raw: str):
    """Convert a raw CSV string to the appropriate Python/Firestore type."""
    if not raw or raw.strip() == "":
        return None

    raw = raw.strip()

    # Firestore Timestamp string  →  Python datetime (UTC)
    if field in TIMESTAMP_FIELDS:
        m = _TS_RE.match(raw)
        if m:
            secs = int(m.group(1))
            return datetime.fromtimestamp(secs, tz=timezone.utc)
        # Try ISO-8601 fallback
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return raw  # keep as string if unparseable

    # Numeric fields
    if field in NUMERIC_FIELDS:
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw

    return raw


def build_doc(row: dict, fallback_id: str) -> tuple[str, dict]:
    """
    Build a (doc_id, doc_data) pair from a CSV row.
    Uses the 'id' column as the document ID, generating a new UUID if missing.
    """
    doc_id = (row.get("id") or "").strip() or fallback_id

    doc = {}
    for field, raw in row.items():
        if field in SKIP_FIELDS:
            continue
        if field == "id":
            continue  # stored as the document key, not a field

        val = parse_value(field, raw)
        if val is not None:
            doc[field] = val

    # Ensure the email is always stored on the document (for query convenience)
    doc["user_email"] = TARGET_EMAIL
    # Tag restored docs so we can audit them
    doc["restore_source"] = "backup_2026-06-19"
    doc["restore_at"] = datetime.now(tz=timezone.utc)

    return doc_id, doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Print stats without writing to Firestore")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only restore first N coins (0 = all)")
    args = ap.parse_args()

    # ── Load CSV ────────────────────────────────────────────────────────────
    print(f"Reading backup: {BACKUP_CSV}")
    rows = []
    with open(BACKUP_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total = len(rows)
    print(f"  {total:,} coins found in backup")

    if args.limit:
        rows = rows[:args.limit]
        print(f"  Limiting to first {args.limit} coins (--limit flag)")

    if args.dry_run:
        print("\n⚠️  DRY RUN — no writes will occur\n")

    # ── Connect to Firestore ─────────────────────────────────────────────────
    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)

    # ── Safety check: confirm collection is empty ────────────────────────────
    if not args.dry_run:
        existing = list(
            db.collection("users").document(TARGET_EMAIL)
              .collection("coins").limit(1).stream()
        )
        if existing:
            print(f"\n⚠️  WARNING: {TARGET_EMAIL}/coins already has documents!")
            print("   Use --dry-run to preview, or clear the collection first.")
            confirm = input("   Type 'yes' to continue anyway: ").strip().lower()
            if confirm != "yes":
                print("Aborted.")
                return

    # ── Batch write ──────────────────────────────────────────────────────────
    col_ref    = db.collection("users").document(TARGET_EMAIL).collection("coins")
    batch      = db.batch()
    batch_count = 0
    total_written = 0
    errors     = 0
    skipped    = 0

    # Preview stats
    has_obverse = 0
    has_reverse = 0
    missing_images = 0

    for i, row in enumerate(rows):
        fallback_id = str(uuid.uuid4())
        try:
            doc_id, doc = build_doc(row, fallback_id)
        except Exception as e:
            print(f"  ERROR building row {i+1}: {e}")
            errors += 1
            continue

        # Track image coverage
        obv = doc.get("image_url_obverse", "")
        rev = doc.get("image_url_reverse", "")
        if obv and str(obv).startswith("http"):
            has_obverse += 1
        if rev and str(rev).startswith("http"):
            has_reverse += 1
        if not (obv and str(obv).startswith("http")) and not (rev and str(rev).startswith("http")):
            missing_images += 1

        if not args.dry_run:
            doc_ref = col_ref.document(doc_id)
            batch.set(doc_ref, doc)
            batch_count += 1
            total_written += 1

            if batch_count >= BATCH_SIZE:
                batch.commit()
                batch = db.batch()
                batch_count = 0
                pct = total_written / len(rows) * 100
                print(f"  Committed {total_written:,}/{len(rows):,} ({pct:.1f}%)")
        else:
            total_written += 1

        if (i + 1) % 500 == 0:
            pct = (i + 1) / len(rows) * 100
            print(f"  Processed {i+1:,}/{len(rows):,} ({pct:.1f}%)")

    # Commit final partial batch
    if not args.dry_run and batch_count > 0:
        batch.commit()
        print(f"  Committed final batch ({batch_count} docs)")

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'DRY RUN ' if args.dry_run else ''}Results:")
    print(f"  Total coins in backup  : {total:,}")
    print(f"  Coins processed        : {total_written:,}")
    print(f"  Errors                 : {errors}")
    print(f"  Coins with obverse img : {has_obverse:,}  ({has_obverse/max(total_written,1)*100:.1f}%)")
    print(f"  Coins with reverse img : {has_reverse:,}  ({has_reverse/max(total_written,1)*100:.1f}%)")
    print(f"  Coins with NO image    : {missing_images:,}  ({missing_images/max(total_written,1)*100:.1f}%)")
    print(f"\n  Target collection      : users/{TARGET_EMAIL}/coins")
    if not args.dry_run:
        print(f"  ✅  Restore complete!")
    else:
        print(f"\n  Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
