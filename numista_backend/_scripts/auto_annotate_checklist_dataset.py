# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os, sys, json, time, argparse, re
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types as genai_types
from google.cloud import documentai_v1beta3 as documentai
from google.cloud import storage as gcs
import google.auth

GCP_PROJECT_NUMBER = "568985927038"
GCP_PROJECT_ID     = "studio-9101802118-8c9a8"
LOCATION           = "us"
PROCESSOR_ID       = "261d6897c84ca28b"
VERTEX_LOCATION    = "us-central1"
GEMINI_MODEL       = "gemini-3.5-flash"
REQUESTS_PER_MIN   = 30
SLEEP_BETWEEN_DOCS = 60.0 / REQUESTS_PER_MIN
ANNOTATION_BUCKET  = "numista-training-docs"
ANNOTATION_PREFIX  = "auto_annotations/"
PROGRESS_FILE      = Path(__file__).parent / "annotation_progress.json"
DATASET_PATH = (
    f"projects/{GCP_PROJECT_NUMBER}/locations/{LOCATION}"
    f"/processors/{PROCESSOR_ID}/dataset"
)
# DocumentLabelingState values confirmed live 2026-04-19:
#   1 = DOCUMENT_LABELED      (20 docs  - protect these, manually reviewed)
#   2 = DOCUMENT_UNLABELED    (0 docs)
#   3 = DOCUMENT_AUTO_LABELED (630 docs - bad auto-labels, replace with Gemini)
STATE_LABELED      = 1
STATE_UNLABELED    = 2
STATE_AUTO_LABELED = 3

EXTRACTION_PROMPT = (
    "You are analyzing a Littleton Coin Company printed checklist PDF.\n"
    "Extract EVERY coin entry precisely.\n\n"
    "SERIES NAME: Read the document header. Extract the coin series name exactly.\n"
    'Examples: "Liberty Head Nickels", "Barber Half Dollars 1892-1915"\n\n'
    "COIN ENTRIES: For EACH row extract:\n"
    "  coin_subject: the text label (e.g. \"1907\", \"1912-D\", \"1883 Without Cents\"). Copy EXACTLY.\n"
    "  is_owned: FILLED/DARKENED circle = true. EMPTY circle = false. Unclear = false.\n\n"
    "Return ONLY valid JSON, no markdown fences:\n"
    '{\n  "series_name": "string",\n  "entries": [{"coin_subject": "string", "is_owned": boolean}]\n}\n\n'
    "Rules: Include ALL rows. Preserve exact text. Multiple mint columns = separate rows per entry.\n"
    'If series name unreadable use "". If subject unreadable use "Unknown".'
)


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"annotated": [], "failed": [], "skipped": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def find_text_anchor(doc_text, search_text, start_from=0):
    idx = doc_text.find(search_text, start_from)
    if idx != -1:
        return idx, min(idx + len(search_text), len(doc_text))
    idx = doc_text.lower().find(search_text.lower(), start_from)
    if idx != -1:
        return idx, min(idx + len(search_text), len(doc_text))
    m = re.match(r"(\d{4})", search_text.strip())
    if m:
        idx = doc_text.find(m.group(1), start_from)
        if idx != -1:
            return idx, min(idx + 4, len(doc_text))
    return -1, -1

def build_entity(type_, mention_text, start_idx, end_idx, properties=None, boolean_value=None):
    kwargs = {
        "type_": type_, "mention_text": mention_text[:(end_idx-start_idx)] if start_idx>=0 and mention_text else mention_text, "confidence": 1.0
    }
    if start_idx >= 0 and end_idx > start_idx:
        kwargs["text_anchor"] = documentai.Document.TextAnchor(
            text_segments=[documentai.Document.TextAnchor.TextSegment(
                start_index=start_idx, end_index=end_idx)]
        )
    entity = documentai.Document.Entity(**kwargs)
    if properties:
        entity.properties.extend(properties)
    if boolean_value is not None:
        entity.normalized_value = documentai.Document.Entity.NormalizedValue(
            boolean_value=boolean_value)
    return entity


