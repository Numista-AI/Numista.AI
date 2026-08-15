"""
Image Intake & Scraping Verifier (Generate-and-Select Pattern)
Validates coin image candidates from scrapers, Wikimedia, and manual uploads
using geometric, resolution, and format constraints before uploading to GCS.
"""

from typing import Dict, Any, List, Optional, Tuple
import io
import struct


def get_image_dimensions(image_bytes: bytes) -> Optional[Tuple[int, int]]:
    """Extract width and height from raw image bytes (JPEG, PNG, GIF, WebP) without heavy external deps."""
    if not image_bytes or len(image_bytes) < 32:
        return None

    # PNG check
    if image_bytes.startswith(b'\x89PNG\r\n\x1a\n') and len(image_bytes) >= 24:
        w, h = struct.unpack('>II', image_bytes[16:24])
        return (w, h)

    # GIF check
    if image_bytes[:6] in (b'GIF87a', b'GIF89a') and len(image_bytes) >= 10:
        w, h = struct.unpack('<HH', image_bytes[6:10])
        return (w, h)

    # JPEG check
    if image_bytes.startswith(b'\xff\xd8'):
        try:
            stream = io.BytesIO(image_bytes)
            stream.read(2)
            b = stream.read(1)
            while b and b != b'':
                while b != b'\xff':
                    b = stream.read(1)
                while b == b'\xff':
                    b = stream.read(1)
                if 0xe0 <= ord(b) <= 0xef or b in (b'\xdb', b'\xc4', b'\xfe'):
                    length = struct.unpack('>H', stream.read(2))[0]
                    stream.read(length - 2)
                elif 0xc0 <= ord(b) <= 0xc3:
                    struct.unpack('>H', stream.read(2))
                    struct.unpack('>B', stream.read(1))
                    h, w = struct.unpack('>HH', stream.read(4))
                    return (w, h)
                else:
                    break
                b = stream.read(1)
        except Exception:
            pass

    return None


def verify_image_candidate(
    image_bytes: bytes,
    metadata: Optional[Dict[str, Any]] = None,
    min_width: int = 300,
    min_height: int = 300,
    min_aspect_ratio: float = 0.75,
    max_aspect_ratio: float = 1.33,
    max_bytes: int = 15 * 1024 * 1024
) -> Dict[str, Any]:
    """
    Validates a scraped or uploaded image candidate before writing to Cloud Storage.
    
    Returns:
        {
            "is_valid": bool,
            "width": int,
            "height": int,
            "aspect_ratio": float,
            "size_bytes": int,
            "errors": list[str],
            "warnings": list[str]
        }
    """
    errors: List[str] = []
    warnings: List[str] = []
    metadata = metadata or {}

    size_bytes = len(image_bytes) if image_bytes else 0

    if size_bytes == 0:
        return {
            "is_valid": False,
            "width": 0,
            "height": 0,
            "aspect_ratio": 0.0,
            "size_bytes": 0,
            "errors": ["Image byte stream is empty (0 bytes)."],
            "warnings": []
        }

    if size_bytes > max_bytes:
        errors.append(f"Image file exceeds maximum allowable size ({size_bytes / (1024*1024):.2f}MB > {max_bytes / (1024*1024):.1f}MB).")

    dimensions = get_image_dimensions(image_bytes)
    width, height, aspect_ratio = 0, 0, 0.0

    if dimensions:
        width, height = dimensions
        if width > 0 and height > 0:
            aspect_ratio = round(width / float(height), 3)

            if width < min_width or height < min_height:
                errors.append(f"Low resolution image ({width}x{height}px). Minimum required is {min_width}x{min_height}px.")

            if aspect_ratio < min_aspect_ratio or aspect_ratio > max_aspect_ratio:
                errors.append(
                    f"Distorted aspect ratio ({aspect_ratio:.2f}). Single coin images should be roughly square "
                    f"({min_aspect_ratio:.2f} to {max_aspect_ratio:.2f}). Possible banner or partial crop."
                )
    else:
        # If dimensions could not be read via lightweight unpacker, issue a warning rather than hard blocking
        warnings.append("Could not determine image dimensions from stream header.")

    # Metadata checks (if provided)
    source_url = metadata.get("url") or metadata.get("source_url") or ""
    if source_url and any(ext in source_url.lower() for ext in [".svg", ".pdf", ".gif"]):
        errors.append(f"Unsupported coin image extension in URL '{source_url}'. Expected JPG, PNG, or WebP.")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "size_bytes": size_bytes,
        "errors": errors,
        "warnings": warnings
    }
