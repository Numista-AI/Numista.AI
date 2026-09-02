"""
generate_westward_journey_checklist.py
=======================================
Generates the Numista.AI native-format printable checklist PDF for the
Westward Journey Nickel Series(tm) (2004-2005).

Authorized under: American 5-Cent Coin Design Continuity Act of 2003
                  Public Law 108-15; 31 U.S.C. Section 5112(p)

Column layout (Schema B grouped format):
  Year / Design  |  P  |  D  |  S Proof  |  P Satin(tt)  |  D Satin(tt)  |  Notes / QTY

Row model: 4 design rows x 6 mint/finish columns (16 live cells):
  2004 Peace Medal     | [] | [] | []  | N/A | N/A |
  2004 Keelboat        | [] | [] | []  | N/A | N/A |
  2005 American Bison  | [] | [] | []  |  [] |  [] |
  2005 Ocean in View!  | [] | [] | []  |  [] |  [] |

Mintage sources (verified 2026-09-02):
  2004-P Peace Medal:         361,440,000  US Mint Annual Report 2004
  2004-D Peace Medal:         372,000,000  US Mint Annual Report 2004
  2004-S Peace Medal (Proof): 2,992,069    PCGS CoinFacts #4155
  2004-P Keelboat:            366,720,000  US Mint Annual Report 2004
  2004-D Keelboat:            344,880,000  US Mint Annual Report 2004
  2004-S Keelboat (Proof):    2,965,422    PCGS CoinFacts #4156
  2005-P American Bison:      448,320,000  US Mint Annual Report 2005
  2005-D American Bison:      487,680,000  PCGS CoinFacts #4159
  2005-S American Bison:      3,344,679    US Mint Annual Report 2005
  2005-P Bison (Satin):       1,160,000    2005 US Mint Uncirculated Set
  2005-D Bison (Satin):       1,160,000    2005 US Mint Uncirculated Set
  2005-P Ocean in View!:      394,080,000  US Mint Annual Report 2005
  2005-D Ocean in View!:      411,120,000  US Mint Annual Report 2005
  2005-S Ocean in View!:      3,344,679    US Mint Annual Report 2005
  2005-P Ocean (Satin):       1,160,000    2005 US Mint Uncirculated Set
  2005-D Ocean (Satin):       1,160,000    2005 US Mint Uncirculated Set

  Lot rules:
  - 2004 Proof Set covers both 2004-S designs (Peace Medal + Keelboat).
  - 2005 Proof Set covers both 2005-S designs (Bison + Ocean in View!).
  - 2005 Uncirculated Set covers all four 2005 Satin slots (P+D Bison, P+D Ocean).

  Speared Bison (2005-D): Die-gouge variety (PCGS FS-901) within the
  standard 2005-D Bison mintage. NOT a 17th official program slot.

Usage:
    python generate_westward_journey_checklist.py

Output:
    numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf
    (gitignored -- GCS upload is Eric-only on a separate Proceed)
"""

import sys
import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
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

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE_DARK   = colors.HexColor('#1a3a6b')
BLUE_MID    = colors.HexColor('#2c5f9e')
BLUE_LIGHT  = colors.HexColor('#dce9f7')
GREY_HEADER = colors.HexColor('#e8e8e8')
GREY_BORDER = colors.HexColor('#aaaaaa')
GREY_NA     = colors.HexColor('#cccccc')
BLACK       = colors.black
WHITE       = colors.white

# ── Coin data (C-2 receipt values baked in) ───────────────────────────────────
# p_satin=None means 2004 had NO Satin Finish Mint Set -> N/A cell
COIN_ROWS = [
    {
        'year': '2004',
        'name': 'Peace Medal\n(Louisiana Purchase)',
        'obverse': '1938 Classic Schlag Portrait',
        'p_mint':  '361,440,000',
        'd_mint':  '372,000,000',
        's_mint':  '2,992,069',    # PCGS CoinFacts #4155
        's_note':  '2004 Proof Set',
        'p_satin': None,
        'd_satin': None,
    },
    {
        'year': '2004',
        'name': 'Keelboat\n(Missouri River)',
        'obverse': '1938 Classic Schlag Portrait',
        'p_mint':  '366,720,000',
        'd_mint':  '344,880,000',
        's_mint':  '2,965,422',    # PCGS CoinFacts #4156
        's_note':  '2004 Proof Set',
        'p_satin': None,
        'd_satin': None,
    },
    {
        'year': '2005',
        'name': 'American Bison',
        'obverse': '2005 One-Year Houdon/Fitzgerald Portrait\n(Handwritten "Liberty" script)',
        'p_mint':  '448,320,000',
        'd_mint':  '487,680,000',  # PCGS CoinFacts #4159
        's_mint':  '3,344,679',
        's_note':  '2005 Proof Set',
        'p_satin': '1,160,000',
        'd_satin': '1,160,000',
    },
    {
        'year': '2005',
        'name': 'Ocean in View!\n("O! The joy!")',
        'obverse': '2005 One-Year Houdon/Fitzgerald Portrait\n(Handwritten "Liberty" script)',
        'p_mint':  '394,080,000',
        'd_mint':  '411,120,000',
        's_mint':  '3,344,679',
        's_note':  '2005 Proof Set',
        'p_satin': '1,160,000',
        'd_satin': '1,160,000',
    },
]

