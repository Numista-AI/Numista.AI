# GB CoS score — NET-816 Catalog v1.8

**60/100 — FAIL.** Required pass: 95+. Not ready for SAG pass / Eric YES / execution.
Reviewed 6 Nov 2026, approximately 9:38–9:43 PM EST (America/New_York).

## Scope and method
Read-only document review and narrowly targeted `git show`, `git grep`, `git ls-tree`, `git log`, `git diff` and hash/existence checks on EDS_Laptop. No laptop writes, fetch, checkout, tests, build, deployment, database access, messages or push. Reports written only to the box. Compilation and runtime outcomes are not claimed.

Repository: `C:\Users\ericd\Documents\MyVertexProject`.
Plan: `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.8.md` (480 lines).
Unless qualified, source citations below mean **b0b058087f1492244a0c0b769e126b38ac1ba06c**, not the working tree. Plan citations mean the delivered local plan.
Observed refs: origin/dev **eb23e011d1e25446e256518e5065b4a989aaba17**; origin/p7-v8.9 and HEAD **4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235**; origin/main **9f04550a45fa4da082ba8948c2d89a521a90fa45**. `git diff b0b05808 origin/dev -- numista_mobile/lib numista_mobile/assets numista_mobile/firebase.json` was empty: the pinned app evidence remains applicable despite documentation-only ref drift.

Read prior CoS-64 and SAG-67 files in RADIO NET, the 1:35 PM scope add, NET-818/819 and the box audit `/workspace/site-audit-2026-11-06/THANKSGIVING_GAP_AUDIT_06NOV.md`. These were evidence, not execution authorization.

## Numbered blocking must-fixes

1. **Replace the cross-branch deletion instructions with complete, branch-specific structural diffs.** Plan lines 338–356 repeat p7 line numbers while targeting dev. On actual pinned dev, `numista_mobile/lib/screens/my_collection_screen.dart:3531–3546` is Group-as-Set / Close UI, NOT Google Images; the inspector invocation is at **3796**, method at **5502**, Kaggle caption at **5592**. `_onSearchGoogle` is absent from pinned dev (git grep); it must not be blindly deleted using p7 coordinates. Even on p7 @4d17ca5e, the specified Google widget deletion **3531–3546** leaves the closing spread at **3547–3548**, and handler deletion **4386–4405** leaves its closing brace at **4406**. Both are malformed edits. The inspector method range **5549–5645** is accurate for p7, not dev. Set a single owner for NET-816/817 shared changes. `photo_sharing_service.dart:12` is a comment naming ingestion, not proof of ingestion logic to remove. Supply exact reviewed code/data deletion lists and require Eric YES on that exact list; a general build YES is not that gate.

2. **Guard every image renderer, not just the browse card, with an owned-storage policy reconciled to actual CSP.** Plan lines 198–222 fixes helper scope in `_CatalogCard`, but `catalog_browse_screen.dart:903–923` (`_buildModalImage`) independently passes the raw URL to `Image.network` and is unmodified by the plan. The claimed rejection of all external requests (plan 46–49) is therefore false. The guard permits plain HTTP (206), any bucket at `storage.googleapis.com` (209,217), and virtual bucket subdomains (210–211,218–219); `numista_mobile/firebase.json:283–284` allows HTTPS **storage.googleapis.com**, not those virtual subdomains. Fixed production hosts are not equivalent to relative same-origin on preview. Specify HTTPS, verified bucket/path ownership, relative/same-origin handling and tests for card AND modal, primary AND type images, malformed and unowned GCS URLs. Do not widen CSP to third-party hotlinks. Rehosting also needs a source/license manifest and separately gated uploads, not just replacing URLs.

