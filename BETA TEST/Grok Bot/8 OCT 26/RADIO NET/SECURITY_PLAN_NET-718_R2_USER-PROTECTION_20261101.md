# NET-718 R2 - Security & User-Protection Plan (Plan-Only)
**Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)  
**Date:** 2026-11-01 18:25 EST  
**Branch & Target:** `origin/p7-v8.9` docs-only (code target `origin/dev 32d4b42e`)  
**Mode:** PLAN-ONLY (Zero code edits, zero builds, zero deploys, zero GCS/Firestore writes)  
**Revision:** R2 Fix-Only (Incorporate Grok CoS score 74 [`COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md`] and Argon score 75 [`GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md`] turnkey citations on `origin/dev 32d4b42e`)  

---

## Executive Summary & Founder Goal (The Aunt Janet Doctrine)

Numista.AI is built to protect physical coin collectors and their families. The average user has thousands or tens of thousands of dollars of tangible wealth stored in physical locations (home safes, bank safe deposit boxes, insured vaults).
If an attacker breaches a digital coin inventory and correlates coin values with a real-world home address, physical burglary or home invasion becomes an existential danger.

**The Aunt Janet Security Doctrine:**
1. *No postal addresses ever enter Numista.AI systems under any circumstance.*
2. *Values are strictly private to the authenticated owner by default.*
3. *Receipt and invoice uploads are redacted in-memory prior to any persistence—no unredacted original exists anywhere, including temporary storage or raw folders.*
4. *Photos never leak GPS coordinates or device identifiers.*
5. *High-value collections are guarded by multi-factor authentication.*
6. *Data minimization and immediate, unrecoverable account deletion are respected unconditionally.*

---

## 1. No Postal Addresses Anywhere [Spec Item 1]

### 1.1 Current State Audit (origin/dev 32d4b42e)
* **Codebase Verbatim Citations:**
  * `scan_service/main.py:695`: Default storage location options are explicitly labeled:
    ```python
    695:     locations = ["Primary Storage / Home Safe", "Bank Safe Deposit Box", "Insurance Vault"]
    ```
  * `numista_mobile/lib/services/estate_fiduciary_service.dart:71`: Uses abstract location strings:
    ```dart
    71:       'storage_location': 'Primary Storage / Home Safe',
    ```
  * `numista_mobile/lib/models/estate_models.dart:215, 262, 288`: Models physical storage as abstract labels (`safeBox`, `bankVault`), never street addresses.
  * `numista_mobile/lib/screens/estate_planning_screen.dart:608-610, 4076, 4196`: UI form inputs for storage location use free-text with hint text `"e.g., Safe Box A, Bank of America Vault"`.
  * `numista_mobile/web/add_coins.html:1315, 1331-1332`: Helper comments demonstrate masking PII (`maskPII`) and default location `"Safe Box A"`.
* **State Assessment:** Numista.AI currently requests zero postal address fields in any user profile, coin item, or estate document schema.

### 1.2 Gap
In `estate_planning_screen.dart:608-610`, storage location fields allow arbitrary free-form text. A non-technical user (or heir) could inadvertently type their full street address (e.g., *"123 Main St, Springfield, Safe in basement"*).

### 1.3 Proposed Fix [PROPOSED]
1. **Frontend Disallowed Pattern Validation (`numista_mobile/lib/utils/pii_sanitizer.dart` [PROPOSED]):**
   * Introduce a client-side regex validator that flags text resembling US/International street addresses (`\d{1,5}\s+[A-Za-z0-9\.\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Way|Lane|Ln|Court|Ct|Circle|Cir)\b` or standard ZIP code / postal patterns `\b\d{5}(?:-\d{4})?\b`).
   * If detected, block form submission and display an immediate warning modal:  
     > *"For your physical safety, never enter your street address or postal location into Numista.AI. Use abstract labels only (e.g., 'Home Safe', 'Safety Deposit Box #4')."*
2. **Backend Ingress Filter (`numista_backend/main.py` [PROPOSED]):**
   * Sanitize location fields on all coin/estate update routes. Any string matching an address pattern is rejected with HTTP 422: `{"error": "Physical addresses strictly prohibited for user safety"}`.

### 1.4 Verification & Tests
* Unit test `test_disallowed_address_patterns()`: Feed 20 diverse US/UK/Canadian address strings into the validator. Assert 100% rejection.
* Verify abstract phrases pass cleanly: `"Home Safe A"`, `"First National Bank Box 302"`, `"Office Lockbox"`.

