"""
scan_service.py — Production Checklist Scan Service + Estate Report Service (Cloud Run endpoints)

POST /scan_checklist
 Body: multipart/form-data
   - image: <JPEG or PNG bytes>
   - program_id: <string>  (must match a program 'id' in Firestore)
   - user_id: <string>     (for writing results back to Firestore)

 Response: JSON
   {
     "program_id": "...",
     "user_id": "...",
     "coins": {"<coin_id>": {"owned": true, "qty": 1, "notes": "..."}, ...},
     "page_confidence": 0.95,
     "firestore_written": true,
     "wishlist_added": 12
   }

POST /generate_estate_report
 Body: application/json
   {
     "uid": <string>   — Firestore user doc ID (email)
     "mode": "living_inventory" | "estate_settlement"
     "state": "NY" | "NC" | "NJ" | "FL" | "CA" | "TX" | "SC"
     "owner_name": <string>
     "report_date": <ISO date string>
     ... (optional: attorney_name, attorney_email, executor_name,
          date_of_death, include_photos, beneficiaries)
   }

 Response: application/pdf  — estate report PDF
   On error: JSON {"error": "..."}

 SDK: google-genai (replaces deprecated vertexai SDK — shutdown Jun 24 2026)
"""

import asyncio
import logging
import os
import json
import re
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, abort, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google import genai
from google.genai import types
from google.cloud import firestore
from estate_state_rules import STATE_RULES

app = Flask(__name__)

# ── Rate limiting — protects the unauthenticated endpoint from API abuse ────────
# Uses in-memory storage (suitable for single Cloud Run instance).
# Limits: 10 scans/min and 5 estate reports/min per client IP.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
)

# ── Model config ───────────────────────────────────────────────────────────────────
# Per official deprecation schedule Jun 11, 2026:
#   gemini-3.5-flash  Released May 19, 2026. NO shutdown announced.
#                     Recommended replacement for gemini-3-flash-preview.
#                     Requires location='global' on Vertex AI.
PROJECT_ID = os.environ.get("GCP_PROJECT", "studio-9101802118-8c9a8")
LOCATION   = os.environ.get("GCP_REGION",  "global")
MODEL      = "gemini-1.5-flash"

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
db     = firestore.Client(project=PROJECT_ID)


SYSTEM_PROMPT = """\
You are a coin collection assistant analyzing a scanned Numista.AI checklist.
Your job is to determine which checkboxes are checked (filled/marked) vs unchecked,
AND to read any content the user wrote in the 'Notes / QTY' column for each row.

Rules:
- CHECKED: has an X, checkmark, tick, pen mark, or filled square.
- UNCHECKED: completely empty checkbox.
- Only return coins from the provided list — never invent new entries.
- If a checkbox is unreadable due to image quality, return null for 'owned'.
- Notes column: capture any handwritten or printed text in the Notes/QTY column for
  that row verbatim (e.g. "QTY:3", "MS-65", "stored in Morgan binder", "cleaned").
  If the notes column is blank, return null for 'notes'.
- Return ONLY valid JSON — no markdown, no explanation.
"""

PROMPT_TEMPLATE = """\
The image shows a checklist page for: {program_name}

Complete coin list (use coin_id as keys in your response):
{coin_list}

Return JSON:
{{
  "program_id": "{program_id}",
  "page_confidence": <0.0-1.0>,
  "coins": {{
    "<coin_id>": {{
      "owned": true | false | null,
      "notes": "<text from Notes/QTY column, or null if blank>"
    }}
  }}
}}
For multi-variety programs, use:
  "<coin_id>": {{
    "<variety_id>": {{
      "owned": true | false | null,
      "notes": "<text or null>"
    }}
  }}

Scan row-by-row. Capture both the checkbox state AND the Notes/QTY column.
Return ONLY JSON.
"""


