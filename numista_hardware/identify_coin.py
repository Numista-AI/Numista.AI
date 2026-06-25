import os
import json
import logging
import tempfile
import requests as _requests
from google import genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Safely loads your API key from the .env file. Never hardcode keys in code!
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY is not set. Check your .env file.")

client = genai.Client(api_key=api_key)

MANIFEST_PATH = 'numista_database_ready (1).csv'

# ── Reference Library (Firestore) ────────────────────────────────────────────
# Lazy-loaded to avoid slowing startup if Firestore isn't available.
_ref_db = None

def _get_ref_db():
    """Return a Firestore client for querying reference_library."""
    global _ref_db
    if _ref_db is not None:
        return _ref_db
    try:
        from google.cloud import firestore as _fs
        import sys
        
        # 1. Try bundled path (if running inside PyInstaller bundle)
        if hasattr(sys, "_MEIPASS"):
            key_file = os.path.join(sys._MEIPASS, "serviceAccountKey.json.json")
        else:
            # 2. Try development path relative to this script
            _here = os.path.dirname(os.path.abspath(__file__))
            key_file = os.path.abspath(
                os.path.join(_here, "..", "numista_backend", "serviceAccountKey.json.json")
            )
            
        if os.path.exists(key_file):
            import google.oauth2.service_account as sa
            creds = sa.Credentials.from_service_account_file(key_file)
            _ref_db = _fs.Client(credentials=creds, project="studio-9101802118-8c9a8")
            logger.info(f"[REF] Firestore client initialized with service account key: {key_file}")
        else:
            logger.warning(f"[REF] Service account key not found at {key_file}. Falling back to ADC.")
            _ref_db = _fs.Client(project="studio-9101802118-8c9a8")
        return _ref_db
    except Exception as e:
        logger.warning(f"[REF] Could not init Firestore for reference library: {e}")
        return None


def _normalize_denom(raw: str) -> str:
    """Map free-form denomination strings to canonical reference_library values."""
    s = raw.lower().strip()
    if 'cent' in s or 'penny' in s or '1c' in s:   return 'Cent'
    if 'nickel' in s or '5c' in s:                   return 'Nickel'
    if 'dime' in s or '10c' in s:                    return 'Dime'
    if 'quarter' in s or '25c' in s:                 return 'Quarter'
    if 'half' in s or '50c' in s:                    return 'Half Dollar'
    if 'dollar' in s or '$1' in s:                   return 'Dollar'
    return raw


def _fetch_reference_images(denomination: str, year: int, max_images: int = 3):
    """
    Query Firestore reference_library for images matching the denomination
    and year (±5). Returns a list of dicts: {gcs_url, year, denomination, side}.
    """
    db = _get_ref_db()
    if db is None:
        return []

    norm = _normalize_denom(denomination)
    year_low = year - 5 if year else 0
    year_high = year + 5 if year else 9999

    try:
        from google.cloud.firestore_v1.base_query import FieldFilter

        q = db.collection("reference_library") \
              .where(filter=FieldFilter("denomination", "==", norm)) \
              .limit(30)
        # Try with year range filter (requires composite index)
        try:
            if year:
                q = db.collection("reference_library") \
                      .where(filter=FieldFilter("denomination", "==", norm)) \
                      .where(filter=FieldFilter("year_int", ">=", year_low)) \
                      .where(filter=FieldFilter("year_int", "<=", year_high)) \
                      .limit(30)
            docs = list(q.stream())
        except Exception:
            # Fall back to denomination-only if composite index missing
            docs = list(
                db.collection("reference_library")
                  .where(filter=FieldFilter("denomination", "==", norm))
                  .limit(30)
                  .stream()
            )

        results = []
        for doc in docs:
            d = doc.to_dict()
            url = d.get("gcs_url", "")
            if url:
                yr_str = d.get("year") or "Unknown"
                results.append({
                    "gcs_url": url,
                    "year": str(yr_str),
                    "denomination": d.get("denomination", ""),
                    "side": d.get("side", ""),
                })

        # Sort by year proximity (safe for None/non-numeric years)
        if year:
            def _year_dist(r):
                try:
                    return abs(int(r["year"]) - year)
                except (ValueError, TypeError):
                    return 9999
            results.sort(key=_year_dist)

        chosen = results[:max_images]
        logger.info(f"[REF] Found {len(results)} reference images for {norm} "
                     f"~{year}, using {len(chosen)}")
        return chosen

    except Exception as e:
        logger.warning(f"[REF] Reference library query failed: {e}")
        return []


