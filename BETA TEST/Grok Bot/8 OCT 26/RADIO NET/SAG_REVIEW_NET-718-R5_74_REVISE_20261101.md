<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-718-R5
SCORE: 74/100
VERDICT: REVISE

## Summary
R5 closes the R4 items in intent: in-memory intake, reject-by-default for classified documents, quarantine gone, signed PUTs removed, both code buckets named from cites, prices quoted, soft-delete limit disclosed. The written procedure does not match those closures. A numeric OCR gate stores short address images with no redaction, free-text screening has an alternate client-write path, and two resource/retention figures are asserted without a source. Not safe to treat as PASS.

## Must-fix (blocking)
1. SEC-1 step 2 is fail-open and contradicts the R5-3 closure. “≥ 10 words or any digit run ≥ 5” stores everything else after EXIF strip only. A short ship-to (UK/CA/AU postcodes, no 5-digit run, under 10 words) never enters SEC-2. Gate must be any OCR token / any readable text, not that heuristic.
2. R5-2’s “any text the parser cannot classify near a name is rejected” is not in SEC-2 steps. Post-burn check says “none of the name tokens,” which can mean only pre-burn hits. Specify: re-run full NER, label, and libpostal detectors on the burned raster; any unclassified text near a name → reject and drop. SEC-2.9 “filtered” line items must reject the upload, not strip-and-store.
3. SEC-15 (3) “or” allows client writes if the client checks, with backend re-check only on read-for-export. That stores addresses. Rules must deny client writes of those fields; backend 422 and no write is the only path.
4. Rule 3: closure table “at most 7 days at today’s setting” conflicts with §1.1 UNVERIFIED soft-delete and is not a B0 result. `studio-9101802118-8c9a8.firebasestorage.app` is not cited (legacy default is often `.appspot.com`). Mark both UNVERIFIED; discover names and retention in B0 before any `buckets update` or delete. Stripe billing address (SEC-14) is still collection under rule 1 — cite a setting that prevents it or an explicit Eric exception; do not leave it as an unaccepted residual.

## Should-fix
- Certificate type “name check only” can keep a submitter address if libpostal misses it. Same burn-and-reject bar as invoices, or reject on any unclassified line.
- Allow-list match must be exact layout hash, templates only, and must not skip post-burn address absence. Fuzzy layout match is an address bypass.
- Stored paths still use `user_email` (P1 and `users/{email}/receipts`). Use uid, as SEC-13 does for archives.
- “email/phone/card/account pattern” is unnamed. Define it or do not claim the check.
- Quote the unquoted cites used as coverage proof: `storage.rules` P10/P11, `main.py:7424-7425` (32 MB), `estate_routes.py:44`, `feedback_callable_route.py:495`, `estate_pdf_builder.py:320`.
- `unit_amount` 2900/499 is quoted; “cents” is not in those lines. Say so or cite Stripe’s unit.
- Document AI still gets bytes while retention is UNVERIFIED. R4 allowed bypass until terms are cited; restore that.
- `bytes(buf)` and OCR/PIL copies are not covered by zeroing `buf`. Fix the heading typo `## R4 closure table## R4 closure table`.

## Risks
- Phase B deletes `would_reject` objects (user data loss), gated on YES, still High.
- Objects soft-deleted before the policy change cannot be purged early; raw scans can remain until `hardDeleteTime`.
- Disabling soft-delete drops restore (called out via NET-676).
- 32 MB plus 200 dpi full-PDF rasters can OOM; 2 GiB is an unverified staging assumption.
- Small spaCy models will miss names; fail-closed rejects are safer than leaks only if classification cannot skip SEC-2.
- Wrong Firebase bucket name means SEC-3/SEC-8 never touch the real default bucket.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. **VIOLATION.** SEC-15 (3): client may write free text and backend only re-checks “on read-for-export.” SEC-14: Stripe `auto` “may still ask for an address” and that path is not an Eric exception. SEC-11 enum and “no street-address field” do not close those paths.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. **VIOLATION.** SEC-1 step 2 stores low-text images after EXIF strip only, before SEC-2. Classified documents are reject-by-default (SEC-2.6), but this gate never classifies short receipts. R5-3 closure text is not what the steps do.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. **VIOLATION.** Two code buckets and `payment_routes.py:50-51` are quoted. Unsourced: “at most 7 days at today’s setting”; bucket `studio-9101802118-8c9a8.firebasestorage.app`; “cents” as if the cited lines say it.

## Notes on verifiability
- Verifiable in-plan: sha `32d4b42e`; bucket constants `main.py:349`, `:7038`, `import_routes.py:21`, `main.py:12587`; signed PUT `main.py:7531-7538` and `import_routes.py:49-53`; wishlist `main.py:12733-12746` and `firestore.rules:250-254`; price lines `payment_routes.py:50-51`; deploy project in `deploy-production.yml:103`.
- Labeled UNVERIFIED where it matters: bucket existence, versioning, soft-delete, which bucket `gcs_lifecycle.json` binds, Document AI terms, Cloud Run secret mounts. Then the closure table still states a 7-day “today’s setting.”
- Not verifiable here: unquoted line numbers; Firebase default bucket string; soft-delete duration; Stripe `billing_address_collection` behavior (second-hand via NET-706, no doc URL in this plan); Google soft-delete sentences (URL given, not a retrieved excerpt).