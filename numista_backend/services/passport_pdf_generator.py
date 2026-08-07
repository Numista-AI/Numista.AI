"""
Passport PDF Generator — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Generates official Numista-branded dual-format PDF documents:
1. 8.5x11" Estate Certificate of Transfer (for legal, tax, and estate binders)
2. 3x5" Binder Passcard (with cut-out borders & QR code for coin flip sleeves & slab boxes)
"""

import io
import qrcode
from typing import Dict, Any, List
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_qr_code_image(data: str, size: int = 150) -> io.BytesIO:
    """Generates a QR code image stream from string data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E293B", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def downsample_image_to_300dpi_thumb(image_bytes: bytes, target_size_px: tuple = (300, 300)) -> io.BytesIO:
    """
    Downsamples raw image bytes (e.g. 1920x1080 capture) to 300 DPI 1-inch thumbnail (300x300 px),
    achieving a ~23x RAM footprint reduction for ReportLab PDF embedding.
    """
    buffer = io.BytesIO()
    try:
        with PILImage.open(io.BytesIO(image_bytes)) as img:
            img.thumbnail(target_size_px, PILImage.Resampling.LANCZOS)
            img.convert('RGB').save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            return buffer
    except Exception:
        buffer.seek(0)
        return buffer

def draw_diagonal_watermark(canvas, doc):
    """Draws a semi-transparent diagonal watermark across each PDF page."""
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 34)
    canvas.setFillColor(colors.HexColor('#94A3B8'))
    try:
        canvas.setFillAlpha(0.20)
    except Exception:
        pass
    canvas.translate(300, 420)
    canvas.rotate(35)
    canvas.drawCentredString(0, 0, "BETA – FOR EVALUATION ONLY")
    canvas.restoreState()

def scrub_item_payload(items: List[Dict[str, Any]], privacy_toggles: Dict[str, bool]) -> List[Dict[str, Any]]:
    """
    Sanitizes item records on the server according to sender privacy toggles.
    Missing toggles default to True (scrubbed) for defense-in-depth safety.
    """
    if not privacy_toggles:
        privacy_toggles = {}

    hide_cost = privacy_toggles.get('hide_cost_basis', True)
    hide_notes = privacy_toggles.get('hide_private_notes', True)
    hide_location = privacy_toggles.get('hide_storage_location', True)
    hide_invoices = privacy_toggles.get('hide_invoices', True)

    sanitized_items = []
    for itm in items:
        clean = dict(itm)
        if hide_cost:
            for k in ['purchaseCost', 'purchase_cost', 'Purchase Cost', 'purchaseDate', 'purchase_date', 'Purchase Date', 'cost_basis', 'acquisition_value', 'financial_records']:
                clean.pop(k, None)
        if hide_notes:
            for k in ['personalNotes', 'personal_notes', 'Personal Notes I', 'personalRef', 'personal_ref', 'Personal Reference #', 'private_notes']:
                clean.pop(k, None)
        if hide_location:
            for k in ['storageLocation', 'storage_location', 'Storage Location', 'safe_box_number', 'bin_location', 'vault_tags']:
                clean.pop(k, None)
        if hide_invoices:
            for k in ['retailer', 'retailerItemNo', 'retailerInvoiceNo', 'Retailer Invoice #', 'receipt_id', 'receiptGcsPath', 'paper_trail']:
                clean.pop(k, None)
        sanitized_items.append(clean)
    return sanitized_items

def generate_passport_pdf(transfer_data: Dict[str, Any]) -> bytes:
    """
    Generates a 2-page PDF containing:
    Page 1: 8.5x11" Formal Estate Certificate of Transfer
    Page 2: 3x5" Cut-Out Passcard for Coin Flip / Storage Bin
    """
    privacy_toggles = transfer_data.get("privacy_toggles", {})
    raw_items = transfer_data.get("items", [])
    items = scrub_item_payload(raw_items, privacy_toggles)

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0284C7'),
        alignment=1
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#B45309'),
        alignment=1
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    body_normal = ParagraphStyle(
        'BodyNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # ── PAGE 1: ESTATE CERTIFICATE ──────────────────────────────────────────────
    story.append(Paragraph("NUMISTA.AI • OFFICIAL PASSPORT PROTOCOL", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("ESTATE CERTIFICATE OF LATERAL TRANSFER", title_style))
    story.append(Spacer(1, 4))

    # BETA LEGAL DISCLAIMER BANNER
    disclaimer_banner = Table(
        [[Paragraph("<b>BETA EVALUATION DOCUMENT:</b> Generated for software testing purposes only. Does not constitute a certified USPAP appraisal or legal IRS Form 706 valuation.", disclaimer_style)]],
        colWidths=[7.5 * inch]
    )
    disclaimer_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF3C7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#F59E0B')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(disclaimer_banner)
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=8))

    transfer_id = transfer_data.get("transfer_id", "N/A")
    claim_pin = transfer_data.get("claim_pin", "******")
    sender_id = transfer_data.get("sender_id", "Anonymous Sender")
    created_at = transfer_data.get("created_at", "")[:10]
    expires_at = transfer_data.get("expires_at", "")[:10]

    # QR Code Generation
    qr_payload = f"https://numista.ai/claim?transfer_id={transfer_id}&pin={claim_pin}"
    qr_buf = generate_qr_code_image(qr_payload, size=180)
    qr_img = Image(qr_buf, width=1.4 * inch, height=1.4 * inch)

    meta_table_data = [
        [
            Paragraph(f"<b>Transfer ID:</b> {transfer_id}<br/>"
                      f"<b>Originating Owner:</b> {sender_id}<br/>"
                      f"<b>Date Initiated:</b> {created_at}<br/>"
                      f"<b>Token Expiration:</b> {expires_at} (60-Day Limit)<br/>"
                      f"<b>Claim PIN Code:</b> <font color='#0284C7' size=12><b>{claim_pin}</b></font>", body_normal),
            qr_img
        ]
    ]

    meta_table = Table(meta_table_data, colWidths=[5.5 * inch, 2.0 * inch])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('ROUNDEDCORNERS', [4, 4, 4, 4])
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Items Table
    story.append(Paragraph("TRANSFERRED INVENTORY SPECIFICATIONS", body_bold))
    story.append(Spacer(1, 4))

    item_rows = [[
        Paragraph("<b>Item Name / Title</b>", body_bold),
        Paragraph("<b>Year / Mint</b>", body_bold),
        Paragraph("<b>Grade / Cert</b>", body_bold),
        Paragraph("<b>Category</b>", body_bold)
    ]]

    for itm in items:
        name = itm.get("title") or itm.get("name") or "Numismatic Item"
        year_mint = f"{itm.get('year', 'N/A')} {itm.get('mint_mark', '')}".strip()
        grade = f"{itm.get('grade', 'Raw')} {itm.get('cert_number', '')}".strip()
        cat = itm.get("category", "Coin")

        item_rows.append([
            Paragraph(name, body_normal),
            Paragraph(year_mint, body_normal),
            Paragraph(grade, body_normal),
            Paragraph(cat, body_normal)
        ])

    items_table = Table(item_rows, colWidths=[3.2 * inch, 1.4 * inch, 1.4 * inch, 1.5 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    story.append(items_table)
    story.append(Spacer(1, 16))

    # Legal & Transfer Affirmation Notice
    affirmation_text = (
        "<b>LEGAL CHAIN OF CUSTODY NOTICE:</b> This passport certificate documents the formal lateral property "
        "transfer initiated via Numista.AI. By scanning the QR code or utilizing the 6-digit Claim PIN above, "
        "the recipient accepts full legal custody and ownership of the item(s) listed herein. All sensitive "
        "acquisition financials and private location metadata have been sanitized per sender specifications."
    )
    story.append(Paragraph(affirmation_text, body_normal))
    story.append(Spacer(1, 24))

    # Signature Lines
    sig_data = [
        [
            Paragraph("__________________________________________<br/><b>Transferor / Sender Signature</b>", body_normal),
            Paragraph("__________________________________________<br/><b>Transferee / Recipient Signature</b>", body_normal)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[3.7 * inch, 3.8 * inch])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'BOTTOM')]))
    story.append(sig_table)

    # ── PAGE 2: 3x5" BINDER PASSCARD ───────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("NUMISTA.AI • COMPACT BINDER PASSCARD (3\" x 5\")", subtitle_style))
    story.append(Paragraph("<i>Cut along dotted lines to insert into coin flip sleeves, binder slots, or shipping boxes.</i>", body_normal))
    story.append(Spacer(1, 12))

    # Build 3x5 Passcard Table
    card_qr_buf = generate_qr_code_image(qr_payload, size=120)
    card_qr_img = Image(card_qr_buf, width=1.1 * inch, height=1.1 * inch)

    first_item = items[0] if items else {}
    item_title = first_item.get("title") or first_item.get("name") or "Numismatic Item"
    item_sub = f"{first_item.get('year', '')} {first_item.get('mint_mark', '')} | {first_item.get('grade', 'Raw')}".strip()

    passcard_content = [
        [
            Paragraph("<font color='#0284C7'><b>NUMISTA PASSCARD</b></font>", body_bold),
            Paragraph(f"<font size=7>PIN: <b>{claim_pin}</b></font>", body_normal)
        ],
        [
            Paragraph(f"<b>{item_title}</b><br/><font size=8 color='#475569'>{item_sub}</font><br/><br/>"
                      f"<font size=7 color='#64748B'>ID: {transfer_id[:12]}...</font>", body_normal),
            card_qr_img
        ]
    ]

    passcard_table = Table(passcard_content, colWidths=[3.2 * inch, 1.6 * inch])
    passcard_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0284C7')),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    story.append(passcard_table)

    doc.build(story, onFirstPage=draw_diagonal_watermark, onLaterPages=draw_diagonal_watermark)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