# Lazy-loaded GCS client
_storage_client = None

def _get_storage_client():
    """Return an authenticated GCS client."""
    global _storage_client
    if _storage_client is not None:
        return _storage_client
    try:
        from google.cloud import storage as _gs
        db = _get_ref_db() # Reuses auth logic from Firestore helper
        if db:
            _storage_client = _gs.Client(credentials=db._credentials, project=db.project)
        else:
            _storage_client = _gs.Client()
        return _storage_client
    except Exception as e:
        logger.warning(f"[REF] Could not init GCS client: {e}")
        return None

def _download_temp(url: str, suffix: str = ".jpg") -> str | None:
    """Download a reference image to a temp file using the GCS client."""
    client = _get_storage_client()
    if not client:
        return None

    try:
        # Extract bucket and blob from https://storage.googleapis.com/BUCKET/BLOB
        if "storage.googleapis.com" in url:
            parts = url.replace("https://storage.googleapis.com/", "").split("/", 1)
            if len(parts) == 2:
                bucket_name, blob_name = parts
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                blob.download_to_filename(tmp.name)
                tmp.close()
                return tmp.name

        # Fallback to requests if it's not a standard GCS URL
        resp = _requests.get(url, timeout=15)
        resp.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        logger.warning(f"[REF] Download failed for {url}: {e}")
        return None