3. **Finish the known-error fix across both data paths and real callers, requiring known matching series AND type.** Model additions (plan 251–274) and real CoinModel names are improvements. However, plan 313–318 permits empty `coinTypes` to pass, contrary to prior CoS must-fix (`COS_SCORE_NET-815...:92`); substring checks at 308–316 can also admit broad or blank metadata. Require normalized, nonblank canonical metadata and explicit accepted matches. The proposed call at plan 325–333 is not the actual integration: `coin_detail_screen.dart:3507–3515` concurrently calls `_fetchLibraryErrors(denom,year)` and `_fetchGreysheetErrors(denom,year)`; library wrapper **3526–3531** still supplies no series/type. Greysheet caller **3537–3551** and backend `numista_backend/routes/greysheet_error_routes.py:48–67` accept only denomination/year. v1.8 specifies no Greysheet fix at all. The merged result can still contain unrelated errors. Supply wrapper/signature changes, fail-closed response/server filtering, schema compatibility for existing error records and positive plus negative fixtures. No Firestore backfill is authorized by this review or by a generic plan YES.

4. **Stop labeling a nonexistent CPG input as verified.** Plan 44 and 229–244 claims `data/cpg_retail_master_2026.json` is a verified CDN dataset. Exact `Test-Path` was false, it is absent from pinned dev's tree, and the proposed `scripts/migrate_catalog_cpg_retail.py` is also absent. A proposed new script is fine; a claimed verified existing source is not. Identify the real authorized feed/file, version, license, retrieval/provenance evidence, actual path and schema, duplicate/NAC/missing-price handling and dry-run report. The new card rendering is directionally correct, but a named fictitious input does not establish sourced retail. Unknowns must remain pending; do not invent prices or mintages.

5. **Implement navigation/history rather than repeat acceptance prose.** Plan 380–410 now accurately quotes the real `_loadCatalog` block at `catalog_browse_screen.dart:71–86` (not `didChangeDependencies` as the baton implies). Plan 413–414 still merely names two different web interop choices, with no imports, listener registration/disposal, Back/Forward or modal-close algorithm. Ask Morgan is only claimed fixed at plan 72, with no patch. Actual `_openAskMorgan` at **223–228** does `pushNamed('/?route=AiChatScreen')`, while `numista_mobile/lib/main.dart:166–179` creates the public catalog in a separate MaterialApp with no routes. Specify outer-app navigation, guest sign-in/signup and return-to-item behavior and test them. Merely re-quoting the loader does not close this prior blocker.

6. **Turn the 1:35 PM additions and Site Auditor #1/#2/#5/#6 into an implementable, source-grounded migration/rendering plan.** Plan 418–434 lists the requested topics, but gives no field mapping, exact source checks/manifests, row joins/deduplication (3,209 research rows vs proposed 3,202 bundle), Laws/social-post renderer, Congress-only Laws validation, licensed crop ingest, nullable mintage conditions or history sanitization patch. Actual detail code renders `history` verbatim at **865–873**; `_buildMintageRow` **987–1017** retains outbound source links and the missing-field UI beyond that block. The prior mintage-link-removal requirement is no longer implemented. Preserve approved social-post X links as distinct data without sending/posting; resolve their relationship to plan 63's broad 'Congress.gov ... only' wording. Define sampled-1943-cent and no-details acceptance fixtures, sourced high-traffic coverage/approved image target by Nov 13, and hide unknowns rather than author invented history. Keep AI replicas labeled and out of primary_image. Section 9 currently restates the audit, not its fix.

7. **Supply real tests, offline fixtures and a field-test gate.** Plan 456–475 contains two comment-only tests, and its only assertion exercises a live static Firestore service without initialization/mock injection, positive fixture, or proof that any error was returned. It can pass vacuously on an empty result. Add actual widget pumping/assertions for retail numeric/string/missing/zero/no-AI fallback; owned/external URL pre-fetch tests for both renderers; same-series/type positive and 1958/1999 negative results from both providers; Google/Kaggle absence; navigation lifecycle; mintage/history/legislation/social links; theme-aware Markdown and measured contrast. The darker colors and `_kText(context)` proposal at 360–373 are sensible but do not prove all table/card/detail B27-11 surfaces or provide Eric/FT's field-test gate. Do not claim 'complete test assertions' (33) or 'executable suite' until they exist and run under a separately authorized build.

