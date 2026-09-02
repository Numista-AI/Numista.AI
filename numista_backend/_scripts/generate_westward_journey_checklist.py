"""
generate_westward_journey_checklist.py
=======================================
Generates the Numista.AI native-format printable checklist PDF for the
Westward Journey Nickel Series(tm) (2004-2005).

Authorized under: American 5-Cent Coin Design Continuity Act of 2003
                  Public Law 108-15; 31 U.S.C. Section 5112(p)

Column layout (per NUMISTA_AI_CHECKLIST_DESIGN_SPEC.md "Schema B" grouped format):
  Year / Design  |  P  |  D  |  S Proof  |  P Satin(dagger)  |  D Satin(dagger)  |  Notes / QTY

Row model -- 4 design rows x columns (12 live cells + 4 N/A satin cells for 2004):
  2004 Peace Medal     | [] | [] | []       | N/A               | N/A               |
  2004 Keelboat        | [] | [] | []       | N/A               | N/A               |
  2005 American Bison  | [] | [] | []       | []                | []                |
  2005 Ocean in View!  | [] | [] | []       | []                | []                |

Mintage sources:
  2004 Peace Medal P:    361,440,000   (US Mint Annual Report 2004)
  2004 Peace Medal D:    372,000,000   (US Mint Annual Report 2004)
  2004 Peace Medal S:    2,965,422     (US Mint Annual Report 2004 -- Proof Set only)
  2004 Keelboat P:       366,720,000   (US Mint Annual Report 2004)
  2004 Keelboat D:       344,880,000   (US Mint Annual Report 2004)
  2004 Keelboat S:       2,965,422     (US Mint Annual Report 2004 -- shared Proof Set run)
  2005 American Bison P: 448,320,000   (US Mint Annual Report 2005)
  2005 American Bison D: 487,680,000   (PCGS CoinFacts #4159 -- corrected from prior draft)
  2005 American Bison S: 3,344,679     (US Mint Annual Report 2005)
  2005 American Bison P-Satin: 1,160,000  (US Mint Uncirculated Set 2005)
  2005 American Bison D-Satin: 1,160,000  (US Mint Uncirculated Set 2005)
  2005 Ocean in View P:  394,080,000   (US Mint Annual Report 2005)
  2005 Ocean in View D:  411,120,000   (US Mint Annual Report 2005)
  2005 Ocean in View S:  3,344,679     (US Mint Annual Report 2005)
  2005 Ocean in View P-Satin: 1,160,000   (US Mint Uncirculated Set 2005)
  2005 Ocean in View D-Satin: 1,160,000   (US Mint Uncirculated Set 2005)

  Note: 2004-S Peace Medal and Keelboat share the same Proof Set production run
  of 2,965,422. Both designs appear in every 2004 Proof Set.

  Note: The 2005-D American Bison "Speared Bison" die-gouge variety (PCGS FS-901)
  is a die error within the standard 2005-D mintage and is NOT a separate official
  program slot. Record it in the Notes column if owned.

Usage:
    python generate_westward_journey_checklist.py

Output:
    numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf
    (gitignored -- serve from GCS like all other checklists)

Requirements:
    pip install reportlab
"""

import sys
import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

sys.stdout.reconfigure(encoding='utf-8')

# ── Output path ───────────────────────────────────────────────────────────────
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
)
OUTPUT_DIR = os.path.join(REPO_ROOT, 'numista_mobile', '_checklists_source')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'westward_journey_nickels_checklist.pdf')

# ── Palette (matches existing Numista.AI checklists) ─────────────────────────
BLUE_DARK    = colors.HexColor('#1a3a6b')   # Header text / borders
BLUE_MID     = colors.HexColor('#2c5f9e')   # Sub-header background
BLUE_LIGHT   = colors.HexColor('#dce9f7')   # Alternate row tint
GREY_HEADER  = colors.HexColor('#e8e8e8')   # Column header background
GREY_BORDER  = colors.HexColor('#aaaaaa')   # Table cell border
GREY_NA      = colors.HexColor('#cccccc')   # N/A cell background
ORANGE_MINT  = colors.HexColor('#c45a00')   # Mint-mark callout color
BLACK        = colors.black
WHITE        = colors.white

# ── Checkbox helper ───────────────────────────────────────────────────────────
def _checkbox(is_na: bool = False) -> str:
    """Return the cell content: blank square or 'N/A' label."""
    if is_na:
        return 'N/A'
    # Unicode open square -- visually clear, PDF-safe in Helvetica
    return '\u25a1'   # □

