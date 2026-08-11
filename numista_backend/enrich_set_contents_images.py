#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
enrich_set_contents_images.py
==============================
Enriches the set_contents array inside parent set documents with
reference library image URLs, operating across ALL users.

Architecture
------------
1. INDEX BUILD  — Scans both GCS reference buckets once at startup into a
   single unified in-memory index (dict of gcs_path → public https URL).
   The code treats both buckets as one namespace; physical consolidation
   can happen later as a pure ops task without touching this script.

2. COIN MATCHING — For each coin object in set_contents:
   a. Map its type name (e.g. "Mercury Dime") to a known GCS subfolder.
   b. Search the index for files in that folder matching the coin's year
      AND a side keyword (obverse / reverse).
   c. If no year-specific match, widen to any image in that folder.
   d. If still no match, fall back to generic_denominations/ placeholder.

3. EXONUMIA BYPASS — Items identified as non-government medals / custom
   commemoratives are routed directly to a generic silver placeholder
   and tagged image_source: "placeholder".

4. FIRESTORE WRITE — Updated set_contents (native array) is written back
   with set(merge=True).  Integrity badges are appended to every coin
   object:  image_source, physical_capture_status, image_match_quality.

5. SCOPE — Iterates every user in the users/ collection and all their
   set documents (category == "set", set_broken_up == False or None).

Usage
-----
    python enrich_set_contents_images.py             # dry-run (safe)
    python enrich_set_contents_images.py --execute   # write to Firestore