### 1.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 3 hours
* **Risk:** Low. No breaking schema changes; abstract labels remain fully supported.

---

## 2. Auto-Redaction of Receipt & Invoice Scans [Spec Item 2]

### 2.1 Current State Audit (origin/dev 32d4b42e)
* **Direct-to-GCS Signed URL Ingress Bypasses:**
  * `POST /api/import/start` (`origin/dev:numista_backend/main.py:7499-7548`): Generates direct V4 signed `PUT` URLs pointing directly to `f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"`:
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
  * `POST /v1/import/get_upload_url` (`numista_backend/routes/import_routes.py:46-66`): Generates direct V4 signed URLs:
    ```python
    46: @router.post("/get_upload_url")
    47: async def get_upload_url(req: UploadUrlRequest, user_token: dict = Depends(verify_firebase_token)):
    ...
    55:     blob_name = f"imports/{user_id}/{uuid.uuid4().hex}_{req.filename}"
    56:     blob = bucket.blob(blob_name)
    ```
* **All Six `/raw/` GCS Writes in `origin/dev:numista_backend/main.py`:**
  * Line 7377: `_save_to_gcs`: `blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"`
  * Line 7434: `POST /api/import/upload`: `blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"`
  * Line 7532: `POST /api/import/start`: `blob_path = f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"`
  * Line 7931: `_execute_import_process_worker`: `blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"`
  * Line 8405: Partner blob: `partner_blob = bucket.blob(f"{user_email}/imports/{session_id}/raw/{partner_safe}")`
  * Line 8489: Partner image: `gcs_path_img = f"gs://{IMPORT_BUCKET}/{user_email}/imports/{session_id}/raw/{safe_name}"`
* **Existing Document AI Client in `origin/dev:numista_backend/main.py`:**
  * Document AI is **ALREADY** imported and active:
    ```python
    19: from google.cloud import documentai
    ...
    2047:         doc_client = documentai.DocumentProcessorServiceClient()
    2048:         name = doc_client.processor_path( DOC_AI_PROJECT_ID, DOC_AI_LOCATION, DOC_AI_PROCESSOR_ID)
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

### 2.2 Gap
1. Direct signed-URL uploads bypass backend memory completely, writing raw unredacted receipts/invoices containing names, street addresses, and payment card numbers straight into GCS.
2. The `/raw/` GCS prefix violates Founder Eric's core invariant: *"No unredacted original anywhere, including temp storage or raw folders."*

### 2.3 Proposed Fix [PROPOSED]
1. **Deprecate Direct-to-GCS Signed URL Ingress for Documents:**
   * In `POST /api/import/start` (`main.py:7528-7545`), disable direct signed PUT URLs. Return `upload_urls[f_meta.name] = "/api/import/upload"`.
   * In `routes/import_routes.py:46-66`, deprecate direct signed URLs for document uploads. All byte streams must route through backend memory.
2. **In-Memory Streaming Redaction Pipeline (Zero Raw Storage Invariant):**
   * In `POST /api/import/upload` (`main.py:7396`) and `_save_to_gcs` (`main.py:7373`):
     * Hold incoming bytes strictly in memory (RAM buffer `io.BytesIO`, capped at 32MB).
     * Pass in-memory bytes through `_sanitize_image_exif()` first.
     * Reuse the existing synchronous stateless Document AI client (`main.py:5008-5018`, `client.process_document` with `raw_document` in-memory) to detect bounding boxes for: `billing_address`, `shipping_address`, `recipient_name`, `customer_name`, `phone_number`, `credit_card_number`.
     * Render solid opaque black rectangles (`#000000`) over 100% of detected PII bounding boxes.
     * Replace `/raw/` prefix with `/redacted/` across lines 7377, 7434, 7532, 7931, 8405, 8489.
     * Write ONLY the redacted bytes to GCS: `{email}/imports/{session_id}/redacted/{safe_name}`.
     * Discard raw unredacted bytes from RAM without writing to `/tmp`, Cloud Run logs, or GCS staging.
3. **Data Logging Invariant:**
   * Logger calls in `main.py` must NEVER log raw OCR text strings, customer names, or addresses. Log ONLY entity counts, confidence scores, and bounding box counts.
   * Document AI enterprise processor runs under Google Cloud Enterprise Data Processing Addendum terms with zero human-in-the-loop review and zero retention.
