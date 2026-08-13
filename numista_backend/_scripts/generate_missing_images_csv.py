"""
System-of-Record (SoR) Multi-Account Missing Image Audit & Provenance Sourcing Tracker
Schema Version: v4.0.0
Desktop Web Launch Target: November 1, 2026

Generates a fully reproducible, legal-grade 34-column CSV tracking missing obverse and reverse
images across confirmed real-person production accounts in Numista.AI.
"""

import argparse
import csv
import datetime
import hashlib
import json
import logging
import os
import re
import sys
import urllib.parse
import urllib.request

import firebase_admin
from firebase_admin import credentials, firestore

SCHEMA_VERSION = "v4.0.0"

# Target production accounts (Strict Allow-List)
PRODUCTION_ACCOUNTS = [
    "jseaman1204@gmail.com",
    "eric.seaman@yahoo.com",
    "thetoadboy@yahoo.com",
    "seaman_duane@yahoo.com",
]

# Strict Exclusion Filter
EXCLUDED_ACCOUNTS = [
    "ericdcman@gmail.com",
    "eric.d.seaman@outlook.com",
    "beta@numista.ai",
]

CSV_HEADER = [
    "priority_tier",
    "user_account",
    "collection_type",
    "doc_id",
    "canonical_doc_id",
    "is_duplicate_record",
    "missing_sides",
    "year",
    "mint_mark",
    "denomination",
    "program_series",
    "theme_subject",
    "variety_error",
    "strike_type",
    "metal_content",
    "condition_grade",
    "grading_service",
    "cert_number",
    "retailer",
    "retailer_item_no",
    "retailer_invoice_no",
    "purchase_date",
    "purchase_cost",
    "personal_notes",
    "existing_obverse_url",
    "existing_reverse_url",
    "naming_key",
    "sourcing_status",
    "source_attribution",
    "image_credit",
    "last_checked_date",
    "attempt_log",
    "direct_search_query",
    "is_foreign",
]

# Setup Logging
os.makedirs("output", exist_ok=True)
log_file = "output/generate_missing_images_audit.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


def init_firestore():
    if not firebase_admin._apps:
        # Search standard locations for serviceAccountKey
        key_paths = [
            "serviceAccountKey.json",
            "numista_backend/serviceAccountKey.json",
            "../serviceAccountKey.json",
        ]
        cred_path = None
        for p in key_paths:
            if os.path.exists(p):
                cred_path = p
                break
        if cred_path:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    return firestore.client()


def slugify(text: str) -> str:
    if not text:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def is_offline_valid_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    u = url.strip()
    if not u or u.startswith("gs://") or not (u.startswith("http://") or u.startswith("https://")):
        return False
    return True


def live_check_url(url: str) -> bool:
    if not is_offline_valid_url(url):
        return False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Numista-SoR-Audit-Engine/4.0"},
            method="HEAD",
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            return resp.status >= 200 and resp.status < 400
    except Exception:
        return False


def determine_priority(doc_dict: dict, missing_sides: str, is_currency: bool) -> str:
    variety = str(doc_dict.get("Variety") or doc_dict.get("variety") or "").lower()
    theme = str(doc_dict.get("Theme/Subject") or doc_dict.get("theme") or "").lower()
    series = str(doc_dict.get("Program/Series") or doc_dict.get("series") or "").lower()
    metal = str(doc_dict.get("Metal Content") or doc_dict.get("metal") or "").lower()
    denom = str(doc_dict.get("Denomination") or doc_dict.get("denomination") or "").lower()
    
    text = f"{variety} {theme} {series} {denom}"

    # P1A: Errors, die varieties, doubled dies, RPMs, overdates
    error_keywords = ["error", "doubled die", "ddo", "ddr", "rpm", "overdate", "clipped", "off-center", "die variety", "var."]
    if any(k in variety for k in error_keywords) or "error" in text:
        return "P1A_ERRORS_AND_VARIETIES"

    # P1B: Rare Currency (Obsolete, CSA, Continental, Fractional, Gold/Silver certs)
    if is_currency or "bank note" in text or "certificate" in text or "continental" in text or "obsolete" in text or "csa" in text:
        return "P1B_RARE_CURRENCY"

    # P1C: Gold Bullion or Missing Both
    if "gold" in metal or "gold" in text or missing_sides == "MISSING_BOTH":
        return "P1C_HIGH_VALUE_OR_BOTH"

    # P2: Obverse Missing
    if missing_sides == "MISSING_OBVERSE":
        return "P2_OBVERSE_MISSING"

    # P3: Reverse Missing
    return "P3_REVERSE_MISSING"