# ── Column widths (7.0in total inside 0.5in margins each side) ────────────────
COL_WIDTHS = [
    0.50 * inch,  # Year
    2.00 * inch,  # Design
    0.52 * inch,  # P
    0.52 * inch,  # D
    0.68 * inch,  # S Proof
    0.68 * inch,  # P Satin
    0.68 * inch,  # D Satin
    1.42 * inch,  # Notes / QTY
]


def build_pdf(output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        topMargin=0.45 * inch, bottomMargin=0.5 * inch,
        title='Westward Journey Nickel Series(tm) Checklist',
        author='Numista.AI System of Record',
    )

    today = date.today().strftime('%Y-%m-%d')

    # ── Styles ────────────────────────────────────────────────────────────────
    h1 = ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=14,
                        textColor=BLUE_DARK, spaceAfter=2)
    h2 = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=10,
                        textColor=BLUE_DARK, spaceAfter=2)
    meta = ParagraphStyle('meta', fontName='Helvetica', fontSize=7.5,
                          textColor=colors.HexColor('#555555'), spaceAfter=0)
    instruction = ParagraphStyle('instruction', fontName='Helvetica-Oblique',
                                 fontSize=8, textColor=colors.HexColor('#444444'),
                                 spaceAfter=4)
    footnote_style = ParagraphStyle('footnote', fontName='Helvetica', fontSize=7,
                                    textColor=colors.HexColor('#444444'),
                                    spaceAfter=2, leading=9)
    cell_design = ParagraphStyle('cell_design', fontName='Helvetica-Bold',
                                 fontSize=8.5, textColor=BLACK, leading=11)
    cell_obverse = ParagraphStyle('cell_obverse', fontName='Helvetica-Oblique',
                                  fontSize=6.5, textColor=colors.HexColor('#555555'),
                                  leading=8)
    cell_mintage = ParagraphStyle('cell_mintage', fontName='Helvetica', fontSize=6.5,
                                  textColor=colors.HexColor('#333333'), leading=8)
    cell_center = ParagraphStyle('cell_center', fontName='Helvetica', fontSize=14,
                                 textColor=BLUE_DARK, alignment=TA_CENTER)
    cell_na = ParagraphStyle('cell_na', fontName='Helvetica-Oblique', fontSize=7,
                             textColor=colors.HexColor('#888888'), alignment=TA_CENTER)
    header_cell = ParagraphStyle('header_cell', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=BLUE_DARK, alignment=TA_CENTER, leading=10)

    story = []

    # ── Page header ───────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph('Numista.AI Checklist', h1),
        Paragraph(f'Generated: {today}',
                  ParagraphStyle('right', fontName='Helvetica', fontSize=7.5,
                                 textColor=colors.HexColor('#555555'),
                                 alignment=TA_RIGHT)),
    ]], colWidths=[5.5 * inch, 2.0 * inch])
    hdr.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(hdr)
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE_DARK, spaceAfter=4))

    # ── Program title ─────────────────────────────────────────────────────────
    story.append(Paragraph(
        'WESTWARD JOURNEY NICKEL SERIES\u2122 \u00a0 (2004\u20132005)', h2))
    story.append(Paragraph(
        'Authorized by: <i>American 5-Cent Coin Design Continuity Act of 2003</i> '
        '(Public Law 108-15; 31\u00a0U.S.C. \u00a7\u00a05112(p)) \u00a0|\u00a0 '
        'Category: Nickel \u00a0|\u00a0 Denomination: Five Cents (Cupro-Nickel Clad)',
        meta))
    story.append(Spacer(1, 4))

    # ── Mint mark box ─────────────────────────────────────────────────────────
    mm = Table([[Paragraph(
        '<b>Mint Mark Location:</b> Right side of Jefferson\'s portrait on the '
        '<b>obverse</b>. \u00a0'
        '<b>2004 obverse:</b> 1938 Schlag portrait. \u00a0'
        '<b>2005 obverse:</b> One-year-only close-up by Fitzgerald/Everhart '
        '(Houdon bust), with handwritten <i>"Liberty"</i> script from '
        'Jefferson\'s draft of the Declaration of Independence.',
        ParagraphStyle('mm', fontName='Helvetica', fontSize=8,
                       textColor=colors.HexColor('#333333'), leading=10)),
    ]], colWidths=[7.0 * inch])
    mm.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, GREY_BORDER),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f4f8ff')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(mm)
    story.append(Spacer(1, 5))

    # ── Instructions ──────────────────────────────────────────────────────────
    story.append(Paragraph(
        'Check off the coins you own. Use the Notes/QTY column for quantity, '
        'grade (e.g. MS-65), or slab service (e.g. PCGS MS-64). '
        '\u2020\u2020 Satin Finish coins were issued exclusively in the 2005 '
        'U.S. Mint Uncirculated (Mint) Set \u2014 not available separately.',
        instruction))

    # ── Main table ────────────────────────────────────────────────────────────
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
    table_data = [col_headers]

    for coin in COIN_ROWS:
        has_satin = coin['p_satin'] is not None

        design_cell = [
            Paragraph(coin['name'], cell_design),
            Spacer(1, 2),
            Paragraph(f"<i>Obv: {coin['obverse']}</i>", cell_obverse),
        ]

        def cb(): return Paragraph('\u25a1', cell_center)
        def na(): return Paragraph('N/A', cell_na)

        def mint_p(val):
            return Paragraph(val, cell_mintage) if val else Paragraph('', cell_mintage)

        row = [
            Paragraph(coin['year'],
                      ParagraphStyle('yr', fontName='Helvetica-Bold', fontSize=10,
                                     textColor=BLUE_DARK, alignment=TA_CENTER)),
            design_cell,
            [cb(), Spacer(1, 1), mint_p(coin['p_mint'])],
            [cb(), Spacer(1, 1), mint_p(coin['d_mint'])],
            [cb(), Spacer(1, 1), mint_p(coin['s_mint']),
             Paragraph(coin.get('s_note', ''),
                       ParagraphStyle('snote', fontName='Helvetica-Oblique',
                                      fontSize=6, textColor=colors.HexColor('#777777'),
                                      leading=7))],
            [cb(), Spacer(1, 1), mint_p(coin['p_satin'])] if has_satin else [na()],
            [cb(), Spacer(1, 1), mint_p(coin['d_satin'])] if has_satin else [na()],
            '',
        ]
        table_data.append(row)

    main_table = Table(table_data, colWidths=COL_WIDTHS, repeatRows=1)

    ts = [
        ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('GRID',          (0, 0), (-1, -1), 0.5, GREY_BORDER),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        # Header
        ('BACKGROUND',    (0, 0), (-1, 0), GREY_HEADER),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
        # Alternating rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, BLUE_LIGHT]),
        # Year col
        ('ALIGN',  (0, 1), (0, -1), 'CENTER'),
        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
        # Checkbox cols
        ('ALIGN',  (2, 1), (6, -1), 'CENTER'),
        # Notes col
        ('ALIGN',  (7, 1), (7, -1), 'LEFT'),
        # Anchor design col
        ('LINEAFTER', (1, 0), (1, -1), 1.0, BLUE_DARK),
    ]
    # N/A cells (2004 rows = table rows 1 & 2, satin cols 5 & 6)
    for row_idx in [1, 2]:
        ts.append(('BACKGROUND', (5, row_idx), (6, row_idx), GREY_NA))
        ts.append(('TEXTCOLOR',  (5, row_idx), (6, row_idx),
                   colors.HexColor('#888888')))

    main_table.setStyle(TableStyle(ts))
    story.append(main_table)
    story.append(Spacer(1, 8))

    # ── Footnotes ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5,
                            color=GREY_BORDER, spaceAfter=3))
    story.append(Paragraph(
        '\u2020\u2020 <b>Satin Finish coins</b> were struck exclusively for the '
        '2005 U.S. Mint Uncirculated Set (1,160,000 sets). Not sold separately. '
        'One 2005 Mint Set covers all four satin slots (P+D Bison, P+D Ocean).',
        footnote_style))
    story.append(Paragraph(
        '<b>Proof Set lot rules:</b> The 2004 Proof Set covers both 2004-S designs '
        '(Peace Medal and Keelboat). The 2005 Proof Set covers both 2005-S designs '
        '(American Bison and Ocean in View!). One lot = both S slots.',
        footnote_style))
    story.append(Paragraph(
        '<b>Speared Bison Variety (2005-D):</b> Die-gouge error (PCGS FS-901) within '
        'the standard 2005-D mintage of 487,680,000. NOT a 17th official slot. '
        'Record it in the Notes column.',
        footnote_style))
    story.append(Paragraph(
        '<b>Jefferson Nickel checklist:</b> 2004\u20132005 Westward Journey coins are '
        'tracked ONLY on this checklist. Do not also mark them on the Jefferson Nickels '
        'checklist to avoid double-counting in collection progress.',
        footnote_style))
    story.append(Spacer(1, 6))

    # ── Notes lines ───────────────────────────────────────────────────────────
    story.append(Paragraph('ADDITIONAL NOTES',
                            ParagraphStyle('nhdr', fontName='Helvetica-Bold',
                                           fontSize=8,
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
        'Mintage data: US Mint Annual Reports 2004\u20132005; PCGS CoinFacts #4155, '
        '#4156, #4159. This checklist is generated by Numista.AI for personal '
        'collection tracking purposes only.',
        ParagraphStyle('legal', fontName='Helvetica', fontSize=6,
                       textColor=colors.HexColor('#888888'), leading=8)))

    doc.build(story)
    print(f'Generated: {output_path}')


if __name__ == '__main__':
    build_pdf(OUTPUT_FILE)
