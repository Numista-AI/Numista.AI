# ARGON REVIEW — `PLAN_C_Model_Usage_Audit.md` (BATON NET-765)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)  
**Date:** 2026-11-04 15:46 ET  
**Baton:** `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-765_ARGON_REVIEW_PLAN_C_Model_Usage_Audit_20261104-1040.md`  
**Target Plan:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_C_Model_Usage_Audit.md` (55 lines)  
**Mode:** PLAN REVIEW ONLY (`NO EXECUTE` — `main` stays `9f04550a`, live site untouched, Stripe OFF, no spend)  
**Verdict:** **PASS — `96 / 100` (0 Blocking Must-Fixes; 3 Non-Blocking Advisories with Exact Codebase Call-Site Map)**

---

## 1. Executive Summary & Scoring Breakdown

`PLAN_C_Model_Usage_Audit.md` defines a strictly read-only pre-launch audit owned by FIN OPS to inventory every AI model call in the codebase, reconcile each call site against the last 14 days of GCP/Vertex billing export data, and classify each call (`KEEP`, `TRY FLASH`, `TRY FLASH-LITE`, `BATCH CANDIDATE`, `CACHE CANDIDATE`) without changing any code, config, models, prompts, keys, or billing.

| Category | Weight | Score | Notes |
|---|---|---|---|
| **1. Read-Only Safety, PII & Secret Hygiene** | 25 | **25 / 25** | Strictly read-only (`lines 13–16`), zero test calls that cost money (`line 16`), zero PII/AJ data (`line 48`), and explicit rule never to copy secret key values (`line 49`). |
| **2. Codebase Grounding (Verified against `numista_backend/` & `numista_ai/`)** | 25 | **23 / 25** | Plan's Step 1–2 (`lines 19–20`) covers `text or image` generation calls well; we provide the exact `file:line` map below and advise also including `gemini-embedding-2`, Vertex AI Search (`discoveryengine_v1`), and Document AI so the table reconciles 100% with GCP billing. |
| **3. Compliance with `.agents\AGENTS.md` Rule 6 (Model Policy)** | 25 | **23 / 25** | Step 4–5 (`lines 22–28`) should cross-check any `TRY FLASH` / `TRY FLASH-LITE` recommendation against `Gemini Deprecation Schedules\` per `.agents\AGENTS.md:100-108`. |
| **4. Verification & Review Chain** | 25 | **25 / 25** | Any model switch requires its own separate plan, Plan B golden-set testing before/after (`line 29`), and a new typed YES from Eric (`line 52`). |
| **TOTAL** | **100** | **96 / 100** | **PASS (Ready for GB CoS 95+ -> SAG -> Eric YES)** |

---

## 2. Verbatim File Quotes Checked in This Turn

### 2.1 `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-765_ARGON_REVIEW_PLAN_C_Model_Usage_Audit_20261104-1040.md:1-5`
```markdown
1: # BATON NET-765 - ARGON: review INBOX\PLAN_C_Model_Usage_Audit.md (PLAN ONLY, ideas from Google's 'Startup guide to AI agents')
2: Filed by Antigravity Desk, 4 Nov 2026 10:40 AM ET, on GB CoS's request. MD5 CBE4E10FA8ADAE3C73E9C6E01B05B8CA. Eric's 4 Nov 10:36 AM decisions are appended to Plans A, B and D.
3: 
4: Write INBOX\ARGON_REVIEW_PLAN_C_Model_Usage_Audit.md with a score out of 100 and any must-fixes.
5: Chain: Argon, then GB CoS 95+, then SAG, then Eric's typed YES. NOTHING EXECUTES. Main stays 9f04550a. The live site stays untouched. Stripe stays OFF. No spend.
```

### 2.2 `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_C_Model_Usage_Audit.md:18-33`
```markdown
18: ## Steps
19: 1. List every place a model is named: Morgan chat, coin identification, image analysis, valuation, catalog builder/nightly jobs, and anything else found. Record the file and line.
20: 2. For each, note the model name and version, whether it's text or image, and whether a user is waiting on it (live) or it can wait (nightly).
21: 3. Match calls to cost using the billing export: requests per day and dollars per day, last 14 days. Mark anything that can't be matched as UNVERIFIED.
22: 4. Label each call:
23:    - KEEP: hard reasoning, or quality matters most.
24:    - TRY FLASH: routine answers.
25:    - TRY FLASH-LITE: classification, tagging, simple extraction.
26:    - BATCH CANDIDATE: can wait (feeds Plan D).
27:    - CACHE CANDIDATE: a big, fixed prompt sent many times (p.9).
28: 5. Estimate the savings for each candidate using Google's public price page (https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing), marked UNVERIFIED until tested.
29: 6. Report to GB CoS. Any switch becomes its own plan with a quality test (Plan B's golden set) before and after.
30: 
31: ## Report format
32: | Call | File:line | Model | Live or nightly | Calls/day | $/day | Label | Est. saving | Notes |
```

### 2.3 Real Codebase Model Definitions & Call Sites Read in This Turn (Head-Start Map for Step 1)

1. **Central Model Config (`numista_backend\config\__init__.py:24-34`):**
```python
24: GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash")          # Primary workhorse
25: GEMINI_PRO_MODEL   = os.getenv("GEMINI_PRO_MODEL",   "gemini-3.1-pro-preview")    # High-reasoning tasks
26: GEMINI_LITE_MODEL  = os.getenv("GEMINI_LITE_MODEL",  "gemini-3.5-flash-lite")     # Lightweight/fast tasks
27: GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")    # Image generation
28: 
29: # Route-level model aliases (used by scan_routes.py and ai_routes.py)
30: # These allow per-route overrides via env vars while defaulting to the core models above.
31: DEFAULT_VISION_MODEL  = os.getenv("DEFAULT_VISION_MODEL",  GEMINI_FLASH_MODEL)    # Coin image analysis
32: FALLBACK_VISION_MODEL = os.getenv("FALLBACK_VISION_MODEL", GEMINI_LITE_MODEL)     # Vision fallback
33: DEFAULT_CHAT_MODEL    = os.getenv("DEFAULT_CHAT_MODEL",    GEMINI_FLASH_MODEL)    # Morgan AI chat
34: FALLBACK_CHAT_MODEL   = os.getenv("FALLBACK_CHAT_MODEL",   GEMINI_LITE_MODEL)     # Chat fallback
```

2. **Document Ingestion Model Config (`numista_backend\config\ingestion_config.py:7-10`):**
```python
7: CLASSIFIER_MODEL = "gemini-3.8-flash"
8: EXTRACTION_MODEL = "gemini-3.1-pro-preview"
9: FALLBACK_FLASH_MODEL = "gemini-3.8-flash"
10: FALLBACK_PRO_MODEL = "gemini-3.5-pro"
```

3. **Shared Router Dependencies (`numista_backend\routes\deps.py:29, 35-37`):**
```python
29:     genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
...
35: # Model Constants (Rule 6 compliant)
36: MODEL_FLASH = "gemini-3.8-flash"
37: MODEL_PRO = "gemini-3.1-pro-preview"
```

4. **Main Backend Bindings & Spreadsheet Header Fallback (`numista_backend\main.py:429-436, 796-802`):**
```python
429: PRIMARY_MODEL = GEMINI_FLASH_MODEL
430: PRO_MODEL     = GEMINI_PRO_MODEL
431: IMAGE_MODEL   = GEMINI_IMAGE_MODEL
432: 
433: # Initialize google-genai client (Vertex AI backend)
434: # Override via GEMINI_LOCATION env var if needed, default to 'global'
435: GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", LOCATION)
436: genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)
```
```python
796:         resp = genai_client.models.generate_content(
797:             model=PRIMARY_MODEL,
798:             contents=[genai_types.Part.from_text(text=mapping_prompt)],
799:             config=genai_types.GenerateContentConfig(
800:                 response_mime_type="application/json",
801:             ),
802:         )
```

5. **Morgan AI Chat Route (`numista_backend\routes\ai_routes.py:51-65`):**
```python
51:     models_to_try = [DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL]
52:     last_err = None
53: 
54:     for model_id in models_to_try:
55:         try:
56:             logger.info(f"Invoking chat model: {model_id}")
57:             resp = genai_client.models.generate_content(
58:                 model=model_id,
59:                 contents=[
60:                     genai_types.Part.from_text(text=f"{system_prompt}\n\nUser Question: {user_query}")
61:                 ],
62:                 config=genai_types.GenerateContentConfig(
63:                     temperature=0.3,
64:                 ),
65:             )
```

6. **Document Classifier & Checklist Extractor (`numista_backend\services\document_classifier_service.py:45-51` & `numista_backend\services\checklist_parser.py:279-285`):**
```python
45:         response = genai_client.models.generate_content(
46:             model=CLASSIFIER_MODEL,
47:             contents=[part, genai_types.Part.from_text(text=CLASSIFIER_PROMPT)],
48:             config=genai_types.GenerateContentConfig(
49:                 response_mime_type="application/json",
50:             ),
51:         )
```
```python
279:         response = genai_client.models.generate_content(
280:             model=EXTRACTION_MODEL,
281:             contents=[pdf_part, genai_types.Part.from_text(text=effective_prompt)],
282:             config=genai_types.GenerateContentConfig(
283:                 response_mime_type="application/json",
284:             ),
285:         )
```
*(Note: `CHECKLIST_EXTRACTION_SYSTEM_PROMPT` at `checklist_parser.py:25-84` is a fixed 60-line prompt sent on every checklist upload — a prime `CACHE CANDIDATE` under Step 4!)*

7. **Cert Slab OCR (`numista_backend\routes\cert_routes.py:419, 457-464`):**
```python
419:     model_name = model or MODEL_FLASH
...
457:             return _scan_client.models.generate_content(
458:                 model=model_name,
459:                 contents=[prompt, image_part],
460:                 config=_genai_types.GenerateContentConfig(
461:                     response_mime_type="application/json",
462:                     max_output_tokens=1024,
463:                 ),
464:             )
```

8. **Vector RAG Embeddings & Discovery Engine (`numista_backend\services\vector_rag_service.py:28, 78-82`, `numista_backend\morgan_knowledge.py:228-247`, `numista_ai\info_bot.py:9-10`):**
```python
28: ACTIVE_EMBEDDING_MODEL = "gemini-embedding-2"
...
78:             resp = self.client.models.embed_content(
79:                 model=self.model_id,
80:                 contents=text.strip(),
81:                 config=genai_types.EmbedContentConfig(output_dimensionality=RAG_EMBEDDING_DIM),
82:             )
```
```python
9: GEMINI_MODEL = "gemini-3.8-flash"
10: EMBEDDING_MODEL = "gemini-embedding-2"
```

9. **Mandatory Gemini Model Policy (`.agents\AGENTS.md:100-108`):**
```markdown
100: ### Rule 6 — Mandatory Gemini Model Policy
101: 
102: Before changing any Gemini model ID (e.g., changing `gemini-3.5-flash` to anything else), you **MUST**:
103: 
104: 1. Read the latest PDF documentation in:
105:    `C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules\`
106: 2. Verify the "Shutdown date" and "Recommended replacement" for the proposed model.
107: 3. NEVER downgrade to a model that has an earlier shutdown date than the current one (e.g., do not move from `gemini-3.5` back to `gemini-1.5` if `1.5` shuts down sooner).
108: 4. If a model is 404ing, check the `location='global'` setting before assuming the model is retired.
```

