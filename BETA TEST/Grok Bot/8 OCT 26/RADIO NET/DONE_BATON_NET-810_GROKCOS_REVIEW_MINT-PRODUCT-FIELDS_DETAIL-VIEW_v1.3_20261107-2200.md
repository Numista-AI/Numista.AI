# BATON NET-810 — GROKCOS REVIEW: Mint Product Fields Detail View Plan v1.3

- **Track ID:** NET-810 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Attempt:** AG CoS v5 attempt **3/4** on revision (v1.0 was 58 FAIL, v1.1 was 56 FAIL, v1.2 was 73 FAIL per `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.2_20261107.md` and `RADIO_NET-851`)
- **Date / DTG:** Saturday, 7 November 2026, 22:00 ET (`2026-11-07 22:00:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.3.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.3.md)
  - SHA256: `f0dba9076450e80fc6ce96212b9c75494fe23002f4e350f62cc3640251debd1d` (58,651 bytes)
- **Status:** **DELIVERED FOR GROKBOT COS REVIEW (>= 95 / 100)**
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's typed YES)

---

### Standing Operational Invariants & Pinned Boundaries
1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Direct pushes, merges, or cherry-picks to main are strictly prohibited.
2. **Stripe Lock:** Stripe strictly locked OFF across all environments.
3. **Budget Policy:** Governed strictly by an **alert-only threshold at $20.00/month** on Google Cloud Billing. Under no circumstances may any agent implement budget caps, hard limits, or automated Hosting teardowns.
4. **Zero Firestore Writes / Seeding:** Execution of this plan performs **0 writes, 0 updates, and 0 creates** in live Firestore or user collection documents.
5. **No Argon:** Cycle has NO Argon (Argon dropped permanently per Founder Eric typed YES 5 Nov 18:07 ET).
6. **Rule 6a Verbatim Code Citations:** All line references and code snippets are quoted verbatim from pinned commit `4d17ca5e` and `origin/dev`.

---

### Verification Summary of 5 Numbered Must-Fix Resolutions (Per Grok Bot CoS 73 FAIL Report & RADIO_NET-851)

1. **MF-1 (Real File:Line Citations vs `git show 4d17ca5e`):**
   - `_CoinDetailScreenState.initState`: Re-quoted verbatim at lines **`:183-193`** calling `_loadInspectorMode()`, explicitly noting that `:111-125` is `CoinDetailScreen.show` and that `_checkWishlist()` and `_loadProvenance()` do not exist in this file.
   - `_DetailsTab(` call site: Re-quoted verbatim at lines **`:774-778`** inside `TabBarView` at line **`:771`** (clarifying lines 845–855 are edit form notes / header comments).
   - `_DetailTile`: Re-quoted verbatim at lines **`:3268-3309`** (clarifying lines 1584–1620 start `_FinancialsTab`).
   - `toFirestore()` optimistic uses: Re-quoted verbatim at lines **`:491`** and **`:683`** (clarifying lines 490 and 682 are the `fromMap` constructor invocations).
   - Surgical diffs in Section 9 rewritten with hunks that apply cleanly at those verified lines.

2. **MF-2 (Demonstrable Real Records — Zero Invention):**
   - Discarded the invented `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1`.
   - Demonstrated real modern Mint product verified directly in `catalog_public_v1.json`:
     **`NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A`** (2024-W American Silver Eagle, West Point, Silver, Dollar, `status_badge: "Needs source"`, `is_placeholder: false`).
   - Retained the verified classic circulation strike:
     **`NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2`** (1921-D Morgan Silver Dollars, Denver, Dollar, `status_badge: "Needs source"`, `is_placeholder: false`).

3. **MF-3 (Status Allow-List & Public Catalog Alignment):**
   - Aligned the public catalog gate with real schema keys: **`is_placeholder == false`** (2,251 records pass; 951 placeholder stubs quarantined).
   - Removed non-existent `record_status` and invalid badge list `{PUBLISHED_ON_X, PREVIEW_DRAFT, PUBLISHED}`.
   - Verified that both `1921-D` and `2024-W` have `is_placeholder: false` and `status_badge: "Needs source"`, surviving the gate.
   - Strictly delineated public catalog schema fields (`nac_code`, `status_badge`, `is_placeholder`, `year`, `series`, etc.) from overlay metadata fields (`product_price_usd`, `mint_schedule_status`, `product_availability`, `release_date`).

4. **MF-4 (Compile-Safe Tests Failing for Right Reason):**
   - Resolved library-private `_DetailsTab` by exporting **`@visibleForTesting class DetailsTab extends StatelessWidget`** in `coin_detail_screen.dart`, enabling clean test compilation.
   - Injected **`FakeFirebaseFirestore`** in a dedicated zero-writes test verifying that initial collection count is 0 and remains 0 after lookup.
   - Replaced tautological hardcoded list test with a real serializer test asserting that the 10 forbidden private collector keys are absent from serialized overlay and public catalog records.
   - Dropped the impossible `GestureDetector` ancestor ban (acknowledging that `:3299` intentionally wraps values for clipboard copy); added an assertion guaranteeing zero commerce/cart/checkout navigation buttons or links (`ElevatedButton`, `TextButton`, `OutlinedButton`, or buy strings).

5. **MF-5 (Real Ingestion Script Input):**
   - Named the concrete planned input file for `scripts/export_mint_product_fields.py`:
     **`data/usmint/usmint_product_schedule_2024.json`** (official U.S. Mint Product Schedule export, explicitly marked **`STATUS: TO-BE-ACQUIRED / PLANNED`**).

Passing baton to GROKCOS for CoS review (target >= 95 / 100).