# ─── Pass 2: Verification with Reference Images ─────────────────────────────
def _run_verification_pass(coin_data: dict, img_a, img_b):
    """
    After the initial identification, fetch reference images from the library
    and run a second Gemini pass for verification, grade refinement, and
    error/variety detection.

    Modifies coin_data in-place with any refinements. Returns coin_data.
    """
    denom = coin_data.get("denomination", "")
    year = coin_data.get("year")
    if not denom or not year:
        logger.info("[REF] Skipping verification pass — no denomination/year")
        return coin_data

    refs = _fetch_reference_images(denom, year)
    if not refs:
        logger.info("[REF] No reference images found — skipping verification pass")
        return coin_data

    # Download reference images and upload to Gemini
    ref_uploads = []
    ref_temp_paths = []
    ref_captions = []
    for ref in refs:
        tmp_path = _download_temp(ref["gcs_url"])
        if tmp_path:
            try:
                uploaded = client.files.upload(file=tmp_path)
                ref_uploads.append(uploaded)
                ref_temp_paths.append(tmp_path)
                ref_captions.append(
                    f"{ref['denomination']} {ref['year']} ({ref['side']})"
                )
            except Exception as e:
                logger.warning(f"[REF] Upload to Gemini failed: {e}")
                os.unlink(tmp_path)

    if not ref_uploads:
        logger.info("[REF] Could not upload any reference images — skipping")
        return coin_data

    try:
        # Build reference caption block
        ref_list = "\n".join(
            f"  - Reference Image {i+1}: {cap}"
            for i, cap in enumerate(ref_captions)
        )

        verification_prompt = f"""You are a senior numismatist performing a VERIFICATION PASS.

An AI system has already identified a coin as:
  - Year: {coin_data.get('year')}
  - Country: {coin_data.get('country')}
  - Denomination: {coin_data.get('denomination')}
  - Program/Series: {coin_data.get('program_series')}
  - Theme/Subject: {coin_data.get('theme_subject')}
  - Mint Mark: {coin_data.get('mint_mark')}
  - Grade: {coin_data.get('grade')}
  - Metal: {coin_data.get('metal_content')}

You are given:
  - The user's ACTUAL SCAN (Image A and Image B, same order as Pass 1)
  - {len(ref_uploads)} REFERENCE IMAGES from a verified catalog:
{ref_list}

Your tasks:
1. VERIFY: Compare the user's scan against the reference images. Do they match the stated identification? If the initial ID is WRONG, provide the correct identification.
2. GRADE REFINEMENT: Based on visual comparison with the reference specimens, refine the grade estimate. Note wear patterns, luster, strike quality, and surface marks visible under microscope magnification.
3. ERROR/VARIETY CHECK: Look carefully for die varieties, doubled dies (DDO/DDR), repunched mint marks (RPM), off-center strikes, die cracks, cuds, or any other errors. Compare against the reference images to distinguish genuine errors from normal die characteristics.
4. CONDITION NOTES: Any significant contact marks, cleaning evidence, environmental damage, or toning worth noting.

Return ONLY a valid JSON object:
{{
  "identification_confirmed": bool,
  "corrected_denomination": string or null (only if initial ID was wrong),
  "corrected_year": int or null (only if initial ID was wrong),
  "refined_grade": string (your improved grade estimate, e.g. "VF-30", "MS-63"),
  "errors_detected": [string] (list of any errors/varieties found, empty array if none),
  "condition_notes": string (brief condition assessment),
  "confidence": string ("HIGH", "MEDIUM", or "LOW"),
  "verification_report": string (detailed paragraph summarizing the verification)
}}"""

        from google.genai import types
        contents = [verification_prompt, img_a, img_b] + ref_uploads
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )

        vdata = json.loads(response.text)
        logger.info(f"[REF] Verification pass complete — "
                     f"confirmed={vdata.get('identification_confirmed')}, "
                     f"grade={vdata.get('refined_grade')}, "
                     f"confidence={vdata.get('confidence')}")

        # Apply refinements to coin_data
        if vdata.get("refined_grade"):
            coin_data["grade"] = vdata["refined_grade"]

        # If the initial identification was wrong, correct it
        if not vdata.get("identification_confirmed", True):
            if vdata.get("corrected_denomination"):
                coin_data["denomination"] = vdata["corrected_denomination"]
            if vdata.get("corrected_year"):
                coin_data["year"] = vdata["corrected_year"]

        # Append variety/error info
        errors = vdata.get("errors_detected", [])
        if errors:
            coin_data["variety"] = "; ".join(errors)

        # Enrich the report with verification details
        verification_report = vdata.get("verification_report", "")
        condition_notes = vdata.get("condition_notes", "")
        confidence = vdata.get("confidence", "")

        addendum = []
        if verification_report:
            addendum.append(f"[Verification: {confidence}] {verification_report}")
        if condition_notes:
            addendum.append(f"Condition: {condition_notes}")
        if errors:
            addendum.append(f"Errors/Varieties: {', '.join(errors)}")

        if addendum:
            existing = coin_data.get("report", "")
            coin_data["report"] = existing + "\n\n--- Reference Verification ---\n" + \
                                  "\n".join(addendum)

        coin_data["verification_confidence"] = confidence
        coin_data["reference_images_used"] = len(ref_uploads)

    except Exception as e:
        logger.warning(f"[REF] Verification pass failed (non-fatal): {e}")
    finally:
        # Clean up temp files
        for tmp in ref_temp_paths:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    return coin_data