8. **Make the launch integration and operational gates unambiguous.** Plan 447 says build on `dev (origin/p7-v8.9)`, but they are different branches: pinned dev contains catalog; current p7 has no `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`. Provide the exact complete integration/change-set path, dependencies and preview smoke gates; no individual-file transplant or implicit main unlock. Preserve main 9f04550a and separate production YES (24–25) and explicitly separate Eric YES for Firestore writes from Eric YES for rules deployment. Restore the prior alert-readiness/runbook acceptance without introducing a cap or automated shutoff. Add the missing US-only scope, 3:00 AM EST AG stand-down/handoff, and preservation/verified laptop + GCS backups of AI coin images before any image migration/deletion. No secrets or AJ PII in fixtures, logs, public metadata or copies. NET-818's Sun 8 Nov Stripe PLAN ONLY remains OFF and needs an owner/handoff for the required beta-tester promo-code plan (omitted here). Date the final Eric preview/production authorization checkpoints, not just the deploy. Never treat another agent's claimed approval as YES.

## Prior-review closeout
- Retail source/schema/NAC join: better specification, **source unverified/nonexistent**; tests open.
- Image helper scope: **closed conceptually**; modal, ownership and CSP remain open.
- Models and known errors: **partial**; both-type requirement, callers and Greysheet open.
- Google/Kaggle: **not closed**; wrong branch and incomplete ranges.
- Contrast: improved colors/Markdown, **tests and broad-surface/FT proof open**.
- Branch/revert: fixed dev pin and execute-set revert retained; **integration prose contradicts it**.
- Deep-link quotation corrected; history/Ask Morgan still not implemented.
- Dated NET-818 schedule exists, and NET-819 + 1:35 PM items are named; implementation/acceptance not complete.

### Correction to previous reviews — do not recycle an unsupported compiler objection
The previous CoS/SAG assertion that a final boolean guard cannot promote a nullable local is not a reliable Dart 3.11 blocker. Dart's documented condition-variable flow analysis saves/restores the nonnull state. Plan 99–100/157–159 uses stable final locals and should not be rejected solely because it omits `!`. Its summary at 42 inaccurately describes an explicit nonnull binding, but this review does NOT claim the shown expression fails compilation. Official implementation documentation read this turn: https://dart.googlesource.com/sdk/+/2f80a99a164c7972cda2307bbeb1ef2d60407251%5E%21/ . Still require actual analyzer evidence in the authorized build. Likewise, do not revive SAG's unsupported blanket Dart-lookbehind objection; the prior CoS correction already addresses it.

## Handoff integrity
Baton `BATONS/BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.8_20261106-2130.md:7` claims four mirrors. Docs, BATONS and RADIO NET match SHA256 **AE337056CACD2720494900BB11506F494575B0166292007DFA1DEAA2FBBAC9D3**. Exact plan copies in **INBOX and OUTBOX are absent**. Correct the claim or complete approved internal mirroring; this review did not write to the laptop.

## Rubric
|Dimension|Score|
|---|---:|
|Standing locks / production gates|12/15|
|Retail implementation / real provenance|10/15|
|Images / CSP / ownership|8/15|
|Known-error model / complete matching|9/15|
|Google/Kaggle structural removal|4/10|
|Navigation and lifecycle|5/10|
|Scope additions / dated launch / integration|11/15|
|Executable verification|1/5|
|**Total**|**60/100 FAIL**|

No AJ PII encountered in the reviewed plan/selected code. No authority granted. Return a revised plan for CoS scoring, then independent SAG 95+, then Eric's typed YES; all separate gates remain.
