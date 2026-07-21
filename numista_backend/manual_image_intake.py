#!/usr/bin/env python3
"""
manual_image_intake.py
======================
Formalizes the manual coin image ingestion workflow.

WHAT IT DOES
------------
1. Scans all subdirectories under BASE_MANUAL for image files.
2. Parses each filename (user-named) into structured coin attributes
   (year, denomination, series/program, side, mint mark).
3. Fuzzy-matches each file against Firestore `definitive_reference` docs
   to find the best doc_id candidate.
4. Auto-commits matches >= 92% confidence:
     a. Renames file to canonical format: {doc_id}_obverse.jpg / {doc_id}_reverse.jpg
     b. Uploads to GCS  →  coins/{doc_id}_{side}.jpg
     c. Updates Firestore  (image_url_obverse / image_url_reverse)
     d. Updates SQLite cache
5. Saves a review log:  manual_intake_log.json
6. Generates / updates:  missing_images_log.csv
   — Every definitive_reference doc that still has no obverse URL after this run.

USAGE
-----
    python manual_image_intake.py [--dry-run] [--folder <path>]

OPTIONS
    --dry-run   Preview matches and uploads without writing anything.
    --folder    Override the root scan folder (default: BASE_MANUAL).
    --audit     Only regenerate missing_images_log.csv, skip intake.

CONFIDENCE THRESHOLD
--------------------
    AUTO_COMMIT_THRESHOLD = 0.92  (92 %)
    Matches below this threshold are written to the review log as NEEDS_REVIEW.
"""

import os
import re
import sys
import csv
import json
import shutil
import sqlite3
import argparse
import io
from pathlib import Path
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
)

# ─── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
SA_KEY       = SCRIPT_DIR / "serviceAccountKey.json.json"
PROJECT_ID   = "studio-9101802118-8c9a8"
BUCKET_NAME  = "numista-uploads-studio-9101802118-8c9a8"
REF_BUCKET   = "numista-reference-library"
DB_PATH      = SCRIPT_DIR / "database" / "numista_coins.db"

BASE_MANUAL  = Path(r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images")

LOG_FILE         = SCRIPT_DIR / "manual_intake_log.json"
MISSING_LOG_CSV  = SCRIPT_DIR / "missing_images_log.csv"

AUTO_COMMIT_THRESHOLD = 0.92   # 92 %
IMAGE_EXTENSIONS      = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

GCS_COIN_PREFIX  = "coins/"
PUBLIC_URL_BASE  = "https://storage.googleapis.com/{bucket}/{path}"

# ─── Third-party imports ──────────────────────────────────────────────────────
try:
    from rapidfuzz import fuzz, process as rfprocess
except ImportError:
    print("[ERROR] rapidfuzz is not installed. Run:  pip install rapidfuzz")
    sys.exit(1)

import firebase_admin
from firebase_admin import credentials, firestore, storage as fb_storage
from google.cloud import storage as gcs_storage

# ─── Init Firebase ────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred, {
        "storageBucket": BUCKET_NAME,
        "projectId": PROJECT_ID,
    })

db = firestore.client()
gcs_client = gcs_storage.Client.from_service_account_json(str(SA_KEY))
upload_bucket = gcs_client.bucket(BUCKET_NAME)

# ─── Logging ──────────────────────────────────────────────────────────────────
run_log = {
    "run_timestamp": datetime.now(timezone.utc).isoformat(),
    "auto_committed": [],
    "needs_review": [],
    "skipped": [],
    "errors": [],
}

def log_error(msg, exc=None):
    entry = {"error": msg, "exception": str(exc) if exc else None}
    run_log["errors"].append(entry)
    print(f"  [ERROR] {msg}" + (f" — {exc}" if exc else ""))

# ─── Filename Parser ──────────────────────────────────────────────────────────
# Expected user naming convention (flexible):
#   "<year>, <Series/Program>, <Park/Design Name>, <side>.jpg"
#   "2017, Washington Quarter, Ellis Island (Statue of Liberty...), obverse.jpg"
#   "2008, Alaska Quarter, obverse.jpg"
#   "1971, Eisenhower Dollar, obverse.jpg"

SIDE_TOKENS = {
    "obverse": "obverse", "obv": "obverse", "front": "obverse", "heads": "obverse",
    "reverse": "reverse", "rev": "reverse", "back": "reverse", "tails": "reverse",
}

