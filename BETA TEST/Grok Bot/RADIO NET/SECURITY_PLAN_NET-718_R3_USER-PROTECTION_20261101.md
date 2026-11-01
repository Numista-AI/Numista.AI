# SECURITY PLAN — NET-718 R3 — USER PROTECTION (Images, Imports, Sharing, Secrets)
**Author:** GB CoS (Grok CoS) — Eric directed at 6:25 PM ET, 2026-11-01: "Take advantage of the Ultra plan and you do it." (supersedes NET-725 to AG)
**Date:** 2026-11-01 ~6:40 PM ET | **Status:** DOCS-ONLY PLAN for Argon review → SAG. No code changed, nothing committed or deployed.
**Source of truth:** every citation is `origin/dev` **32d4b42e** (`git show 32d4b42e:<path>`). Quoted blocks are copied character-for-character, including leading whitespace, unless marked "(trimmed)". Line numbers are 1-based.
**Not cited:** origin/p7-v8.9 is NOT a descendant of dev, and its main.py line numbers differ (for example, import/start is at 7312 there and 7499 on dev). Do not cross-cite.
**Pending Eric's call:** AG pushed docs commit **fbcb35a8** to origin/p7-v8.9 (R2 plan plus radio). That broke the docs-only/no-commit rule. Eric decides whether to keep or revert it. GB CoS has taken no action on it.

Labels: **[EXISTS]** = in code at 32d4b42e. **[PROPOSED]** = new, not built. **[ERIC DECISION]** = open, not a defect.

---
## 0. Eric's rules this plan enforces
1. No raw or unredacted user upload may remain in storage. This covers every upload path, signed-URL PUTs, old stored versions and soft-deleted copies.
2. No invented prices, costs, resource names or vendor assurances. An unsourced claim is marked UNVERIFIED.
3. Backfill is dry-run first, and the report contains hashes and counts only. Destructive Phase B runs only after Eric types YES.

---
## 1. Storage inventory — real buckets and every raw upload path

### 1.1 Buckets (real names)
| Constant | Where | Value |
|---|---|---|
| `USER_CONTENT_BUCKET` | numista_backend/main.py:349 | `"numista-uploads-studio-9101802118-8c9a8"` |
| `IMPORT_BUCKET` | numista_backend/main.py:7038 | `IMPORT_BUCKET = USER_CONTENT_BUCKET  # reuse the existing bucket` |
| `BUCKET_NAME` | numista_backend/routes/import_routes.py:21 | `"studio-9101802118-8c9a8-uploads"` (a **different** bucket) |
| `GCS_BUCKET_NAME` env default | numista_backend/main.py:12587 | `"studio-9101802118-8c9a8-uploads"` (appraisal PDFs) |

So there are **two** user-data buckets in code: `numista-uploads-studio-9101802118-8c9a8` and `studio-9101802118-8c9a8-uploads`. Every redaction, backfill and deletion item covers **both**. Whether each bucket exists, has versioning or has soft-delete is **UNVERIFIED**. Confirm read-only with `gcloud storage buckets describe gs://<name>` (step B0).

### 1.2 Raw upload paths (all must route through redaction)
| # | Path | Bucket | Code |
|---|---|---|---|
| P1 | `{user_email}/imports/{session_id}/raw/{safe_name}` | IMPORT_BUCKET | main.py:7377 (`_save_to_gcs`) |
| P2 | same | IMPORT_BUCKET | main.py:7434 |
| P3 | same — **signed PUT, bytes never touch backend** | IMPORT_BUCKET | main.py:7532 (`/api/import/start`) |
| P4 | same | IMPORT_BUCKET | main.py:7931 |
| P5 | same (partner file) | IMPORT_BUCKET | main.py:8405 |
| P6 | same (path string reused) | IMPORT_BUCKET | main.py:8489 |
| P7 | `imports/{user_id}/{uuid}_{filename}` — **signed PUT** | BUCKET_NAME | routes/import_routes.py:50 |
| P8 | `dest_path` (caller-defined) | USER_CONTENT_BUCKET | main.py:4282-4290 `_upload_to_gcs` |
| P9 | `users/{email}/appraisals/...pdf` (generated, not upload) | GCS_BUCKET_NAME default | main.py:12587-12588 |
| P10 | client-direct `users/{email}/**` (Firebase Storage) | default Firebase bucket | numista_backend/storage.rules:9-12 |
| P11 | `support_screenshots/{ticketId}/{filename}` client upload | default Firebase bucket | storage.rules:19-24 |

