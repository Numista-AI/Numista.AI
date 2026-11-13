# GEMINI 3.8 TECHNICAL REVIEW — `SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md` (R1)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**Target Plan:** [`SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md)  
**Author Reviewed:** AG CoS v4 (`ba2bfdb2`)  
**Companion Grok CoS Score:** [`COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md) (`74/100 REVISE`)  
**Wake Reference:** [`WAKE_AG-COS-V4_NET-723_NET-718-R2-FIX-ONLY_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/WAKES/WAKE_AG-COS-V4_NET-723_NET-718-R2-FIX-ONLY_20261101.md)  
**Date / Time:** 2026-11-01 18:17 ET  
**Score:** **75 / 100 — REVISE (`SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md` required)**  
**Execution Lock:** **NO EXECUTE** — Plan-only review. Zero code changes, zero deploys, zero pushes.

---

## 1. Executive Summary & Scoring Breakdown

`SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md` establishes a strong 10-layer defense-in-depth architecture for protecting collector identities, vault inventories, physical locations, and invoice PII prior to the public ad launch (`NET-706`). However, independent verification against `origin/dev` (`32d4b42e`) confirms **three MUST-FIX (`MF1`–`MF3`) and five SHOULD-FIX (`SF1`–`SF5`) defects** (caused primarily by line shifts between the local `p7-v8.9` working tree and `origin/dev` `32d4b42e`, unquoted rule files, and unaddressed direct-to-GCS signed URL upload paths that bypass backend memory).