def gemini_extract(client, model_name, pdf_bytes):
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                genai_types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                genai_types.Part.from_text(EXTRACTION_PROMPT)
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
                max_output_tokens=8192
            ),
        )
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"    [Gemini] JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"    [Gemini] Error: {e}")
        return None


def _repair_truncated_json(raw: str) -> dict:
    """
    Attempts to repair a truncated JSON response from Gemini.
    Gemini sometimes cuts off mid-entry when token limits are hit.
    Strategy: find the last complete {"coin_subject": ..., "is_owned": ...} entry
    and close the JSON array and object properly.
    Returns a repaired dict or None if can't be salvaged.
    """
    # Find the last complete entry by scanning for the last }  in the entries array
    # A complete entry ends with: "is_owned": true} or "is_owned": false}
    last_complete = max(
        raw.rfind('"is_owned": true}'),
        raw.rfind('"is_owned": false}'),
    )
    if last_complete == -1:
        return None
    end_pos = last_complete + len('"is_owned": true}' if '"is_owned": true}' in raw[last_complete:last_complete+20] else '"is_owned": false}')
    truncated = raw[:end_pos] + "\n  ]\n}"
    try:
        return json.loads(truncated)
    except json.JSONDecodeError:
        return None


def gemini_extract_from_text(client, model_name, doc_text):
    """
    Sends the OCR-extracted text to Gemini for entity extraction.
    Used when raw PDF bytes are not available in the Document AI dataset
    (training docs stored without content bytes).
    Returns {series_name, entries} dict or None.
    """
    # Sanitize OCR text: Littleton checklist OCR contains non-ASCII characters
    # (Greek Omicron U+039F as empty circles, copyright ©, Japanese katakana, etc.)
    # that cause Gemini to truncate its JSON response mid-output.
    # Strategy: replace specific circle chars with ASCII equivalents, then remove
    # all remaining non-ASCII characters to ensure clean JSON output.
    clean_text = doc_text
    # Circle characters: empty -> 'o', filled -> 'x'
    for char in "\u039f\u25cb\u25ef\u2022\u2218\u00b0":   # Greek O, circles, bullet, ring, degree
        clean_text = clean_text.replace(char, "o")
    for char in "\u25cf\u2715\u00d7\u2022\u2713\u2714":   # Black circle, X marks, checkmarks
        clean_text = clean_text.replace(char, "x")
    # Remove all remaining non-ASCII characters (OCR noise)
    clean_text = clean_text.encode("ascii", errors="ignore").decode("ascii")

    prompt = (
        EXTRACTION_PROMPT
        + "\n\n=== DOCUMENT TEXT (OCR extracted) ===\n"
        + clean_text[:14000]  # Generous limit; checklists are ~4k chars
    )
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[genai_types.Part.from_text(prompt)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
                max_output_tokens=16384
            ),
        )
        raw = response.text or ""
        # Strip markdown fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Attempt to repair truncated JSON by trimming to last complete entry
            repaired = _repair_truncated_json(raw)
            if repaired:
                return repaired
            raise  # Re-raise to hit the outer except
    except json.JSONDecodeError as e:
        print(f"    [Gemini] JSON parse error (JSON mode): {e}")
        # Retry without response_mime_type constraint
        try:
            response2 = client.models.generate_content(
                model=model_name,
                contents=[genai_types.Part.from_text(prompt)],
                config=genai_types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=16384
                ),
            )
            raw2 = response2.text or ""
            raw2 = raw2.strip()
            if raw2.startswith("```"):
                raw2 = raw2.split("\n", 1)[-1]
                raw2 = raw2.rsplit("```", 1)[0]
            try:
                return json.loads(raw2)
            except json.JSONDecodeError:
                repaired2 = _repair_truncated_json(raw2)
                if repaired2:
                    return repaired2
                raise
        except Exception as e2:
            print(f"    [Gemini] Retry also failed: {e2}")
            return None
    except Exception as e:
        print(f"    [Gemini] Error: {e}")
        return None


