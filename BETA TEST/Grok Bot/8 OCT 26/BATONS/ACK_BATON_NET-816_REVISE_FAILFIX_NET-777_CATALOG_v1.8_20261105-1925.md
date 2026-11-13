# ACK BATON NET-816 — AG CoS v4 Taking Catalog FAILFIX Plan v1.8 (Thanksgiving Critical Path)
**From:** Antigravity CoS v4 (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Date:** 5 November 2026, 7:25 PM ET  
**Source Baton:** `BATON_NET-816_REVISE_FAILFIX_NET-777_CATALOG_v1.8_PER-COS-64-SAG-67_2026-11-05-1910.md`  
**Scores on v1.7:** CoS 64 FAIL / SAG 67 FAIL (`COS_SCORE_NET-815_FAILFIX-777-v1.7_20261105.md`, `SAG_SCORE_NET-815_FAILFIX-777-v1.7_20261105.md`)  
**Target Deliverable:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.8.md`  
**Protocol:** Argon DROPPED per Eric YES 6:07 PM ET 5 Nov FIN OPS. Forward chain: AG plan -> GB CoS (>=95) -> SAG (>=95) -> Founder Eric typed YES.  
**Mode:** PLAN ONLY. Zero code execution, zero deployments, zero Firestore writes/seeding or security rules changes.

---

## Must-Fix Action Items for Plan v1.8:

1. **Make Retail + Image Patch Compile Against Real Card (`_CatalogCard`):**
   - Promote nullable `valCpg` safely before `toStringAsFixed`.
   - Supply verified CPG source file, input schema, NAC join, and positive/missing/string-price/no-wholesale/no-AI tests.
   - Put host guard in a valid, accessible class scope; reconcile allowed hosts with `img-src` in `firebase.json:283–284`.
   - Test that 167 external primary/type URLs fail before fetch and verify approved internal/relative assets render.

2. **B05N-14 Model-Correct & Strict Fail-Closed (Known Errors):**
   - Address that real `MintError` has no `series`/`coinTypes` and `CoinModel` has `programSeries`, not `series`/`type`.
   - Specify fields, parser, and read migration (zero Firestore writes under this approval), all caller/helper signatures, and verified Greysheet server filtering.
   - Require both matching known series AND type AND applicable year for every branch, including nonempty years.
   - Supply negative 1958 Washington vs 1999 NJ and same-series positive assertions.

3. **B05N-15 / B27-8 Complete Structural Removal (Google Images & Kaggle):**
   - Clean structural deletion (avoiding partial line deletions that break widget syntax).
   - Remove Google Images callback/action and Similar/Kaggle surface; add timeout/error/finally terminal handling.
   - Cover microscope, ref-image doc, and `photo_sharing_service.dart` Kaggle ingestion.
   - Test no off-site photo action (Congress.gov on Laws tab only).

4. **B27-11 Light-Mode Contrast & Theme-Aware Typography:**
   - Replace p7 light-mode AI Insights white h1/h2/strong on white surface with theme-aware dark text.
   - Fix 11px pending chip `#B78103` on `#FFF8E1` (currently 3.21:1) to achieve at least 4.5:1 WCAG AA.
   - Contrast/field test requirements specified.

5. **Actual Deep-Link Code & Navigation:**
   - Real lines 71–82 match only `nac_code`, use `{}` orElse + `match.isNotEmpty` and post-frame modal callback; eliminate invented nullable `orElse`.
   - Implement browser history via actual Dart web interop, not `window.history` pseudocode.
   - Wire Morgan to existing `_openAskMorgan` callers and verified outer navigation; catalog MaterialApp has no named routes.

6. **Executable Verification:**
   - Reference real existing test file `test/catalog_browse_test.dart`.
   - Provide source/assertions/fixtures for any named new tests. Do not call tests "Verified" before execution.

---

## Standing Safeguards:
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- Zero deployments, zero Firestore writes. PLAN ONLY.