4. **Historical Backfill Script (`numista_backend/_scripts/dry_run_receipt_redaction_audit.py` [PROPOSED]):**
   * **Phase A (DRY-RUN ONLY):** Scans historical objects under `gs://numista-vault-imports/*/imports/*/raw/*`.
   * **Safe Dry-Run Logging Rule:** The report `RECEIPT_REDACTION_AUDIT_REPORT.json` records **only** `blob_path_hash` (or object path), `page_count`, `detected_entity_types`, `entity_counts`, `confidence_scores`, and `bounding_boxes` (`[x0, y0, x1, y1]`) — **ZERO extracted PII text strings**.
   * **Phase B (Execution - Requires Founder Eric Typed YES):** Overwrites objects with blackened versions, purges noncurrent object generations (`bucket.list_blobs(versions=True)` $\rightarrow$ `bucket.delete_blob(...)`), and verifies soft-delete retention so unredacted prior generations cannot be recovered.

### 2.4 Verification & Tests
* Unit test with synthetic receipts: verify solid black fill over coordinates, re-OCR shows 0.0% PII text, assert zero files written to `/raw/`.

### 2.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 6 hours
* **Risk:** Medium. Fallback to page-level rasterization ensures zero text leak in complex PDF vector layers.

---

## 3. Universal EXIF / GPS Geolocation Stripping [Spec Item 3]

### 3.1 Current State Audit (origin/dev 32d4b42e)
* `numista_backend/main.py:4295-4313` (`_convert_heic_to_jpeg`):
  ```python
  4295: def _convert_heic_to_jpeg(raw_bytes: bytes) -> tuple:
  ...
  4306:             exif_data = img.getexif()
  4307:             for gps_tag in [0x8825]:  # GPSInfo
  4308:                 exif_data.pop(gps_tag, None)
  4309:             buf_out = BytesIO()
  4310:             exif_bytes = exif_data.tobytes() if exif_data else b''
  4311:             img.save(buf_out, format='JPEG', quality=90, exif=exif_bytes)
  4312:             return buf_out.getvalue(), 'image/jpeg'
  ```
* **Real Central Upload & Photo Ingest Endpoints on `origin/dev 32d4b42e`:**
  * Central GCS helper: `_upload_to_gcs` (`main.py:4282-4293`)
  * `POST /api/identify_coin_photo` (`main.py:6371-6372`)
  * `POST /api/identify_group_photo` (`main.py:5796-5797`)
  * `POST /api/analyze_binder_scan` (`main.py:4621-4622`)
  * `POST /api/analyze_checklist` (`main.py:5104-5105`)
  * `POST /api/convert_heic` (`main.py:5773-5774`)
  * `POST /api/analyze/grade-coin` (`main.py:6726-6727`)
  * `POST /api/identify-world-item` (`main.py:1317-1318`)
  * `POST /api/import/upload` (`main.py:7396-7397`)
  * `POST /upload_document` (`routes/scan_routes.py:84-90`)

### 3.2 Gap
1. `_convert_heic_to_jpeg` takes 1 parameter (`raw_bytes: bytes`), only handles HEIC, and only pops `0x8825` (GPSInfo).
2. Direct JPEG, PNG, and WebP uploads entering photo-ingest routes are never stripped of device serial numbers (`0xA431`), HostComputer (`0x014C`), Software (`0x0131`), or Artist (`0x013B`).

### 3.3 Proposed Fix [PROPOSED]
1. **Universal Server-Side Metadata Sanitizer (`def _sanitize_image_exif(raw_bytes: bytes) -> bytes:` [PROPOSED]):**
   * If HEIC/HEIF: Convert first via `_convert_heic_to_jpeg(raw_bytes)` (`main.py:4295-4313`).
   * Extract image orientation (`orientation = img.getexif().get(0x0112)`).
   * Construct a fresh, empty EXIF container: `clean_exif = PILImage.Exif(); clean_exif[0x0112] = orientation`.
   * Completely strips: `GPSInfo (0x8825)`, `Make (0x010F)`, `Model (0x0110)`, `Artist (0x013B)`, `Copyright (0x8298)`, `HostComputer (0x014C)`, `Software (0x0131)`, `BodySerialNumber (0xA431)`, `LensSerialNumber (0xA435)`, `UserComment (0x9286)`, `MakerNote (0x927C)`, `DateTimeOriginal (0x9003)`.
   * For PNG: Drops all `tEXt`, `zTXt`, `iTXt` metadata chunks.
   * For WebP: Removes EXIF / XMP chunks.
   * Wire `_sanitize_image_exif` directly into `_upload_to_gcs` (`main.py:4282`) and all photo-ingest routes.
