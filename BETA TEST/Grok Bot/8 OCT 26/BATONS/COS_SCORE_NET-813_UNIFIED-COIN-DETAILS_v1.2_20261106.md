# GB CoS score — NET-813 Unified Coin Details View v1.2

**74/100 — FAIL.** Pass requires 95+. Not ready for SAG pass, Eric YES or execution.
Reviewed 6 Nov 2026, approximately 10:02–10:03 PM EST (America/New_York).

## Scope and evidence

Read delivered 533-line BATONS plan (**P** citations), 28-line review baton, prior `RADIO NET/COS_SCORE_NET-806_UNIFIED-COIN-DETAILS-v1.1_20261105.md` (**86**) and `RADIO NET/SAG_SCORE_NET-806_20261105.md` (**58**), and prior box reports for format/rigor. Agent statements are evidence, never approval.

Read-only targeted schema/call-site/source checks on EDS_Laptop in `C:\Users\ericd\Documents\MyVertexProject`. All source citations below mean **origin/p7-v8.9 @03da3195d1aaaed2a44b45714ec81761092d1313**, also HEAD. Main remains **9f04550a45fa4da082ba8948c2d89a521a90fa45**. App lib/assets/firebase diff from 4d17ca5e to this ref was empty. Main-is-ancestor check returned 1 (not ancestor).

No fetch, checkout, laptop writes, tests, build, app/database requests, deployments, push or messages. Only this report is written to the box. CloudAgent was not exposed by tool discovery; this bounded document/source check is not a deep Code Reviewer audit or runtime certification. New files being absent is expected for a plan-only submission, not itself a defect; missing implementation contracts and contradictory claims are defects.

## Numbered blocking must-fixes

1. **Finish the actual rollback and flag operations.** P29–32 correctly rejects locked main and promises exact execute-commit reverts. P460–465 instead reverts **all** `$PRE_EXEC_SHA..HEAD`, potentially including concurrent/unrelated commits. Record actual branch/baseline and ordered execute SHAs; verify ancestry/membership and handle merges/conflicts before an authorized rollback. P471 deletes a preview channel; P473 clones **current live to rollback-temp**, not a previous known-good release back to live. Listing releases at P474 restores nothing. Supply recorded pre-deploy release/version IDs, actual recovery source/target and smoke checks. An accidental live deployment is not authorization for another live change. P446's mutable false boolean is a good test gate, but process-local assignment is not a remotely operable instant rollback for already loaded clients. Specify enable/disable owner, approved mechanism and session/reload recovery without introducing an unauthorized Firestore writer.

2. **Finish parent identity and Previous/Next resolution.** Real `numista_mobile/lib/models/collection_row.dart:5–25` distinguishes synthetic virtual IDs/data from real parent records. Actual cell/card sources `my_collection_screen.dart:2729–2736,2991–2994,3025–3026` match docs/row/index/effectiveId. Info-icon **2754–2761** aborts if parent is absent. P217–220 and P279–282 instead fall back to child map `m` while assigning the parent ID, recreating mixed identity on cache miss. Fail closed or show unavailable-parent state. P307–312 sets index **0** when the selected parent is outside the filtered list: displayed coin disagrees with `coinList[0]`, and Next skips the first actual item. Define a shared immutable navigation-entry/resolver contract for opening AND all transitions, parent deduplication, cache misses, filtered-out parents and list changes. The proposed screen's show API/navigation adapter is not supplied. Preserve correct per-site legacy fallbacks; replace literal `...` at P241,258 with explicit callback-preserving scope.

3. **Make Laws provenance, URL checks and timeout behavior enforceable.** Real `coin_detail_screen.dart:2956–2969` reads `metadata/coin_legislation`/`laws`; **3082–3088** selects Firestore then static fallback. Neither establishes editorial checked status. P394–405 calls these inputs checked/verified without identifying approval metadata, manifest or schema. Bind a reviewed fixture/source version to that badge; absent proof stays unchecked. Real **3152–3160** launches any nonempty congress_url via icon button. P400 proposes a web plain anchor but still passes a raw URI to mobile launchUrl. Specify shared HTTPS/exact `www.congress.gov` validation rejecting lookalikes, userinfo, other schemes and off-host destinations. Explicitly reconcile SAG's plain-anchor/not-launchUrl requirement with mobile, rather than claim it closed. Real **2961** has no timeout; P406–408 names an outcome but no bounded loader, malformed-data handling, mounted/cancellation behavior or fallback precedence on errors. No client live API is needed. Backend writer remains unexecuted; no seeding/write authorized.

4. **Close the missing Morgan-notes and rich-content boundaries.** Prior CoS #3 (`COS_SCORE_NET-806...:35`) required checked catalog notes or labeled unchecked output. P418 only lists AI analysis/insights/confidence, without source binding, unchecked label or failure mapping. Real `_AiInsightsTab` accepts free-text insight (`coin_detail_screen.dart:2682–2696`) and renders Markdown at **2785–2805**, including arbitrary outbound launchUrl at **2801–2804**. Fixing eBay alone cannot enforce P385's Congress-only outbound boundary. Specify safe notes rendering: no arbitrary outbound links/remote Markdown images, no guest private annotations and no unapproved logging/generation side effects. Fix inherited white headings/strong text (**2789–2792**) if reused. P329–335's 'verified CDN' also needs an actual user/reference URL provenance policy and HTTPS/current-origin/verified bucket-path guard BEFORE fetch. No hotlinks or AI primary/card/index fallback. Inspector Image.network at `my_collection_screen.dart:3654,3747` is not proof of those guards.

