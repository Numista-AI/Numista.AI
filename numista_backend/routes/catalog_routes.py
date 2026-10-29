"""
routes/catalog_routes.py
------------------------
U.S. Numismatics Master Catalog API (Plan.v2.1).

  GET   /api/v1/catalog                             public  - browse / filter / search (guest rate-limited)
  GET   /api/v1/catalog/resolve?slug=..             public  - SEO slug -> item
  GET   /api/v1/catalog/{nac_code}                  public  - NAC1 deep link (+ canonical slug)
  GET   /api/v1/catalog/{nac_code}/image-download   gated   - blocks guest image download (403)
  POST  /api/v1/collection/catalog-add              authed  - transactional, kind-routed add (REQ_031 + tier gate)
  PATCH /api/v1/collection/catalog-photo-toggle     authed  - toggle personal vs stock catalog photo (Founder Q3)

The public router lives under its own prefix so main.py's public-path allowlist never
exposes the authenticated write routes.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from google.cloud import firestore

from catalog_models import CollectionAddRequest, PhotoToggleRequest
from catalog_nac1 import validate_nac1
from catalog_service import (
    CatalogError,
    add_catalog_item_in_txn,
    check_guest_search_rate_limit,
    filter_catalog,
    find_by_slug,
    load_catalog,
    toggle_personal_photo_in_txn,
    verify_image_download_allowed,
)
from routes.deps import db, get_current_user, verify_firebase_bearer_token

public_router = APIRouter(prefix="/api/v1/catalog", tags=["US Numismatics Catalog (public)"])
write_router = APIRouter(prefix="/api/v1/collection", tags=["US Numismatics Catalog (collection add)"])


def _items():
    return load_catalog(db)


def _optional_user(request: Request) -> Optional[dict]:
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        return verify_firebase_bearer_token(request)
    return None


@public_router.get("")
def browse_catalog(
    request: Request,
    kind: Optional[str] = Query(None, pattern="^(CN|BN|MD|TK|ST)$"),
    cc: Optional[str] = Query(None, pattern="^(US|CO|PF|CS|FS)$"),
    era: Optional[str] = Query(None),
    facility: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    max_year: Optional[int] = Query(None, ge=1776, le=2026),
    q: Optional[str] = Query(None, max_length=100),
):
    if q and q.strip():
        user = _optional_user(request)
        if not user:
            client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "guest")
            try:
                check_guest_search_rate_limit(client_ip)
            except CatalogError as e:
                raise HTTPException(status_code=e.status_code, detail={"error": e.code, **e.extra})
    items = filter_catalog(_items(), kind=kind, era=era, facility=facility, state=state, max_year=max_year, q=q, cc=cc)
    return {"count": len(items), "items": items}


@public_router.get("/resolve")
def resolve_slug(slug: str = Query(..., max_length=200)):
    item = find_by_slug(_items(), slug)
    if not item:
        raise HTTPException(status_code=404, detail="CATALOG_ITEM_NOT_FOUND")
    return item


@public_router.get("/{nac_code}/image-download")
def download_catalog_image(nac_code: str, request: Request):
    user = _optional_user(request)
    try:
        verify_image_download_allowed(user, nac_code)
    except CatalogError as e:
        raise HTTPException(status_code=e.status_code, detail={"error": e.code, **e.extra})
    for it in _items():
        if it.get("nac_code") == nac_code or nac_code in (it.get("nac_aliases") or []):
            return {
                "nac_code": it["nac_code"],
                "obverse_image_url": it.get("obverse_image_url"),
                "reverse_image_url": it.get("reverse_image_url"),
                "image_license_type": it.get("image_license_type"),
                "image_source_credit": it.get("image_source_credit"),
            }
    raise HTTPException(status_code=404, detail="CATALOG_ITEM_NOT_FOUND")


@public_router.get("/{nac_code}")
def get_by_nac(nac_code: str):
    if not validate_nac1(nac_code):
        raise HTTPException(status_code=400, detail="INVALID_NAC1_CHECKSUM")
    for it in _items():
        if it.get("nac_code") == nac_code or nac_code in (it.get("nac_aliases") or []):
            return {"item": it, "canonical_slug": it.get("seo_slug"), "canonical_nac_code": it["nac_code"]}
    raise HTTPException(status_code=404, detail="CATALOG_ITEM_NOT_FOUND")


def _count_fn(uid: str):
    def _count(tx, collection: str) -> int:
        agg = db.collection("users").document(uid).collection(collection).count()
        return agg.get(transaction=tx)[0][0].value
    return _count


@firestore.transactional
def _run_add(tx, uid, nac_code, tier_limit, new_specimen):
    return add_catalog_item_in_txn(tx, db, uid, nac_code, tier_limit, _count_fn(uid), new_specimen)


@firestore.transactional
def _run_photo_toggle(tx, uid, collection, doc_id, use_personal_photo):
    return toggle_personal_photo_in_txn(tx, db, uid, collection, doc_id, use_personal_photo)


@write_router.post("/catalog-add")
def catalog_add(body: CollectionAddRequest, user: dict = Depends(get_current_user)):
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Authentication token missing or invalid")

    # Server-side entitlement (never trusted from the client)
    from tier_gatekeeper import TIER_COIN_LIMITS, get_user_profile, get_user_tier
    profile = get_user_profile(uid)
    tier = get_user_tier(profile)
    limit = float("inf") if (tier == "power_user" or profile.get("power_user") is True) \
        else TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])

    try:
        result = _run_add(db.transaction(), uid, body.nac_code, limit, body.new_specimen)
    except CatalogError as e:
        raise HTTPException(status_code=e.status_code, detail={"error": e.code, **e.extra})
    return JSONResponse(status_code=201 if result["created"] else 200, content={
        "created": result["created"],
        "message": "Added to collection" if result["created"] else "Already in Collection",
        "collection": result["collection"],
        "doc_id": result["doc_id"],
    })


@write_router.patch("/catalog-photo-toggle")
def catalog_photo_toggle(body: PhotoToggleRequest, user: dict = Depends(get_current_user)):
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Authentication token missing or invalid")
    try:
        result = _run_photo_toggle(db.transaction(), uid, body.collection, body.doc_id, body.use_personal_photo)
    except CatalogError as e:
        raise HTTPException(status_code=e.status_code, detail={"error": e.code, **e.extra})
    return result