2. **Client-Side Camera Interceptor (`numista_mobile/lib/services/camera_capture_service_web.dart` [PROPOSED]):**
   * Renders camera stream to offscreen `<canvas>` and exports `canvas.toBlob('image/jpeg', 0.92)` (clean pixel matrix with zero device metadata).

### 3.4 Verification & Tests
* Automated test suite `test_universal_exif_sanitizer()` across JPEG, PNG, WebP, and HEIC: assert orientation preserved, zero GPS tags, zero serial numbers, zero metadata chunks.

### 3.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 3 hours
* **Risk:** Low. Pure byte sanitization with orientation preservation.

---

## 4. Values Private by Default [Spec Item 4]

### 4.1 Current State Audit (origin/dev 32d4b42e)
* **Wishlist Sharing (`POST /api/wishlist/create-share` at `numista_backend/main.py:12733-12755`):**
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
  * Note: `numista_mobile/firestore.rules:251` gives `/public_wishlists/{token}` `allow get: if true;`. Writing `owner_email` into this document leaks the collector's real email address to anyone reading the public link!
  * Note that `"owner_alias"` is **ALREADY present on line 12746**!
* **Estate Attorney Portal (`numista_mobile/lib/screens/attorney_portal_screen.dart:520, 704`):**
  * Suppresses speculative collector gain/loss formulas.

### 4.2 Gap
1. `main.py:12745` writes `owner_email` into `/public_wishlists/{token}`, which is publicly readable by unauthenticated users per `firestore.rules:251`.
2. Existing `/public_wishlists` documents in production Firestore may contain stored `owner_email` values.

### 4.3 Proposed Fix [PROPOSED]
1. **Drop `owner_email` from Public Wishlist Snapshots:**
   * In `main.py:12743-12751`, remove `"owner_email": req.user_email,` (line 12745).
   * Replace with `"owner_uid": decoded_user.get("uid"),` for server-side audit without email exposure.
   * Keep `"owner_alias": req.owner_alias or "Numista Collector"` (line 12746).
2. **Historical Wishlist Email Cleansing Script (`dry_run_wishlist_email_audit.py` [PROPOSED]):**
   * Dry-run scan across `/public_wishlists` counting documents with `owner_email` present.
   * Upon Eric's typed YES, update documents to delete the `owner_email` field.

### 4.4 Verification & Tests
* Test `POST /api/wishlist/create-share`: Query `/public_wishlists/{token}` in Firestore; verify key `'owner_email'` is completely absent.

### 4.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 2 hours
* **Risk:** Low. Pure removal of leaked field; `owner_alias` is preserved.

---

## 5. 2FA Prompted Above Collection-Value Threshold [Spec Item 5]

### 5.1 Current State Audit (origin/dev 32d4b42e)
* `numista_mobile/lib/services/auth_service.dart:7-23`: Supports email/password and PIN lock (`setPin`, `verifyPin`).
* `numista_mobile/lib/screens/login_screen.dart:127, 154`: Handles standard Firebase Auth credentials.
* No TOTP / SMS 2FA prompt exists tied to portfolio valuation thresholds.

### 5.2 Gap
High-value vaults ($10,000 to $100,000+) are protected solely by single-factor email/password or local device PIN.

### 5.3 Proposed Fix [PROPOSED]
1. **[ERIC DECISION 1 - OPEN QUESTION]: Collection Value Threshold for 2FA:**
   * Option A: Mandatory 2FA prompt when total collection value exceeds **$10,000**.
   * Option B: Mandatory 2FA prompt when total collection value exceeds **$25,000**.
   * Option C: Voluntary opt-in with persistent banner recommendations above $10,000.
   *(This remains an open decision for Founder Eric; implementation parameterized via `REMOTE_CONFIG_2FA_THRESHOLD_USD`).*
2. **Implementation Flow [PROPOSED]:**
   * **Client Evaluation (`home_dashboard.dart` / `settings_screen.dart`):** When total portfolio value crosses threshold, trigger `MfaSecurityModal` [PROPOSED].
   * **Firebase Authentication Multi-Factor Auth (Identity Platform MFA):**
     * Supports TOTP (Google Authenticator / Authy) or SMS verification.
     * Costs: `[TBD (pending volume projection and official GCP pricing page citation)]`.

