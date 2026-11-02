# SECURITY PLAN — NET-718 R4 — USER PROTECTION (Images, Imports, Sharing, Secrets)
**Author:** GB CoS (Grok Bot). R4 = FIX-ONLY round closing every must-fix in SAG_REVIEW_NET-718-R3_71_REVISE_20261101.md.
**Date:** 2026-11-01 ~9:30 PM ET | **Status:** DOCS-ONLY. No code changed, nothing committed, pushed or deployed. A PASS still needs Eric's typed YES.
**Source of truth:** `origin/dev` **32d4b42e** (`git show 32d4b42e:<path>`, re-read 2026-11-01 evening on EDS_Laptop). Line numbers are 1-based.
**Not cited:** origin/p7-v8.9 (diverged from dev). **Pending Eric's call:** AG docs commit fbcb35a8 on p7-v8.9 (keep or revert); no action taken.

## R4 closure table (SAG R3 must-fixes)
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
1. **The raw scan is never stored, anywhere, for any length of time.** Redaction happens in memory on the backend; only the blacked-out copy is written. If redaction is not confident, the upload is rejected and the bytes are dropped. This covers every upload path, signed URLs, client-direct writes, old stored versions and soft-deleted copies.
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

### SEC-1 Sanitize in memory before the only write (images: EXIF/GPS strip; documents: redaction)
- **Current state [EXISTS]:** only HEIC gets GPS stripped (`_convert_heic_to_jpeg`, main.py:4255-4279; lines 4269-4272 pop tag 0x8825). JPEG/PNG/WebP/PDF are written unchanged: `/api/import/upload` writes `file.file` straight to `{user_email}/imports/{session_id}/raw/{safe_name}` (main.py:7433-7441); `_save_to_gcs` (7373-7385) and `_upload_to_gcs` (4282-4290) write the bytes they are given; `/api/import/start` hands clients a signed PUT to the same raw path (7531-7544).
- **Fix [PROPOSED]:** one function `sanitize_upload(data: bytes, mime: str) -> bytes | Reject`, run in the request handler on bytes held in memory (FastAPI `UploadFile` read into a `bytes` object; max 32 MB already enforced at main.py:7424-7425). No temp file, no GCS write, no Firestore write before it returns.
  - **Images (all formats incl. HEIC/phone/webcam/microscope):** decode → apply EXIF orientation to pixels → re-encode from pixels only. Output carries no EXIF/XMP/IPTC (so no GPS, device serial or owner name). PNG text chunks and WebP EXIF/XMP chunks are not written.
  - **Documents (receipts, invoices, appraisals the user uploads; PDF or photo):** rasterize each page in memory → SEC-2 redaction → write a flattened image-only PDF. No text layer from the original survives.
  - **Reject path:** `Reject` returns HTTP 422 `REDACTION_NOT_CONFIDENT` (or `UNSUPPORTED_DOCUMENT`); the handler drops the bytes and writes nothing (no object, no Firestore doc, no log line containing filename, path or extracted text).
  - **Call sites (all must call it before any write):** main.py:7441 (import upload), 7384 (`_save_to_gcs`, callers incl. 7931 and partner file 8404-8405), 4289 (`_upload_to_gcs`), routes/estate_routes.py:44, routes/feedback_callable_route.py:495, scan_service/estate_pdf_builder.py:320, and the HEIC path. CI check: `git grep -n "upload_from_string\|upload_from_file"` in numista_backend must show each hit wrapped (allow-list file in repo).
  - **Signed URLs removed:** `/api/import/start` (main.py:7531-7544) stops issuing PUT URLs and returns `upload_url="/api/import/upload"` for every file (the existing fallback at 7543). routes/import_routes.py:50-53 (signed PUT to `imports/{user_id}/...` in `studio-9101802118-8c9a8-uploads`) is replaced by the same backend upload. CI: grep fails on any `generate_signed_url(` with `method="PUT"`.
  - **Client-direct Storage (P10 `users/{email}/**`, P11 `support_screenshots/`):** storage.rules set `allow write: if false` for those paths; the client (coin_detail_screen.dart:4402-4410, my_collection_screen.dart:5440-5446, support screenshot upload) posts to the backend sanitize endpoint instead. Reads unchanged.
- **Test:** fixtures (JPEG+GPS, PNG tEXt, WebP XMP, HEIC+GPS, receipt PDF with a known name and ship-to, low-confidence blurry receipt) through every endpoint. Read back stored objects: exiftool shows no GPS/metadata; OCR of stored receipt finds neither the name nor any address line; low-confidence fixture returns 422 and `gcloud storage ls` shows **no object** for it; signed-PUT grep is empty; client-direct write to `users/...` is denied in the emulator.
- **Owner:** Backend + Mobile | **Effort:** 2.5 d | **Risk:** Medium (re-encode changes bytes; dedupe must hash the sanitized output; 32 MB in-memory on Cloud Run needs memory headroom checked).

