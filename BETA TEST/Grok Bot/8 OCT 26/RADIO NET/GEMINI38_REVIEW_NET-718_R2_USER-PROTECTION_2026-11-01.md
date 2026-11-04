# GEMINI 3.8 TECHNICAL REVIEW — `SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md` (R2)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**Target Plan:** [`SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md)  
**Author Reviewed:** AG CoS v4 (`ba2bfdb2`)  
**Prior Scores:** Grok CoS R1 `74/100 REVISE` ([`COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md)) | Argon R1 `75/100 REVISE` ([`GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md))  
**Date / Time:** 2026-11-01 18:22 ET  
**Score:** **89 / 100 — REVISE (`R3` Fix-Only required for remaining unverified route line numbers & `.hasOnly()` rule fix)**  
**Execution Lock:** **NO EXECUTE** — Plan-only review. Zero code changes, zero deploys, zero pushes.

---

## 1. Executive Summary & Scoring Breakdown

`SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md` resolves the majority of the R1 findings (`MF1` Firestore rules line numbers & verbatim quotes, `MF2` `/api/import/start` direct signed-URL upload closure + Document AI client reuse + PII-free dry-run report + GCS version purge, `MF3` `$12.99` removal + `NET-706 R5` `160-166` quote + `privacy.html:325`/`privacy_screen.dart:139` quotes, `SF1` full-history `gitleaks git --verbose`, `SF2` `TBD` cost labels, and `SF4` `owner_alias` recognition).

However, our line-by-line verification against `origin/dev` (`32d4b42e`) and `HEAD` (`p7-v8.9`) caught **four specific remaining defects** that prevent a `>=95/100 PASS` under `GEMINI.md` Rule 6(a):
1. **Fabricated Photo-Ingest Route Line Numbers in Section 3.1 (`lines 125-132`):** Five `main.py` line numbers (`4178`, `4315`, `4148`, `4981`, `4410`) and two router line numbers (`routes/scan_routes.py:15`, `routes/ai_routes.py:25`) do not match either `origin/dev` (`32d4b42e`) or `HEAD` (`p7-v8.9`), and `/api/coin_crop` is a `GET` endpoint, not a `POST` upload route.
2. **Wrong Workflow Line Range & `storage.rules` Path in Section 6.1 (`lines 253-258, 294`):** `Deploy Firestore rules` in `.github/workflows/deploy-production.yml` is at lines **`101-103`** (not `68-71`), and `storage.rules` is at **`numista_backend/storage.rules`** (not `numista_mobile/storage.rules`, which does not exist in git).
3. **`/public_wishlists/{token}` `.hasAny()` Vulnerability Left Unfixed in Section 6.3 (`line 318`):** `affectedKeys().hasAny(['reserved_items', 'reservation_details'])` still uses `.hasAny()` instead of `.hasOnly()`, allowing an unauthenticated caller who touches `reserved_items` to simultaneously overwrite `items` or `owner_alias`.
4. **Mixed `HEAD` (`p7-v8.9`) vs `origin/dev` (`32d4b42e`) Line Numbers in `numista_backend/main.py` + Missed `routes/import_routes.py:46-66`:** `R2` declares `code target origin/dev 32d4b42e` in its header (line 4), but cites `HEAD` (`p7-v8.9`) line numbers for `main.py:4116, 7209, 7247, 7312, 11672, 12428` while citing `origin/dev` line numbers for `main.py:2047, 5008`. Also, `POST /v1/import/get_upload_url` (`numista_backend/routes/import_routes.py:46-66`) is a second direct-to-GCS V4 signed URL endpoint that must be closed alongside `/api/import/start`.

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Technical Accuracy & `origin/dev` Alignment** | 30 | **23 / 30** | `-7`: Section 3.1 photo route line numbers (`4178, 4315, 4148, 4981, 4410, scan_routes:15, ai_routes:25`) and `.github/workflows/deploy-production.yml:68-71` / `numista_mobile/storage.rules` are wrong. |
| **2. Receipt Redaction & Zero-Retention Completeness** | 25 | **23 / 25** | `-2`: Closed `/api/import/start`, but missed second signed-URL route `POST /v1/import/get_upload_url` (`numista_backend/routes/import_routes.py:46-66`). |
| **3. Rule 6(a) Verbatim Code Citations** | 20 | **18 / 20** | `-2`: Mixed `HEAD` (`p7-v8.9`) and `origin/dev` (`32d4b42e`) line numbers in `main.py`. |
| **4. Machine-Checkable Exit Criteria & Rules Security** | 15 | **15 / 15** | Full-history `gitleaks git --verbose` + Firestore emulator test suite + zero-PII Playwright test. |
| **5. Governance & Scope Hygiene** | 10 | **10 / 10** | Respects `NO EXECUTE` lock, `TBD` cost labels, and `[PROPOSED]` tags. |
| **TOTAL** | **100** | **89 / 100** | **REVISE (`R3` Fix-Only)** |

