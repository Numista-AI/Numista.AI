"""
routes/greysheet_admin_routes.py
---------------------------------
Admin-only routes for the Greysheet Known Errors feature.

  POST /api/greysheet/admin/seed-node-map       — re-indexes denomination→node_id mapping
  POST /api/greysheet/admin/allowlist/promote   — promotes a keyword_candidate GSID to the
                                                   human-confirmed allow-list

Both routes require the custom claim 'admin': True (require_admin_user dependency).
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from routes.deps import db, require_admin_user
from services.greysheet_error_service import GreysheetErrorService

logger = logging.getLogger("greysheet_admin_routes")
router = APIRouter(prefix="/api/greysheet/admin", tags=["greysheet-admin"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class PromoteRequest(BaseModel):
    gsid: int
    error_type_code: str
    category: str


class SeedNodeMapResponse(BaseModel):
    status: str
    denominations_indexed: int


class PromoteResponse(BaseModel):
    status: str
    gsid: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/seed-node-map", response_model=SeedNodeMapResponse)
async def seed_node_map(
    _user: Dict[str, Any] = Depends(require_admin_user),
) -> SeedNodeMapResponse:
    """
    Triggers a full re-index of the Greysheet denomination → node_id mapping.
    Writes the result to greysheet_cache/node_map.
    Subsequent /known-errors list requests read from this cache — no live crawl.

    Only the admin-authed Cloud Run service account may call this.
    """
    svc = GreysheetErrorService(db=db)
    result = await svc.admin_seed_node_map()
    logger.info(
        f"[greysheet_admin_routes] Node map seeded by admin {_user.get('email')}: "
        f"{result['denominations_indexed']} denominations indexed"
    )
    return SeedNodeMapResponse(
        status=result.get("status", "ok"),
        denominations_indexed=result.get("denominations_indexed", 0),
    )


@router.post("/allowlist/promote", response_model=PromoteResponse)
async def promote_to_allowlist(
    body: PromoteRequest,
    _user: Dict[str, Any] = Depends(require_admin_user),
) -> PromoteResponse:
    """
    Promotes a keyword_candidate GSID to the human-confirmed allow-list.
    Writes to config/greysheet_error_gsid_allowlist (Cloud Run service account).
    Next cache TTL expiry will reclassify matching entries as is_confirmed=true.

    Only the admin-authed Cloud Run service account may call this.
    """
    svc = GreysheetErrorService(db=db)
    svc.admin_promote_to_allowlist(
        gsid=body.gsid,
        error_type_code=body.error_type_code,
        category=body.category,
    )
    logger.info(
        f"[greysheet_admin_routes] GSID {body.gsid} promoted to allowlist "
        f"by admin {_user.get('email')} (category={body.category})"
    )
    return PromoteResponse(status="ok", gsid=body.gsid)
