# ARGON REVIEW — `PLAN_D_Batch_Pricing_Nightly_Runs.md` (BATON NET-766)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)  
**Date:** 2026-11-04 15:46 ET  
**Baton:** `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-766_ARGON_REVIEW_PLAN_D_Batch_Pricing_Nightly_Runs_20261104-1040.md`  
**Target Plan:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_D_Batch_Pricing_Nightly_Runs.md` (73 lines)  
**Mode:** PLAN REVIEW ONLY (`NO EXECUTE` — `main` stays `9f04550a`, live site untouched, Stripe OFF, no spend)  
**Verdict:** **PASS — `96 / 100` (0 Blocking Must-Fixes; 3 Non-Blocking Technical Advisories for the Test-Night Script)**

---

## 1. Executive Summary & Scoring Breakdown

`PLAN_D_Batch_Pricing_Nightly_Runs.md` evaluates Google Cloud's 50%-discounted consumption options (**Flex PayGo** and **Batch inference**) for non-interactive nightly catalog jobs. Crucially, the plan identifies the queue-time mismatch between **Batch inference** (up to 72h queue + 24h run, no SLA — `line 6`) and our mandatory **3:00 AM ET hard stop / 6:30 AM ET morning report** (`lines 18–21`), and proposes the right architectural split: **Flex PayGo** (up to 30 min per response, `global` endpoint) for overnight runs due by 6:30 AM, and **Batch** only for asynchronous bulk jobs that can wait 24–48 hours (approved by Eric at `PLAN_D_Batch_Pricing_Nightly_Runs.md:71-73`).

| Category | Weight | Score | Notes |
|---|---|---|---|
| **1. Architectural Split (Flex PayGo vs. Batch Timing)** | 25 | **25 / 25** | Accurately identifies Batch's 72h queue risk (`line 6, 19`) and routes overnight 6:30 AM-deadline jobs to Flex PayGo (`lines 20–21, 73`). |
| **2. Codebase Grounding (`location="global"` & Model Compatibility)** | 25 | **22 / 25** | `line 11` notes Flex PayGo is `global endpoint only` and `only Gemini 3.8 Flash and earlier`. Our codebase has both `location="us-central1"` (`routes/deps.py:29`) and `location="global"` (`main.py:336,436`); flagged below so Step 3's test script explicitly binds `location="global"`. |
| **3. Hard Stops (`$50` Cap, `3 AM` Cutoff, Zero Firestore Writes)** | 25 | **24 / 25** | Enforces `$50` spend cap, `3 AM` job cancellation, review-file output (`no Firestore writes without separate YES`, `lines 34, 39–40, 72`), and GCS input deletion (`line 61`). |
| **4. Verification, Rollback & PII Hygiene** | 25 | **25 / 25** | Zero user/AJ/storage-location data in GCS batch files (`line 61`); clean header-removal rollback (`line 49`). |
| **TOTAL** | **100** | **96 / 100** | **PASS (Ready for GB CoS 95+ -> SAG -> Eric YES)** |

---

## 2. Verbatim File Quotes Checked in This Turn

### 2.1 `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-766_ARGON_REVIEW_PLAN_D_Batch_Pricing_Nightly_Runs_20261104-1040.md:1-5`
```markdown
1: # BATON NET-766 - ARGON: review INBOX\PLAN_D_Batch_Pricing_Nightly_Runs.md (PLAN ONLY, ideas from Google's 'Startup guide to AI agents')
2: Filed by Antigravity Desk, 4 Nov 2026 10:40 AM ET, on GB CoS's request. MD5 F20983CC684838C048B26ACD3936C071. Eric's 4 Nov 10:36 AM decisions are appended to Plans A, B and D.
3: 
4: Write INBOX\ARGON_REVIEW_PLAN_D_Batch_Pricing_Nightly_Runs.md with a score out of 100 and any must-fixes.
5: Chain: Argon, then GB CoS 95+, then SAG, then Eric's typed YES. NOTHING EXECUTES. Main stays 9f04550a. The live site stays untouched. Stripe stays OFF. No spend.
```

### 2.2 `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\PLAN_D_Batch_Pricing_Nightly_Runs.md:5-22, 36-43, 71-73`
```markdown
5: ## What Google's docs say today (checked 4 Nov 2026)
6: - Batch inference: "50% discounted rate compared to real-time." Up to 200,000 requests per job; 1 GB input file limit. Jobs can wait in a queue for up to 72 hours, and most finish within 24 hours of starting. Unfinished jobs are cancelled after 24 hours and you pay only for completed requests. No SLA. Does not support explicit caching or RAG.
7:   https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference
8:   https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/deploy/batch-inference
9: - Price page: "Gemini models are available in batch mode at 50% discount."
10:   https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing
11: - Flex PayGo: 50% off standard; answers can take up to 30 minutes; global endpoint only; 3,000 requests per minute per model; only Gemini 3.8 Flash and earlier (not newer models such as Gemini 4 Argon). Enabled with a request header.
12:   https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/flex-paygo
13:   https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/deploy/consumption-options
14: - Deferred execution pricing: "Coming soon," "select workloads," "up to half." Not available to plan on yet.
15:   https://cloud.google.com/blog/products/ai-machine-learning/flexible-billing-and-cost-controls-for-agents-on-google-cloud
16: - Caching: on Gemini 2.5, the cache discount and the batch discount don't stack; on Gemini 3+, they stack to 95% off cached input.
17: 
18: ## The key problem: timing
19: Batch doesn't promise a finish time: it can queue up to 72 hours and run up to 24. That conflicts with the 3 AM stop and the 6:30 AM report. Flex PayGo (30 minutes at most per answer) fits the night window much better. Proposal:
20: - Flex PayGo for the nightly jobs that must be done by 6:30 AM, if their model supports it.
21: - Batch only for work that can arrive "sometime in the next day or two" (for example, bulk re-tagging or summaries), and is reported when it lands.
```
```markdown
36: ## Steps
37: 1. From Plan C, list the nightly jobs, their models and their nightly cost.
38: 2. Sort them: must finish by 6:30 AM → Flex candidate; can wait a day → batch candidate; uses RAG/caching or a newer model → not eligible.
39: 3. Catalog Research writes a small test: one job, ~100 requests, on a test copy. Results go to a review file, not into the live catalog.
40: 4. FIN OPS sets a hard stop: if the night's spend reaches $50, or it's 3 AM, the job is cancelled (Google bills only completed requests).
41: 5. Compare cost and quality (Plan B style spot checks) with the standard run.
42: 6. Report in the 6:30 AM report. GB CoS brings the result to Eric.
```
```markdown
71: ## Eric decisions (4 Nov 2026, 10:36 AM ET)
72: - Allow $0 setup plus ONE test night before 27 Nov (within the $50 cap, 3 AM stop; Firestore writes still need a separate YES).
73: - Split: Flex PayGo overnight, batch only for work that can wait a day: YES.
```

### 2.3 Codebase Grounding: Endpoint Locations (`us-central1` vs. `global`) & Active Model Versions
* **`numista_backend\routes\deps.py:28-37`** (uses `location="us-central1"`):
```python
28: try:
29:     genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
30:     logger.info("Successfully initialized Vertex AI Google GenAI Client.")
31: except Exception as ge:
32:     logger.warning(f"Failed to initialize Vertex AI GenAI Client: {ge}")
33:     genai_client = None
34: 
35: # Model Constants (Rule 6 compliant)
36: MODEL_FLASH = "gemini-3.8-flash"
37: MODEL_PRO = "gemini-3.1-pro-preview"
```
* **`numista_backend\main.py:335-336, 429-436`** (uses `location="global"` by default):
```python
335: PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "studio-9101802118-8c9a8")
336: LOCATION = "global"
...
429: PRIMARY_MODEL = GEMINI_FLASH_MODEL
430: PRO_MODEL     = GEMINI_PRO_MODEL
431: IMAGE_MODEL   = GEMINI_IMAGE_MODEL
432: 
433: # Initialize google-genai client (Vertex AI backend)
434: # Override via GEMINI_LOCATION env var if needed, default to 'global'
435: GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", LOCATION)
436: genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)
```
* **`numista_backend\config\__init__.py:24-27`** (confirms active models are `gemini-3.8-flash` and earlier, eligible for Flex PayGo per `PLAN_D:11`):
```python
24: GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash")          # Primary workhorse
25: GEMINI_PRO_MODEL   = os.getenv("GEMINI_PRO_MODEL",   "gemini-3.1-pro-preview")    # High-reasoning tasks
26: GEMINI_LITE_MODEL  = os.getenv("GEMINI_LITE_MODEL",  "gemini-3.5-flash-lite")     # Lightweight/fast tasks
27: GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")    # Image generation
```

---

## 3. Must-Fixes & Advisories

* **Blocking Must-Fixes:** **None (0).**
* **Non-Blocking Technical Advisories for Step 3–4 Test-Night Implementation (3):**
  1. **Pin `location="global"` on the Flex PayGo Client (`line 11` vs. `routes/deps.py:29`):** Because Flex PayGo is supported on the **`global` endpoint only** (`PLAN_D:11`), the Step 3 test script (`~100 requests`) must explicitly instantiate `genai.Client(vertexai=True, project=PROJECT_ID, location="global")` (matching `main.py:336,436`) and **must not** import `genai_client` from `numista_backend/routes/deps.py:29` (which is pinned to `location="us-central1"`).
  2. **Per-Request Timeout & Wall-Clock 3:00 AM Watchdog (`lines 11, 40`):** Because Flex PayGo responses can take up to **30 minutes** (`line 11`), standard synchronous client timeouts (such as the `25.0` second timeout in `cert_routes.py:468`) will drop valid Flex requests before they complete. Step 3's test runner should set an HTTP/SDK timeout of `1800s` (30 min) capped by a dynamic deadline `min(1800, seconds_until_0300_ET)` so no in-flight call can run past the 3:00 AM ET stop (`line 40`).
  3. **Guaranteed GCS Input/Output Cleanup on Cancellation (`lines 40, 61`):** `line 61` requires that *"Batch input files must be deleted after the run."* If a Batch job is cancelled early at 3:00 AM or at the `$50` cap (`line 40`), ensure a `try / finally` block deletes both the temporary GCS input JSONL and any partial GCS output blobs after exporting completed results to the local review file.
