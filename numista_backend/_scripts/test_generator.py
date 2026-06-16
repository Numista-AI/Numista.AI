"""Quick test — generate 3 variants of the 50 State Quarter checklist locally, no GCS upload."""
import fitz, random, os, sys
sys.stdout.reconfigure(encoding='utf-8')

EMPTY_CIRCLE_CHAR = "\uf0a6"
FILLED_COLOR = (0.1, 0.1, 0.1)
OUTPUT_DIR = r"C:\Users\ericd\Documents\MyVertexProject\training_output\test"
os.makedirs(OUTPUT_DIR, exist_ok=True)

src = r"C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs\LC-KGW-50-State-Commemorative-Quarter-Checklist.pdf"

def find_circles(page):
    circles = []
    blocks = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                for ch in span.get("chars", []):
                    if ch.get("c") == EMPTY_CIRCLE_CHAR:
                        b = ch.get("bbox")
                        if b:
                            cx = (b[0]+b[2])/2
                            cy = (b[1]+b[3])/2
                            r  = (b[2]-b[0])/2 * 0.75
                            circles.append((cx, cy, r))
    return circles

test_cases = [
    ("delaware_only",  [0]),                                 # Only first circle
    ("sparse_20pct",   None, 0.20),                          # 20% random
    ("heavy_75pct",    None, 0.75),                          # 75% random
]

doc_check = fitz.open(src)
circles = find_circles(doc_check[0])
doc_check.close()
print(f"Found {len(circles)} circle positions on page")
print(f"Expected: 56 coins × 4 options = 224 circles")
print()

rng = random.Random(42)

for test in test_cases:
    name = test[0]
    doc = fitz.open(src)
    page = doc[0]

    filled = 0
    for i, (cx, cy, r) in enumerate(circles):
        should_fill = False
        if len(test) == 2:
            should_fill = (i in test[1])
        elif len(test) == 3:
            should_fill = rng.random() < test[2]

        if should_fill:
            page.draw_circle(fitz.Point(cx, cy), r,
                             color=FILLED_COLOR, fill=FILLED_COLOR, overlay=True)
            filled += 1

    out_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
    doc.save(out_path)
    doc.close()

    # Also render to PNG for visual inspection
    doc2 = fitz.open(out_path)
    pix = doc2[0].get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    pix.save(png_path)
    doc2.close()

    print(f"  {name}: {filled}/{len(circles)} filled → {out_path}")
    print(f"         PNG: {png_path}")

print("\nTest complete. Check training_output/test/ folder for results.")
