"""Authenticated 15-minute V4 Signed URL minting for user coin photos."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from routes.deps import (
    check_and_increment_rate_cap,
    logger,
    require_registered_user,
    storage_client,
)
from services.coin_image_service import (
    generate_v4_signed_get_url,
    is_production_env,
    parse_and_validate_storage_url,
)

router = APIRouter(prefix="/api/v1/photos", tags=["User Photo Signed URLs"])
MAX_BATCH_URLS = 50
SIGNED_URL_EXPIRY_MINUTES = 15


class SignedPhotoUrlRequest(BaseModel):
    urls: List[str]
    owner_hint: Optional[str] = None


@router.post("/signed_url")
def create_signed_photo_urls(
    req: SignedPhotoUrlRequest,
    user: Dict[str, Any] = Depends(require_registered_user),
) -> Dict[str, Any]:
    """Mints 15-minute V4 GCS Signed GET URLs for verified owner photo paths."""
    caller_uid = (user.get("uid") or user.get("user_id") or "").strip()
    caller_email = (user.get("email") or "").strip().lower()

    if not req.urls or len(req.urls) > MAX_BATCH_URLS:
        raise HTTPException(
            status_code=400,
            detail=f"urls must contain between 1 and {MAX_BATCH_URLS} items.",
        )

    rate_key = (caller_uid or caller_email).lower()
    if not rate_key:
        raise HTTPException(status_code=401, detail="Invalid user identity in token")

    is_admin = user.get("admin") is True
    check_and_increment_rate_cap(
        rate_key,
        "photo_signed_url",
        daily_limit=600,
        is_admin=is_admin,
        amount=len(req.urls),
    )

    allowed_owners = {x for x in (caller_email, caller_uid) if x}
    if is_admin and req.owner_hint and req.owner_hint.strip():
        hint = req.owner_hint.strip().lower()
        logger.warning(
            "photo_signed_url admin access admin=%s owner=%s count=%d",
            caller_email or caller_uid,
            hint,
            len(req.urls),
        )
        allowed_owners.add(hint)

    signed_urls: Dict[str, str] = {}
    errors: Dict[str, str] = {}
    first_http_exc: Optional[HTTPException] = None

    try:
        for raw_url in req.urls:
            try:
                bucket_name, blob_name = parse_and_validate_storage_url(
                    raw_url, allowed_owners
                )
                signed_urls[raw_url] = generate_v4_signed_get_url(
                    storage_client,
                    bucket_name,
                    blob_name,
                    expiry_minutes=SIGNED_URL_EXPIRY_MINUTES,
                )
            except HTTPException as exc:
                if first_http_exc is None:
                    first_http_exc = exc
                errors[raw_url] = "forbidden" if exc.status_code == 403 else "invalid"

        if not signed_urls and first_http_exc is not None:
            raise first_http_exc

        return {
            "status": "ok",
            "expires_in_seconds": SIGNED_URL_EXPIRY_MINUTES * 60,
            "signed_urls": signed_urls,
            "errors": errors,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to generate photo signed URL")
        raise HTTPException(status_code=500, detail="Could not generate photo link.")
