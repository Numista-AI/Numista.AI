<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-718-R4
SCORE: 74/100
VERDICT: REVISE

## Summary
Architecture is right: quarantine gone, signed PUTs and client-direct writes cut, both named buckets in scope, migrate-then-rule, dry-run reports hashes/counts only, prices mostly cited, unknowns labeled UNVERIFIED. The redaction control is still fail-open. SEC-2 treats “detector saw no address” as proof there is no name or ship-to, then stores the bytes. That misses the plan’s own “not confident = drop” rule and can persist home addresses. Not a pass.

## Must-fix (blocking)
1. SEC-2 step 3 is fail-open: accept if a Ship-to/Bill-to/Sold-to block was burned **or** if no address-pattern line was found (“no addressee”). Missed OCR is not confidence. Fail closed: store only if name and ship-to were positively found and burned, or a positively identified allow-listed template has no such block **and** an independent check shows those pixels gone. Otherwise 422 and drop bytes. Do not send that object to Document AI or Firestore.
2. Name redaction is “person-name lines adjacent to” address labels only. The rule requires the person’s name redacted on the scan, including header/thank-you lines with no ship-to label. Non-US street forms (no City-ST-ZIP) never match, then hit the accept-on-miss path. Undefined name detection plus US-only patterns cannot satisfy redaction-before-storage.
3. `sanitize_upload` splits “images: EXIF strip only” from “documents (PDF or photo): SEC-2”, but does not say how a JPEG receipt, invoice photo, or support screenshot is classified. Mime-based image handling stores ship-to in the pixels. Run address/name burn on every upload path (P1–P11, including P8 and P10/P11) or reject; do not assume coin-photo vs receipt-photo.
4. SEC-3 Phase B: “purge soft-deleted copies **or wait out the window**” leaves raw scans stored. Rule text in §0.1 forbids any duration. Purge noncurrent and soft-deleted copies in both buckets and the Firebase bucket, or do not claim the invariant. Same for SEC-8, which omits soft-delete.
5. “No temp file” is not met by reading `UploadFile` into `bytes`. Starlette spools large multipart bodies to disk before the handler. Disable disk spool, forbid body logging, and define crash cleanup so /tmp is not a raw-scan store.
6. Rule 1 is not enforced. SEC-14 is a field-name CI grep (`address|street|zip|...`). Notes and other free text can still hold a street address; SEC-13 only keeps it out of PDFs. Reject or strip address-pattern text on write for those fields. “Stripe Checkout: address collection off (owned by NET-706 R6 §7.4)” is not evidenced here — quote it or mark UNVERIFIED; do not assert it is off.
7. Rule 3: §3 cites `unit_amount = 2900 if tier in ["estate","family_estate"] else 499` (payment_routes.py:50) and labels that “$4.99/mo and $29/yr”. The cited expression has no interval. Drop /mo and /yr unless quoted. “The only prices in code” needs the grep shown, not asserted.

## Should-fix
- Serve paths (main.py:8566, 8899, 8953, P6:8489) need a redaction marker and must refuse legacy/unmarked objects. “Already-redacted” is assumed, not checked. Quote P6; do not infer coverage.
- Fixture pass criteria use the same OCR that missed the address. Require a second engine or human read of stored pixels. “0 strings recoverable by OCR” is not “burned”.
- Do not call Document AI until retention terms are quoted in this plan. Burned-only plus UNVERIFIED retention is still third-party storage.
- Name the default Firebase bucket or mark the name UNVERIFIED. Enumerate every `_upload_to_gcs` `dest_path`. Widen CI beyond `upload_from_string|upload_from_file` and `generate_signed_url` PUT (resumable sessions, `blob.open`).
- Import keys stay `{user_email}/...` while appraisals move to uid. Paths leak into GCS logs. Hash or switch to uid before SEC-3 reports and serving.
- SEC-5: name the membership fields that build `member_uids`. SEC-4 dry-run should count emails that do not resolve, not only docs with `owner_email`. Paste the full wishlist `update` rule (auth + `hasOnly`), not only the `hasOnly` fragment.
- Already-issued signed PUTs live 900s (quoted expiration). Cutover must wait them out or ignore those objects.
- SEC-14 grep misses `location`, `geopoint`, `plus_code`, `coords`.

## Risks
- Fail-open gate plus Document AI on “burned” bytes ships unread ship-to to Google while retention is UNVERIFIED.
- SEC-3 deletes would-reject receipts after YES. Irreversible loss of purchase records if the detector false-rejects. High, gated — still the correct privacy side once the gate is fail-closed.
- 32 MB rasterized in memory can OOM Cloud Run; partial-write behavior is unspecified. Bucket versioning/soft-delete is UNVERIFIED, so prefix deletes can miss generations.
- Until Phase B, old `*/imports/*/raw/*` objects remain readable. Rules-before-migration is avoided for family groups; raw-object serving has no equivalent hold.
- Public wishlist `get: if true` remains. Email removal is necessary but item/value data stays world-readable.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. — **VIOLATION**. SEC-14 states the invariant, but enforcement is a name grep. SEC-2 stores a scan when no address pattern matches. Free-text notes are not blocked (SEC-13 only strips PDF output). Stripe “address collection off” is delegated, not shown. Enum `home` in SEC-11 is a category, not a street address — that part is fine.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. — **VIOLATION**. §0.1 and SEC-1 require in-memory burn and reject-on-doubt, but SEC-2 step 3 accepts “absence of any address-pattern line”, and names are only “adjacent to those” labels. Image vs document dispatch is unspecified. Soft-delete may “wait out the window” (SEC-3).
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. — **VIOLATION**. Bucket names are cited (main.py:349, :7038, :12587; import_routes.py:21) and existence is UNVERIFIED — that part complies. The $4.99/mo and $29/yr labels are not in the quoted `unit_amount` line. “Only prices in code” and Stripe address-collection-off are unsourced in this plan. No SKUs invented.

## Notes on verifiability
This review did not re-run `git show 32d4b42e`. Quoted blocks (signed PUT 7531–7538, import_routes.py:49–53, `_upload_to_gcs` 4287–4289, wishlist 12733–12746, firestore.rules:250–254) are internally consistent, not re-checked against the tree. Cited but not quoted: 32 MB at 7424–7425, storage.rules:9–12 and :19–24, Document AI 5008–5016, isOwner at firestore.rules:13–15, `gcs_lifecycle.json` age 30, receipt handlers 8566/8899/8953, P6:8489. Effort figures sum to 11.5 d as stated. NET-706 R6 is not in this document; any claim that rests on it is unverified here.