# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Debug: print the raw Gemini response bytes to find the truncation character."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from google import genai
from google.genai import types as genai_types
from google.cloud import documentai_v1beta3 as documentai
import google.auth, json

creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
client = genai.Client(vertexai=True, project="studio-9101802118-8c9a8", location="us-central1", credentials=creds)

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

# Sanitize
clean_text = doc_text
for char in "\u039f\u25cb\u25ef\u2022\u2218":
    clean_text = clean_text.replace(char, "o")
clean_text = clean_text.replace("\u25cf", "x")
clean_text = clean_text.replace("\u2715", "x")

# Check for remaining non-ASCII
non_ascii = [(i, c, ord(c)) for i, c in enumerate(clean_text) if ord(c) > 127]
print(f"Remaining non-ASCII chars after sanitize: {len(non_ascii)}")
for i, c, code in non_ascii[:20]:
    print(f"  pos {i}: U+{code:04X} = {repr(c)}")

PROMPT = (
    'You are analyzing a Littleton Coin Company checklist.\n'
    'Extract series_name and all coin entries.\n'
    'For each row: coin_subject = year/descriptor text, is_owned = true if circle is filled, false if empty.\n'
    'Return ONLY valid JSON:\n'
    '{"series_name": "string", "entries": [{"coin_subject": "string", "is_owned": boolean}]}\n\n'
    "=== DOCUMENT TEXT (OCR extracted) ===\n"
    + clean_text[:12000]
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=PROMPT,
    config=genai_types.GenerateContentConfig(
        response_mime_type="application/json", temperature=0.0, max_output_tokens=8192),
)
raw = response.text or ""
print(f"\nResponse length: {len(raw)}")

# Find non-ASCII in response
non_ascii_resp = [(i, c, ord(c)) for i, c in enumerate(raw) if ord(c) > 127]
print(f"Non-ASCII in response: {len(non_ascii_resp)}")
for i, c, code in non_ascii_resp[:10]:
    print(f"  pos {i}: U+{code:04X} = {repr(c)}")
    print(f"    context: {repr(raw[max(0,i-30):i+30])}")

# Show around error position
print(f"\nAround char 700-800 of response:")
print(repr(raw[700:830]))

# Try parse
try:
    result = json.loads(raw)
    entries = result.get("entries", [])
    print(f"\nSUCCESS: {len(entries)} entries, {sum(1 for e in entries if e.get('is_owned'))} owned")
    for e in entries[:5]:
        print(f"  {e}")
except json.JSONDecodeError as exc:
    print(f"\nParse error at char {exc.pos}: {exc.msg}")
    print("Context:", repr(raw[max(0,exc.pos-80):exc.pos+80]))
