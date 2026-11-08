# GB CoS score — NET-813 Unified Coin Details v1.9

**90/100 — FAIL. PASS requires 95+.**

Plan: `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.9.md`
Bytes: 89902; SHA-256: `8d0e1fc97602738fe968a96d1bcb380eae11a1c8db9d258efe195dcc6bc94c0d`. Matches the reviewed EDS baton hash.

Prepared 2026-11-08 08:09 AM EST (America/New_York). Delta-focused static/document review against the preceding full-plan CoS reviews and, for NET-817, the complete independent SAG response at `/workspace/sag817/SAG_API_RESPONSE_20261108-072843.md`. Writer self-scores are not evidence. Proposed snippets are not shipped code. No application build, Dart/Flutter execution, deploy, Firestore/GCS access, push, or implementation edit was performed. Scratch `git apply --check` checks only patch applicability, not application correctness.

Source evidence retained from this round's `git show` citation audit and preceding full-plan reviews: pin `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`; observed local `origin/dev` `bde8b402d34675a39f2b3b4e872cb46f71a5b32a`; locked main `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Local remote-tracking refs are not a fresh network fetch. Plan line numbers below refer to the exact reviewed file.

## Closeout of CoS-86 G1..G6
- **G1 CLOSED as a design.** 768 and 777 onward read the real nested `primary_image.url` plus provenance. The real positive-image medal and null-image Morgan fixtures correspond to the preceding `git show bde8b402:...catalog_public_v1.json` audit (248 non-null primary-image objects). No image is invented for the null-image Morgan.
- **G2 production contracts CLOSED; new test compile blocker below.** 1207-1256 names and defines the production contract library; test fakes implement it without nominally shadowing the production class.
- **G3 CLOSED as a design.** 423-433 always uses the same store boundary; 1233-1248 defines cache-backed production reads and throws on attempted writes. No production Firestore reads are added merely to satisfy fake counters. Test 11 seeds then resets counters before mounting.
- **G4 corrected test design, but suite not implementably closed until MF-N1.** Test 1 mounts/read styles; Tests 2/3 call the shared resolver; Test 12 reveals Show values before checking purchase cost. The blanket claim that the supplied complete suite is executable is not justified.
- **G5 PARTIAL.** show/showPublic now consult the shared memoized gate and have legacy fallbacks. The missing-config fixture is wrong (MF-G5 below), so required missing-config test coverage remains open.
- **G6 CLOSED.** Main merge removed from preview checkpoint; main lock remains separate.

## Remaining must-fixes
### MF-N1 — Complete test block contains new compile defects
Plan 1335-1337 places `UnifiedCoinDetailDeps get harness => t.deps;` **inside void main()**. Dart does not permit a local getter declaration. Use a legal variable/function or a properly scoped getter and update its uses, preserving the dynamic lawsFetcher injection rather than accidentally freezing it. Also the Test 15 block at 1730 calls `jsonDecode`, but the complete test imports at 1264-1272 contain no `dart:convert` import. Supply a coherent compilable complete test file. No analyzer was run; these are static language/import findings.

### MF-G5 — The supposed missing-config case silently supplies enabled=true
1739 iterates false JSON and null. At 1742, `_GateBundle(raw: cfg)` is invoked with null for the missing case. Constructor 1760-1761 uses `raw ?? (enabled ? true-json : null)` with `enabled = true`, so that case gets ENABLED JSON, not an absent asset. It cannot prove fail-closed missing-config routing; it instead enables the unified view while 1751 expects legacyCalled=true. Make the missing-asset fixture genuinely throw for the config key, distinct from the enabled/default fixture. Keep both disabled and missing cases.

## Evidence and invention check
Retained prior pin audit: `CoinModel` real fields/defaults, `CollectionRow` 1-37; five collection call sites at 2736,2761-2770,2773-2782,3042-3045,3118-3124; dev catalog modal 810 and dispatch paths 80/466. Newly named dependencies are expressly new proposed production files, not claimed existing APIs. The problems above are in the proposed plan text itself, not an invented repository defect.

## Rubric
Standing locks 20/20; rollback/gate 12/15; navigation identity 14/15; laws/notes/outbound 14/15; guest privacy/images 14/15; accessibility 9/10; offline verification/shared harness 7/10 = **90/100**. No SAG advancement while these must-fixes remain.

## Privacy, gates, and filing
- Count-only exact private-promotion scan: **six current plans: 0; handoff tree: 0**. Handoff scope: 2,852 text files recursively under `BETA TEST/Grok Bot/8 OCT 26`, including RADIO NET, For SAG, BATONS, INBOX and OUTBOX. The historical literal was derived internally from the previously cited historical document and never printed. No claim that repository history was erased.
- PLAN ONLY. Main locked, US-only, Stripe sandbox/OFF, alerts only and never caps. No AJ/private collector values or promotion token reproduced.
- PASS is plan readiness only: CoS >=95 -> independent SAG reading the complete current plan >=95 -> Eric's explicit typed YES. Firestore writes and deployments each retain separate YES gates. No beta retest before Field Tester evidence closes every open item.
- DONE on a review baton means review completed, not approval. This executor prepared score files on the box only: repository filing and baton renames require a sanctioned repository-editing executor; CloudAgent was absent from this executor's available tool catalog. No repository write, commit, or rename is claimed here.
