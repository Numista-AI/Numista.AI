# GB CoS score — NET-817 Cards v1.5 + Images v1.5

**Combined: 65/100 — FAIL.** Equal-weight plan scores: **Cards 72/100 FAIL; Images 58/100 FAIL**. Each must reach 95+; averaging never bypasses a failed plan.
Reviewed 6 Nov 2026, approximately 9:38–9:43 PM EST (America/New_York).

## Scope and evidence
Plans: `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md` (C, 388 lines) and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md` (I, 421 lines).
Read prior `COS_SCORE_NET-812_780b-780c-v1.4_20261105.md` (67) and `SAG_SCORE_NET-812_780b-780c-v1.4_20261105.md` (64), including CoS's correction of SAG's unsupported Dart lookbehind claim.

Repository on EDS_Laptop: `C:\Users\ericd\Documents\MyVertexProject`. Actual origin/p7-v8.9 and HEAD **4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235**; dev **eb23e011d1e25446e256518e5065b4a989aaba17**; main **9f04550a45fa4da082ba8948c2d89a521a90fa45**. All source citations below mean **p7 @4d17ca5e** unless otherwise specified. App lib/assets/firebase diff from the prior a07cf9f2 audit to this ref was empty. The pinned dev b0b05808 has no canonical service; p7 execution scope is appropriate.
Only machine-targeted read-only document/existence/hash/git commands were used. No fetch, checkout, tests, build, database/network-to-app calls, laptop writes, deploy, push or messages. The box contains these review reports only. Proposed snippets were inspected, not compiled or applied.

## Numbered must-fixes

1. **[C+I; blocking syntax] Supply full structural deletions, not the still-truncated ranges.** C 274–284 / I 366–373 prescribe deleting Google widget 3531–3546 and handler 4386–4405. Real `numista_mobile/lib/screens/my_collection_screen.dart` has the widget's `SizedBox` and closing spread at **3547–3548**, and the handler's closing brace at **4406**. Literal application leaves unmatched structure. Correct complete ranges are 3531–3548 for that block and 4387–4406 for the method on this exact ref, but require an actual anchored diff rather than relying on line arithmetic. Inspector removal **5549–5645** and invocation **3820** are correctly targeted for p7. NET-816 targets a different dev file: its equivalent inspector is 3796/5502, and those p7 Google anchors are absent there. Name one owner and a complete tested integration set. Preserve consent/sharing functionality: `photo_sharing_service.dart:12` is a Kaggle comment, not proof of executable ingestion logic. Obtain Eric YES on the exact approved deletion list; neither plan states that separate gate.

2. **[C; identity/data corruption] Make canonicalYear conservative and correct for direct dual dates and notes.** C 169–202 prefers any `2026` in combined text including **Personal Notes at178**. The real canonical service intentionally excludes Personal Notes at `canonical_mint_asset_service.dart:160–161` so neighbor-coin notes cannot hijack identity. A missing-year ordinary nickel with a note mentioning 2026 can now be assigned 2026 art; the helper's 'never' guarantee is false. Direct `{'Year':'1776-2026'}` is not recognized: it fails the direct four-digit check, is never included in text, and returns the unnormalized dual date if no text exists. Empty lower-case `year` also masks populated `Year` through `??`. `title ?? name` drops name if title is empty. Parse valid direct candidates first, normalize direct dual dates, exclude personal notes from identity, define conflict/ambiguity handling and only infer from reliable coin metadata. Keep the sensible propagation to both `extractSku`107 and `resolveFromMap`172, but supply the promised direct `resolve` path (C161) or precisely bound its contract. Add public resolver tests for these counterexamples and 2023-with-2026-note, not only the easy explicit-2023 fixture.

3. **[I; photo preservation] Extract the same user-photo aliases that the detector recognizes, and use a shared presence policy.** I220–230 calls `hasUserUploadedPhotos` but reads only `_F.imageReverse`/`_F.imageObverse` (`image_url_*`) and `stored_*`; it omits camelCase **imageReverse / imageObverse**, which the real service detects at `canonical_mint_asset_service.dart:44–49`. A valid camelCase microscope upload is therefore replaced by a placeholder. The null-coalescing read also lets an empty/invalid earlier alias hide a valid later alias. Detection is URL-pattern based, not simply 'any direct field exists'; supply an explicit provenance/presence predicate for all real user sources and iterate nonempty accepted candidates. Preserve the good new fail-closed behavior: rejected user photos must not fall through to canonical/reference art. Note the baseline's `resolveFromMap:153–158` already rejects recognized uploads: I103–104 overstates 'canonical steals all user photos' merely because that call appears first. Fix the actual alias/read defect, not that inaccurate root-cause claim.

4. **[I; compile/applicability] Replace the entire original class, not lines inside it.** I114 says replace **6360–6480** with two complete classes. Original `_CollectionCardImage` begins at `my_collection_screen.dart:6356`, and fields/constructor at **6357–6358** remain if that literal edit is applied. The new class declarations would be inserted inside the old class. Specify whole-class replacement from its real declaration through its matching brace, or an anchored diff. The supplied `_buildCoinImage` at I300–334 does cure the previous omitted-method problem in principle; do not lose it. Analyzer and compile proof still belong to a later separately authorized build, not this plan review.

5. **[I; fetching, ownership and liveness] Cache by semantic request key and bound lookup completion.** I136–140 compares Map identity: newly constructed equivalent maps refetch; same Map mutated in place does not update. Use a normalized immutable identity/request key and dependency injection. `_initFuture` I143–163 starts a reference read even where an accepted direct image will win in build step3; skip unnecessary requests. No timeout exists in I154–160/259–290, so a never-completing read leaves the spinner indefinitely; the real `coin_image_service.dart:562–579` awaits sequential Firestore reads and catch603–606 does not bound a hung future. Specify timeout/error/no-result terminal states and tests. The allowlist I181–199 treats path prefixes `/microscope/`, `/users/`, `/user_uploads/` as if they were verified GCS buckets, accepts a prefix for arbitrary similarly named upload buckets, and admits every googleusercontent subdomain without ownership proof; CSP permission is not ownership/license evidence. Conversely it rejects own `numista.ai`/preview same-origin and bucket-host URL forms. Ground allowed forms to verified actual bucket/path manifests and HTTPS/current-origin policy, never hotlinks; test accepted user/reference fixtures plus rejected third-party/unowned storage before any fetch.

6. **[C+I; tests are not substantive] Replace tautologies and comments with real, offline behavior tests and mocks.** C307–338 at least proposes public-resolver assertions. But C340–349 names a regex test, creates negative docs then never uses them, and asserts only year ==2026, not denomination matching. C359–385 never pumps a widget; `expect('$45.50',contains('$45.50'))` cannot test app behavior, nor can checking a locally recomputed bool establish no AI fallback. I387–418 never pumps the image widget, supplies no mocks, and two bodies have no assertions. No test proves precedence, rejection-before-fetch, reference result allowlisting, retry/cache behavior, timeout, Google/Kaggle removal, or light/dark contrast. Private widget access needs a real test seam or public harness. Supply imports/fixtures, injectable fake image/provider/Firestore boundaries, counted reads, captured requested URLs, widget finders and negative assertions. Actual canonical test path **numista_mobile/test/services/canonical_mint_asset_service_test.dart** is correct; `test/widgets` files are proposed new files, not existing proof. Remove 'complete offline mocks' and 'full assertions' claims (I66–68, C72–74) until actually supplied. Do not run production reads to validate tests.

7. **[I; explicit standing-rule violation] Remove the hard $0 cap and the zero-cost guarantee.** I55 literally says **Hard $0.00 Spend Cap**; I348 repeats it. Eric's standing policy is **budget alerts only, never caps**. Read-only Firestore requests and GCS downloads may be billable: no mutations does not prove zero cost. The accurate read boundary at I341–347 is an improvement. State anticipated costs/measurement and alert thresholds/owners, no cap, no automatic shutoff. Keep review/build validation offline; do not use a cap to authorize or suppress runtime reads.

8. **[C+I; remaining gates] Carry the operational/privacy/image-protection constraints into an explicit execution checklist.** Existing header main lock, Stripe OFF, preview vs separate live YES, no Firestore writes/rules under general YES, and 'Zero AJ PII' are good. Add **separate Eric YES for writes and separate Eric YES for rules deployment**, exact-list deletion approval, US-only scope, **3:00 AM EST AG stand-down/handoff**, no invention/sourced metadata, and preserved/verified **laptop + GCS backups of AI coin images** before any image migration/deletion. No off-site publishing or bulk scraping/upload is authorized. Expand AJ protection to logs, mocks, filenames and any public attribution; do not insert real user data into tests. Dynamic pre-execute SHA + exact execute-set revert (C290–298, I354–362) is the right rollback direction; require recorded commit membership and preview Hosting release recovery, not stale checkout. Coordinate NET-816 shared changes without conflating dev and p7.

## What improved / prior must-fix status
- **Rollback:** stale pin removed; dynamic p7 HEAD / exact execute-set revert **accepted as proposed**, not executed.
- **Year helper:** both extract and map resolver now targeted, but direct dual dates, unreliable notes and conflicts are **blocking**.
- **Widget completeness:** `_buildCoinImage` restored; state/future concept improved; **literal replacement scope and alias/cache tests remain blockers**.
- **User-first fail-closed:** good direction; camelCase reads still missing.
- **Price:** positive CPG retail overrides pending, primary AI fallback removed; scope exclusion for Cert Add is honest. Dark brown text proposal improves AA. **No executed widget/contrast/FT evidence**.
- **Regex:** proposed lookbehind need not be rejected; previous CoS's installed-SDK finding corrected SAG. The new so-called regex test does not test it.
- **Google/Kaggle:** now included, but actual deletion edits still malformed and need cross-branch ownership.
- **Network:** permitted reads now acknowledged; arbitrary $0 cap conflicts with standing instructions and charged reads.
- **Tests:** correct service path, but many new examples are empty/tautological rather than full offline tests.

## Handoff integrity
`BATONS/BATON_NET-817_GROKCOS_REVIEW_FAILFIX_PLAN_780b-780c_v1.5_20261106-2140.md:8–9` claims INBOX/OUTBOX mirrors. Exact copies of **both plans are absent in both directories**. Docs/BATONS/RADIO NET copies do match:
- Cards SHA256 **64D339D45158C51814357D60E0488F2DF890E6D5B0ED74DD0D632421A82B4BFF**.
- Images SHA256 **CD17B43CE145BAEA90389537BA1B644E491BA2403D359C252EBE71704E18AF37**.
Correct the claim or arrange approved internal mirroring. No laptop write performed by this reviewer.

## Rubrics
|Cards dimension|Score|
|---|---:|
|Branch/rollback/standing locks|17/20|
|Canonical year / denomination correctness|20/30|
|Retail precedence and contrast proposal|19/20|
|Shared structural removal/integration|8/15|
|Behavioral tests/provenance proof|8/15|
|**Cards**|**72/100 FAIL**|

|Images dimension|Score|
|---|---:|
|Branch/rollback/standing locks|12/20|
|Complete applicable widget/future lifecycle|14/25|
|User-photo preservation and ownership/CSP|15/25|
|Network truth/operational safety|7/15|
|Real verification and shared removals|10/15|
|**Images**|**58/100 FAIL**|

Combined arithmetic: (72+58)/2 = **65/100 FAIL**. Score is plan readiness, not proof of runtime safety. No AJ PII encountered in the reviewed plan/selected code. No code, deployment, Firestore, deletion, main, or Stripe authority granted. Revised CoS 95+, then independent SAG 95+, then Eric typed YES; separate gates remain separate.
