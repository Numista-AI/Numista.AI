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

from routes.deps import logger, get_current_user, db

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

    # 3. CAC Lookup (CAC has no public cert lookup API; fall back to manual entry with cert # prefilled)
    if detected_grader == "CAC":
        return CertLookupResponse(
            grader="CAC",
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
