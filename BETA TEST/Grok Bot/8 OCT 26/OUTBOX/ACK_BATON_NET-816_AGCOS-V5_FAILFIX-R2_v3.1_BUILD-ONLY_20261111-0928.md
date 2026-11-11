# ACK_BATON: NET-816 Fail-Fix R2 v3.1 Build-Only & Stop at READY-TO-DEPLOY

- **From:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot CoS, Eric
- **Timestamp:** 2026-11-11T09:28:00-05:00 (ET)
- **Reference Baton:** `BATON_NET-816_AGCOS-V5_FAILFIX-R2_v3.1_IMPLEMENT-PREVIEW_20261110-2148.md` (SHA-256 `bf74d5e57d5c88dceeba03c1de5379352c370d25a13ebe42f902374130c4d5df`)
- **Reference Auth & Note:**
  - `AUTH_NET-816_v3.1_BUILD_bf74d5e5_ERIC-YES_COS-CARD-t2588s9893_20261111-0910.md` (Eric YES on card `t2588s9893` at 09:10 ET)
  - `NOTE_AGCOS-V5_NET-816_v3.1_STOP-AT-READY-TO-DEPLOY_AUTH-8de8365e_20261111-0913.md` (Auth 8de8365e supersedes deploy step; stop at READY-TO-DEPLOY)

---

## 1. Plan Verification
- **Target Plan:** `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md`
- **Confirmed SHA-256:** `785B04E55CD3BC2CCEFCF40B970E2139AD84ABA679053DDE7A59BB0C9EC13D04` (41,293 bytes). Verified via `Get-FileHash`.

## 2. Scope & Execution Invariants
- **Branch:** `p7-v8.9` (base `a3d7dca20fbbaf06a522205b22d0740b600de52b`).
- **Code Edits:** Exactly files in Plan §4 items 1–6 (with edit (a) folding item 7 into item 6 inside `test/catalog_chunk1_face_value_and_card_test.dart`; `test/catalog_browse_test.dart` untouched).
- **Allowed Deviations:** Only deviations (a) and (b) per Baton §3.
- **Safety Invariants:** Zero pushes to origin; zero actions on `origin/main` (`9f04550a`); zero live channel deployments; zero Stripe, Firestore, or GCS mutations.
- **Stop Point:** STOP at **READY-TO-DEPLOY** upon passing all tests (`flutter analyze`, target tests, and full test suite). Report `BUILT_SHA` and test results. No deployment until Eric types his scoped YES DEPLOY line.

AG CoS v5 is executing the build and test runbook now.

WILCO.
