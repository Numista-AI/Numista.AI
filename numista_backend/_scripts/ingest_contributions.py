# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
ingest_contributions.py
Upload everything in new_coin_images/ to GCS user_contributed and
register each image in the coin_image_index Firestore collection.
Parses year, mint mark, program and side from filename automatically.
"""
import os, re, json, google.auth
from google.cloud import storage, firestore
from pathlib import Path
from datetime import datetime

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

PROJECT  = "studio-9101802118-8c9a8"
BUCKET   = "numista-reference-library"
GCS_PRE  = "reference_library/user_contributed/eric_admin/"
LOCAL    = Path(r"C:\Users\ericd\Documents\MyVertexProject\new_coin_images")
COLLECT  = "coin_image_index"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# Regex: year + optional attached mint mark  e.g. "1989W"  "2025-W"  "1921-D"
YEAR_MINT_RE = re.compile(r"\b(1[789]\d{2}|20[012]\d)\s*[-]?\s*([PDSWpdswOo]|CC)?\b")
PROGRAM_MAP  = [
    (r"gold.?eagle|american.?eagle.?gold|american.?gold.?eagle|gold.+\$50|\$50.+gold|\$25.+gold|gold.+\$25", "american-eagle-gold"),
    (r"silver.?eagle|american.?eagle.?silver|\$1.+silver|silver.+\$1",                                       "american-eagle-silver"),
    (r"morgan",                                                         "morgan-dollar"),
    (r"peace.?dollar",                                                  "peace-dollar"),
    (r"kennedy|half.?dollar",                                           "kennedy-half-dollar"),
    (r"quarter",                                                        "quarter"),
    (r"lincoln|wheat.?cent|penny",                                      "lincoln-cent"),
    (r"buffalo.?nickel",                                                "buffalo-nickel"),
    (r"jefferson.?nickel",                                              "jefferson-nickel"),
    (r"mercury.?dime|winged.?liberty",                                  "mercury-dime"),
    (r"dime",                                                           "dime"),
    (r"nickel",                                                         "nickel"),
    (r"cent",                                                           "cent"),
]


def detect_program(slug):
    for pattern, canonical in PROGRAM_MAP:
        if re.search(pattern, slug, re.I):
            return canonical
    return "unknown"


def detect_side(name):
    if re.search(r"rev(?:erse)?|back", name, re.I):
        return "reverse"
    return "obverse"


def parse_filename(stem):
    """Return (year, mint, program, side) from an image filename stem."""
    m = YEAR_MINT_RE.search(stem)
    year = m.group(1) if m else ""
    mint = (m.group(2) or "").upper() if m else ""
    program = detect_program(stem)
    side    = detect_side(stem)
    return year, mint, program, side


def main():
    creds, _ = google.auth.default()
    sc = storage.Client(credentials=creds, project=PROJECT)
    db = firestore.Client(credentials=creds, project=PROJECT)
    bucket = sc.bucket(BUCKET)

    images = sorted(
        f for f in LOCAL.iterdir()
        if f.suffix.lower() in IMAGE_EXTS
    )

    if not images:
        print("No images found in", LOCAL)
        return

    print(f"Found {len(images)} images to ingest from {LOCAL}\n")
    indexed = 0

    for img in images:
        year, mint, program, side = parse_filename(img.stem)

        # Build GCS path (keep original filename)
        gcs_blob_path = GCS_PRE + img.name
        blob = bucket.blob(gcs_blob_path)
        blob.upload_from_filename(str(img))

        encoded = gcs_blob_path.replace(" ", "%20")
        public_url = f"https://storage.googleapis.com/{BUCKET}/{encoded}"

        # Build canonical Firestore key
        key_parts = [year] if year else ["unknown"]
        if mint:
            key_parts.append(mint)
        key_parts.append(program)
        key_parts.append(side)
        doc_key = "_".join(key_parts)

        doc_ref = db.collection(COLLECT).document(doc_key)
        doc_ref.set({
            side: {
                "gcs_path":    f"gs://{BUCKET}/{gcs_blob_path}",
                "public_url":  public_url,
                "source_tier": 1,
                "source_label": "Eric Admin Contribution",
                "attribution": "Image courtesy United States Mint. Used with permission.",
                "indexed_at":  datetime.utcnow().isoformat(),
            },
            "year":    year,
            "mint":    mint or None,
            "program": program,
        }, merge=True)

        print(f"  [{side}] {img.name}")
        print(f"       key: {doc_key}")
        print(f"       url: {public_url[:80]}...")
        indexed += 1

    print(f"\nDone — {indexed} images uploaded and indexed in Firestore.")


if __name__ == "__main__":
    main()
