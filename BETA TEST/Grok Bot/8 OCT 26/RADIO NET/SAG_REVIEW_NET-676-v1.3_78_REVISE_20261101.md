<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-676-v1.3
SCORE: 78/100
VERDICT: REVISE

## Summary
Docs-only image-consolidation plan with per-phase YES gates, commit-pinned code quotes, and an explicit refusal to move receipts or owner-photo objects. Safety intent is real, but the controlling privacy gate and the P3 write-abort set do not match the protections stated elsewhere, so a later YES could authorize the wrong write.

## Must-fix (blocking)
- Sec 8 G-718 pass text (v1.3 S1) requires only NET-718 R5 name/address burn-in, reject-if-no-address, no-disk-write, and soft-delete off. It drops EXIF/GPS strip. Sec 7c still says the strip “belongs to NET-718 R4 SEC-1” and that G-718 is that gate. P5 (new owner-photo keys / promotion) can be declared unblocked from Sec 8 alone while GPS remains in stored images. One gate definition: R5 (not R4) must include all-format in-memory EXIF/GPS strip-before-write, and 7c must match it.
- P3 abort is narrower than Sec 3 protection. Abort matches only `(^|/)users(/|%2F)` and paths under `receipts`, `invoices`, `appraisals`, `binder_scans`, `estate_reports`. Sec 3’s pattern also covers `uploads|user-content|user_contributed|firebasestorage\.app`, and Sec 2 names protected buckets `numista-uploads-studio-9101802118-8c9a8`, `studio-9101802118-8c9a8-uploads`, and `studio-9101802118-8c9a8.firebasestorage.app`. Those are not abort conditions. `import_sessions` is OUT in Sec 5.2 and missing from the abort list. Owner-photo fields already quoted (`url`, `original_url`, `storage_path`, `original_storage_path` at `coin_model.dart:40` and `coin_detail_screen.dart:4412-4417`) are not marked OUT, while S2 defines “user content” as whatever Sec 5.2 marks. List those fields OUT now; abort on the full Sec 3 pattern, all three protected buckets, and any field not on an explicit P3 allowlist.

## Should-fix
- Sec 10 says “hash user path segments”; Sec 9 forbids hashing emails and uses `users/<redacted>/`. Make Sec 10 match Sec 9.
- P2 stop says “user regex” without binding it to the Sec 3 pattern plus protected bucket names.
- `gcs_dedupe.ps1` is untracked and not at `32d4b42e`. Pin the reviewed script in-repo before any YES P0.
- Sec 4.2 external-URL check is still `[PROPOSED]` while P6 depends on it. Make it a mandatory same-day P6 predicate, not optional.
- Firestore export target `gs://numista-firestore-exports/` has no field/collection limit. State export = remap collections only; exclude OUT collections and any name/address/receipt fields.
- Sec 3 item 4 “7,422 images / 5,959 user docs” is carried `[v1]` with no source file. Mark provisional or cite the scan.
- Laptop path strings disagree: `COIN IMAGES` (Sec 1) vs `Coin Images` (Sec 3 script path).

## Risks
- Versioning is off (Sec 4.2). P6 rollback is “None reliable”; 7-day soft delete does not cover a missed ref (email, CDN, third-party embed).
- P3 fail-closed side drops can stall the batch; that is correct, but a bad `side` column stops all writes.
- Promotion “re-encode from pixels / no user id” (Sec 7d) is untested in this plan.
- `found_by` intake metadata can capture a person’s name into object metadata.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. — COMPLIANT. Intake metadata (Sec 6) is source_url, license, year, view_type, mint_code, found_by, date. Sec 9: “No names, emails, addresses or receipt contents in any report.” No address-collection field is added. Residual: GPS strip is not in the Sec 8 gate (must-fix); that is location metadata, not a stated address field.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. — COMPLIANT for this plan’s actions. “This plan moves, copies or remaps no receipt, invoice, appraisal or binder-scan object and adds no receipt path” (v1.2 M1). Sec 8: P0–P4 “never touch receipts, invoices, appraisals, binder scans or owner photos,” and G-718 pass requires “the person's name (anywhere on the page) and ship-to / bill-to / deliver-to address” burned before any user-content write, else reject and store nothing. Redaction code is not in this plan; it is a hard gate on NET-718 R5. Plan also states current code does not redact (`main.py:5008-5016` raw bytes).
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. — COMPLIANT. No prices or SKUs. Bucket names and versioning/soft-delete cited to `buckets.txt` and `gcloud storage buckets describe` (1 Nov 2026). Counts tied to named artifacts (`gcs_keep_copy_map.csv`, `firestore_image_refs_summary.txt`, `code_bucket_refs_20261031.csv`) or marked provisional (210; 1,626 bytes “not yet recounted”). Code quotes pinned to `git show 32d4b42e`. Arithmetic 2,559 − 375 − 558 = 1,626 and 179 + 31 = 210 is internal only.

## Notes on verifiability
- Reviewer cannot recompute 210 / 456,547,455 / 290 / 1,626 bytes: sources are local CSVs plus an untracked ps1, not git at `32d4b42e`.
- “0 match the v1.1 user regex” (Sec 2) is not a proof under the v1.2/v1.3 pattern; M5 already calls 210 provisional. Keep that wording in the P6 row.
- Line cites (`coin_detail_screen.dart:4402-4403`, `firebase_options.dart:55`, `storage.rules:9-12`, `build_image_index.py:52-60`) are checkable only against commit `32d4b42e`, which the plan names.
- “about 1-2 dev days” (Sec 7) is an unsourced estimate, not a measured figure.