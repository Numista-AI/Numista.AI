# MODEL USAGE AUDIT REPORT (Plan C v1.1 / NET-778)
**Date:** 4 November 2026  
**Auditor:** AG CoS v4 (FIN OPS Read-Only Audit)  
**Authority:** Founder Eric's typed YES at 4:32 PM ET on 4 Nov 2026 ("YES, execute Plan C")  
**Scope:** Complete codebase audit of AI, Gemini, Vertex AI, Embedding, Document AI, and Discovery Engine model calls across backend, mobile, and offline jobs.  
**System Integrity Confirmation:** Zero code changes, zero config changes, zero model switches, zero Firestore reads/writes, zero spend. `origin/main` strictly locked at `9f04550a`. Stripe strictly locked OFF.

---

## 1. Executive Summary
- **Total Model Call Sites Identified:** 36 distinct call sites across 18 modules.
- **Active Production Workhorses:**
  - Primary Vision & Workhorse: `gemini-3.8-flash` (code default & Cloud Run default via `config/__init__.py:24`).
  - High Reasoning / Extraction: `gemini-3.1-pro-preview` (`config/__init__.py:25` & `ingestion_config.py:8`).
  - Lightweight / Fast: `gemini-3.5-flash-lite` (`config/__init__.py:26`).
  - Semantic Vector Embeddings: `gemini-embedding-2` (1536-dim MRL, `vector_rag_service.py:28`).
  - Managed Enterprise Search: Vertex AI Search (`numista-coin-search`, `coin_search_endpoint.py:16`).
  - Document OCR: Google Cloud Document AI (`DocumentProcessorServiceClient`, `main.py:2040`).
- **Live Cloud Run Environment State:**
  - Service `numista-backend` and `numista-scan-service` have **NO model environment variable overrides** set. All services cleanly run the centralized code defaults from `config/__init__.py` and `ingestion_config.py`.
- **AGENTS.md Rule 6 Compliance:**
  - Evaluated against the latest official Google deprecation schedule (`Gemini deprecations 2 SEPT 2026.pdf`).
  - All recommended models (`gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-pro-preview`, `gemini-embedding-2`) have **NO shutdown dates announced**.
  - Zero models recommended have earlier shutdown dates than existing ones.
- **Top 5 Optimization Candidates Identified:** Potential savings of **50% to 94%** on targeted high-volume and Pro-tier workloads (detailed in Section 4).

---

## 2. Complete Model Usage Inventory Table

