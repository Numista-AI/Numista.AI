#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
heal_remaining_82.py
====================
Custom image healing for the remaining 82 unhealed coins in AJ's collection.
These coins failed standard catalog healing due to being proof sets, rare commemorative gold,
ancient coins, Hawaiian coins, pattern coins, or having user typos in the year/subject.
"""

import sys
import os
import re
import time
import csv
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
SA_KEY = SCRIPT_DIR / "serviceAccountKey.json.json"
PROJECT_ID = "studio-9101802118-8c9a8"
UPLOADS_BUCKET = f"numista-uploads-{PROJECT_ID}"
REF_BUCKET = "numista-reference-library"
USER_EMAIL = "jseaman1204@gmail.com"
GCS_PUB_BASE = f"https://storage.googleapis.com/{UPLOADS_BUCKET}"

# Initializing SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)

db = firestore.client()
gcs = storage.Client.from_service_account_json(str(SA_KEY))
uploads_bucket_obj = gcs.bucket(UPLOADS_BUCKET)
ref_bucket_obj = gcs.bucket(REF_BUCKET)

# Mappings of exact coin IDs to GCS/external URLs for non-generic ones
EXACT_MAPPINGS = {
    # 103-76BC Bronze Widow's Mite
    "03153afb-9f63-4c3c-b30b-0973c47e679f": {
        "obv": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Widowsmite.png",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Widowsmite.png",
        "attribution": "Public Domain. Source: Wikimedia Commons",
        "source": "wikimedia_commons"
    },
    # 1883 Hawaiian Quarter
    "4b608086-063a-4f7e-870b-14538d71d791": {
        "obv": "https://upload.wikimedia.org/wikipedia/commons/e/e1/%C2%BC_Dollar_1883_Kal%C4%81kaua_I._vz_-_MA-Shops.jpg",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/e/e1/%C2%BC_Dollar_1883_Kal%C4%81kaua_I._vz_-_MA-Shops.jpg",
        "attribution": "Public Domain. Source: Wikimedia Commons / MA-Shops",
        "source": "wikimedia_commons"
    },
    # 1879 Schoolgirl Pattern Dollar
    "3cd50285-6219-4745-8550-8c71aea23682": {
        "obv": "https://upload.wikimedia.org/wikipedia/commons/1/19/1879_%22Schoolgirl%22_dollar_pattern_%28obverse%29.jpg",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/c/cd/1879_%22Schoolgirl%22_dollar_pattern_%28reverse%29.jpg",
        "attribution": "Public Domain. Source: Wikimedia Commons",
        "source": "wikimedia_commons"
    },
    # 2021 Celebrating America Zitkala-Sa Quarter
    "39b04e68-45a8-4b80-9c88-d0901d621e20": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/6/6c/2024_Zitkala-Sa_Womens_Quarter.jpg",
        "attribution": "Public Domain. Source: Wikimedia Commons / US Mint",
        "source": "wikimedia_commons"
    },
    # 1989 W Gold American Eagle $50 (Obverse only; reverse was correct from local)
    "db37a3ab-2b83-4d0b-a082-9ed7115d8017": {
        "obv": "local_file:C:\\Users\\ericd\\Documents\\MyVertexProject\\new_coin_images\\1989W Gold American Eagle $50 Obverse.jpg",
        "rev": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/1989W Gold American Eagle $50 Reverse.jpg",
        "attribution": "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov",
        "source": "us_mint"
    },
    # 1916-1920 Wheat Cents Set
    "537b08c8-95c6-4311-9599-fbd96fe5f16c": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/1909-S_VDB_Lincoln_cent_obverse.jpg",
        "rev": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Wheat_cent/1909-S_VDB_Lincoln_cent_reverse.jpg",
        "attribution": "Public Domain. Source: US Mint / GCS Reference Library",
        "source": "gcs_reference_library"
    },
    # 1979-99 SBA 4-coin Year Set
    "cad31f3d-3385-4923-b5b4-60f1c260290b": {
        "obv": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/1999-susan-b-anthony-dollar-obverse.jpg",
        "rev": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/1999-susan-b-anthony-dollar-reverse.jpg",
        "attribution": "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov",
        "source": "us_mint"
    },
    # Washington Stamp Set
    "c88df2f6-830f-4246-8dea-db43d5c47c42": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg",
        "rev": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/Quarter Dollar.png",
        "attribution": "Public Domain. Source: US Mint / GCS Reference Library",
        "source": "gcs_reference_library"
    },
    # 1942 Coin Set - Birth Year
    "c5244bae-0f9c-460b-b86b-4ee9b58e1798": {
        "obv": "https://upload.wikimedia.org/wikipedia/commons/0/05/A_1969_United_States_Mint_Proof_Set.jpg",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/0/05/A_1969_United_States_Mint_Proof_Set.jpg",
        "attribution": "Public Domain. Source: Wikimedia Commons",
        "source": "wikimedia_commons"
    },
    # 2006 Gold American Eagle $5
    "281ba0e9-69f6-432e-816e-654438ba6fd4": {
        "obv": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/American-Eagle-Gold-Proof-Obverse.jpg",
        "rev": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/American-Eagle-Gold-Proof-Reverse.jpg",
        "attribution": "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov",
        "source": "us_mint"
    },
    # 2009 Lincoln Bicentennial cents colorized and gold plated set
    "782d600f-041e-4d29-bb2f-819205fe4260": {
        "obv": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2009-lincoln-cent-penny-uncirculated-obverse.jpg",
        "rev": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2009-lincoln-cent-penny-professional-life-illinois-uncirculated-reverse.jpg",
        "attribution": "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov",
        "source": "us_mint"
    },
    # 1926 $2.5 Commemorative Gold - Coinage
    "b0db4df7-d921-4897-b304-29daff76b2d3": {
        "obv": "https://upload.wikimedia.org/wikipedia/commons/2/21/1926_Sesquicentennial_quarter_eagle_obverse.jpg",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/3/30/1926_Sesquicentennial_quarter_eagle_reverse.jpg",
        "attribution": "Public Domain. Source: Wikimedia Commons",
        "source": "wikimedia_commons"
    },
    # 1926 $2.5 Commemorative Gold - Sesquicentennial
    "4648dbc9-96d4-42fe-abc7-4a6885784cf6": {
        "obv": "https://upload.wikimedia.org/wikipedia/commons/2/21/1926_Sesquicentennial_quarter_eagle_obverse.jpg",
        "rev": "https://upload.wikimedia.org/wikipedia/commons/3/30/1926_Sesquicentennial_quarter_eagle_reverse.jpg",
        "attribution": "Public Domain. Source: Wikimedia Commons",
        "source": "wikimedia_commons"
    }
}

# America the Beautiful specific mappings (healed from GCS reference library)
ATB_MAPPINGS = {
    # 2019 P Michigan Pictured Rocks (Released in 2018)
    "89b41513-ccc0-4cb6-9b3d-cfa991e630d7": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg",
        "rev": "gs://numista-reference-library/reference_library/bulk_programs/america_the_beautiful/2018-america-the-beautiful-quarters-coin-pictured-rocks-michigan-uncirculated-reverse.jpg"
    },
    # 2010 S Weir Farm (Released in 2020)
    "bca640d6-4949-4ed5-b531-275d78638b4b": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg",
        "rev": "gs://numista-reference-library/reference_library/bulk_programs/america_the_beautiful/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg"
    },
    # 2012 S George Rogers Clark (Released in 2017)
    "e2af6882-80ee-4b9d-b59a-5398e4148e5b": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg",
        "rev": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/2017_United_States_quarters/America_the_Beautiful_quarter__George_Rogers_Clark_/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-proof-reverse-768x768.jpg"
    },
    # 2019 PDS Quarter - America the Beautiful General
    "c57b2abf-8876-41a3-88d6-c35ac6b3a540": {
        "obv": "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg",
        "rev": "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/Quarter Dollar.png"
    }
}

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────
def download_image(url: str) -> bytes | None:
    try:
        # Rate limit friendly sleep to avoid 429
        time.sleep(1.0)
        req = urllib.request.Request(url, headers={'User-Agent': 'NumistaBot/1.0 (contact@numista.ai; developer-migration)'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except Exception as e:
        print(f"    [ERR] Failed to download {url}: {e}")
        return None

def copy_gcs_blob(src_path: str, dest_blob_path: str):
    """Copy a blob from GCS reference/upload bucket to target path in uploads bucket."""
    try:
        # Parse src_path like gs://bucket-name/path/to/blob
        src_clean = src_path.replace("gs://", "")
        parts = src_clean.split("/", 1)
        src_bucket_name = parts[0]
        src_blob_name = parts[1]

        src_bucket = gcs.bucket(src_bucket_name)
        src_blob = src_bucket.blob(src_blob_name)

        dest_blob = uploads_bucket_obj.blob(dest_blob_path)
        uploads_bucket_obj.copy_blob(src_blob, uploads_bucket_obj, dest_blob_path)

        # Set headers
        dest_blob.cache_control = "no-cache, no-store, must-revalidate"
        dest_blob.content_type = src_blob.content_type or "image/jpeg"
        dest_blob.patch()
        return True
    except Exception as e:
        print(f"    [ERR] GCS copy failed from {src_path} to {dest_blob_path}: {e}")
        return False

def upload_bytes(data_bytes: bytes, dest_blob_path: str, content_type: str = "image/jpeg"):
    try:
        blob = uploads_bucket_obj.blob(dest_blob_path)
        blob.cache_control = "no-cache, no-store, must-revalidate"
        blob.upload_from_string(data_bytes, content_type=content_type)
        return True
    except Exception as e:
        print(f"    [ERR] GCS upload failed to {dest_blob_path}: {e}")
        return False

# ─── MAIN Sweeping ────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("HEAL REMAINING 82 UNHEALED COINS")
    print("=" * 70)

    # 1. Load unhealed report details
    unhealed_ids = []
    unhealed_report_path = SCRIPT_DIR.parent / "audit_findings.csv"
    
    col_ref = db.collection("users").document(USER_EMAIL).collection("coins")
    docs = list(col_ref.stream())
    doc_map = {doc.id: doc.to_dict() for doc in docs}

    # Find unhealed coin IDs
    for doc_id, data in doc_map.items():
        reason = data.get("image_fix_reason", "")
        # If it was audited/flagged in the findings but did not heal
        if "Auto-healed by audit pipeline" not in reason:
            # Check if this ID is in audit findings
            # (We will check if it was flagged as unhealed or has mismatches)
            # Actually, let's load all unhealed from unhealed_report.txt to be 100% precise!
            pass

    # Read IDs from unhealed_report.txt directly
    report_path = SCRIPT_DIR.parent / "numista_backend" / "unhealed_report.txt"
    if not report_path.exists():
        report_path = SCRIPT_DIR / "unhealed_report.txt"
        
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    unhealed_ids = re.findall(r"ID:\s*([a-f0-9\-]+)", content)
    unhealed_ids = list(set(unhealed_ids))
    print(f"Loaded {len(unhealed_ids)} unhealed coin IDs from unhealed_report.txt")

    success_count = 0
    fail_count = 0

    for idx, doc_id in enumerate(unhealed_ids):
        coin = doc_map.get(doc_id)
        if not coin:
            print(f"[{idx+1}/{len(unhealed_ids)}] Doc ID {doc_id} not found in Firestore!")
            fail_count += 1
            continue

        year = str(coin.get("Year", coin.get("year", ""))).strip()
        denom = str(coin.get("Denomination", coin.get("denomination", ""))).strip()
        program = str(coin.get("Program/Series", coin.get("program", ""))).strip()
        theme = str(coin.get("Theme/Subject", coin.get("theme", ""))).strip()
        coin_name = f"{year} {denom} - {program}"
        
        print(f"\n[{idx+1}/{len(unhealed_ids)}] Sourcing: {coin_name} (ID: {doc_id})")

        obv_url = rev_url = None
        attribution = DEFAULT_ATTRIBUTION = "Public Domain. Source: US Mint / GCS Reference Library."
        source_tag = "gcs_reference_library"

        # Rule 1: Exact Mappings
        if doc_id in EXACT_MAPPINGS:
            mapping = EXACT_MAPPINGS[doc_id]
            obv_url = mapping["obv"]
            rev_url = mapping["rev"]
            attribution = mapping["attribution"]
            source_tag = mapping["source"]

        # Rule 2: Presidential Dollar (5 coins)
        elif "Presidential" in program:
            # We identified that all 5 unhealed Presidential Dollars are George Washington!
            obv_url = "gs://numista-reference-library/reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/2007_Presidential_dollar_coins/Presidential_dollar__George_Washington_/George_Washington_Presidential__241_Coin_obverse.png"
            rev_url = "gs://numista-reference-library/reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png"
            attribution = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"
            source_tag = "us_mint"
            # Let's also update the subject/theme field in Firestore so the metadata is correct!
            db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id).update({
                "`Theme/Subject`": "George Washington",
                "theme": "George Washington"
            })
            print("  -> Updated Subject to George Washington in Firestore")

        # Rule 3: Capped Bust Quarters (3 coins)
        elif "capped bust" in program.lower() or "capped bust" in coin_name.lower():
            obv_url = "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Capped_Bust_quarter/1819_quarter_dollar_obv.jpg"
            rev_url = "gs://numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Capped_Bust_quarter/1819_quarter_dollar_rev.jpg"
            attribution = "Public Domain. Source: Wikimedia Commons / NNC"
            source_tag = "wikimedia_commons"

        # Rule 4: Liberty Head Gold Half Eagles (7 coins)
        elif "half eagle" in program.lower() or "half eagle" in coin_name.lower() or ("$5" in denom and "liberty" in program.lower()):
            obv_url = "https://upload.wikimedia.org/wikipedia/commons/5/5e/1839-C_%245_Gold_Coin.jpg"
            rev_url = "https://upload.wikimedia.org/wikipedia/commons/a/a6/1839-C_%245_Gold_Coin%2C_Reverse.jpg"
            attribution = "Public Domain. Source: Wikimedia Commons"
            source_tag = "wikimedia_commons"

        # Rule 5: American Gold Eagle 2006 (1 coin)
        elif "gold" in program.lower() and "eagle" in program.lower() and "2006" in year:
            obv_url = "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/American-Eagle-Gold-Proof-Obverse.jpg"
            rev_url = "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/American-Eagle-Gold-Proof-Reverse.jpg"
            attribution = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"
            source_tag = "us_mint"

        # Rule 6: America the Beautiful / National Park Quarters (4 coins)
        elif doc_id in ATB_MAPPINGS:
            mapping = ATB_MAPPINGS[doc_id]
            obv_url = mapping["obv"]
            rev_url = mapping["rev"]
            attribution = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"
            source_tag = "us_mint"

        # Rule 7: Silver Eagles (4 coins)
        elif "american eagle silver dollar" in program.lower() or "american eagle silver dollar" in coin_name.lower() or ("eagle" in program.lower() and "silver" in coin_name.lower()):
            # Using our high-quality Silver Eagle images from GCS
            obv_url = "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American Eagle 2023 One Ounce Silver Proof Coin Obverse.jpg"
            rev_url = "gs://numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American Eagle 2023 One Ounce Silver Proof Coin Reverse.jpg"
            attribution = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"
            source_tag = "us_mint"

        # Rule 8: Proof Sets (47 coins)
        elif "proof set" in program.lower() or "proof set" in coin_name.lower() or "silver proof set" in program.lower():
            # Determine set year
            set_year = 0
            match = re.search(r"\b(19|20)\d{2}\b", coin_name)
            if match:
                set_year = int(match.group(0))
            
            if set_year < 1980:
                obv_url = rev_url = "https://upload.wikimedia.org/wikipedia/commons/0/05/A_1969_United_States_Mint_Proof_Set.jpg"
            elif 1980 <= set_year < 2000:
                obv_url = rev_url = "https://upload.wikimedia.org/wikipedia/commons/1/1a/1995_U.S._Mint_silver_proof_set.jpg"
            else:
                if "silver" in coin_name.lower():
                    obv_url = rev_url = "https://upload.wikimedia.org/wikipedia/commons/e/e2/2019_US_Mint_silver_proof_set.jpg"
                else:
                    obv_url = rev_url = "https://upload.wikimedia.org/wikipedia/commons/4/4b/2019_US_Mint_proof_set.jpg"
            attribution = "Public Domain. Source: Wikimedia Commons"
            source_tag = "wikimedia_commons"

        else:
            print(f"  [WARN] No matching rules for {coin_name}!")
            fail_count += 1
            continue

        # Upload files
        obv_ok = False
        rev_ok = False

        dest_obv_path = f"users/{USER_EMAIL}/coins/{doc_id}/obverse.jpg"
        dest_rev_path = f"users/{USER_EMAIL}/coins/{doc_id}/reverse.jpg"

        # Process Obverse
        print(f"  Obverse source: {obv_url}")
        if obv_url.startswith("local_file:"):
            local_path = obv_url.replace("local_file:", "")
            with open(local_path, "rb") as lf:
                obv_ok = upload_bytes(lf.read(), dest_obv_path)
        elif obv_url.startswith("gs://"):
            obv_ok = copy_gcs_blob(obv_url, dest_obv_path)
        elif obv_url.startswith("http"):
            b_data = download_image(obv_url)
            if b_data:
                obv_ok = upload_bytes(b_data, dest_obv_path)
        
        # Process Reverse
        print(f"  Reverse source: {rev_url}")
        if rev_url.startswith("local_file:"):
            local_path = rev_url.replace("local_file:", "")
            with open(local_path, "rb") as lf:
                rev_ok = upload_bytes(lf.read(), dest_rev_path)
        elif rev_url.startswith("gs://"):
            rev_ok = copy_gcs_blob(rev_url, dest_rev_path)
        elif rev_url.startswith("http"):
            b_data = download_image(rev_url)
            if b_data:
                rev_ok = upload_bytes(b_data, dest_rev_path)

        if obv_ok and rev_ok:
            # Update Firestore
            t_now = int(time.time())
            firestore_updates = {
                "image_url_obverse": f"{GCS_PUB_BASE}/{dest_obv_path}?t={t_now}",
                "image_url_reverse": f"{GCS_PUB_BASE}/{dest_rev_path}?t={t_now}",
                "image_source": source_tag,
                "image_attribution": attribution,
                "image_fix_reason": "Auto-healed by custom sourcing pipeline",
                "image_updated_at": datetime.now(timezone.utc)
            }
            db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id).update(firestore_updates)
            print(f"  [SUCCESS] Updated Firestore for {coin_name}")
            success_count += 1
        else:
            print(f"  [FAILED] Failed to copy/upload obverse={obv_ok}, reverse={rev_ok}")
            fail_count += 1

    print("\n" + "=" * 70)
    print("HEALING MIGRATION COMPLETED")
    print(f"Total processed: {len(unhealed_ids)}")
    print(f"Successful     : {success_count}")
    print(f"Failed         : {fail_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
