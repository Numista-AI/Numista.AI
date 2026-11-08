# GB CoS score — NET-814 Soft-404 / Public Catalog / Pricing v1.8

**94/100 — FAIL. PASS requires 95+.**

Plan: `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.8.md`
Bytes: 66079; SHA-256: `2f65da2bcd8cbaab7d0754167610aadda1c71fe0a7ad0a50d00511732dbf8892`. Matches the reviewed EDS baton hash.

Prepared 2026-11-08 08:09 AM EST (America/New_York). Delta-focused static/document review against the preceding full-plan CoS reviews and, for NET-817, the complete independent SAG response at `/workspace/sag817/SAG_API_RESPONSE_20261108-072843.md`. Writer self-scores are not evidence. Proposed snippets are not shipped code. No application build, Dart/Flutter execution, deploy, Firestore/GCS access, push, or implementation edit was performed. Scratch `git apply --check` checks only patch applicability, not application correctness.

Source evidence retained from this round's `git show` citation audit and preceding full-plan reviews: pin `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`; observed local `origin/dev` `bde8b402d34675a39f2b3b4e872cb46f71a5b32a`; locked main `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Local remote-tracking refs are not a fresh network fetch. Plan line numbers below refer to the exact reviewed file.

## Closeout of CoS-88 F1..F4
- **F1 CLOSED in scanned working artifacts.** Exact known private-promotion literal: six current plans 0, handoff tree 0. Pricing/coverage statements are now expressly PROPOSED without founder decision evidence, not accepted commercial promises. Historical commits are not redacted by this scan.
- **F2 CLOSED as a response-layer design.** 473-478 specifies generator-emitted catalog_unknown.html with served robots noindex and catalog canonical; only unknown /catalog/** falls through to it. Existing per-coin files remain ahead of rewrites, root shell remains unchanged, and HTTP 200 is honestly retained. Browser behavior has a separate browser test rather than being attributed to curl.
- **F3 PARTIAL.** The dangerous whole-private-upload-namespace acceptance is narrowed: only promoted reference/ paths in the upload bucket; Firebase originals are rejected. However the newly promised raw traversal rejection is not implemented for absolute HTTPS URLs (remaining must-fix below).
- **F4 CLOSED as a shell specification.** Section 7.3 uses fail-fast settings, non-subshell iteration, full preflight and conflict abort before any pull/push. No rollback/push was run.

## Remaining must-fix — MF-F3-RawPath
Plan 16 promises rejection of raw `.`/`..` traversal. In 719-748, pre-parse checks reject encoded dot/slash/backslash, but do **not** inspect the raw absolute path for literal dot segments. Only after `Uri.tryParse` does 735-736 inspect pathSegments. Dart's default Uri implementation already normalizes dot segments, so those checks cannot establish the claimed rejection.

Counterexample under the proposed contract: `https://storage.googleapis.com/us_mint_coin_images/a/../x.jpg` normalizes within an allowed bucket and is accepted, despite the promised raw-dot rejection. Likewise a promoted-reference path containing a/../ can normalize to the accepted reference namespace. Reject raw path dot segments before parsing/normalization, retain the decoded/normalized checks, and include an **in-allowlist normalization** negative test. Testing only traversal to an unapproved bucket does not catch this.

This is a guard-contract and test-honesty defect; it is NOT a claim that this example escapes the final bucket/prefix allowlist or proves a private-photo release. Official Dart reference: https://api.dart.dev/dart-core/Uri/normalizePath.html states that the default Uri implementation always normalizes paths. No Dart test was run.

## Source grounding
Retained `git show` evidence: pin build_image_index.py 46,55,62,303; build_currency_image_index.py 40,42,267; promote_user_photos.py 35-37,130 and verified destination 196 `reference/{program_slug}/{doc_id}.jpg`. The promoted prefix is real; passing a host guard still does not establish image release/provenance. Prior routing/main/CSP/catalog census audits remain applicable; new files and generator work are explicitly planned rather than falsely delivered.

## Rubric
Ground truth/census/marketing 19/20; user direction 20/20; routing/static HTML 19/20; public image/privacy guard 17/20; rollback/implementability 19/20 = **94/100**.

## Privacy, gates, and filing
- Count-only exact private-promotion scan: **six current plans: 0; handoff tree: 0**. Handoff scope: 2,852 text files recursively under `BETA TEST/Grok Bot/8 OCT 26`, including RADIO NET, For SAG, BATONS, INBOX and OUTBOX. The historical literal was derived internally from the previously cited historical document and never printed. No claim that repository history was erased.
- PLAN ONLY. Main locked, US-only, Stripe sandbox/OFF, alerts only and never caps. No AJ/private collector values or promotion token reproduced.
- PASS is plan readiness only: CoS >=95 -> independent SAG reading the complete current plan >=95 -> Eric's explicit typed YES. Firestore writes and deployments each retain separate YES gates. No beta retest before Field Tester evidence closes every open item.
- DONE on a review baton means review completed, not approval. This executor prepared score files on the box only: repository filing and baton renames require a sanctioned repository-editing executor; CloudAgent was absent from this executor's available tool catalog. No repository write, commit, or rename is claimed here.