| # | Call Name / Feature | File & Line | Model (Code Default / Cloud Run Env) | Type & Modality | Live or Nightly | Calls/day | $/day | Label | Est. Saving | Notes |
|---|---------------------|-------------|--------------------------------------|-----------------|-----------------|-----------|-------|-------|-------------|-------|
| 1 | Coin Photo ID: Pass 1 Base | [main.py:6197](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L6197), [6323](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L6323) | `gemini-3.8-flash` / default | Vision (Multimodal + Text) | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Primary coin identification pass. Core accuracy driver. |
| 2 | Coin Photo ID: Pass 2 Fine Details | [main.py:6380](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L6380) | `gemini-3.8-flash` / default | Vision (Multimodal + Text) | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | High-zoom crop pass for fine varieties/mint marks. |
| 3 | Morgan AI Chat Turn | [ai_routes.py:57](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/ai_routes.py#L57), [142](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/ai_routes.py#L142) | `gemini-3.8-flash` / default (fallback: `gemini-3.5-flash-lite`) | Text (RAG + Persona) | Live | UNVERIFIED | UNVERIFIED | **CACHE CANDIDATE** / **TRY FLASH-LITE** | ~75% input tokens | Large static persona/rules prompt (~2.5k tokens). Prime target for Gemini Prompt Caching. Routine QA can move to Flash-Lite. |
| 4 | Morgan Numismatic Research Essay | [ai_routes.py:262](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/ai_routes.py#L262) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Deep dive historical synthesis. Quality matters most. |
| 5 | Semantic Vector RAG Retrieval | [vector_rag_service.py:28](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/vector_rag_service.py#L28), [39](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/vector_rag_service.py#L39) | `gemini-embedding-2` / default | Text Embedding (1536-dim) | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Vertex AI global endpoint. Highly efficient ($0.02/1M tokens). |
| 6 | Knowledge Base RAG Migrator | [brain_to_rag_migrator.py:41](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/brain_to_rag_migrator.py#L41), [127](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/brain_to_rag_migrator.py#L127) | `gemini-embedding-2` / default | Text Embedding (1536-dim) | Nightly / Batch | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% on bulk | Feeds Plan D for bulk offline knowledge indexing. |
| 7 | Legacy RAG Info Bot Endpoint | [info_bot.py:9](file:///c:/Users/ericd/Documents/MyVertexProject/numista_ai/info_bot.py#L9), [59](file:///c:/Users/ericd/Documents/MyVertexProject/numista_ai/info_bot.py#L59) | `gemini-3.8-flash` + `gemini-embedding-2` | Text + Embedding | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Simple factoid retrieval query engine. |
| 8 | Document AI Invoice/Receipt Parser | [main.py:2040](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L2040), [4870](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L4870) | Google Document AI Service | OCR / Table Parser | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Managed Google Document AI parser for receipts and invoices. |
| 9 | Invoice Normalization (`_apply_defaults`) | [main.py:2282](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L2282) | `gemini-3.1-pro-preview` (PRO_MODEL) | Text (JSON schema) | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH** | **~94% saving** | Currently calls PRO model! JSON normalization can easily run on `gemini-3.8-flash`. Top candidate. |
| 10 | Invoice Error Recovery Sanitizer | [main.py:2390](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L2390) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | String literal syntax repair on malformed invoice JSON. |
| 11 | Deep Dive Collector Essay | [main.py:3472](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L3472), [3497](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L3497) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Long-form numismatic analytical essays. |
| 12 | Document Type Classifier | [document_classifier_service.py:46](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/document_classifier_service.py#L46) | `gemini-3.8-flash` (CLASSIFIER_MODEL) | Multimodal Image/PDF | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Classifies document type (checklist vs invoice vs slab). Simple categorization task. |
| 13 | Checklist Grid & Handwriting Extraction | [checklist_parser.py:280](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/checklist_parser.py#L280) | `gemini-3.1-pro-preview` (EXTRACTION_MODEL) | Multimodal Image/PDF | Live / Batch | UNVERIFIED | UNVERIFIED | **KEEP** / **CACHE CANDIDATE** | 75% prompt cache | Extreme reasoning required for messy checkboxes across 25+ rows. Large static prompt can be cached. |
| 14 | Checklist Direct Analyzer | [main.py:5125](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L5125) | `gemini-3.8-flash` / default | Multimodal Image/PDF | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | End-to-end single pass checklist parser. |
| 15 | Binder Scan Multipage Vision | [main.py:4541](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L4541) | `gemini-3.8-flash` / default | Multimodal Image | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | 20-pocket coin flip binder page analyzer. |
| 16 | Group Photo Multi-Coin Detector | [main.py:5773](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L5773) | `gemini-3.8-flash` / default | Multimodal Image | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Detects & localizes multiple coins in a single photo. |
| 17 | World & Specialty Item Identifier | [main.py:1365](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L1365), [1384](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L1384) | `gemini-3.8-flash` / default | Multimodal Image + Text | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Broad visual taxonomy across world coins & medals. |
| 18 | Text Valuation Estimator | [main.py:6749](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L6749) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Text-based rough valuation estimate. |
| 19 | General Valuation Estimator | [main.py:6844](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L6844) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | General valuation lookup from metadata. |
| 20 | Spreadsheet Header Fast Mapper | [main.py:796](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L796) | `gemini-3.8-flash` / default | Text | Live / Ingestion | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Maps arbitrary column names to standard coin fields. |
| 21 | Spreadsheet Image Import Processing | [main.py:7972](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L7972), [8116](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8116), [8146](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8146) | `gemini-3.8-flash` / default | Multimodal Image + Text | Batch / Ingestion | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% batch discount | Runs asynchronously with HTTP 202. Excellent for Batch API. |
| 22 | Numismatic Reference Search Expander | [main.py:9816](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L9816) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Query expansion for reference lookup. |
| 23 | Littleton SKU Catalog Resolver | [littleton_sku_helper.py:268](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/numista_backend/littleton_sku_helper.py#L268), [main.py:10008](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L10008) | `gemini-3.8-flash` / default | Text | Live / Batch | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Parses vendor item description into coin specs. |
| 24 | Brain Suggestions Rescorer | [main.py:10568](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L10568) | `gemini-3.8-flash` / default | Text | Nightly / Admin | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% batch discount | Backfill scoring over suggestions. Can wait. |
| 25 | Greysheet Semantic Coin Match & Ranking | [greysheet_service.py:444](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/greysheet_service.py#L444), [635](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/greysheet_service.py#L635) | `gemini-3.8-flash` / default | Text | Live / Scheduled | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Semantic title verification and fuzzy ranking. |
| 26 | eBay EPN Search Normalizer | [main.py:12409](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L12409) | `gemini-3.8-flash` / default | Text | Live | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | Rewrites coin params into eBay query tokens. |
| 27 | Unified Cert Slab Scan OCR/Verification | [cert_routes.py:457](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/cert_routes.py#L457), [548](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/cert_routes.py#L548) | `gemini-3.8-flash` / default | Vision (Multimodal + Text) | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Optical verification of PCGS/NGC slab barcodes & labels. |
| 28 | Admin Feedback Transcript Redactor | [feedback_callable_route.py:282](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/feedback_callable_route.py#L282) | `gemini-3.8-flash` / default | Text | Admin / Background | UNVERIFIED | UNVERIFIED | **TRY FLASH-LITE** | ~75% token cost | PII redaction and feedback categorization. |
| 29 | Estate Appraisal AI Narrative | [estate_report_generator.py:633](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/scan_service/estate_report_generator.py#L633) | `gemini-3.8-flash` / default | Text | Live / On-demand | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Generates formal legal appraisal narratives. |
| 30 | Grading Advisor Wear Assessment | [grading_advisor.py:157](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/numista_scraper/grading_advisor.py#L157), [176](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/numista_scraper/grading_advisor.py#L176) | `gemini-3.8-flash` (fallback: `gemini-3.1-pro-preview`) | Vision (Multimodal + Text) | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Evaluates high-point wear against Sheldon scale. |
| 31 | Variety Detector Service | [variety_detector.py:92](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/variety_detector.py#L92) | `gemini-3.8-flash` / default | Vision (Multimodal + Text) | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Attributions of doubled dies, repunched mint marks. |
| 32 | Definitive Catalog Generator | [generate_definitive_catalog.py:235](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/generate_definitive_catalog.py#L235) | `gemini-3.8-flash` / default | Text | Nightly / Offline | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% batch discount | Bulk catalog generation script. Feeds Plan D. |
| 33 | Definitive Catalog Medal Ingestion | [load_definitive_catalog.py:336](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/load_definitive_catalog.py#L336) | `gemini-3.8-flash` / default | Text | Nightly / Offline | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% batch discount | Offline catalog loading script. |
| 34 | Banknote Catalog Ingestion | [ingest_banknotes.py:169](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/ingest_banknotes.py#L169) | `gemini-3.8-flash` / default | Text | Nightly / Offline | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% batch discount | Bulk banknote catalog ingestion. |
| 35 | Brain Knowledge Base Auto-Processor | [brain_processor.py:286](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/brain_processor.py#L286) | `gemini-3.8-flash` / default | Multimodal + Text | Nightly Daemon | UNVERIFIED | UNVERIFIED | **BATCH CANDIDATE** | 50% batch discount | Background indexing daemon. |
| 36 | Vertex AI Search: Coin Library | [coin_search_endpoint.py:112](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/vertex_search/coin_search_endpoint.py#L112) | Vertex AI Search (`numista-coin-search`) | Managed Search | Live | UNVERIFIED | UNVERIFIED | **KEEP** | $0 | Enterprise Search over official numismatic corpus. |

*Note on Billing Data:* The BigQuery billing export table `studio-9101802118-8c9a8.billing_export.gcp_billing_export_v1_010E3C_D8346A_91A35E` exists, but direct queries require `bigquery.jobs.create` permissions not currently assigned to the runtime service account; calls/day and $/day are marked **UNVERIFIED** per Step 3 and Step 5 instructions. Public pricing figures are used for all relative savings percentages.

---

## 3. Reference Pricing & Deprecation Analysis

### A. Google Generative AI / Vertex AI Public Pricing (Q4 2026)
- **`gemini-3.8-flash`**:
  - Input: $0.075 per 1,000,000 tokens
  - Output: $0.30 per 1,000,000 tokens
  - Context Caching: $0.01875 per 1,000,000 tokens (75% discount) + $1.00/1M tokens/hour storage
- **`gemini-3.5-flash-lite`**:
  - Input: $0.01875 per 1,000,000 tokens (4x cheaper than Flash)
  - Output: $0.075 per 1,000,000 tokens (4x cheaper than Flash)
- **`gemini-3.1-pro-preview`**:
  - Input: $1.25 per 1,000,000 tokens (16.6x more expensive than Flash)
  - Output: $5.00 per 1,000,000 tokens (16.6x more expensive than Flash)
- **`gemini-embedding-2`**:
  - Input: $0.02 per 1,000,000 tokens
- **Vertex AI Batch Prediction API**:
  - 50% discount on standard prompt & generation rates across all supported models.

### B. AGENTS.md Rule 6 Deprecation Verification
Verified directly against `Gemini Deprecation Schedules\Gemini deprecations 2 SEPT 2026.pdf`:
1. `gemini-3.8-flash`: Released Sept 2, 2026. **No shutdown date announced.**
2. `gemini-3.5-flash-lite`: Released July 21, 2026. **No shutdown date announced.**
3. `gemini-3.1-pro-preview`: Released Feb 19, 2026. **No shutdown date announced.**
4. `gemini-embedding-2`: Released April 22, 2026. **No shutdown date announced.**
5. `gemini-3.1-flash-image`: Released May 28, 2026. **No shutdown date announced.**
*Conclusion:* All evaluated and proposed models comply fully with Rule 6. Zero risk of retiring endpoints.

---

## 4. Top 5 Optimization Candidates Ranked by Estimated Savings

### Rank 1: Invoice Normalization (`_apply_defaults` in `main.py:2282`)
- **Current Model:** `gemini-3.1-pro-preview` ($1.25 / 1M input, $5.00 / 1M output).
- **Proposed Model:** `gemini-3.8-flash` ($0.075 / 1M input, $0.30 / 1M output).
- **Rationale:** Formatting and schema sanitization of line items already extracted by Document AI is a structured formatting task, not a complex reasoning problem.
- **Estimated Savings:** **~94% cost reduction** for invoice normalization calls (UNVERIFIED until tested).
- **Next Step:** Propose separate migration plan with golden-set validation (Plan B).

### Rank 2: Morgan AI Chat System Prompt Context Caching (`routes/ai_routes.py:57`)
- **Current Model:** `gemini-3.8-flash` uncached ($0.075 / 1M input on ~2,500-4,000 prompt tokens per chat message).
- **Proposed Optimization:** Enable Vertex AI Context Caching for static system instructions, Morgan persona, and feature reference docs.
- **Rationale:** Multi-turn chats resend the same system instructions repeatedly. Context Caching provides a 75% discount on cached input tokens.
- **Estimated Savings:** **Up to ~75% reduction in input token costs** across chat conversations (UNVERIFIED).

### Rank 3: Document Upload Classifier (`services/document_classifier_service.py:46`)
- **Current Model:** `gemini-3.8-flash` ($0.075 / 1M input).
- **Proposed Model:** `gemini-3.5-flash-lite` ($0.01875 / 1M input).
- **Rationale:** Document routing (deciding whether a PDF is a checklist, invoice, slab, or raw coin) is a lightweight categorization task matching the exact profile of Flash-Lite (Google guide p.7-8).
- **Estimated Savings:** **~75% cost reduction** on all document classification calls (UNVERIFIED).

### Rank 4: Littleton SKU & Spreadsheet Header Resolvers (`littleton_sku_helper.py:268`, `main.py:796`, `main.py:12409`)
- **Current Model:** `gemini-3.8-flash` ($0.075 / 1M input).
- **Proposed Model:** `gemini-3.5-flash-lite` ($0.01875 / 1M input).
- **Rationale:** Mapping vendor product descriptions (e.g. "1921-D MORGAN SILV DLR BU") or user column names ("yr", "mint", "grade") to structured keys.
- **Estimated Savings:** **~75% cost reduction** on catalog imports and SKU fallbacks (UNVERIFIED).

### Rank 5: Offline Catalog & Dataset Generation Scripts (`generate_definitive_catalog.py`, `brain_processor.py`, `ingest_banknotes.py`)
- **Current Execution:** Synchronous online REST calls at standard rates.
- **Proposed Optimization:** Route through Vertex AI Batch Prediction API (Plan D candidate).
- **Rationale:** Background catalog population and knowledge indexing jobs have zero user-latency constraints.
- **Estimated Savings:** **50% flat discount** on all input/output tokens via Vertex Batch API (UNVERIFIED).

---

## 5. System Integrity & Governance Sign-Off
- **Codebase Integrity:** FIN OPS / AG CoS confirms that this audit was 100% read-only. No source files, scripts, environment variables, or cloud configurations were modified.
- **Branch & Remote Locks:** `origin/main` remains untouched at `9f04550a`. Stripe remains locked OFF. No Firestore writes occurred.
- **Policy Compliance:** In strict adherence to BATON NET-778 and Plan C v1.1, zero model switches have been executed. Any switch requires its own separate plan, golden-set quality evaluation, and explicit typed YES from Founder Eric.

*Report filed on 4 Nov 2026 by AG CoS v4.*
