"""
routes/catalog_routes.py
------------------------
U.S. Numismatics Master Catalog API (Plan.v2).

  GET  /api/v1/catalog                  public  - browse / filter / search
  GET  /api/v1/catalog/resolve?slug=..  public  - SEO slug -> item
  GET  /api/v1/catalog/{nac_code}       public  - NAC1 deep link (+ canonical slug)
  POST /api/v1/collection/catalog-add   authed  - transactional, kind-routed add (REQ_031 + tier gate)

The public router lives under its own prefix so main.py's public-path allowlist never
exposes the authenticated write route.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from google.cloud import firestore

from catalog_models import CollectionAddRequest
from catalog_nac1 import validate_nac1
from catalog_service import (
    CatalogError,
    add_catalog_item_in_txn,
    filter_catalog,
    find_by_slug,
    load_catalog,
)
from routes.deps import db, get_current_user

public_router = APIRouter(prefix="/api/v1/catalog", tags=["US Numismatics Catalog (public)"])
write_router = APIRouter(prefix="/api/v1/collection", tags=["US Numismatics Catalog (collection add)"])


def _items():
    return load_catalog(db)


@public_router.get("")
def browse_catalog(
    kind: Optional[str] = Query(None, pattern="^(CN|BN|MD|TK|ST)$"),
    era: Optional[str] = Query(None),
    facility: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    max_year: Optional[int] = Query(None, ge=1776, le=2026),
    q: Optional[str] = Query(None, max_length=100),
):
    items = filter_catalog(_items(), kind, era, facility, state, max_year, q)
    return {"count": len(items), "items": items}


@public_router.get("/resolve")
def resolve_slug(slug: str = Query(..., max_length=200)):
    item = find_by_slug(_items(), slug)
    if not item:
        raise HTTPException(status_code=404, detail="CATALOG_ITEM_NOT_FOUND")
    return item


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