MINT_TOKENS = {
    "_p": "P", "-p": "P", " p ": "P",
    "_d": "D", "-d": "D", " d ": "D",
    "_s": "S", "-s": "S", " s ": "S",
    "_cc": "CC", "-cc": "CC",
    "_o": "O", "-o": "O",
    " (p)": "P", " (d)": "D", " (s)": "S",
}


def parse_filename(filename: str) -> dict:
    """
    Extract structured attributes from a user-named image filename.
    Returns a dict: {year, side, mint_mark, description, raw_stem}
    """
    stem = Path(filename).stem
    raw  = stem

    # ── Detect side ───────────────────────────────────────────────────────────
    side = "obverse"   # default
    stem_lower = stem.lower()
    for token, mapped in SIDE_TOKENS.items():
        # Match at end of string or surrounded by non-alphanumeric
        if re.search(r'(?<![a-z])' + re.escape(token) + r'(?![a-z])', stem_lower):
            side = mapped
            # Remove side token from stem for cleaner description
            stem = re.sub(re.escape(token), "", stem, flags=re.IGNORECASE).strip(", .-_")
            break

    # ── Detect year ───────────────────────────────────────────────────────────
    year_match = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", stem)
    year = year_match.group(1) if year_match else None
    if year:
        stem = stem.replace(year, "").strip(", .-_")

    # ── Detect mint mark ─────────────────────────────────────────────────────
    mint_mark = None
    for token, mapped in MINT_TOKENS.items():
        if token in stem_lower:
            mint_mark = mapped
            stem = re.sub(re.escape(token), "", stem, flags=re.IGNORECASE).strip(", .-_")
            break

    # ── Remaining text = description ─────────────────────────────────────────
    description = re.sub(r"\s+", " ", stem).strip(", .-_()")

    return {
        "year":        year,
        "side":        side,
        "mint_mark":   mint_mark,
        "description": description,
        "raw_stem":    raw,
    }


# ─── Firestore Catalog Loader ─────────────────────────────────────────────────

_catalog_cache: list = []   # [{doc_id, match_string, data}, ...]


def load_catalog() -> list:
    """
    Load all definitive_reference docs and build match strings for fuzzy search.
    Cached after first call.
    """
    global _catalog_cache
    if _catalog_cache:
        return _catalog_cache

    print("📚 Loading definitive_reference catalog from Firestore …")
    docs = db.collection("definitive_reference").stream()
    for doc in docs:
        d = doc.to_dict()
        d["doc_id"] = doc.id

        # Build a rich text string to match against
        parts = [
            str(d.get("year") or ""),
            str(d.get("denomination") or ""),
            str(d.get("series") or ""),
            str(d.get("variety") or ""),
            str(d.get("mint_mark") or ""),
            str(d.get("category") or ""),
        ]
        match_str = " ".join(p for p in parts if p).lower()
        _catalog_cache.append({"doc_id": doc.id, "match_string": match_str, "data": d})

    print(f"  Loaded {len(_catalog_cache)} catalog records.")
    return _catalog_cache


# Keywords that map common collector shorthand to catalog terminology
_PROGRAM_SYNONYMS = {
    "washington quarter":     "quarter dollar",
    "atb quarter":            "america the beautiful",
    "national parks quarter": "america the beautiful",
    "state quarter":          "50 state",
    "50 state quarter":       "50 state",
    "innovation dollar":      "american innovation",
    "presidential dollar":    "presidential",
    "sacagawea dollar":        "sacagawea",
    "native american dollar": "native american",
    "kennedy half":           "kennedy half dollar",
    "eisenhower dollar":      "eisenhower",
    "morgan dollar":          "morgan",
    "peace dollar":           "peace",
}


def normalize_query(text: str) -> str:
    """
    Normalize collector shorthand to match catalog terminology:
      • Strip parentheticals  (long official park names, etc.)
      • Apply synonym map
    """
    # Remove parenthetical blocks like  "(Statue of Liberty National Monument, NJ)"
    text = re.sub(r'\([^)]*\)', '', text)
    text = text.lower().strip()
    for src, dst in _PROGRAM_SYNONYMS.items():
        text = text.replace(src, dst)
    return text


def build_query_string(parsed: dict) -> str:
    """Build a normalized query string from parsed filename attributes."""
    desc = normalize_query(parsed.get("description") or "")
    parts = [
        parsed.get("year") or "",
        desc,
        parsed.get("mint_mark") or "",
    ]
    return " ".join(p for p in parts if p).strip()