### 5.4 Verification & Tests
* Flutter widget test for `MfaSecurityModal`: Mock portfolio valuation > threshold; assert dialog appears prompting TOTP enrollment.

### 5.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 5 hours
* **Risk:** Low-Medium. Keep optional/grace period so legitimate collectors are never locked out of their vault.

---

## 6. Firestore & Storage Security Rules Audit [Spec Item 6]

### 6.1 Current State Audit (origin/dev 32d4b42e)
* **Authoritative Deployed Ruleset (`numista_mobile/firebase.json:1-6`):**
  ```json
  1: {
  2:   "firestore": {
  3:     "rules": "firestore.rules",
  4:     "indexes": "firestore.indexes.json"
  5:   },
  6:   "hosting": {
  ```
  * Active CI deployment target in `.github/workflows/deploy-production.yml:68-71`:
    ```yaml
    - name: Deploy Firestore rules
      working-directory: numista_mobile
      run: firebase deploy --only firestore:rules --project studio-9101802118-8c9a8
    ```
  * By contrast, `numista_backend/firestore.rules:1-11` is an undeployed reference mirror (`numista_backend/firebase.json` has only `"functions"`):
    ```javascript
    1: // ╔══════════════════════════════════════════════════════════════════════╗
    2: // ║  ⚠️  NOT DEPLOYED — REFERENCE MIRROR ONLY                          ║
    3: // ║  The DEPLOYED rules are in: numista_mobile/firestore.rules         ║
    4: // ║  (deployed via `firebase deploy --only firestore:rules` from       ║
    5: // ║   the numista_mobile/ directory, where firebase.json has the       ║
    6: // ║   "firestore" key).                                                ║
    7: // ╚══════════════════════════════════════════════════════════════════════╝
    ```
* **Exact Verbatim Rules from `origin/dev 32d4b42e:numista_mobile/firestore.rules`:**
  * Lines 13-15 (`isOwner(email)`):
    ```javascript
    13:     function isOwner(email) {
    14:       return request.auth != null && (request.auth.token.email == email || request.auth.uid == email);
    15:     }
    ```
  * Lines 40-67 (`/users/{email}/coins/{coinId}`):
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
  * Lines 247-254 (`/public_wishlists/{token}`, NOT line 182 which is `/config`):
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
  * Lines 277-281 (`/family_groups/{familyGroupId}`, NOT line 190 which is `/coin_image_index`):
    ```javascript
    277:     // Family Trust Inheritance Sync (Phase 3.4)
    278:     match /family_groups/{familyGroupId} {
    279:       allow read: if request.auth != null;
    280:       allow write: if request.auth != null && request.auth.uid == resource.data.primary_owner_uid;
    281:     }
    ```

### 6.2 Gap
1. **Critical Family Groups Data Leak (`firestore.rules:278-279`):**
   `allow read: if request.auth != null;` permits ANY signed-in user in the entire application to query and read any family group document, exposing member email addresses and family vault configurations!
2. **Public Wishlists Flaws (`firestore.rules:252-253`):**
   - Line 253 `.hasAny(...)`: Evaluates to `true` as long as *at least one* of the two reservation keys is modified, allowing an unauthenticated attacker to overwrite `items`, `owner_alias`, etc., in the same update!
   - Line 252 `allow create`: Allows arbitrary client creation bypassing backend sanitation.

### 6.3 Proposed Fix [PROPOSED]
1. **Harden `/family_groups/{familyGroupId}` (`firestore.rules:278-281`):**
   ```firestore
   match /family_groups/{familyGroupId} {
     allow read: if request.auth != null 
                 && (request.auth.uid == resource.data.primary_owner_uid 
                     || request.auth.token.email in resource.data.member_emails);
     allow write: if request.auth != null && request.auth.uid == resource.data.primary_owner_uid;
   }
   ```
2. **Harden `/public_wishlists/{token}` (`firestore.rules:250-254`):**
   ```firestore
   match /public_wishlists/{token} {
     allow get: if true;
     allow create: if false; // Cloud Run Admin SDK only via POST /api/wishlist/create-share
     allow update: if request.resource.data.diff(resource.data).affectedKeys().hasOnly(['reserved_items', 'reservation_details']);
     allow delete: if false;
   }
   ```