The signed-URL fallback also writes to P1: main.py:7543 sets `url = f"/api/import/upload"`.

Exact quotes:
```
7531|        safe_name = f["name"].replace(" ", "_")
7532|        blob_path = f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"
7533|        blob = bucket.blob(blob_path)
7534|        try:
7535|            url = blob.generate_signed_url(
7536|                version="v4",
7537|                expiration=900,
7538|                method="PUT",
```
```
49|    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
50|    blob_name = f"imports/{user_id}/{uuid.uuid4().hex}_{req.filename}"
51|    
52|    try:
53|        bucket = storage_client.bucket(BUCKET_NAME)
```
```
4287|    bucket = gcs_client.bucket(USER_CONTENT_BUCKET)
4288|    blob   = bucket.blob(dest_path)
4289|    blob.upload_from_string(file_bytes, content_type=content_type)
```

---
## 2. Items (per-item format)

### SEC-1 Redact before store: one sanitizer on every write path
- **Current state [EXISTS]:** The only EXIF handling is HEIC-only GPS stripping in `_convert_heic_to_jpeg`, main.py:4254-4279:
```
4269|            # Strip GPS from EXIF for privacy
4270|            exif_data = img.getexif()
4271|            for gps_tag in [0x8825]:  # GPSInfo
4272|                exif_data.pop(gps_tag, None)
```
  JPEG, PNG, WebP and PDF go to storage unchanged on P1-P8.
- **Gap:** Raw originals with full EXIF (GPS, device serial, owner name) and unredacted documents (invoices, appraisals with addresses) are stored.
- **Fix [PROPOSED]:** `sanitize_upload(data: bytes, mime: str) -> bytes` with one parameter path:
  - Images: re-encode from pixels only and drop all EXIF/XMP/IPTC/ICC-comment fields. Keep orientation by applying it to the pixels, not by keeping the tag. PNG: drop tEXt/iTXt/zTXt/eXIf. WebP: drop EXIF/XMP chunks.
  - Documents: run PII redaction (see SEC-2) before storing.
  - Call it at P1, P2, P4, P5, P8 and the 7543 fallback.
  - P3 and P7 change from direct signed PUTs to an upload to `quarantine/` with a 24 h lifecycle delete. A backend worker sanitizes into the final path and deletes the quarantine object. Clients never get a PUT URL to the final path.
- **Test:** Fixtures (JPEG with GPS, PNG tEXt, WebP XMP, HEIC, PDF with an address) go through each endpoint, then the stored object is read back. Assert exiftool shows no metadata beyond dimensions, and the PDF fixture string is absent. CI check: grep fails if `generate_signed_url(` targets any path outside `quarantine/`.
- **Owner:** Backend (AG CoS impl) | **Effort:** 2 d | **Risk:** Medium. Re-encode changes bytes, and existing hash-dedupe must use the post-sanitize hash.

### SEC-2 Document PII redaction + low-confidence user review
- **Current state [EXISTS]:** Document AI is already wired (main.py:5015-5016 `name=DOCUMENT_AI_PROCESSOR_PATH,` / `raw_document=raw_doc,`). There is no redaction step.
- **Gap:** Names, addresses, account and card numbers on invoices and appraisals are stored and indexed unredacted.
- **Fix [PROPOSED]:**
  - Detect PII (names, street addresses, emails, phones, account/card numbers) and burn black boxes into a flattened image or PDF before storing.
  - Any detection under the confidence threshold goes into a **user review queue**. The user confirms or adds boxes before the file is finalized. Until then only the quarantine copy exists, auto-deleted at 24 h.
  - The original is never kept.
- **Vendor data-retention:** Google's Document AI data-handling/retention terms are **UNVERIFIED** in this plan. Before shipping, cite the current Google Cloud Document AI data-usage page in the PR. No "zero retention" claim may appear in user copy until then.
- **Test:** A PDF fixture with known PII yields no PII text in the stored object (text-extract + grep). A low-confidence fixture lands in the review queue and is not finalized.
- **Owner:** Backend + Mobile (review UI) | **Effort:** 3 d | **Risk:** Medium. OCR misses are why the review step exists.