# ─── Main Identification Entry Point ─────────────────────────────────────────
def run_numista_report(img_path_a, img_path_b):
    """
    Two-pass AI identification pipeline:

    Pass 1: Sends both coin images to Gemini for initial identification
            (denomination, year, grade, metal, mint mark, etc.)

    Pass 2: Fetches 2-3 matching reference images from the Firestore
            reference_library and sends them alongside the user's scan
            for verification, grade refinement, and error/variety detection.
            Falls back gracefully if Firestore or references are unavailable.
    """
    logger.info("[GEMINI] Analyzing Image A (%s) and Image B (%s)", img_path_a, img_path_b)
    
    try:
        # Upload images WITHOUT telling Gemini which is which
        img_a = client.files.upload(file=img_path_a)
        img_b = client.files.upload(file=img_path_b)
        
        # ── PASS 1: Initial Identification ───────────────────────────────────
        prompt = """
        You are a professional numismatist. You are given two coin images: Image A and Image B.
        The user may have scanned them in any order — do NOT assume A is the obverse.

        Your tasks:
        1. Determine which image is the OBVERSE (heads / portrait / date side) and which is the REVERSE (tails / design side).
        2. Identify the coin: Year, Country, Denomination, Program/Series, Theme/Subject, and estimated Grade.
        3. MINT MARK (critical): Look extremely carefully at the obverse image for a small letter mint mark.
           Common locations: below the date, near the bottom of the portrait, just above or below "IN GOD WE TRUST", or along the lower rim.
           US Mint facility codes: P (Philadelphia), D (Denver), S (San Francisco), W (West Point), CC (Carson City), O (New Orleans).
           If you can see any letter in these locations — even faint or partially obscured — report it. If genuinely absent, return "None (P)".
        4. METAL COMPOSITION (critical for value):
           - State whether the coin contains silver. US coins dated before 1965 (dimes, quarters, halves) are 90% silver.
           - Half dollars 1965-1970 are 40% silver.
           - Morgan Dollars, Peace Dollars, Franklin Halves, Walking Liberty Halves, and Mercury Dimes are silver.
           - Modern clad coins (post-1964 quarters, post-1970 halves, all modern dollars) contain NO silver.
           - American Silver Eagles are 99.9% silver.
           - Set "is_silver" to true or false based on this analysis.
           - Set "metal_content" to the precise composition string (e.g. "90% Silver, 10% Copper" or "Clad (Copper-Nickel)").
        5. Provide a 'file_slug' (e.g., 2026_American_Liberty_Half_Dollar_D).
        6. Provide a brief 'report' summarizing the coin's key features and numismatic significance.

        Return ONLY a valid JSON object with these exact keys:
        {
          "obverse_image": "A" or "B",
          "year": int,
          "country": string,
          "denomination": string,
          "program_series": string,
          "theme_subject": string,
          "mint_mark": string,
          "grade": string,
          "is_silver": bool,
          "metal_content": string,
          "file_slug": string,
          "report": string
        }
        """

        from google.genai import types
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[prompt, img_a, img_b],
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        try:
            res_data = json.loads(response.text)
        except Exception as json_err:
            # Some models wrap JSON in markdown fences — strip and retry
            cleaned = response.text.strip().lstrip('`').lstrip('json').lstrip('`').rstrip('`').strip()
            try:
                res_data = json.loads(cleaned)
                logger.info("[GEMINI] JSON parsed after stripping markdown fences")
            except Exception:
                logger.error("[GEMINI] JSON parse failed (%s). Raw response (first 300): %s",
                             json_err, response.text[:300] if response.text else "(empty)")
                res_data = {"file_slug": "detected_coin", "report": response.text, "obverse_image": "A"}


        # Route image paths based on Gemini's side determination
        obverse_is_a = res_data.get("obverse_image", "A").upper() == "A"
        identified_obv_path = img_path_a if obverse_is_a else img_path_b
        identified_rev_path = img_path_b if obverse_is_a else img_path_a
        
        logger.info("[GEMINI] Identified Image %s as OBVERSE", res_data.get('obverse_image', 'A'))

        coin_data = {
            "year": res_data.get("year"),
            "country": res_data.get("country", "Unknown"),
            "denomination": res_data.get("denomination", ""),
            "program_series": res_data.get("program_series", ""),
            "theme_subject": res_data.get("theme_subject", ""),
            "mint_mark": res_data.get("mint_mark", ""),
            "grade": res_data.get("grade", "N/A"),
            "is_silver": res_data.get("is_silver", False),
            "metal_content": res_data.get("metal_content", ""),
            "file_slug": res_data.get("file_slug", "detected_coin"),
            "report": res_data.get("report", "No detailed analysis provided."),
            "source": "Gemini 3 Flash Preview",
            "obverse_image_path": identified_obv_path,
            "reverse_image_path": identified_rev_path,
        }

        # ── PASS 2: Reference Verification ───────────────────────────────────
        logger.info("[GEMINI] Starting reference verification pass...")
        coin_data = _run_verification_pass(coin_data, img_a, img_b)

        ref_count = coin_data.get("reference_images_used", 0)
        confidence = coin_data.get("verification_confidence", "N/A")
        logger.info("[GEMINI] Verification complete — %d reference images, confidence: %s", ref_count, confidence)

        return coin_data

    except Exception as e:
        logger.error("[GEMINI] Analysis failed with exception: %s", e, exc_info=True)
        return None
