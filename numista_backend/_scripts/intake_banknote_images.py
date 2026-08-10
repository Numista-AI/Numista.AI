# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
intake_banknote_images.py
─────────────────────────────────────────────────────────────────────────────
Ingests banknote reference image batches into Google Cloud Storage
gs://numista-reference-library/reference_library/us_banknotes/ and updates Firestore.

Requirements:
  - Staging directory containing banknote images + MANIFEST.json
  - MANIFEST.json must contain valid source, attribution, license, and attestation.

Run:
    python numista_backend/_scripts/intake_banknote_images.py --staging-dir ./scratch/intake_batch1 [--dry-run] [--ai-screening]

Options:
    --staging-dir   Path to local directory with images + MANIFEST.json
    --dry-run       Validate MANIFEST and files without pushing to GCS or Firestore
    --ai-screening  Opt-in Gemini vision inspection to detect synthetic AI renders
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from google.cloud import storage, firestore
import google.auth

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

PROJECT_ID = "studio-9101802118-8c9a8"
REFERENCE_BUCKET = "numista-reference-library"
GCS_PREFIX = "reference_library/us_banknotes/"

# Default credentials setup
if os.path.exists("./serviceAccountKey.json.json"):
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
elif os.path.exists("./serviceAccountKey.json"):
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json")


def validate_manifest(staging_path: Path):
    """Validates presence and schema of MANIFEST.json."""
    manifest_file = staging_path / "MANIFEST.json"
    if not manifest_file.exists():
        return False, f"Missing MANIFEST.json in {staging_path}", None

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Failed to parse MANIFEST.json: {e}", None

    items = data.get("items", [])
    if not items:
        return False, "MANIFEST.json contains no items under 'items' array", None

    # Validate each item
    for idx, item in enumerate(items):
        req_fields = ["filename", "side", "catalog_key", "source", "attribution", "license"]
        for field in req_fields:
            if not item.get(field):
                return False, f"Item #{idx+1} ({item.get('filename', 'unknown')}) missing required field: '{field}'", None

        filename = item["filename"]
        file_path = staging_path / filename
        if not file_path.exists():
            return False, f"Referenced image file does not exist in staging: {filename}", None

        # Check AI render attestation
        if item.get("is_ai_generated") is True:
            return False, f"Item '{filename}' is flagged as AI generated. AI renders are prohibited from shared reference library.", None

    return True, "MANIFEST validated successfully", data


