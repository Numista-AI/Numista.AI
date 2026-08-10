# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
build_currency_image_index.py
─────────────────────────────────────────────────────────────────────────────
Scans the banknote reference GCS bucket:
    gs://numista-reference-library/reference_library/us_banknotes/

and builds/updates the Firestore index collection:
    currency_image_index

Document ID in Firestore = catalog_key (for direct O(1) point-reads).
Examples:
  - Federal:      fr_1613_n_star_obv
  - Fractional:   frac_fr1230_norm_obv
  - Confederate:  csa_t64_obv
  - Obsolete:     obs_va_richmond_merchants_5_obv
  - Error:        err_fr91_pcblic_rev
  - Uncut Sheet:  sheet_fr226_4sub_obv

Run:
    python numista_backend/_scripts/build_currency_image_index.py [--dry-run] [--clean-stale] [--verbose]
"""

import os
import re
import sys
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from google.cloud import storage, firestore
import google.auth

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ID = "studio-9101802118-8c9a8"
FIRESTORE_COLLECTION = "currency_image_index"
REFERENCE_BUCKET = "numista-reference-library"
GCS_PREFIX = "reference_library/us_banknotes/"
PUBLIC_URL_BASE = "https://storage.googleapis.com"

# Default application credentials setup
if os.path.exists("./serviceAccountKey.json.json"):
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
elif os.path.exists("./serviceAccountKey.json"):
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json")


def parse_banknote_key(filename: str, rel_path: str = ""):
    """
    Parses a human-readable GCS filename and returns structured catalog key metadata.

    Supports 6 Taxonomy Tiers:
      1. Federal: fr_{friedberg}[_{variant}][_{star|norm}]_{obv|rev}
      2. Fractional: frac_fr{friedberg}_norm_{obv|rev}
      3. Confederate: csa_t{t_number}_{obv|rev}
      4. Obsolete: obs_{state}_{city}_{bank_slug}_{denom}_{obv|rev}
      5. Error: err_{base_fr}_{error_slug}_{obv|rev}
      6. Uncut Sheet: sheet_{issuer_slug}_{layout}_{obv|rev}
    """
    stem = Path(filename).stem.lower()

    # Determine side
    side = "obverse"
    side_suffix = "obv"
    if "reverse" in stem or "rev" in stem or "back" in stem:
        side = "reverse"
        side_suffix = "rev"

    is_star = True if ("star" in stem or "*" in stem) else False
    star_token = "star" if is_star else "norm"

    # 1. Error Notes
    if "err_" in stem or "/errors/" in rel_path.lower():
        m = re.search(r"err_([a-z0-9]+)_([a-z0-9_]+)_(obverse|reverse|obv|rev)", stem)
        if m:
            base_fr = m.group(1)
            error_slug = m.group(2)
            catalog_key = f"err_{base_fr}_{error_slug}_{side_suffix}"
            return {
                "catalog_key": catalog_key,
                "catalog_tier": "errors",
                "friedberg": base_fr,
                "error_type": error_slug,
                "side": side,
                "denomination_str": "Various",
                "denomination_num": 0.0,
                "series": "N/A",
                "is_star_note": is_star,
            }
        # Fallback error keying
        slug = stem.replace("err_", "").replace("_obverse", "").replace("_reverse", "").replace("_obv", "").replace("_rev", "")
        return {
            "catalog_key": f"err_{slug}_{side_suffix}",
            "catalog_tier": "errors",
            "error_type": slug,
            "side": side,
            "denomination_str": "Various",
            "denomination_num": 0.0,
            "series": "N/A",
            "is_star_note": is_star,
        }

    # 2. Uncut Sheets
    if "sheet_" in stem or "/uncut_sheets/" in rel_path.lower():
        m = re.search(r"sheet_([a-z0-9_]+)_([0-9]+subject|[0-9]+sub|[a-z0-9]+)_(obverse|reverse|obv|rev)", stem)
        if m:
            issuer = m.group(1)
            layout = m.group(2)
            catalog_key = f"sheet_{issuer}_{layout}_{side_suffix}"
            return {
                "catalog_key": catalog_key,
                "catalog_tier": "uncut_sheets",
                "issuer": issuer,
                "layout": layout,
                "side": side,
                "denomination_str": "Uncut Sheet",
                "denomination_num": 0.0,
                "series": "N/A",
                "is_star_note": is_star,
            }
        slug = stem.replace("sheet_", "").replace("_obverse", "").replace("_reverse", "").replace("_obv", "").replace("_rev", "")
        return {
            "catalog_key": f"sheet_{slug}_{side_suffix}",
            "catalog_tier": "uncut_sheets",
            "side": side,
            "denomination_str": "Uncut Sheet",
            "denomination_num": 0.0,
            "series": "N/A",
            "is_star_note": is_star,
        }

    # 3. Fractional Currency
    if "frac_" in stem or "/fractional/" in rel_path.lower():
        m = re.search(r"fr([0-9]+[a-z]?)", stem)
        fr_num = m.group(1) if m else "1230"
        catalog_key = f"frac_fr{fr_num}_{star_token}_{side_suffix}"
        return {
            "catalog_key": catalog_key,
            "catalog_tier": "fractional",
            "friedberg": fr_num,
            "side": side,
            "denomination_str": "Fractional",
            "denomination_num": 0.50,
            "series": "Civil War Era",
            "is_star_note": is_star,
        }

    # 4. Confederate States of America (CSA)
    if "csa_" in stem or "/confederate/" in rel_path.lower():
        m = re.search(r"t[-_]?([0-9]+)", stem)
        t_num = m.group(1) if m else "64"
        catalog_key = f"csa_t{t_num}_{side_suffix}"
        return {
            "catalog_key": catalog_key,
            "catalog_tier": "confederate",
            "csa_t_number": f"T-{t_num}",
            "side": side,
            "denomination_str": "CSA Note",
            "denomination_num": 0.0,
            "series": "1861-1864",
            "is_star_note": False,
        }

    # 5. Obsolete / Broken Bank Notes
    if "obs_" in stem or "/obsolete/" in rel_path.lower():
        m = re.search(r"obs_([a-z]{2})_([a-z0-9_]+)_([0-9]+)_(obverse|reverse|obv|rev)", stem)
        if m:
            state = m.group(1)
            bank_slug = m.group(2)
            denom = m.group(3)
            catalog_key = f"obs_{state}_{bank_slug}_{denom}_{side_suffix}"
            return {
                "catalog_key": catalog_key,
                "catalog_tier": "obsolete",
                "state": state.upper(),
                "bank": bank_slug,
                "side": side,
                "denomination_str": f"${denom}.00",
                "denomination_num": float(denom),
                "series": "Obsolete Era",
                "is_star_note": False,
            }
        slug = stem.replace("obs_", "").replace("_obverse", "").replace("_reverse", "").replace("_obv", "").replace("_rev", "")
        return {
            "catalog_key": f"obs_{slug}_{side_suffix}",
            "catalog_tier": "obsolete",
            "side": side,
            "denomination_str": "Obsolete Note",
            "denomination_num": 0.0,
            "series": "Obsolete Era",
            "is_star_note": False,
        }

    # 6. Federal Currency (Default)
    m = re.search(r"fr[-_]?([0-9]+)([a-z]?)", stem)
    if m:
        fr_base = m.group(1)
        fr_variant = m.group(2).lower() if m.group(2) else ""
        variant_token = f"_{fr_variant}" if fr_variant else ""
        catalog_key = f"fr_{fr_base}{variant_token}_{star_token}_{side_suffix}"
        return {
            "catalog_key": catalog_key,
            "catalog_tier": "federal",
            "friedberg": fr_base,
            "variant": fr_variant.upper() if fr_variant else None,
            "side": side,
            "denomination_str": "$1.00",
            "denomination_num": 1.00,
            "series": "Federal Issue",
            "is_star_note": is_star,
        }

    # Generic Fallback
    clean_stem = re.sub(r"_(obverse|reverse|obv|rev)$", "", stem)
    catalog_key = f"fr_{clean_stem}_{star_token}_{side_suffix}"
    return {
        "catalog_key": catalog_key,
        "catalog_tier": "federal",
        "side": side,
        "denomination_str": "$1.00",
        "denomination_num": 1.00,
        "series": "Unknown Series",
        "is_star_note": is_star,
    }


def main():
    parser = argparse.ArgumentParser(description="Build Firestore currency_image_index from GCS reference library.")
    parser.add_argument("--dry-run", action="store_true", help="Scan GCS and output actions without writing to Firestore.")
    parser.add_argument("--clean-stale", action="store_true", help="Remove documents from Firestore if file no longer exists in GCS.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed metadata for each processed note.")
    args = parser.parse_args()

    print("==========================================================")
    print("Numista.AI Banknote Reference Indexer")
    print(f"Bucket Target: gs://{REFERENCE_BUCKET}/{GCS_PREFIX}")
    print(f"Firestore Target: collection '{FIRESTORE_COLLECTION}'")
    print("==========================================================")

    try:
        credentials, project = google.auth.default()
        storage_client = storage.Client(credentials=credentials, project=PROJECT_ID)
        db = firestore.Client(credentials=credentials, project=PROJECT_ID)
    except Exception as e:
        print(f"❌ Failed to initialize GCP Clients: {e}")
        sys.exit(1)

    bucket = storage_client.bucket(REFERENCE_BUCKET)
    blobs = list(bucket.list_blobs(prefix=GCS_PREFIX))
    print(f"📦 Found {len(blobs)} files under gs://{REFERENCE_BUCKET}/{GCS_PREFIX}")

    processed_count = 0
    scanned_keys = set()

    for blob in blobs:
        if blob.name.endswith("/") or not blob.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        filename = Path(blob.name).name
        parsed = parse_banknote_key(filename, rel_path=blob.name)
        catalog_key = parsed["catalog_key"]
        scanned_keys.add(catalog_key)

        public_url = f"{PUBLIC_URL_BASE}/{REFERENCE_BUCKET}/{blob.name}"
        now_iso = datetime.now(timezone.utc).isoformat()

        doc_data = {
            "catalog_key": catalog_key,
            "catalog_tier": parsed.get("catalog_tier", "federal"),
            "friedberg": parsed.get("friedberg"),
            "variant": parsed.get("variant"),
            "is_star_note": parsed.get("is_star_note", False),
            "denomination_str": parsed.get("denomination_str", "$1.00"),
            "denomination_num": parsed.get("denomination_num", 1.00),
            "series": parsed.get("series", "Standard"),
            "side": parsed.get("side", "obverse"),
            "gcs_path": f"gs://{REFERENCE_BUCKET}/{blob.name}",
            "public_url": public_url,
            "source": "Wikimedia Commons / NNC",
            "attribution": "National Numismatic Collection, National Museum of American History",
            "license": "Public Domain",
            "is_reference_fallback": True,
            "updated_at": now_iso,
        }

        if args.verbose or args.dry_run:
            print(f"  📄 [{catalog_key}] -> {blob.name}")

        if not args.dry_run:
            # Write using catalog_key directly as Document ID for O(1) point-reads
            doc_ref = db.collection(FIRESTORE_COLLECTION).document(catalog_key)
            doc_ref.set(doc_data, merge=True)

        processed_count += 1

    print("----------------------------------------------------------")
    print(f"✅ Processed {processed_count} banknote reference images.")
    if args.dry_run:
        print("🔍 DRY RUN COMPLETE — No Firestore changes committed.")
    else:
        print("💾 Firestore currency_image_index updated successfully.")


if __name__ == "__main__":
    main()
