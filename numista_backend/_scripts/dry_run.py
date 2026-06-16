"""
Dry run — generate 3 variants per PDF locally, no GCS upload.
Renders each to PNG for quick visual inspection.
"""
import fitz, random, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

CIRCLE_GLYPHS = {"\uf0a6", "\uf06d", "\u00a6"}
FILLED_COLOR  = (0.1, 0.1, 0.1)
INPUT_DIR     = r"C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs"
OUTPUT_DIR    = r"C:\Users\ericd\Documents\MyVertexProject\training_output\dry_run"
SKIP = {"2026-US-Circulating-Coins-Identification-Chart-508.pdf", "LC53-Mint-Mark-Guide.pdf"}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_circles(page):
    circles = []
    blocks = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                for ch in span.get("chars", []):
                    if ch.get("c") in CIRCLE_GLYPHS:
                        b = ch.get("bbox")
                        if b:
                            cx = (b[0]+b[2])/2
                            cy = (b[1]+b[3])/2
                            r  = (b[2]-b[0])/2 * 0.75
                            circles.append((cx, cy, r))
    return circles

TEST_PROBS = [0.0, 0.4, 0.85]  # empty, moderate, heavy
rng = random.Random(42)
summary = {}

for fname in sorted(os.listdir(INPUT_DIR)):
    if not fname.endswith(".pdf") or fname in SKIP:
        continue
    src = os.path.join(INPUT_DIR, fname)
    stem = fname.replace(".pdf","")

    doc_check = fitz.open(src)
    circles = find_circles(doc_check[0])
    doc_check.close()

    if not circles:
        print(f"SKIP (no circles): {fname}")
        summary[fname] = {"circles": 0, "status": "skipped"}
        continue

    out_dir = os.path.join(OUTPUT_DIR, stem)
    os.makedirs(out_dir, exist_ok=True)
    variants = []

    for i, prob in enumerate(TEST_PROBS):
        doc = fitz.open(src)
        page = doc[0]
        filled = 0
        for cx, cy, r in circles:
            if rng.random() < prob:
                page.draw_circle(fitz.Point(cx, cy), r,
                                 color=FILLED_COLOR, fill=FILLED_COLOR, overlay=True)
                filled += 1
        out_pdf = os.path.join(out_dir, f"variant_{i:02d}_p{int(prob*100)}.pdf")
        doc.save(out_pdf)
        # Render PNG
        out_png = out_pdf.replace(".pdf", ".png")
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(100/72, 100/72))
        pix.save(out_png)
        doc.close()
        variants.append({"prob": prob, "filled": filled, "total": len(circles)})

    summary[fname] = {"circles": len(circles), "variants": variants, "status": "ok"}
    pct = [f"{v['filled']}/{v['total']}" for v in variants]
    print(f"OK  {stem[:55]:57s}  circles={len(circles):4d}  filled={pct}")

with open(os.path.join(OUTPUT_DIR, "dry_run_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

ok = sum(1 for v in summary.values() if v.get("status") == "ok")
sk = sum(1 for v in summary.values() if v.get("status") == "skipped")
print(f"\nDone: {ok} PDFs processed, {sk} skipped (no circles / font not embedded)")
