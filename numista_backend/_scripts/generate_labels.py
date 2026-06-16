"""
generate_labels.py
==================
Automatically generates Document AI ground truth labels for every
synthetic training document we created.

Since WE generated the filled PDFs programmatically, we know EXACTLY:
  - Which circles are filled (from the random seed + persona)
  - Where each circle is on the page (from PDF text extraction)
  - Which coin + mint mark each circle represents (from text alignment)

This script:
1. Parses each blank PDF to extract coin rows and their circle positions
2. Replays the exact same fill decisions (same seed) for each variant
3. Outputs Document AI JSONL ground truth files to GCS

Document AI Custom Extractor import format (document.jsonl):
  One JSON object per line, each representing one labeled document.
  https://cloud.google.com/document-ai/docs/workbench/label-api

Output: gs://numista-training-docs/Numista.AI Training Data/Labels/<stem>/labels.jsonl
"""

import fitz
import random
import os
import sys
import json
import re
from pathlib import Path
from google.cloud import storage as gcs
import google.auth

sys.stdout.reconfigure(encoding='utf-8')

# ── Config (must match generate_training_docs.py) ─────────────────────────────
INPUT_DIR    = r"C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs"
OUTPUT_DIR   = r"C:\Users\ericd\Documents\MyVertexProject\training_output"
GCS_BUCKET   = "numista-training-docs"
GCS_SYNTH    = "Numista.AI Training Data/Synthetic Filled"
GCS_LABELS   = "Numista.AI Training Data/Labels"
RANDOM_SEED  = 42

# New dedicated checklist processor (separate from receipt processor c113e9bb62be1554)
CHECKLIST_PROCESSOR_ID = "7425afc720652ee4"
CHECKLIST_PROCESSOR_PATH = f"projects/568985927038/locations/us/processors/{CHECKLIST_PROCESSOR_ID}"

CIRCLE_CHARS        = {"\uf0a6", "\uf06d", "\u00a6"}
WINGDINGS_FONT_NAMES = {"wingdings-regular", "wingdings", "wingdings 2", "wingdings 3"}

SKIP = {
    "2026-US-Circulating-Coins-Identification-Chart-508.pdf",
    "LC53-Mint-Mark-Guide.pdf",
}

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


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_circles(page: fitz.Page) -> list:
    """Returns list of (cx, cy, radius) for every radio button circle."""
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
                    if c in CIRCLE_CHARS or (c == "\ufffd" and is_wingdings):
                        b = ch.get("bbox")
                        if b:
                            cx = (b[0] + b[2]) / 2
                            cy = (b[1] + b[3]) / 2
                            r  = (b[2] - b[0]) / 2 * 0.75
                            circles.append({
                                "cx": cx, "cy": cy, "r": r,
                                "bbox": list(b),   # [x0,y0,x1,y1]
                            })
    return circles


def extract_coin_rows(page: fitz.Page) -> list:
    """
    Extracts coin entries from the text layer, aligned by Y position.
    Returns list of dicts: {text, x, y, bbox}
    Filters out header/footer text, keeping only coin name lines.
    """
    rows = []
    # Known non-coin text to skip
    SKIP_PATTERNS = [
        r"^(unc|proof|date|statehood|mint\s?mark|key|philadelphia|denver|san francisco|"
        r"carson city|new orleans|for additional|learn about|littleton|serving|"
        r"lc-|©|\d{4}\s+lcc|common|obverse|reverse|\*coins|in\s+\d{4}|these coins|"
        r"when\s+first|the\s+following|mint\s+set|struck\s+in)",
        r"^\s*$",
        r"^[0-9]{4}$",      # Plain year headers like "1999", "2003"
        r"^[pds].+key",
    ]
    skip_re = re.compile("|".join(SKIP_PATTERNS), re.IGNORECASE)

    blocks = page.get_text("blocks")
    for b in blocks:
        x0, y0, x1, y1, text, *_ = b
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line or skip_re.search(line):
                continue
            # Coin rows are typically short: "Delaware", "1879-S", "1878 all kinds*"
            if len(line) > 60:
                continue
            rows.append({
                "text": line,
                "x": x0,
                "y": y0,
                "bbox": [x0, y0, x1, y1],
            })
    return rows


