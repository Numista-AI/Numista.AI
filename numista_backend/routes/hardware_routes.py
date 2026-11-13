"""
Authenticated Desktop Microscope Agent Installer Download Route
Generates short-lived V4 GCS Signed URLs for gs://numista-private-installers/downloads/NumistaAgentSetup.exe.
"""

import os
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from routes.deps import storage_client, logger, require_registered_user, check_and_increment_rate_cap
from services.gcs_signing_service import generate_v4_signed_url

router = APIRouter(prefix="/api/v1/hardware", tags=["Hardware Agent"])

PRIVATE_INSTALLER_BUCKET = os.getenv("PRIVATE_INSTALLER_BUCKET", "numista-private-installers")
INSTALLER_BLOB_PATH = "downloads/NumistaAgentSetup.exe"
SIGNED_URL_EXPIRY_MINUTES = 15


@router.get("/installer_url")
async def get_hardware_installer_url(user: Dict[str, Any] = Depends(require_registered_user)) -> Dict[str, Any]:
    """Return a 15-minute V4 Signed URL for NumistaAgentSetup.exe to authenticated non-guest users."""
    uid = (user.get("uid") or user.get("user_id") or user.get("email") or "").strip()
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid user identity in token")

    is_admin = user.get("admin") is True
    check_and_increment_rate_cap(uid, "hardware_installer_url", daily_limit=10, is_admin=is_admin)

    try:
        signed_url = generate_v4_signed_url(
            storage_client,
            PRIVATE_INSTALLER_BUCKET,
            INSTALLER_BLOB_PATH,
            expiry_minutes=SIGNED_URL_EXPIRY_MINUTES,
            method="GET",
            response_disposition='attachment; filename="NumistaAgentSetup.exe"',
            response_type="application/octet-stream",
        )
        logger.info(f"Issued 15-min installer signed URL for uid={uid}")
        return {
            "status": "success",
            "filename": "NumistaAgentSetup.exe",
            "signed_url": signed_url,
            "expires_in_seconds": SIGNED_URL_EXPIRY_MINUTES * 60,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to generate installer signed URL for uid={uid}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unable to generate installer download link.")
