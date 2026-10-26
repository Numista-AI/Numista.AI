"""
PCGS Certification Lookup Routes
Shields web clients from CORS restrictions and queries api.pcgs.com using server-managed tokens.
"""

import requests as _requests
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from routes.deps import db, logger, verify_firebase_bearer_token, get_current_user

router = APIRouter(prefix="/api/pcgs", tags=["PCGS Certification Lookup"])

_PCGS_API_BASE = "https://api.pcgs.com/publicapi"

def _get_pcgs_token() -> Optional[str]:
    """Reads the PCGS bearer token from environment variable PCGS_BEARER_TOKEN or Firestore config/pcgs -> bearerToken."""
    import os
    token = os.environ.get("PCGS_BEARER_TOKEN") or os.environ.get("PCGS_TOKEN")
    if token:
        return token.strip()
    try:
        doc = db.collection("config").document("pcgs").get()
        token = doc.to_dict().get("bearerToken") if doc.exists else None
        return token or None
    except Exception as e:
        logger.error(f"PCGS: could not read token from Firestore: {e}")
        return None

@router.get("/cert/{cert_no}")
async def pcgs_cert_lookup(cert_no: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Looks up a PCGS certification number via the PCGS Public API.
    Endpoint: GET /api/pcgs/cert/{certNo}
    Requires valid Firebase JWT. PCGS pre-check: Option A confirmed (Flutter proxy in use).
    """
    if not cert_no.isdigit() or not (6 <= len(cert_no) <= 9):
        raise HTTPException(status_code=400, detail="cert_no must be 6-9 digits.")

    token = _get_pcgs_token()
    if not token:
        raise HTTPException(
            status_code=503,
            detail="PCGS bearer token not configured. Add PCGS_BEARER_TOKEN environment variable or bearerToken in Firestore config/pcgs."
        )

    url = f"{_PCGS_API_BASE}/coindetail/GetCoinFactsByCertNo/{cert_no}"
    params = {"retrieveAllData": "true"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        resp = _requests.get(url, params=params, headers=headers, timeout=15)
    except _requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="PCGS API timed out.")
    except Exception as e:
        logger.error(f"PCGS API request failed for cert {cert_no}: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with PCGS API.")

    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="PCGS bearer token is invalid or expired. Generate a new one at pcgs.com/publicapi/documentation.")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"PCGS API returned HTTP {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="PCGS API returned invalid JSON.")

    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Unexpected response structure from PCGS API.")

    is_valid = data.get("IsValidRequest")
    server_msg = str(data.get("ServerMessage") or "").strip()
    logger.info(f"PCGS cert {cert_no} response: IsValidRequest={is_valid}, ServerMessage='{server_msg}'")

    if is_valid is False:
        msg_lower = server_msg.lower()
        if any(term in msg_lower for term in ("quota", "limit", "rate", "auth", "token", "unauthorized", "exceeded", "unavailable")):
            raise HTTPException(
                status_code=503,
                detail={"error": "quota", "message": "PCGS lookup unavailable right now. Try again later or type the coin in instead."}
            )
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": f"Cert not found: {server_msg}"}
        )

    # Normalize coinDetail for frontend
    coin_detail = None
    if isinstance(data.get("CoinDetails"), list) and data["CoinDetails"]:
        coin_detail = data["CoinDetails"][0]
    elif isinstance(data.get("CoinDetail"), dict):
        coin_detail = data["CoinDetail"]
    elif isinstance(data.get("coinDetail"), dict):
        coin_detail = data["coinDetail"]
    else:
        coin_detail = data

    return {
        **data,
        "found": True,
        "coinDetail": coin_detail,
        "CoinDetail": coin_detail,
    }
