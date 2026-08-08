"""
Affiliate Links, EPN Monetization, and Public Wishlist Reservation Routes
"""

import secrets
import logging
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Request
from google.cloud import firestore

from schemas.affiliate_schemas import ShareWishlistRequest, ReserveItemRequest, UnreserveItemRequest
from services.common import normalize_colloquial_header, safe_get_str
from routes.deps import db, logger, get_current_user

router = APIRouter(prefix="/api/v1", tags=["Affiliate & Shareable Public Wishlists"])

EPN_CAMPAIGN_ID = "5339148752"
EPN_ROTATION_ID = "711-53200-19255-0"

# In-memory IP rate limiter: IP -> list of timestamps
_RATE_LIMIT_STORE: Dict[str, List[datetime]] = {}

# High-risk key dates requiring mandatory (PCGS, NGC, CAC) certification filters regardless of price
HIGH_RISK_KEY_DATES = [
    "1909-s vdb", "1916-d", "1932-d", "1893-s", "1877",
    "1911-d", "classic head", "st. gaudens"
]

def _extract_client_ip(request: Request) -> str:
    """Extract true client IP behind Cloud Run load balancers via X-Forwarded-For header."""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def _check_rate_limit(client_ip: str, limit: int = 10, window_seconds: int = 60):
    """Enforce rate limiting per client IP."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    timestamps = _RATE_LIMIT_STORE.get(client_ip, [])
    valid_timestamps = [t for t in timestamps if t > cutoff]
    
    if len(valid_timestamps) >= limit:
        raise HTTPException(status_code=429, detail="Too many reservation requests. Please try again shortly.")
    
    valid_timestamps.append(now)
    _RATE_LIMIT_STORE[client_ip] = valid_timestamps

# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/wishlist/share")
async def share_wishlist(req: ShareWishlistRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Generate or sync a 12-character public wishlist share document with 90-day expiry."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    token = secrets.token_urlsafe(9)[:12]
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=90)

    items_map = {}
    for item in req.items:
        cid = item.get("coin_id") or item.get("id") or secrets.token_hex(8)
        items_map[cid] = {
            "coin_id": cid,
            "title": item.get("title") or item.get("Title") or "Coin Item",
            "estimated_value": float(item.get("estimated_value") or item.get("value") or 0.0),
            "type": item.get("type", "coin"),
            "image_url": item.get("image_url"),
            "notes": item.get("notes")
        }

    doc_data = {
        "token": token,
        "owner_uid": user_id,
        "collector_display_name": req.collector_display_name or "Collector",
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "last_synced_at": now.isoformat(),
        "items": items_map,
        "reserved_items": {}
    }

    try:
        db.collection("public_wishlists").document(token).set(doc_data)
        return {
            "status": "success",
            "token": token,
            "share_url": f"https://numista.ai/#/wishlist/{token}",
            "expires_at": expires_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to create public wishlist document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create share link: {e}")


@router.post("/wishlist/reserve")
async def reserve_item(req: ReserveItemRequest, request: Request):
    """
    Atomic transaction endpoint for unauthenticated gift buyers to reserve an item.
    Enforces X-Forwarded-For IP rate-limiting and lazy 48-hour timeout evaluation.
    """
    client_ip = _extract_client_ip(request)
    _check_rate_limit(client_ip)

    # Sanitize reserved_by string
    clean_name = req.reserved_by.strip()[:50]
    if not clean_name:
        raise HTTPException(status_code=400, detail="Reservation name cannot be empty")

    doc_ref = db.collection("public_wishlists").document(req.token)

    @firestore.transactional
    def _do_reserve(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists:
            raise HTTPException(status_code=444, detail="Wishlist link not found or expired")

        data = snapshot.to_dict() or {}
        items = data.get("items") or {}
        if req.coin_id not in items:
            raise HTTPException(status_code=404, detail="Item not found on this wishlist")

        reserved = data.get("reserved_items") or {}
        now = datetime.now(timezone.utc)
        
        # Check lazy 48-hour expiration on existing hold
        existing = reserved.get(req.coin_id)
        if existing:
            r_at_str = existing.get("reserved_at")
            if r_at_str:
                try:
                    r_at = datetime.fromisoformat(r_at_str)
                    if now < r_at + timedelta(hours=48):
                        raise HTTPException(status_code=409, detail=f"Item already reserved by {existing.get('reserved_by', 'another relative')}")
                except (ValueError, TypeError):
                    pass

        # Perform atomic reservation
        reserved[req.coin_id] = {
            "reserved_by": clean_name,
            "reserved_at": now.isoformat()
        }

        transaction.update(ref, {"reserved_items": reserved})
        return {
            "status": "success",
            "token": req.token,
            "coin_id": req.coin_id,
            "reserved_by": clean_name,
            "reserved_at": now.isoformat()
        }

    transaction = db.transaction()
    return _do_reserve(transaction, doc_ref)


@router.delete("/wishlist/reserve")
async def unreserve_item(req: UnreserveItemRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Owner un-reserve endpoint allowing collectors to manually clear locked items."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    doc_ref = db.collection("public_wishlists").document(req.token)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    data = doc.to_dict() or {}
    if data.get("owner_uid") != user_id:
        raise HTTPException(status_code=403, detail="Only the wishlist owner can clear reservations")

    reserved = data.get("reserved_items") or {}
    if req.coin_id in reserved:
        del reserved[req.coin_id]
        doc_ref.update({"reserved_items": reserved})

    return {"status": "success", "token": req.token, "coin_id": req.coin_id, "message": "Reservation cleared"}


@router.get("/affiliate/search_url")
async def get_affiliate_search_url(
    token: str,
    title: str,
    estimated_value: float = 0.0,
    item_type: str = "coin"
):
    """
    Generates EPN affiliate search URL with boolean safety filters and customid tracking.
    """
    clean_title = title.strip()
    lower_title = clean_title.lower()

    # Check key date override
    is_key_date = any(kd in lower_title for kd in HIGH_RISK_KEY_DATES)

    # Build boolean query string
    if item_type == "currency":
        query_suffix = " (PMG, 'PCGS Banknote')" if (estimated_value >= 200.0 or is_key_date) else ""
    else:
        query_suffix = " (PCGS, NGC, CAC)" if (estimated_value >= 200.0 or is_key_date) else ""

    full_query = f"{clean_title}{query_suffix}"
    encoded_query = urllib.parse.quote_plus(full_query)

    custom_id = f"numista_wishlist_{token}"
    affiliate_url = (
        f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}"
        f"&campid={EPN_CAMPAIGN_ID}&mkrid={EPN_ROTATION_ID}&customid={custom_id}"
    )

    return {
        "status": "success",
        "title": clean_title,
        "query": full_query,
        "affiliate_url": affiliate_url,
        "is_certified_filtered": bool(query_suffix)
    }
