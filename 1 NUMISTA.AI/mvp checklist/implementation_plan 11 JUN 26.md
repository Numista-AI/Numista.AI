# Numista.AI Stabilization Plan — Updated

## Summary

Goal: Stabilize https://numista-vault.web.app.

| Item | Status |
|------|--------|
| ✅ Gray screen fix deployed | Confirmed live (10:22 AM build) |
| ✅ Backend health check | `GET /` → `{status: ok, service: Numista.AI Backend}` |
| ✅ Review Hub code | All 4 operations implemented and correct |
| ✅ Bulk Upload code | Correct multipart upload to `/api/process_invoice` |
| ✅ Morgan AI Chat code | Correct Firestore session + `deep_dive` endpoint |
| 🚨 **CRITICAL: vertexai SDK deprecated** | Shuts down **June 24, 2026 — 13 days away** |

---

## 🚨 CRITICAL: vertexai SDK Shutdown

The backend `main.py` uses `vertexai.generative_models` throughout. The SDK will be **forcibly shut down on June 24, 2026** — breaking every AI endpoint.

This is the most urgent issue. **The scan_service already migrated** to `google-genai` SDK (v3.1 released April 2026), but the main backend has not.

> [!CAUTION]
> If not migrated, ALL AI features will fail on June 24, 2026:
> - ❌ Invoice / PDF scan (Bulk Upload flow)
> - ❌ Binder photo scan (Single Invoice Scan)
> - ❌ Morgan AI Chat (`/api/deep_dive`)
> - ❌ Spreadsheet AI column mapping (`/api/import_spreadsheet`)
> - ❌ Coin checklist analysis (`/api/analyze_checklist`)

---

## API Change Summary (vertexai → google-genai)

The `scan_service/main.py` shows the exact migration pattern:

```python
# OLD (vertexai SDK — shutting down Jun 24, 2026)
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-flash")
response = model.generate_content([...], generation_config=GenerationConfig(...))
text = response.text

# NEW (google-genai SDK — current)
from google import genai
from google.genai import types
client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[types.Part.from_text("..."), types.Part.from_bytes(data=..., mime_type=...)],
    config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=65536),
)
text = response.candidates[0].content.parts[0].text
# or text = response.text
```

Key differences:
- `vertexai.init()` → `client = genai.Client(vertexai=True, project=..., location="global")`
- `GenerativeModel("gemini-2.5-flash")` → no model object; model is specified per call
- `Part.from_data(data=bytes, mime_type=...)` → `types.Part.from_bytes(data=bytes, mime_type=...)`
- `Part.from_text("...")` → `types.Part.from_text(text="...")`
- `GenerationConfig(...)` → `types.GenerateContentConfig(...)`
- `response.text` → `response.text` (same) or `response.candidates[0].content.parts[0].text`
- `response_mime_type` → still supported in `GenerateContentConfig`

---

## Proposed Changes

### Backend: `main.py`

> [!IMPORTANT]
> This is a significant migration but the pattern is consistent throughout. The code is structured around `model.generate_content()` calls which all need to change to `client.models.generate_content()`.

#### [MODIFY] [main.py](file:///C:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py)

Changes in sections:
1. **Lines 19-88**: Replace `import vertexai` / `from vertexai.generative_models import ...` with `from google import genai` / `from google.genai import types`, replace model init with `client = genai.Client(vertexai=True, ...)`
2. **`/api/import_spreadsheet` ~L450**: Update `Part.from_text()` → `types.Part.from_text(text=...)` and `model.generate_content()` → `client.models.generate_content(model=..., ...)`
3. **`/api/process_invoice` ~L700**: Same Part/generate_content updates
4. **`/api/deep_dive` ~L1850**: Same updates
5. **`/api/analyze_binder_scan` line 2702**: Remove inline `from vertexai.generative_models import Part, GenerationConfig as GC`, update to `types.Part`
6. **`/api/analyze_checklist` ~L3100**: Same updates

#### [MODIFY] [requirements.txt](file:///C:/Users/ericd/Documents/MyVertexProject/numista_backend/requirements.txt)

Add `google-genai>=1.16.0` (current is 1.16). Keep `google-cloud-aiplatform` for other uses (Discovery Engine, etc.) but can pin it lower.

### Backend Deploy

After changing `main.py` + `requirements.txt`:
```bash
gcloud run deploy numista-backend \
  --source . \
  --region us-central1 \
  --project studio-9101802118-8c9a8
```

---

## Other Issues Found (Medium Priority)

### MIME Type in Bulk Upload (Flutter)
- **File**: `add_coins_hub.dart` line 150
- **Bug**: Hardcodes `contentType: MediaType('application', 'pdf')` for ALL file types (including Excel/CSV)
- **Impact**: Low — backend uses filename extension, not MIME type, for parsing
- **Fix**: Use `_mimeTypeFromExtension(file.name)` helper (cosmetic but correct)

### Gemini Model Deprecation Note
The `scan_service/main.py` uses `gemini-3-flash-preview` on `location="global"`. When we migrate `main.py`, we should also confirm that `gemini-2.5-flash` and `gemini-2.5-pro` are still available on `us-central1` or switch to `global`.

---

## Verification Plan

### After SDK Migration

1. Deploy to Cloud Run
2. `POST /api/process_invoice` with a test PDF → expect `{extracted_items: N, ...}`
3. `POST /api/deep_dive` with `{user_email: ..., query: "what is my rarest coin?"}` → expect Morgan response
4. `POST /api/analyze_binder_scan` with test image → expect coin slots JSON
5. Open https://numista-vault.web.app and run the full flows manually

### Manual End-to-End Tests

| Flow | Expected |
|------|----------|
| Login → Dashboard | No gray screen ✅ |
| Add Coins → Bulk Upload → PDF → Submit | Success dialog → Review Hub |
| Review Hub → Select Item → Commit | Item moves to My Collection |
| Morgan AI Chat → "What coins do I have?" | Morgan responds with context |

---

## Approval Required

> [!IMPORTANT]
> The backend SDK migration (`vertexai` → `google-genai`) in `main.py` is a broad change touching ~8 call sites. I recommend proceeding since the deadline is 13 days away. Approve to begin the migration.
