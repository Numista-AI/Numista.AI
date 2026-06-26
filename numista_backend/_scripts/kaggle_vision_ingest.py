"""
kaggle_vision_ingest.py
────────────────────────────────────────────────────────────────
Classifies unlabeled Kaggle coin images using Gemini Vision and
writes them into the Firestore coin_image_index.

Features:
  - Checkpoint file: saves every 50 images (safe to Ctrl+C and resume)
  - Time limit: --stop-at HH:MM (24-hr local time) or --minutes N
  - Rate limiting: 1.2 sec between Gemini calls
  - Skips already-processed images on resume
  - Dry-run: --dry-run shows what would be indexed without writing

Usage:
  python _scripts/kaggle_vision_ingest.py --stop-at 10:04
  python _scripts/kaggle_vision_ingest.py --stop-at 11:03 --resume
  python _scripts/kaggle_vision_ingest.py --dry-run
"""

import os, re, sys, json, time, argparse
from datetime import datetime, date
from pathlib import Path

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
import google.auth.transport.requests
from google.cloud import storage, firestore

# ── Gemini SDK ──────────────────────────────────────────────────────────────
from google import genai as _genai
from google.genai import types as genai_types

try:
    _credentials, _ = google.auth.default()
    GENAI_CLIENT = _genai.Client(
        vertexai=True,
        project="studio-9101802118-8c9a8",
        location="global",
    )
    print("[init] Using google.genai SDK")
except Exception as e:
    print(f"ERROR: Cannot initialize Gemini SDK: {e}")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT    = "studio-9101802118-8c9a8"
BUCKET     = "numista-uploads-studio-9101802118-8c9a8"
PREFIX     = "kaggle/"
COLLECTION = "coin_image_index"
CHECKPOINT = "_scripts/kaggle_vision_checkpoint.json"
TIER       = 3
LABEL      = "Kaggle Dataset"
ATTR       = "Kaggle / Public Domain"
RATE       = 1.2   # seconds between Gemini calls
PUB_BASE   = "https://storage.googleapis.com"
# Model candidates in priority order — script picks first one that responds
MODEL_CANDIDATES = [
    "gemini-3.5-flash",
    "gemini-3.0-flash",
    "gemini-3-flash-preview",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]
MODEL = None  # resolved at runtime

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".PNG", ".JPG", ".JPEG"}

