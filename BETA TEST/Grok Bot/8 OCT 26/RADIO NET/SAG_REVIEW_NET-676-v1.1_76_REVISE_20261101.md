<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-676-v1.1
SCORE: 76/100
VERDICT: REVISE

## Summary
Dry-run image consolidation plan is unusually well gated (per-phase YES, commit-pinned citations, versioning checked and found off, user buckets called out, side-guard, report email hashing). It is not executable as written: quarantine cardinality contradicts itself, GCS delete is under-gated given no versioning, and the two standing privacy rules are not operationalized even though receipts, owner photos, and EXIF GPS are in scope.

## Must-fix (blocking)
- Receipt/invoice redaction is missing. Sec 5.2 marks `users/*/receipts` OUT of remap and Sec 9 says paths are counted, never listed. That is not automatic redaction of the person’s name and ship-to address before storage. Cite the redaction implementation at `32d4b42e` or add a hard gate; do not assume it.
- Home-location data is still stored. Sec 7c states compressed and original owner photos keep the same bytes, including EXIF GPS, and defers stripping to NET-718. Sec 8 does not stop any phase if NET-718 is not live. Gate ingest and any new owner-photo keys on strip-before-write.
- Quarantine count is inconsistent. Sec 0/2/8: laptop candidates **2,184** after dropping 375 (`2,559 − 375 = 2,184`), and P1 quarantines “2,184 … COIN IMAGES only.” Sec 3 then removes **558** non-`COIN IMAGES` rows from that set. Publish one P1 count and the exact filter that yields it.
- P6 can delete live objects. Versioning is off; soft delete is 7 days (Sec 4.2). Stop condition is external-URL hits only, not a fresh Firestore/code/relative-path/index ref scan. Re-run the P0 ref match immediately before delete; any hit keeps the object. Soft delete is not the safety net.
- User-path regex can miss. Sec 3: `'…|^users/'`. A full `gs://…/users/…` or `https://…/users/…` string will not match `^users/`. State the exact subject string; match `(^|/)users/`. Re-prove the 210 candidates still have zero hits.
- P3 stop is ambiguous. “Stop if >0 side-guard hits” (Sec 8) will either always fire (110 excluded groups, Sec 5.1) or not catch a bad write. Stop only on a side-mismatch in the apply diff.

## Should-fix
- Exact-string replace (Sec 5.3) can corrupt a longer URL if the old value is a prefix or substring. Require URL/token boundaries; review `code_remap_diff.csv` for partial hits.
- Filename grammar ≠ index key (Sec 1). P2 YES must include the mapping table; it is not in the phase gate.
- Sec 9 `sha256-first8` of email is reversible against the known user list. Omit the segment or use a keyed hash. Apply the same rule to external-URL search artifacts (Sec 4.2).
- Define “FT”, p7-gate, and “measurably better” (Sec 7d) with numeric thresholds before P5.
- Side guard covers obverse/reverse only. Edge, `privy_detail`, and `ogp` can still land in the wrong field.
- Do not mint new public `storage.googleapis.com` URLs for the check if the object is not already public.

## Risks
- Irreversible GCS loss: no versioning, 7-day soft delete, originals left as the only copy until P6.
- Wrong-side or wrong-coin cards if remap escapes the 110-group exclusion.
- User objects pulled into quarantine if the regex subject is a full URI.
- Promoted “collector” images can still carry GPS/email if NET-718 slips and re-encode is not proven.
- Truncated email hashes plus coin ids re-identify users in dry-run CSVs.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. **NOT ADDRESSED.** Sec 9 bars addresses in reports, but Sec 7c records that owner-photo uploads keep EXIF GPS in both copies and does not gate storage on stripping. No prohibition on collecting a home address elsewhere in the plan.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. **NOT ADDRESSED.** Sec 5.2 (`users/*/receipts` … OUT) and Sec 9 (paths counted, never listed) never state or verify pre-storage redaction of name and ship-to.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. **COMPLIANT** on sourcing intent (commit `32d4b42e`, `buckets.txt`, `gcloud storage buckets describe`, named CSVs; no prices or SKUs). **Not reliable as stated:** 2,184 vs 558 (Sec 3 vs Sec 8) is an unresolved figure, and v1’s versioning assumption is correctly retracted rather than reused.

## Notes on verifiability
- Arithmetic that checks: `2,559 − 375 = 2,184`; `2,556 − 290 = 2,266`; `153 + 30 + 9 = 192`; soft-delete `604,800 s = 7 days`.
- Not checkable from this text alone: 210 objects / 456,547,455 bytes, 110 side groups, 290 stripped rows, 7,422 images / 5,959 docs, 15,895 greysheet URLs, collision filenames. Cited to files, not embedded.
- `gcs_dedupe.ps1` is untracked; the regex change is not at `32d4b42e`. Line cites for Dart are pinned to that commit; treat them as the only code evidence.
- “Recounted 1 Nov” is an assertion, not a command log. Do not execute P1/P6 on the prose counts until the CSVs and the regex subject are attached to the YES packet.