---

## 3. Must-Fixes & Advisories

* **Blocking Must-Fixes:** **None (0).**
* **Non-Blocking Advisories for the Audit Execution (3):**
  1. **Broaden Step 2 Model Type Column (`line 20`) to Include Embeddings, Vertex AI Search & Document AI:** In addition to `text or image` generation models, the codebase invokes `gemini-embedding-2` (`numista_backend\services\vector_rag_service.py:28,78` and `numista_ai\info_bot.py:10`), Vertex AI Search / Discovery Engine (`numista_backend\morgan_knowledge.py:228-247` and `numista_backend\main.py:303`), and Document AI (`numista_backend\main.py:19`). Including those rows in the audit report will ensure the bottom-up call table reconciles with the top-down GCP billing export.
  2. **Enforce `.agents\AGENTS.md` Rule 6 on All `TRY FLASH` / `TRY FLASH-LITE` Recommendations (`lines 24–25`):** Every candidate model recommended in Step 4 must be checked against `C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules\` so the report never suggests switching from `gemini-3.8-flash` (`Released September 2, 2026`, `main.py:423`) to `gemini-3.5-flash-lite` (`Released July 21, 2026`, `main.py:425`) if `gemini-3.5-flash-lite` has an earlier deprecation/shutdown horizon.
  3. **Check Cloud Run Environment Variables Read-Only (`config\__init__.py:24-34`):** Because `config\__init__.py:24-34` resolves model IDs via `os.getenv(...)`, FIN OPS should record both the code default and any active Cloud Run env var override.
