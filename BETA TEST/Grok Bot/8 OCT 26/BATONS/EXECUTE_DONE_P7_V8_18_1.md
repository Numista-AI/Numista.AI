# EXECUTE DONE: P7 V8.18.1

**Target:** Targeted fixes from the V8.18 FAIL score  
**Date:** 2026-10-19  
**Branch:** `p7-v8.9`  
**Commit SHA:** `0f2f06e0` (`0f2f06e064bfadd6df0fa83ba7e65027271f924c`)  
**Base Commit:** `1137b732`  
**Worktree:** `C:\Users\ericd\AppData\Local\Temp\p7v89_build`  
**Flutter Analyze:** 0 errors, 0 warnings (ran in 14.8s)  
**Flutter Tests:** 585/585 passed (baseline 583)  
**Backend Pytest:** 573 passed, 250 warnings in 19.96s (baseline 571)  
**GEMINI38 Review:** PASS  

---

## 1. Summary of Fixes

### FIX 1: Invoice PDF Import Path
- **Button Wired:** In `numista_mobile/lib/screens/add_coins_hub.dart:1147-1165`, the previously dead simulation button was retitled to `"Open Invoice Importer →"` and wired directly to `buildAddCoinsHtmlPath(AuthService.userEmail)`.
- **Route:** Opens `add_coins.html?email=<user>&api=<api_base>` (full-screen bulk import and invoice ingestion).
- **Backend Endpoints:**
  - `POST /api/import/upload` (or direct GCS upload via `POST /api/import/start`)
  - `POST /api/import/process` (`main.py:7192`)
  - Background worker: `_execute_import_process_worker` (`main.py:7224`)
- **Gemini vs Document AI:**
  - In `numista_backend/main.py:7435`, documents are classified via `classify_document_bytes` using Gemini 3.7 Flash (`services/document_classifier_service.py:46`).
  - Checklist documents are processed via `extract_checklist_document` (`services/checklist_parser.py:257`) using Gemini 3.1 Pro Preview.
  - Invoices and receipts (`main.py:7533-7538`) are processed directly via `genai_client.models.generate_content(model=PRIMARY_MODEL, ...)` using Gemini 3.8 Flash.
  - **Confirmation:** The invoice processing path does **NOT** use or depend on Document AI processors. It is 100% powered by Gemini and functional on p7gate.
- **Dead Simulation Cleanup:** Removed `_runParallelBatchSim`, `_isBatchProcessing`, `_batchProgress`, `_batchStatusMsg`, and `_batchItems` mockup code from `add_coins_hub.dart`.

### FIX 2: Scan Root Cause & Server-Side 25s Cap
- **(a) cert-photo 403 Root Cause:**
  - **File:Line:** `numista_backend/routes/cert_routes.py:374`
  - **Exact code:** `_SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")`
  - **Why p7gate gets `numista-qc`:** On Cloud Run revisions, Google Cloud sets `GOOGLE_CLOUD_PROJECT` or `GCLOUD_PROJECT`, but `FIREBASE_PROJECT_ID` was unset in the p7gate Cloud Run deployment environment. Consequently, `cert_routes.py:374` fell back to its default `"numista-qc"`. When `_genai.Client(vertexai=True, project=_SCAN_PROJECT_ID, location=_SCAN_LOCATION)` made calls to Vertex AI, it called project `numista-qc` using service account `568985927038-compute@developer.gserviceaccount.com` (which lives in `studio-9101802118-8c9a8`), triggering the 403 `PERMISSION_DENIED` on `projects/numista-qc`.
  - **Proposed Infra Fix for Grok CoS:** Set environment variable `FIREBASE_PROJECT_ID=studio-9101802118-8c9a8` (and/or `GOOGLE_CLOUD_PROJECT=studio-9101802118-8c9a8`) on the Cloud Run revision. No code changes needed for this infra fix.
- **(b) identify_coin_photo Server-Side 25s Timeout:**
  - **File:Line:** `numista_backend/main.py:6130, 6133-6149, 6209-6228, 6248-6265`
  - Extracted helper `call_gemini_identify(contents, model=PRIMARY_MODEL)` executing in an executor thread (`run_in_executor`) to keep the asyncio event loop completely unblocked.
  - Added configurable timeout `GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))`.
  - Pass 1 is wrapped in `asyncio.wait_for(call_gemini_identify(...), timeout=GEMINI_IDENTIFY_TIMEOUT)`. On `asyncio.TimeoutError`, it immediately raises `HTTPException(status_code=408, detail="Image identification timed out. Please try again.")`.
  - Pass 2 is bounded at `timeout=min(10.0, GEMINI_IDENTIFY_TIMEOUT)` with non-fatal fallback.