PROMPT = """\
You are a US coin identification expert. Examine this coin image and return \
a JSON object with exactly these keys:
  year:       4-digit year string visible on the coin, e.g. "1921" — or null
  mint:       mint mark if visible: "P", "D", "S", "W", "CC", "O" — or null
  program:    one of: american-eagle-silver, american-eagle-gold,
              american-eagle-platinum, american-eagle-palladium,
              50-state-quarters, america-the-beautiful, american-women-quarters,
              american-innovation, native-american-dollar, presidential-dollars,
              morgan-dollar, peace-dollar, trade-dollar, eisenhower-dollar,
              walking-liberty, mercury-dime, liberty-seated-dime,
              liberty-seated-quarter, liberty-seated-half-dollar,
              liberty-seated-dollar, barber-dime, barber-quarter,
              barber-half-dollar, franklin-half-dollar, kennedy-half-dollar,
              liberty-walking-half-dollar, capped-bust-half-dollar,
              lincoln-cent, jefferson-nickel, buffalo-nickel, liberty-nickel,
              shield-nickel, indian-head-cent, flying-eagle-cent,
              large-cent, half-cent, saint-gaudens, bicentennial,
              commemorative, american-liberty, flowing-hair,
              dollar, dime, quarter, nickel, cent, unknown
  side:       "obverse" or "reverse"
  confidence: "high", "medium", or "low"
Return ONLY the JSON object. No markdown, no explanation.\
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_checkpoint():
    if Path(CHECKPOINT).exists():
        with open(CHECKPOINT, encoding="utf-8") as f:
            return json.load(f)
    return {"processed": [], "indexed": 0, "skipped": 0, "errors": 0}

def save_checkpoint(cp):
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2)

def probe_model():
    """Try each candidate model with a tiny text prompt and return first that works."""
    global MODEL
    for candidate in MODEL_CANDIDATES:
        try:
            GENAI_CLIENT.models.generate_content(
                model=candidate,
                contents=["Say: OK"]
            )
            MODEL = candidate
            print(f"[model] Using {MODEL}")
            return
        except Exception as e:
            print(f"[model] {candidate} not available: {str(e)[:60]}")
    raise RuntimeError("No Gemini model available! Check project permissions.")


def classify(blob):
    """Download blob and ask Gemini to identify the coin."""
    image_bytes = blob.download_as_bytes()
    ext  = Path(blob.name).suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    response = GENAI_CLIENT.models.generate_content(
        model=MODEL,
        contents=[
            genai_types.Part.from_bytes(data=image_bytes, mime_type=mime),
            PROMPT,
        ],
    )
    raw = response.text.strip()

    # Strip markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
    raw = re.sub(r"\s*```$", "", raw.strip())
    return json.loads(raw)

# Filename-based program fallback — used when Vision returns prog=unknown
# Keys must appear in the blob filename (lowercased)
FILENAME_PROGRAM_MAP = [
    ("franklin",       "franklin-half-dollar"),
    ("morgan",         "morgan-dollar"),
    ("peace",          "peace-dollar"),
    ("eisenhower",     "eisenhower-dollar"),
    ("state_quarter",  "50-state-quarters"),
    ("state quarter",  "50-state-quarters"),
    ("kennedy",        "kennedy-half-dollar"),
    ("walking",        "liberty-walking-half-dollar"),
    ("mercury",        "mercury-dime"),
    ("lincoln",        "lincoln-cent"),
    ("jefferson",      "jefferson-nickel"),
    ("buffalo",        "buffalo-nickel"),
    ("indian",         "indian-head-cent"),
    ("barber",         "barber-half-dollar"),
    ("presidential",   "presidential-dollars"),
    ("sacagawea",      "native-american-dollar"),
    ("american_eagle", "american-eagle-silver"),
    ("saint_gaudens",  "saint-gaudens"),
]

def infer_program_from_filename(blob_name: str) -> str | None:
    """Returns a program slug based on the blob filename, or None if unrecognized."""
    lower = Path(blob_name).stem.lower()
    for keyword, program in FILENAME_PROGRAM_MAP:
        if keyword in lower:
            return program
    return None

def make_key(year, mint, program, side):
    parts = [str(year or "")]
    if mint:
        parts.append(str(mint).upper())
    parts += [str(program or "unknown"), str(side or "obverse")]
    return "_".join(parts)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stop-at",  help="Stop at HH:MM local time, e.g. 10:04")
    ap.add_argument("--dry-run",  action="store_true")
    ap.add_argument("--resume",   action="store_true", help="Resume from checkpoint (default if checkpoint exists)")
    args = ap.parse_args()

    # Parse stop time
    stop_dt = None
    if args.stop_at:
        h, m   = map(int, args.stop_at.split(":"))
        stop_dt = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        print(f"[config] Will stop at {stop_dt.strftime('%H:%M:%S')}")

    credentials, _ = google.auth.default()
    gcs_client     = storage.Client(credentials=credentials, project=PROJECT)

    # Probe to find a working Gemini model before processing any images
    probe_model()
    db             = firestore.Client(credentials=credentials, project=PROJECT)

    cp = load_checkpoint()
    already_done = set(cp["processed"])
    print(f"[checkpoint] {len(already_done)} images already processed from previous run")

    # List all images
    bucket_obj = gcs_client.bucket(BUCKET)
    all_blobs  = [
        b for b in bucket_obj.list_blobs(prefix=PREFIX)
        if Path(b.name).suffix in IMAGE_EXTS
    ]
    print(f"[scan] {len(all_blobs)} total image files in {BUCKET}/{PREFIX}")
    remaining = [b for b in all_blobs if b.name not in already_done]
    print(f"[scan] {len(remaining)} remaining to process\n")

    # Progress counters
    total_indexed  = cp.get("indexed", 0)
    total_skipped  = cp.get("skipped", 0)
    total_errors   = cp.get("errors",  0)
    session_n      = 0

    batch    = db.batch() if not args.dry_run else None
    batch_n  = 0

    for blob in remaining:
        # Time check
        if stop_dt and datetime.now() >= stop_dt:
            print(f"\n[STOP] Reached stop time {args.stop_at}. Saving checkpoint.")
            break

        session_n += 1
        pct = 100 * (len(already_done) + session_n) / len(all_blobs)
        print(f"  [{session_n:4d}/{len(remaining)}] ({pct:.1f}%) {blob.name.split('/')[-1][:50]}", end=" ", flush=True)

        try:
            result = classify(blob)
        except Exception as e:
            print(f"ERROR: {e}")
            total_errors += 1
            cp["processed"].append(blob.name)
            cp["errors"] = total_errors
            save_checkpoint(cp)
            time.sleep(RATE)
            continue

        year       = result.get("year")
        mint       = result.get("mint") or None
        program    = result.get("program") or "unknown"
        side       = result.get("side") or "obverse"
        confidence = result.get("confidence") or "low"

        # If Vision returned unknown program, try to infer from filename
        if program == "unknown":
            inferred = infer_program_from_filename(blob.name)
            if inferred:
                program = inferred
                print(f"         [filename fallback] program={program}")

        # Skip low-confidence or still-unidentifiable
        if not year or program == "unknown" or confidence == "low":
            print(f"skip ({confidence}, prog={program}, year={year})")
            total_skipped += 1
            cp["processed"].append(blob.name)
            cp["skipped"]  = total_skipped
            save_checkpoint(cp)
            time.sleep(RATE)
            continue

        doc_key = make_key(year, mint, program, side)
        pub_url = f"{PUB_BASE}/{BUCKET}/{blob.name}"

        print(f"-> {doc_key}")

        if not args.dry_run:
            doc_ref  = db.collection(COLLECTION).document(doc_key)
            doc_data = {
                side: {
                    "gcs_path":    f"gs://{BUCKET}/{blob.name}",
                    "public_url":  pub_url,
                    "source_tier": TIER,
                    "source_label": LABEL,
                    "attribution": ATTR,
                    "indexed_at":  datetime.now().isoformat(),
                    "confidence":  confidence,
                },
                "year":    year,
                "mint":    mint,
                "program": program,
            }
            # Only write if no higher-tier image already exists for this key+side
            existing = doc_ref.get()
            if existing.exists:
                ex_data = existing.to_dict()
                ex_tier = ex_data.get(side, {}).get("source_tier", 99) if isinstance(ex_data.get(side), dict) else 99
                if ex_tier <= TIER:
                    print(f"         (skipping — tier {ex_tier} already in index)")
                    total_skipped += 1
                    cp["processed"].append(blob.name)
                    cp["skipped"] = total_skipped
                    save_checkpoint(cp)
                    time.sleep(RATE)
                    continue

            batch.set(doc_ref, doc_data, merge=True)
            batch_n += 1
            if batch_n >= 200:
                batch.commit()
                batch = db.batch()
                batch_n = 0

        total_indexed += 1
        cp["processed"].append(blob.name)
        cp["indexed"]  = total_indexed
        save_checkpoint(cp)
        time.sleep(RATE)

    # Commit any remaining batch
    if not args.dry_run and batch_n > 0:
        batch.commit()

    print(f"""
========================================
  KAGGLE VISION INGEST — SESSION DONE
  Processed this session : {session_n}
  Indexed (all sessions) : {total_indexed}
  Skipped (low conf/dup) : {total_skipped}
  Errors                 : {total_errors}
  Remaining              : {len(remaining) - session_n}
  Checkpoint saved to    : {CHECKPOINT}
========================================
Re-run with same command to resume where you left off.
""")

if __name__ == "__main__":
    main()