---

## 2. Turnkey Fixes for `SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md`

### Fix 1 (MUST-FIX): Replace Fabricated Photo-Ingest Route Line Numbers in Section 3.1 (`R2 lines 124-133`) with Verified `origin/dev` (`32d4b42e`) & `HEAD` (`p7-v8.9`) Citations

- **Why R2 Failed Here:** `R2` lines `125-132` cited `main.py:4178, 4315, 4148, 4981, 4410`, `routes/scan_routes.py:15`, and `routes/ai_routes.py:25` without quoting the lines. None of those line numbers match `origin/dev` (`32d4b42e`) or `HEAD` (`p7-v8.9`), `/api/coin_crop` is a `GET` route (`@app.get("/api/coin_crop")`), and `/api/ai/chat` takes JSON `ChatTurnRequest` (not image bytes).
- **Turnkey Replacement for Section 3.1 (Verified Against Both `origin/dev 32d4b42e` and `HEAD p7-v8.9`):**
  - `_convert_heic_to_jpeg` (`origin/dev:numista_backend/main.py:4254-4279` | `HEAD:4116-4141`):
    ```python
    4254: def _convert_heic_to_jpeg(raw_bytes: bytes) -> tuple:
    4255:     """Convert HEIC/HEIF to JPEG. Strips GPS EXIF for privacy, keeps orientation.
    4256:     Returns (jpeg_bytes, 'image/jpeg'). If not HEIC, returns input unchanged."""
    ```
  - Central GCS image upload helper `_upload_to_gcs` (`origin/dev:numista_backend/main.py:4282-4289` | `HEAD:4144-4151`):
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
  - `POST /api/identify_coin_photo` (`origin/dev:numista_backend/main.py:6371-6372` | `HEAD:6233-6234`):
    ```python
    6371: @app.post("/api/identify_coin_photo")
    6372: async def identify_coin_photo(request: Request, obverse: UploadFile = File(...), reverse: Optional[UploadFile] = File(None), user_email: str = Form("default"), decoded_user: dict = Depends(verify_token)):
    ```
  - `POST /api/identify_group_photo` (`origin/dev:numista_backend/main.py:5796-5797` | `HEAD:5658-5659`):
    ```python
    5796: @app.post("/api/identify_group_photo")
    5797: async def identify_group_photo(request: Request, file: UploadFile = File(...), user_email: str = Form("default"), Fast_Mode: bool = Form(True), decoded_user: dict = Depends(verify_token)):
    ```
  - `POST /api/analyze_binder_scan` (`origin/dev:numista_backend/main.py:4621-4622` | `HEAD:4483-4484`):
    ```python
    4621: @app.post("/api/analyze_binder_scan")
    4622: async def analyze_binder_scan(
    ```
  - `POST /api/analyze_checklist` (`origin/dev:numista_backend/main.py:5104-5105` | `HEAD:4966-4967`):
    ```python
    5104: @app.post("/api/analyze_checklist")
    5105: async def analyze_checklist(request: Request, file: UploadFile = File(...), user_email: str = Form("default"), decoded_user: dict = Depends(verify_token)):
    ```
  - `POST /api/analyze/grade-coin` (`origin/dev:numista_backend/main.py:6726-6727` | `HEAD:6588-6589`):
    ```python
    6726: @app.post("/api/analyze/grade-coin")
    6727: async def grade_coin(
    ```
  - `POST /api/import/upload` (`origin/dev:numista_backend/main.py:7396-7397` | `HEAD:7209-7210`):
    ```python
    7396: @app.post("/api/import/upload")
    7397: async def import_upload(
    ```
  - `POST /upload_document` (`origin/dev:numista_backend/routes/scan_routes.py:84-85`):
    ```python
    84: @router.post("/upload_document", response_model=DocumentParseResponse)
    85: async def upload_document(
    ```

---

### Fix 2 (MUST-FIX): Correct `.github/workflows/deploy-production.yml` Line Numbers (`101-103`) & `numista_backend/storage.rules` Path in Section 6.1

