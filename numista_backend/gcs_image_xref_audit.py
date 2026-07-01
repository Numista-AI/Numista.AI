#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
gcs_image_xref_audit.py
=======================
Deep cloud cross-reference audit for Numista.AI.

Targets coin records flagged as "Missing both images" for
jseaman1204@gmail.com and verifies whether matching physical files
actually exist in the GCS uploads bucket.

GCS path structure confirmed:
    users/{email}/coins/{doc_id}/obverse.jpg
    users/{email}/coins/{doc_id}/reverse.jpg

Classification:
  LOGICAL_ORPHAN : Firestore URL fields blank, but matching file EXISTS in GCS.
  TRUE_ORPHAN    : Firestore URL fields blank AND no file exists in GCS.

Match strategy (in priority order):
  1. Doc-ID path  : GCS path contains the Firestore doc_id (primary, exact)
  2. Name template: {year}_{mint}_{theme-slug}_{program-slug}_{side}.ext
  3. Fuzzy keyword: year + at least 2 of [denom-slug, program-slug, theme-slug]

This script is ALWAYS read-only. It never writes to Firestore or GCS.

Usage:
    python gcs_image_xref_audit.py            # standard run
    python gcs_image_xref_audit.py --verbose  # print each coin result
"""

import sys
import re
import csv
import unicodedata
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── CONFIG ────────────────────────────────────────────────────────────────────
SCRIPT_DIR     = Path(__file__).resolve().parent
SA_KEY         = SCRIPT_DIR / "serviceAccountKey.json.json"
PROJECT_ID     = "studio-9101802118-8c9a8"
UPLOADS_BUCKET = f"numista-uploads-{PROJECT_ID}"
TARGET_USER    = "jseaman1204@gmail.com"
GCS_COINS_PFX  = f"users/{TARGET_USER}/coins/"
REPORT_OUT     = SCRIPT_DIR.parent / "gcs_xref_audit_report.csv"
IMAGE_EXTS     = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tiff", ".bmp"}

# ── INIT CLIENTS ──────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)

db             = firestore.client()
gcs            = storage.Client.from_service_account_json(str(SA_KEY))
uploads_bucket = gcs.bucket(UPLOADS_BUCKET)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_val(d: dict, *keys) -> str:
    for k in keys:
        v = d.get(k)
        if v is not None:
            return str(v).strip()
    return ""


def slugify(text: str) -> str:
    """Lowercase, strip accents, replace non-alnum with hyphens."""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def is_image(blob_name: str) -> bool:
    return Path(blob_name).suffix.lower() in IMAGE_EXTS


def build_fuzzy_fragments(year: str, mint: str, theme: str,
                           program: str, denom: str) -> list[str]:
    """Return loose keyword fragments for secondary matching."""
    frags = []
    y = (year or "").strip()
    for slug in [slugify(theme), slugify(program), slugify(denom)]:
        if slug and len(slug) > 4:
            if y:
                frags.append(f"{y}-{slug}")
                frags.append(f"{y}_{slug}")
            frags.append(slug)
    return frags


# ── STEP 1: FETCH MISSING-IMAGE COINS FROM FIRESTORE ─────────────────────────

def fetch_missing_coins() -> list[dict]:
    print(f"\n[STEP 1] Fetching coins for {TARGET_USER} from Firestore ...")
    col_ref = db.collection("users").document(TARGET_USER).collection("coins")
    docs    = list(col_ref.stream())
    print(f"         Total coin documents  : {len(docs):,}")

    missing = []
    for doc in docs:
        d   = doc.to_dict()
        obv = (d.get("image_url_obverse") or "").strip()
        rev = (d.get("image_url_reverse") or "").strip()
        if not obv and not rev:
            missing.append({
                "doc_id":  doc.id,
                "year":    get_val(d, "Year", "year", "date"),
                "mint":    get_val(d, "Mint Mark", "mint_mark", "mintMark", "mint"),
                "denom":   get_val(d, "Denomination", "denomination", "face_value"),
                "program": get_val(d, "Program/Series", "program", "Program", "series"),
                "theme":   get_val(d, "Theme/Subject", "theme", "subject"),
            })

    print(f"         Missing BOTH image URLs: {len(missing):,}")
    return missing, len(docs)


# ── STEP 2: SCAN GCS UPLOADS BUCKET ──────────────────────────────────────────

def scan_gcs() -> tuple[set[str], dict[str, list[str]]]:
    """
    Returns:
      doc_ids_in_gcs : set of doc_ids that have at least one file in GCS
      doc_blobs      : dict of doc_id -> list of blob names
    """
    print(f"\n[STEP 2] Scanning GCS bucket '{UPLOADS_BUCKET}' "
          f"prefix '{GCS_COINS_PFX}' ...")

    doc_blobs: dict[str, list[str]]  = defaultdict(list)
    loose_blobs:  list[str]          = []
    total_objects = 0
    total_images  = 0

    for blob in uploads_bucket.list_blobs(prefix=GCS_COINS_PFX):
        total_objects += 1
        name = blob.name
        # Expected structure: users/{email}/coins/{doc_id}/{filename}
        relative = name[len(GCS_COINS_PFX):]     # e.g.  "abc-123.../obverse.jpg"
        parts    = relative.split("/", 1)
        if len(parts) == 2 and parts[0]:
            candidate_id = parts[0]
            if is_image(parts[1]):
                total_images += 1
                doc_blobs[candidate_id].append(name)
        else:
            # Non-standard path — collect for fuzzy matching
            if is_image(name):
                total_images += 1
                loose_blobs.append(name)

    print(f"         Total objects under prefix  : {total_objects:,}")
    print(f"         Image files found           : {total_images:,}")
    print(f"         Unique doc_ids with images  : {len(doc_blobs):,}")

    return doc_blobs, loose_blobs, total_images


# ── STEP 3: CROSS-REFERENCE ───────────────────────────────────────────────────

def cross_reference(missing: list[dict],
                    doc_blobs: dict[str, list[str]],
                    loose_blobs: list[str],
                    verbose: bool) -> tuple[list[dict], int, int]:

    print(f"\n[STEP 3] Cross-referencing {len(missing):,} coins ...")

    logical_orphans = 0
    true_orphans    = 0
    results         = []

    for coin in missing:
        doc_id  = coin["doc_id"]
        year    = coin["year"]
        mint    = coin["mint"]
        denom   = coin["denom"]
        program = coin["program"]
        theme   = coin["theme"]
        label   = f"{year} {mint} {denom} - {program} ({theme})".strip("- ()")

        matched_blobs: list[str] = []
        match_method = ""

        # ── Primary: exact doc_id path match ─────────────────────────────
        if doc_id in doc_blobs:
            matched_blobs = doc_blobs[doc_id]
            match_method  = "doc_id_path"

        # ── Secondary: fuzzy keyword in loose_blobs ───────────────────────
        if not matched_blobs and loose_blobs:
            frags = build_fuzzy_fragments(year, mint, theme, program, denom)
            for bn in loose_blobs:
                bn_lower = bn.lower()
                if any(f and f in bn_lower for f in frags):
                    matched_blobs.append(bn)
                    match_method = "fuzzy_keyword"

        # ── Classify ──────────────────────────────────────────────────────
        if matched_blobs:
            status = "LOGICAL_ORPHAN"
            logical_orphans += 1
        else:
            status = "TRUE_ORPHAN"
            true_orphans += 1

        # Identify obverse / reverse
        obv_blobs = [b for b in matched_blobs
                     if any(x in Path(b).stem.lower()
                            for x in ["obverse", "obv", "front"])]
        rev_blobs = [b for b in matched_blobs
                     if any(x in Path(b).stem.lower()
                            for x in ["reverse", "rev", "back"])]
        ambiguous = [b for b in matched_blobs
                     if b not in obv_blobs and b not in rev_blobs]

        results.append({
            "status":         status,
            "doc_id":         doc_id,
            "coin_label":     label,
            "year":           year,
            "denom":          denom,
            "program":        program,
            "theme":          theme,
            "match_method":   match_method,
            "matched_files":  len(matched_blobs),
            "obv_files":      len(obv_blobs),
            "rev_files":      len(rev_blobs),
            "ambiguous_files":len(ambiguous),
            "sample_gcs_path":matched_blobs[0] if matched_blobs else "",
        })

        if verbose:
            icon = "🔗" if status == "LOGICAL_ORPHAN" else "❌"
            print(f"  {icon} {status:<16} {label[:65]}")
            if matched_blobs:
                print(f"         → {matched_blobs[0]}")

    return results, logical_orphans, true_orphans


# ── STEP 4: WRITE CSV + PRINT TABLE ──────────────────────────────────────────

FIELDNAMES = [
    "status", "doc_id", "coin_label", "year", "denom", "program", "theme",
    "match_method", "matched_files", "obv_files", "rev_files",
    "ambiguous_files", "sample_gcs_path"
]


def write_csv(results: list[dict]):
    print(f"\n[STEP 4] Writing report to {REPORT_OUT.name} ...")
    with open(REPORT_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
    print(f"  [OK] {len(results):,} rows written.")


def print_summary(logical: int, true_orphan: int,
                  total_fs: int, total_gcs_imgs: int):
    total    = logical + true_orphan
    heal_pct = (logical / total * 100) if total else 0
    bar      = "=" * 70

    print(f"\n{bar}")
    print("  NUMISTA.AI — GCS IMAGE CROSS-REFERENCE AUDIT — SUMMARY")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  MODE: DRY-RUN (read-only)")
    print(bar)
    print(f"  {'Firestore coin docs scanned':<40}: {total_fs:>6,}")
    print(f"  {'GCS image files scanned':<40}: {total_gcs_imgs:>6,}")
    print(f"  {'Coins with both URL fields blank':<40}: {total:>6,}")
    print(f"  {'-' * 48}")
    print(f"  {'🔗 LOGICAL ORPHANS (file in GCS, link missing)':<40}: {logical:>6,}  ({heal_pct:.1f}%)")
    print(f"  {'❌ TRUE ORPHANS (no file in GCS at all)':<40}: {true_orphan:>6,}  ({100 - heal_pct:.1f}%)")
    print(bar)
    print(f"\n  RECOMMENDATION:")
    if logical > 0:
        print(f"    ✅  {logical:,} coins can be auto-healed by re-linking GCS paths.")
    if true_orphan > 0:
        print(f"    ⚠️   {true_orphan:,} coins need image sourcing before they can be healed.")
    print(f"\n  Full detail → {REPORT_OUT.name}\n")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Read-only GCS cross-reference audit for missing image links."
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Print each coin result while processing.")
    args = parser.parse_args()

    print("=" * 70)
    print("NUMISTA.AI -- GCS IMAGE CROSS-REFERENCE AUDIT")
    print("Mode         : DRY-RUN  (read-only, no writes)")
    print(f"Target user  : {TARGET_USER}")
    print(f"Bucket       : {UPLOADS_BUCKET}")
    print("=" * 70)

    missing, total_fs = fetch_missing_coins()
    if not missing:
        print("\n✅ No coins with missing image URLs. Nothing to audit.")
        return

    doc_blobs, loose_blobs, total_gcs_imgs = scan_gcs()
    results, logical, true_orphan = cross_reference(
        missing, doc_blobs, loose_blobs, verbose=args.verbose
    )
    write_csv(results)
    print_summary(logical, true_orphan, total_fs, total_gcs_imgs)


if __name__ == "__main__":
    main()
