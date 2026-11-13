<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-718-R3
SCORE: 71/100
VERDICT: REVISE

## Summary
Path inventory, sha-pinned quotes, two-bucket scope, gated backfill, and UNVERIFIED labels are real improvements over a fabricated plan. The design still stores raw uploads before redaction, does not stop home-address collection, and prints a price table with no source. Not safe to build as written.

## Must-fix (blocking)
- SEC-1/SEC-2 violate redaction-before-storage. Signed PUT to `quarantine/` (24 h) and “only the quarantine copy exists” until user review keep unredacted name and ship-to in durable storage. That also breaks §0 rule 1 (“no raw or unredacted user upload may remain in storage”) and SEC-2’s “original is never kept.” Sanitize in memory (or an ephemeral non-persisted buffer) and write only the burned object. If name or ship-to is not confidently burned, drop the bytes; do not queue or store the raw file.
- Rule “no user home addresses are ever collected” is unmet. Invoice/appraisal ingest, Document AI egress, the review UI, and `custodialLocation` can all obtain a home address. Prohibit street-address fields, strip them from logs/shares/exports/queue payloads, and do not send raw address-bearing bytes to a vendor until retention terms are cited in this plan—not deferred to a PR.
- §3 prices are unsourced and not marked UNVERIFIED, against §0 rule 2. Cite `git show 32d4b42e:<path>` for every tier, top-up, and 6× export figure, or delete the table. `$109` and `$150` do not match the `.99` monthly pattern; treat as suspect until quoted.
- Existing `public_wishlists` still expose `owner_email` (`allow get: if true`). Add a dry-run-then-strip backfill; rules-only forward fix leaves the leak.
- SEC-5 tightens reads to `member_uids` / `primary_owner_uid` with no deploy-after-migration order. Rules-first locks out every family group.
- P9 appraisal PDFs (`main.py:12587-12588`) and P6 (`main.py:8489`) are outside the sanitize call list (P1, P2, P4, P5, P8, 7543 fallback). Any write that can hold a name or ship-to must use the same pre-store burn, including generated appraisals.

## Should-fix
- Quote `storage.rules:9-12` and `:19-24`, `gcs_lifecycle.json`, and the Firebase bucket host. `studio-9101802118-8c9a8.firebasestorage.app` is asserted, not quoted. Deny client writes to final prefixes, not only public read on `quarantine/`.
- SEC-7 checks Firestore rules drift only. `storage.rules` is the P10/P11 control and is uncovered.
- Drop or cite “existing hash-dedupe” and the Gemini-enterprise paraphrase (`privacy.html:324` is cited, not quoted).
- `sha256(object_path)` is reversible for predictable `{email}/…/{filename}` paths. HMAC with a secret, or omit path hashes.
- State whether a delete-account job already exists (no cite) before SEC-8 extends it.
- 24 h lifecycle is not a proposed config bound to both buckets plus the Firebase bucket. Do not use lifecycle as the privacy invariant.

## Risks
- Worker or lifecycle failure leaves raw invoices in GCS. Fail-closed discard is the only safe default.
- Document AI retention is UNVERIFIED; raw PII would leave the project before any local burn.
- `hasOnly` and `allow create: if false` will break current client reservation/create paths if field names differ from the quote.
- Phase B is destructive across two buckets, generations, and soft-delete; B0 is still UNVERIFIED. A wrong prefix (`users/*/**`) can wipe non-import objects.
- Re-encode breaks byte-identical dedupe and can change PDF text extraction used by the SEC-2 test.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. **VIOLATION.** SEC-2 ingests “street addresses” on invoices and appraisals; quarantine and the review queue retain them; SEC-11 keeps `custodialLocation` (`scan_service/main.py:695`, default `'Primary Storage / Home Safe'`). No prohibition on collecting a home address.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. **VIOLATION.** SEC-1: “upload to `quarantine/` with a 24 h lifecycle delete. A backend worker sanitizes into the final path.” SEC-2: low-confidence files are “not finalized” while “only the quarantine copy exists.” Redaction is after a durable write and not automatic.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. **VIOLATION.** Bucket constants in §1.1 are line-cited. §3 prices (Copper `$4.99`/`$49.99` through Gold `$15.99`/`$150`, top-up `$5`, exports `$29.94`/`$53.94`/`$65.94`/`$95.94`) have no cite and are not UNVERIFIED. No SKUs appear.

## Notes on verifiability
- Verifiable as written: quoted blocks for signed PUT (`main.py:7531-7538`), `import_routes.py:49-53`, `_upload_to_gcs` (`4287-4289`), EXIF pop (`4269-4272`), wishlist create (`12733-12746`), `public_wishlists` rules (`250-254`), pinned to `32d4b42e`. Branch non-citation and the `fbcb35a8` note are consistent.
- Not verifiable from this text: §3 prices; Firebase host string; `gcs_lifecycle.json` body; storage.rules text; Gemini sentence; “existing hash-dedupe”; Cloud Run secret mounting (correctly UNVERIFIED); that either GCS bucket exists (correctly UNVERIFIED).
- Annual figures are internally inconsistent with ×10 of the monthly column (`10.99×10=109.90` vs `$109`; `15.99×10=159.90` vs `$150`). Export column matches monthly×6 only if the monthly numbers are true. Do not treat §3 as evidence.