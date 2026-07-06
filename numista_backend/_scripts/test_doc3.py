# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os, sys, json
from google import genai
from google.genai import types as genai_types
from google.cloud import documentai_v1beta3 as documentai
import google.auth

GCP_PROJECT_ID = "studio-9101802118-8c9a8"
VERTEX_LOCATION = "us-central1"
PROCESSOR_ID = "261d6897c84ca28b"
DATASET_PATH = f"projects/568985927038/locations/us/processors/{PROCESSOR_ID}/dataset"
DOC_ID = "c90443241b3945d4"
ANNOTATION_BUCKET  = "numista-training-docs"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=VERTEX_LOCATION, credentials=credentials)
doc_service = documentai.DocumentServiceClient(
    credentials=credentials, client_options={"api_endpoint": "us-documentai.googleapis.com"})

doc_text = doc_service.get_document(
    request=documentai.GetDocumentRequest(dataset=DATASET_PATH,
    document_id=documentai.DocumentId(unmanaged_doc_id=documentai.DocumentId.UnmanagedDocumentId(doc_id=DOC_ID)),
    read_mask="text")
).document.text

clean_text = doc_text
for char in "\u039f\u25cb\u25ef\u2022\u2218\u00b0": clean_text = clean_text.replace(char, "o")
for char in "\u25cf\u2715\u00d7\u2022\u2713\u2714": clean_text = clean_text.replace(char, "x")
clean_text = clean_text.encode("ascii", errors="ignore").decode("ascii")

EXTRACTION_PROMPT = "You are analyzing a checklist. Extract series_name and all coin rows.\nReturn ONLY valid JSON: {\"series_name\": \"str\", \"entries\": [{\"coin_subject\": \"str\", \"is_owned\": bool}]}"
prompt = EXTRACTION_PROMPT + "\n\n" + clean_text[:14000]

schema = {
    "type": "OBJECT",
    "properties": {
        "series_name": {"type": "STRING"},
        "entries": {"type": "ARRAY", "items": {
            "type": "OBJECT", "properties": {
                "coin_subject": {"type": "STRING"}, "is_owned": {"type": "BOOLEAN"}
            }
        }}
    }
}

try:
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json", response_schema=schema, temperature=0.0)
    )
    gemini_result = json.loads(response.text)
except Exception as e:
    print("Gemini Fail:", e)
    sys.exit(1)

def find_text_anchor(doc_txt, search_text, start_from=0):
    idx = doc_txt.find(search_text, start_from)
    if idx == -1:
        idx = doc_txt.lower().find(search_text.lower(), start_from)
    if idx != -1:
        start_byte = len(doc_txt[:idx].encode('utf-8'))
        end_byte = start_byte + len(search_text.encode('utf-8'))
        return start_byte, end_byte, idx, idx + len(search_text)
    return -1, -1, -1, -1

def build_entity(type_, mention_text, start_idx, end_idx, properties=None, boolean_value=None):
    kwargs = {"type_": type_, "mention_text": mention_text, "confidence": 1.0}
    if start_idx >= 0 and end_idx > start_idx:
        kwargs["text_anchor"] = documentai.Document.TextAnchor(
            text_segments=[documentai.Document.TextAnchor.TextSegment(start_index=start_idx, end_index=end_idx)])
    entity = documentai.Document.Entity(**kwargs)
    if properties: entity.properties.extend(properties)
    if boolean_value is not None: entity.normalized_value = documentai.Document.Entity.NormalizedValue(boolean_value=boolean_value)
    return entity

entities = []
cursor = 0
s_n = gemini_result.get("series_name", "")
if s_n:
    s_b, e_b, s_c, e_c = find_text_anchor(doc_text, s_n)
    if s_b >= 0: entities.append(build_entity("series_name", doc_text[s_c:e_c], s_b, e_b))
for entry in gemini_result.get("entries", []):
    subj = str(entry.get("coin_subject", "")).strip()
    is_owned = bool(entry.get("is_owned", False))
    if not subj: continue
    ss_b, se_b, ss_c, se_c = find_text_anchor(doc_text, subj, cursor)
    if ss_b > 0: cursor = se_c
    subj_txt = doc_text[ss_c:se_c] if ss_b>=0 else subj
    subj_e = build_entity("coin_subject", subj_txt, ss_b, se_b)
    owned_txt = doc_text[ss_c:ss_c+1] if ss_b>=0 else ("filled" if is_owned else "empty")
    ss1_byte = len(doc_text[:ss_c+1].encode('utf-8')) if ss_b>=0 else -1
    owned_e = build_entity("is_owned", owned_txt, ss_b, ss1_byte, boolean_value=is_owned)
    entities.append(build_entity("coin_entry", subj_txt, ss_b, se_b, properties=[subj_e, owned_e]))

annotated_doc = documentai.Document(text=doc_text, entities=entities)
doc_json = documentai.Document.to_json(annotated_doc)
from google.cloud import storage as gcs
gcs_client = gcs.Client(credentials=credentials, project=GCP_PROJECT_ID)
gcs_path = f"auto_annotations/{DOC_ID}.json"
gcs_client.bucket(ANNOTATION_BUCKET).blob(gcs_path).upload_from_string(doc_json, content_type="application/json")
gcs_uri = f"gs://{ANNOTATION_BUCKET}/{gcs_path}"

import_op = doc_service.import_documents(
    request=documentai.ImportDocumentsRequest(
        dataset=DATASET_PATH,
        batch_documents_import_configs=[documentai.ImportDocumentsRequest.BatchDocumentsImportConfig(
            dataset_split=documentai.DatasetSplitType.DATASET_SPLIT_TRAIN,
            batch_input_config=documentai.BatchDocumentsInputConfig(gcs_documents=documentai.GcsDocuments(documents=[
                documentai.GcsDocument(gcs_uri=gcs_uri, mime_type="application/json")
            ]))
        )]
    )
)
print("Importing to DocAI...")
import_op.result(timeout=120)
print("SUCCESS!")
