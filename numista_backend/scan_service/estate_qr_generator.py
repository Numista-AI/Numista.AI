"""
estate_qr_generator.py — QR Code generation for Numista.AI estate reports

Generates PNG QR codes as bytes, used in the attorney access page of the
estate PDF. Requires: qrcode[pil]>=7.4.2
"""

import qrcode
from io import BytesIO


def generate_qr_bytes(
    url: str,
    box_size: int = 6,
    border: int = 2,
) -> bytes:
    """
    Generate a QR code PNG as raw bytes for the given URL.

    Args:
        url:      The URL or data string to encode.
        box_size: Size of each QR box in pixels (default 6).
        border:   White border width in boxes (default 2).

    Returns:
        PNG image as bytes, suitable for embedding in a ReportLab PDF via
        reportlab.platypus.Image(BytesIO(qr_bytes)).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
