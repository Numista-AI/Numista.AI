"""
auto_label_receipts.py
======================
Auto-labels coin purchase invoice scans for Document AI training.

Pipeline:
  1. Collect PDFs from local Scans folder (deduplicate multi-part scans)
  2. Upload to gs://numista-training-docs/receipt-training/
  3. Send each PDF to Gemini Vision to extract structured invoice data
  4. Convert Gemini extractions to Document AI training labels
  5. Upload label files alongside PDFs
  6. Import PDFs + labels into the Coin Receipts Data Extractor dataset

Schema being labeled:
  Invoice level: invoice_number, date, customer_name, customer_number,
                 retailer_phone, retailer_website, total_amount
  line_item[]:  item_number, quantity, club_selection, description,
                condition, certification, amount
"""
import sys, os, json, re, base64, time
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from google.cloud import storage, documentai_v1beta3 as docai
from google.protobuf import field_mask_pb2
import google.auth
from google import genai
from google.genai import types as genai_types

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ID        = "568985927038"
VERTEX_PROJECT    = "studio-9101802118-8c9a8"
LOCATION          = "us"
VERTEX_REGION     = "us-central1"
RECEIPT_PROC_ID   = "c113e9bb62be1554"
GCS_BUCKET        = "numista-training-docs"
GCS_RECEIPT_DIR   = "receipt-training"
SCANS_DIR         = Path(r"C:\Users\ericd\Documents\MyVertexProject\Scans 28 JAN 2026")
OUTPUT_DIR        = Path(r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\receipt_labels")
DATASET_NAME      = (f"projects/{PROJECT_ID}/locations/{LOCATION}"
                     f"/processors/{RECEIPT_PROC_ID}/dataset")
MODEL_ID          = "gemini-2.5-flash"

GEMINI_PROMPT = """
You are analyzing a scanned coin purchase invoice. Extract the following data
and return ONLY valid JSON — no markdown, no commentary.

Return this exact structure (omit keys that are absent from the document):
{
  "invoice_number": "...",
  "date": "YYYY-MM-DD",
  "customer_name": "...",
  "customer_number": "...",
  "retailer_phone": "...",
  "retailer_website": "...",
  "total_amount": "...",
  "rewards_points_earned": "...",
  "line_items": [
    {
      "item_number": "...",
      "quantity": 1,
      "club_selection": "...",
      "description": "...",
      "condition": "...",
      "certification": "...",
      "amount": "..."
    }
  ]
}

Rules:
- invoice_number: the Inv# or invoice number printed on the document
- date: normalize to YYYY-MM-DD (e.g., "10/30/23" -> "2023-10-30")
- customer_number: labeled Cust#, Account#, or similar
- retailer_phone: the toll-free or contact phone number
- club_selection: any club/program name above the coin description (e.g. "WASHINGTON QUARTER CLUB SELECTION")
- description: the full coin description text (year, type, variety, certification label if present)
- condition: the grade/condition string exactly as printed (e.g. "Extra Fine 4", "MS-63", "Proof 69 DCAM")
- certification: just the service abbreviation if graded (NGC, PCGS, ANACS, ICG) — separate from description
- amount: the dollar amount for that line item (numbers only, no $ sign)
- total_amount: the invoice total if shown
- If a field is not present in the document, OMIT it from the JSON entirely.
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def collect_pdfs(scans_dir: Path) -> list[Path]:
    """
    Collect PDFs, keeping only the largest (most complete) file for each
    multi-part group (e.g. variant_Part1..Part5 -> keep Part5 only).
    """
    all_pdfs = sorted(scans_dir.rglob("*.pdf"))
    # Group multi-part scans: key by base name without _PartN suffix
    groups: dict[str, list[Path]] = {}
    for pdf in all_pdfs:
        # Match pattern like "Scan_... (109)_Part3.pdf"
        m = re.match(r"^(.*?)(_Part\d+)?\.pdf$", pdf.name, re.IGNORECASE)
        if m:
            base = m.group(1)
        else:
            base = pdf.stem
        key = str(pdf.parent / base)
        groups.setdefault(key, []).append(pdf)

    result = []
    for key, parts in groups.items():
        if len(parts) == 1:
            result.append(parts[0])
        else:
            # Keep only the largest file (most complete multi-page PDF)
            largest = max(parts, key=lambda p: p.stat().st_size)
            skipped = [p.name for p in parts if p != largest]
            print(f"  Multi-part: keeping {largest.name}, skipping {skipped}")
            result.append(largest)
    return sorted(result)


def upload_to_gcs(local_path: Path, bucket, gcs_dir: str) -> str:
    gcs_path = f"{gcs_dir}/{local_path.name}"
    blob = bucket.blob(gcs_path)
    if not blob.exists():
        blob.upload_from_filename(str(local_path))
        print(f"    Uploaded: {gcs_path}")
    else:
        print(f"    Exists:   {gcs_path}")
    return f"gs://{GCS_BUCKET}/{gcs_path}"


def call_gemini(client, model_name: str, pdf_path: Path) -> dict | None:
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_part = genai_types.Part.from_bytes(mime_type="application/pdf", data=pdf_bytes)
        response = client.models.generate_content(
            model=model_name,
            contents=[GEMINI_PROMPT, pdf_part]
        )
        text = response.text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        print(f"    Raw response: {text[:200]}")
        return None
    except Exception as e:
        print(f"    Gemini error: {type(e).__name__}: {e}")
        return None


def build_label_jsonl(gcs_uri: str, extraction: dict) -> dict:
    """
    Build a Document AI import label record.
    Uses text mention approach — Document AI will match text during import.
    """
    entities = []

    def add_entity(etype: str, value: str):
        if value:
            entities.append({
                "type": etype,
                "mentionText": str(value),
            })

    # Invoice-level fields
    add_entity("invoice_number", extraction.get("invoice_number", ""))
    add_entity("date", extraction.get("date", ""))
    add_entity("customer_name", extraction.get("customer_name", ""))
    add_entity("customer_number", extraction.get("customer_number", ""))
    add_entity("retailer_phone", extraction.get("retailer_phone", ""))
    add_entity("retailer_website", extraction.get("retailer_website", ""))
    add_entity("total_amount", extraction.get("total_amount", ""))
    add_entity("rewards_points_earned", extraction.get("rewards_points_earned", ""))

    # Per-line-item nested entities
    for item in extraction.get("line_items", []):
        child_entities = []
        def add_child(etype, val):
            if val:
                child_entities.append({
                    "type": etype,
                    "mentionText": str(val),
                })
        add_child("item_number",   item.get("item_number", ""))
        add_child("quantity",      str(item.get("quantity", "")))
        add_child("club_selection", item.get("club_selection", ""))
        add_child("description",   item.get("description", ""))
        add_child("condition",     item.get("condition", ""))
        add_child("certification", item.get("certification", ""))
        add_child("amount",        item.get("amount", ""))

        entities.append({
            "type": "line_item",
            "mentionText": item.get("description", ""),
            "properties": child_entities,
        })

    return {
        "document": {"gcsUri": gcs_uri, "mimeType": "application/pdf"},
        "entities": entities,
    }


def import_to_dataset(docai_client, gcs_uris: list[str]):
    """Import all PDFs into the receipt processor dataset."""
    print(f"\nImporting {len(gcs_uris)} PDFs into Document AI dataset...")
    configs = []
    for uri in gcs_uris:
        # Import each file individually so we can track progress
        folder = uri.rsplit("/", 1)[0] + "/"
        if folder not in [c["folder"] for c in configs]:
            configs.append({"folder": folder})

    # Build one big import from the parent GCS folder
    gcs_prefix = f"gs://{GCS_BUCKET}/{GCS_RECEIPT_DIR}/"
    try:
        op = docai_client.import_documents(
            request=docai.ImportDocumentsRequest(
                dataset=DATASET_NAME,
                batch_documents_import_configs=[
                    docai.ImportDocumentsRequest.BatchDocumentsImportConfig(
                        batch_input_config=docai.BatchDocumentsInputConfig(
                            gcs_prefix=docai.GcsPrefix(gcs_uri_prefix=gcs_prefix)
                        ),
                        dataset_split=docai.DatasetSplitType.DATASET_SPLIT_TRAIN,
                    )
                ]
            )
        )
        print(f"  Import operation started: {op.operation.name}")
        print("  (Runs in background — check Label & Build page in a few minutes)")
        return op.operation.name
    except Exception as e:
        print(f"  Import failed: {type(e).__name__}: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Coin Receipt Auto-Labeling Pipeline")
    print("=" * 60)

    # Init clients
    creds, _ = google.auth.default()
    gcs_client = storage.Client(credentials=creds)
    bucket = gcs_client.bucket(GCS_BUCKET)
    docai_client = docai.DocumentServiceClient(
        credentials=creds,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    )
    client = genai.Client(vertexai=True, project=VERTEX_PROJECT, location=VERTEX_REGION)

    # Step 1: Collect PDFs
    print("\nStep 1: Collecting PDFs...")
    pdfs = collect_pdfs(SCANS_DIR)
    print(f"  Found {len(pdfs)} unique invoices (after deduplication)")

    # Step 2: Upload + Gemini label
    print("\nStep 2: Uploading to GCS & extracting with Gemini...")
    review_records = []
    gcs_uris = []
    label_lines = []

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n  [{i}/{len(pdfs)}] {pdf_path.name}")

        # Upload PDF
        gcs_uri = upload_to_gcs(pdf_path, bucket, GCS_RECEIPT_DIR)
        gcs_uris.append(gcs_uri)

        # Gemini extraction
        print(f"    Calling Gemini...")
        extraction = call_gemini(client, MODEL_ID, pdf_path)
        if extraction:
            inv = extraction.get("invoice_number", "N/A")
            items = len(extraction.get("line_items", []))
            print(f"    Extracted: Inv#{inv}, {items} line item(s)")
            label_rec = build_label_jsonl(gcs_uri, extraction)
            label_lines.append(json.dumps(label_rec))
            review_records.append({"file": pdf_path.name, "extraction": extraction})
        else:
            print(f"    Gemini extraction failed — doc will be unlabeled")
            review_records.append({"file": pdf_path.name, "extraction": None})

        # Rate limit: avoid hammering Gemini
        time.sleep(1.5)

    # Step 3: Save review file
    review_path = OUTPUT_DIR / "gemini_review.json"
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_records, f, indent=2)
    print(f"\nStep 3: Review file saved → {review_path}")

    # Step 4: Save label JSONL
    label_path = OUTPUT_DIR / "receipt_labels.jsonl"
    with open(label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(label_lines))
    print(f"Step 4: Labels saved → {label_path}")
    print(f"  Labeled: {len(label_lines)} / {len(pdfs)} documents")

    # Step 5: Upload label file to GCS
    label_blob = bucket.blob(f"{GCS_RECEIPT_DIR}/labels/receipt_labels.jsonl")
    label_blob.upload_from_filename(str(label_path))
    print(f"Step 5: Labels uploaded → gs://{GCS_BUCKET}/{GCS_RECEIPT_DIR}/labels/receipt_labels.jsonl")

    # Step 6: Import PDFs to Document AI dataset
    print("\nStep 6: Importing to Document AI...")
    op_name = import_to_dataset(docai_client, gcs_uris)

    # Summary
    print("\n" + "=" * 60)
    print("DONE")
    print(f"  PDFs processed:  {len(pdfs)}")
    print(f"  Labeled by Gemini: {len(label_lines)}")
    print(f"  Review file:     {review_path}")
    print(f"  GCS prefix:      gs://{GCS_BUCKET}/{GCS_RECEIPT_DIR}/")
    if op_name:
        print(f"  Import op:       {op_name}")
    print()
    print("Next steps:")
    print("  1. Refresh the Coin Receipts Data Extractor Label & Build page")
    print("  2. Check that documents are appearing in the dataset")
    print("  3. Review gemini_review.json to spot any Gemini errors")
    print("  4. Click 'Fine tune' once all docs are labeled")

if __name__ == "__main__":
    main()
