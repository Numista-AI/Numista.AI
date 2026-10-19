"""
routes/cert_routes.py
---------------------
Unified Certification Lookup Routes for PCGS, NGC, and CAC.

Grader Lookup Documentation:
- PCGS:
    Web lookup: https://www.pcgs.com/cert/{cert_num}
    API endpoint: https://api.pcgs.com/publicapi/coindetail/GetCoinFactsByCertNo/{cert_num}
    Method: Authenticated API call using server-managed bearer token.
- NGC:
    Web lookup: https://www.ngccoin.com/certlookup/{cert_num}/
    API status: No public JSON API available (direct programmatic requests blocked by Cloudflare with 403).
    Method: Documented 'no public API, fall back to manual entry with cert # prefilled'.
- CAC:
    Web lookup: https://www.cacgrading.com/cert-verify/{cert_num} or https://www.caccoin.com/cert-lookup/
    API status: CAC does not have a public cert lookup API.
    Method: Always fall back to manual entry with cert # prefilled and grader='CAC'.

Auto-Detection Rules:
- CAC: Starts with 'CAC' (e.g. CAC12345, CACG12345) or user selects manually.
- NGC: Typically 7 digits (e.g. 1234567 or 1234567-001).
- PCGS: Typically 8 digits (numeric only, e.g. 53652580, or barcode with slash 986403.70/53652580).
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import requests as _requests
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends

from routes.deps import logger, get_current_user, db, MODEL_FLASH

# google-genai SDK — Vertex AI + ADC (no API key). Patchable at module level for tests.
from google import genai as _genai
from google.genai import types as _genai_types


router = APIRouter(prefix="/api", tags=["Certification Lookup"])

_PCGS_API_BASE = "https://api.pcgs.com/publicapi"

# In-memory user rate limiter: user_id -> list of timestamps (10/min)
_CERT_RATE_LIMIT_STORE: Dict[str, List[datetime]] = {}

def _check_cert_rate_limit(user_key: str, limit: int = 10, window_seconds: int = 60):
    """Enforce rate limiting: max 10 calls per minute per user."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    timestamps = _CERT_RATE_LIMIT_STORE.get(user_key, [])
    valid_timestamps = [t for t in timestamps if t > cutoff]
    if len(valid_timestamps) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded: max 10 cert lookups per minute."
        )
    valid_timestamps.append(now)
    _CERT_RATE_LIMIT_STORE[user_key] = valid_timestamps

def _get_pcgs_token() -> Optional[str]:
    """Reads PCGS bearer token from environment variable or Firestore config/pcgs."""
    import os
    token = os.environ.get("PCGS_BEARER_TOKEN") or os.environ.get("PCGS_TOKEN")
    if token:
        return token.strip()
    try:
        doc = db.collection("config").document("pcgs").get()
        token = doc.to_dict().get("bearerToken") if doc.exists else None
        return token or None
    except Exception as e:
        logger.error(f"cert_routes: could not read PCGS token from Firestore: {e}")
        return None

def auto_detect_grader(cert_num: str) -> str:
    """Auto-detects grader from cert number format."""
    clean = cert_num.strip().upper()
    if clean.startswith("CACG"):
        return "CACG"
    if clean.startswith("CAC"):
        return "CAC"
    # Extract digits
    if "/" in clean:
        parts = clean.split("/")
        digits = re.sub(r"\D", "", parts[-1])
    elif "-" in clean:
        parts = clean.split("-")
        digits = re.sub(r"\D", "", parts[0])
    else:
        digits = re.sub(r"\D", "", clean)

    if len(digits) == 7:
        return "NGC"
    if len(digits) == 8:
        return "PCGS"
    # Default to PCGS
    return "PCGS"

def clean_cert_number(cert_num: str) -> str:
    """Extracts the canonical cert number from raw input (e.g. handling slab slash)."""
    raw = cert_num.strip()
    if "/" in raw:
        parts = raw.split("/")
        return parts[-1].strip()
    return raw

class CertLookupRequest(BaseModel):
    cert_num: str
    grader: Optional[str] = None

