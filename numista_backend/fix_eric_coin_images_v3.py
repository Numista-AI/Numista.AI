import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

def upload_coin_image(doc_id: str, side: str, data: bytes, content_type: str = "image/jpeg") -> str:
    dest_path = f"users/{USER_EMAIL}/coins/{doc_id}/{side}.jpg"
    blob = uploads_bucket_obj.blob(dest_path)
    blob.cache_control = "no-cache, no-store, must-revalidate"
    blob.upload_from_string(data, content_type=content_type)
    url = f"{public_url(UPLOADS_BUCKET, dest_path)}?t={int(time.time())}"
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

# ─── FIX ACTIONS ─────────────────────────────────────────────────────────────

def fix_1a_madison():
    """2007 James Madison Presidential $1 — wrong obverse (showing Jamestown scene) and reverse showing obverse"""
    log("\n" + "="*60)
    log("GROUP 1a: 2007 James Madison Presidential $1")
    log("="*60)
    doc_id = COINS["1a_madison"]
    log(f"  Doc ID: {doc_id}")

    # Obverse: James Madison Berlin Münzkabinett LEFT photo
    obv_blob = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"
                "Presidential__1_Coin_Program/2007_Presidential_dollar_coins/"
                "Presidential_dollar__James_Madison_/USA-_2007_James_Madison_-_M_C3_BCnzkabinett_2C_Berlin_-_5520390_LEFT.jpg")
    # Reverse: James Madison Berlin Münzkabinett RIGHT photo (Statue of Liberty)
    rev_blob = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"
                "Presidential__1_Coin_Program/2007_Presidential_dollar_coins/"
                "Presidential_dollar__James_Madison_/USA-_2007_James_Madison_-_M_C3_BCnzkabinett_2C_Berlin_-_5520390_RIGHT.jpg")

    log("  Source obverse: GCS ref (Berlin Madison LEFT)")
    log("  Source reverse: GCS ref (Berlin Madison RIGHT - Statue of Liberty)")

    delete_existing_upload(doc_id, "obverse")
    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

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
        "image_fix_reason": "Replaced incorrect Jamestown/Madison images with Berlin Münzkabinett obverse and Statue of Liberty reverse.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1a Madison - {doc_id}")

def fix_1b_new_jersey():
    """1999 New Jersey State Quarter — currently showing reverse on both sides"""
    log("\n" + "="*60)
    log("GROUP 1b: 1999 New Jersey State Quarter")
    log("="*60)
    doc_id = COINS["1b_nj"]
    log(f"  Doc ID: {doc_id}")

    # Obverse: Washington Denver State Quarter obverse
    obv_blob = ("reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/"
                "50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg")
    # Reverse: uncirculated New Jersey reverse
    rev_blob = ("reference_library/bulk_programs/50_state_quarters/"
                "1999-50-state-quarters-coin-new-jersey-uncirculated-reverse.jpg")

    log("  Source obverse: GCS ref (Denver State Quarter Washington obverse)")
    log("  Source reverse: GCS ref (1999 NJ uncirculated reverse)")

    delete_existing_upload(doc_id, "obverse")
    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    delete_existing_upload(doc_id, "reverse")
    rev_data = download_gcs_ref(rev_blob)
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": "gcs_reference_library",
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": GCS_ATTRIBUTION,
        "image_attribution": GCS_ATTRIBUTION,
        "image_fix_reason": "Uploaded correct State Quarter Denver obverse (Washington portrait) and New Jersey uncirculated reverse.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1b New Jersey - {doc_id}")

