"""
fix_skipped_pdfs.py
====================
Handles the 3 PDFs skipped due to unembedded Wingdings fonts:
  - LC-147-Roosevelt-Dime-Checklist.pdf       (262 circles)
  - LC-151-Kennedy-Half-Dollar-Checklist.pdf  (214 circles)
  - LC-4760-American-Silver-Eagle-Checklist.pdf (106 circles)

Strategy: U+FFFD in Wingdings-Regular font = those ARE the radio button circles.
We detect them by checking (char == U+FFFD AND font == Wingdings-Regular).
"""
import fitz, random, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import storage as gcs
import google.auth

# All circle glyph strategies:
# Strategy A: character is a known circle glyph
CIRCLE_CHARS = {"\uf0a6", "\uf06d", "\u00a6"}
# Strategy B: character is U+FFFD (font not embedded) but font is Wingdings
WINGDINGS_FONT_NAMES = {"wingdings-regular", "wingdings", "wingdings 2", "wingdings 3"}

FILLED_COLOR     = (0.1, 0.1, 0.1)
INPUT_DIR        = r"C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs"
OUTPUT_DIR       = r"C:\Users\ericd\Documents\MyVertexProject\training_output"
GCS_BUCKET       = "numista-training-docs"
GCS_PREFIX       = "Numista.AI Training Data/Synthetic Filled"
RANDOM_SEED      = 42

TARGET_PDFS = [
    "LC-147-Roosevelt-Dime-Checklist.pdf",
    "LC-151-Kennedy-Half-Dollar-Checklist.pdf",
    "LC-4760-American-Silver-Eagle-Checklist.pdf",
]

PERSONAS = [
    {"name": "empty",         "prob": 0.00},
    {"name": "sparse",        "prob": 0.10},
    {"name": "sparse2",       "prob": 0.15},
    {"name": "light",         "prob": 0.25},
    {"name": "light2",        "prob": 0.30},
    {"name": "moderate",      "prob": 0.40},
    {"name": "moderate2",     "prob": 0.45},
    {"name": "moderate3",     "prob": 0.50},
    {"name": "half",          "prob": 0.55},
    {"name": "heavy",         "prob": 0.65},
    {"name": "heavy2",        "prob": 0.70},
    {"name": "heavy3",        "prob": 0.75},
    {"name": "heavy4",        "prob": 0.80},
    {"name": "near_complete", "prob": 0.85},
    {"name": "near_complete2","prob": 0.90},
    {"name": "complete",      "prob": 1.00},
    {"name": "p_only",        "prob": 0.00, "bias": "p"},
    {"name": "d_only",        "prob": 0.00, "bias": "d"},
    {"name": "proof_only",    "prob": 0.00, "bias": "proof"},
    {"name": "early_heavy",   "prob": 0.00, "bias": "early"},
    {"name": "late_sparse",   "prob": 0.00, "bias": "late"},
    {"name": "random_mix1",   "prob": 0.35},
    {"name": "random_mix2",   "prob": 0.55},
    {"name": "random_mix3",   "prob": 0.70},
    {"name": "random_mix4",   "prob": 0.45},
]


def find_circles(page: fitz.Page) -> list:
    """
    Finds all radio button circle positions using two strategies:
    A) Known circle glyphs (U+F0A6, U+F06D, U+00A6)
    B) U+FFFD in Wingdings font (font not embedded — but still Wingdings circles)
    """
    circles = []
    blocks = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font = span.get("font", "").lower()
                is_wingdings = any(w in font for w in WINGDINGS_FONT_NAMES)
                for ch in span.get("chars", []):
                    c = ch.get("c", "")
                    # Strategy A: known glyph
                    is_circle_glyph = c in CIRCLE_CHARS
                    # Strategy B: replacement char in Wingdings font
                    is_wingdings_replacement = (c == "\ufffd" and is_wingdings)

                    if is_circle_glyph or is_wingdings_replacement:
                        b = ch.get("bbox")
                        if b:
                            cx = (b[0] + b[2]) / 2
                            cy = (b[1] + b[3]) / 2
                            r  = (b[2] - b[0]) / 2 * 0.75
                            circles.append((cx, cy, r))
    return circles


def assign_filled(circles, persona, rng):
    bias = persona.get("bias")
    prob = persona.get("prob", 0.5)
    n = len(circles)
    result = []
    for i, _ in enumerate(circles):
        if bias == "p":      filled = (i % 4 == 0)
        elif bias == "d":    filled = (i % 4 == 1)
        elif bias == "proof": filled = (i % 4 in (2, 3))
        elif bias == "early": filled = rng.random() < (0.8 if i < n//2 else 0.1)
        elif bias == "late":  filled = rng.random() < (0.1 if i < n//2 else 0.7)
        else:                filled = rng.random() < prob
        result.append(filled)
    return result


def process_pdf(fname, bucket):
    src = os.path.join(INPUT_DIR, fname)
    stem = fname.replace(".pdf", "")
    rng = random.Random(RANDOM_SEED)

    print(f"\n{'='*60}")
    print(f"Processing: {stem}")

    doc_check = fitz.open(src)
    circles = find_circles(doc_check[0])
    doc_check.close()
    print(f"  Found {len(circles)} circle positions")

    if not circles:
        print("  STILL no circles found — skipping")
        return

    for i, persona in enumerate(PERSONAS):
        out_dir   = os.path.join(OUTPUT_DIR, stem)
        os.makedirs(out_dir, exist_ok=True)
        out_fname = f"variant_{i:02d}_{persona['name']}.pdf"
        out_path  = os.path.join(out_dir, out_fname)
        gcs_key   = f"{GCS_PREFIX}/{stem}/{out_fname}"

        doc = fitz.open(src)
        page = doc[0]
        flags = assign_filled(circles, persona, rng)
        filled = sum(1 for f in flags if f)

        for (cx, cy, r), is_filled in zip(circles, flags):
            if is_filled:
                page.draw_circle(fitz.Point(cx, cy), r,
                                 color=FILLED_COLOR, fill=FILLED_COLOR, overlay=True)
        doc.save(out_path, garbage=4, deflate=True)
        doc.close()

        blob = bucket.blob(gcs_key)
        blob.upload_from_filename(out_path, content_type="application/pdf")
        print(f"  [{i+1:2d}/{len(PERSONAS)}] {persona['name']:15s}  "
              f"filled={filled:3d}/{len(circles)}  -> gs://{GCS_BUCKET}/{gcs_key}")


def main():
    creds, _ = google.auth.default()
    gcs_client = gcs.Client(credentials=creds)
    bucket = gcs_client.bucket(GCS_BUCKET)

    for fname in TARGET_PDFS:
        process_pdf(fname, bucket)

    print(f"\nDone! {len(TARGET_PDFS) * len(PERSONAS)} additional files uploaded.")


if __name__ == "__main__":
    main()