To accelerate `AG CoS v4` (`ba2bfdb2`) on [`WAKE_AG-COS-V4_NET-723_NET-718-R2-FIX-ONLY_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/WAKES/WAKE_AG-COS-V4_NET-723_NET-718-R2-FIX-ONLY_20261101.md), this review provides **turnkey, byte-exact verbatim code blocks and line numbers verified directly from `origin/dev` (`32d4b42e`)** for every `MF1–MF3` and `SF1–SF5` item.

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Technical Accuracy & `origin/dev` Alignment** | 30 | **18 / 30** | `-12`: `firestore.rules` line numbers wrong and unquoted (`MF1`); invented `$12.99` price, wrong Secret Manager line range (`main.py:60-120`), and non-existent photo endpoints (`MF3`). |
| **2. Receipt Redaction & Zero-Retention Completeness** | 25 | **16 / 25** | `-9`: Missed direct-to-GCS V4 signed URL uploads in `POST /api/import/start` (`main.py:7499-7548`) and `POST /v1/import/get_upload_url` (`routes/import_routes.py:46-66`), plus `/raw/` paths at `main.py:7377, 7434, 7532, 7931, 8405, 8489` (`MF2`). |
| **3. Rule 6(a) Verbatim Code Citations** | 20 | **16 / 20** | `-4`: `firestore.rules`, `firebase.json`, and `NET-706 R5` lines `160-166` cited by line number without verbatim quotes (`MF1`, `MF3`). |
| **4. Machine-Checkable Exit Criteria (Rule 8)** | 15 | **15 / 15** | Strong emulator test matrix, `pytest` targets, and privacy audit commands; needs full-history `gitleaks git --verbose --redact` (`SF1`). |
| **5. Governance & Scope Hygiene** | 10 | **10 / 10** | Respects `NO EXECUTE` lock and two-phase dry-run $\rightarrow$ Eric's typed `YES` gate for GCS receipt backfill. |
| **TOTAL** | **100** | **75 / 100** | **REVISE (`R2` Fix-Only)** |

---

## 2. Detailed Audit & Turnkey `origin/dev` (`32d4b42e`) Citations for `R2`

### MUST-FIX 1 (`MF1`): `firestore.rules` & `firebase.json` Verbatim Quotes, Exact Line Numbers, and `public_wishlists` Hardening

1. **Which `firestore.rules` is deployed (`numista_mobile/firebase.json:1-6` vs `numista_backend/firestore.rules:1-11`):**
   - `numista_mobile/firestore.rules` is the **authoritative deployed ruleset**, configured in [`numista_mobile/firebase.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firebase.json#L1-L6):
     ```json
     1: {
     2:   "firestore": {
     3:     "rules": "firestore.rules",
     4:     "indexes": "firestore.indexes.json"
     5:   },
     6:   "hosting": {
     ```
   - By contrast, [`numista_backend/firestore.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/firestore.rules#L1-L11) is an undeployed reference mirror (`numista_backend/firebase.json` configures only `"functions"`):
     ```javascript
      1: // ╔══════════════════════════════════════════════════════════════════════╗
      2: // ║  ⚠️  NOT DEPLOYED — REFERENCE MIRROR ONLY                          ║
      3: // ║                                                                    ║
      4: // ║  The DEPLOYED rules are in: numista_mobile/firestore.rules         ║
      5: // ║  (deployed via `firebase deploy --only firestore:rules` from       ║
      6: // ║   the numista_mobile/ directory, where firebase.json has the       ║
      7: // ║   "firestore" key).                                                ║
      8: // ║                                                                    ║
      9: // ║  numista_backend/firebase.json has ONLY "functions" — running      ║
     10: // ║  deploy from here will NOT update Firestore rules in production.   ║
     11: // ╚══════════════════════════════════════════════════════════════════════╝
     ```

2. **`isOwner(email)` (`numista_mobile/firestore.rules:13-15`, NOT lines `14-18`):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_mobile/firestore.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firestore.rules#L13-L15):
     ```javascript
     13:     function isOwner(email) {
     14:       return request.auth != null && (request.auth.token.email == email || request.auth.uid == email);
     15:     }
     ```

3. **`/users/{email}/coins/{coinId}` (`numista_mobile/firestore.rules:40-67`):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_mobile/firestore.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firestore.rules#L40-L67):
     ```javascript
     40:     match /users/{email}/coins/{coinId} {
     41:       // Owner reads their own coins (list + get)
     42:       allow read: if isOwner(email);
     43: 
     44:       // Owner deletes their own coins (needed for account reset, coin removal,
     45:       // and client-side demo purging fallback)
     46:       allow delete: if isOwner(email);
     47: 
     48:       // Client-created coins MUST explicitly declare is_demo == false and
     49:       // is_demo_cleared == false. This prevents client code from ever
     50:       // stamping demo coins into a user's vault — only the backend Admin
     51:       // SDK (which bypasses rules) can write is_demo: true.
     52:       // Using keys().hasAll() + explicit == false check handles missing fields
     53:       // safely without throwing property-access evaluation errors in rules v2.
     54:       // (Root cause fix for the "332 coins" regression, 2026-03-31.)
     55:       allow create: if isOwner(email)
     56:                     && request.resource.data.keys().hasAll(['is_demo', 'is_demo_cleared'])
     57:                     && request.resource.data.is_demo == false
     58:                     && request.resource.data.is_demo_cleared == false;
     59: 
     60:       // Client updates may modify any coin fields EXCEPT is_demo and
     61:       // is_demo_cleared — those flags are backend-managed only.
     62:       // Using diff().affectedKeys() avoids failing when fields are absent on old docs.
     63:       allow update: if isOwner(email)
     64:                     && !request.resource.data.diff(resource.data)
     65:                           .affectedKeys()
     66:                           .hasAny(['is_demo', 'is_demo_cleared']);
     67:     }
     ```

4. **`/public_wishlists/{token}` (`numista_mobile/firestore.rules:247-254`, NOT line `182`):**
   - *(Note: Line `182` in `numista_mobile/firestore.rules` is `match /config/{document=**}`.)*
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_mobile/firestore.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firestore.rules#L247-L254):
     ```javascript
     247:     // Public Wishlists: Anyone with the token can read a single shared wishlist (no list/enumeration).
     248:     // Authenticated owners can create shares.
     249:     // Unauthenticated gift-buyers can ONLY update the `reserved_items` and `reservation_details` fields.
     250:     match /public_wishlists/{token} {
     251:       allow get: if true;
     252:       allow create: if request.auth != null;
     253:       allow update: if request.resource.data.diff(resource.data).affectedKeys().hasAny(['reserved_items', 'reservation_details']);
     254:     }
     ```
   - **Critical Security Finding on Lines 252–253 (Must Include in `R2` Section 2.1):**
     1. **Line 253 (`hasAny` vs `hasOnly`):** `affectedKeys().hasAny(['reserved_items', 'reservation_details'])` evaluates to `true` as long as *at least one* of those two keys is modified — meaning an unauthenticated attacker who modifies `reserved_items` can **simultaneously overwrite `items`, `owner_alias`, or inject arbitrary fields** in the same `update` call! It **must** be changed to `.hasOnly(['reserved_items', 'reservation_details'])`.
     2. **Line 252 (`allow create`):** Because `/api/wishlist/create-share` (`main.py:12733-12755`) writes the share document server-side via the Admin SDK (`db.collection("public_wishlists").document(token).set(snapshot)`), client-side `create` should either be locked to `allow create: if false;` (Admin SDK only) or strictly bound to `request.auth != null && request.resource.data.owner_uid == request.auth.uid && !('owner_email' in request.resource.data)`.

5. **`/family_groups/{familyGroupId}` (`numista_mobile/firestore.rules:277-281`, NOT line `190`):**
   - *(Note: Line `190` in `numista_mobile/firestore.rules` is `match /coin_image_index/{document=**}`.)*
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_mobile/firestore.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firestore.rules#L277-L281):
     ```javascript
     277:     // Family Trust Inheritance Sync (Phase 3.4)
     278:     match /family_groups/{familyGroupId} {
     279:       allow read: if request.auth != null;
     280:       allow write: if request.auth != null && request.auth.uid == resource.data.primary_owner_uid;
     281:     }
     ```

6. **`numista_backend/storage.rules` (`origin/dev` `32d4b42e` lines `1-52`):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/storage.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/storage.rules#L1-L52) (already quoted accurately in `NET-718` Section 2.2; keep synchronized in both `numista_backend/storage.rules` and `numista_mobile/storage.rules` `[PROPOSED]` if deployed from `numista_mobile/firebase.json`).

---

### MUST-FIX 2 (`MF2`): Receipt Redaction Pipeline, Direct Signed-URL Bypass Closure, and Existing Document AI Client

1. **Close Direct-to-GCS Signed-URL Upload Bypasses (`origin/dev:numista_backend/main.py:7499-7548` & `routes/import_routes.py:46-66`):**
   - Currently on `origin/dev` (`32d4b42e`), `POST /api/import/start` (`numista_backend/main.py:7499-7548`) generates V4 signed `PUT` URLs pointing directly to `f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"`, allowing the client browser/app to upload unredacted invoice/receipt files straight to GCS **without ever touching backend memory**:
     ```python
     7499: @app.post("/api/import/start")
     7500: async def import_start(req: ImportStartRequest, decoded_user: dict = Depends(verify_token)):
     ...
     7531:                 safe_name = os.path.basename(f_meta.name)
     7532:                 blob_path = f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"
     7533:                 blob = bucket.blob(blob_path)
     7534:                 url = blob.generate_signed_url(
     7535:                     version="v4",
     7536:                     expiration=900, # 15 mins
     7537:                     method="PUT",
     7538:                     content_type=f_meta.type or "application/octet-stream",
     7539:                      credentials=signing_creds
     7540:                 )
     7541:                 upload_urls[f_meta.name] = url
     ```
   - Similarly, [`numista_backend/routes/import_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/import_routes.py#L46-L66) exposes `POST /v1/import/get_upload_url`:
     ```python
     46: @router.post("/get_upload_url")
     47: async def get_upload_url(
     48:     req: UploadUrlRequest,
     49:     user_token: dict = Depends(verify_firebase_token)
     50: ):
     51:     """Generates a V4 Signed URL for direct-to-GCS client upload."""
     52:     user_id = user_token.get("uid") or user_token.get("email")
     53:     bucket = get_gcs_bucket()
     54:     
     55:     blob_name = f"imports/{user_id}/{uuid.uuid4().hex}_{req.filename}"
     56:     blob = bucket.blob(blob_name)
     ```
   - **`R2` Fix Requirement:** `R2` must explicitly specify that:
     - In `POST /api/import/start` (`main.py:7528-7545`), direct-to-GCS V4 signed `PUT` URLs are disabled (`upload_urls[f_meta.name] = "/api/import/upload"`), forcing all client imports through `POST /api/import/upload` (`main.py:7396`) where in-memory EXIF stripping and PII redaction execute **before** `blob.upload_from_string(...)`.
     - In `POST /v1/import/get_upload_url` (`routes/import_routes.py:46-66`), direct signed `PUT` URLs for document/image uploads are deprecated/disabled in favor of backend-proxied redaction upload.

2. **All Six `/raw/` GCS Path Occurrences in `origin/dev:numista_backend/main.py` (`7377, 7434, 7532, 7931, 8405, 8489`):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L7373-L7381):
     ```python
     7373: def _save_to_gcs(user_email: str, session_id: str, filename: str, content: bytes, content_type: str = "application/octet-stream"):
     7374:     """Save raw uploaded file to GCS under user/imports/session_id/raw/"""
     7375:     bucket = _get_gcs_bucket()
     7376:     safe_name = os.path.basename(filename)
     7377:     blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
     7378:     blob = bucket.blob(blob_path)
     7379:     blob.upload_from_string(content, content_type=content_type)
     7380:     return f"gs://{IMPORT_BUCKET}/{blob_path}"
     ```
   - Verbatim from `origin/dev` (`32d4b42e`) `numista_backend/main.py:7433-7442` (`POST /api/import/upload`):
     ```python
     7433:         safe_name = os.path.basename(file.filename)
     7434:         blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
     7435:         
     7436:         bucket = _get_gcs_bucket()
     7437:         blob = bucket.blob(blob_path)
     7438:         
     7439:         # Stream directly from the SpooledTemporaryFile to GCS without loading full bytes into RAM
     7440:         file.file.seek(0)
     7441:         blob.upload_from_file(file.file, content_type=file.content_type or "application/octet-stream")
     7442:         gcs_uri = f"gs://{IMPORT_BUCKET}/{blob_path}"
     ```
   - Verbatim from `origin/dev` (`32d4b42e`) `numista_backend/main.py:7930-7933, 8404-8406, 8488-8490` (`_execute_import_process_worker`):
     ```python
     7930:             safe_name = os.path.basename(f_meta.get("name", ""))
     7931:             blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
     7932:             blob = bucket.blob(blob_path)
     ...
     8404:                                 partner_safe = os.path.basename(partner_file)
     8405:                                 partner_blob = bucket.blob(f"{user_email}/imports/{session_id}/raw/{partner_safe}")
     ...
     8488:                                 safe_name = os.path.basename(source_file)
     8489:                                 gcs_path_img = f"gs://{IMPORT_BUCKET}/{user_email}/imports/{session_id}/raw/{safe_name}"
     ```
   - Also cite `POST /api/process_invoice` (`origin/dev:numista_backend/main.py:2023-2048`) and `POST /upload_document` (`origin/dev:numista_backend/routes/scan_routes.py:84-101`):
     ```python
     2023: @app.post("/api/process_invoice")
     2024: async def process_invoice(request: Request, file: UploadFile = File(...), user_email: str = Form("default"), decoded_user: dict = Depends(verify_token)):
     ...
     2047:         doc_client = documentai.DocumentProcessorServiceClient()
     2048:         name = doc_client.processor_path( DOC_AI_PROJECT_ID, DOC_AI_LOCATION, DOC_AI_PROCESSOR_ID)
     ```
     ```python
     84: @router.post("/upload_document", response_model=DocumentParseResponse)
     85: async def upload_document(
     86:     request: Request,
     87:     file: UploadFile = File(...),
     88:     user_email: str = Form("default"),
     89:     decoded_user: dict = Depends(verify_firebase_token),
     90: ):
     ```
   - **`R2` Fix Requirement:** Replace `/raw/` with `/redacted/` across `main.py:7377, 7434, 7532, 7931, 8405, 8489`, pass uploaded bytes through `_sanitize_image_exif()` + `_redact_receipt_pii_bytes()` in memory (`io.BytesIO`) inside `POST /api/import/upload` (`main.py:7433-7442`) and `_save_to_gcs` (`main.py:7373-7380`) before writing to GCS, and never write unredacted bytes to `/tmp`, Cloud Run logs, or GCS staging.

3. **Existing Document AI Client in `origin/dev:numista_backend/main.py` (`lines 19, 2047-2048, 5008-5018`):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L5008-L5018):
     ```python
       19: from google.cloud import documentai
     ...
     5008:     client = documentai.DocumentProcessorServiceClient(
     5009:         credentials=credentials,
     5010:         client_options={"api_endpoint": "us-documentai.googleapis.com"},
     5011:     )
     5012: 
     5013:     raw_doc = documentai.RawDocument(content=file_bytes, mime_type=content_type)
     5014:     request = documentai.ProcessRequest(
     5015:         name=DOCUMENT_AI_PROCESSOR_PATH,
     5016:         raw_document=raw_doc,
     5017:     )
     5018:     result = await asyncio.to_thread(client.process_document, request=request)
     ```
   - Reuse this exact stateless synchronous `client.process_document` pattern (where Document AI processes `raw_document` in-memory without GCS staging and does not retain customer data under Google Cloud Enterprise Data Processing Addendum terms).

4. **GCS Versioning / Soft Delete & PII-Free Dry-Run Audit Report:**
   - Specify in `Section 4.3` that `RECEIPT_REDACTION_AUDIT_REPORT.json` records **only** `blob_path_hash` (or object path), `page_count`, `detected_entity_types` (e.g., `["PERSON_NAME", "STREET_ADDRESS", "PHONE_NUMBER"]`), `entity_counts`, `confidence_scores`, and `bounding_boxes` (`[x0, y0, x1, y1]`) — **ZERO extracted PII text strings**.
   - In Phase B (after Eric's typed `YES`), after overwriting the live object with redacted bytes, explicitly delete noncurrent object generations (`bucket.list_blobs(versions=True)` $\rightarrow$ `bucket.delete_blob(blob.name, generation=old_generation)`) and verify soft-delete policy retention so unredacted prior generations cannot be recovered.

---

### MUST-FIX 3 (`MF3`): Invented `$12.99` Price Removal, Secret Manager Citation, Real Photo-Ingest Routes, and Verbatim Quotes

1. **Remove Invented `$12.99` Price (`Section 8`, lines `297` & `307`):**
   - Replace `value: 12.99` with Plan v3.2 canonical prices (`$4.99` Copper, `$8.99` Silver, `$10.99` Platinum, `$15.99` Gold, `$5.00` AI Top-Up, `$29.94–$95.94` Full Exports) or `"server-verified Stripe session amount_total / 100.0"`.
   - Quote verbatim `PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md:160-166`:
     ```dart
     160:       if (kIsWeb) {
     161:         js.context.callMethod('fbq', ['track', 'Purchase', js.JsObject.jsify({
     162:           'value': amountUsd,
     163:           'currency': 'USD',
     164:         })]);
     165:         prefs.setBool('meta_purchase_fired_$sessionId', true);
     166:       }
     ```

2. **Real Secret Manager / `os.environ` Citations (`Section 7.1`, replacing wrong `main.py:60-120` cite):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L11977-L11986):
     ```python
     11977:     """Obtain an OAuth2 application token from eBay (Client Credentials Grant).
     11978:     Reads EBAY_CERT_ID exclusively from os.environ (mounted via Secret Manager).
     11979:     Caches the token in-memory until 5 minutes before expiry.
     11980:     Returns None if credentials are missing or the token request fails.
     11981:     """
     11982:     global _ebay_oauth_token_cache
     11983:     ebay_app_id = os.environ.get("EBAY_APP_ID", "EricDeis-CoinApp-PRD-96bc5b6bc-042c7233")
     11984:     ebay_cert_id = os.environ.get("EBAY_CERT_ID")
     ```
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/routes/payment_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L172-L176):
     ```python
     172:     payload = await request.body()
     173:     sig_header = request.headers.get("stripe-signature")
     174:     webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
     ```
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/stripe_config.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/stripe_config.py#L28-L31):
     ```python
     28:     # Keys come exclusively from environment variables / Secret Manager.
     29:     pub_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
     30:     sec_key = os.environ.get("STRIPE_SECRET_KEY")
     ```

3. **Real Photo-Ingest Endpoints & Central GCS Upload Helpers (`Section 3.3`, replacing non-existent `/api/coins/{id}/photo` and `/api/chat/photo`):**
   - Verbatim central upload helpers in `origin/dev` (`32d4b42e`) [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L4282-L4293):
     ```python
     4282: def _upload_to_gcs(bucket_name: str, file_bytes: bytes, destination_blob_name: str, content_type: str = "image/jpeg") -> str:
     4283:     """Uploads bytes to GCS and returns a gs:// URI for Vertex AI consumption."""
     4284:     try:
     4285:         storage_client = storage.Client()
     4286:         bucket = storage_client.bucket(bucket_name)
     4287:         blob = bucket.blob(destination_blob_name)
     4288:         blob.upload_from_string(file_bytes, content_type=content_type)
     4289:         return f"gs://{bucket_name}/{destination_blob_name}"
     ```
   - Verbatim real photo-ingest endpoints in `origin/dev` (`32d4b42e`) `numista_backend/main.py`:
     - `POST /api/identify_coin_photo` (`main.py:6371-6372`, uploads obverse/reverse via `_upload_to_gcs` at `main.py:6670, 6676`):
       ```python
       6371: @app.post("/api/identify_coin_photo")
       6372: async def identify_coin_photo(request: Request, obverse: UploadFile = File(...), reverse: Optional[UploadFile] = File(None), user_email: str = Form("default"), decoded_user: dict = Depends(verify_token)):
       ```
     - `POST /api/identify_group_photo` (`main.py:5796-5797`, uploads via `_upload_to_gcs` at `main.py:5840`):
       ```python
       5796: @app.post("/api/identify_group_photo")
       5797: async def identify_group_photo(request: Request, file: UploadFile = File(...), user_email: str = Form("default"), Fast_Mode: bool = Form(True), decoded_user: dict = Depends(verify_token)):
       ```
     - `POST /api/analyze_binder_scan` (`main.py:4621-4622`, uploads via `_upload_to_gcs` at `main.py:4668`):
       ```python
       4621: @app.post("/api/analyze_binder_scan")
       4622: async def analyze_binder_scan(
       ```
     - `POST /api/analyze_checklist` (`main.py:5104-5105`, uploads via `_upload_to_gcs` at `main.py:5143`):
       ```python
       5104: @app.post("/api/analyze_checklist")
       5105: async def analyze_checklist(request: Request, file: UploadFile = File(...), user_email: str = Form("default"), decoded_user: dict = Depends(verify_token)):
       ```
     - `POST /api/convert_heic` (`main.py:5773-5774`):
       ```python
       5773: @app.post("/api/convert_heic")
       5774: async def convert_heic_endpoint(file: UploadFile = File(...)):
       ```
     - `POST /api/analyze/grade-coin` (`main.py:6726-6727`):
       ```python
       6726: @app.post("/api/analyze/grade-coin")
       6727: async def grade_coin(
       ```
     - `POST /api/identify-world-item` (`main.py:1317-1318`):
       ```python
       1317: @app.post("/api/identify-world-item")
       1318: async def identify_world_item(
       ```
     - `POST /api/import/upload` (`main.py:7396-7397`).

4. **Current `origin/dev` (`32d4b42e`) vs Proposed Post-`NET-706 R5` Privacy Text (`Section 10.1`):**
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_mobile/web/privacy.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/privacy.html#L324-L326):
     ```html
     324:         <h2>3. Data Sharing &amp; Third-Party Service Providers</h2>
     325:         <p>We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
     ```
   - Verbatim from `origin/dev` (`32d4b42e`) [`numista_mobile/lib/screens/privacy_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/privacy_screen.dart#L137-L140):
     ```dart
     137:             _buildSection(
     138:               'Data Storage & Security',
     139:               'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
     140:             ),
     ```
   - Label `"We do not sell, rent, or trade your personal data or coin collection details to third parties."` as the **proposed post-`NET-706 R5` update** alongside the current `origin/dev` text above.

---

### SHOULD-FIX Items (`SF1`–`SF5`) Turnkey Resolutions for `R2`

- **`SF1` (Full-History Secret Scan):** Replace `--no-git` and `--since-commit 9f04550a` in Sections 7.2 and 11 with full-repository git history scanning across all branches:
  ```bash
  gitleaks git --verbose --redact
  trufflehog git file://. --only-verified
  ```
- **`SF2` (Unverified Cost Figures):** Mark Document AI (`$1.50/1,000 pages`) and Identity Platform MFA (`$0.01–$0.06`) cost estimates in Section 4.1 and Section 12 as `TBD (pending volume projection and official GCP pricing page citation)`.
- **`SF3` (Comprehensive EXIF Stripper Across `JPEG`, `PNG`, `WEBP`, `HEIC`):** Use a single signature `def _sanitize_image_exif(raw_bytes: bytes) -> bytes:` in both prose and code; convert `HEIC`/`HEIF` first via `_convert_heic_to_jpeg(raw_bytes)` (`origin/dev:numista_backend/main.py:4295-4313`), extract `orientation = img.getexif().get(0x0112)`, build a fresh `clean_exif = PILImage.Exif()` with only `clean_exif[0x0112] = orientation` (stripping **all** GPS `0x8825`, MakerNote `0x927C`, UserComment `0x9286`, SerialNumber `0xA431`, LensSerialNumber `0xA435`, DateTimeOriginal `0x9003`, Artist `0x013B`, Copyright `0x8298`, XMP, and PNG `tEXt`/`iTXt`/`zTXt` chunks), and re-encode cleanly for `JPEG`, `PNG`, and `WEBP`.
- **`SF4` (`public_wishlists` `owner_alias` Already Exists on `origin/dev:numista_backend/main.py:12743-12755`):**
  - Verbatim from `origin/dev` (`32d4b42e`) [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L12733-L12755):
    ```python
    12733: @app.post("/api/wishlist/create-share")
    12734: async def create_wishlist_share(req: WishlistShareCreateRequest, decoded_user: dict = Depends(verify_token)):
    ...
    12743:         snapshot = {
    12744:             "token": token,
    12745:             "owner_email": req.user_email,
    12746:             "owner_alias": req.owner_alias or "Numista Collector",
    12747:             "created_at": datetime.utcnow().isoformat(),
    12748:             "items": req.items,
    12749:             "reserved_items": {},
    12750:             "reservation_details": {},
    12751:         }
    12752: 
    12753:         if db is not None:
    12754:             db.collection("public_wishlists").document(token).set(snapshot)
    ```
  - Note that `"owner_alias"` is **already present on line `12746`**! The exact diff is simply to remove `"owner_email": req.user_email,` (line `12745`), add `"owner_uid": decoded_user.get("uid"),` for server-side ownership tracking without email exposure, and include a dry-run audit step to inspect existing `/public_wishlists/*` docs for any legacy `owner_email` field.
- **`SF5` (`[PROPOSED]` Labels):** Explicitly mark all new files and endpoints (`numista_mobile/lib/widgets/mfa_security_modal.dart` `[PROPOSED]`, `numista_mobile/test_rules/firestore_storage_security.test.ts` `[PROPOSED]`, `numista_backend/_scripts/dry_run_receipt_redaction_audit.py` `[PROPOSED]`, `DELETE /api/user/account` `[PROPOSED]`) as `[PROPOSED]`.

---

## 3. Verdict

**75 / 100 — REVISE.** Ready for `AG CoS v4` (`ba2bfdb2`) to incorporate the turnkey verbatim citations above into `SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md`.
