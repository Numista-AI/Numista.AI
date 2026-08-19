"""
Passport PDF Generator — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Generates official Numista-branded dual-format PDF documents:
1. 8.5x11" Official Certificate of Transfer & Invoice Record
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

try:
    font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'DejaVuSans.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    else:
        alt_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
        ]
        for ap in alt_paths:
            if os.path.exists(ap):
                pdfmetrics.registerFont(TTFont('DejaVuSans', ap))
                break
except Exception:
    pass

def downsample_image_to_300dpi_thumb(image_bytes: bytes, max_size: tuple = (300, 300)) -> io.BytesIO:
    """
    Downsample raw image bytes to a 300 DPI-equivalent thumbnail for PDF embedding.

    Reduces high-resolution coin images to a compact thumbnail to minimize PDF
    file size while maintaining print quality. Uses Lanczos resampling for sharpness.

    Args:
        image_bytes: Raw image bytes (PNG, JPEG, etc.)
        max_size: Maximum (width, height) in pixels. Defaults to (300, 300).

    Returns:
        BytesIO buffer containing the downsampled PNG image.
    """
    img = PILImage.open(io.BytesIO(image_bytes))
    img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
    out_buf = io.BytesIO()
    img.save(out_buf, format='PNG', optimize=True)
    out_buf.seek(0)
    return out_buf

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
    Default to False (unscrubbed / full invoice data included).
    """
    if not privacy_toggles:
        privacy_toggles = {}

    hide_cost = privacy_toggles.get('hide_cost_basis', False)
    hide_notes = privacy_toggles.get('hide_private_notes', False)
    hide_location = privacy_toggles.get('hide_storage_location', False)
    hide_invoices = privacy_toggles.get('hide_invoices', False)

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

def _get_val(itm: Dict[str, Any], *keys: str) -> str:
    for k in keys:
        if k in itm and itm[k] is not None:
            v = str(itm[k]).strip()
            if v and v.upper() != "N/A":
                return v
    return ""

def format_item_title(itm: Dict[str, Any]) -> str:
    year = _get_val(itm, "year", "Year")
    series = _get_val(itm, "programSeries", "Program/Series", "program_series")
    denom = _get_val(itm, "denomination", "Denomination")
    variety = _get_val(itm, "variety", "Variety")
    theme = _get_val(itm, "themeSubject", "Theme/Subject", "theme")

    parts = [p for p in [year, series, denom, variety, theme] if p]
    if parts:
        return " ".join(parts)
    
    fallback = _get_val(itm, "title", "name", "originalDescription", "original_description")
    return fallback if fallback else "Numismatic Item"

def format_year_mint(itm: Dict[str, Any]) -> str:
    year = _get_val(itm, "year", "Year")
    mint = _get_val(itm, "mintMark", "Mint Mark", "mint_mark")
    variety = _get_val(itm, "variety", "Variety")
    parts = [p for p in [year, mint, variety] if p]
    return " ".join(parts) if parts else "N/A"

def format_grade_cert(itm: Dict[str, Any]) -> str:
    service = _get_val(itm, "gradingService", "Grading Service", "grading_service")
    grade = _get_val(itm, "condition", "Condition", "grade")
    cert = _get_val(itm, "certificationNumber", "Certification Number", "cert_number")

    grade_str = f"{service} {grade}".strip() if (service or grade) else "Raw / Ungraded"
    if cert:
        grade_str += f" (#{cert})"
    return grade_str

