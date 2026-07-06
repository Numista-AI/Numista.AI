# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Detect what circle/bullet glyph each PDF uses."""
import fitz, os, sys
sys.stdout.reconfigure(encoding='utf-8')

folder = r'C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs'
SKIP = {'2026-US-Circulating-Coins-Identification-Chart-508.pdf', 'LC53-Mint-Mark-Guide.pdf'}

for fname in sorted(os.listdir(folder)):
    if not fname.endswith('.pdf') or fname in SKIP:
        continue
    doc = fitz.open(os.path.join(folder, fname))
    page = doc[0]
    # Collect all unique non-ASCII chars used
    blocks = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
    special_chars = {}
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font = span.get("font", "")
                for ch in span.get("chars", []):
                    c = ch.get("c", "")
                    cp = ord(c) if c else 0
                    if cp > 127:
                        key = f"U+{cp:04X} ({repr(c)})"
                        if key not in special_chars:
                            special_chars[key] = {'count': 0, 'font': font}
                        special_chars[key]['count'] += 1
    # Sort by count descending
    sorted_chars = sorted(special_chars.items(), key=lambda x: -x[1]['count'])
    top = sorted_chars[:5]
    print(f"{fname[:50]:52s}  glyphs: {top}")
    doc.close()
