"""
Authenticated Desktop Microscope Agent Installer Download Route
Generates short-lived V4 GCS Signed URLs for gs://numista-private-installers/downloads/NumistaAgentSetup.exe.
"""

import os
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from google.auth.transport import requests as google_auth_requests
from routes.deps import storage_client, logger, get_current_user, check_and_increment_rate_cap

router = APIRouter(prefix="/api/v1/hardware", tags=["Hardware Agent"])

PRIVATE_INSTALLER_BUCKET = os.getenv("PRIVATE_INSTALLER_BUCKET", "numista-private-installers")
INSTALLER_BLOB_PATH = "downloads/NumistaAgentSetup.exe"
SIGNED_URL_EXPIRY_MINUTES = 15
DEFAULT_SIGNER_SA = os.getenv(
    "INSTALLER_SIGNER_SA",
    "568985927038-compute@developer.gserviceaccount.com",
)


@router.get("/installer_url")
async def get_hardware_installer_url(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Return a 15-minute V4 Signed URL for NumistaAgentSetup.exe to authenticated non-guest users."""
    firebase_claims = user.get("firebase") or {}
    if firebase_claims.get("sign_in_provider") == "anonymous":
        raise HTTPException(
            status_code=403,
            detail="Please sign in with a registered Numista.AI account to download the Desktop Agent.",
        )

    uid = (user.get("uid") or user.get("user_id") or user.get("email") or "").strip()
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid user identity in token")
    if uid == "dev_guest_uid":
        raise HTTPException(
            status_code=403,
            detail="Please sign in with a registered Numista.AI account to download the Desktop Agent.",
        )

    is_admin = user.get("admin") is True
    check_and_increment_rate_cap(uid, "hardware_installer_url", daily_limit=10, is_admin=is_admin)

    try:
        bucket = storage_client.bucket(PRIVATE_INSTALLER_BUCKET)
        blob = bucket.blob(INSTALLER_BLOB_PATH)

        sign_kwargs: Dict[str, Any] = {
            "version": "v4",
            "expiration": timedelta(minutes=SIGNED_URL_EXPIRY_MINUTES),
            "method": "GET",
            "response_disposition": 'attachment; filename="NumistaAgentSetup.exe"',
            "response_type": "application/octet-stream",
        }

        # Support both local serviceAccountKey.json signing and Cloud Run IAM signBlob
        creds = storage_client._credentials
        if not hasattr(creds, "sign_bytes"):
            auth_req = google_auth_requests.Request()
            creds.refresh(auth_req)
            sa_email = getattr(creds, "service_account_email", None) or DEFAULT_SIGNER_SA
            sign_kwargs["service_account_email"] = sa_email
            sign_kwargs["access_token"] = creds.token

        signed_url = blob.generate_signed_url(**sign_kwargs)
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
