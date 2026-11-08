# GB CoS round-3 score — NET-814 Soft-404 / Public Catalog / Pricing v1.9

**96/100 — PASS. Threshold >=95. Remaining must-fixes: none.**

Reviewed plan: `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.9.md`
Bytes: 67948; SHA-256: `665ae9ba510b3c5f7c874e0fbddcf1c18d5c6ecc814bcc7c913bb85d20ac00a5`. Independently matches the 20261108-0813 review baton.

Prepared 2026-11-08 08:19 AM EST (America/New_York). **PLAN-ONLY, delta-focused independent CoS review.** Exact EDS files were copied verbatim, fingerprinted, and compared line-for-line with the round-2 reviewed artifacts. Every round-3 added/changed span was reviewed against the round-2 must-fixes. Unchanged source grounding relies on the preceding full-plan/citation audits; it is not relabeled as a fresh full-repository investigation. Writer self-scores and baton claims are not approval.

No application code edited or executed, no Dart analyzer/Flutter tests/builds, no Firestore/GCS access, deployments, commits, pushes, external sends, or EDS filing/renames. The only execution was independent box-side document comparison and WCAG arithmetic. Narrow read-only `git show` source spot-checks confirmed collection surface colors at pin `4d17ca5e`, lines 211 and 3029-3032. Three distinct full object IDs retained across the four plans resolve; unresolved 0. `origin/main` remains `9f04550a45fa4da082ba8948c2d89a521a90fa45`.

## Round-2 MF-F3-RawPath: CLOSED
- The actual helper at **726-729** inspects the raw URL string, excludes query/fragment suffixes, splits on literal '/', and rejects exactly '.' or '..' segments.
- **733** calls that helper before local-asset acceptance and before **743** Uri.tryParse. Thus parsing cannot normalize away evidence before the rejection check. Encoded dot/slash/backslash and post-parse decoded checks remain in place.
- The actual test examples at **1141-1145** add all required categories: within-allowed-bucket a/../; ./; promoted-reference a/../; cross-allowed-bucket ../. These are the cases that distinguish true raw rejection from merely rejecting the final unapproved bucket.
- The helper deliberately excludes query/fragment content; a dot string in a query is not a path traversal segment. No source-normalization loophole from round 2 remains in the specified check ordering.

## New-content / inherited controls
No new bucket/source, image-release permission, catalog fact, price or founder approval was introduced. The newly added URLs are explicitly negative synthetic test cases, not assertions that storage objects exist. Narrowing to promoted reference/ paths, Firebase-original rejection, per-image release/provenance gates, served noindex unknown document, HTTP-200 limitation and fail-fast rollback remain unchanged from the reviewed version. The new raw-path helper is explicitly proposed code, not a claimed shipped API.

**Remaining must-fixes: none.** Nonblocking handoff hygiene: the H1 title says v1.9, while the secondary title, Document Tracking, mirror path and old Review Baton fields still name v1.8. Current v1.9 baton and matching SHA identify the reviewed bytes. Reconcile these labels before a later polished delivery; do not mistake the stale paths for an instruction to overwrite/reuse older approval.

## Rubric
Ground truth/census/marketing 19/20; user direction 20/20; routing/static HTML 19/20; public guard/privacy 19/20; rollback/implementability 19/20 = **96/100 PASS**.

## Privacy, authority and next gate
Promo scan counts only: **current four plans 0; handoff tree 0** (2,867 text files recursively under `BETA TEST/Grok Bot/8 OCT 26`). The exact previously identified private literal was derived internally from its cited historical document and never printed. History was not rewritten; a zero working-file count is not proof of erased history or a universal unknown-secret detector.

Main locked; US-only; Stripe sandbox/OFF; alerts only, NEVER caps; no AJ identifying values or private tokens reproduced. PASS means plan readiness, not runtime correctness, deployment permission or beta retest clearance. Next: independent SAG must read the **entire exact current plan**, score >=95 separately per plan, then Eric's typed YES. An older-version score or this delta summary is insufficient. Firestore writes and deploys each retain separate YES gates; no beta retest before Field Tester evidence closes every open item.

Files are prepared only in `/workspace/round3-scoring/scores/`. Eric/parent will file them using `FILING_MANIFEST.json`. No destination file or baton has been modified by this executor. DONE on a review baton denotes completed review, never approval.