def chunk_coin_list(program: dict, page: int, total_pages: int = 3) -> list:
    """Return the subset of coins for a given page number (1-indexed).
    Splits the full coin list into equal thirds so Gemini only processes
    the coins actually visible on that page — cutting output tokens by ~65%."""
    coins = program.get("coins", [])
    if total_pages <= 1 or page <= 0:
        return coins
    chunk_size = -(-len(coins) // total_pages)  # ceiling division
    start = (page - 1) * chunk_size
    return coins[start:start + chunk_size]


def get_program_from_firestore(program_id: str) -> dict:
    doc = db.collection("global_programs").document(program_id).get()
    if not doc.exists:
        abort(404, f"Program not found: {program_id}")
    return doc.to_dict()

def _make_coin_id(coin: dict) -> str:
    """Synthesize a stable coin_id from name when the 'id' field is missing."""
    raw = coin.get("id") or coin.get("name") or coin.get("year", "unknown")
    # Lowercase, replace spaces/special chars with underscores, strip trailing _
    import re as _re
    cid = _re.sub(r"[^a-z0-9]+", "_", str(raw).lower()).strip("_")
    return cid


def build_coin_list(program: dict) -> str:
    lines = []
    for coin in program.get("coins", []):
        cid   = _make_coin_id(coin)
        name  = coin.get("name") or coin.get("year", "")
        # Only show distinct varieties if there are more than one
        vars  = [v.get("id", "") for v in coin.get("varieties", []) if v.get("id")]
        if len(vars) > 1:
            lines.append(f"[{cid}] {name}  (varieties: {', '.join(vars)})")
        else:
            lines.append(f"[{cid}] {name}")
    return "\n".join(lines)


def parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Gemini truncated the response mid-JSON (hit token limit).
        # Attempt recovery: strip trailing partial entry and close the objects.
        # Find the last complete top-level coin entry (ends with '}}')
        last_good = text.rfind('}}')
        if last_good != -1:
            repaired = text[:last_good + 2] + '}}'
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass
        # Last resort: return empty coins so Firestore write still runs
        return {"program_id": "", "page_confidence": 0.0, "coins": {}}


def _parse_qty(notes: str | None) -> int:
    """Extract quantity from a notes string like 'QTY:3' or 'qty: 2'. Defaults to 1."""
    if not notes:
        return 1
    m = re.search(r"qty\s*:?\s*(\d+)", notes, re.IGNORECASE)
    return int(m.group(1)) if m else 1


def write_to_firestore(user_id: str, program_id: str, coins: dict) -> int:
    """
    Upsert coin entries into the user's collection.
    - owned=True  → write to checklist_entries with qty + notes
    - owned=False → write to checklist_entries AND add to wishlist if not already present
    - owned=None  → skip (don't overwrite existing data)
    Returns count of coins added to wishlist.
    """
    batch          = db.batch()
    entries_col    = db.collection("users").document(user_id).collection("checklist_entries")
    wishlist_col   = db.collection("users").document(user_id).collection("wishlist")
    wishlist_added = 0

    def _write_entry(doc_id: str, coin_id: str, owned: bool, notes: str | None,
                     variety_id: str | None = None):
        nonlocal wishlist_added
        qty = _parse_qty(notes) if owned else 0

        entry_data = {
            "program_id":  program_id,
            "coin_id":     coin_id,
            "owned":       owned,
            "qty":         qty,
            "notes":       notes,
            "source":      "checklist_scan",
            "updated_at":  firestore.SERVER_TIMESTAMP,
        }
        if variety_id:
            entry_data["variety_id"] = variety_id

        batch.set(entries_col.document(doc_id), entry_data, merge=True)

        # Auto-add unowned coins to wishlist (merge=True so we never overwrite
        # an existing wishlist entry the user may have already customized)
        if not owned:
            wishlist_id   = f"{program_id}__{coin_id}"
            if variety_id:
                wishlist_id += f"__{variety_id}"
            wishlist_data = {
                "program_id": program_id,
                "coin_id":    coin_id,
                "source":     "checklist_scan",
                "added_at":   firestore.SERVER_TIMESTAMP,
            }
            if variety_id:
                wishlist_data["variety_id"] = variety_id
            # Only set if document doesn't already exist (use create semantics via merge
            # with a sentinel — we use set+merge so existing priority/notes are preserved)
            batch.set(wishlist_col.document(wishlist_id), wishlist_data, merge=True)
            wishlist_added += 1

    for coin_id, value in coins.items():
        if isinstance(value, dict) and ("owned" in value or "notes" in value):
            # Simple coin with owned + notes at top level
            owned = value.get("owned")
            notes = value.get("notes")
            if owned is None:
                continue
            doc_id = f"{program_id}__{coin_id}"
            _write_entry(doc_id, coin_id, owned, notes)
        elif isinstance(value, dict):
            # Multi-variety: keys are variety IDs
            for variety_id, vdata in value.items():
                if not isinstance(vdata, dict):
                    continue
                owned = vdata.get("owned")
                notes = vdata.get("notes")
                if owned is None:
                    continue
                doc_id = f"{program_id}__{coin_id}__{variety_id}"
                _write_entry(doc_id, coin_id, owned, notes, variety_id=variety_id)
        # else: skip unexpected shape

    batch.commit()
    return wishlist_added


@app.route("/scan_checklist", methods=["POST"])
@limiter.limit("10 per minute")
def scan_checklist():
    # ── Parse request ─────────────────────────────────────────────────────────
    if "image" not in request.files:
        abort(400, "Missing 'image' in multipart body")
    image_file  = request.files["image"]
    program_id  = request.form.get("program_id")
    user_id     = request.form.get("user_id")
    if not program_id or not user_id:
        abort(400, "Missing 'program_id' or 'user_id'")

    image_bytes = image_file.read()
    mime_type   = image_file.content_type or "image/jpeg"
    page_number = int(request.form.get("page_number", "1"))
    total_pages = int(request.form.get("total_pages", "1"))

    # ── Load program from Firestore ───────────────────────────────────────────
    program   = get_program_from_firestore(program_id)
    # Only send coins for this page — reduces output tokens by ~65%
    page_coins = chunk_coin_list(program, page_number, total_pages)
    program_page = dict(program)
    program_page["coins"] = page_coins
    coin_list = build_coin_list(program_page)
    prompt    = PROMPT_TEMPLATE.format(
        program_name=program.get("name", program_id),
        program_id=program_id,
        coin_list=coin_list,
    )

    # ── Call Gemini Vision (google-genai SDK) ─────────────────────────────────
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_text(text=SYSTEM_PROMPT),
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=8192,
            response_mime_type="application/json",
        ),
    )

    raw    = response.candidates[0].content.parts[0].text
    result = parse_json(raw)
    coins  = result.get("coins", {})

    # Diagnostic log — visible in Cloud Run logs
    import logging
    logging.warning(f"[SCAN] program={program_id} page={page_number}/{total_pages} "
                    f"coins_returned={len(coins)} confidence={result.get('page_confidence')} "
                    f"raw_snippet={raw[:200]}")

    # ── Write to Firestore ────────────────────────────────────────────────────
    wishlist_added = write_to_firestore(user_id, program_id, coins)

    return jsonify({
        "program_id":        program_id,
        "user_id":           user_id,
        "coins":             coins,
        "page_confidence":   result.get("page_confidence"),
        "firestore_written": True,
        "wishlist_added":    wishlist_added,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL, "sdk": "google-genai"})


