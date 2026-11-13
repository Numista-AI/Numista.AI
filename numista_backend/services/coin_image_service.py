"""Shared coin image URL validation, cropping, and EXIF-stripping service."""

import io
import os
import posixpath
import urllib.parse
from datetime import timedelta
from typing import Any, Dict, Optional, Set, Tuple

from fastapi import HTTPException
from PIL import Image, ImageOps

from services.gcs_signing_service import DEFAULT_SIGNER_SA, generate_v4_signed_url

DEFAULT_ALLOWED_IMAGE_BUCKETS = (
    "numista-uploads-studio-9101802118-8c9a8,"
    "studio-9101802118-8c9a8.firebasestorage.app"
)
MAX_IMAGE_BYTES = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000


def is_production_env() -> bool:
    """Matches routes/deps.py production environment detection."""
    return bool(
        os.environ.get("K_SERVICE")
        or os.environ.get("ENVIRONMENT") == "production"
    )


def get_allowed_image_buckets() -> Set[str]:
    """Returns the allowlisted GCS / Firebase Storage bucket names."""
    raw = os.environ.get("ALLOWED_IMAGE_BUCKETS", DEFAULT_ALLOWED_IMAGE_BUCKETS)
    return {b.strip() for b in raw.split(",") if b.strip()}


def parse_and_validate_storage_url(
    url: str,
    allowed_owners: Set[str],
) -> Tuple[str, str]:
    """Parses a GCS/Firebase Storage URL and enforces bucket + owner-prefix rules.

    Strictly URL-decodes the blob path once BEFORE normalization, traversal checks,
    and prefix matching so double-encoded (%252F) or traversal (..) payloads fail closed.
    """
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=404, detail="No coin image on file.")

    clean_url = url.strip()
    bucket_name = ""
    raw_blob = ""

    if clean_url.startswith("gs://"):
        rest = clean_url[5:]
        if "/" not in rest:
            raise HTTPException(status_code=403, detail="Forbidden")
        bucket_name, raw_blob = rest.split("/", 1)
    else:
        parsed = urllib.parse.urlparse(clean_url)
        host = (parsed.netloc or "").lower()
        if parsed.scheme != "https":
            raise HTTPException(status_code=403, detail="Forbidden")
        if host == "storage.googleapis.com":
            path = parsed.path.lstrip("/")
            if "/" not in path:
                raise HTTPException(status_code=403, detail="Forbidden")
            bucket_name, raw_blob = path.split("/", 1)
        elif host == "firebasestorage.googleapis.com":
            # Expected: /v0/b/<bucket>/o/<url_encoded_blob>
            parts = parsed.path.lstrip("/").split("/")
            if len(parts) < 5 or parts[0] != "v0" or parts[1] != "b" or parts[3] != "o":
                raise HTTPException(status_code=403, detail="Forbidden")
            bucket_name = parts[2]
            raw_blob = "/".join(parts[4:])
        else:
            raise HTTPException(status_code=403, detail="Forbidden")

    if bucket_name not in get_allowed_image_buckets():
        raise HTTPException(status_code=403, detail="Forbidden")

    # Reject any remaining query/fragment delimiters on gs:// paths.
    raw_blob = raw_blob.split("?", 1)[0].split("#", 1)[0]

    # Single-pass URL decode BEFORE traversal/prefix checks.
    decoded = urllib.parse.unquote(raw_blob)
    if (
        urllib.parse.unquote(decoded) != decoded
        or "%" in decoded
        or "\\" in decoded
        or "\x00" in decoded
        or decoded.startswith("/")
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    segments = decoded.split("/")
    if any(seg in ("", ".", "..") for seg in segments):
        raise HTTPException(status_code=403, detail="Forbidden")

    norm_blob = posixpath.normpath(decoded)
    if norm_blob != decoded:
        raise HTTPException(status_code=403, detail="Forbidden")

    owners = {o.strip().lower() for o in allowed_owners if o and o.strip()}
    if not owners or not any(
        norm_blob.lower().startswith(f"users/{o}/") for o in owners
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    return bucket_name, norm_blob


def crop_slot_image(img: Image.Image, slot_bbox: dict) -> Image.Image:
    """Crops a binder slot using percentage coordinates with a 25% margin."""
    width, height = img.size
    x_pct = float(slot_bbox.get("x_pct", 0))
    y_pct = float(slot_bbox.get("y_pct", 0))
    w_pct = float(slot_bbox.get("w_pct", 0.1))
    h_pct = float(slot_bbox.get("h_pct", 0.1))

    margin_x = w_pct * 0.25
    margin_y = h_pct * 0.25

    x1 = max(0, int((x_pct - margin_x) * width))
    y1 = max(0, int((y_pct - margin_y) * height))
    x2 = min(width, int((x_pct + w_pct + margin_x) * width))
    y2 = min(height, int((y_pct + h_pct + margin_y) * height))

    if (x2 - x1) < 80 or (y2 - y1) < 80:
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        half = max(60, (x2 - x1) // 2, (y2 - y1) // 2)
        x1 = max(0, cx - half)
        x2 = min(width, cx + half)
        y1 = max(0, cy - half)
        y2 = min(height, cy + half)

    return img.crop((x1, y1, x2, y2))


def load_sanitized_coin_image(
    storage_client,
    bucket_name: str,
    blob_name: str,
    slot_bbox: Optional[dict] = None,
    max_edge: int = 1600,
    quality: int = 85,
) -> Tuple[bytes, Tuple[int, int]]:
    """Downloads a validated blob, optionally crops, strips EXIF, and encodes JPEG."""
    Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if getattr(blob, "size", None) is None and hasattr(blob, "reload"):
        try:
            blob.reload()
        except Exception:
            pass
    blob_size = getattr(blob, "size", None)
    if isinstance(blob_size, (int, float)) and blob_size > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large.")

    img_bytes = blob.download_as_bytes()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large.")

    img = Image.open(io.BytesIO(img_bytes))
    img = ImageOps.exif_transpose(img).convert("RGB")

    has_bbox = bool(
        slot_bbox
        and float(slot_bbox.get("w_pct", 0) or 0) > 0
        and float(slot_bbox.get("h_pct", 0) or 0) > 0
    )
    if has_bbox and slot_bbox is not None:
        out_img = crop_slot_image(img, slot_bbox)
    else:
        out_img = img.copy()
        out_img.thumbnail((max_edge, max_edge))

    buf = io.BytesIO()
    out_img.save(buf, format="JPEG", quality=quality, exif=b"")
    return buf.getvalue(), out_img.size


def generate_v4_signed_get_url(
    storage_client,
    bucket_name: str,
    blob_name: str,
    expiry_minutes: int = 15,
) -> str:
    """Generates a short-lived V4 GCS Signed GET URL (supports local key & Cloud Run IAM signBlob)."""
    return generate_v4_signed_url(
        storage_client=storage_client,
        bucket_name=bucket_name,
        blob_name=blob_name,
        expiry_minutes=expiry_minutes,
        method="GET",
    )