def generate_naming_key(year, country, denom, series, side, doc_id):
    y_slug = slugify(str(year)) if year else "unknown"
    c_slug = slugify(country) if country else "us"
    d_slug = slugify(denom) if denom else "item"
    s_slug = slugify(series) if series else "specimen"
    side_slug = "obverse" if "obv" in side.lower() else "reverse"

    key = f"{y_slug}_{c_slug}_{d_slug}_{s_slug}_{side_slug}.png"
    # Ensure regex compliance ^[a-z0-9\-_]+\.png$
    clean_key = re.sub(r"[^a-z0-9\-_]", "-", key[:-4]) + ".png"
    clean_key = re.sub(r"-+", "-", clean_key)
    
    if len(clean_key) > 100 or clean_key.startswith("unknown_"):
        clean_key = f"unknown_{doc_id[:8]}_{side_slug}.png"
    return clean_key


def generate_search_query(year, country, denom, series, theme, variety):
    parts = []
    if year:
        parts.append(str(year))
    if country and country != "United States":
        parts.append(country)
    if denom:
        parts.append(str(denom))
    if series and series != "Unmapped" and series != "USA Invoice Import":
        parts.append(str(series))
    if theme and theme != "Unmapped":
        parts.append(str(theme))
    if variety and variety != "Standard Strike":
        parts.append(str(variety))
    
    raw_query = " ".join(parts) if parts else "US Coin"
    encoded = urllib.parse.quote_plus(raw_query)
    return f"https://www.google.com/search?tbm=isch&q={encoded}"