class CertLookupResponse(BaseModel):
    grader: str
    cert_num: str
    coin_name: Optional[str] = None
    year: Optional[str] = None
    mint: Optional[str] = None
    grade: Optional[str] = None
    denomination: Optional[str] = None
    found: bool
    source: str  # 'api' | 'scrape' | 'manual_fallback'

@router.post("/cert_lookup", response_model=CertLookupResponse)
async def cert_lookup(
    req: CertLookupRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Unified graded coin cert lookup endpoint for PCGS, NGC, and CAC.
    Requires authentication. Rate limited to 10 req/min per user.
    Never writes to any collection.
    """
    user_key = current_user.get("uid") or current_user.get("user_id") or current_user.get("email") or "anon_user"
    _check_cert_rate_limit(user_key)

    raw_cert = (req.cert_num or "").strip()
    if not raw_cert:
        raise HTTPException(status_code=400, detail="cert_num must not be empty.")

    # Determine grader
    grader_input = (req.grader or "").strip()
    if not grader_input:
        detected_grader = auto_detect_grader(raw_cert)
    else:
        g_upper = grader_input.upper()
        if "PCGS" in g_upper:
            detected_grader = "PCGS"
        elif "NGC" in g_upper:
            detected_grader = "NGC"
        elif "CACG" in g_upper:
            detected_grader = "CACG"
        elif "CAC" in g_upper:
            detected_grader = "CAC"
        else:
            detected_grader = g_upper

    clean_cert = clean_cert_number(raw_cert)

    # 1. PCGS Lookup
    if detected_grader == "PCGS":
        token = _get_pcgs_token()
        if token:
            digits_only = re.sub(r"\D", "", clean_cert)
            url = f"{_PCGS_API_BASE}/coindetail/GetCoinFactsByCertNo/{digits_only}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
            try:
                resp = _requests.get(url, params={"retrieveAllData": "true"}, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict) and data.get("IsValidRequest") is True:
                        coin_detail = data.get("CoinDetail")
                        if isinstance(coin_detail, list) and coin_detail:
                            coin_detail = coin_detail[0]
                        if isinstance(coin_detail, dict):
                            year_val = coin_detail.get("Year")
                            return CertLookupResponse(
                                grader="PCGS",
                                cert_num=clean_cert,
                                coin_name=coin_detail.get("FullName") or coin_detail.get("Name"),
                                year=str(year_val) if year_val else None,
                                mint=coin_detail.get("MintMark") or "",
                                grade=coin_detail.get("Grade") or "",
                                denomination=coin_detail.get("Denomination") or "",
                                found=True,
                                source="api",
                            )
            except Exception as e:
                logger.warning(f"PCGS cert lookup failed for {clean_cert}: {e}")

        # PCGS not found or API failed / token missing -> fallback
        return CertLookupResponse(
            grader="PCGS",
            cert_num=clean_cert,
            coin_name=None,
            year=None,
            mint=None,
            grade=None,
            denomination=None,
            found=False,
            source="manual_fallback",
        )

    # 2. NGC Lookup (No public API; fall back to manual entry with cert # prefilled)
    if detected_grader == "NGC":
        return CertLookupResponse(
            grader="NGC",
            cert_num=clean_cert,
            coin_name=None,
            year=None,
            mint=None,
            grade=None,
            denomination=None,
            found=False,
            source="manual_fallback",
        )

    # 3. CAC / CACG Lookup (No public cert lookup API; fall back to manual entry with cert # prefilled)
    if detected_grader in ("CAC", "CACG"):
        return CertLookupResponse(
            grader=detected_grader,
            cert_num=clean_cert,
            coin_name=None,
            year=None,
            mint=None,
            grade=None,
            denomination=None,
            found=False,
            source="manual_fallback",
        )

    # Catch-all fallback
    return CertLookupResponse(
        grader=detected_grader,
        cert_num=clean_cert,
        coin_name=None,
        year=None,
        mint=None,
        grade=None,
        denomination=None,
        found=False,
        source="manual_fallback",
    )


# ── Dup-Add / Save Endpoints (NET-087 / Task 3) ──────────────────────────────

class CertExistsResponse(BaseModel):
    exists: bool
    cert_num: str
    existing_coin_id: Optional[str] = None


class CertSaveRequest(BaseModel):
    cert_num: str
    grader: Optional[str] = None
    allow_duplicate: bool = False
    coin_data: Optional[Dict[str, Any]] = None


class CertSaveResponse(BaseModel):
    status: str
    coin_id: Optional[str] = None
    duplicate_allowed: bool = False
    message: Optional[str] = None


@router.get("/cert_exists", response_model=CertExistsResponse)
def check_cert_exists(
    cert_num: str,
    user: dict = Depends(get_current_user),
):
    """
    Checks if a coin with the given cert_num already exists in user's collection.
    """
    if not cert_num or not cert_num.strip():
        raise HTTPException(status_code=400, detail="cert_num is required")

    clean_cert = cert_num.strip()
    user_email = (user.get("email") or user.get("uid") or "").strip().lower()
    if not user_email:
        raise HTTPException(status_code=401, detail="User identification missing")

    existing_id = None
    try:
        coins_ref = db.collection("users").document(user_email).collection("coins")
        matches = list(coins_ref.where("certNo", "==", clean_cert).limit(1).stream())
        if not matches:
            matches = list(coins_ref.where("cert_num", "==", clean_cert).limit(1).stream())
        if matches:
            existing_id = matches[0].id
    except Exception as e:
        logger.warning(f"Error checking cert existence for {clean_cert}: {e}")

    return CertExistsResponse(
        exists=bool(existing_id),
        cert_num=clean_cert,
        existing_coin_id=existing_id,
    )


@router.post("/cert_save", response_model=CertSaveResponse)
def cert_save(
    req: CertSaveRequest,
    user: dict = Depends(get_current_user),
):
    """
    Checks whether a cert already exists in the user's collection.
    Returns HTTP 409 if the cert exists and allow_duplicate is False.
    Returns HTTP 200 (status='clear') otherwise.

    NOTE: This endpoint does NOT write to Firestore. The Flutter client is the
    single writer — it calls this endpoint first, then does its own
    FirebaseFirestore.instance.collection(coinsPath).add(coinDoc) on 200.
    This prevents double-write bugs. (FAIL 1 fix: removed backend Firestore write.
    FAIL 2 fix: removed eric_emails safeguard block — never fake data.)
    """
    if not req.cert_num or not req.cert_num.strip():
        raise HTTPException(status_code=400, detail="cert_num is required")

    clean_cert = req.cert_num.strip()
    user_email = (user.get("email") or user.get("uid") or "").strip().lower()
    if not user_email:
        raise HTTPException(status_code=401, detail="User identification missing")

    # Check for existing duplicate
    existing_id = None
    try:
        coins_ref = db.collection("users").document(user_email).collection("coins")
        matches = list(coins_ref.where("certNo", "==", clean_cert).limit(1).stream())
        if not matches:
            matches = list(coins_ref.where("cert_num", "==", clean_cert).limit(1).stream())
        if matches:
            existing_id = matches[0].id
    except Exception as e:
        logger.warning(f"Error checking duplicate in cert_save for {clean_cert}: {e}")

    if existing_id and not req.allow_duplicate:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "cert_duplicate",
                "cert_num": clean_cert,
                "existing_coin_id": existing_id,
                "message": "This cert # is already in your collection.",
            }
        )

    # Return clear — Flutter does the single Firestore write.
    return CertSaveResponse(
        status="clear",
        coin_id=None,
        duplicate_allowed=req.allow_duplicate,
        message="OK to save",
    )


# ── NET-093: Slab Photo Cert # Scanner ───────────────────────────────────────

class ScanCertResponse(BaseModel):
    cert_number: Optional[str] = None
    grader: Optional[str] = None   # "PCGS" | "NGC" | "CAC" | null
    confidence: str = "LOW"        # "HIGH" | "MEDIUM" | "LOW"
    message: str = ""



from fastapi import UploadFile, File as FastAPIFile
import base64, os, json


# Vertex AI backend — uses ADC, no API key. Match resolution chain from main.py:312.
# Never default to "numista-qc" — that project does not have the service account.
_SCAN_PROJECT_ID = (
    os.environ.get("FIREBASE_PROJECT_ID")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or "studio-9101802118-8c9a8"
)
_SCAN_LOCATION = os.environ.get("GEMINI_LOCATION", "global")


def extract_cert_from_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Shared OCR function for grading slab photos to extract cert number and grader.
    Used by both /api/scan_cert_number_upload and /api/identify_coin_photo.
    Returns a dict with keys: cert_number, grader, confidence, message.
    """
    model_name = model or MODEL_FLASH
    try:
        _scan_client = _genai.Client(
            vertexai=True,
            project=_SCAN_PROJECT_ID,
            location=_SCAN_LOCATION,
        )

        prompt = (
            "You are examining an image of a certified coin grading slab label. "
            "Your ONLY job is to extract the certification number and identify the grading company.\n\n"
            "Grading companies and their cert # formats:\n"
            "- PCGS: 8-digit number (e.g. 53652580). Label says 'PCGS' or 'Professional Coin Grading Service'.\n"
            "- NGC: 7-digit number, optionally with a dash suffix (e.g. 8321797 or 8321797-003). "
            "  Label says 'NGC' or 'Numismatic Guaranty Company'.\n"
            "- CAC: starts with 'CAC' (e.g. CAC12345 or CACG12345). "
            "  Label says 'CAC' or 'Certified Acceptance Corporation'.\n\n"
            "Return ONLY valid JSON, no markdown:\n"
            '{"cert_number": "<number or null>", "grader": "<PCGS|NGC|CAC|null>", '
            '"confidence": "<HIGH|MEDIUM|LOW>"}'
        )

        image_part = _genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = _scan_client.models.generate_content(
            model=model_name,
            contents=[prompt, image_part],
            config=_genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=128,
            ),
        )
        text = response.text.strip()
        data = json.loads(text)
        cert_num = (data.get("cert_number") or "").strip() or None
        grader = (data.get("grader") or "").strip().upper() or None
        if grader not in ("PCGS", "NGC", "CAC", "CACG"):
            grader = None
        confidence = data.get("confidence", "LOW").upper()
        if confidence not in ("HIGH", "MEDIUM", "LOW"):
            confidence = "LOW"

        if not cert_num:
            return {
                "cert_number": None,
                "grader": None,
                "confidence": "LOW",
                "message": "No cert number found in image.",
            }

        return {
            "cert_number": cert_num,
            "grader": grader,
            "confidence": confidence,
            "message": "OK",
        }
    except Exception as e:
        logger.warning(f"extract_cert_from_image failed: {e}")
        return {
            "cert_number": None,
            "grader": None,
            "confidence": "LOW",
            "message": "Scan failed — please enter cert # manually.",
        }


@router.post("/scan_cert_number_upload", response_model=ScanCertResponse)
async def scan_cert_number_upload(
    file: UploadFile = FastAPIFile(...),
    user: dict = Depends(get_current_user),
):
    """
    NET-093: OCR a grading slab photo to extract the cert number and grader.
    Accepts multipart/form-data with field 'file' (JPEG/PNG/WEBP).
    Uses Gemini Vision (gemini-3.8-flash) via Vertex AI + ADC.
    Returns {cert_number, grader, confidence, message}.

    Grader detection rules (same as auto-detect in Flutter):
    - PCGS: 8 numeric digits (e.g. 53652580) or barcode slash format
    - NGC: 7 digits, optionally with dash suffix (e.g. 8321797-003)
    - CAC: starts with 'CAC' (e.g. CAC12345) or label says 'CAC'
    """
    _check_cert_rate_limit(user.get("uid") or user.get("email", "anon"), limit=5)

    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB).")

    # Detect MIME type
    mime = file.content_type or "image/jpeg"

    res = extract_cert_from_image(raw, mime_type=mime)
    return ScanCertResponse(**res)