def fix_1c_kennedy_bicentennial():
    """1976 Kennedy Bicentennial Half Dollar — wrong obverse (showing Cowpens medal)"""
    log("\n" + "="*60)
    log("GROUP 1c: 1976 Kennedy Bicentennial Half Dollar")
    log("="*60)
    doc_id = COINS["1c_kennedy76"]
    log(f"  Doc ID: {doc_id}")

    # Obverse: 1976-S 50C Clad Deep Cameo (obverse) — Kennedy portrait with 1776-1976
    obv_blob = ("reference_library/wikimedia_uscoin/Half_dollar__United_States_/"
                "Kennedy_half_dollar/1976-S_50C_Clad_Deep_Cameo__28obv_29.jpg")
    # Reverse: 1976 Bicentennial half dollar reverse (Independence Hall)
    rev_blob = ("reference_library/bulk_programs/bicentennial_coins/"
                "1976-bicentennial-half-dollar-reverse.jpg")

    log("  Source obverse: GCS ref library (1976-S_50C_Clad_Deep_Cameo obverse)")
    log("  Source reverse: GCS ref library (1976 bicentennial half dollar reverse)")

    delete_existing_upload(doc_id, "obverse")
    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

    delete_existing_upload(doc_id, "reverse")
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
        "image_fix_reason": "Replaced incorrect fraternal medal with 1776-1976 Kennedy obverse and Independence Hall reverse.",
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

    # Obverse: 1937 Wheat Penny obverse (closest available era-accurate Wheat Penny obverse in GCS)
    obv_blob = ("reference_library/wikimedia_uscoin/United_States_cents/"
                "Obverses_of_United_States_cents/Both_sides_of_United_States_cents/1937-Wheat-Penny-Front-Back_LEFT.jpg")
    # Reverse: 1937 Wheat Penny reverse
    rev_blob = ("reference_library/wikimedia_uscoin/United_States_cents/"
                "Obverses_of_United_States_cents/Both_sides_of_United_States_cents/1937-Wheat-Penny-Front-Back_RIGHT.jpg")

    log("  Source obverse: GCS ref library (1937 Wheat Penny obverse - date-accurate fallback)")
    log("  Source reverse: GCS ref library (1937 Wheat Penny reverse)")

    delete_existing_upload(doc_id, "obverse")
    obv_data = download_gcs_ref(obv_blob)
    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")

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
        "image_fix_reason": "Replaced incorrect Arkansas Half Dollar with era-accurate 1937 Wheat Penny obverse and reverse.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 1d Lincoln Wheat 1936 - {doc_id}")

def fix_2_sba():
    """SBA Dollars — 1979-P, 1979-D, 1980-D showing wrong 1981 obverse"""
    log("\n" + "="*60)
    log("GROUP 2: SBA Dollars - Wrong Year Obverse (1979-P, 1979-D, 1980-D)")
    log("="*60)

    # 1979 SBA obverse
    sba_1979_obv_blob = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/"
                         "Susan_B._Anthony_dollar/1_us_dollar_1979_LEFT.jpg")

    log("  Source 1979 obverse: GCS ref library (1_us_dollar_1979_LEFT.jpg)")
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
            "image_fix_reason": f"Replaced wrong year obverse with 1979 SBA obverse, applied cache-busting.",
            "last_image_fix": datetime.now(timezone.utc).isoformat(),
        })
        log(f"  [DONE] SBA {year}-{mint} - {doc_id}")

    log("\n  [DONE] GROUP 2: All 3 SBA coins updated")

def fix_3a_semiq_half():
    """2026 Half Dollar (SemiQuincentennial) — apply cache-busting"""
    log("\n" + "="*60)
    log("GROUP 3a: 2026 Half Dollar (SemiQuincentennial)")
    log("="*60)
    doc_id = COINS["3a_semiq_half"]
    log(f"  Doc ID: {doc_id}")

    obv_blob = ("reference_library/bulk_programs/us_mint_manual/highres_scrape/"
                "SemiQ-Half-Dollar-Obverse-Unc-P.jpg")
    rev_blob = ("reference_library/bulk_programs/half_dollar/"
                "SemiQ-Half-Dollar-Reverse-Unc.jpg")

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
        "image_fix_reason": "Re-uploaded with cache-busting query parameter.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3a 2026 SemiQ Half - {doc_id}")