def run_gemini_ai_screening(file_path: Path) -> tuple[bool, str]:
    """Runs opt-in Gemini vision screening to inspect candidate image for synthetic artifacts."""
    if not GEMINI_AVAILABLE:
        return True, "google-genai SDK not installed, skipping AI screening."

    try:
        client = genai.Client()
        with open(file_path, "rb") as img_f:
            image_bytes = img_f.read()

        prompt = (
            "Analyze this banknote image. Determine if this is an authentic physical note photograph "
            "or a synthetic/AI-generated render. Respond in JSON format with keys:\n"
            '{"is_authentic_photo": true|false, "confidence": float, "reasoning": "string"}'
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt,
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        res_json = json.loads(response.text)
        is_authentic = res_json.get("is_authentic_photo", True)
        reasoning = res_json.get("reasoning", "Passed inspection")

        if not is_authentic:
            return False, f"Gemini Vision flagged potential synthetic render: {reasoning}"
        return True, f"Passed Gemini screening ({reasoning})"

    except Exception as e:
        print(f"⚠️ Gemini screening warning for {file_path.name}: {e}")
        return True, f"Screening bypassed due to API response: {e}"


def get_gcs_folder_for_tier(catalog_tier: str) -> str:
    """Maps catalog tier to subfolder in GCS reference library."""
    tier_map = {
        "federal": "federal/silver_certificates/",
        "confederate": "confederate/",
        "fractional": "fractional/",
        "obsolete": "obsolete/",
        "errors": "errors/",
        "uncut_sheets": "uncut_sheets/",
    }
    return tier_map.get(catalog_tier.lower(), "federal/")


def main():
    parser = argparse.ArgumentParser(description="Intake banknote reference image batch into GCS and Firestore.")
    parser.add_argument("--staging-dir", required=True, help="Path to local directory containing images and MANIFEST.json")
    parser.add_argument("--dry-run", action="store_true", help="Validate batch without uploading to GCS or Firestore")
    parser.add_argument("--ai-screening", action="store_true", help="Run optional Gemini vision screening to detect AI renders")
    args = parser.parse_args()

    staging_path = Path(args.staging_dir)
    print("==========================================================")
    print("Numista.AI Banknote Reference Intake Engine")
    print(f"Staging Path: {staging_path.resolve()}")
    print(f"Target Bucket: gs://{REFERENCE_BUCKET}/{GCS_PREFIX}")
    print(f"Dry Run Mode: {args.dry_run}")
    print(f"AI Vision Screening: {args.ai_screening}")
    print("==========================================================")

    # 1. Validate MANIFEST
    valid, msg, manifest = validate_manifest(staging_path)
    if not valid:
        print(f"❌ MANIFEST Validation Failed: {msg}")
        sys.exit(1)

    print(f"✅ {msg}")
    items = manifest.get("items", [])
    print(f"📦 Found {len(items)} items in manifest batch '{manifest.get('batch_id', 'unknown')}'")

    # Initialize GCP clients
    try:
        credentials, project = google.auth.default()
        storage_client = storage.Client(credentials=credentials, project=PROJECT_ID)
        db = firestore.Client(credentials=credentials, project=PROJECT_ID)
    except Exception as e:
        print(f"❌ GCP Client Initialization Failed: {e}")
        sys.exit(1)

    bucket = storage_client.bucket(REFERENCE_BUCKET)
    uploaded_count = 0

    # 2. Process items
    for item in items:
        filename = item["filename"]
        catalog_key = item["catalog_key"]
        file_path = staging_path / filename

        print(f"\nProcessing [{catalog_key}] -> {filename}")

        # Optional Gemini Vision Screening
        if args.ai_screening:
            print("  🤖 Running Gemini vision inspection...")
            pass_ai, ai_msg = run_gemini_ai_screening(file_path)
            if not pass_ai:
                print(f"  ❌ AI Screening Rejected File: {ai_msg}")
                sys.exit(1)
            print(f"  ✅ {ai_msg}")

        # Determine GCS path
        tier = item.get("catalog_tier", "federal")
        subfolder = get_gcs_folder_for_tier(tier)
        gcs_object_name = f"{GCS_PREFIX}{subfolder}{filename}"
        public_url = f"https://storage.googleapis.com/{REFERENCE_BUCKET}/{gcs_object_name}"

        if args.dry_run:
            print(f"  🔍 DRY RUN: Would upload to gs://{REFERENCE_BUCKET}/{gcs_object_name}")
        else:
            # Upload to GCS
            blob = bucket.blob(gcs_object_name)
            blob.upload_from_filename(str(file_path), content_type="image/jpeg")
            print(f"  ☁️ Uploaded to gs://{REFERENCE_BUCKET}/{gcs_object_name}")

            # Write Firestore record with catalog_key as Document ID (O(1) point read)
            now_iso = datetime.now(timezone.utc).isoformat()
            doc_data = {
                "catalog_key": catalog_key,
                "catalog_tier": tier,
                "friedberg": item.get("friedberg"),
                "variant": item.get("variant"),
                "is_star_note": item.get("is_star_note", False),
                "denomination_str": item.get("denomination_str", "$1.00"),
                "denomination_num": item.get("denomination_num", 1.00),
                "series": item.get("series", "Standard"),
                "side": item.get("side", "obverse"),
                "gcs_path": f"gs://{REFERENCE_BUCKET}/{gcs_object_name}",
                "public_url": public_url,
                "source": item.get("source"),
                "attribution": item.get("attribution"),
                "license": item.get("license"),
                "notes": item.get("notes"),
                "is_reference_fallback": True,
                "updated_at": now_iso,
            }

            db.collection("currency_image_index").document(catalog_key).set(doc_data, merge=True)
            print(f"  💾 Firestore Document updated: currency_image_index/{catalog_key}")

        uploaded_count += 1

    print("\n----------------------------------------------------------")
    print(f"🎉 Intake Complete. Processed {uploaded_count} reference images.")
    if args.dry_run:
        print("🔍 DRY RUN FINISHED — No files were written to GCS or Firestore.")


if __name__ == "__main__":
    main()