def match_circles_to_coins(circles: list, page: fitz.Page, page_w: float, page_h: float) -> list:
    """
    Attempts to match each circle to a coin row + column position.
    For unknown layouts, returns simplified entries with position info.
    
    Returns list of coin_slot dicts aligned with the circles list:
    {
        "circle_index": int,
        "coin_label": str,       # best guess coin name
        "mint_label": str,       # "P", "D", "S", "S-Slv", "CC", "O", etc.
        "cx": float, "cy": float,
        "bbox": [x0,y0,x1,y1],  # circle bounding box
    }
    """
    coin_rows = extract_coin_rows(page)

    # Group circles by approximate Y band (row height ~14 pts)
    ROW_TOLERANCE = 8  # pts
    circle_rows = {}
    for i, c in enumerate(circles):
        key = round(c["cy"] / ROW_TOLERANCE) * ROW_TOLERANCE
        circle_rows.setdefault(key, []).append((i, c))

    # Sort circles within each row by X
    for key in circle_rows:
        circle_rows[key].sort(key=lambda x: x[1]["cx"])

    # Sort text rows by Y
    coin_rows_sorted = sorted(coin_rows, key=lambda r: r["y"])

    # Build flat circle metadata list
    circle_meta = [None] * len(circles)

    # Simple pass: for each circle, find the nearest coin label by Y proximity
    for key_y, row_circles in sorted(circle_rows.items()):
        # Find nearest coin text row
        nearest_coin = None
        min_dist = float("inf")
        for cr in coin_rows_sorted:
            dist = abs(cr["y"] - key_y)
            if dist < min_dist:
                min_dist = dist
                nearest_coin = cr

        coin_label = nearest_coin["text"] if nearest_coin and min_dist < 30 else "unknown"

        # Assign mint marks by position within the row
        # Littleton consistently uses: leftmost = P, next = D, then S, then S-Slv
        MINT_SEQUENCE = ["P", "D", "S", "S-Slv"]
        for pos, (idx, c) in enumerate(row_circles):
            mint = MINT_SEQUENCE[pos] if pos < len(MINT_SEQUENCE) else f"slot{pos}"
            circle_meta[idx] = {
                "circle_index": idx,
                "coin_label": coin_label,
                "mint_label": mint,
                "cx": c["cx"],
                "cy": c["cy"],
                "bbox": c["bbox"],
            }

    return circle_meta