### SEC-3 Backfill existing raw objects (dry-run first)
- **Current state:** Unknown count of raw objects in both buckets under `*/imports/*/raw/*`, `imports/*`, `users/*/**`.
- **Fix [PROPOSED]:**
  - **B0 (read-only):** `gcloud storage buckets describe` both buckets. Record versioning and soft-delete settings. Note: `gcs_lifecycle.json` in the repo root has `{"type": "Delete"}` with `"age": 30, "isLive": false`. Which bucket, if any, it is applied to is UNVERIFIED.
  - **Phase A dry-run:** List the scoped prefixes and run the sanitizer in memory. The report has only `sha256(object_path)`, `sha256(content)`, mime, size, an EXIF-present flag, a PII-detected count and an action. **No object paths, emails, filenames, or extracted text** appear in the report. Paths contain email and filename (P1: `{user_email}/...{safe_name}`).
  - **Phase B (only after Eric types YES):** Write sanitized versions, delete originals, delete all noncurrent generations, and purge soft-deleted copies (or wait out the soft-delete window, stated from B0 facts).
- **Test:** Phase A on staging. Assert the report contains no `@` and no file extensions. Phase B on staging. Assert `gcloud storage ls -a` shows zero noncurrent generations of touched objects.
- **Owner:** Backend | **Effort:** 1.5 d | **Risk:** High (destructive), so it is gated.

### SEC-4 Wishlist share: authenticate and stop exposing email
- **Current state [EXISTS]:** main.py:12733-12751. There is no auth dependency, and the owner email is taken from the request body and published:
```
12733|@app.post("/api/wishlist/create-share")
12734|async def api_create_wishlist_share(req: WishlistShareRequest):
```
```
12744|            "token": token,
12745|            "owner_email": req.user_email,
12746|            "owner_alias": req.owner_alias or "Numista Collector",
```
  Firestore rules numista_mobile/firestore.rules:250-254:
```
250|    match /public_wishlists/{token} {
251|      allow get: if true;
252|      allow create: if request.auth != null;
253|      allow update: if request.resource.data.diff(resource.data).affectedKeys().hasAny(['reserved_items', 'reservation_details']);
254|    }
```
- **Gap:**
  - Anyone can create a public share under any email.
  - `owner_email` is world-readable via `get: if true`.
  - `hasAny` lets an anonymous update change any field as long as it also touches `reserved_items`.
  - The client can `create` directly, bypassing the backend.
- **Fix [PROPOSED]:**
  - Add `user: dict = Depends(get_current_user)` (same pattern as main.py:7500) and derive the email/uid from the token, not the body.
  - Drop `owner_email` from the snapshot and store `owner_uid` in a private `/wishlist_tokens` doc. `owner_alias` already exists.
  - Rules: `hasOnly(['reserved_items','reservation_details'])` and `allow create: if false;` (Admin SDK writes).
  - Add token revoke.
- **Test:** Emulator: unauthenticated POST returns 401; the snapshot has no `owner_email`; an anonymous update touching `items` is denied; a client create is denied.
- **Owner:** Backend + Rules | **Effort:** 0.5 d | **Risk:** Low.

### SEC-5 family_groups read scope
- **Current [EXISTS]:** firestore.rules:278-279 `match /family_groups/{familyGroupId} {` / `allow read: if request.auth != null;`. Any signed-in user can read any family group.
- **Fix [PROPOSED]:** Read only if `request.auth.uid` is in `resource.data.member_uids` or is the `primary_owner_uid`. Migration adds `member_uids` to existing docs (dry-run count first).
- **Test:** Emulator: a non-member read is denied. **Owner:** Rules | **Effort:** 0.5 d | **Risk:** Low.

### SEC-6 Secrets
- **Current [EXISTS]:**
  - Stripe webhook secret: payment_routes.py:174 `webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")`.
  - stripe_config.py:28 `# 1. Primary Attempt: Load from Environment Variables (standard backend/.env method)`, so keys may come from a local `.env`.
  - eBay: main.py:11978 docstring says EBAY_CERT_ID is "mounted via Secret Manager". The Cloud Run mounting is UNVERIFIED.
- **Fix [PROPOSED]:** Confirm read-only with `gcloud run services describe` that every secret is a Secret Manager reference. Remove the `.env` fallback for production. Run gitleaks on full history (`gitleaks detect --log-opts="--all"`), and if anything is found, rotate first.
- **Test:** CI gitleaks job is green, and the service describe shows `secretKeyRef` for STRIPE_* / EBAY_*. **Owner:** Backend/DevOps | **Effort:** 0.5 d | **Risk:** Low.

