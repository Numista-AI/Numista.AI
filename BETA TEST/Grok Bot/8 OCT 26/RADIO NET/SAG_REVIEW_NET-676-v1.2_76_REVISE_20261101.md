<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-676-v1.2
SCORE: 76/100
VERDICT: REVISE

## Summary
Dry-run image-consolidation plan with per-phase YES gates, honest versioning findings, and several v1.1 fixes (provisional 210, email redaction in reports, no new public URLs). It does not close the receipt-redaction rule, and the apply/delete specs are still fail-open where prose and the phase table disagree.

## Must-fix (blocking)
1. Rule 2 is not closed. M1/G-718 admit no redaction exists and Document AI (`main.py:5008-5016`) gets raw bytes, then defer to “in-memory redaction, raw never stored, reject if not confident.” That text never requires automatic redaction of the person’s name and ship-to address before any storage. Non-touch of receipts in this plan is not that control. Do not record M1 closed. G-718 pass criteria must name those two fields, reject-and-store-nothing if redaction is not confident, and point at the staging tests that assert them.
2. P3 stop column does not enforce the user-content ban. `users/*/coins` image fields are IN (Sec 5.2); stop is only side mismatch and FT fail (Sec 8). A table marked OUT is not a writer check. Apply must abort the batch if any old/new value matches the user regex, or the doc path is receipts, invoices, appraisals, binder scans, estate reports, or owner-photo fields.
3. Side guard is not fail-closed. Existing objects are not renamed to the grammar (Sec 1), but P3 stops only when a detected side disagrees with the target field (M6/Sec 8). If side is missing, ambiguous, or not in the 6-value enum, stop that row. Side must come from a clean-map column, not an ad-hoc filename guess.

## Should-fix
- Sec 2 still presents laptop candidates as 2,184 / 1,367,270,043 bytes. Operative P1 set is 1,626; bytes for that set are unknown. An executor using Sec 2 can quarantine the 558 non-coin rows.
- Phase table still says delete “210”. Count and 456,547,455 bytes are provisional until P0 re-proves the new regex (M5). P6 input must be “P0 count only.”
- Sec 10 says “hash user path segments”; Sec 9 forbids hashing emails because a short hash is reversible. Align Sec 10 with `<redacted>`.
- Appraisals are in the G-718 ban but absent from the Sec 5.2 IN/OUT table. Add a row or “none found in the 31 Oct scan; P0 must confirm.”
- P2 object names are unspecified (preserve basename vs new grammar). Fail closed if year/program/subject/side cannot be derived. Do not invent them. Index key order (`year…program_side`) differs from filename grammar (`year_program_subject_side`); the P2 mapping table must be a hard input, not a note.
- `gcs_dedupe.ps1` is untracked at `32d4b42e`. Pin the full script in-repo before P0 so the regex cannot drift.
- P6 rollback is “None reliable”; versioning is off; soft delete is 7 days. Keep a verified-md5 quarantine copy for longer than soft delete before any delete. Do not treat soft delete as the safety net.
- Interim rule “Eric-YES'd plans exempt (no-clobber, no deletes)” can be read as allowing deletes. State that YES does not waive G-718 or the same-day ref scan.

## Risks
- Live app still stores owner-photo EXIF/GPS (`coin_detail_screen.dart:4404` and `:4409`, same bytes, no strip). This plan does not remove those objects.
- Relative paths and `%252F` double-encoding can miss the `(^|/)users(/|%2F)` pattern; a miss on the P6 scan deletes a live object with no reliable restore.
- Evidence base is local/untracked (`buckets.txt`, CSVs, `firestore_image_refs_summary.txt`), not `git show 32d4b42e`.
- Remap of `users/*/coins` URL fields can swap or drop card images if the clean map is dirty.
- Emails remain in stored `users/$userEmail/` object names even if reports redact them.
- Document AI raw receipt path keeps running in production regardless of this dry-run.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. — COMPLIANT. Sec 9: “No names, emails, addresses or receipt contents in any report; receipts/binder_scans/estate paths are counted, never listed.” No step collects a home address.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. — VIOLATION. M1: “No redaction exists at 32d4b42e … Document AI at main.py:5008-5016 receives raw bytes.” G-718 requires only “in-memory redaction, raw never stored, reject if not confident” via NET-718, and does not name person or ship-to address, or implement before-storage redaction.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. — COMPLIANT. Bucket names and versioning are tied to `buckets.txt` and `gcloud storage buckets describe` (Sec 2, Sec 4.2). No prices or SKUs. 1,626 is shown as 2,559 − 375 − 558; the 1,367,270,043 byte figure is explicitly not the P1 total; 210 is marked provisional. Counts are cited, not re-proven here.

## Notes on verifiability
- Line citations (`main.py:5008-5016`, `coin_detail_screen.dart:4402-4417`, `storage.rules:9-12`, `build_image_index.py:52-60`) are assertions against `32d4b42e`. This review did not re-run `git show`.
- 22,085 objects, 210 / 456,547,455 bytes, 290 stripped rows, 5 collisions, 110 side groups, 7,422 refs, 192 files, and 15,895 greysheet URLs depend on local scans/CSVs not included in the plan. Arithmetic is internally consistent; accuracy is not independently verifiable.
- `gcs_dedupe.ps1:4` is admitted untracked, so that citation is not verifiable from the locked commit.
- P0 recomputation is required before any YES P1/P6. Until those reports exist, treat every action count as unverified.