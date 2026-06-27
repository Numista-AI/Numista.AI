"""
estate_pdf_builder.py — Professional attorney-grade PDF generator for Numista.AI estate reports

Uses ReportLab Platypus to produce a multi-section PDF suitable for submission
to estate attorneys, probate courts, and tax professionals.

Design principles:
  - Dark navy (#0E1117) header/accents, white body, light gray alternating rows
  - Times-Roman for narrative/legal text; Helvetica for data tables
  - Every page has a footer with page number and confidentiality notice
  - Handles large collections (2000+ coins) without memory overflow via chunked
    table rendering and optional portrait-mode condensed layout
  - Photos fetched with timeout and graceful fallback on failure

PDF structure:
  Page 1  — Cover page
  Page 2  — Table of contents
  Page 3+ — Executive summary with stat boxes and denomination breakdown
  Next    — State-specific guidance
  Next    — Itemized coin table (landscape for columns, portrait condensed for >500 coins)
  Next    — Appraiser flag section
  Next    — Stepped-up basis analysis
  Next    — NJ inheritance tax section (NJ only)
  Next    — NY estate tax section (NY only)
  Next    — Legal attestation block
  Last    — Disclaimer page
  Last    — Attorney access / QR code page
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime
from io import BytesIO
from typing import Any

import requests
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.colors import HexColor

log = logging.getLogger(__name__)

# ── Design tokens ──────────────────────────────────────────────────────────────
NAVY          = HexColor('#0E1117')
NAVY_LIGHT    = HexColor('#1A2233')
WHITE         = colors.white
GOLD          = HexColor('#C9A84C')
RED_WARN      = HexColor('#C0392B')
ORANGE_WARN   = HexColor('#E67E22')
ROW_ALT       = HexColor('#F8F9FA')
ROW_HEADER    = NAVY
BORDER_GRAY   = HexColor('#D1D5DB')
TEXT_DARK     = HexColor('#111827')
TEXT_MID      = HexColor('#4B5563')
TEXT_LIGHT    = HexColor('#9CA3AF')
BOX_BG        = HexColor('#F3F4F6')
BOX_WARN_BG   = HexColor('#FFF3CD')
BOX_WARN_BORD = HexColor('#D97706')
BOX_ERR_BG    = HexColor('#FEE2E2')
BOX_ERR_BORD  = RED_WARN
GREEN_GOOD    = HexColor('#166534')
BOX_SUCCESS   = HexColor('#DCFCE7')

# ── Page sizes ─────────────────────────────────────────────────────────────────
PAGE_PORTRAIT  = letter                  # 8.5 × 11 in
PAGE_LANDSCAPE = landscape(letter)       # 11 × 8.5 in

# ── Margins ────────────────────────────────────────────────────────────────────
MARGIN        = 0.65 * inch
MARGIN_BOTTOM = 0.75 * inch            # extra for footer

# ── Large-collection threshold ─────────────────────────────────────────────────
LARGE_COLLECTION = 500
VERY_LARGE_COLLECTION = 2000

# ── IRS appraisal threshold (mirrors estate_report_generator.py) ──────────────
IRS_THRESHOLD = 3_000.0

# ── Photo thumbnail size (inches, for embedding in coin table) ─────────────────
THUMB_W = 0.55 * inch
THUMB_H = 0.55 * inch

# ─────────────────────────────────────────────────────────────────────────────
# STYLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _styles() -> dict:
    """
    Build and return a dict of named ParagraphStyle objects.
    Called once per PDF build.
    """
    base = getSampleStyleSheet()

    def ps(name, **kwargs) -> ParagraphStyle:
        parent = kwargs.pop('parent', 'Normal')
        s = ParagraphStyle(name, parent=base[parent], **kwargs)
        return s

    return {
        # ── Cover page ──────────────────────────────────────────────────────
        'CoverTitle': ps(
            'CoverTitle', fontSize=26, fontName='Times-Bold',
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=8,
        ),
        'CoverSubtitle': ps(
            'CoverSubtitle', fontSize=14, fontName='Times-Roman',
            textColor=HexColor('#CBD5E1'), alignment=TA_CENTER, spaceAfter=6,
        ),
        'CoverOwner': ps(
            'CoverOwner', fontSize=20, fontName='Times-Bold',
            textColor=TEXT_DARK, alignment=TA_CENTER, spaceBefore=24, spaceAfter=8,
        ),
        'CoverMeta': ps(
            'CoverMeta', fontSize=11, fontName='Helvetica',
            textColor=TEXT_MID, alignment=TA_CENTER, spaceAfter=4,
        ),
        'CoverDisclaimer': ps(
            'CoverDisclaimer', fontSize=7.5, fontName='Helvetica',
            textColor=TEXT_MID, alignment=TA_LEFT, leading=11,
        ),
        # ── Section headings ────────────────────────────────────────────────
        'H1': ps(
            'H1', fontSize=16, fontName='Times-Bold',
            textColor=NAVY, spaceBefore=16, spaceAfter=6, leading=20,
        ),
        'H2': ps(
            'H2', fontSize=13, fontName='Times-Bold',
            textColor=NAVY, spaceBefore=12, spaceAfter=4, leading=16,
        ),
        'H3': ps(
            'H3', fontSize=11, fontName='Helvetica-Bold',
            textColor=NAVY, spaceBefore=8, spaceAfter=3,
        ),
        # ── Body text ───────────────────────────────────────────────────────
        'Body': ps(
            'Body', fontSize=10, fontName='Times-Roman',
            textColor=TEXT_DARK, leading=15, spaceAfter=6,
        ),
        'BodySmall': ps(
            'BodySmall', fontSize=8.5, fontName='Times-Roman',
            textColor=TEXT_DARK, leading=12, spaceAfter=4,
        ),
        'BodyTiny': ps(
            'BodyTiny', fontSize=7.5, fontName='Helvetica',
            textColor=TEXT_MID, leading=10,
        ),
        'BulletBody': ps(
            'BulletBody', fontSize=9.5, fontName='Times-Roman',
            textColor=TEXT_DARK, leading=14, leftIndent=12, bulletIndent=0,
            spaceAfter=2,
        ),
        # ── Table cells ─────────────────────────────────────────────────────
        'TableHeader': ps(
            'TableHeader', fontSize=8, fontName='Helvetica-Bold',
            textColor=WHITE, alignment=TA_CENTER,
        ),
        'TableCell': ps(
            'TableCell', fontSize=7.5, fontName='Helvetica',
            textColor=TEXT_DARK, alignment=TA_LEFT, leading=10,
        ),
        'TableCellCenter': ps(
            'TableCellCenter', fontSize=7.5, fontName='Helvetica',
            textColor=TEXT_DARK, alignment=TA_CENTER, leading=10,
        ),
        'TableCellRight': ps(
            'TableCellRight', fontSize=7.5, fontName='Helvetica',
            textColor=TEXT_DARK, alignment=TA_RIGHT, leading=10,
        ),
        'TableCellSmall': ps(
            'TableCellSmall', fontSize=6.5, fontName='Helvetica',
            textColor=TEXT_DARK, alignment=TA_LEFT, leading=9,
        ),
        # ── Warning / info boxes ─────────────────────────────────────────────
        'WarnText': ps(
            'WarnText', fontSize=9.5, fontName='Helvetica-Bold',
            textColor=HexColor('#7C2D12'), leading=13,
        ),
        'InfoText': ps(
            'InfoText', fontSize=9.5, fontName='Helvetica',
            textColor=NAVY, leading=13,
        ),
        # ── TOC ─────────────────────────────────────────────────────────────
        'TOCEntry': ps(
            'TOCEntry', fontSize=11, fontName='Times-Roman',
            textColor=TEXT_DARK, leading=16, spaceAfter=2,
        ),
        'TOCPage': ps(
            'TOCPage', fontSize=11, fontName='Times-Roman',
            textColor=TEXT_MID, alignment=TA_RIGHT, leading=16, spaceAfter=2,
        ),
        # ── Attestation / legal ──────────────────────────────────────────────
        'Legal': ps(
            'Legal', fontSize=9, fontName='Times-Roman',
            textColor=TEXT_DARK, leading=14, spaceAfter=4,
        ),
        'LegalSmall': ps(
            'LegalSmall', fontSize=8, fontName='Times-Roman',
            textColor=TEXT_MID, leading=12, spaceAfter=3,
        ),
        # ── Stat box ─────────────────────────────────────────────────────────
        'StatLabel': ps(
            'StatLabel', fontSize=8, fontName='Helvetica',
            textColor=TEXT_MID, alignment=TA_CENTER,
        ),
        'StatValue': ps(
            'StatValue', fontSize=15, fontName='Helvetica-Bold',
            textColor=NAVY, alignment=TA_CENTER, leading=18,
        ),
        'StatValueLarge': ps(
            'StatValueLarge', fontSize=13, fontName='Helvetica-Bold',
            textColor=NAVY, alignment=TA_CENTER, leading=16,
        ),
    }


def _ts_base() -> list:
    """Base TableStyle directives shared across most tables."""
    return [
        ('GRID',        (0, 0), (-1, -1), 0.4, BORDER_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ROW_ALT]),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND',  (0, 0), (-1, 0), ROW_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTSIZE',    (0, 0), (-1, 0), 8),
        ('FONTSIZE',    (0, 1), (-1, -1), 7.5),
        ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',  (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# PHOTO FETCHING
# ─────────────────────────────────────────────────────────────────────────────

def fetch_image_bytes(url: str, max_size: tuple = (80, 80)) -> bytes | None:
    """
    Fetch a coin photo from a URL, resize as thumbnail, and return JPEG bytes.

    Returns None on any failure (network error, bad URL, invalid image, timeout).
    Designed to be called with try/except — never raises.
    """
    if not url or not str(url).startswith('http'):
        return None
    try:
        resp = requests.get(str(url), timeout=5, stream=True)
        if resp.status_code != 200:
            return None
        content = resp.content
        if len(content) < 100:          # too small to be a real image
            return None
        img = PILImage.open(BytesIO(content))
        img = img.convert('RGB')        # ensure JPEG-compatible mode
        img.thumbnail(max_size, PILImage.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=82)
        return buf.getvalue()
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PAGE TEMPLATES (header/footer canvas callbacks)
# ─────────────────────────────────────────────────────────────────────────────

class _PageDecor:
    """
    Mixin providing canvas-level header/footer drawing methods.
    Used as page template callbacks in the ReportLab Platypus document.
    """

    def __init__(self, owner_name: str, mode: str, total_pages_ref: list):
        self.owner_name = owner_name
        self.mode = mode
        self.total_pages_ref = total_pages_ref   # mutable list so we can set it later

    def draw_footer(self, canvas, doc):
        """Draw footer on every page except cover."""
        if doc.page == 1:
            return
        canvas.saveState()
        w, h = doc.pagesize
        footer_y = MARGIN_BOTTOM - 0.45 * inch
        # Thin rule above footer
        canvas.setStrokeColor(BORDER_GRAY)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, footer_y + 10, w - MARGIN, footer_y + 10)
        # Left: branding
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(TEXT_LIGHT)
        canvas.drawString(
            MARGIN, footer_y,
            'Numista.AI Estate Planning Report  |  Confidential'
        )
        # Center: owner + mode
        mode_label = (
            'Living Inventory' if self.mode == 'living_inventory'
            else 'Estate Settlement Report'
        )
        canvas.drawCentredString(
            w / 2, footer_y,
            f'{self.owner_name}  •  {mode_label}'
        )
        # Right: page number
        total = self.total_pages_ref[0] if self.total_pages_ref[0] > 0 else '?'
        canvas.drawRightString(
            w - MARGIN, footer_y,
            f'Page {doc.page} of {total}'
        )
        canvas.restoreState()

    def draw_cover_footer(self, canvas, doc):
        """Minimal footer for cover page."""
        canvas.saveState()
        w, _ = doc.pagesize
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(TEXT_LIGHT)
        canvas.drawCentredString(
            w / 2, 0.35 * inch,
            'Generated by Numista.AI  |  This document is confidential and prepared for estate planning purposes only'
        )
        canvas.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION BUILDERS — each returns a list of Flowables
# ─────────────────────────────────────────────────────────────────────────────

def _cover_page(ctx: dict, st: dict) -> list:
    """Build the cover page flowables."""
    rr = ctx['report_request']
    state_rules = ctx['state_rules']
    mode = ctx['mode']
    owner = rr.get('owner_name', 'Estate Owner')
    report_date = rr.get('report_date', date.today().isoformat())
    dod = rr.get('date_of_death', '')
    attorney = rr.get('attorney_name', '')
    attorney_email = rr.get('attorney_email', '')
    executor = rr.get('executor_name', '')

    mode_label = 'Living Inventory' if mode == 'living_inventory' else 'Estate Settlement Report'

    story: list = []

    # ── Dark navy header band ──────────────────────────────────────────────────
    # We draw this via a Table to stay in the Platypus flow
    header_data = [[
        Paragraph('NUMISMATIC COLLECTION', st['CoverTitle']),
    ], [
        Paragraph(mode_label.upper(), st['CoverSubtitle']),
    ]]
    header_table = Table(header_data, colWidths=[7.2 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING',    (0, 0), (-1, -1), 22),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 22),
        ('LEFTPADDING',   (0, 0), (-1, -1), 20),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 20),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4 * inch))

    # ── Owner name ─────────────────────────────────────────────────────────────
    story.append(Paragraph(owner, st['CoverOwner']))
    story.append(Spacer(1, 0.15 * inch))

    # ── Meta info table ────────────────────────────────────────────────────────
    meta_rows = [
        ['Report Date:', _fmt_date(report_date)],
        ['Jurisdiction:', state_rules['display_name']],
    ]
    if mode == 'estate_settlement':
        meta_rows.insert(0, ['Date of Death:', _fmt_date(dod) if dod else 'Not specified'])
        meta_rows.append(['Estate of:', owner])
    else:
        meta_rows.append(['Prepared for:', 'Estate Planning Purposes'])
    if executor:
        meta_rows.append(['Executor / PR:', executor])
    if attorney:
        meta_rows.append(['Attorney:', attorney])
    if attorney_email:
        meta_rows.append(['Attorney Email:', attorney_email])

    meta_table = Table(
        [[Paragraph(r[0], st['CoverMeta']), Paragraph(r[1], ParagraphStyle(
            'CoverMetaVal', parent=getSampleStyleSheet()['Normal'],
            fontSize=11, fontName='Times-Bold', textColor=TEXT_DARK,
            alignment=TA_LEFT,
        ))] for r in meta_rows],
        colWidths=[2.2 * inch, 4.0 * inch],
        hAlign='CENTER',
    )
    meta_table.setStyle(TableStyle([
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * inch))

    # ── Thin gold rule ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1.5, color=GOLD, spaceAfter=6))

    # ── Key stats preview ──────────────────────────────────────────────────────
    summary = ctx['summary']
    stats_data = [[
        _stat_cell('Total Coins', f'{summary["total_coins"]:,}', st),
        _stat_cell('Est. Collection FMV', f'${summary["total_fmv"]:,.0f}', st),
        _stat_cell('Cost Basis', f'${summary["total_cost_basis"]:,.0f}', st),
    ]]
    stats_table = Table(stats_data, colWidths=[2.4 * inch] * 3, hAlign='CENTER')
    stats_table.setStyle(TableStyle([
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOX',          (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('LINEBEFORE',   (1, 0), (1, -1), 0.5, BORDER_GRAY),
        ('LINEBEFORE',   (2, 0), (2, -1), 0.5, BORDER_GRAY),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.4 * inch))

    # ── Disclaimer box ─────────────────────────────────────────────────────────
    if mode == 'living_inventory':
        disc_text = (
            '<b>LIVING INVENTORY NOTICE:</b> This document is a preliminary inventory of a '
            'numismatic collection prepared for estate planning purposes. Estimated values '
            'are derived from AI image analysis and are not a qualified appraisal under '
            'IRC §170(f)(11). This document does not constitute legal or tax advice. '
            'The owner and their estate counsel should retain this inventory and obtain a '
            'formal qualified appraisal from a certified numismatist before filing any '
            'estate or gift tax return.'
        )
    else:
        disc_text = (
            '<b>ESTATE SETTLEMENT NOTICE:</b> This document is an estate inventory of a '
            'numismatic collection prepared for probate and estate settlement purposes. '
            'Estimated values are derived from AI image analysis and are NOT a qualified '
            'appraisal for IRS or court purposes. An independent, qualified numismatic '
            'appraiser must be retained. This document does not constitute legal or tax '
            'advice. All figures are subject to professional review and revision.'
        )
    disc_box = _info_box(disc_text, st['CoverDisclaimer'], bg=BOX_BG, border=BORDER_GRAY)
    story.append(disc_box)

    story.append(PageBreak())
    return story


def _stat_cell(label: str, value: str, st: dict) -> list:
    """Return a two-Paragraph list for a stat box cell."""
    return [
        Paragraph(label, st['StatLabel']),
        Paragraph(value, st['StatValue']),
    ]


def _info_box(
    text: str,
    style: ParagraphStyle,
    bg: HexColor = BOX_BG,
    border: HexColor = BORDER_GRAY,
    padding: float = 10,
) -> Table:
    """Wrap a paragraph in a colored background box."""
    t = Table(
        [[Paragraph(text, style)]],
        colWidths=[7.2 * inch],
    )
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), bg),
        ('BOX',           (0, 0), (-1, -1), 1, border),
        ('TOPPADDING',    (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ('LEFTPADDING',   (0, 0), (-1, -1), padding),
        ('RIGHTPADDING',  (0, 0), (-1, -1), padding),
    ]))
    return t


def _toc_page(ctx: dict, st: dict) -> list:
    """Build the Table of Contents page."""
    story: list = [
        Paragraph('Table of Contents', st['H1']),
        HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8),
    ]

    mode = ctx['mode']
    state_code = ctx['state_code']
    summary = ctx['summary']

    sections = [
        ('Executive Summary', '3'),
        (f'{ctx["state_rules"]["display_name"]} Estate Planning Guidance', '—'),
        ('Heir Liquidation Playbook', '—'),
    ]
    if ctx.get('division_results'):
        sections.append(('Equitable Division Plan', '—'))

    sections += [
        ('Itemized Coin Inventory', '—'),
        ('Coins Requiring Professional Appraisal', '—'),
        ('Step-Up in Basis Analysis', '—'),
    ]
    if state_code == 'NJ':
        sections.append(('NJ Inheritance Tax Analysis', '—'))
    if state_code == 'NY':
        sections.append(('NY Estate Tax Analysis', '—'))
    sections += [
        ('Legal Attestation', '—'),
        ('Disclaimer and Limitations', '—'),
        ('Attorney Access', '—'),
    ]

    toc_data = [[
        Paragraph(f'{i + 1}.  {title}', st['TOCEntry']),
        Paragraph(pg, st['TOCPage']),
    ] for i, (title, pg) in enumerate(sections)]

    toc_table = Table(toc_data, colWidths=[6.4 * inch, 0.8 * inch])
    toc_table.setStyle(TableStyle([
        ('ALIGN',         (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW',     (0, 0), (-1, -2), 0.3, BORDER_GRAY),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    return story


def _executive_summary(ctx: dict, st: dict) -> list:
    """Build the executive summary section with stat boxes and denomination table."""
    summary = ctx['summary']
    narrative = ctx['narrative']
    rr = ctx['report_request']
    state_rules = ctx['state_rules']
    story: list = []

    # ── Section heading ────────────────────────────────────────────────────────
    story.append(Paragraph('Executive Summary', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8))

    # ── Six stat boxes ─────────────────────────────────────────────────────────
    def stat(label, val):
        t = Table(
            [[Paragraph(label, st['StatLabel'])], [Paragraph(val, st['StatValueLarge'])]],
            colWidths=[2.3 * inch],
        )
        t.setStyle(TableStyle([
            ('BOX',           (0, 0), (-1, -1), 0.8, NAVY),
            ('BACKGROUND',    (0, 0), (-1, -1), BOX_BG),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ]))
        return t

    appraisal_count = summary['total_coins_needing_appraisal']
    step_up = summary['stepped_up_basis_benefit']

    row1 = [[
        stat('Total Coins', f'{summary["total_coins"]:,}'),
        stat('Collection FMV', f'${summary["total_fmv"]:,.0f}'),
        stat('Total Melt Value', f'${summary["total_melt_value"]:,.0f}'),
    ]]
    row2 = [[
        stat('Total Cost Basis', f'${summary["total_cost_basis"]:,.0f}'),
        stat('Step-Up Benefit', f'${step_up:,.0f}'),
        stat('Need Appraisal', f'{appraisal_count:,}'),
    ]]

    for row in [row1, row2]:
        box_table = Table(row, colWidths=[2.4 * inch] * 3, hAlign='LEFT')
        box_table.setStyle(TableStyle([
            ('ALIGN',  (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(box_table)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))

    # ── AI executive summary narrative ─────────────────────────────────────────
    story.append(Paragraph('Collection Overview', st['H2']))
    story.append(Paragraph(
        narrative.get('executive_summary', ''), st['Body']
    ))
    story.append(Paragraph(
        narrative.get('valuation_narrative', ''), st['Body']
    ))
    story.append(Paragraph(
        narrative.get('special_items_narrative', ''), st['Body']
    ))

    # ── Cliff warning (NY) ─────────────────────────────────────────────────────
    cliff = summary.get('cliff_warning')
    if cliff:
        is_critical = 'exceeds' in cliff
        bg    = BOX_ERR_BG    if is_critical else BOX_WARN_BG
        bord  = BOX_ERR_BORD  if is_critical else BOX_WARN_BORD
        label = '⚠ NY ESTATE TAX CLIFF — CRITICAL WARNING' if is_critical else '⚠ NY ESTATE TAX CLIFF — APPROACHING THRESHOLD'
        story.append(Spacer(1, 6))
        story.append(Paragraph(label, st['H3']))
        story.append(_info_box(cliff, st['WarnText'] if is_critical else st['InfoText'], bg=bg, border=bord))
        story.append(Spacer(1, 6))

    # ── Denomination breakdown ─────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph('FMV by Denomination', st['H2']))

    denom_data = [['Denomination', 'Coins', 'Total FMV', '% of Collection']]
    fmv_total = summary['total_fmv'] or 1.0  # avoid div/0
    for denom, info in summary['fmv_by_denomination'].items():
        pct = (info['total_fmv'] / fmv_total * 100) if fmv_total > 0 else 0
        denom_data.append([
            denom,
            f'{info["count"]:,}',
            f'${info["total_fmv"]:,.0f}',
            f'{pct:.1f}%',
        ])

    denom_table = Table(
        denom_data,
        colWidths=[3.0 * inch, 1.0 * inch, 1.6 * inch, 1.6 * inch],
    )
    denom_table.setStyle(TableStyle(_ts_base() + [
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ]))
    story.append(denom_table)

    # ── Location breakdown ─────────────────────────────────────────────────────
    if summary.get('fmv_by_location') and len(summary['fmv_by_location']) > 1:
        story.append(Spacer(1, 12))
        story.append(Paragraph('FMV by Storage Location', st['H2']))
        loc_data = [['Storage Location', 'Coins', 'Total FMV', '% of Collection']]
        for loc, info in summary['fmv_by_location'].items():
            pct = (info['total_fmv'] / fmv_total * 100) if fmv_total > 0 else 0
            loc_data.append([
                loc,
                f'{info["count"]:,}',
                f'${info["total_fmv"]:,.0f}',
                f'{pct:.1f}%',
            ])
        loc_table = Table(
            loc_data,
            colWidths=[3.0 * inch, 1.0 * inch, 1.6 * inch, 1.6 * inch],
        )
        loc_table.setStyle(TableStyle(_ts_base() + [
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ]))
        story.append(loc_table)

    story.append(PageBreak())
    return story


def _state_guidance_section(ctx: dict, st: dict) -> list:
    """Build state-specific estate planning guidance section."""
    state_rules = ctx['state_rules']
    state_code = ctx['state_code']
    mode = ctx['mode']
    summary = ctx['summary']
    narrative = ctx['narrative']
    rr = ctx['report_request']
    story: list = []

    heading = f'{state_rules["display_name"]} Estate Planning Guidance'
    story.append(Paragraph(heading, st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8))

    # ── AI jurisdiction guidance ───────────────────────────────────────────────
    jg = narrative.get('jurisdiction_guidance', '')
    if jg:
        story.append(Paragraph(jg, st['Body']))
        story.append(Spacer(1, 6))

    # ── Deadline warning box ───────────────────────────────────────────────────
    days = state_rules['filing_deadline_days']
    warn_text = state_rules['report_deadline_warning']
    deadline_bg   = BOX_ERR_BG  if days <= 60 else BOX_WARN_BG
    deadline_bord = BOX_ERR_BORD if days <= 60 else BOX_WARN_BORD
    deadline_st   = st['WarnText'] if days <= 60 else st['InfoText']

    story.append(Paragraph('Filing Deadline', st['H2']))
    story.append(_info_box(
        f'<b>Deadline: {days} days</b>  —  {warn_text}',
        deadline_st, bg=deadline_bg, border=deadline_bord,
    ))
    story.append(Spacer(1, 10))

    # ── Key requirements table ─────────────────────────────────────────────────
    story.append(Paragraph('Jurisdiction Summary', st['H2']))

    def yn(v):
        return 'Yes' if v else 'No'

    req_data = [
        ['Item', 'Details'],
        ['State', state_rules['display_name']],
        ['Governing Statute', state_rules['governing_statute']],
        ['Probate Form', f'{state_rules["probate_form"]}  ({state_rules["probate_form_code"]})'],
        ['Filed With', state_rules['filed_with']],
        ['Filing Deadline', f'{days} days'],
        ['State Estate Tax', yn(state_rules['estate_tax'])],
        ['State Inheritance Tax', yn(state_rules['inheritance_tax'])],
        ['Community Property State', yn(state_rules['community_property'])],
        ['TPP Memorandum Allowed', yn(state_rules['tpp_memo_allowed'])],
        ['Inventory Confidential', yn(state_rules.get('inventory_confidential', False))],
    ]
    if state_rules.get('estate_tax') and state_rules.get('exemption_2026'):
        req_data.append([
            'State Exemption (2026)',
            f'${state_rules["exemption_2026"]:,.0f}'
        ])
    if state_rules.get('cliff_rule'):
        req_data.append(['Cliff Rule', f'Yes — cliff at {state_rules["cliff_multiplier"]:.0%} × exemption'])
    if state_rules.get('tpp_memo_capped'):
        req_data.append([
            'TPP Memo Cap',
            f'${state_rules["tpp_memo_cap_per_item"]:,.0f}/item; '
            f'${state_rules["tpp_memo_cap_total"]:,.0f} total',
        ])
    if state_rules.get('tpp_memo_statute'):
        req_data.append(['TPP Memo Statute', state_rules['tpp_memo_statute']])
    if state_rules.get('dor_reporting_threshold'):
        req_data.append([
            'DOR Reporting Threshold',
            f'${state_rules["dor_reporting_threshold"]:,.0f} (inventory copy sent to Dept of Revenue)',
        ])
    if state_rules.get('coins_in_statute'):
        req_data.append(['Coins Named in Statute', 'Yes — TX Estates Code §255.001 explicitly names coin collections'])

    req_table = Table(req_data, colWidths=[2.6 * inch, 4.6 * inch])
    req_table.setStyle(TableStyle(_ts_base() + [
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, -1), 8),
        ('TEXTCOLOR', (0, 1), (0, -1), NAVY),
    ]))
    story.append(req_table)
    story.append(Spacer(1, 12))

    # ── Special notes ──────────────────────────────────────────────────────────
    special_notes = state_rules.get('special_notes', [])
    if special_notes:
        story.append(Paragraph('Important Notes for This Jurisdiction', st['H2']))
        for note in special_notes:
            story.append(Paragraph(f'• {note}', st['BulletBody']))
        story.append(Spacer(1, 8))

    # ── NJ inheritance tax rate table ─────────────────────────────────────────
    if state_code == 'NJ' and state_rules.get('inheritance_tax_classes'):
        story.append(Paragraph('NJ Inheritance Tax — Beneficiary Class Rates', st['H3']))
        classes = state_rules['inheritance_tax_classes']
        class_data = [['Class', 'Who Qualifies', 'Rate']]
        class_info = {
            'A': 'Spouse, civil union partner, children, grandchildren, parents, grandparents',
            'C': 'Siblings, sons-in-law, daughters-in-law, surviving spouses of children',
            'D': 'All other beneficiaries (friends, cousins, nephews, unrelated parties)',
            'E': 'Qualifying charitable, religious, scientific organizations',
        }
        for cls, rate in sorted(classes.items()):
            class_data.append([
                f'Class {cls}',
                class_info.get(cls, ''),
                f'{rate:.0%}' if rate > 0 else '0% (Exempt)',
            ])
        class_table = Table(class_data, colWidths=[0.8 * inch, 4.4 * inch, 2.0 * inch])
        class_table.setStyle(TableStyle(_ts_base() + [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ]))
        story.append(class_table)
        story.append(Spacer(1, 6))
        story.append(_info_box(
            'NJ PHYSICAL SITUS RULE: Coins physically located in New Jersey are subject to '
            'NJ inheritance tax regardless of the decedent\'s state of residence. '
            'Storage location of each coin should be documented. '
            'Coins stored out-of-state may not be subject to NJ inheritance tax.',
            st['WarnText'], bg=BOX_WARN_BG, border=BOX_WARN_BORD,
        ))

    story.append(PageBreak())
    return story


def _coin_table_section(ctx: dict, st: dict) -> list:
    """
    Build the itemized coin inventory table.

    For large collections (>500), uses condensed portrait-mode layout.
    For very large collections (>2000), groups by denomination with subtotals.
    Photos are only embedded for smaller collections where it won't time out.
    """
    enriched_coins = ctx['enriched_coins']
    include_photos = ctx['report_request'].get('include_photos', True)
    total = len(enriched_coins)
    story: list = []

    story.append(Paragraph('Itemized Coin Inventory', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=4))
    story.append(Paragraph(
        f'Total coins documented: {total:,}  |  '
        f'Estimated collection FMV: ${ctx["summary"]["total_fmv"]:,.2f}  |  '
        f'Report generated: {ctx["report_request"].get("report_date", "")}',
        st['BodySmall'],
    ))
    story.append(Spacer(1, 8))

    # ── Very large collection — grouped view ───────────────────────────────────
    if total > VERY_LARGE_COLLECTION:
        story += _coin_table_grouped(enriched_coins, st)
        story.append(PageBreak())
        return story

    # ── Large collection — condensed portrait, no photos ──────────────────────
    if total > LARGE_COLLECTION:
        story += _coin_table_condensed(enriched_coins, st)
        story.append(PageBreak())
        return story

    # ── Standard collection — full landscape table ─────────────────────────────
    # Decide whether to attempt photo fetching
    fetch_photos = include_photos and total <= 300

    rows = _build_coin_rows(enriched_coins, st, fetch_photos=fetch_photos)

    if not rows:
        story.append(Paragraph('No coin records found in this collection.', st['Body']))
        story.append(PageBreak())
        return story

    # ── Headers ────────────────────────────────────────────────────────────────
    headers = [
        '#', 'Year', 'Mint', 'Denom.', 'Series', 'Grade', 'Holder',
        'Svc', 'Cert #', 'Metal', 'Country',
        'Purch. Date', 'Cost', 'Est. FMV', 'Melt',
        'Storage', 'Beneficiary', 'Notes', 'Appr?',
    ]
    if fetch_photos:
        headers = ['Photo'] + headers

    col_widths_landscape = _landscape_col_widths(fetch_photos)

    all_rows = [headers] + rows

    # ── Chunk the rows to avoid PDF memory issues ──────────────────────────────
    CHUNK = 150
    for chunk_start in range(0, len(all_rows), CHUNK + 1):
        chunk = all_rows[0:1] + all_rows[max(1, chunk_start):chunk_start + CHUNK + 1]
        if len(chunk) <= 1:
            break
        t = Table(chunk, colWidths=col_widths_landscape, repeatRows=1)
        style_cmds = _ts_base() + [
            ('FONTSIZE', (0, 0), (-1, -1), 6.5),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('TOPPADDING',    (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]
        # Highlight appraisal-needed rows
        for i, row in enumerate(chunk[1:], start=1):
            # Last column is the appraisal flag
            appr_col = -1
            if isinstance(row, list) and len(row) > 0:
                appr_val = row[appr_col]
                if appr_val == 'Y' or (hasattr(appr_val, 'text') and 'Y' in str(appr_val)):
                    style_cmds.append(('BACKGROUND', (0, i), (-1, i), HexColor('#FFF9C4')))
        t.setStyle(TableStyle(style_cmds))
        story.append(t)
        story.append(Spacer(1, 4))

    story.append(PageBreak())
    return story


def _build_coin_rows(coins: list, st: dict, fetch_photos: bool) -> list:
    """Build individual data rows for the full coin table."""
    rows = []
    for idx, coin in enumerate(coins, start=1):
        fmv    = coin.get('_fmv')
        melt   = coin.get('_melt')
        cost   = coin.get('_cost')
        appr   = 'Y' if coin.get('_needs_appraisal') else ''
        photo_cell = ''

        if fetch_photos:
            url = (
                coin.get('image_url', '') or
                coin.get('Image URL', '') or
                coin.get('photo_url', '')
            )
            img_bytes = fetch_image_bytes(url) if url else None
            if img_bytes:
                try:
                    photo_cell = Image(BytesIO(img_bytes), width=THUMB_W, height=THUMB_H)
                except Exception:
                    photo_cell = ''

        def _v(key1, key2='', fallback=''):
            return str(coin.get(key1, coin.get(key2, fallback)) or fallback)

        row = [
            str(idx),
            _v('Year', 'year'),
            _v('Mint Mark', 'mint_mark'),
            _v('Denomination', 'denomination'),
            _v('Series', 'series'),
            _v('Grade', 'grade'),
            _v('Holder Type', 'holder_type'),
            _v('Grading Service', 'grading_service'),
            _v('Cert Number', 'cert_number'),
            _v('Metal', 'metal'),
            _v('Country', 'country'),
            _v('Purchase Date', 'purchase_date'),
            f'${cost:,.0f}' if cost is not None else '',
            f'${fmv:,.0f}' if fmv is not None else '—',
            f'${melt:,.2f}' if melt is not None else '',
            _v('Storage Location', 'storage_location'),
            coin.get('_beneficiary', '') or '',
            coin.get('_estate_notes', '') or '',
            appr,
        ]

        if fetch_photos:
            row = [photo_cell] + row

        rows.append(row)
    return rows


def _landscape_col_widths(with_photo: bool) -> list:
    """Return column widths for landscape coin table (10 × 7.5 in printable)."""
    # Total available: landscape letter = 11in wide, minus 2×0.65in margin = 9.7in
    w = [
        0.22,  # #
        0.35,  # Year
        0.28,  # Mint
        0.55,  # Denom
        0.75,  # Series
        0.38,  # Grade
        0.45,  # Holder
        0.35,  # Svc
        0.55,  # Cert #
        0.35,  # Metal
        0.50,  # Country
        0.55,  # Purch Date
        0.45,  # Cost
        0.50,  # FMV
        0.45,  # Melt
        0.70,  # Storage
        0.65,  # Beneficiary
        0.90,  # Notes
        0.32,  # Appr?
    ]
    widths = [x * inch for x in w]
    if with_photo:
        widths = [0.65 * inch] + widths
    return widths


def _coin_table_condensed(coins: list, st: dict) -> list:
    """Portrait condensed table for collections 500-2000 coins."""
    story = []
    story.append(Paragraph(
        f'Condensed inventory ({len(coins):,} coins). '
        'For collections of this size, key fields are shown. '
        'Full data available in the Numista.AI app.',
        st['BodySmall'],
    ))
    story.append(Spacer(1, 6))

    headers = ['#', 'Year', 'Mint', 'Denomination', 'Series', 'Grade', 'Cert #',
               'Cost', 'Est. FMV', 'Melt', 'Beneficiary', 'Appr?']
    col_w = [0.28, 0.42, 0.30, 0.90, 1.10, 0.40, 0.65,
             0.52, 0.55, 0.52, 0.90, 0.40]
    col_widths = [x * inch for x in col_w]

    rows_data = [headers]
    for idx, coin in enumerate(coins, start=1):
        fmv  = coin.get('_fmv')
        melt = coin.get('_melt')
        cost = coin.get('_cost')
        rows_data.append([
            str(idx),
            str(coin.get('Year', coin.get('year', '')) or ''),
            str(coin.get('Mint Mark', coin.get('mint_mark', '')) or ''),
            str(coin.get('Denomination', coin.get('denomination', '')) or ''),
            str(coin.get('Series', coin.get('series', '')) or ''),
            str(coin.get('Grade', coin.get('grade', '')) or ''),
            str(coin.get('Cert Number', coin.get('cert_number', '')) or ''),
            f'${cost:,.0f}' if cost is not None else '',
            f'${fmv:,.0f}' if fmv is not None else '—',
            f'${melt:,.2f}' if melt is not None else '',
            str(coin.get('_beneficiary', '') or ''),
            'Y' if coin.get('_needs_appraisal') else '',
        ])

    CHUNK = 200
    for i in range(0, len(rows_data) - 1, CHUNK):
        chunk = rows_data[0:1] + rows_data[max(1, i):i + CHUNK + 1]
        if len(chunk) <= 1:
            break
        t = Table(chunk, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle(_ts_base() + [
            ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ]))
        story.append(t)
        story.append(Spacer(1, 4))

    return story


def _coin_table_grouped(coins: list, st: dict) -> list:
    """Group table by denomination with subtotals for very large collections."""
    story = []
    story.append(Paragraph(
        f'Collection of {len(coins):,} coins — displayed by denomination with subtotals. '
        'Individual items available in the Numista.AI app. '
        'A complete line-item inventory is available as a supplemental CSV export.',
        st['Body'],
    ))
    story.append(Spacer(1, 8))

    # Group by denomination
    groups: dict[str, list] = {}
    for coin in coins:
        denom = str(
            coin.get('Denomination', coin.get('denomination', 'Unknown')) or 'Unknown'
        ).strip() or 'Unknown'
        groups.setdefault(denom, []).append(coin)

    for denom, group_coins in sorted(groups.items()):
        story.append(Paragraph(denom, st['H3']))
        count = len(group_coins)
        total_fmv = sum((c.get('_fmv') or 0.0) for c in group_coins)
        total_cost = sum((c.get('_cost') or 0.0) for c in group_coins)
        needs_appr = sum(1 for c in group_coins if c.get('_needs_appraisal'))

        summary_data = [
            ['Coins', 'Total FMV', 'Total Cost', 'Need Appraisal'],
            [f'{count:,}', f'${total_fmv:,.0f}', f'${total_cost:,.0f}', f'{needs_appr}'],
        ]
        summ_t = Table(summary_data, colWidths=[1.5 * inch] * 4)
        summ_t.setStyle(TableStyle(_ts_base()))
        story.append(summ_t)
        story.append(Spacer(1, 6))

        # Show up to 20 coins per denomination inline
        sample = sorted(group_coins, key=lambda c: (c.get('_fmv') or 0.0), reverse=True)[:20]
        sample_data = [['Year', 'Mint', 'Grade', 'Cert #', 'Est. FMV', 'Beneficiary', 'Appr?']]
        for coin in sample:
            fmv = coin.get('_fmv')
            sample_data.append([
                str(coin.get('Year', coin.get('year', '')) or ''),
                str(coin.get('Mint Mark', coin.get('mint_mark', '')) or ''),
                str(coin.get('Grade', coin.get('grade', '')) or ''),
                str(coin.get('Cert Number', coin.get('cert_number', '')) or ''),
                f'${fmv:,.0f}' if fmv is not None else '—',
                str(coin.get('_beneficiary', '') or ''),
                'Y' if coin.get('_needs_appraisal') else '',
            ])
        if len(group_coins) > 20:
            sample_data.append([
                f'… and {len(group_coins) - 20:,} more', '', '', '', '', '', '',
            ])

        t = Table(
            sample_data,
            colWidths=[0.6, 0.45, 0.55, 0.85, 0.75, 1.5, 0.45],
            hAlign='LEFT',
        )
        t.setStyle(TableStyle(_ts_base() + [('FONTSIZE', (0, 0), (-1, -1), 7)]))
        story.append(t)
        story.append(Spacer(1, 10))

    return story


def _appraisal_section(ctx: dict, st: dict) -> list:
    """Build the Coins Requiring Professional Appraisal section."""
    coins_needing = ctx['coins_needing_appraisal']
    narrative = ctx['narrative']
    story: list = []

    story.append(Paragraph('Coins Requiring Professional Appraisal', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=6))
    story.append(Paragraph(narrative.get('appraiser_guidance', ''), st['Body']))
    story.append(Spacer(1, 6))

    story.append(_info_box(
        f'<b>IRS Requirement:</b> Any coin (or group of similar coins) with an estimated '
        f'fair market value of ${IRS_THRESHOLD:,.0f} or more requires a qualified appraisal '
        f'under IRC §170(f)(11) and Treasury Regulation §1.170A-17 for inclusion on '
        f'IRS Form 706 (federal estate tax) or state equivalents. '
        f'The appraiser must be qualified and the appraisal must meet the "qualified appraisal" '
        f'definition. Appraisers should hold credentials from PCGS, NGC, ASA, or ISA.',
        st['InfoText'], bg=BOX_BG, border=NAVY,
    ))
    story.append(Spacer(1, 8))

    if not coins_needing:
        story.append(Paragraph(
            f'No individual coins in this collection currently have an AI-estimated FMV '
            f'at or above the ${IRS_THRESHOLD:,.0f} IRS threshold. '
            'However, a comprehensive numismatic appraisal is still recommended for '
            'formal estate and probate purposes.',
            st['Body'],
        ))
        story.append(PageBreak())
        return story

    story.append(Paragraph(
        f'{len(coins_needing):,} coin(s) have an estimated FMV at or above '
        f'${IRS_THRESHOLD:,.0f}:',
        st['BodySmall'],
    ))
    story.append(Spacer(1, 4))

    appr_data = [['Year', 'Mint', 'Denomination', 'Series', 'Grade', 'Cert #',
                  'Est. FMV', 'Appraiser', 'Reason']]
    for coin in sorted(coins_needing, key=lambda c: (c.get('_fmv') or 0), reverse=True):
        fmv = coin.get('_fmv')
        appr_data.append([
            str(coin.get('Year', coin.get('year', '')) or ''),
            str(coin.get('Mint Mark', coin.get('mint_mark', '')) or ''),
            str(coin.get('Denomination', coin.get('denomination', '')) or ''),
            str(coin.get('Series', coin.get('series', '')) or ''),
            str(coin.get('Grade', coin.get('grade', '')) or ''),
            str(coin.get('Cert Number', coin.get('cert_number', '')) or ''),
            f'${fmv:,.0f}' if fmv is not None else '—',
            str(coin.get('_appraiser_name', '') or 'Not yet assigned'),
            f'Est. FMV ≥ ${IRS_THRESHOLD:,.0f}',
        ])

    col_w = [0.42, 0.32, 0.85, 1.0, 0.42, 0.65, 0.65, 1.2, 1.72]
    appr_table = Table(appr_data, colWidths=[x * inch for x in col_w], repeatRows=1)
    appr_table.setStyle(TableStyle(_ts_base() + [
        ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
    ]))
    story.append(appr_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Note: The AI-estimated values above are preliminary and are not a qualified '
        'appraisal. The actual appraised values may differ materially. This list is '
        'provided as a planning tool only.',
        st['LegalSmall'],
    ))

    story.append(PageBreak())
    return story


def _stepup_section(ctx: dict, st: dict) -> list:
    """Build the stepped-up basis analysis section."""
    summary = ctx['summary']
    state_rules = ctx['state_rules']
    state_code = ctx['state_code']
    rr = ctx['report_request']
    story: list = []

    story.append(Paragraph('Step-Up in Basis Analysis', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=6))

    step_up_text = (
        'Under IRC §1014, when property is inherited, the heir\'s tax basis is "stepped up" '
        '(or down) to the fair market value at the date of death. For a numismatic collection '
        'with significant appreciation, this means heirs may sell the coins immediately after '
        'inheritance without any capital gains tax on the pre-death appreciation. '
        'This benefit is sometimes called the "Angel of Death" provision.'
    )
    story.append(Paragraph(step_up_text, st['Body']))

    if state_rules.get('community_property'):
        story.append(Spacer(1, 4))
        story.append(_info_box(
            f'<b>Community Property Double Step-Up ({state_rules["display_name"]}):</b> '
            f'Under IRC §1014(b)(6), the ENTIRE community property coin collection — '
            f'both spouses\' halves — receives a step-up to FMV at death. '
            f'This is a significant advantage over common-law states where only the '
            f'decedent\'s 50% share steps up.',
            st['InfoText'], bg=BOX_SUCCESS, border=GREEN_GOOD,
        ))

    story.append(Spacer(1, 10))
    story.append(Paragraph('Basis Summary', st['H2']))

    total_fmv = summary['total_fmv']
    total_cost = summary['total_cost_basis']
    unrealized = total_fmv - total_cost
    new_heir_basis = total_fmv  # full step-up

    basis_data = [
        ['Category', 'Total FMV', 'Total Cost Basis', 'Unrealized Gain', 'New Heir Basis (FMV)'],
        [
            'Entire Collection',
            f'${total_fmv:,.2f}',
            f'${total_cost:,.2f}',
            f'${max(0.0, unrealized):,.2f}',
            f'${new_heir_basis:,.2f}',
        ],
    ]

    if state_rules.get('community_property'):
        community_fmv  = total_fmv  # entire collection steps up
        community_cost = total_cost
        basis_data.append([
            'Community Property (Double Step-Up)',
            f'${community_fmv:,.2f}',
            f'${community_cost:,.2f}',
            f'${max(0.0, community_fmv - community_cost):,.2f}',
            f'${community_fmv:,.2f}',
        ])

    basis_table = Table(
        basis_data,
        colWidths=[1.9 * inch, 1.3 * inch, 1.4 * inch, 1.3 * inch, 1.5 * inch],
    )
    basis_table.setStyle(TableStyle(_ts_base() + [
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), BOX_SUCCESS if state_rules.get('community_property') else ROW_ALT),
    ]))
    story.append(basis_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        '<b>Important:</b> This document should be retained by heirs as a basis reference '
        'record. The date-of-death FMV column represents the new cost basis for each heir. '
        'Heirs should obtain a formal qualified appraisal to establish the exact step-up '
        'basis figure for tax reporting purposes.',
        st['Legal'],
    ))

    story.append(PageBreak())
    return story


def _nj_inheritance_section(ctx: dict, st: dict) -> list:
    """Build NJ inheritance tax analysis (NJ only)."""
    rr = ctx['report_request']
    enriched_coins = ctx['enriched_coins']
    state_rules = ctx['state_rules']
    story: list = []

    story.append(Paragraph('NJ Inheritance Tax Analysis', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=6))

    classes = state_rules.get('inheritance_tax_classes', {})

    story.append(_info_box(
        'NJ inheritance tax is assessed on the BENEFICIARY, not the estate. '
        'The tax rate depends entirely on the beneficiary\'s relationship class to the decedent. '
        'Class A beneficiaries (spouse, children, parents) pay 0%. '
        'Class D beneficiaries (friends, cousins, unrelated parties) pay 15–16% on the '
        'entire transferred value above $499. '
        'The estate CANNOT distribute assets to non-Class-A beneficiaries until '
        'NJ tax waivers are issued by the NJ Division of Taxation.',
        st['InfoText'], bg=BOX_WARN_BG, border=BOX_WARN_BORD,
    ))
    story.append(Spacer(1, 8))

    # ── Beneficiary breakdown from report_request ──────────────────────────────
    beneficiaries = rr.get('beneficiaries') or []
    if beneficiaries:
        story.append(Paragraph('Beneficiary Tax Estimates', st['H2']))
        benef_data = [['Beneficiary', 'Relationship', 'Class', 'Items', 'FMV', 'Est. NJ Tax']]
        for b in beneficiaries:
            b_name = b.get('name', 'Unknown')
            b_rel  = b.get('relationship', '')
            # Infer class from relationship keyword
            b_class = _infer_nj_class(b_rel)
            rate = classes.get(b_class, 0.15)
            # FMV for this beneficiary's coins
            b_items = b.get('items', [])
            b_fmv = sum(
                (c.get('_fmv') or 0.0)
                for c in enriched_coins
                if c.get('_beneficiary', '') == b_name or c.get('_doc_id', '') in b_items
            )
            tax_est = (b_fmv - 499.0) * rate if b_fmv > 499 and rate > 0 else 0.0
            benef_data.append([
                b_name, b_rel, f'Class {b_class}',
                str(len(b_items)) if b_items else 'See inventory',
                f'${b_fmv:,.0f}',
                f'${tax_est:,.0f}' if tax_est > 0 else 'Exempt',
            ])
        benef_table = Table(
            benef_data,
            colWidths=[1.6, 1.2, 0.65, 0.9, 0.9, 1.0],
        )
        benef_table.setStyle(TableStyle(_ts_base()))
        story.append(benef_table)
        story.append(Spacer(1, 6))

    story.append(Paragraph(
        'Note: The above NJ inheritance tax estimates are preliminary. '
        'The actual tax is calculated on the final appraised value at date of death, '
        'not AI-estimated values. Consult a NJ estate attorney and the NJ Division of '
        'Taxation for accurate tax computation and waiver procedures.',
        st['LegalSmall'],
    ))

    story.append(PageBreak())
    return story


def _infer_nj_class(relationship: str) -> str:
    """Infer NJ inheritance tax class from a relationship string."""
    rel = relationship.lower()
    if any(k in rel for k in ['spouse', 'child', 'son', 'daughter', 'parent', 'grandchild', 'grandparent']):
        return 'A'
    if any(k in rel for k in ['sibling', 'brother', 'sister', 'in-law']):
        return 'C'
    if any(k in rel for k in ['charity', 'charitable', 'nonprofit', '501']):
        return 'E'
    return 'D'


def _ny_estate_tax_section(ctx: dict, st: dict) -> list:
    """Build NY estate tax analysis section (NY only)."""
    summary = ctx['summary']
    state_rules = ctx['state_rules']
    story: list = []

    story.append(Paragraph('NY Estate Tax Analysis', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=6))

    exemption = state_rules['exemption_2026']
    cliff_threshold = exemption * state_rules['cliff_multiplier']
    total_fmv = summary['total_fmv']
    cliff_warning = summary.get('cliff_warning')

    # ── Cliff warning if triggered ─────────────────────────────────────────────
    if cliff_warning:
        is_over = total_fmv > cliff_threshold
        story.append(_info_box(
            cliff_warning,
            st['WarnText'],
            bg=BOX_ERR_BG if is_over else BOX_WARN_BG,
            border=BOX_ERR_BORD if is_over else BOX_WARN_BORD,
        ))
        story.append(Spacer(1, 8))

    # ── NY tax exposure table ──────────────────────────────────────────────────
    story.append(Paragraph('NY Estate Tax Thresholds (2026)', st['H2']))

    ny_data = [
        ['Item', 'Amount'],
        ['NY Basic Exclusion (2026)', f'${exemption:,.0f}'],
        ['NY Cliff Threshold (105%)', f'${cliff_threshold:,.0f}'],
        ['Collection Estimated FMV', f'${total_fmv:,.0f}'],
        ['FMV vs. Exemption', f'${total_fmv - exemption:,.0f}' if total_fmv > exemption else 'Under exemption'],
        ['FMV vs. Cliff', f'${total_fmv - cliff_threshold:,.0f} OVER CLIFF' if total_fmv > cliff_threshold
                          else f'${cliff_threshold - total_fmv:,.0f} below cliff'],
        ['Collection FMV Triggers Cliff', 'YES — URGENT' if total_fmv > cliff_threshold else
                                           'NO (other estate assets may still trigger it)'],
        ['ET-706 Required', 'Yes — if total gross estate > $7,350,000'],
        ['Filing Deadline', '270 days from date of death (9 months)'],
    ]

    ny_table = Table(ny_data, colWidths=[3.5 * inch, 3.7 * inch])
    ny_ts = _ts_base() + [('ALIGN', (0, 0), (-1, -1), 'LEFT')]
    # Highlight the cliff row red if triggered
    for i, row in enumerate(ny_data):
        if 'OVER CLIFF' in str(row[1]) or 'YES — URGENT' in str(row[1]):
            ny_ts.append(('BACKGROUND', (0, i), (-1, i), BOX_ERR_BG))
            ny_ts.append(('TEXTCOLOR', (0, i), (-1, i), RED_WARN))
            ny_ts.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
    ny_table.setStyle(TableStyle(ny_ts))
    story.append(ny_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph('NY-Specific Planning Notes', st['H2']))
    for note in state_rules.get('special_notes', []):
        story.append(Paragraph(f'• {note}', st['BulletBody']))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'The coin collection value alone does not determine NY estate tax liability — '
        'all assets in the gross estate (real property, financial accounts, retirement '
        'accounts, life insurance, and 3-year gift clawback) are included. '
        'A complete estate tax projection by a NY-licensed estate attorney is essential.',
        st['Legal'],
    ))

    story.append(PageBreak())
    return story


def _attestation_section(ctx: dict, st: dict) -> list:
    """Build the legal attestation / signature block."""
    rr = ctx['report_request']
    mode = ctx['mode']
    story: list = []

    story.append(Paragraph('Legal Attestation', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=6))

    if mode == 'living_inventory':
        attest_text = (
            'I, the undersigned, hereby attest that to the best of my knowledge and belief, '
            'the numismatic collection described in this inventory document accurately '
            'reflects the coins owned by me as of the report date set forth herein. '
            'I acknowledge that the estimated fair market values contained herein were '
            'generated by an artificial intelligence system and do not constitute a '
            'qualified appraisal. I understand that a formal appraisal will be required '
            'for estate tax, insurance, or probate purposes.'
        )
        signer_label = 'Collection Owner'
    else:
        attest_text = (
            'I, the undersigned, hereby attest that to the best of my knowledge and belief, '
            'the numismatic collection described in this estate inventory accurately reflects '
            'the coins owned by the decedent as of the date of death set forth herein. '
            'I acknowledge that the estimated fair market values contained herein were '
            'generated by an artificial intelligence system and do not constitute a '
            'qualified appraisal under IRC §170(f)(11). '
            'I understand that a formal qualified appraisal is required prior to filing '
            'any federal or state estate tax return.'
        )
        signer_label = 'Executor / Personal Representative'

    story.append(Paragraph(attest_text, st['Legal']))
    story.append(Spacer(1, 24))

    # Signature lines
    sig_data = [
        [
            Paragraph(f'<u>{"_" * 45}</u>', st['Legal']),
            Spacer(0.5 * inch, 1),
            Paragraph(f'<u>{"_" * 25}</u>', st['Legal']),
        ],
        [
            Paragraph(signer_label, st['LegalSmall']),
            Spacer(0.5 * inch, 1),
            Paragraph('Date', st['LegalSmall']),
        ],
    ]
    sig_table = Table(
        sig_data, colWidths=[4.0 * inch, 0.3 * inch, 2.9 * inch]
    )
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 24))

    # Notary block (dashed outline)
    notary_text = (
        'STATE OF ________________________  COUNTY OF ________________________\n\n'
        'Subscribed and sworn to before me this _____ day of __________, 20____.\n\n\n'
        'Notary Public: ________________________________     '
        'Commission Expires: ______________\n\n'
        '(NOTARY SEAL)'
    )
    notary_t = Table(
        [[Paragraph(notary_text, st['LegalSmall'])]],
        colWidths=[7.2 * inch],
    )
    notary_t.setStyle(TableStyle([
        ('BOX',           (0, 0), (-1, -1), 1, BORDER_GRAY),
        ('LINEDASH',      (0, 0), (-1, -1), 4, 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('BACKGROUND',    (0, 0), (-1, -1), BOX_BG),
    ]))
    story.append(notary_t)
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        'This inventory was prepared with the assistance of Numista.AI, an artificial '
        'intelligence-powered numismatic collection management platform. '
        'AI-estimated values are for planning reference only and are not a substitute '
        'for a certified professional appraisal.',
        st['LegalSmall'],
    ))

    story.append(PageBreak())
    return story


def _disclaimer_page(ctx: dict, st: dict) -> list:
    """Full disclaimer page."""
    story: list = []

    story.append(Paragraph('Disclaimer and Limitations', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8))

    disc_sections = [
        ('NOT A QUALIFIED APPRAISAL',
         'This document does not constitute a "qualified appraisal" as defined under '
         'IRC §170(f)(11) and Treasury Regulation §1.170A-17. The estimated fair market '
         'values contained herein were generated by an artificial intelligence system '
         'using image analysis and market comparables available at the time of generation. '
         'These estimates have not been prepared by a qualified appraiser and may not '
         'be used to support a deduction on any federal or state tax return without '
         'a formal qualified appraisal.'),

        ('NOT LEGAL OR TAX ADVICE',
         'Nothing in this document constitutes legal or tax advice. The information '
         'provided is for general estate planning reference purposes only. '
         'The owner and any estate representative should consult with an estate attorney '
         'licensed in the applicable jurisdiction and a qualified tax advisor before '
         'making any legal or financial decisions based on this document.'),

        ('AI-ESTIMATED VALUES',
         'Estimated fair market values are generated by Numista.AI using machine learning '
         'models trained on numismatic data, auction records, and dealer price guides. '
         'Actual market values may differ materially. Factors affecting coin value — '
         'including strike quality, eye appeal, surface preservation, and collector '
         'market trends — may not be fully captured by automated analysis. '
         'Professional numismatic appraisal is required for any formal estate, insurance, '
         'or donation valuation.'),

        ('JURISDICTION-SPECIFIC GUIDANCE',
         'The state-specific information in this document is provided as general '
         'background and may not reflect the most current statutes, regulations, or '
         'court rules. Estate law changes frequently. Consult current state statutes '
         'and a licensed estate attorney in the applicable jurisdiction before relying '
         'on any jurisdiction-specific information in this report.'),

        ('CONFIDENTIALITY',
         'This document is prepared for the exclusive use of the named owner, their '
         'estate attorney, and authorized estate representatives. This document contains '
         'sensitive financial information and should not be disclosed to third parties '
         'without the consent of the owner or estate representative. '
         'Numista.AI does not share estate report data with any third party '
         'except as required by law.'),

        ('DATA ACCURACY',
         'The accuracy of this report depends on the accuracy of the coin data '
         'entered into the Numista.AI system. Numista.AI is not responsible for '
         'errors or omissions in coin data entered by the user. '
         'The owner or estate representative is responsible for verifying the '
         'accuracy of all coin records before relying on this report for any purpose.'),
    ]

    # Add NY-specific disclaimer if this is a NY report
    state_code = ctx.get('state_code', '')
    if state_code == 'NY':
        disc_sections.append((
            'NEW YORK — SPECIAL NOTICE',
            'This report was prepared for a New York domiciliary and references '
            'New York State estate tax rules in effect as of the date of generation. '
            'The New York "cliff rule" (Tax Law §952): if the gross estate (including '
            'this collection and all other assets) exceeds 105% of the New York basic '
            'exclusion amount ($7,717,500 for 2026), the ENTIRE gross estate — not just '
            'the excess — becomes subject to New York estate tax. Gifts made within '
            '3 years of death are added back to the gross estate for cliff calculation '
            'purposes (Tax Law §954(a)(3)). The New York estate tax return (ET-706) '
            'and Surrogate\'s Court inventory (SCPA §2102 / 22 NYCRR §207.20) are '
            'due within 9 months of the date of death. This coin collection alone '
            f'does not trigger the cliff (FMV: ${ctx.get("total_fmv", 0):,.0f} vs. '
            'cliff threshold of $7,717,500), but the collection value must be '
            'combined with all other estate assets to determine total exposure. '
            'Consult a New York estate attorney before filing any tax returns or '
            'probate inventory.'
        ))

    for title, body in disc_sections:
        story.append(Paragraph(title, st['H3']))
        story.append(Paragraph(body, st['Legal']))
        story.append(Spacer(1, 8))

    story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER_GRAY, spaceAfter=6))
    story.append(Paragraph(
        f'Report generated by Numista.AI  |  '
        f'© {datetime.utcnow().year} SGroup LLC  |  '
        f'All rights reserved  |  '
        f'www.numista.ai',
        st['BodyTiny'],
    ))

    story.append(PageBreak())
    return story


def _attorney_page(ctx: dict, st: dict) -> list:
    """Attorney access page with QR code."""
    qr_bytes = ctx.get('qr_bytes')
    attorney_url = ctx.get('attorney_portal_url', 'https://app.numista.ai')
    rr = ctx['report_request']
    attorney = rr.get('attorney_name', '')
    attorney_email = rr.get('attorney_email', '')
    story: list = []

    story.append(Paragraph('Attorney Access', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph(
        'The complete numismatic collection database — including high-resolution '
        'coin photographs, detailed grading information, purchase documentation, '
        'and AI analysis — is available to authorized estate counsel through the '
        'Numista.AI attorney portal.',
        st['Body'],
    ))
    story.append(Spacer(1, 10))

    # QR code + URL side by side
    if qr_bytes:
        try:
            qr_img = Image(BytesIO(qr_bytes), width=1.5 * inch, height=1.5 * inch)
            url_para = Paragraph(
                f'<b>Attorney Portal URL:</b><br/>'
                f'<font color="navy">{attorney_url}</font><br/><br/>'
                f'Scan the QR code or visit the URL above to access '
                f'the complete collection database.<br/><br/>'
                f'<b>Link validity:</b> 90 days from report generation date.',
                st['Body'],
            )
            access_table = Table(
                [[qr_img, url_para]],
                colWidths=[2.0 * inch, 5.2 * inch],
            )
            access_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(access_table)
        except Exception:
            story.append(Paragraph(f'Attorney Portal: {attorney_url}', st['Body']))
    else:
        story.append(Paragraph(f'Attorney Portal: {attorney_url}', st['Body']))

    story.append(Spacer(1, 16))

    if attorney:
        story.append(Paragraph(f'Prepared for: {attorney}', st['Body']))
    if attorney_email:
        story.append(Paragraph(f'Attorney email: {attorney_email}', st['Body']))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER_GRAY, spaceAfter=6))
    story.append(Paragraph(
        'Numista.AI  —  Professional Numismatic Collection Management and Estate Planning\n'
        'www.numista.ai  |  support@numista.ai\n'
        '© SGroup LLC. All rights reserved. This platform does not provide legal or tax advice.',
        st['BodyTiny'],
    ))

    return story


def _liquidation_playbook_section(ctx: dict, st: dict) -> list:
    """Build the Heir Liquidation Playbook section."""
    narrative = ctx['narrative']
    story: list = []

    story.append(Paragraph('Heir Liquidation Playbook', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8))

    playbook_text = narrative.get('liquidation_playbook', '')
    if playbook_text:
        story.append(Paragraph(playbook_text, st['Body']))
        story.append(Spacer(1, 10))

    # Add a styled warning callout box with liquidation precautions
    warning_content = (
        "<b>CRITICAL INHERITANCE PRECAUTIONS:</b><br/>"
        "• <b>Do NOT Clean Coins:</b> Cleaning, polishing, or dipping coins chemically can permanently destroy their numismatic value, "
        "often reducing their worth by 50% to 90%. Leave them exactly as they are found.<br/>"
        "• <b>Avoid Pawn Shops:</b> Pawn shops and general jewelry buyers typically offer 10% to 30% of fair market value. Use specialized coin auction channels.<br/>"
        "• <b>Keep in Holders:</b> If a coin is in a plastic holder or cert cardboard sleeve, do not remove it. Slabbed coins carry certified grades that dictate value."
    )
    story.append(_info_box(warning_content, st['WarnText'], bg=BOX_WARN_BG, border=BOX_WARN_BORD))
    story.append(Spacer(1, 12))

    story.append(PageBreak())
    return story


def _division_plan_section(ctx: dict, st: dict) -> list:
    """Build the Equitable Division Plan section if multiple heirs exist."""
    division_results = ctx.get('division_results')
    if not division_results:
        return []

    story: list = []
    story.append(Paragraph('Equitable Division Plan', st['H1']))
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph(
        'Based on the collection\'s total value and the list of beneficiaries, the Smart Division Engine '
        'has partitioned the coins to minimize variance in total lot value. '
        'Manually locked assignments specified by the owner have been respected first.',
        st['Body'],
    ))
    story.append(Spacer(1, 10))

    # Summary Table
    heirs = ctx['report_request'].get('beneficiaries', [])
    heir_names = {heir['id']: heir['name'] for heir in heirs}
    totals = division_results['heir_totals']
    lots = division_results['heir_lots']

    avg_value = sum(totals.values()) / len(heirs) if heirs else 0.0

    summary_rows = [['Beneficiary / Heir', 'Coins Assigned', 'Total Lot Value', 'Variance from Avg.', 'Cash Adjustment']]
    
    for hid, total_val in totals.items():
        coin_count = len(lots.get(hid, []))
        name = heir_names.get(hid, 'Unknown Heir')
        
        diff = total_val - avg_value
        pct_diff = (diff / avg_value * 100) if avg_value > 0 else 0.0
        sign = '+' if diff >= 0 else ''
        
        offset = -diff
        offset_str = f"+${abs(offset):,.2f} cash" if offset >= 0 else f"-${abs(offset):,.2f} cash"
        
        summary_rows.append([
            name,
            f'{coin_count:,} coins',
            f'${total_val:,.2f}',
            f'{sign}{pct_diff:.1f}%',
            offset_str,
        ])

    summary_rows.append([
        'Average / Ideal Split',
        '—',
        f'${avg_value:,.2f}',
        '0.0%',
        'Balanced',
    ])

    summary_table = Table(summary_rows, colWidths=[2.2 * inch, 1.2 * inch, 1.4 * inch, 1.2 * inch, 1.2 * inch])
    summary_table.setStyle(TableStyle(_ts_base() + [
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('LINEABOVE', (0, -1), (-1, -1), 1.0, NAVY),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(Paragraph('Division Summary', st['H2']))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Detail table: list of coins assigned to each heir
    story.append(Paragraph('Beneficiary Lot Allocations', st['H2']))
    story.append(Paragraph('Below is the itemized list of coins assigned to each heir lot.', st['BodySmall']))
    story.append(Spacer(1, 6))

    for heir in heirs:
        hid = heir['id']
        heir_coins = lots.get(hid, [])
        story.append(Paragraph(f"<b>Lot for {heir['name']}</b> ({len(heir_coins)} coins, Total: ${totals[hid]:,.2f})", st['H3']))
        
        if not heir_coins:
            story.append(Paragraph('No coins assigned to this lot.', st['BodySmall']))
            story.append(Spacer(1, 6))
            continue
            
        coin_data = [['Year', 'Mint', 'Denomination', 'Grade', 'Est. FMV', 'Locked?']]
        for c in heir_coins[:100]:  # Limit to top 100 per heir in PDF to prevent page explosion
            is_locked = 'Yes' if c.get('_division_locked') else 'No'
            coin_data.append([
                str(c.get('Year', c.get('year', '')) or ''),
                str(c.get('Mint Mark', c.get('mint_mark', '')) or ''),
                str(c.get('Denomination', c.get('denomination', '')) or ''),
                str(c.get('Grade', c.get('grade', '')) or ''),
                f"${c.get('_fmv', 0.0):,.2f}",
                is_locked,
            ])
            
        if len(heir_coins) > 100:
            coin_data.append([
                f"… and {len(heir_coins) - 100} more coins (view full list in portal)", "", "", "", "", "",
            ])
            
        t = Table(coin_data, colWidths=[0.8 * inch, 0.8 * inch, 2.2 * inch, 1.0 * inch, 1.4 * inch, 1.0 * inch], hAlign='LEFT')
        t.setStyle(TableStyle(_ts_base() + [
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    story.append(PageBreak())
    return story


# ─────────────────────────────────────────────────────────────────────────────
# DATE FORMAT HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_date(iso_str: str | None) -> str:
    """Format an ISO date string to 'Month DD, YYYY'. Returns original string if unparseable."""
    if not iso_str:
        return ''
    try:
        d = date.fromisoformat(str(iso_str)[:10])
        return d.strftime('%B %d, %Y')
    except Exception:
        return str(iso_str)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PDF BUILD FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def build_estate_pdf(ctx: dict) -> bytes:
    """
    Build a complete estate report PDF from the given context dict.

    Args:
        ctx: Dict containing:
            report_request  — original request dict
            state_rules     — dict from STATE_RULES
            state_code      — 'NY', 'NC', etc.
            mode            — 'living_inventory' or 'estate_settlement'
            summary         — output of build_collection_summary()
            narrative       — output of generate_ai_narrative()
            enriched_coins  — list of enriched coin dicts
            coins_needing_appraisal — filtered list
            qr_bytes        — QR code PNG bytes or None
            attorney_portal_url — str
            estate_profile  — dict

    Returns:
        PDF as bytes.
    """
    buf = BytesIO()
    rr = ctx['report_request']
    owner = rr.get('owner_name', 'Estate Owner')
    mode  = ctx['mode']
    state_code = ctx['state_code']

    # ── Page number tracking ───────────────────────────────────────────────────
    total_pages_ref = [0]
    decor = _PageDecor(owner_name=owner, mode=mode, total_pages_ref=total_pages_ref)

    # ── Styles ─────────────────────────────────────────────────────────────────
    st = _styles()

    # ── We use a two-pass approach: build story → measure page count → rebuild ─
    # For simplicity, we do a single pass and use an onLaterPages callback.
    # Total page count is set via a post-build hook.

    doc = SimpleDocTemplate(
        buf,
        pagesize=PAGE_PORTRAIT,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN_BOTTOM,
        title=f'Estate Inventory — {owner}',
        author='Numista.AI',
        subject='Numismatic Collection Estate Report',
        creator='Numista.AI | SGroup LLC',
    )

    # ── Build story (list of Flowables) ───────────────────────────────────────
    story: list = []

    story += _cover_page(ctx, st)
    story += _toc_page(ctx, st)
    story += _executive_summary(ctx, st)
    story += _state_guidance_section(ctx, st)
    story += _liquidation_playbook_section(ctx, st)
    story += _division_plan_section(ctx, st)
    story += _coin_table_section(ctx, st)
    story += _appraisal_section(ctx, st)
    story += _stepup_section(ctx, st)

    if state_code == 'NJ':
        story += _nj_inheritance_section(ctx, st)
    if state_code == 'NY':
        story += _ny_estate_tax_section(ctx, st)

    story += _attestation_section(ctx, st)
    story += _disclaimer_page(ctx, st)
    story += _attorney_page(ctx, st)

    # ── First pass: build to get page count ────────────────────────────────────
    first_buf = BytesIO()
    first_doc = SimpleDocTemplate(
        first_buf,
        pagesize=PAGE_PORTRAIT,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN_BOTTOM,
        title=f'Estate Inventory — {owner}',
        author='Numista.AI',
        subject='Numismatic Collection Estate Report',
        creator='Numista.AI | SGroup LLC',
    )

    # We need page count for footers.  Build once with a dummy total.
    page_counter = [0]

    def _on_page(canvas, doc_obj):
        page_counter[0] = max(page_counter[0], doc_obj.page)
        decor.draw_footer(canvas, doc_obj)
        if doc_obj.page == 1:
            decor.draw_cover_footer(canvas, doc_obj)

    # Build the real document (single pass with page count from first build if possible)
    # For production correctness we do a genuine two-pass:
    try:
        first_doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
        total_pages_ref[0] = page_counter[0]
    except Exception as e:
        log.warning(f'[estate] First PDF pass failed (non-fatal, continuing): {e}')
        total_pages_ref[0] = 99  # fallback

    # ── Second pass: build with correct total page count ───────────────────────
    story2: list = []
    story2 += _cover_page(ctx, st)
    story2 += _toc_page(ctx, st)
    story2 += _executive_summary(ctx, st)
    story2 += _state_guidance_section(ctx, st)
    story2 += _liquidation_playbook_section(ctx, st)
    story2 += _division_plan_section(ctx, st)
    story2 += _coin_table_section(ctx, st)
    story2 += _appraisal_section(ctx, st)
    story2 += _stepup_section(ctx, st)

    if state_code == 'NJ':
        story2 += _nj_inheritance_section(ctx, st)
    if state_code == 'NY':
        story2 += _ny_estate_tax_section(ctx, st)

    story2 += _attestation_section(ctx, st)
    story2 += _disclaimer_page(ctx, st)
    story2 += _attorney_page(ctx, st)

    doc.build(story2, onFirstPage=_on_page, onLaterPages=_on_page)

    pdf_bytes = buf.getvalue()
    if len(pdf_bytes) < 1000:
        # Something went wrong — try returning first build
        log.error('[estate] Second PDF pass produced tiny output; falling back to first pass.')
        pdf_bytes = first_buf.getvalue()

    log.info(f'[estate] PDF complete: {len(pdf_bytes):,} bytes')
    return pdf_bytes