5. **Resolve the value/privacy matrix and bind the real public entry.** Guest positive retail outside private tabs (P373–377) is a real improvement. `CoinModel` exposes nonnullable double cpgRetail (`coin_model.dart:54,130`) parsed from cpg_retail/cpgRetail at **225**: use that real contract and define invalid/zero/negative/nonfinite cases. P340 hides all financial metrics including CPG until Show values, but P416 says Overview always shows positive retail. P383 says all valuation figures exclusively use CPG while P343 promises purchase/melt and P377 secondary AI. Define exact owner/guest visibility and distinct field sources. All five collection dispatches hardcode guest=false (P230,250,267,292,314); P356–360 is an uncited hypothetical public call. Pinned p7 has **no numista_mobile/lib/screens/catalog/**. Name the real dev/catalog integration dependency, public adapter and route; no individual-file transplant or main unlock. Require a safe public data projection, not only widget hiding of an unrestricted private model: include notes/AI text, semantics, photos, links/logs/filenames. /catalog stays public; no auth detour or extra click.

6. **Turn the verification checklist into an implementable offline test plan.** P481–520 lists assertions, not authored tests; the named test file is absent on the pinned ref. Proposed tests are appropriate, but need a public harness, injected law/image/read boundaries, fake callbacks/writers and captured URLs. Cover all five sites flag on/off; virtual parent missing; filtered-out parent; navigation identity and value reset; malformed/unreviewed/hanging Laws; hostile URLs; Markdown links/images; accepted user-photo priority; eBay absence; positive/invalid retail and guest private data absence. Count writes (zero), external fetches and unnecessary reads. P519 mocks Congress API errors although approved architecture reads Firestore/static: mock the real boundary. Add measured light/dark contrast, keyboard/focus/52px targets, one-tap opening and Previous/Next field-test acceptance. Do not claim runtime proof from prose, but do not pretend disabled new-feature callbacks already perform writes either.

7. **Carry the standing rules and operational gates into the checklist.** Main lock, Stripe OFF, plan-only, explicit live YES and no initial writes/rules/seeding are correctly stated (P12–14,428–435,530–532). Explicitly retain **separate Eric YES for Firestore writes and separate Eric YES for rules deploys**. Add US-only; sourced/no-invention content; AJ PII protection across fixtures/notes/images/public metadata/logs/semantics; and **budget alerts only, never caps**, with read-cost measurement/owner/readiness. No cap appears here, but read-only is not guaranteed free. If shared image migration/deletion enters from NET-816/817, require exact approved deletion scope and verified laptop+GCS preservation first. This plan authorizes no deletion. Date preview/field-test/Founder checkpoints inside 10–16 Nov and state the dependency on Catalog live around 13 Nov without moving either deadline. Scope read-only claims to this new feature, not the whole existing app.

## Prior must-fix closeout — all items

| Prior item | Disposition |
|---|---|
| CoS #1 / SAG #1 rollback | **Partial:** locked-main revert removed; broad-range revert and non-restoring Hosting commands open (#1). |
| CoS #2 / SAG #5 read-only | **Closed in policy:** P428–435 disables new-feature mutation/logging; new calls supply no mutation callbacks. Offline enforcement and separate gates remain (#6–7). |
| CoS #3 checked notes/Laws, failures, retail | **Partial:** Laws labels/retail preference improved; notes provenance absent, checked status assumed (#3–6). |
| SAG #2 code quotes / eBay | **Corrected as proposal:** P139–153 matches actual 3849–3863; P157–167 matches 3989–3999. P384 explicitly removes outbound eBay from NEW view. Legacy fallback still has eBay at 3861, intentionally outside new-view scope. Rich-content outbound boundary open (#4). |
| SAG #3 default-off gate/fallback | **Mostly addressed:** mutable false flag and correct fallback per site supplied; instant operational rollback overstated (#1,6). |
| SAG #4 real Laws | **Partial:** correct read/fallback and no-writer direction; provenance/URL/mobile/timeout contracts open (#3). |
| SAG #6 guest price / AI image hygiene | **Policy substantially addressed:** positive Overview retail, no primary/card/index replicas explicit. Owner contradiction, actual public integration and image enforcement open (#4–5). |
| SAG #7 real resolvers/list | **Partial:** real docs/index/parent casts provided, Global Search dropped. Cache-miss identity and out-of-list navigation wrong (#2). |

## Handoff integrity

Baton `BATONS/BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.2_20261106-2200.md:8` claims INBOX/OUTBOX mirrors. Exact copies there are **absent**. Docs, BATONS and RADIO NET copies match SHA256 **2DA404313959737C7D941207DA1911F380A481DF667EC4EB274ECA663CB2F06C**. Correct claim or arrange approved internal mirroring; reviewer wrote nothing to laptop.

## Rubric

| Dimension | Score |
|---|---:|
| Standing locks / read-only / approval boundaries | 17/20 |
| Branch, rollback and feature gate | 10/15 |
| Five-site resolution / navigation identity | 11/15 |
| Laws, notes and outbound safety | 10/15 |
| Guest privacy / CPG / image precedence | 12/15 |
| Accessibility / low-click UX | 9/10 |
| Offline verification / field-test readiness | 5/10 |
| **Total** | **74/100 FAIL** |

No AJ PII encountered in reviewed plan/selected code. No authority granted. Revised CoS 95+, then independent SAG 95+, then Eric typed YES; separate production/write/rules/deletion gates remain. No messages sent; no Eric ping tonight.