# ── Coin data (16 slots, 4 design rows) ──────────────────────────────────────
# Columns: design_label, p_mintage, d_mintage, s_mintage,
#          p_satin_mintage (None = N/A), d_satin_mintage (None = N/A)
COIN_ROWS = [
    {
        'year': '2004',
        'name': 'Peace Medal\n(Louisiana Purchase)',
        'obverse': '1938 Classic Schlag Portrait',
        'p_mint':  '361,440,000',
        'd_mint':  '372,000,000',
        's_mint':  '2,965,422',
        'p_satin': None,   # 2004 had NO Satin Finish Mint Set
        'd_satin': None,
    },
    {
        'year': '2004',
        'name': 'Keelboat\n(Missouri River)',
        'obverse': '1938 Classic Schlag Portrait',
        'p_mint':  '366,720,000',
        'd_mint':  '344,880,000',
        's_mint':  '2,965,422',
        'p_satin': None,
        'd_satin': None,
    },
    {
        'year': '2005',
        'name': 'American Bison',
        'obverse': '2005 One-Year Houdon/Fitzgerald Portrait\n(Handwritten "Liberty" script)',
        'p_mint':  '448,320,000',
        'd_mint':  '487,680,000',   # PCGS CoinFacts #4159 -- corrected
        's_mint':  '3,344,679',
        'p_satin': '1,160,000',    # US Mint Uncirculated Set 2005
        'd_satin': '1,160,000',
    },
    {
        'year': '2005',
        'name': 'Ocean in View!\n("O! The joy!")',
        'obverse': '2005 One-Year Houdon/Fitzgerald Portrait\n(Handwritten "Liberty" script)',
        'p_mint':  '394,080,000',
        'd_mint':  '411,120,000',
        's_mint':  '3,344,679',
        'p_satin': '1,160,000',
        'd_satin': '1,160,000',
    },
]

# ── Column widths (letter = 8.5in, margins 0.5in each side → 7.5in usable) ──
# Year | Design         | P    | D    | S Proof | P Satin | D Satin | Notes
COL_WIDTHS = [
    0.50 * inch,   # Year
    2.00 * inch,   # Design
    0.52 * inch,   # P
    0.52 * inch,   # D
    0.68 * inch,   # S Proof
    0.68 * inch,   # P Satin†
    0.68 * inch,   # D Satin†
    1.42 * inch,   # Notes / QTY
]  # Total: 7.00in -- fits inside 7.5in with breathing room


