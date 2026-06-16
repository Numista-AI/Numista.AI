"""
generate_training_docs.py
=========================
Generates 25 synthetic "filled" versions of each Littleton checklist PDF
for Document AI training. Works by:

1. Parsing the PDF text layer to find all empty circle glyphs (U+F0A6 in
   Wingdings/Symbol font) and their exact page coordinates.
2. For each synthetic variant, randomly deciding which circles to fill
   (based on a collector persona: sparse, moderate, heavy, complete, etc.)
3. Drawing a filled circle directly over each "selected" empty circle
   using a matching dark fill color (matches the Littleton green/teal header,
   or rendered as dark bullet match).

Output: saved to  ..\\training_output\\<pdf_stem>\\variant_NN.pdf
        and simultaneously uploaded to GCS training bucket.

Usage:
    python generate_training_docs.py

Requirements:
    pip install pymupdf google-cloud-storage
"""

import fitz          # PyMuPDF
import random
import os
import json
import sys
from pathlib import Path
from google.cloud import storage as gcs
import google.auth

sys.stdout.reconfigure(encoding='utf-8')

# ── Configuration ──────────────────────────────────────────────────────────────
INPUT_DIR      = r"C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs"
OUTPUT_DIR     = r"C:\Users\ericd\Documents\MyVertexProject\training_output"
GCS_BUCKET     = "numista-training-docs"
GCS_PREFIX     = "Numista.AI Training Data/Synthetic Filled"

VARIANTS_PER_DOC = 25   # How many filled versions to generate per blank PDF
RANDOM_SEED      = 42   # Reproducible randomness

# All known Littleton circle/bullet glyphs used as radio buttons across their PDF catalog.
# U+F0A6: Wingdings bullet ○  — newer format (State Qtrs, Nat'l Park, Presidential, etc.)
# U+F06D: Wingdings filled-circle variant — older format (Lincoln, Morgan, Barber, etc.)
# U+00A6: Broken bar ¦  — used in US Women Quarters checklist
# U+FFFD: Replacement char — font not embedded (Kennedy, Roosevelt) → skip these PDFs
CIRCLE_GLYPHS = {"\uf0a6", "\uf06d", "\u00a6"}


# Collector personas — define probability that any given circle is filled
PERSONAS = [
    {"name": "empty",        "prob": 0.00},   # Completely empty (sanity check)
    {"name": "sparse",       "prob": 0.10},   # Just started collecting
    {"name": "sparse2",      "prob": 0.15},
    {"name": "light",        "prob": 0.25},
    {"name": "light2",       "prob": 0.30},
    {"name": "moderate",     "prob": 0.40},
    {"name": "moderate2",    "prob": 0.45},
    {"name": "moderate3",    "prob": 0.50},
    {"name": "half",         "prob": 0.55},
    {"name": "heavy",        "prob": 0.65},
    {"name": "heavy2",       "prob": 0.70},
    {"name": "heavy3",       "prob": 0.75},
    {"name": "heavy4",       "prob": 0.80},
    {"name": "near_complete","prob": 0.85},
    {"name": "near_complete2","prob": 0.90},
    {"name": "complete",     "prob": 1.00},   # Fully filled (sanity check)
    # Biased variants: only P mint, only proof, only 1999-2002 era
    {"name": "p_only",       "prob": 0.00, "bias": "p"},
    {"name": "d_only",       "prob": 0.00, "bias": "d"},
    {"name": "proof_only",   "prob": 0.00, "bias": "proof"},
    {"name": "early_heavy",  "prob": 0.00, "bias": "early"},
    {"name": "late_sparse",  "prob": 0.00, "bias": "late"},
    {"name": "random_mix1",  "prob": 0.35},
    {"name": "random_mix2",  "prob": 0.55},
    {"name": "random_mix3",  "prob": 0.70},
    {"name": "random_mix4",  "prob": 0.45},
]

# Filled circle color — dark grey/black to match filled bullet
FILLED_COLOR = (0.1, 0.1, 0.1)


def find_circle_positions(page: fitz.Page) -> list:
    """
    Finds all empty circle glyphs on the page using character-level text extraction.
    Returns list of dicts: {x, y, width, height, char_index, block_info}
    """
    circles = []
    # Get character-level detail
    blocks = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]

    for block in blocks:
        if block.get("type") != 0:  # text block only
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                chars = span.get("chars", [])
                for ch in chars:
                    if ch.get("c") in CIRCLE_GLYPHS:
                        bbox = ch.get("bbox")  # (x0, y0, x1, y1)
                        if bbox:
                            circles.append({
                                "x0": bbox[0],
                                "y0": bbox[1],
                                "x1": bbox[2],
                                "y1": bbox[3],
                                "cx": (bbox[0] + bbox[2]) / 2,
                                "cy": (bbox[1] + bbox[3]) / 2,
                                "r":  (bbox[2] - bbox[0]) / 2 * 0.75,  # slightly smaller
                            })
    return circles