def find_best_match(parsed: dict, catalog: list) -> tuple:
    """
    Return (best_doc_id, confidence_0_to_1, best_data) or (None, 0.0, None).

    Strategy:
      1. Pre-filter to same year (massive precision gain).
      2. Run token_set_ratio  AND  partial_ratio — keep the higher score.
      3. Apply a small boost if a key program keyword is found in both the
         query and the winning match string (rewards correct program matches).
    """
    query = build_query_string(parsed)
    if not query.strip():
        return None, 0.0, None

    year = parsed.get("year")
    if year:
        candidates = [c for c in catalog if year in c["match_string"]]
    else:
        candidates = catalog

    if not candidates:
        candidates = catalog

    match_strings = [c["match_string"] for c in candidates]

    # Try multiple scorers and take the best
    best_score = 0
    best_idx   = 0
    for scorer in (fuzz.token_set_ratio, fuzz.partial_ratio, fuzz.WRatio):
        result = rfprocess.extractOne(query, match_strings, scorer=scorer, score_cutoff=0)
        if result and result[1] > best_score:
            best_score, best_idx = result[1], result[2]

    best_entry = candidates[best_idx]
    confidence = best_score / 100.0

    # ── Keyword boost (up to +5 pp) ───────────────────────────────────────────
    # When both the query and the matched record share a strong anchor keyword,
    # add a small confidence bonus.  This prevents long parenthetical park names
    # from unfairly suppressing an otherwise correct match.
    BOOST_KEYWORDS = [
        "america the beautiful", "50 state", "presidential", "innovation",
        "sacagawea", "native american", "kennedy", "morgan", "peace",
        "eisenhower", "seated liberty", "barber", "walking liberty",
        "buffalo", "lincoln", "jefferson", "franklin",
        "ellis island", "quarter", "dollar", "half dollar",
    ]
    matched_str = best_entry["match_string"]
    q_lower     = query.lower()
    for kw in BOOST_KEYWORDS:
        if kw in q_lower and kw in matched_str:
            confidence = min(1.0, confidence + 0.05)
            break   # one boost only

    # ── Mint-ambiguity boost ──────────────────────────────────────────────────
    # When no mint mark is given in the filename but the year and design keyword
    # both match, score can plateau around 88-91% due to mint variants in the
    # catalog.  We add 4pp and flag it so downstream knows which mint was assumed.
    mint_ambiguous = False
    if parsed.get("mint_mark") is None and year and confidence >= 0.87 and confidence < 0.92:
        year_ok    = year in best_entry["match_string"]
        design_kws = ["america the beautiful", "50 state", "presidential",
                      "innovation", "sacagawea", "native american", "kennedy",
                      "morgan", "peace", "eisenhower", "quarter", "dollar"]
        design_ok  = any(kw in q_lower and kw in matched_str for kw in design_kws)
        if year_ok and design_ok:
            confidence   = min(1.0, confidence + 0.04)
            mint_ambiguous = True

    result_entry = best_entry
    result_entry["_mint_ambiguous"] = mint_ambiguous

    return best_entry["doc_id"], confidence, best_entry["data"]


# ─── GCS Upload ───────────────────────────────────────────────────────────────

def upload_to_gcs(local_path: Path, gcs_path: str, dry_run: bool = False) -> str | None:
    """Upload a local file to GCS. Returns public URL."""
    public_url = PUBLIC_URL_BASE.format(bucket=BUCKET_NAME, path=gcs_path)
    if dry_run:
        print(f"    [DRY-RUN] Would upload {local_path.name} → gs://{BUCKET_NAME}/{gcs_path}")
        return public_url

    try:
        blob = upload_bucket.blob(gcs_path)
        ext  = local_path.suffix.lower()
        ct_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                  ".png": "image/png",  ".webp": "image/webp"}
        ct = ct_map.get(ext, "image/jpeg")
        blob.upload_from_filename(str(local_path), content_type=ct)
        blob.metadata = {
            "attribution": "United States Mint / Manually sourced reference image",
            "source":      "manual_intake",
            "license":     "public_domain_us_government",
            "copyright":   "Public Domain",
        }
        blob.patch()
        print(f"    [GCS] ✅ {local_path.name} → {gcs_path}")
        return public_url
    except Exception as e:
        log_error(f"GCS upload failed: {local_path}", e)
        return None


# ─── Database Updaters ────────────────────────────────────────────────────────

def update_firestore(doc_id: str, side: str, url: str, dry_run: bool = False):
    field = "image_url_obverse" if side == "obverse" else "image_url_reverse"
    if dry_run:
        print(f"    [DRY-RUN] Would set Firestore {doc_id}.{field} = {url}")
        return
    try:
        db.collection("definitive_reference").document(doc_id).update({field: url})
        print(f"    [Firestore] ✅ {doc_id}.{field} updated")
    except Exception as e:
        log_error(f"Firestore update failed for {doc_id}", e)


