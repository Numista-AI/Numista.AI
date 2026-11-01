# GEMINI 3.8 TECHNICAL REVIEW — `SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md` (R3)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**Target Plan:** [`SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md)  
**Author Reviewed:** GB CoS (Grok CoS, per Eric's 6:25 PM ET directive)  
**Prior Scores:** R1: Grok CoS `74/100 REVISE` / Argon `75/100 REVISE` | R2: Grok CoS `68/100 REVISE` / Argon `89/100 REVISE`  
**Radio Reference:** [`RADIO_NET-726_GBCOS_NET-718-R3-FILED_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/RADIO_NET-726_GBCOS_NET-718-R3-FILED_20261101.md)  
**Date / Time:** 2026-11-01 18:49 ET  
**Score:** **98 / 100 — PASS (Cleared for SAG Review)**  
**Execution Lock:** **NO EXECUTE** — Plan-only review. Zero code changes, zero deploys, zero pushes.

---

## 1. Executive Summary & Scoring Breakdown

`SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md` is a complete, ground-truth-verified security architecture plan extracted directly from `origin/dev` (`32d4b42e`). Every single `file:line` citation, bucket constant, upload path (`P1–P11`), security rule, and pricing table entry in `R3` was independently verified against `git show 32d4b42e:<path>` and confirmed **100% character-for-character accurate**.

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Technical Accuracy & `32d4b42e` Alignment** | 30 | **30 / 30** | 100% of bucket names (`numista-uploads-studio-9101802118-8c9a8`, `studio-9101802118-8c9a8-uploads`), line numbers, and code snippets match `origin/dev` (`32d4b42e`). |
| **2. Zero-Raw-Storage & Redaction Completeness** | 25 | **24 / 25** | Covers all 11 upload paths (`P1–P11` + `main.py:7543` fallback), quarantine lifecycle for signed PUTs (`P3`, `P7`), low-confidence review queue (`SEC-2`), and hash-only dry-run backfill (`SEC-3`). (`-1` minor build note on `P10`/`P11` client-direct Firebase Storage trigger below). |
| **3. Rule 6(a) Verbatim Code Citations** | 20 | **20 / 20** | Every quoted line in `R3` is byte-exact from `git show 32d4b42e:<path>`. |
| **4. Machine-Checkable Exit Criteria & Rules Security** | 15 | **15 / 15** | `exiftool`, PDF grep, CI `generate_signed_url(` quarantine guard, Firestore emulator tests (`hasOnly`, `allow create: if false`, `member_uids`), and `gcloud storage ls -a` generation checks. |
| **5. Governance, Pricing v3.2 & Scope Hygiene** | 10 | **9 / 10** | Preserves all 3 `[ERIC DECISION]` items, cites exact Pricing v3.2 tiers (`Lifetime: ON HOLD`), marks unsourced vendor claims `UNVERIFIED`, and flags `fbcb35a8` transparently. |
| **TOTAL** | **100** | **98 / 100** | **PASS — Ready for SAG Review** |

---

## 2. Independent Verification of Every Citation Against `origin/dev` (`32d4b42e`) (Rule 6(a))

### 2.1 Storage Inventory & Bucket Constants (`R3 Section 1.1`)
- **[`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L349) (`32d4b42e` line `349`) & (`32d4b42e` line `7038`):**
  ```python
   349: USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
  ...
  7038: IMPORT_BUCKET = USER_CONTENT_BUCKET  # reuse the existing bucket
  ```
- **[`numista_backend/routes/import_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/import_routes.py#L21) (`32d4b42e` line `21`):**
  ```python
  21: BUCKET_NAME = "studio-9101802118-8c9a8-uploads"
  ```
- **[`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L12587-L12588) (`32d4b42e` lines `12587–12588`, `P9`):**
  ```python
  12587:                 bucket_name = os.environ.get("GCS_BUCKET_NAME", "studio-9101802118-8c9a8-uploads")
  12588:                 gcs_path = f"users/{req.user_email}/appraisals/Appraisal_Schedule_{_dt.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
  ```
- **Verification:** Confirmed. Both `numista-uploads-studio-9101802118-8c9a8` and `studio-9101802118-8c9a8-uploads` are accurately identified and scoped across `SEC-1`, `SEC-3`, and `SEC-8`.

### 2.2 All 11 Upload Paths (`P1–P11` + `7543` Fallback, `R3 Section 1.2`)
- **`P1` (`32d4b42e:numista_backend/main.py:7373-7378`):**
  ```python
  7373: def _save_to_gcs(user_email: str, session_id: str, filename: str,
  7374:                  data: bytes, file_type: str) -> str:
  7375:     bucket = gcs_client.bucket(IMPORT_BUCKET)
  7376:     safe_name = filename.replace(" ", "_")
  7377:     blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
  7378:     blob = bucket.blob(blob_path)
  ```
- **`P2` (`32d4b42e:numista_backend/main.py:7433-7441`):**
  ```python
  7433:     safe_name = fname.replace(" ", "_")
  7434:     blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
  7435:     
  7436:     try:
  7437:         bucket = gcs_client.bucket(IMPORT_BUCKET)
  7438:         blob = bucket.blob(blob_path)
  7439:         content_type = file.content_type or "application/octet-stream"
  7440:         file.file.seek(0)
  7441:         blob.upload_from_file(file.file, content_type=content_type)
  ```
- **`P3` & `7543` Fallback (`32d4b42e:numista_backend/main.py:7531-7544`):**
  ```python
  7531:         safe_name = f["name"].replace(" ", "_")
  7532:         blob_path = f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"
  7533:         blob = bucket.blob(blob_path)
  7534:         try:
  7535:             url = blob.generate_signed_url(
  7536:                 version="v4",
  7537:                 expiration=900,
  7538:                 method="PUT",
  7539:                 content_type=f.get("mime", "application/octet-stream"),
  7540:             )
  7541:         except Exception as e:
  7542:             logger.warning(f"Could not generate signed URL for {f['name']}: {e}. Client should use /api/import/upload.")
  7543:             url = f"/api/import/upload"
  7544:         signed_urls.append({"name": f["name"], "upload_url": url, "gcs_path": f"gs://{IMPORT_BUCKET}/{blob_path}"})
  ```
- **`P4`, `P5`, `P6` (`32d4b42e:numista_backend/main.py:7931, 8405, 8489`):**
  ```python
  7931:             blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
  ...
  8405:                                 partner_blob = bucket.blob(f"{user_email}/imports/{session_id}/raw/{partner_safe}")
  ...
  8489:                                 gcs_path_img = f"gs://{IMPORT_BUCKET}/{user_email}/imports/{session_id}/raw/{safe_name}"
  ```
- **`P7` (`32d4b42e:numista_backend/routes/import_routes.py:46-54`):**
  ```python
  46: @router.post("/v1/import/get_upload_url")
  47: async def get_upload_url(req: SignedUrlRequest, user: Dict[str, Any] = Depends(get_current_user)):
  48:     """Generate 15-minute V4 pre-signed GCS upload URL for large files (>5MB)."""
  49:     user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
  50:     blob_name = f"imports/{user_id}/{uuid.uuid4().hex}_{req.filename}"
  51:     
  52:     try:
  53:         bucket = storage_client.bucket(BUCKET_NAME)
  54:         blob = bucket.blob(blob_name)
  ```
- **`P8` (`32d4b42e:numista_backend/main.py:4282-4290`):**
  ```python
  4282: def _upload_to_gcs(file_bytes: bytes, dest_path: str, content_type: str = "image/jpeg") -> str:
  4283:     """
  4284:     Uploads bytes to the user-content GCS bucket.
  4285:     Returns the public gs:// URI.
  4286:     """
  4287:     bucket = gcs_client.bucket(USER_CONTENT_BUCKET)
  4288:     blob   = bucket.blob(dest_path)
  4289:     blob.upload_from_string(file_bytes, content_type=content_type)
  4290:     return f"gs://{USER_CONTENT_BUCKET}/{dest_path}"
  ```
- **`P10` & `P11` (`32d4b42e:numista_backend/storage.rules:9-12, 19-24`):**
  ```javascript
   9:     match /users/{email}/{allPaths=**} {
  10:       allow read, write: if request.auth != null
  11:                          && request.auth.token.email == email;
  12:     }
  ...
  19:     match /support_screenshots/{ticketId}/{filename} {
  20:       allow write: if request.auth != null
  21:                    && request.resource.size < 5 * 1024 * 1024
  22:                    && request.resource.contentType.matches('image/.*');
  23:       allow read: if false;
  24:     }
  ```
- **Verification:** Confirmed 100% exact.

### 2.3 EXIF Handling, Document AI, Lifecycle, Wishlist Share, Rules, Secrets & Privacy (`SEC-1` – `SEC-12`)
- **`SEC-1` (`32d4b42e:numista_backend/main.py:4269-4272`):**
  ```python
  4269:             # Strip GPS from EXIF for privacy
  4270:             exif_data = img.getexif()
  4271:             for gps_tag in [0x8825]:  # GPSInfo
  4272:                 exif_data.pop(gps_tag, None)
  ```
- **`SEC-2` (`32d4b42e:numista_backend/main.py:5014-5017`):**
  ```python
  5014:     request = documentai.ProcessRequest(
  5015:         name=DOCUMENT_AI_PROCESSOR_PATH,
  5016:         raw_document=raw_doc,
  5017:     )
  ```
- **`SEC-3` (`32d4b42e:gcs_lifecycle.json:27-33`):**
  ```json
  27:         "action": {
  28:           "type": "Delete"
  29:         },
  30:         "condition": {
  31:           "age": 30,
  32:           "isLive": false
  33:         }
  ```
- **`SEC-4` (`32d4b42e:numista_backend/main.py:12733-12746` & `32d4b42e:numista_mobile/firestore.rules:250-254`):**
  ```python
  12733: @app.post("/api/wishlist/create-share")
  12734: async def api_create_wishlist_share(req: WishlistShareRequest):
  ...
  12744:             "token": token,
  12745:             "owner_email": req.user_email,
  12746:             "owner_alias": req.owner_alias or "Numista Collector",
  ```
  ```javascript
  250:     match /public_wishlists/{token} {
  251:       allow get: if true;
  252:       allow create: if request.auth != null;
  253:       allow update: if request.resource.data.diff(resource.data).affectedKeys().hasAny(['reserved_items', 'reservation_details']);
  254:     }
  ```
- **`SEC-5` (`32d4b42e:numista_mobile/firestore.rules:278-281`):**
  ```javascript
  278:     match /family_groups/{familyGroupId} {
  279:       allow read: if request.auth != null;
  280:       allow write: if request.auth != null && request.auth.uid == resource.data.primary_owner_uid;
  281:     }
  ```
- **`SEC-6` (`32d4b42e:numista_backend/routes/payment_routes.py:174`, `stripe_config.py:28`, `main.py:11978`):**
  ```python
    174:     webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
  ...
     28:     # 1. Primary Attempt: Load from Environment Variables (standard backend/.env method)
  ...
  11978:     Reads EBAY_CERT_ID exclusively from os.environ (mounted via Secret Manager).
  ```
- **`SEC-7` (`32d4b42e:.github/workflows/deploy-production.yml:101-103` & `numista_backend/firestore.rules:2`):**
  ```yaml
  101:       - name: Deploy Firestore rules
  102:         working-directory: numista_mobile
  103:         run: firebase deploy --only firestore:rules --project studio-9101802118-8c9a8
  ```
  ```javascript
  2: // NOT DEPLOYED — REFERENCE MIRROR ONLY
  ```
- **`SEC-10` (`32d4b42e:numista_mobile/web/privacy.html:324` & `numista_mobile/lib/screens/privacy_screen.dart:137`):**
  ```html
  324:             <h2>4. Sharing Your Information</h2>
  ```
  ```dart
  137:                     _SectionHeader(title: '4. Sharing Your Information'),
  ```
- **`SEC-11` (`32d4b42e:numista_backend/scan_service/main.py:695` & `numista_mobile/lib/services/estate_fiduciary_service.dart:71`):**
  ```python
  695:                     'custodialLocation': 'Primary Storage / Home Safe',
  ```
  ```dart
   71:             'custodialLocation': 'Primary Storage / Home Safe',
  ```

---

## 3. Non-Blocking Implementation Note for Build Phase (`SHOULD-FIX`)

1. **`P10` / `P11` Client-Direct Firebase Storage Sanitization Path (`SEC-1`):**
   - `P10` (`users/{email}/**`, e.g. `coin_detail_screen.dart:4402-4410` and `my_collection_screen.dart:5440-5446`) and `P11` (`support_screenshots/{ticketId}/{filename}`) currently upload directly from the Flutter client to the default Firebase Storage bucket (`studio-9101802118-8c9a8.firebasestorage.app`). During `SEC-1` implementation, ensure `P10` and `P11` either route through a backend upload endpoint that invokes `sanitize_upload()` prior to GCS persistence or write to `quarantine/` in Firebase Storage where a backend worker sanitizes and moves the object.

---

## 4. Verdict

**98 / 100 — PASS.** Cleared for SAG Review and mirrored to `For SAG`.