def build_pdf(output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.5 * inch,
        title='Westward Journey Nickel Series(tm) Checklist',
        author='Numista.AI System of Record',
    )

    styles = getSampleStyleSheet()
    today  = date.today().strftime('%Y-%m-%d')

    # ── Custom paragraph styles ───────────────────────────────────────────────
    h1 = ParagraphStyle('h1',
        fontName='Helvetica-Bold', fontSize=14,
        textColor=BLUE_DARK, spaceAfter=2)
    h2 = ParagraphStyle('h2',
        fontName='Helvetica-Bold', fontSize=10,
        textColor=BLUE_DARK, spaceAfter=2)
    meta = ParagraphStyle('meta',
        fontName='Helvetica', fontSize=7.5,
        textColor=colors.HexColor('#555555'), spaceAfter=0)
    instruction = ParagraphStyle('instruction',
        fontName='Helvetica-Oblique', fontSize=8,
        textColor=colors.HexColor('#444444'), spaceAfter=4)
    footnote_style = ParagraphStyle('footnote',
        fontName='Helvetica', fontSize=7,
        textColor=colors.HexColor('#444444'), spaceAfter=2, leading=9)
    cell_design = ParagraphStyle('cell_design',
        fontName='Helvetica-Bold', fontSize=8.5,
        textColor=BLACK, leading=11)
    cell_obverse = ParagraphStyle('cell_obverse',
        fontName='Helvetica-Oblique', fontSize=6.5,
        textColor=colors.HexColor('#555555'), leading=8)
    cell_mintage = ParagraphStyle('cell_mintage',
        fontName='Helvetica', fontSize=6.5,
        textColor=colors.HexColor('#333333'), leading=8)
    cell_center = ParagraphStyle('cell_center',
        fontName='Helvetica', fontSize=14,
        textColor=BLUE_DARK, alignment=TA_CENTER)
    cell_na = ParagraphStyle('cell_na',
        fontName='Helvetica-Oblique', fontSize=7,
        textColor=colors.HexColor('#888888'), alignment=TA_CENTER)
    header_cell = ParagraphStyle('header_cell',
        fontName='Helvetica-Bold', fontSize=8,
        textColor=BLUE_DARK, alignment=TA_CENTER, leading=10)

    story = []

    # ── Page Header ───────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('Numista.AI Checklist', h1),
        Paragraph(f'Generated: {today}', ParagraphStyle('right',
            fontName='Helvetica', fontSize=7.5,
            textColor=colors.HexColor('#555555'), alignment=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=[5.5 * inch, 2.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=1.5,
                            color=BLUE_DARK, spaceAfter=4))

    # ── Program Title ─────────────────────────────────────────────────────────
    story.append(Paragraph(
        'WESTWARD JOURNEY NICKEL SERIES\u2122 &nbsp; (2004\u20132005)', h2))
    story.append(Paragraph(
        'Authorized by: <i>American 5-Cent Coin Design Continuity Act of 2003</i> '
        '(Public Law 108-15; 31&nbsp;U.S.C. \u00a7&nbsp;5112(p)) &nbsp;|&nbsp; '
        'Category: Circulating Coin Program &nbsp;|&nbsp; '
        'Denomination: Five Cents (Cupro-Nickel Clad)',
        meta))
    story.append(Spacer(1, 4))

    # ── Mint Mark Location Box ────────────────────────────────────────────────
    mm_data = [[
        Paragraph(
            '<b>Mint Mark Location:</b> Right side of Jefferson\'s portrait on the '
            '<b>obverse</b> (no mint mark on 1965\u20131967 coins \u2014 none issued '
            'for this series). &nbsp; '
            '<b>2005 obverse:</b> One-year-only close-up portrait of Jefferson by '
            'Joe Fitzgerald/Don Everhart based on the 1789 Houdon bust, with '
            'handwritten <i>"Liberty"</i> script from Jefferson\'s draft of the '
            'Declaration of Independence.',
            ParagraphStyle('mm', fontName='Helvetica', fontSize=8,
                           textColor=colors.HexColor('#333333'), leading=10)),
    ]]
    mm_table = Table(mm_data, colWidths=[7.0 * inch])
    mm_table.setStyle(TableStyle([
        ('BOX',        (0, 0), (-1, -1), 0.75, GREY_BORDER),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f4f8ff')),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    story.append(mm_table)
    story.append(Spacer(1, 5))

    # ── Instructions ──────────────────────────────────────────────────────────
    story.append(Paragraph(
        'Check off the coins you own. Use the Notes/QTY column to record quantity '
        '(e.g. QTY:2), grade (e.g. MS-65), or slab service (e.g. PCGS MS-64). '
        '\u2020\u2020 = Satin Finish coins were issued exclusively in the 2005 U.S. '
        'Mint Uncirculated (Mint) Set; they are NOT available separately.',
        instruction))

    # ── Main Checklist Table ──────────────────────────────────────────────────
    # Header row
    col_headers = [
        Paragraph('Year', header_cell),
        Paragraph('Design / Reverse', header_cell),
        Paragraph('P', header_cell),
        Paragraph('D', header_cell),
        Paragraph('S\nProof', header_cell),
        Paragraph('P\nSatin\u2020\u2020', header_cell),
        Paragraph('D\nSatin\u2020\u2020', header_cell),
        Paragraph('Notes / QTY', header_cell),
    ]
    # Mintage sub-header row (italicized mintage under column headers)
    mintage_headers = [
        Paragraph('', meta),
        Paragraph('<i>Mintage (approx.)</i>',
                  ParagraphStyle('mh', fontName='Helvetica-Oblique', fontSize=6.5,
                                 textColor=colors.HexColor('#777777'), alignment=TA_CENTER)),
        '', '', '', '', '', '',
    ]

    table_data = [col_headers]

    for i, coin in enumerate(COIN_ROWS):
        has_satin = coin['p_satin'] is not None

        design_cell = [
            Paragraph(coin['name'], cell_design),
            Spacer(1, 2),
            Paragraph(f"<i>Obv: {coin['obverse']}</i>", cell_obverse),
        ]
        p_cell   = Paragraph(_checkbox(), cell_center)
        d_cell   = Paragraph(_checkbox(), cell_center)
        s_cell   = Paragraph(_checkbox(), cell_center)
        ps_cell  = Paragraph(_checkbox(), cell_center) if has_satin \
                   else Paragraph('N/A', cell_na)
        ds_cell  = Paragraph(_checkbox(), cell_center) if has_satin \
                   else Paragraph('N/A', cell_na)

        # Mintage sub-row beneath each checkbox
        p_mint_p  = Paragraph(coin['p_mint'], cell_mintage)
        d_mint_p  = Paragraph(coin['d_mint'], cell_mintage)
        s_mint_p  = Paragraph(coin['s_mint'], cell_mintage)
        ps_mint_p = Paragraph(coin['p_satin'] or '', cell_mintage)
        ds_mint_p = Paragraph(coin['d_satin'] or '', cell_mintage)

        row = [
            Paragraph(coin['year'], ParagraphStyle('yr',
                fontName='Helvetica-Bold', fontSize=10,
                textColor=BLUE_DARK, alignment=TA_CENTER)),
            design_cell,
            [p_cell,  Spacer(1, 1), p_mint_p],
            [d_cell,  Spacer(1, 1), d_mint_p],
            [s_cell,  Spacer(1, 1), s_mint_p],
            [ps_cell, Spacer(1, 1), ps_mint_p],
            [ds_cell, Spacer(1, 1), ds_mint_p],
            '',   # Notes column (blank for user to fill)
        ]
        table_data.append(row)

    main_table = Table(table_data, colWidths=COL_WIDTHS, repeatRows=1)

    # Build cell-level style commands
    ts = [
        # Global
        ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('GRID',          (0, 0), (-1, -1), 0.5, GREY_BORDER),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),

        # Header row
        ('BACKGROUND',    (0, 0), (-1, 0), GREY_HEADER),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0), 8),
        ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 0), (-1, 0), [GREY_HEADER]),

        # Alternate data rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, BLUE_LIGHT]),

        # Year column: center
        ('ALIGN',  (0, 1), (0, -1), 'CENTER'),
        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),

        # Checkbox columns (P D S P-Satin D-Satin): center
        ('ALIGN',  (2, 1), (6, -1), 'CENTER'),

        # Notes column: left
        ('ALIGN',  (7, 1), (7, -1), 'LEFT'),
    ]

    # N/A cells (2004 rows, satin columns = rows 1 and 2, cols 5 and 6)
    for row_idx in [1, 2]:
        ts.append(('BACKGROUND', (5, row_idx), (6, row_idx), GREY_NA))
        ts.append(('TEXTCOLOR',  (5, row_idx), (6, row_idx),
                   colors.HexColor('#888888')))

    # Thick left border on Design column to visually anchor it
    ts.append(('LINEAFTER', (1, 0), (1, -1), 1.0, BLUE_DARK))

    main_table.setStyle(TableStyle(ts))
    story.append(main_table)
    story.append(Spacer(1, 8))

    # ── Footnotes ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5,
                            color=GREY_BORDER, spaceAfter=3))
    story.append(Paragraph(
        '\u2020\u2020 <b>Satin Finish coins</b> were struck exclusively for the '
        '2005 U.S. Mint Uncirculated Set (1,160,000 sets issued). '
        'These are <b>not</b> available as individual purchases. '
        'A single 2005 Mint Set contains one each of the P and D Satin Finish '
        'Bison and Ocean in View nickels.',
        footnote_style))
    story.append(Paragraph(
        '<b>Speared Bison Variety (2005-D):</b> A prominent die-gouge error '
        '(PCGS FS-901) creates the appearance of a spear through the Bison\'s '
        'back on some 2005-D coins. This is a sought-after variety within the '
        'standard 2005-D mintage of 487,680,000 \u2014 it is <b>not</b> a '
        'separate official program slot. Record it in the Notes column.',
        footnote_style))
    story.append(Paragraph(
        '<b>Shared S Proof mintage:</b> The 2004-S Peace Medal and 2004-S '
        'Keelboat nickels share a single Proof Set production run of 2,965,422. '
        'Both designs appear in every 2004 Proof Set.',
        footnote_style))
    story.append(Paragraph(
        '<b>Jefferson Nickel checklist exclusion:</b> Coins in this program '
        '(2004 Peace Medal, 2004 Keelboat, 2005 American Bison, 2005 Ocean in '
        'View!) are tracked <i>only</i> on this checklist. Do not also mark them '
        'on the standard Jefferson Nickels checklist to avoid double-counting.',
        footnote_style))
    story.append(Spacer(1, 6))

    # ── Additional Notes lines ────────────────────────────────────────────────
    story.append(Paragraph('ADDITIONAL NOTES',
        ParagraphStyle('notes_hdr', fontName='Helvetica-Bold', fontSize=8,
                       textColor=colors.HexColor('#555555'))))
    story.append(Spacer(1, 3))
    for _ in range(3):
        story.append(HRFlowable(width='100%', thickness=0.5,
                                color=GREY_BORDER, spaceBefore=10, spaceAfter=2))

    # ── Legal footer ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=0.5,
                            color=GREY_BORDER, spaceAfter=2))
    story.append(Paragraph(
        'Westward Journey Nickel Series\u2122 is a trademark of the United States Mint. '
        'Mintage data sourced from U.S. Mint Annual Reports and PCGS CoinFacts. '
        'This checklist is generated by Numista.AI and is for personal collection '
        'tracking purposes only.',
        ParagraphStyle('legal', fontName='Helvetica', fontSize=6,
                       textColor=colors.HexColor('#888888'), leading=8)))

    doc.build(story)
    print(f'Generated: {output_path}')


if __name__ == '__main__':
    build_pdf(OUTPUT_FILE)