def assign_filled(n_circles: int, persona: dict, rng: random.Random) -> list:
    """Replays the exact fill decisions used during generation."""
    bias = persona.get("bias")
    prob = persona.get("prob", 0.5)
    result = []
    for i in range(n_circles):
        if bias == "p":       filled = (i % 4 == 0)
        elif bias == "d":     filled = (i % 4 == 1)
        elif bias == "proof": filled = (i % 4 in (2, 3))
        elif bias == "early": filled = rng.random() < (0.8 if i < n_circles // 2 else 0.1)
        elif bias == "late":  filled = rng.random() < (0.1 if i < n_circles // 2 else 0.7)
        else:                 filled = rng.random() < prob
        result.append(filled)
    return result


def make_document_ai_label(gcs_uri: str, filled_flags: list,
                           circle_meta: list, page_w: float, page_h: float) -> dict:
    """
    Builds a Document AI ground truth document label.
    Format: Document proto JSON
    https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    """
    entities = []
    
    # Group circles by (coin_label, approximate_y) to create coin_entry parents
    from collections import defaultdict
    coin_groups = defaultdict(list)
    for i, meta in enumerate(circle_meta):
        if meta is None:
            continue
        key = (meta["coin_label"], round(meta["cy"] / 8) * 8)
        coin_groups[key].append((i, meta, filled_flags[i]))

    for (coin_label, _), slots in coin_groups.items():
        if not slots:
            continue

        # Compute bounding box of entire coin row
        all_x = [m["bbox"][0] for _, m, _ in slots] + [m["bbox"][2] for _, m, _ in slots]
        all_y = [m["bbox"][1] for _, m, _ in slots] + [m["bbox"][3] for _, m, _ in slots]
        row_bbox = [min(all_x), min(all_y), max(all_x), max(all_y)]

        def norm_vertex(x, y):
            return {"x": round(x / page_w, 4), "y": round(y / page_h, 4)}

        def bbox_to_poly(b):
            return {"normalizedVertices": [
                norm_vertex(b[0], b[1]),
                norm_vertex(b[2], b[1]),
                norm_vertex(b[2], b[3]),
                norm_vertex(b[0], b[3]),
            ]}

        properties = []

        # coin_subject property
        properties.append({
            "type": "coin_subject",
            "mentionText": coin_label,
            "pageAnchor": {
                "pageRefs": [{"page": 0, "boundingPoly": bbox_to_poly(row_bbox)}]
            }
        })

        # Per-mint properties
        for idx, meta, is_filled in slots:
            c_bbox = meta["bbox"]
            properties.append({
                "type": f"has_{meta['mint_label'].lower().replace('-', '_')}",
                "mentionText": "true" if is_filled else "false",
                "pageAnchor": {
                    "pageRefs": [{"page": 0, "boundingPoly": bbox_to_poly(c_bbox)}]
                }
            })

        entities.append({
            "type": "coin_entry",
            "mentionText": coin_label,
            "pageAnchor": {
                "pageRefs": [{"page": 0, "boundingPoly": bbox_to_poly(row_bbox)}]
            },
            "properties": properties,
        })

    return {
        "gcsUri": gcs_uri,
        "mimeType": "application/pdf",
        "entities": entities,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    creds, _ = google.auth.default()
    gcs_client = gcs.Client(credentials=creds)
    bucket = gcs_client.bucket(GCS_BUCKET)

    pdf_files = sorted(
        p for p in os.listdir(INPUT_DIR)
        if p.endswith(".pdf") and p not in SKIP
    )

    total_labels = 0

    for fname in pdf_files:
        stem = fname.replace(".pdf", "")
        src  = os.path.join(INPUT_DIR, fname)

        doc = fitz.open(src)
        page = doc[0]
        page_w, page_h = page.rect.width, page.rect.height
        circles = find_circles(page)
        circle_meta = match_circles_to_coins(circles, page, page_w, page_h)
        doc.close()

        if not circles:
            print(f"SKIP (no circles): {fname}")
            continue

        print(f"\nLabeling: {stem} ({len(circles)} circles, {len(circle_meta)} mapped)")

        jsonl_lines = []
        rng = random.Random(RANDOM_SEED)

        for i, persona in enumerate(PERSONAS):
            filled_flags = assign_filled(len(circles), persona, rng)
            gcs_uri = (f"gs://{GCS_BUCKET}/{GCS_SYNTH}/{stem}/"
                       f"variant_{i:02d}_{persona['name']}.pdf")

            label_doc = make_document_ai_label(
                gcs_uri, filled_flags, circle_meta, page_w, page_h
            )
            jsonl_lines.append(json.dumps(label_doc))

        # Write JSONL locally
        local_labels_dir = os.path.join(OUTPUT_DIR, "labels", stem)
        os.makedirs(local_labels_dir, exist_ok=True)
        local_jsonl = os.path.join(local_labels_dir, "labels.jsonl")
        with open(local_jsonl, "w", encoding="utf-8") as f:
            f.write("\n".join(jsonl_lines))

        # Upload to GCS
        gcs_key = f"{GCS_LABELS}/{stem}/labels.jsonl"
        blob = bucket.blob(gcs_key)
        blob.upload_from_filename(local_jsonl, content_type="application/jsonl")
        print(f"  Uploaded {len(jsonl_lines)} label entries -> gs://{GCS_BUCKET}/{gcs_key}")
        total_labels += len(jsonl_lines)

    print(f"\nDone! {total_labels} total label documents uploaded.")
    print(f"GCS labels location: gs://{GCS_BUCKET}/{GCS_LABELS}/")


if __name__ == "__main__":
    main()