### SEC-2 Receipt/invoice redaction: name and ship-to burned in memory; not confident = rejected
- **Current state [EXISTS]:** Document AI is called on raw bytes (main.py:5008-5016: `DocumentProcessorServiceClient`, `RawDocument(content=file_bytes, ...)`, `name=DOCUMENT_AI_PROCESSOR_PATH`), reached from `/api/process_invoice` (main.py:2023). There is no image/document redaction. (`git grep -i redact` finds only the support-ticket field redaction described in numista_backend/SUPPORT_WORKFLOW.md:64-82, which hides Firestore fields from support staff and does not touch scans.)
- **Fix [PROPOSED]:**
  1. **Detect in memory, on the server, before any vendor call:** local OCR (Tesseract via `pytesseract`, runs in the Cloud Run container; no data leaves) produces word boxes. Rules mark: the block after "Ship to / Sold to / Bill to / Deliver to / Name" labels; any line matching a US street-address pattern (number + street word, PO Box, City-ST-ZIP); person-name lines adjacent to those; emails; phones; card/account numbers (Luhn / ≥8 digits).
  2. **Burn:** fill every marked box solid black on the raster (not an annotation), then flatten to an image-only PDF.
  3. **Confidence gate:** accept only if (a) OCR mean confidence on the page ≥ threshold T, and (b) a "Ship to"/"Bill to"/"Sold to" label was found and its block burned, or the document type is one with no addressee (e.g. a US Mint order page with no address block, detected by the absence of any address-pattern line). Otherwise **reject (422), drop bytes, store nothing**; the UI tells the user to retake the photo or crop out the address first. No review queue. T is set on staging from the fixture set (start 80); **[ERIC DECISION]** only if he wants a different trade-off.
  4. **Document AI** (parsing line items) runs only on the **burned** output. Until Google's Document AI data-usage terms are cited in this plan, that is the only way bytes reach it. **UNVERIFIED:** Document AI retention terms.
  5. Extracted fields saved to Firestore receipts docs (main.py:7361-7366 writes `line_items`, `linked_coin_ids`, `unlinked_items`) must not contain name/address: the parser output is filtered through the same address/name patterns before the write.
- **Test:** 20-fixture set (US Mint, eBay, APMEX, dealer handwritten, phone photo at angle). Pass = 0 name/address strings recoverable by OCR from any stored object; every fixture is either stored-and-clean or rejected-with-nothing-stored. Log scrub test: no address pattern in Cloud Run logs for the run.
- **Owner:** Backend + Mobile (error message) | **Effort:** 3 d | **Risk:** Medium (false rejects annoy users; better than a stored address).

### SEC-3 Backfill existing raw objects (dry-run first)
- **Scope:** both user buckets (`numista-uploads-studio-9101802118-8c9a8`, `studio-9101802118-8c9a8-uploads`) and the default Firebase bucket, prefixes `*/imports/*/raw/*`, `imports/*`, `users/*/**`, `support_screenshots/*`.
- **B0 (read-only):** `gcloud storage buckets describe` each bucket; record versioning/soft-delete. (`gcs_lifecycle.json` in repo root: Delete, age 30, isLive false; which bucket it is applied to is UNVERIFIED.)
- **Phase A dry-run:** stream each object into memory, run `sanitize_upload`, discard output. Report = `sha256(path)`, `sha256(content)`, mime, size, exif_present, address_detected (bool), would_reject (bool). No paths, emails, filenames or text.
- **Phase B (Eric YES only):** for sanitized-OK objects write the clean version and delete the original; for would_reject receipts **delete the object** (keeping an unredacted scan is not allowed); delete all noncurrent generations; purge soft-deleted copies or wait out the window stated from B0.
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
- **Fix [PROPOSED]:** The delete-account job purges P1-P11 prefixes in **both** buckets plus the default Firebase bucket, including noncurrent generations, and then the Firestore user tree. **Test:** On staging, create a user, upload to each path, delete, then `ls -a` shows zero objects. **Effort:** 1 d | **Risk:** Medium.

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

### SEC-14 No-home-address invariant [R4: M2]
- No model, form, API schema or Firestore field may hold a street address, city+ZIP pair or GPS coordinate for a user. CI grep on PRs for new fields named `address|street|zip|postal|ship_to|lat|lng|gps` in numista_mobile/lib/models and numista_backend schemas fails unless allow-listed (e.g., Stripe `billing_address_collection` setting itself).
- Stripe Checkout: address collection off (owned by NET-706 R6 §7.4).
- Logs: request logging must not include upload filenames or OCR text (SEC-2 log scrub test).

---
## 3. Prices
This plan sets no prices and quotes none. For reference only, the only prices in code at 32d4b42e are `unit_amount = 2900 if tier in ["estate","family_estate"] else 499` (routes/payment_routes.py:50) — $4.99/mo and $29/yr. Pricing v3.2 lives in NET-706 R6 §5 with source tags. Implementation cloud costs: **UNVERIFIED / not estimated.**

## 4. Sequence
SEC-7 → SEC-14 (CI guard) → SEC-4 (code + rules, then backfill after YES) → SEC-5 (dry-run → migrate → verify → rule) → SEC-6 → SEC-1 + SEC-2 (ship together; signed URLs and client-direct writes are cut over in the same release) → SEC-13 → SEC-11 → SEC-3 (A, then Eric YES, then B) → SEC-8. SEC-9, SEC-10, SEC-12 wait on Eric. About 11.5 d engineering.

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
