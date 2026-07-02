"""
scan_multipage.py — Multi-page checklist scan

Scans all images in a folder, one page at a time, then merges
the coin results across pages into a single unified JSON result.

Usage:
    python scan_multipage.py "scans/Morgan Test" "Morgan"
"""

import sys, json, re, pathlib, os
from google import genai
from google.genai import types as genai_types

# ── Config ─────────────────────────────────────────────────────────────────────
# Deprecation chain (Gemini Deprecation Schedule, Apr 14 2026):
#   gemini-2.0-flash-001 → shutdown Jun  1 2026 → replaced by gemini-3.5-flash
#   gemini-3.5-flash     → shutdown Jun 17 2026 → replaced by gemini-3-flash-preview
#   gemini-3-flash-preview = current recommended (Public Preview, no shutdown listed)
#   IMPORTANT: post-Jun-2025 preview models require location='global' on Vertex AI
PROJECT_ID  = "studio-9101802118-8c9a8"
LOCATION    = "global"
MODEL       = "gemini-3-flash-preview"
MASTER_JSON = pathlib.Path(__file__).parent / "master_coin_programs.json"

SYSTEM_PROMPT = """\
You are a coin collection assistant analyzing ONE PAGE of a printed Numista.AI checklist.
Your job is to determine which checkboxes are checked AND to read the Notes/QTY column.

IMPORTANT RULES:
- CHECKED = has an X, checkmark, tick, pen mark, scribble, or filled area inside the box.
- UNCHECKED = completely empty, the box is blank.
- Notes/QTY column: read ANY text written in this column for each row, even if faint.
  - If it contains "QTY:N" or "QTY N" (e.g. QTY:3), extract the number as the quantity.
  - Any other text (e.g. "mishit", "MS65", "VF30") should be captured as notes.
- If a checkbox appears unchecked but has a QTY note, treat it as checked.
- Only return coin IDs from the provided list — never invent new entries.
- Only include coins that APPEAR on THIS PAGE.
- Return ONLY valid JSON — no markdown fences, no explanation text.
- Also look for an 'ADDITIONAL NOTES' ruled section at the bottom of the page and capture all text written there.
"""

PROMPT_TEMPLATE = """\
This is page {page_num} of a checklist for: {program_name}

The complete coin list for this program (all pages combined):
{coin_list}

Only process the coins visible on THIS PAGE IMAGE.
For each coin you can see on this page:
1. Determine if the "Owned?" checkbox is checked (true/false/null).
2. Read the "Notes / QTY" column for that row:
   - If it says "QTY:N" or similar, extract N as an integer quantity.
   - Any other handwritten text (grade like MS65, condition note, etc.) capture as a string.
3. If a row has notes but an ambiguous checkbox, treat it as owned=true.

Also check if there is an 'ADDITIONAL NOTES' section at the bottom of the page
with ruled lines for freeform text. If so, transcribe everything written there.

Return ONLY this JSON (include only coins visible on this page):
{{
  "page": {page_num},
  "page_confidence": <0.0 to 1.0>,
  "additional_notes": "<any text in the ADDITIONAL NOTES block, or null>",
  "coins": {{
    "<coin_id>": {{
      "owned": true | false | null,
      "quantity": <integer or null>,
      "notes": "<text from Notes/QTY column, or null>"
    }}
  }}
}}

Scan each row carefully left-to-right, top-to-bottom. Return ONLY the JSON object.
"""


def load_program(search_term: str) -> dict:
    data = json.loads(MASTER_JSON.read_text(encoding="utf-8"))
    term = search_term.lower()
    for p in data:
        if term in p.get("name", "").lower():
            return p
    raise ValueError(f"No program matching '{search_term}'")


def build_coin_list(program: dict) -> str:
    lines = []
    for i, coin in enumerate(program.get("coins", []), 1):
        yr    = coin.get("year", "")
        name  = coin.get("name", "")
        cid   = coin.get("id", name.replace(" ", "_"))
        label = f"{yr} - {name}".strip(" -") if yr and name != yr else (yr or name)
        vars_ = [v["id"] for v in coin.get("varieties", [])]
        if vars_ and len(vars_) > 1:
            lines.append(f"  {i:3}. [{cid}] {label}  (varieties: {', '.join(vars_)})")
        else:
            lines.append(f"  {i:3}. [{cid}] {label}")
    return "\n".join(lines)


def parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def scan_page(client, model_name: str, image_path: pathlib.Path, page_num: int,
              program: dict, coin_list: str) -> dict:
    img_bytes = image_path.read_bytes()
    mime = "image/jpeg" if image_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"

    prompt = PROMPT_TEMPLATE.format(
        page_num=page_num,
        program_name=program["name"],
        coin_list=coin_list,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=[
            genai_types.Part.from_text(text=SYSTEM_PROMPT),
            genai_types.Part.from_bytes(data=img_bytes, mime_type=mime),
            genai_types.Part.from_text(text=prompt),
        ],
        config=genai_types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=8192,
            response_mime_type="application/json",
        ),
    )

    raw = response.text
    return parse_json(raw)


