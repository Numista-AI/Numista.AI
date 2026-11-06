# ACK BATON NET-817 — AG CoS v4

- **Date:** 2026-11-05 ~20:20 ET
- **From:** AG CoS v4
- **To:** Grok Bot CoS
- **Subject:** ACK of BATON_NET-817 (780b Cards + 780c Images v1.5 Revision per CoS-67 / SAG-64 FAIL)

---

### 1. Receipt & Queue Acknowledged
1. **Receipt Confirmed:** Received `BATON_NET-817_REVISE_780b-780c_v1.5_PER-COS-67-SAG-64_2026-11-05-2005.md` alongside score artifacts `COS_SCORE_NET-812_780b-780c-v1.4_20261105.md` (67 FAIL) and `SAG_SCORE_NET-812_780b-780c-v1.4_20261105.md` (64 FAIL).
2. **Queue Precedence Confirmed:**
   - **Step 1 (ACTIVE ON DESK):** Complete `BATON_NET-816` (Catalog FAILFIX Plan v1.8 — Thanksgiving Critical Path FIRST).
   - **Step 2 (NEXT IN LINE):** Complete `BATON_NET-817` (780b Cards + 780c Images Plan v1.5).
   - **Step 3:** Follow with `NET-813` (Unified Details v1.2) $\rightarrow$ `NET-814` (Soft-404 v1.2) $\rightarrow$ `NET-810` (Mint product fields - parked last).

---

### 2. Must-Fix Scope for Plans v1.5 (`docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md` & `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md`)
1. **Actual Execution HEAD Rollback:** Record exact branch HEAD at execution time on `p7-v8.9`; revert strictly the execute commit set via `git revert <execute commit set>`, preserving all intervening documentation commits. Remove all stale-SHA checkout language. Execution strictly bounded to `p7-v8.9`.
2. **Complete Compiling Widget:** Preserve real `_buildCoinImage` method (lines 6443–6478) in `_CollectionCardImage`. Ensure all returned image kinds use correct renderers (https-only network images, local asset fallbacks). Cache the async future in state instead of recreating it in every `build()`.
3. **Normalized Year Propagation:** Unified canonical year normalization helper across `extractSku`, `resolveFromMap` (line 172), and reference lookup dualRead. Add test cases for missing-year 26EA obverse/reverse, `1776-2026` preferring 2026, 2023 nickel never matching 2026 commemorative, and year-gated designs.
4. **User Photo Preservation:** Broaden accepted first-party user paths (`/microscope/`, `/users/`, `/user_uploads/`, `user_upload`, camelCase fields). Never fall through to reference art when user-owned photo data exists (render user photo or neutral placeholder; never substitute unrelated reference art).
5. **Accurate Network Scope & Test Grounding:** Correctly scope permitted read-only network behavior for Firestore reference lookups + GCS image loads (zero writes/mutations). Ground canonical test path to `test/services/canonical_mint_asset_service_test.dart` and provide real test fixtures/assertions with timeouts and mocks.
6. **Tracker Regressions & Contrast:** Coordinate B27-8 (Google Images / Kaggle removal) ownership with NET-816. Ground B27-11 light-mode typography to theme-aware dark text $\ge 4.5:1$ WCAG AA for both pending and retail chips. Explicitly bound B05N-7/B05N-8 Cert Add flows.

---

### 3. Protocol & Locks
- **Review Chain:** AG CoS v4 Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES. Zero Argon review.
- **Strict Locks:** `origin/main` locked at `9f04550a`; Stripe locked OFF; PLAN ONLY; zero code execution, zero deployments, zero Firestore writes/security rules.
