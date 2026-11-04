# SECURITY PLAN — NET-718 R5 — USER PROTECTION (Images, Imports, Sharing, Secrets)
**Author:** GB CoS (Grok Bot). R5 = FIX-ONLY round closing every must-fix in SAG_REVIEW_NET-718-R4_74_REVISE_20261101.md, on Eric's redaction direction of 1 Nov 2026 ~9:09 PM ET. R4 closures kept below.
**Date:** 2026-11-01 ~9:45 PM ET | **Status:** DOCS-ONLY. No code changed, nothing committed, pushed or deployed. A PASS still needs Eric's typed YES.
**Source of truth:** `origin/dev` **32d4b42e** (`git show 32d4b42e:<path>`, re-read 2026-11-01 evening on EDS_Laptop). Line numbers are 1-based.
**Not cited:** origin/p7-v8.9 (diverged from dev). **Pending Eric's call:** AG docs commit fbcb35a8 on p7-v8.9 (keep or revert); no action taken.

## R5 closure table (SAG R4 must-fixes)
| # | SAG R4 must-fix | R5 fix | Where |
|---|---|---|---|
| R5-1 | Accept-on-miss is fail-open | **Default is reject.** A document is stored only if its type is positively classified AND every required PII class for that type was found and burned AND a post-burn OCR re-check finds none of it. "No address found" on a type that should have one = reject. The only exception is a document **template** (not an individual upload) that a human reviewer has flagged "has no addressee"; that flag lives in a versioned allow-list file reviewed by Eric. | SEC-2 |
| R5-2 | Names only near labels; US-only patterns | Names are detected anywhere on the page: (a) the account holder's own display name and email local-part, matched fuzzily anywhere; (b) a person-name NER model run locally on all OCR text (header, greeting "Dear/Hi/Thank you", signature, ship-to, bill-to); (c) all label families incl. non-US ("Ship to, Deliver to, Bill to, Sold to, Customer, Name, Attn, Recipient, Destinataire, Lieferadresse"). Address detection uses `libpostal` address parsing (international) plus US/CA/UK/AU postcode patterns; any line it parses as a street address is burned. A document with any text the parser cannot classify near a name is rejected. | SEC-2 |
| R5-3 | JPEG receipts get only EXIF strip | **Every upload of any type runs the same pipeline:** EXIF strip, then OCR text-presence check. Any image with readable text (receipt photo, invoice JPEG, support screenshot, appraisal photo) goes through full SEC-2 redaction with the reject default. Images with no readable text (a coin photo) pass after EXIF strip. No mime or filename trust. Applies to P1-P11. | SEC-1 |
| R5-4 | Soft-deleted copies may wait out the window | Before any delete in SEC-3/SEC-8, soft delete is **disabled** on the user-content buckets (`gcloud storage buckets update --clear-soft-delete`), and the job waits ≥30 s for propagation, so every delete this plan makes is permanent immediately. Google documents that copies **already** soft-deleted before that change cannot be purged early (they are kept until their `hardDeleteTime`, at most 7 days at today's setting); this is stated as a known limit, not hidden. | SEC-3, SEC-8 |
| R5-5 | `UploadFile` spools to disk | Upload endpoints stop using multipart/`UploadFile`. The client sends the file as the raw request body (`application/octet-stream`, metadata in headers); the handler reads `request.stream()` into a capped `bytearray` (32 MB) in memory. No `SpooledTemporaryFile`, no `/tmp`, no body logging; on exception the buffer is zeroed and dropped. | SEC-1 |
| R5-6 | Free-text notes can hold an address; Stripe claim unevidenced | New SEC-15: notes and every free-text field show a warning ("Don't type your address here") and are screened on write with the same address parser; a match is rejected with a message. The Stripe point is quoted with its source below. | SEC-14, SEC-15 |
| R5-7 | §3 "$4.99/mo, $29/yr" not shown by the cited line | §3 quotes lines 50-51 together (amount and interval) and shows the grep. | §3 |

## R4 closure table## R4 closure table (SAG R3 must-fixes)
| # | SAG must-fix | R4 fix | Where |
|---|---|---|---|
| M1 | `quarantine/` durable write keeps unredacted name/ship-to; contradicts rule 1 | **Quarantine removed entirely.** All bytes arrive at the backend, are sanitized and redacted **in memory**, and only the burned copy is written. Low confidence = upload rejected and bytes dropped; nothing queued or stored. Signed PUT URLs to user paths are removed (P3, P7). Client-direct Storage writes (P10, P11) are denied by rules and routed through the backend. | SEC-1, SEC-2 |
| M2 | Home addresses can be collected (invoices, Document AI, review UI, custodialLocation) | New SEC-14 invariant: no street-address field anywhere; addresses detected on scans are burned, never extracted into Firestore, logs, or exports. Document AI receives only redacted bytes, or is bypassed until its retention terms are cited. `custodialLocation` becomes a fixed enum with no free text (SEC-11). Review UI removed. | SEC-2, SEC-11, SEC-14 |
| M3 | §3 prices unsourced | §3 deleted and replaced with a pointer: this plan sets no prices. The only prices in code are $4.99/mo and $29/yr (`payment_routes.py:50-51`). | §3 |
| M4 | Existing `public_wishlists` docs keep `owner_email` | SEC-4 adds a dry-run-then-strip backfill (counts only), gated on Eric YES. | SEC-4 |
| M5 | SEC-5 rules-first locks out family groups | Order fixed: migration (dry-run, then write `member_uids`) → verify 100% docs have the field → then deploy the rule. | SEC-5, §4 |
| M6 | P9 appraisal PDFs and P6 outside the sanitize list | P6 (main.py:8489) is a path string pointing at the object P1/P2 already wrote, so it is covered once P1/P2 are. P9 (main.py:12559-12592) gets SEC-13: field allow-list in the PDF generator (no address/custody text) plus the archive copy stops being written under an email path. Receipts endpoints (main.py:8566, 8899, 8953) serve only stored, already-redacted objects. | SEC-13 |

Labels: **[EXISTS]** = in code at 32d4b42e. **[PROPOSED]** = new, not built. **[ERIC DECISION]** = open, not a defect.

---
## 0. Eric's rules this plan enforces
1. **The raw scan is never stored, anywhere, for any length of time.** Every upload is redacted in memory on the backend; only the blacked-out copy is written. A receipt, invoice or appraisal must have the person's name and ship-to/bill-to address positively found and burned out; if a document that should have an address shows none, or redaction is not confident, the upload is rejected and the bytes are dropped, unless a human reviewer has flagged that document type as having no address. This covers every upload path, signed URLs, client-direct writes, temp files, old stored versions and soft-deleted copies.
2. **No user home address is ever collected.** Not as a field, not extracted from a scan, not in logs, shares or exports.
3. No invented prices, costs, resource names or vendor assurances. An unsourced claim is marked UNVERIFIED.
4. Backfill is dry-run first; reports contain hashes and counts only. Destructive steps run only after Eric types YES.

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

### SEC-1 One in-memory pipeline for every upload, every type
- **Current state [EXISTS]:** only HEIC gets GPS stripped (`_convert_heic_to_jpeg`, main.py:4255-4279; 4269-4272 pop tag 0x8825). `/api/import/upload` (main.py:7396-7441) takes `file: UploadFile = File(...)` (7398) and writes `file.file` straight to `{user_email}/imports/{session_id}/raw/{safe_name}` (7434-7441). `_save_to_gcs` (7373-7385) and `_upload_to_gcs` (4282-4290) write what they are given. `/api/import/start` issues signed PUTs to the same raw path (7531-7544).
- **Fix [PROPOSED]:**
  1. **Intake, memory only [R5-5]:** FastAPI `UploadFile` is backed by a `SpooledTemporaryFile` that moves to disk above its size limit, so it is not used. Every upload endpoint accepts the file as the raw body: `Content-Type: application/octet-stream`, filename/mime/session in headers. Handler:
     ```python
     buf = bytearray()
     async for chunk in request.stream():
         buf += chunk
         if len(buf) > 32 * 1024 * 1024:   # same cap as main.py:7424-7425
             buf[:] = b"\0" * len(buf); raise HTTPException(413, "FILE_TOO_LARGE")
     try:
         out = sanitize_upload(bytes(buf), declared_mime)   # Reject raises
     finally:
         buf[:] = b"\0" * len(buf); del buf
     ```
     No file is opened for writing anywhere in the pipeline (PIL, pdf rasterizer and OCR are called on in-memory buffers: `Image.open(io.BytesIO(...))`, `pypdfium2.PdfDocument(bytes)`, `pytesseract.image_to_data(PIL.Image)`). Note: pytesseract itself writes a temp image file for the Tesseract binary, so OCR uses the in-process `tesserocr` binding (C API, memory only) instead. Request-body logging is off for these routes; exceptions log only an error code. A unit test patches `tempfile`, `open(..., "w*")` and `os.open` to raise and runs every fixture: any disk write fails the test.
  2. **Classify by content, not mime [R5-3]:** decode (images: PIL incl. HEIC via pillow-heif; PDFs: rasterize every page at 200 dpi). EXIF/XMP/IPTC/ICC dropped by re-encoding from pixels, orientation applied to pixels. Then OCR every raster. If OCR finds ≥ 10 words or any digit run ≥ 5, the file is a **document** (receipt photo, invoice JPEG, screenshot, appraisal photo, PDF) and goes to SEC-2. Otherwise it is a **photo** (coin, edge, microscope) and is stored after EXIF strip.
  3. **Write:** only `out` is written, to the existing final path. Clients never get a signed PUT URL (P3 main.py:7531-7544 and P7 routes/import_routes.py:50-53 removed; P3 returns `upload_url="/api/import/upload"` as its fallback at 7543 already does). Client-direct Storage writes (P10 `users/{email}/**`, P11 `support_screenshots/`) are denied in storage.rules (`allow write: if false`) and the app posts to the backend.
  4. **Call sites (all P1-P11):** main.py:7441, 7384 (callers 7931, 8404-8405), 4289, routes/estate_routes.py:44, routes/feedback_callable_route.py:495, routes/import_routes.py:54/97, scan_service/estate_pdf_builder.py:320. CI: `git grep -n "upload_from_string\|upload_from_file\|UploadFile"` in numista_backend must match an allow-list where every hit is downstream of `sanitize_upload`; any `generate_signed_url(` with `method="PUT"` fails CI.
- **Test:** fixtures: coin JPEG+GPS, receipt JPEG (phone photo), invoice PNG screenshot, receipt PDF, HEIC receipt, WebP with XMP, non-US receipt (UK, Canada), blurry receipt. For each endpoint: stored objects have no metadata (exiftool); OCR of stored documents finds no name/address; rejected fixtures leave **no** object; the no-disk-write test passes; signed-PUT grep empty; emulator denies client-direct writes.
- **Owner:** Backend + Mobile | **Effort:** 3.5 d | **Risk:** Medium (Cloud Run memory sizing for 32 MB + rasters; set instance memory ≥ 2 GiB, verified on staging).

### SEC-2 Document redaction: default reject
- **Current state [EXISTS]:** Document AI receives raw bytes (main.py:5008-5016, `RawDocument(content=file_bytes, ...)`), reached from `/api/process_invoice` (main.py:2023). No image/document redaction exists (`git grep -i redact` finds only the support-ticket field redaction in numista_backend/SUPPORT_WORKFLOW.md:64-82, which hides Firestore fields from support staff).
- **Fix [PROPOSED]:** all steps run on in-memory rasters from SEC-1, on the server, with no external call.
  1. **Classify type:** receipt / invoice / packing slip / appraisal / certificate / other, using local keyword + layout rules on OCR text. "other" with readable text = **reject**.
  2. **Required PII per type:** receipt, invoice, packing slip, appraisal = person name AND address required to be found. Certificate (e.g. grading cert) = name check only.
  3. **Detect names anywhere [R5-2]:** (a) the signed-in user's display name, first and last name tokens and email local-part, fuzzy-matched (edit distance ≤ 2) on every OCR word; (b) local person-name NER (spaCy `en_core_web_sm` / `xx_ent_wiki_sm`, run in-process) over all text, including headers, greetings, thank-you lines and signatures; (c) every line following a label in the label list (Ship to, Deliver to, Bill to, Sold to, Customer, Name, Attn, Recipient, Buyer, plus FR/DE/ES equivalents).
  4. **Detect addresses, international [R5-2]:** `libpostal` (`pypostal`) parses each line and 2-3-line window; any parse with `house_number`+`road`, `po_box`, or `postcode`+`city` is an address block. Postcode regexes for US, CA, UK, AU as a second check.
  5. **Burn:** solid black fill on the raster over every detected word box with 4 px margin; output flattened image (or image-only PDF). No text layer survives.
  6. **Verify (fail closed) [R5-1]:** re-OCR the burned raster. Store only if: required PII for the type was found before burn; after burn, none of the name tokens, no libpostal address parse and no email/phone/card/account pattern is found; mean OCR confidence of the page ≥ 80. Anything else -> **reject: HTTP 422 `REDACTION_NOT_CONFIDENT`**, bytes zeroed and dropped, nothing stored, nothing sent to Document AI, no Firestore doc. User message: "We couldn't safely black out your name and address on this file, so we didn't keep it. Try a clearer photo, or crop out the address first."
  7. **Human-review exception (templates only):** a reviewer (Eric or delegate) may add a template to `redaction_no_addressee_allowlist.json` (e.g. "US Mint order-status web page, layout hash X: no addressee"), only from synthetic or consented examples, never from a stored user upload. A matching document skips the "address required" check but still runs name detection and verify. The file is versioned and every change needs Eric's YES.
  8. **Document AI** (line-item parsing) receives only the burned output. Its data-usage terms remain **UNVERIFIED** in this plan.
  9. Extracted line items written to `users/{email}/receipts` (main.py:7361-7366) are filtered by the same name/address detectors before the write.
- **Test:** 30-fixture set (US Mint, eBay, APMEX, dealer handwritten, UK and Canadian invoices, greeting-line names, thank-you names, no-label names, appraisal letter). Pass = every fixture either stored with 0 recoverable name/address (independent OCR + libpostal over the stored object) or rejected with no object; the "no address on an address type" fixture is rejected; an allow-listed template passes.
- **Owner:** Backend + Mobile | **Effort:** 4 d | **Risk:** Medium (more rejects; by design).

### SEC-3 Backfill existing raw objects (dry-run first)
- **Scope:** both user buckets (`numista-uploads-studio-9101802118-8c9a8`, `studio-9101802118-8c9a8-uploads`) and the default Firebase bucket, prefixes `*/imports/*/raw/*`, `imports/*`, `users/*/**`, `support_screenshots/*`.
- **B0 (read-only):** `gcloud storage buckets describe` each bucket; record versioning/soft-delete. (`gcs_lifecycle.json` in repo root: Delete, age 30, isLive false; which bucket it is applied to is UNVERIFIED.)
- **Phase A dry-run:** stream each object into memory, run `sanitize_upload`, discard output. Report = `sha256(path)`, `sha256(content)`, mime, size, exif_present, address_detected (bool), would_reject (bool). No paths, emails, filenames or text.
- **Phase B (Eric YES only) [R5-4]:** step 1, disable soft delete on `numista-uploads-studio-9101802118-8c9a8`, `studio-9101802118-8c9a8-uploads` and `studio-9101802118-8c9a8.firebasestorage.app` (`gcloud storage buckets update --clear-soft-delete gs://<bucket>`; Google: "After disabling a soft delete policy on your bucket, Cloud Storage doesn't retain newly deleted objects", docs.cloud.google.com/storage/docs/disable-soft-delete) and wait ≥ 30 s (Google's stated propagation wait). Step 2, write sanitized versions and delete originals; would_reject documents are **deleted** (never kept). Step 3, delete all noncurrent generations. Result: every delete is permanent at once. **Known limit:** Google states that objects soft-deleted before the policy change "are retained until the previously applied retention duration expires" and the delete API "cannot be used to permanently delete soft-deleted objects"; any such copies expire on their own `hardDeleteTime` (≤ 7 days, from B0). Phase A lists their count (`gcloud storage ls --soft-deleted`, counts only). Soft delete stays off on these buckets afterwards (NET-676 v1.3 notes the lost restore option).
- **Test:** staging A then B; report has no `@` or extensions; `gcloud storage ls -a` shows no noncurrent generations of touched objects. **Effort:** 1.5 d | **Risk:** High, gated.

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
  - Add `user: dict = Depends(get_current_user)` (same pattern as `/api/import/upload`, main.py:7401) and derive uid from the token, not the body.
  - Drop `owner_email` from new snapshots; store `owner_uid` in a private `/wishlist_tokens/{token}` doc (rules: read/write false). `owner_alias` stays.
  - Rules (numista_mobile/firestore.rules:250-254): `hasOnly(['reserved_items','reservation_details'])`; `allow create: if false;`.
  - Client reads that use `owner_email` must change: wishlist_screen.dart:1031 (`.where('owner_email', isEqualTo: userEmail)`) → query `/wishlist_tokens` via backend list endpoint; public_wishlist_view_screen.dart:157 shows `owner_alias` only; beta_checklist_service.dart:392 query switched to `owner_uid` (the comment at :389 already allows `owner_uid == uid`).
  - **Backfill existing docs [R4: M4]:** script `strip_wishlist_email.py`. Dry-run: count of `public_wishlists` docs with `owner_email` (count only). After Eric YES: for each doc, write `owner_uid` to `/wishlist_tokens/{token}` (resolve uid from email via Admin Auth; unresolved → token revoked), then `update({'owner_email': DELETE_FIELD})`. Verify: count with `owner_email` = 0.
  - Add token revoke.
- **Test:** Emulator: unauthenticated POST returns 401; the snapshot has no `owner_email`; an anonymous update touching `items` is denied; a client create is denied.
- **Owner:** Backend + Rules | **Effort:** 0.5 d | **Risk:** Low.

### SEC-5 family_groups read scope (migrate first, rule second)
- **Current [EXISTS]:** numista_mobile/firestore.rules:278-281: `allow read: if request.auth != null;` (any signed-in user reads any group); write limited to `primary_owner_uid` (line 280).
- **Fix [PROPOSED], in this order:**
  1. Dry-run: count `family_groups` docs, and how many lack `member_uids` (counts only).
  2. Migration (Eric YES): add `member_uids` (array incl. `primary_owner_uid`) to every doc, built from existing membership data. App code that adds/removes members is updated in the same PR to maintain `member_uids`.
  3. Verify: 100% of docs have non-empty `member_uids`; emulator test with a copy of prod shape.
  4. Only then deploy the rule: `allow read: if request.auth != null && (request.auth.uid in resource.data.member_uids || request.auth.uid == resource.data.primary_owner_uid);`
  5. Rollback: redeploy previous rules file (one command) if any member reports lockout.
- **Test:** emulator member read allowed, non-member denied; staging check before prod. **Effort:** 0.75 d | **Risk:** Low with this order.

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
- **Fix [PROPOSED]:** The delete-account job purges P1-P11 prefixes in **both** buckets plus the default Firebase bucket, including noncurrent generations, and then the Firestore user tree. Soft delete is off on those buckets (SEC-3 Phase B), so the purge is permanent immediately; the test also asserts `gcloud storage ls --soft-deleted` shows none of the user's objects. **Test:** On staging, create a user, upload to each path, delete, then `ls -a` shows zero objects. **Effort:** 1 d | **Risk:** Medium.

### SEC-9 Account security (2FA) — [ERIC DECISION]
- **Proposal [PROPOSED]:** Optional TOTP for all users, required above a collection-value threshold. **[ERIC DECISION] threshold value — open.**

### SEC-10 Public security copy — [ERIC DECISION]
- **Current [EXISTS]:** privacy.html:324 `<h2>4. Sharing Your Information</h2>` and privacy_screen.dart:137 `_SectionHeader(title: '4. Sharing Your Information'),`. The existing text says images are processed on Gemini enterprise.
- **Fix [PROPOSED]:** After SEC-1 to SEC-3 ship, add a "Your uploads are sanitized" section. No vendor-retention claims unless sourced (see SEC-2). **[ERIC DECISION] final wording — open.**

### SEC-11 Custody location field: fixed enum, no free text
- **Current [EXISTS]:** scan_service/main.py:695 and estate_fiduciary_service.dart:71 default `'custodialLocation': 'Primary Storage / Home Safe'`; estate_models.dart:215 stores it as free `String?`; estate_planning_screen.dart:4196 displays it.
- **Fix [PROPOSED]:** replace free text with an enum: `home`, `bank_safe_deposit`, `dealer_or_vault_storage`, `with_family`, `other`, `unspecified` (default). No address, city, room or safe description can be entered. Migration maps existing values: known strings → enum, anything else → `other` with the text deleted (dry-run counts first, Eric YES). Field stays owner-only (firestore.rules:13-15 isOwner) and is excluded from shares, attorney snapshots, third-party exports and logs.
- **Test:** model rejects non-enum values; migration dry-run report counts only; share/export payload tests show the field absent. **Effort:** 0.5 d | **Risk:** Low.

### SEC-12 Marketing pixel — [ERIC DECISION]
- **Current:** No pixel was found in numista_mobile/web/index.html at 32d4b42e (R2's "commented-out pixel at 43-56" was wrong; those lines are twitter meta tags).
- **Proposal [PROPOSED]:** If a Pixel is added, send no PII and fire only after consent. **[ERIC DECISION] Pixel Purchase event value — open.**

### SEC-13 Generated appraisal PDFs (P9) [R4: M6]
- **Current [EXISTS]:** `/api/export/appraisal-pdf` (main.py:12559) builds a PDF with `generate_passport_pdf({"sender_email": req.user_email, "items": items[:50]})` (12577-12583) and archives it to `users/{req.user_email}/appraisals/Appraisal_Schedule_<ts>.pdf` in `GCS_BUCKET_NAME` default `studio-9101802118-8c9a8-uploads` (12587-12590).
- **Fix [PROPOSED]:** (a) the generator builds from an explicit field allow-list (year, denomination, mint mark, grade, cost, value, image refs); `custodialLocation`, any address-pattern text and any receipt text are excluded; a final pass runs the SEC-2 address/name patterns over the PDF text and fails closed (500, nothing stored) on a hit. (b) Archive copy is written under `users/{uid}/appraisals/` (uid, not email) only if the user opts in; default is no archive (the PDF is streamed back as today, 12594-12598). (c) `/api/estate/generate-appraisal-url` (12768) gets the same allow-list.
- **Test:** item fixture with `custodialLocation` and an address in notes → PDF text has neither; archive off by default. **Effort:** 0.5 d.

### SEC-14 No-home-address invariant
- No model, form, API schema or Firestore field may hold a street address, city+postcode pair or GPS coordinate for a user. CI grep on PRs for new fields named `address|street|zip|postal|ship_to|lat|lng|gps` in numista_mobile/lib/models and numista_backend schemas fails unless allow-listed.
- Stripe Checkout: owned by NET-706 R7 §7.4, which quotes Stripe's API reference: `billing_address_collection` has only `auto` ("Checkout will only collect the billing address when necessary") and `required`. `auto` is the lowest value; Stripe may still ask for an address when a card needs it, and that data stays at Stripe. At 32d4b42e, `git grep -n -E "address_collection|automatic_tax|customer_details" 32d4b42e -- numista_backend` returned 0 hits (run 2026-11-01), so no backend code reads or stores a Stripe address today.
- Logs: no upload filenames, OCR text or note text in logs.

### SEC-15 Free-text notes: warn and screen [R5-6]
- **Current [EXISTS]:** free text is stored on coins and estate items (e.g. `custodialLocation` before SEC-11, coin notes fields); no address screening exists.
- **Fix [PROPOSED]:** (1) every free-text input (coin notes, captions, estate notes, wishlist notes, support messages) shows helper text "Please don't type your home address here." (2) On write, the backend runs the SEC-2 address detector (libpostal + postcode patterns) on the text; a match returns 422 `ADDRESS_IN_TEXT` with the message "This looks like an address. For your safety we don't store addresses — please remove it." Nothing is saved. (3) Firestore rules deny client writes of these fields directly (writes go through the backend) or the client runs the same check before write and the backend re-checks on read-for-export. (4) SEC-3 dry-run adds a count of existing notes that match (counts only); Phase B clears the matching text after Eric YES.
- **Test:** writing "123 Main St, Springfield IL 62701" or "10 Downing Street, London SW1A 2AA" to each field is rejected; a coin note like "1921 Morgan, VF-20" is accepted. **Effort:** 1 d.

---
## 3. Prices [R5-7]
This plan sets no prices. For reference, `numista_backend/routes/payment_routes.py:50-51` at 32d4b42e (lines quoted together):
```
50|        unit_amount = 2900 if tier in ["estate", "family_estate"] else 499
51|        interval = "year" if tier in ["estate", "family_estate"] else "month"
```
That is 2900 cents per year for estate/family_estate and 499 cents per month otherwise. Other pricing is in NET-706 R7 §5. Cloud costs: **UNVERIFIED / not estimated.**

## 4. Sequence
SEC-7 → SEC-14 (CI guard) → SEC-4 (code + rules, then backfill after YES) → SEC-5 (dry-run → migrate → verify → rule) → SEC-6 → SEC-1 + SEC-2 (ship together; signed URLs and client-direct writes are cut over in the same release) → SEC-13 → SEC-15 → SEC-11 → SEC-3 (A, then Eric YES, then B) → SEC-8. SEC-9, SEC-10, SEC-12 wait on Eric. About 15 d engineering.

## 5. Lessons (from R1 74 and R2 68)
1. R2 lost about 20 points to "verbatim" blocks that were never in the file. Rule: quote only from `git show <sha>:<path>` output, with the sha in the header.
2. Bucket names were invented (`numista-vault*`). Rule: resource names come from code constants, with line cites.
3. There are two buckets, not one. Grep every `bucket(` and `generate_signed_url(` before claiming coverage.
4. Reports and logs leak through paths, because paths contain emails and filenames. Hash them.
5. Vendor assurances need a source or an UNVERIFIED label.
6. Don't cross-cite branches that have diverged (p7-v8.9 vs dev).
7. Docs-only means no commits or pushes, docs included (fbcb35a8).

## R4 lessons
8. "Quarantine then redact" is still storing the raw file. If a rule says never stored, the only safe design is in-memory redaction with reject-on-doubt.
9. Rules that narrow access ship after the data migration, never before.
10. A plan that does not set prices should not quote them.

## R3 docs-only fold (GB CoS, 2026-11-01)
Argon NET-726A SHOULD-FIX (P10/P11 client-direct uploads) folded into SEC-1. Score of record: author-of-record; independence via Argon and SAG.