### SEC-7 Rules deploy source of truth
- **Current [EXISTS]:** `.github/workflows/deploy-production.yml:103` runs `firebase deploy --only firestore:rules --project studio-9101802118-8c9a8` (deployed file per numista_mobile/firebase.json). numista_backend/firestore.rules line 2 is `// NOT DEPLOYED — REFERENCE MIRROR ONLY`.
- **Fix [PROPOSED]:** CI fails if the two rules files diverge without a marker, so all SEC-4/5 edits go to numista_mobile/firestore.rules. **Effort:** 0.25 d | **Risk:** Low.

### SEC-8 Account deletion covers all storage
- **Fix [PROPOSED]:** The delete-account job purges P1-P11 prefixes in **both** buckets plus the default Firebase bucket, including noncurrent generations, and then the Firestore user tree. **Test:** On staging, create a user, upload to each path, delete, then `ls -a` shows zero objects. **Effort:** 1 d | **Risk:** Medium.

### SEC-9 Account security (2FA) — [ERIC DECISION]
- **Proposal [PROPOSED]:** Optional TOTP for all users, required above a collection-value threshold. **[ERIC DECISION] threshold value — open.**

### SEC-10 Public security copy — [ERIC DECISION]
- **Current [EXISTS]:** privacy.html:324 `<h2>4. Sharing Your Information</h2>` and privacy_screen.dart:137 `_SectionHeader(title: '4. Sharing Your Information'),`. The existing text says images are processed on Gemini enterprise.
- **Fix [PROPOSED]:** After SEC-1 to SEC-3 ship, add a "Your uploads are sanitized" section. No vendor-retention claims unless sourced (see SEC-2). **[ERIC DECISION] final wording — open.**

### SEC-11 Custody location field
- **Current [EXISTS]:** numista_backend/scan_service/main.py:695 `'custodialLocation': 'Primary Storage / Home Safe',` (trimmed) and numista_mobile/lib/services/estate_fiduciary_service.dart:71 uses the same `'custodialLocation'` key. Storing where valuables are kept is sensitive.
- **Fix [PROPOSED]:** Keep it owner-only (already under `/users/{email}` via isOwner, firestore.rules:13-15). Exclude it from shares, exports to third parties and logs. Add a log-scrub test. **Effort:** 0.25 d | **Risk:** Low.

### SEC-12 Marketing pixel — [ERIC DECISION]
- **Current:** No pixel was found in numista_mobile/web/index.html at 32d4b42e (R2's "commented-out pixel at 43-56" was wrong; those lines are twitter meta tags).
- **Proposal [PROPOSED]:** If a Pixel is added, send no PII and fire only after consent. **[ERIC DECISION] Pixel Purchase event value — open.**

---
## 3. Prices (Pricing v3.2 — reference only, no new prices)
| Tier | Monthly | Annual |
|---|---|---|
| Copper | $4.99 | $49.99 |
| Silver | $8.99 | $89.99 |
| Platinum | $10.99 | $109 |
| Gold | $15.99 | $150 |
- Top-up: $5.
- One-time full exports (6x monthly): $29.94 / $53.94 / $65.94 / $95.94.
- **Lifetime: ON HOLD.**
- Implementation cloud costs are **TBD** (no estimates invented).

## 4. Sequence
SEC-7 → SEC-4 → SEC-5 → SEC-6 → SEC-1 → SEC-2 → SEC-3 (A, then Eric YES, then B) → SEC-8 → SEC-11. SEC-9, SEC-10 and SEC-12 wait on Eric. Total about 9.5 d of engineering.

## 5. Lessons (from R1 74 and R2 68)
1. R2 lost about 20 points to "verbatim" blocks that were never in the file. Rule: quote only from `git show <sha>:<path>` output, with the sha in the header.
2. Bucket names were invented (`numista-vault*`). Rule: resource names come from code constants, with line cites.
3. There are two buckets, not one. Grep every `bucket(` and `generate_signed_url(` before claiming coverage.
4. Reports and logs leak through paths, because paths contain emails and filenames. Hash them.
5. Vendor assurances need a source or an UNVERIFIED label.
6. Don't cross-cite branches that have diverged (p7-v8.9 vs dev).
7. Docs-only means no commits or pushes, docs included (fbcb35a8).