- **(c) Mocked Pytest Added:**
  - File: `numista_backend/tests/test_identify_timeout.py`
  - `test_identify_coin_photo_returns_408_on_timeout`: verifies 408 response and `"timed out"` detail on TimeoutError.
  - `test_identify_coin_photo_real_wait_for_timeout`: verifies actual `asyncio.wait_for` timing out on slow calls.

### FIX 3: Sub-16px Text Sizes & Back Arrow Confirmation
- **1. Settings Screen Microscope Description:**
  - **File:Line:** `numista_mobile/lib/screens/settings_screen.dart:587-590`
  - **Change:** `fontSize: 13` → `fontSize: 16`.
  - **Plain English update:** `"Connects digital USB microscopes via the Numista Desktop Agent on localhost. Keep disabled if you use phone camera or file uploads."` → `"Connect a USB microscope to identify coins up close."`
- **2. Add Coins Hub NFC Badge:**
  - **File:Line:** `numista_mobile/lib/screens/add_coins_hub.dart:4139-4140`
  - **Change:** `fontSize: 12` → `fontSize: 16`.
- **3. Back Arrow Tap Target Confirmation:**
  - **File:Line:** `numista_mobile/lib/screens/add_coins_hub.dart:621-624` (and 617, 637, 647):
    ```dart
    appBar: AppBar(
      title: const Text('Add by Cert #'),
      leading: const BackButton(),
    ),
    ```
  - **Confirmation:** Default Flutter `BackButton` renders an `IconButton` adhering to `kMinInteractiveDimension = 48.0`. There are no custom constraints or padding overrides shrinking it.

### FIX 4: Reset `_welcomeDone` on Sign-Out
- **File:Line:** `numista_mobile/lib/widgets/auth_gate.dart:56-60, 68-70`
  - Exposed `AuthGate.resetWelcome()` and `AuthGate.welcomeDone`.
  - Defined `_AuthGateState.resetWelcome()` to set `_welcomeDone = false`.
- **File:Line:** `numista_mobile/lib/screens/base_layout.dart:1369`
  - Added `AuthGate.resetWelcome()` inside the sign-out confirmation handler.
- **File:Line:** `numista_mobile/lib/services/auth_service.dart:205`
  - Added `AuthGate.resetWelcome()` inside `AuthService.signOut()`.

---

## 2. Investigations

### 1. CAC Slab 403 / Scan Root Cause
- **Evidence from COS_SCORE:**
  `numista-backend-00468-qir at 09:36:41 ET: 403 PERMISSION_DENIED ... Permission 'aiplatform.endpoints.predict' denied on resource '//aiplatform.googleapis.com/projects/numista-qc/locations/global/publishers/google/models/gemini-3.8-flash'. Backend runs as 568985927038-compute@developer.gserviceaccount.com.`
- **Exact File:Line:**
  `numista_backend/routes/cert_routes.py:374`:
  ```python
  _SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")
  ```
- **Why p7gate gets `numista-qc`:**
  `main.py:312` reads `PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "studio-9101802118-8c9a8")`, which defaults correctly to `studio-9101802118-8c9a8`. However, `cert_routes.py:374` uniquely defaults to `"numista-qc"`. Because `FIREBASE_PROJECT_ID` is not explicitly set as an environment variable on the Cloud Run revision, `cert_routes.py` instantiated `_genai.Client(vertexai=True, project='numista-qc')`. The service account `568985927038-compute@developer.gserviceaccount.com` has IAM permissions in `studio-9101802118-8c9a8`, but not in `numista-qc`, resulting in `403 PERMISSION_DENIED`.
- **Proposed Infra Fix for Grok CoS:**
  Set `FIREBASE_PROJECT_ID=studio-9101802118-8c9a8` in Cloud Run revision environment variables.