- **Why R2 Failed Here:**
  1. `R2` lines `253-258` cited `.github/workflows/deploy-production.yml:68-71` for `Deploy Firestore rules`, but lines `66-70` are `Authenticate to Google Cloud` in Job 1. The actual `Deploy Firestore rules` step is at **lines `101-103`** of [`.github/workflows/deploy-production.yml`](file:///c:/Users/ericd/Documents/MyVertexProject/.github/workflows/deploy-production.yml#L101-L103):
     ```yaml
     101:       - name: Deploy Firestore rules
     102:         working-directory: numista_mobile
     103:         run: firebase deploy --only firestore:rules --project studio-9101802118-8c9a8
     ```
  2. `R2` line `294` cited `numista_mobile/storage.rules` (`Lines 9-12`), which **does not exist in git** (`git ls-files *storage.rules*` returns only `numista_backend/storage.rules`). Cite [`numista_backend/storage.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/storage.rules#L1-L52) as the existing tracked file and label `numista_mobile/storage.rules` as `[PROPOSED]`.

---

### Fix 3 (MUST-FIX): Harden `/public_wishlists/{token}` `allow update` from `.hasAny()` to `.hasOnly()` in Section 6.3 (`R2 line 318`)

- **Why R2 Failed Here:** In `R2` line `318`, the proposed rule still reads:
  ```javascript
  allow update: if request.resource.data.diff(resource.data).affectedKeys().hasAny(['reserved_items', 'reservation_details']);
  ```
  In Firestore Rules v2, `Set.hasAny(list)` returns `true` if the modified keys intersect the list at all — meaning an unauthenticated user who modifies `reserved_items` can simultaneously modify `items` or `owner_alias` in the same request!
- **Turnkey Replacement for Section 6.3 (`numista_mobile/firestore.rules:250-254`):**
  ```javascript
  match /public_wishlists/{token} {
    allow get: if true;
    allow create: if false; // Cloud Run Admin SDK only via POST /api/wishlist/create-share
    allow update: if request.resource.data.diff(resource.data).affectedKeys().hasOnly(['reserved_items', 'reservation_details']);
    allow delete: if false;
  }
  ```

---

### Fix 4 (SHOULD-FIX): Standardize `main.py` Line Numbers to `origin/dev` (`32d4b42e`) (or Cite Both `origin/dev` & `HEAD`) and Include `routes/import_routes.py:46-66`

- **Why R2 Had a 187–306 Line Shift in `main.py`:** The workspace is currently checked out on `p7-v8.9` (`main.py` = 12,530 lines), whereas `origin/dev` (`32d4b42e`) has 12,836 lines. Citing both (`origin/dev` / `p7-v8.9`) eliminates any branch ambiguity:
  - `POST /api/import/upload`: `origin/dev:numista_backend/main.py:7396-7442` (`p7-v8.9:7209-7255`), `/raw/` write at `origin/dev:7434` (`p7-v8.9:7247`).
  - `POST /api/import/start`: `origin/dev:numista_backend/main.py:7499-7548` (`p7-v8.9:7312-7359`), `/raw/` signed URL at `origin/dev:7532-7540` (`p7-v8.9:7345-7353`).
  - Other `/raw/` occurrences in `main.py`: `origin/dev:7377, 7931, 8405, 8489` (`p7-v8.9:7678, 8099, 8183, 8572-8575`).
  - Second direct signed-URL route to close in Section 2.1/2.3: `POST /v1/import/get_upload_url` in [`numista_backend/routes/import_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/import_routes.py#L46-L66):
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
  - `_get_ebay_access_token` (`os.environ` mounted via Secret Manager): `origin/dev:numista_backend/main.py:11975-11985` (`p7-v8.9:11669-11676`), plus `.github/workflows/deploy-production.yml:156` (`--update-secrets=EBAY_CERT_ID=EBAY_CERT_ID:latest`) and `numista_backend/functions/feedbackIntelligence.js:21-23`.
  - `POST /api/wishlist/create-share`: `origin/dev:numista_backend/main.py:12733-12764` (`p7-v8.9:12427-12458`) — note the route path is `/api/wishlist/create-share` (not `/wishlist/share`).

---

## 3. Verdict

**89 / 100 — REVISE (`R3` Fix-Only).** Applying the 4 turnkey fixes above will bring `SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md` to `>=97/100 PASS`.