def run_audit(dry_run=False, live_validate=False, redact_pii=False, output_path="output/missing_images_sourcing_master.csv"):
    logging.info(f"=== Starting Numista.AI Missing Image Audit (Schema {SCHEMA_VERSION}) ===")
    logging.info(f"Execution Mode: {'DRY RUN' if dry_run else 'PRODUCTION GENERATION'}")
    logging.info(f"Live Validation: {live_validate} | Redact PII: {redact_pii}")
    logging.info(f"Target Accounts: {PRODUCTION_ACCOUNTS}")

    db = init_firestore()
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    rows = []
    seen_hashes = {}  # hash -> canonical_doc_id

    total_scanned = 0
    total_deficiencies = 0

    for email in PRODUCTION_ACCOUNTS:
        logging.info(f"Auditing account: {email}")

        # Scan both coins and currency subcollections
        for col_name in ["coins", "currency"]:
            col_ref = db.collection("users").document(email).collection(col_name)
            docs = list(col_ref.stream())
            logging.info(f"  - users/{email}/{col_name}: {len(docs)} documents")

            for doc in docs:
                total_scanned += 1
                d = doc.to_dict()
                doc_id = doc.id

                # Evaluate obverse & reverse
                obv_raw = d.get("image_url_obverse") or d.get("obverse_image_url") or ""
                rev_raw = d.get("image_url_reverse") or d.get("reverse_image_url") or ""

                if live_validate:
                    obv_ok = live_check_url(obv_raw)
                    rev_ok = live_check_url(rev_raw)
                else:
                    obv_ok = is_offline_valid_url(obv_raw)
                    rev_ok = is_offline_valid_url(rev_raw)

                # Skip if both images are valid
                if obv_ok and rev_ok:
                    continue

                total_deficiencies += 1

                if not obv_ok and not rev_ok:
                    missing_sides = "MISSING_BOTH"
                elif not obv_ok:
                    missing_sides = "MISSING_OBVERSE"
                else:
                    missing_sides = "MISSING_REVERSE"

                # Extract normalized metadata
                year = d.get("Year") or d.get("year") or ""
                mint = d.get("Mint Mark") or d.get("mint_mark") or ""
                denom = d.get("Denomination") or d.get("denomination") or ""
                series = d.get("Program/Series") or d.get("program_series") or d.get("Series") or ""
                theme = d.get("Theme/Subject") or d.get("theme_subject") or d.get("Theme") or ""
                variety = d.get("Variety") or d.get("variety") or ""
                strike = d.get("Strike Type") or d.get("strike_type") or "Standard"
                metal = d.get("Metal Content") or d.get("metal_content") or ""
                grade = d.get("Condition") or d.get("condition_grade") or d.get("Grade") or ""
                service = d.get("Grading Service") or d.get("grading_service") or ""
                cert = d.get("Certification Number") or d.get("cert_number") or ""
                retailer = d.get("Retailer") or d.get("retailer") or ""
                item_no = d.get("Retailer Item Number") or d.get("retailer_item_no") or d.get("Item No") or ""
                inv_no = d.get("Retailer Invoice Number") or d.get("retailer_invoice_no") or d.get("Invoice No") or ""
                p_date = d.get("Purchase Date") or d.get("purchase_date") or ""
                cost = str(d.get("Cost") or d.get("purchase_cost") or "")
                notes = d.get("Personal Notes") or d.get("personal_notes") or d.get("Notes") or ""
                country = d.get("Country") or d.get("country") or "United States"

                is_foreign = (country.strip().lower() != "united states")
                is_currency = (col_name == "currency") or ("note" in denom.lower()) or ("certificate" in denom.lower())

                # Deduplication logic
                is_duplicate = False
                canonical_id = doc_id
                
                # Check for explicit cert deduplication first
                if cert and service:
                    dedup_key = f"{service}_{cert}".lower()
                elif year and denom and (variety or theme):
                    dedup_key = f"{year}_{mint}_{denom}_{series}_{theme}_{variety}".lower()
                else:
                    dedup_key = None  # Sparse records exempted from auto-collapsing

                if dedup_key:
                    h = hashlib.sha256(dedup_key.encode("utf-8")).hexdigest()[:16]
                    if h in seen_hashes:
                        is_duplicate = True
                        canonical_id = seen_hashes[h]
                    else:
                        seen_hashes[h] = doc_id

                priority = determine_priority(d, missing_sides, is_currency)
                naming_key = generate_naming_key(year, country, denom, series or theme, missing_sides, doc_id)
                search_query = generate_search_query(year, country, denom, series, theme, variety)

                # Attempt log structured as compact JSON array
                attempt_list = [
                    {
                        "timestamp": now_utc,
                        "action": "AUDIT_EXTRACTION",
                        "source": "FIRESTORE_SOR",
                        "result": missing_sides,
                    }
                ]
                attempt_json = json.dumps(attempt_list, separators=(",", ":"))

                # PII Redaction
                if redact_pii:
                    out_cost = "[REDACTED]"
                    out_inv_no = "[REDACTED]"
                    out_notes = "[REDACTED]"
                else:
                    out_cost = cost
                    out_inv_no = str(inv_no)
                    out_notes = str(notes).replace("\n", " ").replace("\r", "")

                row = {
                    "priority_tier": priority,
                    "user_account": email,
                    "collection_type": col_name,
                    "doc_id": doc_id,
                    "canonical_doc_id": canonical_id,
                    "is_duplicate_record": is_duplicate,
                    "missing_sides": missing_sides,
                    "year": str(year),
                    "mint_mark": str(mint),
                    "denomination": str(denom),
                    "program_series": str(series),
                    "theme_subject": str(theme),
                    "variety_error": str(variety),
                    "strike_type": str(strike),
                    "metal_content": str(metal),
                    "condition_grade": str(grade),
                    "grading_service": str(service),
                    "cert_number": str(cert),
                    "retailer": str(retailer),
                    "retailer_item_no": str(item_no),
                    "retailer_invoice_no": out_inv_no,
                    "purchase_date": str(p_date),
                    "purchase_cost": out_cost,
                    "personal_notes": out_notes,
                    "existing_obverse_url": obv_raw,
                    "existing_reverse_url": rev_raw,
                    "naming_key": naming_key,
                    "sourcing_status": "PENDING_SOURCING",
                    "source_attribution": "Numista Sourcing Pipeline",
                    "image_credit": "Pending Reference Acquisition",
                    "last_checked_date": now_utc,
                    "attempt_log": attempt_json,
                    "direct_search_query": search_query,
                    "is_foreign": is_foreign,
                }
                rows.append(row)

    # Sort rows by priority tier hierarchy
    tier_order = {
        "P1A_ERRORS_AND_VARIETIES": 1,
        "P1B_RARE_CURRENCY": 2,
        "P1C_HIGH_VALUE_OR_BOTH": 3,
        "P2_OBVERSE_MISSING": 4,
        "P3_REVERSE_MISSING": 5,
    }
    rows.sort(key=lambda r: (tier_order.get(r["priority_tier"], 99), r["year"] or "0", r["doc_id"]))

    logging.info(f"Audit Complete: Scanned {total_scanned} total items across 4 production accounts.")
    logging.info(f"Found {len(rows)} deficiency rows to export.")

    if not dry_run:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        logging.info(f"Successfully generated master CSV at: {output_path}")

        # Also write timestamped snapshot
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snap_path = f"output/missing_images_sourcing_{ts}.csv"
        with open(snap_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        logging.info(f"Saved reproducible timestamped snapshot at: {snap_path}")

    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Numista.AI Missing Image Sourcing Tracker")
    parser.add_argument("--dry-run", action="store_true", help="Run audit and schema validation without writing file")
    parser.add_argument("--live-validate", action="store_true", help="Perform live HTTP HEAD checks on existing URLs")
    parser.add_argument("--redact-pii", action="store_true", help="Redact confidential PII fields for external catalogers")
    parser.add_argument("--output", default="output/missing_images_sourcing_master.csv", help="Output file path")
    args = parser.parse_args()

    run_audit(
        dry_run=args.dry_run,
        live_validate=args.live_validate,
        redact_pii=args.redact_pii,
        output_path=args.output,
    )
