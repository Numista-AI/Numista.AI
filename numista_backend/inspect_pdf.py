import fitz, sys
sys.stdout.reconfigure(encoding='utf-8')

# Render the PDF at high DPI to understand the actual visual structure
path = r'C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs\LC-KGW-50-State-Commemorative-Quarter-Checklist.pdf'
doc = fitz.open(path)
page = doc[0]

# Render at 150 DPI for inspection
mat = fitz.Matrix(150/72, 150/72)
pix = page.get_pixmap(matrix=mat)
out_path = r'C:\Users\ericd\Documents\MyVertexProject\numista_backend\checklist_render.png'
pix.save(out_path)
print(f"Saved render: {out_path}")
print(f"Image size: {pix.width} x {pix.height} px")

# Also get all text blocks with positions to understand layout
blocks = page.get_text("blocks")
print(f"\nText blocks: {len(blocks)}")
# Show first 30 blocks with positions
for i, b in enumerate(blocks[:30]):
    x0, y0, x1, y1, text, bno, btype = b
    text_clean = text.strip().replace('\n', ' ')[:60]
    print(f"  Block {i:2d}: ({x0:5.0f},{y0:5.0f})-({x1:5.0f},{y1:5.0f}) | {repr(text_clean)}")

doc.close()