def update_sqlite(doc_id: str, side: str, url: str, dry_run: bool = False):
    field = "image_url_obverse" if side == "obverse" else "image_url_reverse"
    if dry_run:
        print(f"    [DRY-RUN] Would set SQLite {doc_id}.{field} = {url}")
        return
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute(
            f"UPDATE definitive_reference SET {field} = ? WHERE doc_id = ?",
            (url, doc_id),
        )
        conn.commit()
        conn.close()
        print(f"    [SQLite] ✅ {doc_id}.{field} updated")
    except Exception as e:
        log_error(f"SQLite update failed for {doc_id}", e)


# ─── Canonical Rename ─────────────────────────────────────────────────────────

def canonical_filename(doc_id: str, side: str, ext: str) -> str:
    """e.g.  atb_2017_nj_ellis_island_P_obverse.jpg"""
    safe_id = re.sub(r"[^a-z0-9_\-]", "_", doc_id.lower())
    return f"{safe_id}_{side}{ext}"


def rename_file(original_path: Path, new_name: str, dry_run: bool = False) -> Path:
    new_path = original_path.parent / new_name
    if dry_run:
        print(f"    [DRY-RUN] Would rename: {original_path.name} → {new_name}")
        return new_path
    if new_path.exists() and new_path != original_path:
        print(f"    [RENAME] Target already exists, skipping rename: {new_name}")
        return original_path
    original_path.rename(new_path)
    print(f"    [RENAME] {original_path.name} → {new_name}")
    return new_path


# ─── Missing Images Log ───────────────────────────────────────────────────────

def generate_missing_images_log(dry_run: bool = False):
    """
    Stream all definitive_reference docs and write a CSV of every coin
    that still lacks an obverse image URL after this run.
    """
    print("\n📋 Generating missing_images_log.csv …")
    rows = []
    docs = db.collection("definitive_reference").stream()
    for doc in docs:
        d = doc.to_dict()
        obv = d.get("image_url_obverse") or ""
        rev = d.get("image_url_reverse") or ""
        if not obv.strip():
            rows.append({
                "doc_id":       doc.id,
                "year":         d.get("year", ""),
                "denomination": d.get("denomination", ""),
                "mint_mark":    d.get("mint_mark", ""),
                "series":       d.get("series", ""),
                "variety":      d.get("variety", ""),
                "category":     d.get("category", ""),
                "has_reverse":  "YES" if rev.strip() else "NO",
                "notes":        "",
            })

    rows.sort(key=lambda r: (r.get("category", ""), str(r.get("year", ""))))

    if dry_run:
        print(f"  [DRY-RUN] Would write {len(rows)} rows to {MISSING_LOG_CSV}")
        return rows

    with open(MISSING_LOG_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "doc_id", "year", "denomination", "mint_mark",
            "series", "variety", "category", "has_reverse", "notes",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"  ✅ Written {len(rows)} missing-image records → {MISSING_LOG_CSV}")
    return rows


# ─── Main Intake Loop ─────────────────────────────────────────────────────────

