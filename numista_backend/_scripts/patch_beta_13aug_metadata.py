import os
import sys
import json
import argparse
import urllib.request
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# Determine service account key path
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
key_path = backend_dir / "serviceAccountKey.json.json"
if not key_path.exists():
    key_path = backend_dir / "serviceAccountKey.json"

if not firebase_admin._apps:
    print(f"[patch_beta_13aug] Initializing Firebase Admin with key: {key_path}", flush=True)
    cred = credentials.Certificate(str(key_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

US_ALLOW_LIST = {
    "united states", "usa", "us", "united states of america", "u.s.", "u.s.a.",
    "united states mint", "puerto rico", "guam", "u.s. virgin islands", "usvi",
    "american samoa", "northern mariana islands", "confederate states", "csa", "us philippines"
}

IMAGE_URLS_TO_VALIDATE = [
    "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/1932-george-washington-quarter-obverse.jpg",
    "https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg"
]

def preflight_validate_image_urls():
    print("[patch_beta_13aug] Running pre-flight image URL existence check (HTTP HEAD)...", flush=True)
    valid_all = True
    for url in IMAGE_URLS_TO_VALIDATE:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print(f"  [OK 200] {url}", flush=True)
                else:
                    print(f"  [WARN {response.status}] {url}", flush=True)
                    valid_all = False
        except Exception as e:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    print(f"  [OK GET {response.status}] {url}", flush=True)
            except Exception as ex:
                print(f"  [FAIL URL Check] {url} -> {ex}", flush=True)
                valid_all = False
    return valid_all

def backup_user_collections(output_file):
    print(f"[patch_beta_13aug] Generating JSON backup snapshot at: {output_file}", flush=True)
    snapshot = []
    users = list(db.collection("users").stream())
    for user_doc in users:
        uid = user_doc.id
        for subcoll in ["coins"]:
            docs = list(db.collection("users").document(uid).collection(subcoll).stream())
            for d in docs:
                snapshot.append({
                    "uid": uid,
                    "collection": subcoll,
                    "doc_id": d.id,
                    "data": d.to_dict()
                })
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)
    print(f"[patch_beta_13aug] Backup complete. Total items backed up: {len(snapshot)}", flush=True)

def sanitize_mint_mark(val):
    if not val:
        return ""
    clean = str(val).strip()
    if clean.lower() in ["none", "no mint mark", "null", "n/a"]:
        return ""
    return clean

def patch_beta_remediation(dry_run=True):
    mode_str = "DRY-RUN MODE (No DB writes)" if dry_run else "LIVE MODE (Executing Firestore set with merge=True)"
    print(f"\n========================================================", flush=True)
    print(f"[patch_beta_13aug] Starting remediation — {mode_str}", flush=True)
    print(f"========================================================\n", flush=True)

    # Use list_documents() to include stub/phantom user docs (like eric.seaman@yahoo.com)
    user_docs = list(db.collection("users").list_documents())
    total_scanned = 0
    total_patched = 0

    for user_ref in user_docs:
        uid = user_ref.id
        coins_ref = db.collection("users").document(uid).collection("coins")
        coin_docs = list(coins_ref.stream())

        if not coin_docs:
            continue

        print(f"Processing User '{uid}' (coins count: {len(coin_docs)})", flush=True)

        for doc in coin_docs:
            total_scanned += 1
            doc_id = doc.id
            data = doc.to_dict() or {}
            
            c_val = data.get("country") if data.get("country") is not None else data.get("Country")
            raw_country = str(c_val or "").strip()
            if raw_country.lower() in ["none", "null", "n/a"]:
                raw_country = ""

            raw_is_foreign = data.get("is_foreign")

            d_val = data.get("denomination") if data.get("denomination") is not None else data.get("Denomination")
            raw_denom = str(d_val or "").strip()
            if raw_denom.lower() in ["none", "null", "n/a"]:
                raw_denom = ""

            y_val = data.get("year") if data.get("year") is not None else data.get("Year")
            raw_year = str(y_val or "").strip()

            m_val = data.get("mint_mark") if data.get("mint_mark") is not None else data.get("Mint Mark")
            raw_mint = str(m_val or "").strip()

            p_val = data.get("program_series") if data.get("program_series") is not None else data.get("Program/Series")
            raw_program = str(p_val or "").strip()

            t_val = data.get("theme_subject") if data.get("theme_subject") is not None else data.get("Theme/Subject")
            raw_theme = str(t_val or "").strip()

            v_val = data.get("variety_error") if data.get("variety_error") is not None else (data.get("Variety/Error") if data.get("Variety/Error") is not None else data.get("Variety"))
            raw_variety = str(v_val or "").strip()

            raw_cost = data.get("purchase_cost") if data.get("purchase_cost") is not None else (data.get("Purchase Cost") if data.get("Purchase Cost") is not None else data.get("Cost"))

            updates = {}

            # ── Predicate 1: US Coin Country & is_foreign Normalization ────────
            country_lower = raw_country.lower()
            is_us_denom = raw_denom in [
                "Quarter Dollar", "Quarter", "Dime", "One Cent", "Cent", "Penny", 
                "Lincoln Cent", "Jefferson Nickel", "Half Dollar", "Dollar", "Five Dollars (Half Eagle)",
                "Half Eagle", "Eagle", "Double Eagle", "Silver Eagle", "Gold Eagle"
            ]
            is_us_coin = (country_lower in US_ALLOW_LIST) or (raw_country == "" and is_us_denom)
            
            if is_us_coin:
                if raw_country != "United States":
                    updates["country"] = "United States"
                    updates["Country"] = "United States"
                if raw_is_foreign is not False:
                    updates["is_foreign"] = False

            # ── Predicate 2: 2019-W San Antonio Quarter Realignment ────────────
            is_san_antonio = (
                ("san antonio" in raw_theme.lower() or "san antonio" in raw_variety.lower()) or
                (raw_year == "2019" and raw_mint.upper() == "W" and ("Quarter" in raw_denom or "2019 Quarter" in raw_theme))
            )
            if is_san_antonio:
                if raw_program != "America the Beautiful Quarters":
                    updates["program_series"] = "America the Beautiful Quarters"
                    updates["Program/Series"] = "America the Beautiful Quarters"
                if raw_theme != "San Antonio Missions":
                    updates["theme_subject"] = "San Antonio Missions"
                    updates["Theme/Subject"] = "San Antonio Missions"
                if raw_variety != "":
                    updates["variety_error"] = ""
                    updates["Variety/Error"] = ""
                    updates["Variety"] = ""
                if raw_mint.upper() != "W":
                    updates["mint_mark"] = "W"
                    updates["Mint Mark"] = "W"
                updates["country"] = "United States"
                updates["Country"] = "United States"
                updates["is_foreign"] = False
                updates["obverse_image_url"] = IMAGE_URLS_TO_VALIDATE[0]
                updates["reverse_image_url"] = IMAGE_URLS_TO_VALIDATE[1]
                updates["image_url_obverse"] = IMAGE_URLS_TO_VALIDATE[0]
                updates["image_url_reverse"] = IMAGE_URLS_TO_VALIDATE[1]

            # ── Predicate 3: Kuwait 50 Fils Metadata Clean-up ──────────────────
            is_kuwait = (country_lower == "kuwait" or "kuwait" in raw_program.lower() or raw_denom == "50 Fils")
            if is_kuwait:
                if raw_program != "":
                    updates["program_series"] = ""
                    updates["Program/Series"] = ""
                if raw_theme != "":
                    updates["theme_subject"] = ""
                    updates["Theme/Subject"] = ""
                if raw_variety.lower() in ["none", "null"]:
                    updates["variety_error"] = ""
                    updates["Variety/Error"] = ""
                    updates["Variety"] = ""
                if raw_is_foreign is not True:
                    updates["is_foreign"] = True
                raw_ai_val = str(data.get("AI Estimated Value") or data.get("ai_estimated_value") or "").strip()
                if raw_ai_val == "15.00-25.00":
                    updates["AI Estimated Value"] = "$15.00 - $25.00"
                    updates["ai_estimated_value"] = "$15.00 - $25.00"

            # ── Predicate 4: Mint Mark Sanitization ("None" -> "") ─────────────
            clean_mint = sanitize_mint_mark(raw_mint)
            if clean_mint != raw_mint:
                updates["mint_mark"] = clean_mint
                updates["Mint Mark"] = clean_mint

            # ── Predicate 5: Purchase Cost Normalization (preserve $0.00) ──────
            if raw_cost in [0, 0.0, "0", "0.00", "$0", "$0.00"]:
                if raw_cost != "$0.00":
                    updates["purchase_cost"] = "$0.00"
                    updates["Purchase Cost"] = "$0.00"
                    updates["Cost"] = "$0.00"

            if updates:
                total_patched += 1
                print(f"  [MATCH] Doc ID: {doc_id} | Year: {raw_year} | Denom: {raw_denom} | Mint: {raw_mint}", flush=True)
                print(f"          Mutations: {updates}", flush=True)
                if not dry_run:
                    coins_ref.document(doc_id).set(updates, merge=True)
                    print(f"          -> WRITTEN (merge=True)", flush=True)

    print(f"\n[patch_beta_13aug] Complete. Scanned: {total_scanned} | Patched: {total_patched}\n", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Beta 13 AUG 2026 Database Remediation Script")
    parser.add_argument("--live", action="store_true", help="Execute live writes to Firestore (default is dry-run)")
    args = parser.parse_args()

    dry_run = not args.live

    valid = preflight_validate_image_urls()
    if not valid and not dry_run:
        print("[patch_beta_13aug] ERROR: Pre-flight image URL check failed! Aborting live write.", flush=True)
        sys.exit(1)

    backup_path = script_dir / "backup_coins_13aug2026.json"
    backup_user_collections(backup_path)

    patch_beta_remediation(dry_run=dry_run)

if __name__ == "__main__":
    main()
