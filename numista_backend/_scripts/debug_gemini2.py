"""Debug: print raw Gemini response from actual dataset document."""
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
from google.cloud import documentai_v1beta3 as documentai
import google.auth, json

creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
vertexai.init(project="studio-9101802118-8c9a8", location="us-central1", credentials=creds)
model = GenerativeModel("gemini-2.5-flash")

doc_service = documentai.DocumentServiceClient(
    credentials=creds,
    client_options={"api_endpoint": "us-documentai.googleapis.com"},
)
dataset = "projects/568985927038/locations/us/processors/261d6897c84ca28b/dataset"
doc_id = "c90443241b394dc6"

doc_text = doc_service.get_document(request=documentai.GetDocumentRequest(
    dataset=dataset,
    document_id=documentai.DocumentId(
        unmanaged_doc_id=documentai.DocumentId.UnmanagedDocumentId(doc_id=doc_id)),
    read_mask="text",
)).document.text

print(f"Text length: {len(doc_text)}")
print("First 200 chars:", repr(doc_text[:200]))
print("Chars ~char 700-800:", repr(doc_text[700:800]))
print()

EXTRACTION_PROMPT = (
    "You are analyzing a Littleton Coin Company checklist.\n"
    "Extract series_name and all coin entries.\n"
    "For each row: coin_subject = year/descriptor text, is_owned = true if circle is filled, false if empty.\n"
    "Return ONLY valid JSON:\n"
    '{"series_name": "string", "entries": [{"coin_subject": "string", "is_owned": boolean}]}\n\n'
    "=== DOCUMENT TEXT (OCR extracted) ===\n"
)
prompt = EXTRACTION_PROMPT + doc_text[:12000]

response = model.generate_content(
    [Part.from_text(prompt)],
    generation_config=GenerationConfig(
        response_mime_type="application/json", temperature=0.0, max_output_tokens=8192),
)
raw = response.text or ""
print("Raw response length:", len(raw))
print("Around char 730-800 of response:", repr(raw[730:820]))
print()

# Try to parse
try:
    result = json.loads(raw)
    entries = result.get("entries", [])
    print(f"SUCCESS: {len(entries)} entries")
    for e in entries[:5]:
        print(f"  {e}")
except json.JSONDecodeError as exc:
    print(f"Parse error at char {exc.pos}: {exc.msg}")
    print("Context:", repr(raw[max(0,exc.pos-50):exc.pos+50]))