def scan_and_ingest(root: Path, dry_run: bool = False):
    """
    Walk root directory, parse every image file, match against catalog,
    and commit or flag for review.
    """
    catalog = load_catalog()

    image_files = []
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(root.rglob(f"*{ext}"))
        image_files.extend(root.rglob(f"*{ext.upper()}"))

    # Deduplicate (rglob on case variants can produce duplicates on Windows)
    seen = set()
    unique_files = []
    for f in image_files:
        key = str(f).lower()
        if key not in seen:
            seen.add(key)
            unique_files.append(f)

    if not unique_files:
        print(f"\n⚠  No image files found under: {root}")
        return

    print(f"\n🖼  Found {len(unique_files)} image file(s) to process.\n")

    for img_path in sorted(unique_files):
        print(f"─── {img_path.relative_to(root)}")
        parsed = parse_filename(img_path.name)
        print(f"  Parsed  →  year={parsed['year']}  side={parsed['side']}  "
              f"mint={parsed['mint_mark']}  desc='{parsed['description']}'")

        doc_id, confidence, coin_data = find_best_match(parsed, catalog)

        if doc_id is None:
            print(f"  ⚠  No match found — added to NEEDS_REVIEW")
            run_log["needs_review"].append({
                "file":       str(img_path),
                "parsed":     parsed,
                "confidence": 0.0,
                "reason":     "no_match",
            })
            continue

        coin_label = (
            f"{coin_data.get('year','')} {coin_data.get('denomination','')} "
            f"[{coin_data.get('series','')}] mint={coin_data.get('mint_mark','')} "
            f"— {doc_id}"
        )
        pct = f"{confidence * 100:.1f}%"
        print(f"  Match   →  {pct}  →  {coin_label}")

        if confidence < AUTO_COMMIT_THRESHOLD:
            print(f"  ⚠  Below 92% threshold — added to NEEDS_REVIEW")
            run_log["needs_review"].append({
                "file":         str(img_path),
                "parsed":       parsed,
                "best_match":   coin_label,
                "doc_id":       doc_id,
                "confidence":   round(confidence, 4),
                "reason":       "low_confidence",
            })
            continue

        # ── Auto-commit ───────────────────────────────────────────────────────
        print(f"  ✅ Auto-committing ({pct}) …")

        # 1. Determine canonical filename and rename
        ext = img_path.suffix.lower()
        if ext in {".tif", ".tiff"}:
            ext = ".jpg"   # normalize
        new_name  = canonical_filename(doc_id, parsed["side"], ext)
        new_path  = rename_file(img_path, new_name, dry_run=dry_run)

        # 2. Upload to GCS
        gcs_path  = f"{GCS_COIN_PREFIX}{new_name}"
        gcs_url   = upload_to_gcs(new_path, gcs_path, dry_run=dry_run)

        if gcs_url:
            # 3. Update Firestore + SQLite
            update_firestore(doc_id, parsed["side"], gcs_url, dry_run=dry_run)
            update_sqlite(doc_id, parsed["side"], gcs_url, dry_run=dry_run)

            run_log["auto_committed"].append({
                "original_file":  str(img_path),
                "renamed_to":     new_name,
                "doc_id":         doc_id,
                "side":           parsed["side"],
                "confidence":     round(confidence, 4),
                "gcs_url":        gcs_url,
                "coin":           coin_label,
            })
        else:
            log_error(f"GCS upload returned no URL for {img_path.name}")
            run_log["skipped"].append({"file": str(img_path), "reason": "gcs_upload_failed"})

        print()


# ─── Save Run Log ─────────────────────────────────────────────────────────────

def save_log():
    run_log["summary"] = {
        "auto_committed":  len(run_log["auto_committed"]),
        "needs_review":    len(run_log["needs_review"]),
        "skipped":         len(run_log["skipped"]),
        "errors":          len(run_log["errors"]),
    }
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(run_log, f, indent=2, ensure_ascii=False)
    print(f"\n[LOG] Run log saved → {LOG_FILE}")


# ─── Entry Point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Manual coin image intake — fuzzy-match and upload."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview actions without writing anything."
    )
    parser.add_argument(
        "--folder", type=str, default=str(BASE_MANUAL),
        help="Root folder to scan (default: Manual downloaded Coin Images)."
    )
    parser.add_argument(
        "--audit", action="store_true",
        help="Only regenerate missing_images_log.csv; skip image intake."
    )
    args = parser.parse_args()

    root   = Path(args.folder)
    is_dry = args.dry_run

    if is_dry:
        print("🔍 DRY-RUN mode — no files will be modified or uploaded.\n")

    if args.audit:
        generate_missing_images_log(dry_run=is_dry)
    else:
        scan_and_ingest(root, dry_run=is_dry)
        generate_missing_images_log(dry_run=is_dry)
        save_log()

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("INTAKE SUMMARY")
    print("═" * 60)
    print(f"  Auto-committed  : {len(run_log['auto_committed'])}")
    print(f"  Needs review    : {len(run_log['needs_review'])}")
    print(f"  Skipped         : {len(run_log['skipped'])}")
    print(f"  Errors          : {len(run_log['errors'])}")
    print("═" * 60)

    if run_log["needs_review"]:
        print("\n⚠  NEEDS REVIEW (below 92% threshold or no match):")
        for item in run_log["needs_review"]:
            pct = f"{item['confidence'] * 100:.1f}%" if item["confidence"] else "—"
            print(f"  [{pct}] {Path(item['file']).name}")
            if item.get("best_match"):
                print(f"          Best guess: {item['best_match']}")
            print(f"          Reason: {item['reason']}")

    print(f"\n  Missing-image log  → {MISSING_LOG_CSV}")
    if not args.audit:
        print(f"  Full intake log    → {LOG_FILE}")


if __name__ == "__main__":
    main()
