# EXECUTE DONE: NET-778 - Plan C Model Usage Audit
To: Antigravity Desk / GB CoS / Eric  
From: AG CoS v4  
Date: 4 Nov 2026 5:00 PM ET  
Status: 100% COMPLETE & FILED (AUDIT + REPORT ONLY)

## 1. Deliverables
- Comprehensive audit report filed at:
  - `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\MODEL_USAGE_AUDIT_REPORT_2026-11-04.md`
  - `BETA TEST\Grok Bot\8 OCT 26\BATONS\MODEL_USAGE_AUDIT_REPORT_2026-11-04.md`
  - `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\MODEL_USAGE_AUDIT_REPORT_2026-11-04.md`

## 2. Key Findings Summary
1. **Total Call Sites:** 36 distinct AI / Gemini / Vertex / Document AI / Discovery Engine call sites across 18 backend & mobile files.
2. **Current Models:**
   - Workhorse: `gemini-3.8-flash` (code default & Cloud Run default).
   - High-Reasoning / Extraction: `gemini-3.1-pro-preview` (`main.py:2282`, `checklist_parser.py:280`).
   - Fast/Lite: `gemini-3.5-flash-lite` (fallback in `ai_routes.py`, `config/__init__.py:26`).
   - Embeddings: `gemini-embedding-2` (1536-dim MRL, `vector_rag_service.py:28`).
   - Managed Enterprise Search: Vertex AI Search (`numista-coin-search`, `coin_search_endpoint.py:16`).
   - Document OCR: Google Cloud Document AI (`main.py:2040`).
3. **Cloud Run Live Environment Check:**
   - Both `numista-backend` and `numista-scan-service` have zero model overrides in Cloud Run env vars; code defaults are active.
4. **AGENTS.md Rule 6 Deprecation Check:**
   - Verified against `Gemini Deprecation Schedules\Gemini deprecations 2 SEPT 2026.pdf`.
   - All proposed and current models have NO shutdown dates announced. PASS.
5. **Top 5 Savings Candidates:**
   - **Rank 1:** Invoice Normalization (`_apply_defaults` in `main.py:2282`) moving from `gemini-3.1-pro-preview` to `gemini-3.8-flash` (~94% cost reduction).
   - **Rank 2:** Morgan AI Chat System Prompt Context Caching (`routes/ai_routes.py:57`) enabling 75% input token discount via Vertex Context Caching.
   - **Rank 3:** Document Type Classifier (`services/document_classifier_service.py:46`) moving from `gemini-3.8-flash` to `gemini-3.5-flash-lite` (~75% cost reduction).
   - **Rank 4:** Littleton SKU & Spreadsheet Header Resolvers (`littleton_sku_helper.py:268`, `main.py:796`, `main.py:12409`) moving to `gemini-3.5-flash-lite` (~75% cost reduction).
   - **Rank 5:** Offline Catalog & Dataset Generation Scripts (`generate_definitive_catalog.py`, `brain_processor.py`, `ingest_banknotes.py`) moving to Vertex AI Batch Prediction API (50% flat discount, feeds Plan D).

## 3. Scope & System Invariance Confirmation
- Zero model switches executed.
- Zero code or config modifications.
- Zero Firestore reads/writes of user records.
- Zero spend.
- `origin/main` remains strictly locked at `9f04550a`. Stripe strictly locked OFF.
- Ready to proceed to queued next task: `BATON_NET-777` (Live Catalog FAILFIX Plan v1).