def build_document_entities(gemini_result, doc_text):
    entities = []
    cursor = 0
    series_name = gemini_result.get("series_name", "").strip()
    if series_name:
        s, e = find_text_anchor(doc_text, series_name)
        entities.append(build_entity("series_name", series_name, s, e))
    for entry in gemini_result.get("entries", []):
        subject  = str(entry.get("coin_subject", "")).strip()
        is_owned = bool(entry.get("is_owned", False))
        if not subject:
            continue
        ss, se = find_text_anchor(doc_text, subject, start_from=cursor)
        if ss > 0 and se > ss:
            cursor = se
        subj_e  = build_entity("coin_subject", subject, ss, se)
        owned_e = build_entity("is_owned", "filled" if is_owned else "empty",
                               ss, ss + 1, boolean_value=is_owned)
        entities.append(build_entity("coin_entry", subject, ss, se,
                                     properties=[subj_e, owned_e]))
    return entities


def upload_to_gcs(gcs_client, annotated_doc, doc_id):
    doc_json = documentai.Document.to_json(annotated_doc)
    gcs_path = f"{ANNOTATION_PREFIX}{doc_id}.json"
    gcs_client.bucket(ANNOTATION_BUCKET).blob(gcs_path).upload_from_string(
        doc_json, content_type="application/json")
    return f"gs://{ANNOTATION_BUCKET}/{gcs_path}"


def make_doc_id_request(doc_id, mask):
    return documentai.GetDocumentRequest(
        dataset=DATASET_PATH,
        document_id=documentai.DocumentId(
            unmanaged_doc_id=documentai.DocumentId.UnmanagedDocumentId(doc_id=doc_id)),
        read_mask=mask,
    )