def format_financial_details(itm: Dict[str, Any]) -> str:
    cost = _get_val(itm, "purchaseCost", "purchase_cost", "Purchase Cost", "cost_basis", "price_paid")
    p_date = _get_val(itm, "purchaseDate", "purchase_date", "Purchase Date")
    ret = _get_val(itm, "retailer", "Retailer", "vendor_name")
    inv = _get_val(itm, "retailerInvoiceNo", "retailer_invoice_no", "Retailer Invoice #", "invoice_id")
    loc = _get_val(itm, "storageLocation", "storage_location", "Storage Location")
    est_val = _get_val(itm, "AI Estimated Value", "ai_value", "cpgRetail", "greysheetBid", "Melt Value")
    # Personal notes strictly from user input (series_description is ignored)
    raw_notes = _get_val(itm, "personalNotes", "personal_notes", "Personal Notes I", "Personal Notes")
    
    # Legacy Defense: If a legacy document contains catalog essay text inside personal_notes,
    # split and exclude the essay portion while preserving genuine short user provenance/vault notes.
    notes = ""
    if raw_notes:
        if (len(raw_notes) > 120 or raw_notes.strip().startswith("This coin is") or raw_notes.strip().startswith("Struck at")) and any(marker in raw_notes for marker in ["This coin is", "Struck at", "Designed by", "mintage of", "composition of"]):
            # Legacy item with embedded essay: extract user notes if a line break or delimiter is present, otherwise omit essay
            lines = raw_notes.split("\n")
            user_lines = [l.strip() for l in lines if l.strip() and not any(m in l for m in ["This coin is", "Struck at", "Designed by", "mintage of", "composition of"])]
            notes = " ".join(user_lines)[:200].strip()
        else:
            notes = raw_notes

    details = []
    # Qty
    qty_val = _get_val(itm, "Quantity", "qty", "quantity")
    try:
        qty = int(qty_val) if (qty_val and int(qty_val) > 0) else 1
    except (ValueError, TypeError):
        qty = 1
    
    # Cost
    cost_val = _get_val(itm, "purchaseCost", "purchase_cost", "Purchase Cost", "cost_basis", "price_paid")
    if cost_val is None or str(cost_val).strip() in ("", "null", "UKN", "unknown"):
        cost_str = "UKN"
    else:
        clean_c = str(cost_val).replace("$", "").replace(",", "").strip()
        try:
            val_c = float(clean_c)
            cost_str = f"${val_c:,.2f}"
        except ValueError:
            cost_str = str(cost_val)
    details.append(f"<b>Qty:</b> {qty} | <b>Cost:</b> {cost_str}")

    # Wholesale (Greysheet Bid)
    bid_raw = _get_val(itm, "greysheetBid", "greysheet_bid")
    if bid_raw is not None and str(bid_raw).strip() not in ("", "null"):
        try:
            bid_num = float(str(bid_raw).replace("$", "").replace(",", "").strip())
            details.append(f"<b>Wholesale (Bid):</b> ${bid_num:,.2f}")
        except ValueError:
            details.append("<b>Wholesale (Bid):</b> —")
    else:
        details.append("<b>Wholesale (Bid):</b> —")

    # Retail (CPG Market)
    cpg_raw = _get_val(itm, "cpgRetail", "cpg_retail")
    if cpg_raw is not None and str(cpg_raw).strip() not in ("", "null"):
        try:
            cpg_num = float(str(cpg_raw).replace("$", "").replace(",", "").strip())
            details.append(f"<b>Retail (CPG):</b> ${cpg_num:,.2f}")
        except ValueError:
            details.append("<b>Retail (CPG):</b> —")
    else:
        details.append("<b>Retail (CPG):</b> —")

    if p_date:
        details.append(f"<b>Acquired:</b> {p_date}")
    if ret:
        details.append(f"<b>Vendor:</b> {ret}")
    if inv:
        details.append(f"<b>Inv #:</b> {inv}")
    if loc:
        details.append(f"<b>Vault:</b> {loc}")
    if notes:
        details.append(f"<b>Notes:</b> {notes}")

    if details:
        return "<br/>".join(details)
    return "<font color='#64748B'>Full Specifications Included</font>"