### 6.4 Verification & Tests
* Jest / Firestore Rules Unit Tests (`numista_mobile/test_rules/firestore_storage_security.test.ts` [PROPOSED]):
  * Assert user B cannot read user A's `/family_groups` document (returns permission-denied).
  * Assert client cannot create `/public_wishlists` directly (returns permission-denied).
  * Assert unauthenticated user modifying `items` alongside `reserved_items` is rejected by `.hasOnly(...)`.

### 6.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 2.5 hours
* **Risk:** Low. Prevents cross-tenant data sniffing without affecting valid members.

---

## 7. Secrets Exclusively in Secret Manager & Leaked-Key Scan [Spec Item 7]

### 7.1 Current State Audit (origin/dev 32d4b42e)
* `numista_backend/main.py:11977-11986`:
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
* `numista_backend/routes/payment_routes.py:172-176`:
  ```python
  172:     payload = await request.body()
  173:     sig_header = request.headers.get("stripe-signature")
  174:     webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
  ```
* `numista_backend/stripe_config.py:28-31`:
  ```python
  28:     # Keys come exclusively from environment variables / Secret Manager.
  29:     pub_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
  30:     sec_key = os.environ.get("STRIPE_SECRET_KEY")
  ```
* `functions/feedbackIntelligence.js:21`: Directly imports `@google-cloud/secret-manager` (`SecretManagerServiceClient`).

### 7.2 Gap
Ensure zero API keys or credentials exist anywhere in full git history across all branches.

### 7.3 Proposed Fix [PROPOSED]
1. **Full-History Secret Scanning Across All Branches:**
   ```bash
   gitleaks git --verbose --redact
   trufflehog git file://. --only-verified
   ```
   Must exit with code 0 (zero leaks found across entire repository history).
2. **Pre-Commit & CI Secret Shield:** Enforce `.pre-commit-config.yaml` with Gitleaks hook in GitHub Actions.

### 7.4 Verification & Tests
* Terminal execution of `gitleaks git --verbose --redact` exits with code 0.

### 7.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 1.5 hours
* **Risk:** Low. Hygiene and compliance guarantee.

---

## 8. Meta Pixel Event Safety & Zero-PII Invariant [Spec Item 8]

### 8.1 Current State Audit & NET-706 Reconciliation
* In `NET-706 R5` (`PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md`, scored 97 PASS):
  * Meta Pixel is currently commented out in `web/index.html:43-56`.
  * Verbatim from `PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md:160-166`:
    ```dart
    160:       if (kIsWeb) {
    161:         js.context.callMethod('fbq', ['track', 'Purchase', js.JsObject.jsify({
    162:           'value': amountUsd,
    163:           'currency': 'USD',
    164:         })]);
    165:         prefs.setBool('meta_purchase_fired_$sessionId', true);
    166:       }
    ```
  * `amountUsd` is verified server-side via `/api/stripe/verify-session`.
  * Plan v3.2 canonical prices are:
    * Monthly subscription: **$4.99** (Copper)
    * Silver subscription: **$8.99**
    * Platinum subscription: **$10.99**
    * Gold subscription: **$15.99**
    * AI Top-Up: **$5.00**
    * Annual / Lifetime exports: **$29.94 – $95.94**
    *(Note: `$12.99` is an invented price that does not exist in v3.2 and was fully expunged).*

### 8.2 Gap
Strict invariant needed to ensure Meta Pixel never receives customer names, emails, collection totals, or coin metadata.

### 8.3 Reconciliation & Invariant Specification [PROPOSED]
1. **[ERIC DECISION 2 - OPEN QUESTION]: Purchase Event Value Parameter:**
   * Option A (Standard eCommerce): Pass verified subscription amount (`'value': amountUsd, 'currency': 'USD'`).
   * Option B (Ultra-Minimalist Privacy): Omit `'value'` entirely (`js.context.callMethod('fbq', ['track', 'Purchase']);`), logging only event occurrence with zero financial figures transmitted to Meta.
2. **Absolute Zero-PII Invariant on Meta Pixel:**
   * Meta Advanced Matching (`fbq('init', PIXEL_ID, { em: user_email })`) is **PERMANENTLY DISABLED**.
   * Under no circumstances shall `fbq` be called with:
     * User email or user UID
     * User real name or postal address
     * Coin titles, grades, denominations, or mint marks
     * Total vault / collection valuation.

