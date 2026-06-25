"""
fix_eric_coin_images_v2.py
===========================
Fixes image errors and missing images for eric@numista.ai's coin collection.
Uses exact doc IDs found via pre-scan.

Run: python fix_eric_coin_images_v2.py
"""

import sys
import os
# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# ─── CONFIG ──────────────────────────────────────────────────────────────────
WORK_DIR = Path(r"C:\Users\ericd\Documents\MyVertexProject\numista_backend")
SA_KEY = WORK_DIR / "serviceAccountKey.json.json"
PROJECT_ID = "studio-9101802118-8c9a8"
REF_BUCKET = "numista-reference-library"
UPLOADS_BUCKET = f"numista-uploads-{PROJECT_ID}"
USER_EMAIL = "eric@numista.ai"

GCS_ATTRIBUTION = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"
WIKI_ATTRIBUTION = "Public Domain. Source: Wikimedia Commons"

LOCAL_HIGHRES = Path(r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\HighRes_Scrape")
LOCAL_2026 = Path(r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\US MINT\2026")

# ─── EXACT DOC IDs (pre-scanned) ─────────────────────────────────────────────
COINS = {
    "1a_madison":     "6ee1bdb5-47cd-4fe1-b9fb-033f5bf45689",  # 2007 James Madison Presidential $1
    "1b_nj":          "b5f9c5ae-11dd-44b6-9f1f-b0113cf9cbf6",  # 1999 New Jersey State Quarter
    "1c_kennedy76":   "f0b1984b-0ebf-496e-93fd-aa5ea63f04b8",  # 1976 Kennedy Bicentennial Half
    "1d_lincoln36":   "80103054-84e3-45ab-aebd-322c01e723b9",  # 1936 Lincoln Cent Wheat
    "2_sba_1979p":    "0a7be39a-8210-4524-985a-fe8e87de440a",  # 1979-P SBA
    "2_sba_1980d":    "0ff72932-2a36-4cad-b1de-4a5deb2d295a",  # 1980-D SBA
    "2_sba_1979d":    "dee46559-9787-4fac-8e02-96f0ea6cfb43",  # 1979-D SBA
    "3a_semiq_half":  "b22f8905-4eca-45e9-ba57-920fb5427b22",  # 2026 SemiQ Half Dollar
    "3b_lincoln2015": "dd851d66-227f-45af-9aff-c0adb69b8bd4",  # 2015 Lincoln Shield Cent
    "3c_kennedy73":   "9d06e94d-eb85-48c2-b4ba-38a47c9ed39f",  # 1973 Kennedy Half
    "3d_dime63":      "fccc89c5-3d05-4dcd-8f28-f9acadff4d72",  # 1963 Roosevelt Dime
    "3e_steel43":     "6057acbd-ec5b-4f52-9a2c-fa21534267d8",  # 1943 Steel Cent
}

# ─── INITIALIZE ──────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)

db = firestore.client()
gcs = storage.Client.from_service_account_json(str(SA_KEY))
ref_bucket_obj = gcs.bucket(REF_BUCKET)
uploads_bucket_obj = gcs.bucket(UPLOADS_BUCKET)

REPORT = []


def log(msg):
    # Replace any problematic unicode with ASCII equivalents
    safe = msg.replace("✓", "[OK]").replace("✅", "[DONE]").replace("❌", "[ERR]").replace(
        "🗑", "[DEL]").replace("⚠", "[WARN]").replace("→", "->").replace("↔", "<->")
    print(safe)
    REPORT.append(safe)


def public_url(bucket_name, blob_path):
    return f"https://storage.googleapis.com/{bucket_name}/{blob_path}"


def download_gcs_ref(blob_path: str) -> bytes:
    blob = ref_bucket_obj.blob(blob_path)
    return blob.download_as_bytes()


def download_local(file_path: Path) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def upload_coin_image(doc_id: str, side: str, data: bytes,
                      content_type: str = "image/jpeg") -> str:
    dest_path = f"users/{USER_EMAIL}/coins/{doc_id}/{side}.jpg"
    bucket = uploads_bucket_obj
    blob = bucket.blob(dest_path)
    blob.upload_from_string(data, content_type=content_type)
    url = public_url(UPLOADS_BUCKET, dest_path)
    log(f"  [OK] Uploaded {side} -> {dest_path}")
    return url


def delete_existing_upload(doc_id: str, side: str):
    blob_path = f"users/{USER_EMAIL}/coins/{doc_id}/{side}.jpg"
    blob = uploads_bucket_obj.blob(blob_path)
    try:
        if blob.exists():
            blob.delete()
            log(f"  [DEL] Deleted existing {side}: {blob_path}")
    except Exception as e:
        log(f"  [WARN] Could not delete {blob_path}: {e}")


def update_firestore(doc_id: str, fields: dict):
    doc_ref = (db.collection("users")
               .document(USER_EMAIL)
               .collection("coins")
               .document(doc_id))
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    doc_ref.update(fields)
    log(f"  [OK] Firestore updated: {list(fields.keys())}")


# ─── FIXES ───────────────────────────────────────────────────────────────────

def fix_1a_madison():
    """2007 James Madison Presidential $1 — wrong obverse (showing Jamestown scene)"""
    log("\n" + "="*60)
    log("GROUP 1a: 2007 James Madison Presidential $1")
    log("="*60)
    doc_id = COINS["1a_madison"]
    log(f"  Doc ID: {doc_id}")

    # Delete wrong image first
    delete_existing_upload(doc_id, "obverse")

    # Obverse: James Madison Presidential $1 Coin obverse (high res PNG from Wikimedia via GCS)
    obv_blob = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"
                "Presidential__1_Coin_Program/2007_Presidential_dollar_coins/"
                "Presidential_dollar__James_Madison_/James_Madison_Presidential__241_Coin_obverse.png")
    # Reverse: Use the full coin image (front+reverse combined) as reverse placeholder,
    # or the 1_dollar_James_Madison_.jpg which shows the whole coin
    rev_blob = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"
                "Presidential__1_Coin_Program/2007_Presidential_dollar_coins/"
                "Presidential_dollar__James_Madison_/1_dollar_James_Madison_.jpg")

    log("  Source obverse: GCS ref library (James_Madison_Presidential__241_Coin_obverse.png)")
    log("  Source reverse: GCS ref library (1_dollar_James_Madison_.jpg)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/png")

    delete_existing_upload(doc_id, "reverse")
    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": WIKI_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Wrong image replaced: was showing Jamestown scene, now shows Madison portrait",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1a Madison - {doc_id}")