def generate_passport_pdf(transfer_data: Dict[str, Any]) -> bytes:
    """
    Generates a 2-page PDF containing:
    Page 1: 8.5x11" Official Certificate of Lateral Transfer & Invoice
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

    # ── PAGE 1: OFFICIAL PASSPORT CERTIFICATE ───────────────────────────────────
    story.append(Paragraph("NUMISTA.AI • OFFICIAL PASSPORT PROTOCOL", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("PASSPORT CERTIFICATE OF LATERAL TRANSFER", title_style))
    story.append(Spacer(1, 4))

    # BETA EVALUATION DISCLAIMER BANNER
    disclaimer_banner = Table(
        [[Paragraph("<b>BETA EVALUATION DOCUMENT:</b> Generated for software testing purposes only. Documents item provenance and lateral property transfer.", disclaimer_style)]],
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

    from config import APP_PUBLIC_DOMAIN

    transfer_id = transfer_data.get("transfer_id", "N/A")
    claim_pin = transfer_data.get("claim_pin", "******")
    sender_id = transfer_data.get("sender_id", "Anonymous Sender")
    created_at = transfer_data.get("created_at", "")[:10]
    expires_at = transfer_data.get("expires_at", "")[:10]

    # QR Code Generation pointing directly to web app claim route
    qr_payload = f"https://{APP_PUBLIC_DOMAIN}/#/claim?transfer_id={transfer_id}&pin={claim_pin}"
    qr_buf = generate_qr_code_image(qr_payload, size=180)
    qr_img = Image(qr_buf, width=1.4 * inch, height=1.4 * inch)

    meta_table_data = [
        [
            Paragraph(f"<b>Transfer ID:</b> {transfer_id}<br/>"
                      f"<b>Originating Owner:</b> {sender_id}<br/>"
                      f"<b>Date Initiated:</b> {created_at}<br/>"
                      f"<b>Token Expiration:</b> {expires_at} (60-Day Limit)<br/>"
                      f"<b>Claim PIN Code:</b> <font color='#0284C7' size=13><b>{claim_pin}</b></font><br/><br/>"
                      f"<font color='#0284C7' size=8><b>WEB / DESKTOP RECEIVE INSTRUCTIONS:</b><br/>"
                      f"1. Sign into recipient account on <b>{APP_PUBLIC_DOMAIN}</b><br/>"
                      f"2. Click <b>Claim Transfer</b> (or <b>Lateral Transfer &rarr; Receive</b>)<br/>"
                      f"3. Enter Transfer ID &amp; PIN <b>{claim_pin}</b> to adopt items into vault.</font>", body_normal),
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
    story.append(Paragraph("TRANSFERRED INVENTORY SPECIFICATIONS & INVOICE DETAILS", body_bold))
    story.append(Spacer(1, 4))

    item_rows = [[
        Paragraph("<b>Item Description</b>", body_bold),
        Paragraph("<b>Year / Mint</b>", body_bold),
        Paragraph("<b>Grade &amp; Cert</b>", body_bold),
        Paragraph("<b>Financial &amp; Invoice Details</b>", body_bold)
    ]]

    total_cost = 0.0
    total_wholesale_bid = 0.0
    total_retail_cpg = 0.0
    bid_count = 0
    cpg_count = 0
    has_cost = False

    for itm in items:
        name = format_item_title(itm)
        year_mint = format_year_mint(itm)
        grade_cert = format_grade_cert(itm)
        fin_details = format_financial_details(itm)

        qty_val = _get_val(itm, "Quantity", "qty", "quantity")
        try:
            qty = int(qty_val) if (qty_val and int(qty_val) > 0) else 1
        except (ValueError, TypeError):
            qty = 1

        cost_str = _get_val(itm, "purchaseCost", "purchase_cost", "Purchase Cost", "cost_basis", "price_paid")
        if cost_str and str(cost_str).strip() not in ("", "null", "UKN", "unknown"):
            clean_num = str(cost_str).replace("$", "").replace(",", "").strip()
            try:
                val = float(clean_num)
                total_cost += val * qty
                has_cost = True
            except ValueError:
                pass

        bid_raw = _get_val(itm, "greysheetBid", "greysheet_bid")
        if bid_raw is not None and str(bid_raw).strip() not in ("", "null"):
            try:
                b_val = float(str(bid_raw).replace("$", "").replace(",", "").strip())
                total_wholesale_bid += b_val * qty
                bid_count += 1
            except ValueError:
                pass

        cpg_raw = _get_val(itm, "cpgRetail", "cpg_retail")
        if cpg_raw is not None and str(cpg_raw).strip() not in ("", "null"):
            try:
                c_val = float(str(cpg_raw).replace("$", "").replace(",", "").strip())
                total_retail_cpg += c_val * qty
                cpg_count += 1
            except ValueError:
                pass

        item_rows.append([
            Paragraph(name, body_normal),
            Paragraph(year_mint, body_normal),
            Paragraph(grade_cert, body_normal),
            Paragraph(fin_details, body_normal)
        ])

    if total_wholesale_bid > 0 or total_retail_cpg > 0:
        item_rows.append([
            Paragraph("<b>TOTAL WHOLESALE LIQUIDATION (BID)</b>", body_bold),
            Paragraph(f"{bid_count}/{len(items)} items with Bid", body_normal),
            Paragraph("", body_normal),
            Paragraph(f"<font color='#0284C7'><b>${total_wholesale_bid:,.2f}</b></font>", body_bold)
        ])
        item_rows.append([
            Paragraph("<b>TOTAL RETAIL REPLACEMENT (CPG)</b>", body_bold),
            Paragraph(f"{cpg_count}/{len(items)} items with CPG", body_normal),
            Paragraph("", body_normal),
            Paragraph(f"<font color='#16A34A'><b>${total_retail_cpg:,.2f}</b></font>", body_bold)
        ])

    if has_cost and total_cost > 0:
        item_rows.append([
            Paragraph("<b>TOTAL ACQUISITION COST BASIS</b>", body_bold),
            Paragraph("", body_normal),
            Paragraph("", body_normal),
            Paragraph(f"<font color='#475569'><b>${total_cost:,.2f}</b></font>", body_bold)
        ])

    items_table = Table(item_rows, colWidths=[2.8 * inch, 1.3 * inch, 1.4 * inch, 2.0 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    story.append(items_table)

    # Check for Reference Fallbacks and stamp Legal Provenance Notice
    has_reference_fallback = any(
        itm.get("is_reference_fallback") or itm.get("isReferenceFallback") or (itm.get("image_source") and "reference" in str(itm.get("image_source")).lower())
        for itm in items
    )
    if has_reference_fallback:
        fallback_banner = Table(
            [[Paragraph("<b>LEGAL PROVENANCE NOTICE:</b> CATALOG REFERENCE PHOTO — NOT INDIVIDUAL ASSET PHOTO. "
                        "Item records utilizing reference catalog imagery are contractually flagged for probate and legal audit compliance.", disclaimer_style)]],
            colWidths=[7.5 * inch]
        )
        fallback_banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#EF4444')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        story.append(Spacer(1, 6))
        story.append(fallback_banner)

    story.append(Spacer(1, 16))

    # Legal & Transfer Affirmation Notice
    affirmation_text = (
        "<b>LEGAL CHAIN OF CUSTODY NOTICE:</b> This official passport certificate documents the formal property "
        "transfer initiated via Numista.AI. By entering the 6-digit Claim PIN above or scanning the QR code on the web app, "
        "the recipient accepts full legal custody and ownership of the item(s) listed herein."
    )
    story.append(Paragraph(affirmation_text, body_normal))
    story.append(Spacer(1, 10))

    # Valuation & CDN Greysheet Attribution Disclaimer
    val_disclaimer_text = (
        "<font size=7 color='#64748B'><b>VALUATION NOTICE &amp; DISCLAIMER:</b> Numismatic value estimates powered by "
        "CDN Greysheet® Wholesale Bid &amp; CPG® Retail Price Guides. Bullion values calculated using live spot market feeds. "
        "CDN does not endorse this collection. This document is generated for lateral transfer and inventory documentation "
        "purposes only; it is not a certified USPAP appraisal.</font>"
    )
    story.append(Paragraph(val_disclaimer_text, body_normal))
    story.append(Spacer(1, 14))

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
    item_title = format_item_title(first_item)
    item_sub = f"{format_year_mint(first_item)} | {format_grade_cert(first_item)}".strip()

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