### 2. `identify_coin_photo` 56s-473s Latency
- **Evidence from COS_SCORE:**
  `identify_coin_photo latencies: 56s, 144s, 173s (x3), 180s, 257s, 393s, 459s (500), 473s. Requests stuck for minutes — server-side retries/backoff, not cold start.`
- **Root Cause:**
  `identify_coin_photo` is an `async def` FastAPI route, but it invoked `genai_client.models.generate_content(...)` directly on the main event loop thread without a timeout or worker executor. During Vertex AI latency spikes or internal retry backoffs in the Google genai SDK, the call blocked the server worker thread indefinitely until the Cloud Run request limit terminated it.
- **Fix Implemented:**
  1. Offloaded synchronous `generate_content` calls to a thread pool via `run_in_executor` in `call_gemini_identify`.
  2. Wrapped execution in `asyncio.wait_for(..., timeout=25.0)`.
  3. Added explicit HTTP 408 timeout handler returning: `{"detail": "Image identification timed out. Please try again."}`.

### 3. Backup 314 Records Exported vs 312 Displayed
- **Exact Code Locations:**
  - Export: `numista_mobile/lib/services/backup_export_service.dart:69-72, 106, 151, 161-162, 247-252`
    ```dart
    final snap = await fs.doc(AuthService.userDocPath).collection(subcollection).get();
    for (final doc in snap.docs) {
      results.add({'_id': doc.id, ...doc.data()});
    }
    ...
    'coin_count': coins.length, // 314 raw docs
    'coins': coins,
    ```
  - Display: `numista_mobile/lib/screens/my_collection_screen.dart:1450-1456`
    ```dart
    final liveExpansion = expandCollection(
      coinsDocs.map((d) => d.data()).toList(),
      coinsDocs.map((d) => d.id).toList(),
    );
    final liveCoinsCount = liveExpansion.totalCoins; // 312 physical coins
    ```
  - Counting Rule: `numista_mobile/lib/services/set_expansion_helper.dart:193-195, 232-236`
    ```dart
    bool isPhysicalCoin(Map<String, dynamic> row) {
      final it = (row['item_type']?.toString() ?? 'coin').toLowerCase().trim();
      if (it != 'coin' && it != '') return false;
      return !isSetParent(row);
    }
    ```
- **Explanation:**
  No records were deleted or lost. The user's Firestore `coins` subcollection contains 314 raw document snapshots. The collection screen and dashboard run `expandCollection()`, which filters out set parent container documents and supplies (`isPhysicalCoin == false`), yielding 312 physical coins. In contrast, `BackupExportService.generateExportPayload()` queries the raw Firestore subcollection and dumps all 314 document snapshots (including set parents / supplies). Both numbers are correct for their respective scopes.

### 4. Manual Grading & Cert Fields Scope
- **File:** `numista_mobile/lib/widgets/add_coin_manual_form.dart`
- **Current Fields:**
  - Year (`_yearCtrl`)
  - Mint Mark (`_mintCtrl`)
  - Denomination (`_denomCtrl`)
  - Program/Series (`_programCtrl`)
  - Theme/Subject (`_themeCtrl`)
  - Variety (`_varietyCtrl`)
  - Condition (`_conditionCtrl`)
  - Cost (`_costCtrl`)
  - Quantity (`_qtyCtrl`)
  - Retailer (`_retailerCtrl`)
  - Invoice # (`_invoiceCtrl`)
  - Storage Location (`_storageCtrl`)
  - Notes (`_notesCtrl`)
- **Missing Fields:** Grading Service (PCGS, NGC, CAC, CACG, ANACS, Raw) and Certification Number.
- **Estimated Scope for P7.1:**
  - Adding a `DropdownButtonFormField` for Grading Service (PCGS, NGC, CAC, CACG, ANACS, Raw) + `TextFormField` for Certification Number in `add_coin_manual_form.dart`.
  - Propagating fields into the invoice review screen and submit payload.
  - Estimated diff: ~2 files, ~100 lines.
  - **Recommendation:** File as dedicated P7.1 ticket.

---

## 3. Verification Test Evidence

```
$ flutter analyze lib/
Analyzing lib...                                                
No issues found! (ran in 14.8s)

$ flutter test --reporter compact
00:34 +585: All tests passed!

$ python -m pytest numista_backend/tests/ -q
573 passed, 250 warnings in 19.96s
```
