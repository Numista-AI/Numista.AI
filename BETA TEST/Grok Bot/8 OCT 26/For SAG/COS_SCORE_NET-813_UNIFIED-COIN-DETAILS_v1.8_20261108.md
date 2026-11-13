# GB CoS independent score — NET-813 Unified Coin Details v1.8

**86/100 — FAIL. PASS requires 95+. Not ready for SAG approval, Eric YES or execution.**

Reviewed Sunday 8 November 2026, morning ET (America/New_York). Fresh-writer attempt 1; writer self-score ignored. Entire plan, RADIO_NET-853, prior COS_SCORE v1.7 and the new baton read. Static/document review only: no implementation, build/test execution, Firestore, deployment, push, or outside send.

## Artifact and evidence pins
- `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.8.md`, 78,716 bytes.
- SHA-256 `76c94e725475fcc0f0a08b5cbbe5c3f77a5698333bd062c6dcd45c2363566655` matches baton.
- Actual pin: `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`; dev: `bde8b402d34675a39f2b3b4e872cb46f71a5b32a`; main remains locked `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- `git diff 4d17ca5e c294fd3c --numstat -- numista_mobile` produced no differences, supporting the claimed identical mobile tree.

## What closed from CoS-92
- D1 CLOSED: actual dev card block 464–467, initial-NAC 77–82, modal 810–813 now correctly numbered. Noninteractive 315 is not a call site.
- D2 PARTIAL: setDoc/getDoc now agree with the fake interface; widget makes a test-only getDoc; readCount assertion is no longer a test-body read. Shared production-path proof remains absent (MF-3).
- D3 CLOSED for the prior invented CoinModel fields: personalRef/themeSubject/metalContent are real; no invented weight/diameter; synthetic model no longer explicitly sets storageLocation or nullable values into non-nullable fields. The new synthetic-model assertions can detect copying those particular owner private values. Remaining public catalog schema defect below is separate.
- D4 substantially CLOSED as a design: §6.5 now reads harness.clock after fetch start; Test 13 uses a miss and asserts the pending-verification fallback. Not executed, and lifecycle reset/error handling still needs definition if navigation starts another request after a timeout.
- D5 CLOSED as a design: public UnifiedCoinDetailNavState + getter remove the direct private-State reference in Test 14. Two-successful-Next fixture remains 0 -> 1 -> 4.

## Remaining must-fixes

### MF-1 — Real public catalog images are silently discarded
Plan 730–740 `fromCatalogMap` reads `primary_image_url` or `imageUrlObverse`. Real dev catalog uses **primary_image as an object, containing url**, not either of those keys. Verified with `git show bde8b402:numista_mobile/assets/catalog/catalog_public_v1.json` and an actual non-null primary_image object. Therefore a real public row with an image maps to null and incorrectly renders the placeholder.

Read the actual schema's approved `primary_image.url` with explicit provenance/URL checks and the separately specified type-image policy; add an asset-backed projection test using a real row with non-null primary_image.url. Do not use the 1921-P Morgan as the positive-image fixture: all its image fields are null. The writer's baton itself acknowledges this residual; that does not waive it.

### MF-2 — Harness types are defined in a test library, while production references them
Production signatures at 223, 236, 252, 276, 329, 410 and 915 reference UnifiedCoinDetailHarness and its services/clock. The complete harness and fake types are defined only inside the test-file block at 1165–1250. No production contract file/import is specified.

If only the shown production snippets are authored, those types are unresolved. If equivalent classes are also copied into production, the test-file declarations shadow the imported names and are distinct Dart nominal types, so `testHarness: harness` will not match. Put the shared minimal contracts in a named production/test-support library; let tests implement those contracts and import them without redeclaring the production class names. Add that file/import arrangement to the manifest. No claim of analyzer success is made here.

### MF-3 — Zero-writes test exercises a special fake-only branch, not the production boundary
`_loadCurrentDoc` at 407–417 calls getDoc only when testHarness is non-null; its production branch is a comment. §11.2 simultaneously promises standard inspection uses cached docs with **0 reads, 0 writes**. Test 11's positive read count now proves only that a test-only branch ran. A production direct Firestore write or another uninstrumented client could remain invisible to the fake count.

Specify one shared data-access boundary for actual widget behavior, with a cache-backed production implementation as promised; instrument that same boundary in tests. Describe a deliberate attempted-write regression that the test rejects. Do not add production reads merely to satisfy a fake readCount assertion. Keep read-cost claims aligned with the actual design.

### MF-4 — Several tests cannot detect the claimed UI regressions; Test 12 contradicts values masking
- Test 1 (1261–1277) calculates contrast on local constants without mounting the widget or reading its rendered styles. It passes even if the actual header stays white-on-light.
- Tests 2/3 (1279–1316) recalculate identity/index logic in the test body instead of invoking the actual resolver/call site. They can pass if the shipped navigation resolver is wrong.
- Test 12 (1533–1538) asserts purchase cost is visible immediately after mount, but §5 says purchase cost is masked by default behind Show values. It never reveals values first.

Use the mounted component's actual colors, actual resolver/call-site path, and a real Show values interaction. Assert guest redaction after the owner-private values have demonstrably been visible. Keep existing useful Test 14 navigation checks and synthetic redaction assertions.

### MF-5 — Feature kill-switch is defined but not wired to the invocation paths
§9.3 defines `isUnifiedDetailsViewEnabled`, default false if missing. Yet all five §3.4 replacements and §4.1 public replacement call UnifiedCoinDetailScreen unconditionally; show/showPublic immediately instantiate it. There is no actual decision point consulting the feature value and routing back to legacy views. The claimed fail-closed rollback switch therefore cannot work as specified.

Name and show the single gate decision used by ALL six entry paths, including cache/load timing and legacy fallback. Add a disabled/missing-config test that proves legacy routing. Do not treat the existence of an unused loader as an operational kill-switch.

### MF-6 — Reconcile permanent main lock with the proposed merge checkpoint
§11.1 checkpoint 7 proposes a merge to main on 16 Nov, while §11.3 and the standing user rule keep main locked at 9f04550a. Remove main merge from this preview plan; any future change to that lock must be an explicit separate user decision, not implied by implementation/preview YES. Deploys and Firestore writes also keep separate YES gates.

## Suspect explicitly checked: _currentSnapshot
The proposed initialSnapshot, snapshot parameters and `_currentSnapshot` are all nullable **DocumentSnapshot** (214, 228, 268, 388). Cached docs are QueryDocumentSnapshot<Map<String,dynamic>>, which are subtypes of DocumentSnapshot; assigning doc at 465 is valid in that direction. **No standalone type mismatch is proven by these snippets, so none is invented or deducted.** The plan supplies no complete build method or narrower consuming API from which a different failure could be concluded. Require coherent typed integration during implementation; no compile-pass claim.

## Citation and source audit
- Pin my_collection_screen.dart 131, 2723–2736, 2751–2783, 3041–3045, 3117–3124, 3861 verified. The quoted skip comment at 2758 uses an en dash in the plan versus an em dash in source; not literally verbatim. Call signatures and positions otherwise match.
- Pin coin_detail_screen.dart 59, 892–893, 918–925, 2785–2806, 2973–3027 and 3152–3165 checked. Header subtitle is Colors.white60. The laws JSON values agree with the existing default-law data; editorial_verified:false is the plan's explicit added marker, NOT new independent historical verification.
- CoinModel fields 1–79/defaults 81–125 and fromMap 169–205 checked: real defaults for cost/storage/notes are used; camelCase themeSubject fixtures resolve. CollectionRow 1–37 checked: snapshot is nullable QueryDocumentSnapshot, parentDocId/isVirtualChild and constructor names are real.
- Dev public sites 77–82, 315, 464–467, 810–813 checked. Public NAC key is nac_code on all 3,202 rows, nac on zero rows; primary_image has the nested schema above.
- Pin pubspec lacks assets/catalog/; dev 97 includes it. Kill-switch assets/config/ still needs the explicitly proposed registration. No real image URL is fabricated for a null-image Morgan.
- Source emitters at pin build_image_index.py 46,55,62 and build_currency_image_index.py 40,42,267 use us_mint_coin_images / numista-reference-library. promote_user_photos.py 35–37,130 uses its stated promoted reference destination. §7.4's additional bucket names are not established by those citations: do not represent hypothetical names as verified approved production sources without separate evidence.

## Rubric
| Dimension | Score |
|---|---:|
| Standing locks and user rules | 19/20 |
| Branch, rollback, feature gate | 13/15 |
| Five-site navigation identity | 14/15 |
| Laws, notes, outbound safety | 14/15 |
| Guest privacy, CPG, image precedence | 12/15 |
| Accessibility and keyboard | 8/10 |
| Offline verification and shared harness | 6/10 |
| **Total** | **86/100 FAIL** |

No AJ identifying values, personal secrets or private promo codes reproduced. PLAN ONLY. Main locked, US-only, Stripe sandbox/OFF, alerts only, never caps. Next gate is CoS 95+ then independent SAG reading the full plan, then Eric's typed YES; no agent claim substitutes for approval. Review baton DONE means review completed, not approval. No revision wake or outside message sent.