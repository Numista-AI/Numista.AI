"""
transfer_document_pdf.py — large-print Transfer Document (PLAN v1.2 section 4.1).

Works for eBay sales, private sales and gifts. The seller's e-mail is NEVER printed.
The sender appears as an anonymous collector reference plus an optional name/address
that the seller typed for this document only. The claim section (QR + short code) is
printed only when the raw token/code are supplied; they are never stored.
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.passport_pdf_generator import (
    format_grade_cert,
    format_item_title,
    format_year_mint,
    generate_qr_code_image,
)

APP_PUBLIC_DOMAIN = "numista.ai"

TYPE_LABELS = {
    "sale_ebay": "Sale (eBay)",
    "sale_private": "Sale (private)",
    "gift": "Gift",
    "lateral": "Lateral Transfer",
}


def _esc(text: Any) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def claim_url(claim_token: str) -> str:
    """Token travels in the URL fragment so it is never sent to a server or logged."""
    return f"https://{APP_PUBLIC_DOMAIN}/#/claim?t={claim_token}"


def _styles() -> Dict[str, ParagraphStyle]:
    return {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=28, leading=32, spaceAfter=6),
        "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=22, leading=26, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=16, leading=21),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=14, leading=18),
        "code": ParagraphStyle("code", fontName="Courier-Bold", fontSize=30, leading=36, textColor=colors.black),
        "step": ParagraphStyle("step", fontName="Helvetica", fontSize=16, leading=22, leftIndent=12),
    }


def generate_transfer_document_pdf(
    transfer_data: Dict[str, Any],
    claim_token: Optional[str] = None,
    claim_code: Optional[str] = None,
    item_photos: Optional[Dict[str, List[bytes]]] = None,
) -> bytes:
    s = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title="Numista.AI Transfer Document", author="Numista.AI",
    )
    story = []

    ttype = TYPE_LABELS.get(str(transfer_data.get("transfer_type") or "lateral"), "Lateral Transfer")
    story.append(Paragraph("TRANSFER DOCUMENT", s["title"]))
    story.append(Paragraph(f"{_esc(ttype)} &nbsp;|&nbsp; Numista.AI", s["small"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.black, spaceBefore=6, spaceAfter=8))

    # ---- Item block ----
    story.append(Paragraph("The item", s["h"]))
    for itm in transfer_data.get("items", []) or []:
        qty = int(itm.get("transfer_qty") or itm.get("Quantity") or 1)
        story.append(Paragraph(f"<b>{_esc(format_item_title(itm))}</b>", s["body"]))
        story.append(Paragraph(f"Year / mint mark: {_esc(format_year_mint(itm))}", s["body"]))
        story.append(Paragraph(f"Grade: {_esc(format_grade_cert(itm))}", s["body"]))
        set_contents = itm.get("set_contents")
        if itm.get("is_set") or itm.get("item_type") == "set":
            n = len(set_contents) if isinstance(set_contents, list) else 0
            story.append(Paragraph(f"Set type: set{f' ({n} pieces)' if n else ''}", s["body"]))
        story.append(Paragraph(f"Quantity: {qty}", s["body"]))
        if transfer_data.get("include_photos") and item_photos:
            raw_list = item_photos.get(str(itm.get("id") or "")) or []
            thumbs = []
            for img_bytes in raw_list[:2]:
                if not img_bytes:
                    continue
                try:
                    thumbs.append(
                        Image(io.BytesIO(img_bytes), width=1.6 * inch, height=1.6 * inch, kind="proportional")
                    )
                except Exception:
                    continue
            if thumbs:
                photo_tbl = Table([thumbs], colWidths=[1.8 * inch] * len(thumbs))
                photo_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
                story.append(Spacer(1, 4))
                story.append(photo_tbl)
        story.append(Spacer(1, 6))

    # ---- From / To ----
    story.append(Paragraph("From and to", s["h"]))
    sender_ref = transfer_data.get("sender_ref") or "A Numista.AI collector"
    from_lines = [f"A Numista.AI collector ({_esc(sender_ref)})"]
    if transfer_data.get("sender_display"):
        from_lines.append(_esc(transfer_data["sender_display"]))
    if transfer_data.get("sender_address"):
        from_lines.append(_esc(transfer_data["sender_address"]))
    created = str(transfer_data.get("created_at") or datetime.utcnow().isoformat())[:10]
    rows = [
        [Paragraph("<b>From</b>", s["body"]), Paragraph("<br/>".join(from_lines), s["body"])],
        [Paragraph("<b>To</b>", s["body"]), Paragraph("Recipient (filled in when claimed)", s["body"])],
        [Paragraph("<b>Type</b>", s["body"]), Paragraph(_esc(ttype), s["body"])],
        [Paragraph("<b>Date</b>", s["body"]), Paragraph(_esc(created), s["body"])],
    ]
    if transfer_data.get("show_price") and transfer_data.get("sale_price_usd") is not None:
        rows.append([Paragraph("<b>Price</b>", s["body"]),
                     Paragraph(f"${float(transfer_data['sale_price_usd']):,.2f}", s["body"])])
    tbl = Table(rows, colWidths=[1.2 * inch, 5.5 * inch])
    tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                             ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.grey),
                             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tbl)

    # ---- Claim ----
    story.append(Paragraph("Claim this item (free)", s["h"]))
    expires = str(transfer_data.get("expires_at") or "")[:10]
    if claim_token and claim_code:
        qr = Image(generate_qr_code_image(claim_url(claim_token)), width=2.0 * inch, height=2.0 * inch)
        steps = [
            Paragraph("1. Scan the square code, or go to <b>numista.ai/claim</b>.", s["step"]),
            Paragraph("2. Make a free account or sign in.", s["step"]),
            Paragraph("3. Scan, or type this code:", s["step"]),
            Paragraph(_esc(claim_code), s["code"]),
            Paragraph(f"Use it once. It expires on <b>{_esc(expires)}</b>." if expires else "Use it once.", s["step"]),
        ]
        layout = Table([[qr, steps]], colWidths=[2.3 * inch, 4.4 * inch])
        layout.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(layout)
    else:
        story.append(Paragraph(
            "This is a copy for the sender's records. The claim code was printed on the original "
            "and is not stored. To print a new one, choose <b>Reissue code</b> in Numista.AI.", s["body"]))

    # ---- Legal / signatures ----
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This document records a transfer started in Numista.AI. When the recipient claims it with the code "
        "above, the item and its history move to the recipient's collection. It is a record of transfer, "
        "not a certificate of authenticity.", s["small"]))
    story.append(Spacer(1, 18))
    sig = Table([[Paragraph("____________________________<br/>Sender signature (optional)", s["small"]),
                  Paragraph("____________________________<br/>Recipient signature (optional)", s["small"])]],
                colWidths=[3.35 * inch, 3.35 * inch])
    story.append(sig)

    doc.build(story)
    return buf.getvalue()
