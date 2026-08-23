"""
routes/greysheet_error_routes.py
---------------------------------
Public (authenticated) routes for the Greysheet Known Errors feature.

  GET  /api/greysheet/known-errors          — list of classified error entries (no prices)
  GET  /api/greysheet/known-errors/{gsid}/price — lazy price for a single GSID (on user expand)

Both routes require a valid Firebase ID token.
No user data (UID, coin ID, purchase price) is sent to Greysheet.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from routes.deps import db, get_current_user
from services.greysheet_error_service import GreysheetErrorService

logger = logging.getLogger("greysheet_error_routes")
router = APIRouter(prefix="/api/greysheet", tags=["greysheet-errors"])

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------
class GsErrorEntryResponse(BaseModel):
    gsid: int
    name: str
    classification_source: str   # "allowlist" | "keyword_candidate"
    is_confirmed: bool
    category_hint: Optional[str] = None


class GsLazyPriceResponse(BaseModel):
    gsid: int
    bid_low: Optional[float] = None
    ask_high: Optional[float] = None
    grade_count: int = 0
    attribution: str = "CPG® Data"
    available: bool = True   # False when budget exhausted or call fails


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/known-errors", response_model=List[GsErrorEntryResponse])
async def get_known_errors(
    denomination_norm: str = Query(..., description="Normalized denomination (e.g. 'cent', 'quarter')"),
    year: int = Query(..., description="Coin year (integer)"),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> List[GsErrorEntryResponse]:
    """
    Returns classified Greysheet error collectibles for a denomination/year pair.
    No pricing data is included — pricing is lazy-loaded per row.

    Security:
      - Firebase ID token required (get_current_user dependency).
      - denomination_norm and year are the ONLY values forwarded toward Greysheet.
      - No uid, coin_id, or collection metadata leaves Cloud Run.
    """
    try:
        svc = GreysheetErrorService(db=db)
        entries = await svc.get_error_entries(
            denomination_norm=denomination_norm.strip().lower(),
            year=year,
        )
        return [
            GsErrorEntryResponse(
                gsid=e.gsid,
                name=e.name,
                classification_source=e.classification_source,
                is_confirmed=e.is_confirmed,
                category_hint=e.category_hint,
            )
            for e in entries
        ]
    except Exception as e:
        logger.error(f"[greysheet_error_routes] /known-errors error: {e}")
        # Soft fail — return empty list, not 500
        return []


@router.get("/known-errors/{gsid}/price", response_model=GsLazyPriceResponse)
async def get_known_error_price(
    gsid: int,
    _user: Dict[str, Any] = Depends(get_current_user),
) -> GsLazyPriceResponse:
    """
    Lazy price fetch for a single GSID. Called only when a user expands a Greysheet row.
    Returns { bid_low, ask_high, grade_count, attribution, available }.
    If the monthly error_pricing budget (5,000 calls) is exhausted, returns available=False.
    """
    try:
        svc = GreysheetErrorService(db=db)
        result = await svc.get_lazy_price(gsid)
        if result is None:
            return GsLazyPriceResponse(gsid=gsid, available=False, attribution="CPG® Data")
        return GsLazyPriceResponse(
            gsid=gsid,
            bid_low=result.get("bid_low"),
            ask_high=result.get("ask_high"),
            grade_count=result.get("grade_count", 0),
            attribution=result.get("attribution", "CPG® Data"),
            available=True,
        )
    except Exception as e:
        logger.error(f"[greysheet_error_routes] /known-errors/{gsid}/price error: {e}")
        return GsLazyPriceResponse(gsid=gsid, available=False, attribution="CPG® Data")