### 8.4 Verification & Tests
* Playwright E2E Test (`test_meta_pixel_zero_pii.spec.ts` [PROPOSED]):
  * Intercept all requests to `https://www.facebook.com/tr/`.
  * Assert regex matches: zero email strings, zero dollar figures exceeding verified subscription tiers, zero coin identifiers.

### 8.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 2 hours
* **Risk:** Low. Complete architectural isolation of ad tracking.

---

## 9. Data Minimization & Full Account Deletion [Spec Item 9]

### 9.1 Current State Audit (origin/dev 32d4b42e)
* Soft-delete functionality exists for coins (`is_archived: true`).
* No unified endpoint exists for a user to purge their entire account, coins, receipts, images, and estate records in a single transaction.

### 9.2 Gap
Collectors who decide to leave the platform must have the absolute guarantee that their physical coin catalog and scanned documents are permanently erased from all databases and cloud storage.

### 9.3 Proposed Fix [PROPOSED]
1. **`DELETE /api/user/account` [PROPOSED NEW ENDPOINT]:**
   * Authenticated route requiring active ID token verification and re-authentication (PIN / password confirmation).
   * Transactional cascading purge:
     1. Deletes all documents in `/users/{email}/coins/*`.
     2. Deletes all documents in `/users/{email}/estate_reports/*`.
     3. Deletes all documents in `/users/{email}/import_sessions/*`.
     4. Deletes root document `/users/{email}`.
     5. Purges all GCS objects in `gs://numista-vault/{email}/**` and `gs://numista-vault-imports/{email}/**`.
     6. Calls Firebase Admin Auth SDK `auth.delete_user(uid)`.
2. **Client UI (`settings_screen.dart` [PROPOSED]):**
   * Adds *"Delete Account & Purge All Vault Data"* button with red double-confirmation dialog and mandatory password re-entry.

### 9.4 Verification & Tests
* Integration test `test_user_account_cascading_deletion()`: Seed test user with coins, receipts, and estate report; call `DELETE /api/user/account`; assert Firestore empty, GCS blobs 404, Auth returns user-not-found.

### 9.5 Ownership, Effort & Risk
* **Owner:** AG CoS
* **Effort:** 4 hours
* **Risk:** High (data destruction). Must require explicit re-authentication and double confirmation.

---

## 10. Site Copy Proposal: Plain-Language Security Promise [Spec Item 10]

### 10.1 Current State Audit (origin/dev 32d4b42e)
* `numista_mobile/web/privacy.html:324-326` currently reads:
  ```html
  324:         <h2>3. Data Sharing &amp; Third-Party Service Providers</h2>
  325:         <p>We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
  ```
* `numista_mobile/lib/screens/privacy_screen.dart:137-140` currently reads:
  ```dart
  137:             _buildSection(
  138:               'Data Storage & Security',
  139:               'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
  140:             ),
  ```
* *(Note: When NET-706 R5 Meta Pixel is enabled, Privacy Policy disclosures will be updated per NET-706 R5 specifications [PROPOSED after NET-706 R5 Meta Pixel Enablement]).*

### 10.2 Proposed Site Copy [ERIC DECISION TO APPROVE]

#### Placement A: Landing Page / Marketing Hero (`web/index.html` & `home_dashboard.dart`)
> **"Built for Collectors Who Value Real-World Privacy."**  
> *Your coin collection is tangible wealth. We treat it that way.*  
> • **No Addresses, Ever:** We never ask for, store, or accept your home address or physical storage location.  
> • **Automatic Receipt Scrubbing:** Receipt and invoice scans are redacted in-memory before saving—names, addresses, and card numbers are blacked out forever.  
> • **Zero Geolocation:** GPS coordinates and camera metadata are stripped from your coin photos at upload.  
> • **Private by Default:** Your inventory and collection values are visible only to you.

#### Placement B: Privacy Policy (`web/privacy.html` & `privacy_screen.dart`)
> **Physical Asset Protection Guarantee:**  
> *"Numista.AI recognizes that coin inventories represent physical, high-value assets. To protect our collectors against physical security risks, our platform enforces strict data minimization: we do not store physical street addresses, we strip GPS metadata from all images, and all document uploads undergo automated PII redaction prior to cloud storage."*

#### Placement C: Estate Planning Screen (`estate_planning_screen.dart`)
> **"Location Privacy Notice:** *When noting where coins are stored, use descriptive labels like 'Safe Deposit Box A' or 'Home Fire Safe'. Never enter your street address or postal location into Numista.AI."*

