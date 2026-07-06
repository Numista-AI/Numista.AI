# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
r"""
ingest_coin_set.py
──────────────────────────────────────────────────────────────────────────────
Uploads a folder of coin-set images to GCS, creates denomination-aware entries
in coin_image_index, and writes a single manifest document to coin_set_index.

Usage:
    python ingest_coin_set.py --folder "new_coin_images/Hawaii" \
                              --set-id  "jamul-sovereign-2018" \
                              --set-name "2018 Jamul Sovereign Nation Coin Set" \
                              --year 2018 --program "jamul-indian-coin-set" \
                              --attribution "Images sourced with permission."

Denomination is auto-detected from filename fragments:
  ¢  /  1c / 1cent / penny / one cent  → 1c
  5¢ /  5c / nickel / five cents       → 5c
  10¢ / 10c / dime                     → 10c
  25¢ / 25c / quarter                  → 25c
  50¢ / 50c / half                     → 50c
  $1  / dollar / \$1 / 1d / one dollar → 1d
"""

import os, re, json, argparse, google.auth
from google.cloud import storage, firestore
from pathlib import Path
from datetime import datetime

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

PROJECT  = "studio-9101802118-8c9a8"
BUCKET   = "numista-reference-library"
GCS_BASE = "reference_library/user_contributed/coin_sets/"
IMAGE_IDX = "coin_image_index"
SET_IDX   = "coin_set_index"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".PNG", ".JPG", ".JPEG"}

# ─── Denomination detection ────────────────────────────────────────────────────
DENOM_PATTERNS = [
    (r"[\$]1\b|dollar|\bone.dollar\b|1d\b|\$1",                 "1d"),
    (r"50\s*[¢c]|half.dollar|fifty.cent",                        "50c"),
    (r"25\s*[¢c]|quarter|twenty.?five.cent",                     "25c"),
    (r"10\s*[¢c]|\bdime\b|ten.cent",                             "10c"),
    (r"5\s*[¢c]|\bnickel\b|five.cent|tiki",                      "5c"),
    (r"1\s*[¢c]|\bpenny\b|\bcent\b|one.cent|coconut",            "1c"),
]

DENOM_LABEL = {
    "1c":  "1¢ Penny",
    "5c":  "5¢ Nickel",
    "10c": "10¢ Dime",
    "25c": "25¢ Quarter",
    "50c": "50¢ Half Dollar",
    "1d":  "$1 Dollar",
}

def detect_denom(stem: str) -> str:
    s = stem.lower()
    for pattern, denom in DENOM_PATTERNS:
        if re.search(pattern, s, re.I):
            return denom
    return "unk"

def detect_side(stem: str) -> str:
    return "reverse" if re.search(r"rev(?:erse)?|back", stem, re.I) else "obverse"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder",      required=True, help="Local folder with set images")
    ap.add_argument("--set-id",      required=True, help="Canonical set ID, e.g. jamul-sovereign-2018")
    ap.add_argument("--set-name",    required=True, help="Display name of the set")
    ap.add_argument("--year",        required=True, help="Year of the set")
    ap.add_argument("--program",     required=True, help="Program slug, e.g. jamul-indian-coin-set")
    ap.add_argument("--attribution", default="",   help="Attribution / credit line")
    args = ap.parse_args()

    local_dir = Path(args.folder)
    if not local_dir.exists():
        print(f"ERROR: folder not found: {local_dir}")
        return

    images = sorted(f for f in local_dir.iterdir()
                    if f.suffix in IMAGE_EXTS)
    if not images:
        print(f"No images found in {local_dir}")
        return

    creds, _ = google.auth.default()
    sc = storage.Client(credentials=creds, project=PROJECT)
    db = firestore.Client(credentials=creds, project=PROJECT)
    bucket = sc.bucket(BUCKET)

    print(f"\nIngesting {len(images)} images for set '{args.set_id}'...\n")

    # ── Track coins for the set manifest ──────────────────────────────────────
    set_coins = {}   # denom → { obverse: doc_key, reverse: doc_key, name: ... }

    for img in images:
        denom = detect_denom(img.stem)
        side  = detect_side(img.stem)

        # GCS path: coin_sets/{set_id}/{original_filename}
        gcs_blob_path = f"{GCS_BASE}{args.set_id}/{img.name}"
        blob = bucket.blob(gcs_blob_path)
        blob.upload_from_filename(str(img))

        public_url = (
            f"https://storage.googleapis.com/{BUCKET}/"
            + gcs_blob_path.replace(" ", "%20")
        )

        # Denomination-aware Firestore key:
        # e.g. 2018_jamul-indian-coin-set_25c_obverse
        doc_key = f"{args.year}_{args.program}_{denom}_{side}"

        doc_ref = db.collection(IMAGE_IDX).document(doc_key)
        doc_ref.set({
            side: {
                "gcs_path":    f"gs://{BUCKET}/{gcs_blob_path}",
                "public_url":  public_url,
                "source_tier": 1,
                "source_label": "Eric Admin Contribution",
                "attribution": args.attribution,
                "indexed_at":  datetime.utcnow().isoformat(),
                "set_id":      args.set_id,
            },
            "year":    args.year,
            "mint":    None,
            "program": args.program,
            "set_id":  args.set_id,
        }, merge=True)

        print(f"  [{denom} {side}] {img.name}")
        print(f"       key: {doc_key}")

        # Accumulate for set manifest
        if denom not in set_coins:
            set_coins[denom] = {
                "denomination": denom,
                "label":        DENOM_LABEL.get(denom, denom),
                "name":         "",
                "obverse_key":  None,
                "reverse_key":  None,
                "obverse_url":  None,
                "reverse_url":  None,
            }
        set_coins[denom][f"{side}_key"] = doc_key
        set_coins[denom][f"{side}_url"] = public_url

    # ── Write coin_set_index manifest ─────────────────────────────────────────
    # Hero image = highest-value denomination (dollar or half-dollar)
    hero_order = ["1d", "50c", "25c", "10c", "5c", "1c", "unk"]
    hero_denom = next((d for d in hero_order if d in set_coins), None)
    hero_url   = set_coins[hero_denom]["obverse_url"] if hero_denom else ""

    coins_list = [
        set_coins[d] for d in ["1c", "5c", "10c", "25c", "50c", "1d", "unk"]
        if d in set_coins
    ]

    set_doc = {
        "set_id":        args.set_id,
        "name":          args.set_name,
        "year":          args.year,
        "program":       args.program,
        "attribution":   args.attribution,
        "hero_url":      hero_url,
        "coin_count":    len(set_coins),
        "coins":         coins_list,
        "indexed_at":    datetime.utcnow().isoformat(),
    }

    db.collection(SET_IDX).document(args.set_id).set(set_doc)
    print(f"\n  Manifest written to coin_set_index/{args.set_id}")
    print(f"  Hero image: {hero_url[:80]}...")
    print(f"\nDone — {len(images)} images indexed, set manifest created.")


if __name__ == "__main__":
    main()