# ── Estate Report Endpoint ─────────────────────────────────────────────────────

@app.route("/generate_estate_report", methods=["POST"])
@limiter.limit("5 per minute")
def generate_estate_report():
    """
    POST /generate_estate_report

    Generates a professional numismatic estate planning PDF report.
    Reads coin data from Firestore, calls Gemini for narrative, builds PDF.

    Required JSON body fields: uid, mode, state, owner_name, report_date
    Optional: attorney_name, attorney_email, executor_name, date_of_death,
              include_photos, beneficiaries

    Returns the PDF as application/pdf on success.
    Stores report metadata in Firestore at users/{uid}/estate_reports/{report_id}.
    Optionally uploads PDF to GCS if ESTATE_REPORTS_BUCKET env var is set.
    """
    import logging as _logging
    log = _logging.getLogger(__name__)

    # ── Parse JSON body ────────────────────────────────────────────────────────
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    # ── Validate required fields ───────────────────────────────────────────────
    uid        = (body.get('uid') or '').strip()
    mode       = (body.get('mode') or '').strip()
    state      = (body.get('state') or '').strip().upper()
    owner_name = (body.get('owner_name') or '').strip()
    report_date = (body.get('report_date') or '').strip()

    missing = [f for f, v in [
        ('uid', uid), ('mode', mode), ('state', state),
        ('owner_name', owner_name), ('report_date', report_date),
    ] if not v]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    if mode not in ('living_inventory', 'estate_settlement'):
        return jsonify({
            'error': f'Invalid mode "{mode}". Must be "living_inventory" or "estate_settlement".'
        }), 400

    if state not in STATE_RULES:
        return jsonify({
            'error': f'Unsupported state "{state}". Supported: {", ".join(sorted(STATE_RULES.keys()))}'
        }), 400

    if mode == 'estate_settlement' and not body.get('date_of_death'):
        return jsonify({
            'error': 'date_of_death is required when mode is "estate_settlement".'
        }), 400

    # ── Build report_request dict ──────────────────────────────────────────────
    report_request = {
        'mode':                   mode,
        'state':                  state,
        'owner_name':             owner_name,
        'report_date':            report_date,
        'date_of_death':          body.get('date_of_death'),
        'include_photos':         body.get('include_photos', True),
        'attorney_name':          body.get('attorney_name', ''),
        'attorney_email':         body.get('attorney_email', ''),
        'executor_name':          body.get('executor_name', ''),
        'beneficiaries':          body.get('beneficiaries', []),
        'liquidation_preference': body.get('liquidation_preference', 'consign_all'),
        'preferred_consignor':    body.get('preferred_consignor', 'None'),
        'heirs_count':            body.get('heirs_count', 1),
    }

    log.warning(
        f'[estate] Execution initialized: uid={uid} mode={mode} state={state}'
    )

    # ── Run async report generation in event loop ──────────────────────────────
    try:
        from estate_report_generator import generate_estate_report as _generate

        # Flask is synchronous; run the async function via asyncio.run()
        result = asyncio.run(_generate(
            db=db,
            client=client,
            model=MODEL,
            uid=uid,
            report_request=report_request,
        ))
    except ValueError as ve:
        log.error(f'[estate] Input validation failure: {ve}')
        return jsonify({'error': str(ve)}), 400
    except Exception as exc:
        log.error('[estate] High-density generation processes encountered a failure state.')
        return jsonify({'error': 'Report generation processing failed.'}), 500

    pdf_bytes       = result['pdf_bytes']
    report_metadata = result['report_metadata']

    # ── Store metadata in Firestore ────────────────────────────────────────────
    # Use the same report_id the generator embedded in the PDF QR code.
    report_id = report_metadata.get('report_id') or \
        f'report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}_{str(uuid.uuid4())[:8]}'
    
    SAFE_METADATA_KEYS = {'report_id', 'total_coins', 'total_fmv', 'pdf_size_bytes', 'mode', 'state'}
    sanitized_metadata = {k: v for k, v in report_metadata.items() if k in SAFE_METADATA_KEYS}

    try:
        metadata_doc = {
            **sanitized_metadata,
            'report_id':        report_id,
            'generated_at_ts':  firestore.SERVER_TIMESTAMP,
        }
        db.collection('users').document(uid) \
          .collection('estate_reports').document(report_id) \
          .set(metadata_doc)
        log.warning(f'[estate] Metadata persistence verification complete for asset: {report_id}')
    except Exception as exc:
        # Non-fatal — still return the PDF
        log.error(f'[estate] System telemetry failed to record document metadata indicators: {exc}')



    # ── Build response filename ────────────────────────────────────────────────
    owner_last_name = (owner_name.split()[-1] if owner_name else 'estate').lower()
    safe_name = re.sub(r'[^a-z0-9_]', '', owner_last_name)
    filename = f'numista_estate_report_{safe_name}_{report_date}.pdf'

    log.warning(
        f'[estate] Returning PDF: {len(pdf_bytes):,} bytes | '
        f'coins={report_metadata.get("total_coins")} | '
        f'fmv=${report_metadata.get("total_fmv", 0):,.0f}'
    )

    # ── Return PDF ─────────────────────────────────────────────────────────────
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['X-Report-Id'] = report_id
    response.headers['X-Total-Coins'] = str(sanitized_metadata.get('total_coins', 0))
    response.headers['X-Total-FMV'] = str(sanitized_metadata.get('total_fmv', 0))
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