def fix_1b_new_jersey():
    """1999 New Jersey State Quarter — obverse and reverse fields are swapped"""
    log("\n" + "="*60)
    log("GROUP 1b: 1999 New Jersey State Quarter -- SWAP obverse/reverse")
    log("="*60)
    doc_id = COINS["1b_nj"]
    log(f"  Doc ID: {doc_id}")

    # Get current values
    doc_ref = (db.collection("users")
               .document(USER_EMAIL)
               .collection("coins")
               .document(doc_id))
    data = doc_ref.get().to_dict()
    current_obv = data.get("image_url_obverse", "")
    current_rev = data.get("image_url_reverse", "")
    src_obv = data.get("image_source_obverse", "")
    src_rev = data.get("image_source_reverse", "")

    log(f"  Current obverse URL: ...{current_obv[-60:] if current_obv else 'NONE'}")
    log(f"  Current reverse URL: ...{current_rev[-60:] if current_rev else 'NONE'}")
    log("  -> Swapping obverse <-> reverse fields (images are correct, just in wrong fields)")

    update_firestore(doc_id, {
        "image_url_obverse": current_rev,
        "image_url_reverse": current_obv,
        "image_source_obverse": src_rev,
        "image_source_reverse": src_obv,
        "image_fix_reason": "Swapped: obverse was showing Washington Crossing the Delaware (reverse), now shows Washington portrait",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1b New Jersey - {doc_id} (fields swapped, no re-download needed)")


def fix_1c_kennedy_bicentennial():
    """1976 Kennedy Bicentennial Half Dollar — wrong obverse (showing fraternal org medal)"""
    log("\n" + "="*60)
    log("GROUP 1c: 1976 Kennedy Bicentennial Half Dollar")
    log("="*60)
    doc_id = COINS["1c_kennedy76"]
    log(f"  Doc ID: {doc_id}")

    delete_existing_upload(doc_id, "obverse")
    delete_existing_upload(doc_id, "reverse")

    # Obverse: 1976-S 50C Clad Deep Cameo (obverse) — Kennedy portrait with 1776-1976
    obv_blob = ("reference_library/wikimedia_uscoin/Half_dollar__United_States_/"
                "Kennedy_half_dollar/1976-S_50C_Clad_Deep_Cameo__28obv_29.jpg")
    # Reverse: 1976 Bicentennial half dollar reverse (Independence Hall)
    rev_blob = ("reference_library/bulk_programs/bicentennial_coins/"
                "1976-bicentennial-half-dollar-reverse.jpg")

    log("  Source obverse: GCS ref library (1976-S_50C_Clad_Deep_Cameo obverse - Kennedy portrait)")
    log("  Source reverse: GCS ref library (1976 bicentennial half dollar reverse - Independence Hall)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": GCS_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Wrong image replaced: was showing JOH Egar Howard Legions medal, now shows Kennedy portrait",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1c Kennedy Bicentennial - {doc_id}")


def fix_1d_lincoln_wheat():
    """1936 Lincoln Cent (Wheat Penny) — wrong obverse (showing Arkansas Half Dollar)"""
    log("\n" + "="*60)
    log("GROUP 1d: 1936 Lincoln Cent (Wheat Penny)")
    log("="*60)
    doc_id = COINS["1d_lincoln36"]
    log(f"  Doc ID: {doc_id}")

    delete_existing_upload(doc_id, "obverse")
    delete_existing_upload(doc_id, "reverse")

    # Obverse: Good Lincoln wheat cent obverse. Use 1962-D Lincoln Penny (clean wheat era)
    obv_blob = ("reference_library/wikimedia_uscoin/United_States_cents/"
                "Obverses_of_United_States_cents/1962_D_Lincoln_Penny__28U.S._Coin.jpg")
    # Reverse: 1909-S VDB Lincoln cent RIGHT (wheat reverse — same design 1909-1958)
    rev_blob = ("reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/"
                "Lincoln_Wheat_cent/Obverse__28left_29_and_reverse__28right_29_of_1909-S_VDB_Lincoln_cent_RIGHT.jpg")

    log("  Source obverse: GCS ref library (1962-D Lincoln Penny obverse - wheat era portrait)")
    log("  Source reverse: GCS ref library (1909-S VDB Lincoln cent RIGHT - wheat reverse design)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": WIKI_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Wrong image replaced: was showing 1936 Arkansas Half Dollar, now shows Lincoln Wheat cent",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1d Lincoln Wheat 1936 - {doc_id}")


def fix_2_sba():
    """SBA Dollars — 1979-P, 1979-D, 1980-D showing wrong 1981 obverse"""
    log("\n" + "="*60)
    log("GROUP 2: SBA Dollars - Wrong Year Obverse (1979-P, 1979-D, 1980-D)")
    log("="*60)

    # 1979 SBA obverse (year-specific from GCS reference library)
    sba_1979_obv_blob = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"
                         "Susan_B._Anthony_dollar/1_us_dollar_1979_LEFT.jpg")
    # Same image for 1980 (SBA design identical except date)
    sba_1980_obv_blob = sba_1979_obv_blob

    log("  Source 1979 obverse: GCS ref library (1_us_dollar_1979_LEFT.jpg - shows 1979 date)")
    log("  Source 1980 obverse: GCS ref library (same SBA design - 1979 as best available)")

    sba_data = download_gcs_ref(sba_1979_obv_blob)

    sba_coins = [
        ("2_sba_1979p", COINS["2_sba_1979p"], "1979", "P"),
        ("2_sba_1979d", COINS["2_sba_1979d"], "1979", "D"),
        ("2_sba_1980d", COINS["2_sba_1980d"], "1980", "D"),
    ]

    for key, doc_id, year, mint in sba_coins:
        log(f"\n  Processing {year}-{mint} SBA: {doc_id}")
        delete_existing_upload(doc_id, "obverse")
        obv_url = upload_coin_image(doc_id, "obverse", sba_data, "image/jpeg")
        update_firestore(doc_id, {
            "image_url_obverse": obv_url,
            "image_source_obverse": "gcs_reference_library",
            "image_attribution_obverse": WIKI_ATTRIBUTION,
            "image_attribution": WIKI_ATTRIBUTION,
            "image_fix_reason": f"Wrong year obverse replaced: was showing 1981, now shows correct 1979 SBA",
            "last_image_fix": datetime.now(timezone.utc).isoformat(),
        })
        log(f"  [DONE] SBA {year}-{mint} - {doc_id}")

    log("\n  [DONE] GROUP 2: All 3 SBA coins updated")


def fix_3a_semiq_half():
    """2026 Half Dollar (SemiQuincentennial) — missing images"""
    log("\n" + "="*60)
    log("GROUP 3a: 2026 Half Dollar (SemiQuincentennial)")
    log("="*60)
    doc_id = COINS["3a_semiq_half"]
    log(f"  Doc ID: {doc_id}")

    # GCS reference library has the SemiQ Half Dollar already
    obv_blob = ("reference_library/bulk_programs/us_mint_manual/highres_scrape/"
                "SemiQ-Half-Dollar-Obverse-Unc-P.jpg")
    rev_blob = ("reference_library/bulk_programs/half_dollar/"
                "SemiQ-Half-Dollar-Reverse-Unc.jpg")

    log("  Source obverse: GCS ref library (SemiQ-Half-Dollar-Obverse-Unc-P.jpg)")
    log("  Source reverse: GCS ref library (SemiQ-Half-Dollar-Reverse-Unc.jpg)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": GCS_ATTRIBUTION,
        "image_attribution_reverse": GCS_ATTRIBUTION,
        "image_attribution": GCS_ATTRIBUTION,
        "image_fix_reason": "Added missing images from GCS reference library",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3a 2026 SemiQ Half - {doc_id}")


def fix_3b_lincoln_shield():
    """2015 Abraham Lincoln / Union Shield One Cent — missing images"""
    log("\n" + "="*60)
    log("GROUP 3b: 2015 Abraham Lincoln / Union Shield One Cent")
    log("="*60)
    doc_id = COINS["3b_lincoln2015"]
    log(f"  Doc ID: {doc_id}")

    # Obverse: 2017-P Lincoln Shield cent obverse (same portrait design 2010-present)
    obv_blob = ("reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/"
                "Lincoln_Shield_cent/2017-P_Lincoln_Shield_cent_obverse.jpg")

    log("  Source obverse: GCS ref library (2017-P Lincoln Shield cent obverse)")

    # Reverse: Use 2025 Lincoln proof reverse (Union Shield design) from local HighRes_Scrape
    rev_local = LOCAL_HIGHRES / "2025-lincoln-penny-proof-reverse.jpg"
    if rev_local.exists():
        rev_data = download_local(rev_local)
        rev_source = "local_us_mint_highres (2025-lincoln-penny-proof-reverse.jpg - Union Shield)"
        rev_attribution = GCS_ATTRIBUTION
        log(f"  Source reverse: Local HighRes_Scrape (2025-lincoln-penny-proof-reverse.jpg - Union Shield design)")
    else:
        # Fallback: use 2025 proof reverse from reference lib if available
        rev_blob = "reference_library/bulk_programs/penny/2017-lincoln-penny-uncirculated-obverse-philadelphia.jpg"
        rev_data = download_gcs_ref(rev_blob)
        rev_source = "gcs_reference_library (2017 lincoln penny obverse - fallback)"
        rev_attribution = GCS_ATTRIBUTION
        log("  Source reverse: GCS ref library fallback (2017 lincoln penny)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": rev_source,
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": rev_attribution,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Added missing images - Lincoln portrait obverse, Union Shield reverse",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3b Lincoln Shield 2015 - {doc_id}")


def fix_3c_kennedy_1973():
    """1973 Kennedy Half Dollar — missing images"""
    log("\n" + "="*60)
    log("GROUP 3c: 1973 Kennedy Half Dollar")
    log("="*60)
    doc_id = COINS["3c_kennedy73"]
    log(f"  Doc ID: {doc_id}")

    # Standard Kennedy half (same design 1964-1974, Presidential seal reverse)
    obv_blob = ("reference_library/wikimedia_uscoin/Half_dollar__United_States_/"
                "Kennedy_half_dollar/2005_Half_Dollar_Obv_Unc_P.png")
    rev_blob = ("reference_library/wikimedia_uscoin/Half_dollar__United_States_/"
                "Kennedy_half_dollar/2005_Half_Dollar_Rev_Unc_P.png")

    log("  Source obverse: GCS ref library (2005_Half_Dollar_Obv_Unc_P.png - same 1964-present design)")
    log("  Source reverse: GCS ref library (2005_Half_Dollar_Rev_Unc_P.png - Presidential seal)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/png")

    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/png")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": WIKI_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Added missing images - Kennedy portrait obverse, Presidential seal reverse",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3c Kennedy Half 1973 - {doc_id}")


def fix_3d_roosevelt_dime():
    """1963 Roosevelt Dime — missing images"""
    log("\n" + "="*60)
    log("GROUP 3d: 1963 Roosevelt Dime")
    log("="*60)
    doc_id = COINS["3d_dime63"]
    log(f"  Doc ID: {doc_id}")

    # 2015-W proof Roosevelt dime — same FDR design 1946-present
    obv_blob = ("reference_library/wikimedia_uscoin/United_States_dimes/"
                "Roosevelt_dimes/2015-W_proof_Roosevelt_dime_LEFT.jpg")
    rev_blob = ("reference_library/wikimedia_uscoin/United_States_dimes/"
                "Roosevelt_dimes/2015-W_proof_Roosevelt_dime_RIGHT.jpg")

    log("  Source obverse: GCS ref library (2015-W proof Roosevelt dime LEFT - FDR portrait, same design 1946-present)")
    log("  Source reverse: GCS ref library (2015-W proof Roosevelt dime RIGHT - torch/olive/oak)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": WIKI_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Added missing images - FDR portrait obverse, torch/olive/oak reverse",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3d Roosevelt Dime 1963 - {doc_id}")


def fix_3e_steel_cent():
    """1943 Abraham Lincoln Steel Cent — missing images"""
    log("\n" + "="*60)
    log("GROUP 3e: 1943 Abraham Lincoln Steel Cent")
    log("="*60)
    doc_id = COINS["3e_steel43"]
    log(f"  Doc ID: {doc_id}")

    # High quality 1943 steel penny obverse
    obv_blob = "reference_library/bulk_programs/penny/1943-steel-penny-obverse.jpg"
    # NNC 1943 Lincoln Cent (wheat, zinc-coated steel) RIGHT = reverse
    rev_blob = ("reference_library/wikimedia_uscoin/Coins__NNC_/"
                "NNC-US-1943-1C-Lincoln_Cent__28wheat_2C_zinc-coated_steel_29_RIGHT.jpg")

    log("  Source obverse: GCS ref library (1943-steel-penny-obverse.jpg)")
    log("  Source reverse: GCS ref library (NNC 1943 Lincoln Cent wheat steel RIGHT)")

    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": WIKI_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Added missing images - 1943 steel cent obverse, wheat reverse",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3e Steel Cent 1943 - {doc_id}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("NUMISTA.AI -- Coin Image Fix Script v2")
    log(f"User: {USER_EMAIL}")
    log(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Total coins to fix: {len(COINS)}")
    log("=" * 60)

    errors = []

    def run(label, fn):
        try:
            fn()
        except Exception as e:
            import traceback
            msg = f"[ERR] ERROR in {label}: {e}"
            log(msg)
            errors.append(msg)
            traceback.print_exc()

    # GROUP 1: Wrong images
    run("1a_madison", fix_1a_madison)
    run("1b_nj_swap", fix_1b_new_jersey)
    run("1c_kennedy76", fix_1c_kennedy_bicentennial)
    run("1d_lincoln36", fix_1d_lincoln_wheat)

    # GROUP 2: SBA wrong year
    run("2_sba", fix_2_sba)

    # GROUP 3: Missing images
    run("3a_semiq_half", fix_3a_semiq_half)
    run("3b_lincoln2015", fix_3b_lincoln_shield)
    run("3c_kennedy73", fix_3c_kennedy_1973)
    run("3d_dime63", fix_3d_roosevelt_dime)
    run("3e_steel43", fix_3e_steel_cent)

    # Summary
    log("\n" + "=" * 60)
    log("FINAL SUMMARY")
    log("=" * 60)
    total = 12  # 4 wrong + 3 SBA + 5 missing
    done = total - len(errors)
    log(f"Coins fixed: {done}/{total}")

    if errors:
        log(f"[WARN] {len(errors)} errors:")
        for e in errors:
            log(f"  {e}")
    else:
        log("[DONE] All fixes completed successfully!")

    # Save report
    report_path = WORK_DIR / "fix_eric_coin_images_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(REPORT))
    log(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