---

## 11. Consolidated Implementation Roadmap & Estimates

| Phase | Milestone / Task | Spec Item | Proposed Artifact / Route | Est. Hours | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | Rules Hardening | Item 6 | `firestore.rules:247-254, 277-281` | 2.5 h | Low |
| **Phase 2** | Drop Email from Wishlists | Item 4 | `main.py:12745`, `dry_run_wishlist_email_audit.py` [PROPOSED] | 2.0 h | Low |
| **Phase 3** | Universal EXIF Stripping | Item 3 | `_sanitize_image_exif` across photo routes | 3.0 h | Low |
| **Phase 4** | In-Memory Receipt Redaction & Ingress Fix | Item 2 | `main.py:7528` signed-URL fix, in-memory blackout | 6.0 h | Medium |
| **Phase 5** | Address Prevention Validation | Item 1 | `pii_sanitizer.dart` [PROPOSED], `main.py` filter | 3.0 h | Low |
| **Phase 6** | Secret Shield (Gitleaks Full History) | Item 7 | `gitleaks git --verbose --redact`, pre-commit hook | 1.5 h | Low |
| **Phase 7** | Account Deletion Pipeline | Item 9 | `DELETE /api/user/account` [PROPOSED NEW ENDPOINT] | 4.0 h | High |
| **Phase 8** | High-Value 2FA Modal | Item 5 | `MfaSecurityModal` [PROPOSED] (Pending Eric Threshold) | 5.0 h | Medium |
| **Phase 9** | Meta Pixel Safety Verification | Item 8 | Playwright zero-PII interceptor test | 2.0 h | Low |
| **Phase 10** | Site Copy Update | Item 10 | `web/index.html`, `privacy.html`, `estate_planning_screen.dart` | 1.5 h | Low |
| **Total** | **All 10 Spec Items** | | | **30.5 h** | |

*Cost Implications:* Document AI and Firebase Identity Platform MFA usage costs are marked `[TBD (pending volume projection and official GCP pricing page citation)]`.

---

## 12. Lessons & Self-Improvement

1. **Verify Line Numbers Byte-for-Byte Against `origin/dev`:**
   * In R1, local working tree line shifts caused line citations for `firestore.rules` (e.g. lines 182 and 190) to mismatch `origin/dev 32d4b42e` (`public_wishlists` is lines 247-254, `family_groups` is lines 277-281, and `isOwner` is lines 13-15).
   * In R2, every rule line range and python route line was verified directly by line-by-line inspection against `origin/dev 32d4b42e` and backed by verbatim code blocks per Rule 6(a).
2. **Audit Every Ingress Path for Storage Invariants:**
   * In R1, focusing only on `/api/import/upload` missed `/api/import/start` (`main.py:7499-7548`) and `/v1/import/get_upload_url` (`routes/import_routes.py:46-66`), which generated GCS v4 signed URLs allowing direct client uploads of raw files to GCS.
   * In R2, every upload route was audited and traced to ensure zero raw unredacted bytes can ever touch cloud storage or temporary files.
3. **Never Invent Prices, Routes, or Mechanism Details:**
   * Never invent placeholder figures like `$12.99`. Always check actual v3.2 subscription tiers ($4.99, $8.99, $10.99, $15.99, $5.00, $29.94–$95.94).
   * Accurately reflect Cloud Run environment variable secret mounting rather than claiming direct Secret Manager Python calls in `main.py:60-120`.

---

## 13. Next Steps & Baton Protocol

1. **Distribute R2 Plan:** File across `RADIO NET/`, `BATONS/`, `INBOX/`, `OUTBOX/`, and `For SAG/`.
2. **File Radio Over:** Issue `RADIO_OVER_NET-724_AGCOS-to-ALL_NET718-R2-PLAN-FILED_20261101.md`.
3. **Open Review Baton:** Open `BATON_NET-723_GROKCOS-ARGON_NET-718-R2-REVIEW_20261101.md` assigning review to Grok CoS and Argon.
4. **Docs Commit:** Commit and push docs to `origin/p7-v8.9`.
5. **Stand By / Advance Queue:** Await Grok CoS / Argon scoring on NET-718 R2 ($\ge 95$ target) while advancing to **NET-647 R2.8.10 Mint FAIL-FIX Plan**, followed by **NET-705 US Catalog Site Plan**.
