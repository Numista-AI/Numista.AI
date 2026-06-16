"""
test_scan_checklist.py — Gemini Vision Checklist Scan Pipeline (Option B)

Reads a scanned/photographed Numista.AI checklist image (JPEG or PNG),
sends it to Gemini Vision with the program's coin list as context, and
returns a structured JSON of which coins are checked.

Usage:
    python test_scan_checklist.py <image_path> <program_name_fragment>
    python test_scan_checklist.py scans/morgan_page1.jpg "Morgan"
    python test_scan_checklist.py scans/ike_checklist.jpg "Eisenhower"

Output:
    Prints JSON + writes <program>_scan_result.json
"""

import sys, json, base64, pathlib, re, os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

# ── Config ────────────────────────────────────────────────────────────────────
# Deprecation chain (Gemini Deprecation Schedule, Apr 14 2026):
#   gemini-2.0-flash-001 → shutdown Jun  1 2026 → replaced by gemini-2.5-flash
#   gemini-2.5-flash     → shutdown Jun 17 2026 → replaced by gemini-3-flash-preview
#   gemini-3-flash-preview = current recommended model (Public Preview, no shutdown listed)
#   IMPORTANT: post-Jun-2025 preview models require location='global' on Vertex AI
PROJECT_ID  = "studio-9101802118-8c9a8"
LOCATION    = "global"           # required for gemini-3-flash-preview
MODEL       = "gemini-3-flash-preview"
MASTER_JSON = pathlib.Path(__file__).parent / "master_coin_programs.json"

# ── Prompt template ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a coin collection assistant analyzing a scanned Numista.AI checklist.
Your job is to determine which checkboxes are checked (filled/marked) vs unchecked (empty).

IMPORTANT RULES:
- A checkbox is CHECKED if it has an X, checkmark, tick, pen mark, or is filled.
- A checkbox is UNCHECKED if it is completely empty / blank.
- You must ONLY return coins from the provided list — do not invent new entries.
- If you cannot read a row due to image quality, mark it as null (unknown).
- Return ONLY valid JSON — no markdown fences, no explanation text.
"""

EXTRACTION_PROMPT_TEMPLATE = """\
The image shows a page from a printed checklist for: {program_name}

Here is the complete list of coins that appear on this checklist (in order):
{coin_list}

For each coin in the list, determine if its "Owned?" checkbox is checked.
If the checklist uses variety columns (P, D, S etc.), return an object per coin with keys for each variety.

Return a JSON object in this exact format:
{{
  "program": "{program_name}",
  "page_confidence": 0.0-1.0,
  "coins": {{
    "<coin_id>": true | false | null,
    ...
  }}
}}

For multi-variety programs, use:
{{
  "coins": {{
    "<coin_id>": {{"P": true|false|null, "D": true|false|null, "S": true|false|null}},
    ...
  }}
}}

Scan the image carefully row by row. Return only JSON.
"""


def load_program(search_term: str) -> dict:
    """Find matching program in master JSON."""
    data = json.loads(MASTER_JSON.read_text(encoding="utf-8"))
    term = search_term.lower()
    for p in data:
        if term in p.get("name", "").lower():
            return p
    raise ValueError(f"No program matching '{search_term}'")


def build_coin_list(program: dict) -> str:
    """Build a human-readable numbered coin list for the prompt context."""
    lines = []
    for i, coin in enumerate(program.get("coins", []), 1):
        yr   = coin.get("year", "")
        name = coin.get("name", "")
        cid  = coin.get("id", name.replace(" ", "_"))
        vars = [v["id"] for v in coin.get("varieties", [])]
        label = f"{yr} - {name}".strip(" -") if yr and name != yr else (yr or name)
        if vars and len(vars) > 1:
            lines.append(f"  {i:3}. [{cid}] {label}  (varieties: {', '.join(vars)})")
        else:
            lines.append(f"  {i:3}. [{cid}] {label}")
    return "\n".join(lines)


def image_to_part(image_path: str) -> Part:
    """Load image file and convert to Gemini Part."""
    path = pathlib.Path(image_path)
    data = path.read_bytes()
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return Part.from_data(data=data, mime_type=mime)


def parse_response(text: str) -> dict:
    """Strip any accidental markdown fences and parse JSON."""
    text = text.strip()
    # Strip ```json ... ``` if Gemini accidentally adds it
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def scan_checklist(image_path: str, program_name: str) -> dict:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL)

    program  = load_program(program_name)
    coin_list = build_coin_list(program)
    prompt   = EXTRACTION_PROMPT_TEMPLATE.format(
        program_name=program["name"],
        coin_list=coin_list,
    )

    print(f"Program    : {program['name']}")
    print(f"Coins      : {len(program.get('coins', []))} entries in context")
    print(f"Image      : {image_path}")
    print(f"Model      : {MODEL}")
    print("-" * 60)

    response = model.generate_content(
        [
            Part.from_text(SYSTEM_PROMPT),
            image_to_part(image_path),
            Part.from_text(prompt),
        ],
        generation_config=GenerationConfig(
            temperature=0.0,        # deterministic — no creativity needed
            max_output_tokens=8192,
            response_mime_type="application/json",  # enforce JSON output
        ),
    )

    raw = response.candidates[0].content.parts[0].text
    result = parse_response(raw)

    # ── Confidence summary ────────────────────────────────────────────────────
    coins = result.get("coins", {})
    checked   = sum(1 for v in coins.values() if v is True or
                    (isinstance(v, dict) and any(vv is True for vv in v.values())))
    unknown   = sum(1 for v in coins.values() if v is None or
                    (isinstance(v, dict) and any(vv is None for vv in v.values())))

    print(f"Confidence : {result.get('page_confidence', '?')}")
    print(f"Checked    : {checked} coins")
    print(f"Unknown    : {unknown} coins (low quality / unreadable)")
    print(f"Total parsed: {len(coins)}")

    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_scan_checklist.py <image_path> <program_name_fragment>")
        print("  e.g. python test_scan_checklist.py scans/morgan.jpg 'Morgan'")
        sys.exit(1)

    image_path   = sys.argv[1]
    program_name = sys.argv[2]

    if not pathlib.Path(image_path).exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    result = scan_checklist(image_path, program_name)

    # Pretty-print result
    print("\n── RESULT JSON ──────────────────────────────────────────────────")
    print(json.dumps(result, indent=2))

    # Save to file
    safe = program_name.lower().replace(" ", "_")
    out  = pathlib.Path(f"{safe}_scan_result.json")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nSaved to: {out}")


if __name__ == "__main__":
    main()
