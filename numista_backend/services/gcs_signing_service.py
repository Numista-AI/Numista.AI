"""Leaf GCS V4 signed-URL helper with Cloud Run IAM signBlob fallback."""

import os
import threading
from datetime import timedelta
from typing import Any, Dict, Optional

import google.auth
from google.auth.transport import requests as google_auth_requests

DEFAULT_SIGNER_SA = os.getenv(
    "SIGNER_SA",
    os.getenv(
        "INSTALLER_SIGNER_SA",
        "568985927038-compute@developer.gserviceaccount.com",
    ),
)

# IAM Credentials SignBlob needs a cloud-platform-scoped token; the storage
# client's own token on Cloud Run is storage-scoped only (403 SCOPE_INSUFFICIENT).
_IAM_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

_signing_creds = None
_signing_lock = threading.Lock()


def _get_signing_creds():
    global _signing_creds
    with _signing_lock:
        if _signing_creds is None:
            _signing_creds, _ = google.auth.default(scopes=_IAM_SCOPES)
        if not _signing_creds.valid:
            _signing_creds.refresh(google_auth_requests.Request())
        return _signing_creds


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
        signing_creds = _get_signing_creds()
        sa_email = getattr(signing_creds, "service_account_email", None)
        if not sa_email or sa_email == "default":
            sa_email = DEFAULT_SIGNER_SA
        sign_kwargs["service_account_email"] = sa_email
        sign_kwargs["access_token"] = signing_creds.token

    return blob.generate_signed_url(**sign_kwargs)
