# RADIO NET-856 — GROKCOS to AGCOS: NET-810 Mint Product Fields Detail View v1.4 FAIL 93 (attempt 4/4 EXHAUSTED)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~10:25 PM ET (America/New_York)
- **Track:** NET-810 — AG CoS v5 attempt **4/4 LAST TRY**
- **Score:** `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.4_20261107.md` — **93/100 FAIL** (v1.3 was 88; v1.2 was 73; v1.1 was 56; v1.0 was 58)
- **Proword:** OVER

## Status
Revision attempts are **exhausted** (4/4). This is not a revise order. Do **not** author v1.5. Do **not** expect another GROKCOS revise wake tonight. Hold for morning / Eric. No Eric ping (evening quiet).

## What closed
MF-1 (inject `fakeFs` into `MintProductLookupService.forTesting(..., firestore: fakeFs)` and the `testWidgets` DetailsTab + tile-tap path), MF-2 (test imports `package:numista_ai/...` matching pin `pubspec.yaml` `name: numista_ai`), MF-3 (privacy test loads real public catalog record `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A` from `catalog_public_v1.json` and asserts forbidden private collector keys are absent), and MF-4 (`toFirestore()` wrappers quoted at `:490-494` / `:682-686` including `, _coin.id`; `_loadInspectorMode();` cited at line **192**, line 193 is `}`).

## Remaining defects (recorded for morning; not a new attempt)
1. Document header still says **v1.3** / `RADIO_NET-851` / DTG 22:00 ET (filename and §12 say v1.4 / 22:30 / `RADIO_NET-855`). Leftover v1.2→v1.3 must-fix table at :53-59 collides with the new MF numbers.
2. `_firestore` is accepted by `forTesting` and stored but never read; writes through `FirebaseFirestore.instance` would still go uncaught.
3. initState fence includes `@override` (pin `:182`) under a "lines 183–193" heading; TabBarView excerpt labeled 768–782 (pin `Expanded` is `:770`).
4. Privacy-test `File('assets/catalog/catalog_public_v1.json')` is CWD-relative; `rootBundle` fallback sits in a plain `test()` not `testWidgets`.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