"""

import sys
import re
import csv
import ast
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── CONFIG ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
SA_KEY     = SCRIPT_DIR / "serviceAccountKey.json" if (SCRIPT_DIR / "serviceAccountKey.json").exists() else SCRIPT_DIR / "serviceAccountKey.json.json"
LOG_OUT    = SCRIPT_DIR.parent / "set_enrichment_log.csv"

# Both reference buckets — unified at index time
REF_BUCKET_NAME   = "numista-reference-library"
USMINT_BUCKET_NAME = "us_mint_coin_images"

# Public URL base (no auth required for these reference images)
GCS_PUBLIC = "https://storage.googleapis.com/{bucket}/{path}"

# ── COIN TYPE → GCS SUBFOLDER MAP ─────────────────────────────────────────────
# Keys are lower-cased type names from set_contents Denomination field.
# Values are folder prefixes within the reference library bucket.
COIN_FOLDER_MAP: dict[str, list[str]] = {
    # Cents
    "lincoln cent":                  ["reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Wheat_cent/",
                                      "reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/"],
    "lincoln head cent":             ["reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Wheat_cent/"],
    "indian head cent":              ["reference_library/wikimedia_uscoin/United_States_cents/Indian_Head_cent/"],
    "flying eagle cent":             ["reference_library/wikimedia_uscoin/United_States_cents/Flying_Eagle_cent/"],
    # Nickels
    "jefferson nickel":              ["reference_library/wikimedia_uscoin/United_States_nickels/Jefferson_nickel/",
                                      "reference_library/wikimedia_uscoin/United_States_nickels/Jefferson_nickel/Wartime_Jefferson_nickel/"],
    "buffalo nickel":                ["reference_library/wikimedia_uscoin/United_States_nickels/Buffalo_nickels/"],
    "liberty head nickel":           ["reference_library/wikimedia_uscoin/United_States_nickels/Liberty_Head_nickel/"],
    "shield nickel":                 ["reference_library/wikimedia_uscoin/United_States_nickels/Shield_nickel/"],
    # Dimes
    "mercury dime":                  ["reference_library/wikimedia_uscoin/United_States_dimes/Mercury_dimes/"],
    "roosevelt dime":                ["reference_library/wikimedia_uscoin/United_States_dimes/Roosevelt_dimes/"],
    "barber dime":                   ["reference_library/wikimedia_uscoin/United_States_dimes/Barber_dimes/"],
    "liberty seated dime":           ["reference_library/wikimedia_uscoin/United_States_dimes/Seated_Liberty_dimes/"],
    "capped bust dime":              ["reference_library/wikimedia_uscoin/United_States_dimes/Capped_Bust_dimes/"],
    # Quarters
    "washington quarter":            ["reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/"],
    "barber quarter":                ["reference_library/wikimedia_uscoin/United_States_quarters/Barber_quarter/"],
    "standing liberty quarter":      ["reference_library/wikimedia_uscoin/United_States_quarters/Standing_Liberty_quarters/"],
    "liberty seated quarter":        ["reference_library/wikimedia_uscoin/United_States_quarters/Seated_Liberty_quarter/"],
    "capped bust quarter":           ["reference_library/wikimedia_uscoin/United_States_quarters/Capped_Bust_quarter/"],
    "draped bust quarter":           ["reference_library/wikimedia_uscoin/United_States_quarters/Draped_Bust_quarter/"],
    # Half Dollars
    "walking liberty half dollar":   ["reference_library/wikimedia_uscoin/Half_dollar__United_States_/Walking_Liberty_half_dollars/"],
    "franklin half dollar":          ["reference_library/wikimedia_uscoin/Half_dollar__United_States_/Franklin_half_dollar/"],
    "kennedy half dollar":           ["reference_library/wikimedia_uscoin/Half_dollar__United_States_/Kennedy_half_dollar/"],
    "barber half dollar":            ["reference_library/wikimedia_uscoin/Half_dollar__United_States_/Barber_half_dollar/"],
    "liberty seated half dollar":    ["reference_library/wikimedia_uscoin/Half_dollar__United_States_/Seated_Liberty_half_dollar/"],
    "capped bust half dollar":       ["reference_library/wikimedia_uscoin/Half_dollar__United_States_/Capped_Bust_half_dollar/"],
    # Dollars
    "morgan silver dollar":          ["reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"],
    "peace silver dollar":           ["reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"],
    "peace dollar":                  ["reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"],
    "eisenhower dollar":             ["reference_library/wikimedia_uscoin/Eisenhower_dollars/"],
    "american silver eagle":         ["reference_library/silver_eagles/"],
    "silver eagle":                  ["reference_library/silver_eagles/"],
}

# Generic denomination fallbacks (canonical denomination → generic image)
GENERIC_FALLBACK: dict[str, str] = {
    "cent":          "reference_library/generic_denominations/one_cent_obverse.png",
    "five cents":    "reference_library/generic_denominations/five_cents_obverse.png",
    "dime":          "reference_library/generic_denominations/dime.png",
    "quarter dollar":"reference_library/generic_denominations/quarter_dollar.png",
    "half dollar":   "reference_library/generic_denominations/half_dollar.png",
    "dollar":        "reference_library/generic_denominations/half_dollar.png",
}

# Canonical denomination for each type name (for generic fallback lookup)
TYPE_TO_CANONICAL: dict[str, str] = {
    "lincoln cent": "cent", "lincoln head cent": "cent",
    "indian head cent": "cent", "flying eagle cent": "cent",
    "jefferson nickel": "five cents", "buffalo nickel": "five cents",
    "liberty head nickel": "five cents", "shield nickel": "five cents",
    "mercury dime": "dime", "roosevelt dime": "dime",
    "barber dime": "dime", "liberty seated dime": "dime",
    "washington quarter": "quarter dollar", "barber quarter": "quarter dollar",
    "standing liberty quarter": "quarter dollar",
    "walking liberty half dollar": "half dollar",
    "franklin half dollar": "half dollar", "kennedy half dollar": "half dollar",
    "barber half dollar": "half dollar",
    "morgan silver dollar": "dollar", "peace dollar": "dollar",
    "peace silver dollar": "dollar", "eisenhower dollar": "dollar",
    "american silver eagle": "dollar", "silver eagle": "dollar",
}

# Exonumia patterns — routed directly to generic silver placeholder
EXONUMIA_KEYWORDS = [
    "commemorative", "medal", "medallion", "token", "exonumia",
    "silver comm", "silver commemorative",
]

GENERIC_SILVER_PATH = "reference_library/generic_denominations/half_dollar.png"

# Side keyword sets for obverse/reverse detection
OBVERSE_KEYWORDS = {"obverse", "obv", "front", "heads", "left", "_obv", "observe"}
REVERSE_KEYWORDS = {"reverse", "rev", "back", "tails", "right", "_rev"}


# ── INIT ────────────────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)
db = firestore.client()
# Use the service account key for GCS so we don't depend on gcloud ADC tokens
gcs = storage.Client.from_service_account_json(str(SA_KEY))


# ── HELPERS ─────────────────────────────────────────────────────────────────────

def build_bucket_index(bucket_name: str, prefix: str = "") -> dict[str, str]:
    """Return {blob_name: public_https_url} for all blobs in bucket/prefix."""
    bucket = gcs.bucket(bucket_name)
    index = {}
    for blob in bucket.list_blobs(prefix=prefix):
        url = GCS_PUBLIC.format(bucket=bucket_name, path=blob.name)
        index[blob.name] = url
    return index


def is_exonumia(denomination: str) -> bool:
    d = denomination.lower()
    return any(kw in d for kw in EXONUMIA_KEYWORDS)


def detect_side(filename: str) -> str:
    """Return 'obverse', 'reverse', 'both', or 'unknown'."""
    f = filename.lower()
    has_obv = any(kw in f for kw in OBVERSE_KEYWORDS)
    has_rev = any(kw in f for kw in REVERSE_KEYWORDS)
    # LEFT = obverse, RIGHT = reverse (Wikimedia convention)
    if "_left" in f or "left." in f:
        has_obv = True
    if "_right" in f or "right." in f:
        has_rev = True
    if has_obv and has_rev:
        return "both"
    if has_obv:
        return "obverse"
    if has_rev:
        return "reverse"
    return "unknown"


def find_best_match(
    index: dict[str, str],
    folders: list[str],
    year: str,
    side: str,          # "obverse" or "reverse"
) -> tuple[str, str]:  # (url, match_quality)
    """
    Search index for a file in any of the given folders matching year + side.
    Returns (url, quality) where quality is one of:
        "exact_year" | "nearest_year" | "type_generic" | "not_found"
    """
    candidates = [
        (blob, url) for blob, url in index.items()
        if any(blob.startswith(f) for f in folders)
        and not blob.endswith("/")
        and blob.lower().rsplit(".", 1)[-1] in ("jpg", "jpeg", "png", "webp")
    ]

    if not candidates:
        return "", "not_found"

    side_kws = OBVERSE_KEYWORDS if side == "obverse" else REVERSE_KEYWORDS
    left_right = "_left" if side == "obverse" else "_right"

    # Pass 1: exact year + correct side
    for blob, url in candidates:
        fname = Path(blob).name.lower()
        if year in fname and (
            any(kw in fname for kw in side_kws) or left_right in fname
        ):
            return url, "exact_year"

    # Pass 2: exact year, any side (for coins where only one side is in library)
    for blob, url in candidates:
        fname = Path(blob).name.lower()
        if year in fname:
            return url, "exact_year_any_side"

    # Pass 3: correct side, no year requirement (type-generic)
    for blob, url in candidates:
        fname = Path(blob).name.lower()
        if any(kw in fname for kw in side_kws) or left_right in fname:
            return url, "type_generic"

    # Pass 4: anything in the folder
    blob, url = candidates[0]
    return url, "type_generic"


def enrich_coin(
    coin: dict,
    ref_index: dict[str, str],
    mint_index: dict[str, str],
) -> tuple[dict, str, str]:
    """
    Returns (enriched_coin_dict, obverse_url, match_quality_label).
    Modifies coin in-place with image fields + integrity badges.
    """
    raw_denom = coin.get("Denomination", "")
    year      = str(coin.get("Year", "")).strip()
    type_key  = raw_denom.lower().strip()

    # ── Exonumia bypass ───────────────────────────────────────────────────────
    if is_exonumia(raw_denom):
        generic_url = ref_index.get(
            GENERIC_SILVER_PATH,
            GCS_PUBLIC.format(bucket=REF_BUCKET_NAME, path=GENERIC_SILVER_PATH)
        )
        coin["image_url_obverse"]        = generic_url
        coin["image_url_reverse"]        = ""
        coin["image_source"]             = "placeholder"
        coin["physical_capture_status"]  = "pending_sourcing"
        coin["image_match_quality"]      = "exonumia_placeholder"
        return coin, generic_url, "exonumia_placeholder"

    # ── Primary: reference library ────────────────────────────────────────────
    folders = COIN_FOLDER_MAP.get(type_key, [])

    obv_url, obv_quality = ("", "not_found")
    rev_url, _           = ("", "not_found")

    if folders:
        obv_url, obv_quality = find_best_match(ref_index, folders, year, "obverse")
        rev_url, _           = find_best_match(ref_index, folders, year, "reverse")

    # ── Secondary: US Mint bucket (modern coins) ───────────────────────────────
    if not obv_url and mint_index:
        mint_candidates = [
            (b, u) for b, u in mint_index.items()
            if year in Path(b).name.lower() or type_key.split()[0] in Path(b).name.lower()
        ]
        if mint_candidates:
            obv_url, obv_quality = mint_candidates[0][1], "us_mint_match"
            if len(mint_candidates) > 1:
                rev_url = mint_candidates[1][1]

    # ── Tertiary: generic denomination fallback ────────────────────────────────
    if not obv_url:
        canonical = TYPE_TO_CANONICAL.get(type_key, "")
        generic_path = GENERIC_FALLBACK.get(canonical, "")
        if generic_path:
            obv_url     = GCS_PUBLIC.format(bucket=REF_BUCKET_NAME, path=generic_path)
            obv_quality = "generic_denomination"

    # ── Inject fields ─────────────────────────────────────────────────────────
    coin["image_url_obverse"]       = obv_url
    coin["image_url_reverse"]       = rev_url
    coin["image_source"]            = "reference_library" if "generic" not in obv_quality and "placeholder" not in obv_quality else obv_quality
    coin["physical_capture_status"] = "pending_sourcing"
    coin["image_match_quality"]     = obv_quality

    return coin, obv_url, obv_quality


def get_val(d: dict, *keys) -> str:
    for k in keys:
        v = d.get(k)
        if v is not None:
            return str(v).strip()
    return ""


# ── MAIN ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Enrich set_contents arrays with reference library image URLs."
    )
    parser.add_argument("--execute", action="store_true",
                        help="Write to Firestore (default: dry-run).")
    args = parser.parse_args()
    dry_run = not args.execute

    mode = "DRY-RUN (read-only)" if dry_run else "EXECUTE — WRITING TO FIRESTORE"
    print("=" * 72)
    print("NUMISTA.AI — SET CONTENTS IMAGE ENRICHMENT")
    print(f"Mode   : {mode}")
    print(f"Run at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    # ── Step 1: Build unified reference index ──────────────────────────────────
    print("\n[INDEX] Scanning reference buckets (one-time pass)...")
    ref_index  = build_bucket_index(REF_BUCKET_NAME,   prefix="reference_library/")
    mint_index = build_bucket_index(USMINT_BUCKET_NAME, prefix="Numista_Attributed_Coins")
    print(f"  numista-reference-library : {len(ref_index):,} blobs indexed")
    print(f"  us_mint_coin_images       : {len(mint_index):,} blobs indexed")
    print(f"  Unified index total       : {len(ref_index) + len(mint_index):,}")

    # ── Step 2: Iterate all users ──────────────────────────────────────────────
    print("\n[USERS] Fetching all users...")
    users = list(db.collection("users").stream())
    print(f"  Found {len(users)} user(s)")

    log_rows       = []
    total_sets     = 0
    total_coins    = 0
    match_counts   = {"exact_year": 0, "exact_year_any_side": 0,
                      "type_generic": 0, "generic_denomination": 0,
                      "exonumia_placeholder": 0, "us_mint_match": 0,
                      "not_found": 0}

    for user_doc in users:
        uid     = user_doc.id
        col_ref = db.collection("users").document(uid).collection("coins")

        # Query: category == "set"
        set_docs = list(col_ref.where(  # type: ignore[call-arg]
            filter=firestore.And([
                firestore.FieldFilter("category", "==", "set")
            ])
        ).stream())

        if not set_docs:
            continue

        print(f"\n  [{uid}] — {len(set_docs)} set document(s)")

        for doc in set_docs:
            d          = doc.to_dict() or {}
            doc_id     = doc.id
            theme      = get_val(d, "Theme/Subject", "theme")
            source_file = get_val(d, "source_file")
            broken_up  = d.get("set_broken_up")

            # Skip if already broken up (bool True or string "True")
            if str(broken_up).lower() == "true":
                print(f"    SKIP {doc_id[:8]} — already broken up")
                continue

            # Load set_contents — handle both native list and stringified
            raw_sc = d.get("set_contents")
            if raw_sc is None:
                print(f"    SKIP {doc_id[:8]} — set_contents is None")
                continue
            if isinstance(raw_sc, str):
                try:
                    contents = ast.literal_eval(raw_sc)
                except Exception:
                    print(f"    SKIP {doc_id[:8]} — set_contents unparseable")
                    continue
            else:
                contents = list(raw_sc)

            if not contents:
                print(f"    SKIP {doc_id[:8]} — set_contents is empty")
                continue

            total_sets += 1
            print(f"    SET  {doc_id[:8]}  \"{theme[:50]}\"  ({len(contents)} coins)")

            enriched = []
            for coin in contents:
                if not isinstance(coin, dict):
                    enriched.append(coin)
                    continue

                original_denom = coin.get("Denomination", "")
                enriched_coin, obv_url, quality = enrich_coin(
                    dict(coin), ref_index, mint_index
                )
                enriched.append(enriched_coin)
                total_coins += 1
                match_counts[quality] = match_counts.get(quality, 0) + 1

                log_rows.append({
                    "user":               uid,
                    "set_doc_id":         doc_id,
                    "set_theme":          theme[:60],
                    "source_file":        source_file,
                    "coin_denomination":  original_denom,
                    "coin_year":          coin.get("Year", ""),
                    "image_url_obverse":  obv_url,
                    "image_url_reverse":  enriched_coin.get("image_url_reverse", ""),
                    "image_source":       enriched_coin.get("image_source", ""),
                    "match_quality":      quality,
                    "dry_run":            dry_run,
                })

                flag = "✅" if "exact" in quality else ("⚠️" if "generic" in quality else "🔷")
                print(f"      {flag} {original_denom:<35} [{quality}]")

            # Write back to Firestore
            if not dry_run:
                doc.reference.set({"set_contents": enriched}, merge=True)

    # ── Step 3: Write log ──────────────────────────────────────────────────────
    print(f"\n[LOG] Writing {len(log_rows)} rows to {LOG_OUT.name}...")
    with open(LOG_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "user", "set_doc_id", "set_theme", "source_file",
            "coin_denomination", "coin_year",
            "image_url_obverse", "image_url_reverse",
            "image_source", "match_quality", "dry_run"
        ])
        w.writeheader()
        w.writerows(log_rows)
    print(f"  [OK] Written to {LOG_OUT}")

    # ── Summary ────────────────────────────────────────────────────────────────
    bar = "=" * 72
    print(f"\n{bar}")
    print("  ENRICHMENT SUMMARY")
    print(f"  Mode: {mode}")
    print(bar)
    print(f"  {'Users processed':<45}: {len(users):>5}")
    print(f"  {'Set documents enriched':<45}: {total_sets:>5}")
    print(f"  {'Individual coin items processed':<45}: {total_coins:>5}")
    print(f"  {'-' * 51}")
    print(f"  {'✅  Exact year match':<45}: {match_counts.get('exact_year', 0):>5}")
    print(f"  {'✅  Exact year (any side)':<45}: {match_counts.get('exact_year_any_side', 0):>5}")
    print(f"  {'⚠️   Type-generic (folder match)':<45}: {match_counts.get('type_generic', 0):>5}")
    print(f"  {'⚠️   Generic denomination fallback':<45}: {match_counts.get('generic_denomination', 0):>5}")
    print(f"  {'🔷  US Mint bucket match':<45}: {match_counts.get('us_mint_match', 0):>5}")
    print(f"  {'🔷  Exonumia placeholder':<45}: {match_counts.get('exonumia_placeholder', 0):>5}")
    print(f"  {'❌  Not found':<45}: {match_counts.get('not_found', 0):>5}")
    print(bar)
    if dry_run:
        print("\n  ► DRY-RUN complete. No Firestore writes made.")
        print("  ► Run with --execute to apply enrichment.")
    else:
        print("\n  ✅ Enrichment written to Firestore successfully.")
    print()


if __name__ == "__main__":
    main()