def main():
    parser = argparse.ArgumentParser(description="Gemini-powered Document AI auto-annotator")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview Gemini output without writing to Document AI")
    parser.add_argument("--limit",   type=int, default=None)
    parser.add_argument("--start",   type=int, default=0)
    parser.add_argument("--model",   type=str, default=GEMINI_MODEL)
    args = parser.parse_args()

    print("=" * 65)
    print("  Coin Checklist Auto-Annotator - Schema v4")
    print(f"  Processor : {PROCESSOR_ID}")
    print(f"  Gemini    : {args.model}")
    print(f"  Dry run   : {args.dry_run}")
    print("=" * 65)

    genai_client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=VERTEX_LOCATION)
    doc_service  = documentai.DocumentServiceClient(
        credentials=credentials,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"})
    gcs_client = gcs.Client(credentials=credentials, project=GCP_PROJECT_ID)
    print("[Init] Clients ready.\n")

    progress     = load_progress()
    already_done = set(progress.get("annotated", []))
    print(f"[Progress] {len(already_done)} docs done from previous runs.")

    # list_documents does not support server-side state filtering (QUERY_BUILDER_INVALID_ARGUMENT)
    # Fetch all and filter in Python using meta.labeling_state (int).
    print("[Dataset] Fetching document list...")
    docs_to_annotate = []
    all_count = labeled_count = 0
    try:
        pager = doc_service.list_documents(
            request=documentai.ListDocumentsRequest(dataset=DATASET_PATH, page_size=500))
        for page in pager.pages:
            for meta in page.document_metadata:
                all_count += 1
                state = int(meta.labeling_state)
                if state == STATE_LABELED:
                    labeled_count += 1
                    continue
                try:
                    doc_id = meta.document_id.unmanaged_doc_id.doc_id
                except Exception:
                    continue
                if not doc_id or doc_id in already_done:
                    continue
                docs_to_annotate.append((doc_id, meta.display_name or doc_id))
    except Exception as e:
        print(f"[Dataset] ERROR: {e}")
        sys.exit(1)

    total_target = len(docs_to_annotate)
    print(f"[Dataset] {all_count} total | {labeled_count} manually labeled (protected)"
          f" | {total_target} to re-annotate.\n")
    if total_target == 0:
        print("Nothing to do.")
        return

    batch = docs_to_annotate[args.start:]
    if args.limit:
        batch = batch[:args.limit]
    print(f"[Run] Processing {len(batch)} documents.\n")

    success_count = fail_count = 0

    for idx, (doc_id, display_name) in enumerate(batch, 1):
        print(f"[{idx}/{len(batch)}] {display_name}  ({doc_id})")
        try:
            doc_text = doc_service.get_document(
                request=make_doc_id_request(doc_id, "text")).document.text or ""
            if not doc_text:
                print("    [Skip] No OCR text.")
                progress["skipped"].append(doc_id); save_progress(progress)
                time.sleep(SLEEP_BETWEEN_DOCS); continue
            print(f"    Text: {len(doc_text)} chars")

            # Training docs have no raw PDF bytes stored in the dataset.
            # Use OCR text (already fetched) directly with Gemini.
            print("    [Gemini] Extracting from OCR text...")
            gemini_result = gemini_extract_from_text(genai_client, args.model, doc_text)
            if not gemini_result:
                print("    [Fail] No result from Gemini.")
                progress["failed"].append(doc_id); save_progress(progress)
                fail_count += 1; time.sleep(SLEEP_BETWEEN_DOCS); continue

            series_name = gemini_result.get("series_name", "")
            entries     = gemini_result.get("entries", [])
            owned_count = sum(1 for e in entries if e.get("is_owned"))
            print(f"    Series  : {series_name or '(not detected)'}")
            print(f"    Entries : {len(entries)} rows | {owned_count} owned")

            if not entries:
                print("    [Skip] 0 entries found.")
                progress["skipped"].append(doc_id); save_progress(progress)
                time.sleep(SLEEP_BETWEEN_DOCS); continue

            entities      = build_document_entities(gemini_result, doc_text)
            annotated_doc = documentai.Document(text=doc_text, entities=entities)

            if args.dry_run:
                print("    [Dry Run] Sample entries:")
                for entry in entries[:5]:
                    mark = "OWNED" if entry.get("is_owned") else "empty"
                    print(f"      {mark}  {entry.get('coin_subject', '?')}")
                if len(entries) > 5:
                    print(f"      ... and {len(entries) - 5} more")
                progress["annotated"].append(doc_id); save_progress(progress)
                success_count += 1; time.sleep(SLEEP_BETWEEN_DOCS); continue

            print("    [GCS] Uploading annotated JSON...")
            gcs_uri = upload_to_gcs(gcs_client, annotated_doc, doc_id)
            print(f"    [GCS] {gcs_uri}")

            print("    [DocAI] Importing...")
            import_op = doc_service.import_documents(
                request=documentai.ImportDocumentsRequest(
                    dataset=DATASET_PATH,
                    batch_documents_import_configs=[
                        documentai.ImportDocumentsRequest.BatchDocumentsImportConfig(
                            dataset_split=documentai.DatasetSplitType.DATASET_SPLIT_TRAIN,
                            batch_input_config=documentai.BatchDocumentsInputConfig(
                                gcs_documents=documentai.GcsDocuments(documents=[
                                    documentai.GcsDocument(
                                        gcs_uri=gcs_uri, mime_type="application/json")
                                ])
                            ),
                        )
                    ],
                )
            )
            import_op.result(timeout=120)
            print("    [OK] Import complete.")
            progress["annotated"].append(doc_id); save_progress(progress)
            success_count += 1

        except Exception as e:
            print(f"    [Error] {type(e).__name__}: {e}")
            progress["failed"].append(doc_id); save_progress(progress)
            fail_count += 1

        time.sleep(SLEEP_BETWEEN_DOCS)

    print("\n" + "=" * 65)
    print(f"  Annotated : {success_count}")
    print(f"  Failed    : {fail_count}")
    print(f"  Total done: {len(progress['annotated'])} / {total_target + len(already_done)}")
    if args.dry_run:
        print("  (Dry run - nothing written to Document AI or GCS)")
    print("=" * 65)
    if fail_count > 0:
        print(f"\n[Tip] Re-run to retry failures. Progress saved to: {PROGRESS_FILE}")
    if not args.dry_run and success_count > 0:
        print("\n[Next] Spot-check docs in Document AI console, then trigger")
        print("       'Create Version -> littleton-v2' to retrain the model.")


if __name__ == "__main__":
    main()