def fix_3b_lincoln_shield():
    """2015 Abraham Lincoln / Union Shield One Cent — apply cache-busting"""
    log("\n" + "="*60)
    log("GROUP 3b: 2015 Abraham Lincoln / Union Shield One Cent")
    log("="*60)
    doc_id = COINS["3b_lincoln2015"]
    log(f"  Doc ID: {doc_id}")

    obv_blob = ("reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/"
                "Lincoln_Shield_cent/2017-P_Lincoln_Shield_cent_obverse.jpg")
    obv_data = download_gcs_ref(obv_blob)

    rev_local = LOCAL_HIGHRES / "2025-lincoln-penny-proof-reverse.jpg"
    if rev_local.exists():
        rev_data = download_local(rev_local)
        rev_source = "local_us_mint_highres"
    else:
        rev_blob = "reference_library/bulk_programs/penny/2017-lincoln-penny-uncirculated-obverse-philadelphia.jpg"
        rev_data = download_gcs_ref(rev_blob)
        rev_source = "gcs_reference_library"

    obv_url = upload_coin_image(doc_id, "obverse", obv_data, "image/jpeg")
    rev_url = upload_coin_image(doc_id, "reverse", rev_data, "image/jpeg")

    update_firestore(doc_id, {
        "image_url_obverse": obv_url,
        "image_url_reverse": rev_url,
        "image_source_obverse": "gcs_reference_library",
        "image_source_reverse": rev_source,
        "image_attribution_obverse": WIKI_ATTRIBUTION,
        "image_attribution_reverse": GCS_ATTRIBUTION,
        "image_attribution": WIKI_ATTRIBUTION,
        "image_fix_reason": "Re-uploaded with cache-busting query parameter.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3b Lincoln Shield 2015 - {doc_id}")

def fix_3c_kennedy_1973():
    """1973 Kennedy Half Dollar — apply cache-busting"""
    log("\n" + "="*60)
    log("GROUP 3c: 1973 Kennedy Half Dollar")
    log("="*60)
    doc_id = COINS["3c_kennedy73"]
    log(f"  Doc ID: {doc_id}")

    obv_blob = ("reference_library/wikimedia_uscoin/Half_dollar__United_States_/"
                "Kennedy_half_dollar/2005_Half_Dollar_Obv_Unc_P.png")
    rev_blob = ("reference_library/wikimedia_uscoin/Half_dollar__United_States_/"
                "Kennedy_half_dollar/2005_Half_Dollar_Rev_Unc_P.png")

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
        "image_fix_reason": "Re-uploaded with cache-busting query parameter.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3c Kennedy Half 1973 - {doc_id}")

def fix_3d_roosevelt_dime():
    """1963 Roosevelt Dime — apply cache-busting"""
    log("\n" + "="*60)
    log("GROUP 3d: 1963 Roosevelt Dime")
    log("="*60)
    doc_id = COINS["3d_dime63"]
    log(f"  Doc ID: {doc_id}")

    obv_blob = ("reference_library/wikimedia_uscoin/United_States_dimes/"
                "Roosevelt_dimes/2015-W_proof_Roosevelt_dime_LEFT.jpg")
    rev_blob = ("reference_library/wikimedia_uscoin/United_States_dimes/"
                "Roosevelt_dimes/2015-W_proof_Roosevelt_dime_RIGHT.jpg")

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
        "image_fix_reason": "Re-uploaded with cache-busting query parameter.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3d Roosevelt Dime 1963 - {doc_id}")

def fix_3e_steel_cent():
    """1943 Abraham Lincoln Steel Cent — apply cache-busting"""
    log("\n" + "="*60)
    log("GROUP 3e: 1943 Abraham Lincoln Steel Cent")
    log("="*60)
    doc_id = COINS["3e_steel43"]
    log(f"  Doc ID: {doc_id}")

    obv_blob = "reference_library/bulk_programs/penny/1943-steel-penny-obverse.jpg"
    rev_blob = ("reference_library/wikimedia_uscoin/Coins__NNC_/"
                "NNC-US-1943-1C-Lincoln_Cent__28wheat_2C_zinc-coated_steel_29_RIGHT.jpg")

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
        "image_fix_reason": "Re-uploaded with cache-busting query parameter.",
        "last_image_fix": datetime.now(timezone.utc).isoformat(),
    })
    log(f"  [DONE] 3e Steel Cent 1943 - {doc_id}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("NUMISTA.AI -- Coin Image Fix Script v3 (Cache-Busting & Exact Mappings)")
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

    # GROUP 1: Wrong images & Correct Mappings
    run("1a_madison", fix_1a_madison)
    run("1b_nj_quarter", fix_1b_new_jersey)
    run("1c_kennedy76", fix_1c_kennedy_bicentennial)
    run("1d_lincoln36", fix_1d_lincoln_wheat)

    # GROUP 2: SBA wrong year
    run("2_sba", fix_2_sba)

    # GROUP 3: Missing images & Cache-Busters
    run("3a_semiq_half", fix_3a_semiq_half)
    run("3b_lincoln2015", fix_3b_lincoln_shield)
    run("3c_kennedy73", fix_3c_kennedy_1973)
    run("3d_dime63", fix_3d_roosevelt_dime)
    run("3e_steel43", fix_3e_steel_cent)

    # Summary
    log("\n" + "=" * 60)
    log("FINAL SUMMARY")
    log("=" * 60)
    total = len(COINS)
    done = total - len(errors)
    log(f"Coins fixed: {done}/{total}")

    if errors:
        log(f"[WARN] {len(errors)} errors:")
        for e in errors:
            log(f"  {e}")
    else:
        log("[DONE] All fixes completed successfully!")

    # Save report
    report_path = WORK_DIR / "fix_eric_coin_images_report_v3.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(REPORT))
    log(f"\nReport saved: {report_path}")

if __name__ == "__main__":
    main()