def assign_filled(circles: list, persona: dict, rng: random.Random) -> list:
    """
    Returns a boolean list — True = draw filled circle over this position.
    """
    bias = persona.get("bias")
    prob = persona.get("prob", 0.5)
    result = []
    n = len(circles)

    for i, c in enumerate(circles):
        if bias == "p":
            # Only fill every 4th circle starting at 0 (the P circles)
            filled = (i % 4 == 0)
        elif bias == "d":
            filled = (i % 4 == 1)
        elif bias == "proof":
            # S and S-Slv circles — positions 2 and 3 of each group of 4
            filled = (i % 4 in (2, 3))
        elif bias == "early":
            # First half of circles with high probability, rest sparse
            mid = n // 2
            filled = rng.random() < (0.8 if i < mid else 0.1)
        elif bias == "late":
            mid = n // 2
            filled = rng.random() < (0.1 if i < mid else 0.7)
        else:
            filled = rng.random() < prob
        result.append(filled)
    return result


def generate_variant(
    src_path: str,
    out_path: str,
    persona: dict,
    rng: random.Random,
) -> dict:
    """
    Creates one filled variant of the blank PDF.
    Returns metadata dict for the Document AI labeling file.
    """
    doc = fitz.open(src_path)
    page = doc[0]

    circles = find_circle_positions(page)
    filled_flags = assign_filled(circles, persona, rng)

    filled_count = 0
    for circle, is_filled in zip(circles, filled_flags):
        if is_filled:
            # Draw a solid dark disc over the empty circle glyph
            cx, cy, r = circle["cx"], circle["cy"], circle["r"]
            rect = fitz.Rect(cx - r, cy - r, cx + r, cy + r)
            page.draw_circle(
                fitz.Point(cx, cy),
                r,
                color=FILLED_COLOR,
                fill=FILLED_COLOR,
                overlay=True,
            )
            filled_count += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path, garbage=4, deflate=True)
    doc.close()

    return {
        "out_path":    out_path,
        "persona":     persona["name"],
        "total_slots": len(circles),
        "filled":      filled_count,
        "empty":       len(circles) - filled_count,
    }


def upload_to_gcs(local_path: str, gcs_path: str, bucket):
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path, content_type="application/pdf")
    return f"gs://{GCS_BUCKET}/{gcs_path}"


def process_pdf(pdf_path: str, upload: bool = True) -> list:
    """Process one blank PDF — generate all variants and upload."""
    stem = Path(pdf_path).stem
    rng = random.Random(RANDOM_SEED)
    results = []

    print(f"\n{'='*60}")
    print(f"Processing: {stem}")

    # Verify it has circles
    doc_check = fitz.open(pdf_path)
    test_circles = find_circle_positions(doc_check[0])
    doc_check.close()
    print(f"  Found {len(test_circles)} circle positions")

    if len(test_circles) == 0:
        print(f"  SKIP — no circle positions found (different format?)")
        return []

    creds = None
    bucket = None
    if upload:
        creds, _ = google.auth.default()
        gcs_client = gcs.Client(credentials=creds)
        bucket = gcs_client.bucket(GCS_BUCKET)

    for i, persona in enumerate(PERSONAS):
        out_filename = f"variant_{i:02d}_{persona['name']}.pdf"
        out_path = os.path.join(OUTPUT_DIR, stem, out_filename)
        gcs_key  = f"{GCS_PREFIX}/{stem}/{out_filename}"

        meta = generate_variant(pdf_path, out_path, persona, rng)

        if upload and bucket:
            gcs_url = upload_to_gcs(out_path, gcs_key, bucket)
            meta["gcs_url"] = gcs_url
            print(f"  [{i+1:2d}/{len(PERSONAS)}] {persona['name']:15s}  "
                  f"filled={meta['filled']:3d}/{meta['total_slots']}  -> {gcs_url}")
        else:
            print(f"  [{i+1:2d}/{len(PERSONAS)}] {persona['name']:15s}  "
                  f"filled={meta['filled']:3d}/{meta['total_slots']}  -> {out_path}")

        results.append(meta)

    return results


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Focus on checklists that use the radio-button circle format
    # (skip the Identification Chart and Mint Mark Guide which are different)
    SKIP = {
        "2026-US-Circulating-Coins-Identification-Chart-508.pdf",
        "LC53-Mint-Mark-Guide.pdf",
    }

    pdf_files = sorted(
        p for p in os.listdir(INPUT_DIR)
        if p.endswith(".pdf") and p not in SKIP
    )

    print(f"PDFs to process: {len(pdf_files)}")
    print(f"Variants per PDF: {len(PERSONAS)}")
    print(f"Total output files: {len(pdf_files) * len(PERSONAS)}")

    all_results = {}
    for fname in pdf_files:
        full_path = os.path.join(INPUT_DIR, fname)
        results = process_pdf(full_path, upload=True)
        all_results[fname] = results

    # Save summary JSON
    summary_path = os.path.join(OUTPUT_DIR, "generation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSummary saved: {summary_path}")
    print("Done!")


if __name__ == "__main__":
    main()
