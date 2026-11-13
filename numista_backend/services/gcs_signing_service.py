"""Leaf GCS V4 signed-URL helper with Cloud Run IAM signBlob fallback."""

import os
from datetime import timedelta
from typing import Any, Dict, Optional

from google.auth.transport import requests as google_auth_requests

DEFAULT_SIGNER_SA = os.getenv(
    "SIGNER_SA",
    os.getenv(
        "INSTALLER_SIGNER_SA",
        "568985927038-compute@developer.gserviceaccount.com",
    ),
)


def generate_v4_signed_url(
    storage_client: Any,
    bucket_name: str,
    blob_name: str,
    expiry_minutes: int = 15,
    method: str = "GET",
    content_type: Optional[str] = None,
    response_disposition: Optional[str] = None,
    response_type: Optional[str] = None,
) -> str:
    """Generate a short-lived V4 GCS Signed URL (local key or IAM signBlob)."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    sign_kwargs: Dict[str, Any] = {
        "version": "v4",
        "expiration": timedelta(minutes=expiry_minutes),
        "method": method,
    }
    if content_type:
        sign_kwargs["content_type"] = content_type
    if response_disposition:
        sign_kwargs["response_disposition"] = response_disposition
    if response_type:
        sign_kwargs["response_type"] = response_type

    creds = getattr(storage_client, "_credentials", None)
    if creds is not None and not hasattr(creds, "sign_bytes"):
        auth_req = google_auth_requests.Request()
        creds.refresh(auth_req)
        sa_email = getattr(creds, "service_account_email", None) or DEFAULT_SIGNER_SA
        sign_kwargs["service_account_email"] = sa_email
        sign_kwargs["access_token"] = creds.token

    return blob.generate_signed_url(**sign_kwargs)