def main():
    if len(sys.argv) < 3:
        print("Usage: python scan_multipage.py <image_folder> <program_name_fragment>")
        sys.exit(1)

    folder_path  = pathlib.Path(sys.argv[1])
    program_name = sys.argv[2]

    if not folder_path.exists():
        print(f"ERROR: Folder not found: {folder_path}")
        sys.exit(1)

    # Collect and sort images
    exts = {".jpg", ".jpeg", ".png"}
    images = sorted([f for f in folder_path.iterdir()
                     if f.suffix.lower() in exts])
    if not images:
        print(f"ERROR: No JPEG/PNG images found in {folder_path}")
        sys.exit(1)

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print(f"Found {len(images)} page(s): {[f.name for f in images]}")

    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    program   = load_program(program_name)
    coin_list = build_coin_list(program)

    print(f"Program : {program['name']}")
    print(f"Coins   : {len(program.get('coins', []))} total in context")
    print(f"Model   : {MODEL}")
    print("=" * 60)

    # ── Scan each page ────────────────────────────────────────────────────────
    merged_coins: dict = {}
    page_results = []

    for i, img_path in enumerate(images, 1):
        print(f"\nScanning page {i}: {img_path.name} ...")
        try:
            result = scan_page(client, MODEL, img_path, i, program, coin_list)
        except Exception as e:
            print(f"  ERROR on page {i}: {e}")
            continue

        page_coins = result.get("coins", {})
        conf       = result.get("page_confidence", "?")
        add_notes  = result.get("additional_notes")
        checked    = sum(1 for v in page_coins.values()
                         if (isinstance(v, dict) and v.get("owned")) or v is True)
        unchecked  = sum(1 for v in page_coins.values()
                         if (isinstance(v, dict) and v.get("owned") is False) or v is False)
        unknown    = sum(1 for v in page_coins.values()
                         if (isinstance(v, dict) and v.get("owned") is None) or v is None)
        with_notes = sum(1 for v in page_coins.values()
                         if isinstance(v, dict) and
                         (v.get("quantity") or v.get("notes")))

        print(f"  Confidence    : {conf}")
        print(f"  Coins seen    : {len(page_coins)}  "
              f"(checked={checked}, unchecked={unchecked}, unknown={unknown})")
        if with_notes:
            print(f"  With notes    : {with_notes} rows have Notes/QTY text")
        if add_notes:
            print(f"  Add. notes    : {add_notes}")

        page_results.append(result)

        # Merge — later pages can override earlier ones for the same coin_id
        for coin_id, entry in page_coins.items():
            # Normalise: old-style bool → new-style dict
            if isinstance(entry, bool) or entry is None:
                entry = {"owned": entry, "quantity": None, "notes": None}
            if coin_id not in merged_coins or entry.get("owned") is not None:
                merged_coins[coin_id] = entry

    # ── Summary ───────────────────────────────────────────────────────────────
    total_checked   = sum(1 for v in merged_coins.values()
                         if isinstance(v, dict) and v.get("owned"))
    total_unchecked = sum(1 for v in merged_coins.values()
                         if isinstance(v, dict) and v.get("owned") is False)
    total_unknown   = sum(1 for v in merged_coins.values()
                         if isinstance(v, dict) and v.get("owned") is None)
    total_qty       = sum(
        (v.get("quantity") or 1)
        for v in merged_coins.values()
        if isinstance(v, dict) and v.get("owned")
    )

    final = {
        "program":   program["name"],
        "pages":     len(images),
        "summary":   {
            "total_coins_in_program": len(program.get("coins", [])),
            "coins_detected_in_scan": len(merged_coins),
            "unique_coins_owned":     total_checked,
            "total_quantity_owned":   total_qty,
            "unchecked":             total_unchecked,
            "unknown":               total_unknown,
        },
        "coins": merged_coins,
        "per_page": page_results,
    }

    print("\n" + "=" * 60)
    print("FINAL MERGED RESULT")
    print(f"  Unique coins owned : {total_checked}")
    print(f"  Total qty (w/ QTY) : {total_qty}")
    print(f"  Unchecked          : {total_unchecked}")
    print(f"  Unknown/skipped    : {total_unknown}")
    print(f"  Coins detected     : {len(merged_coins)} / {len(program.get('coins', []))}")

    # Print checked coins with qty and notes
    if total_checked > 0:
        print("\nCHECKED COINS:")
        for cid, entry in merged_coins.items():
            if isinstance(entry, dict) and entry.get("owned"):
                qty   = entry.get("quantity")
                notes = entry.get("notes")
                line  = f"  [x] {cid}"
                if qty and qty > 1:
                    line += f"  (QTY: {qty})"
                if notes:
                    line += f"  -- {notes}"
                print(line)

    # Save result
    safe = program_name.lower().replace(" ", "_")
    out  = pathlib.Path(f"{safe}_scan_result.json")
    out.write_text(json.dumps(final, indent=2), encoding="utf-8")
    print(f"\nFull result saved to: {out}")


if __name__ == "__main__":
    main()
