# BATON NET-813 - GROKCOS REVIEW: Unified Coin Details View Plan v1.6

- **Track ID:** NET-813 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Attempt:** AG CoS v5 attempt **3/4** on revision (prior v1.3 was 76 FAIL, v1.4 was 86 FAIL, v1.5 was 81 FAIL per `RADIO_NET-846`)
- **Date / DTG:** Saturday, 7 November 2026, 20:30 ET (`2026-11-07 20:30:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.6.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.6.md)
- **Status:** **DELIVERED FOR GROKBOT COS REVIEW (>= 95 / 100)**
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's typed YES)

---

### Standing Operational Invariants & Pinned Boundaries
1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Direct pushes, merges, or cherry-picks to main are strictly prohibited.
2. **Stripe Lock:** Stripe strictly locked OFF across all environments.
3. **Budget Policy:** Governed strictly by an **alert-only threshold at $20.00/month** on Google Cloud Billing. Under no circumstances may any agent implement budget caps, hard limits, or automated Hosting teardowns.
4. **Zero Firestore Writes / Seeding:** Execution of this plan performs **0 writes, 0 updates, and 0 creates** in live Firestore or user collection documents.
5. **No Argon:** Cycle has NO Argon (Argon dropped permanently per Founder Eric typed YES 5 Nov 18:07 ET).
6. **Rule 6a Verbatim Code Citations:** All line references and code snippets are quoted verbatim from pinned commit `4d17ca5e`.

---

### Summary of Numbered Must-Fix Resolutions (Per Grok Bot CoS 81 FAIL Report & RADIO_NET-846)

1. **MF-1 (Re-quote Real Code Verbatim & Fix Site Count):**
   - Corrected call-site inventory in §1: Call Sites 1, 4, 5 invoke `_showCoinInspectorDialog` (`:2736`, `:3044`, `:3122`), while Call Sites 2 & 3 invoke `CoinDetailScreen.show(...)` (`:2761`, `:2773`).
   - Re-quoted §2.1–§2.4 and §2.7 verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` and `coin_detail_screen.dart` with zero paraphrasing.

2. **MF-2 (Wire-Up Compiles Cleanly & Passes Required Parameters):**
   - Eliminated non-existent `_allCoinsDocs`; correctly wired to existing `_cachedCoinsDocs` (`:131`).
   - Spliced table cell builder (`:2723-2736`) and card grid tap (`:3041-3045`) to pass `docs` directly into `UnifiedCoinNavigationContext`.
   - Carried all named arguments (`spotPrices`, `onNavigateToAiChat`, `onDeleted`, `onEdited`) through to `UnifiedCoinDetailScreen.show(...)`.

3. **MF-3 (Restore Verbatim Legislation Manifest Citations):**
   - Replaced paraphrased statute citations with verbatim strings from `_kDefaultLaws` (`121 Stat. 2014 (31 U.S.C. § 5112(r))`, `134 Stat. 5101 (31 U.S.C. § 5112(z))`).
   - Marked entries with `editorial_verified: false` pending downstream verification.

4. **MF-4 (True Mock Harness & Executable Assertions):**
   - Built full `UnifiedCoinDetailHarness` with `FakeFirestoreService` (real in-memory Map backing, operation counters, snapshot generators) and `FakeClock`.
   - Provided real snapshot fixtures for Test 5.
   - Fixed Test 9 to pump widget and query element text directly.
   - Spliced Test 12 to test owner photo priority and guest redaction against the identical fixture.
   - Wired Test 13 with fake clock timing out at 4.0s.

5. **MF-5 (Internal Navigation State & Virtual Child Persistence):**
   - Navigation state lives in `_UnifiedCoinDetailScreenState` (`_currentCoin`, `_currentSnapshot`, `_currentParentIndex`).
   - Added Test 14 testing two consecutive Next navigations across virtual children with state preserved.

6. **MF-6 (Handoff Hygiene & Pubspec Asset Declaration):**
   - Declared `assets/config/` in pubspec and file manifest.
   - Recorded prior delivery commit `00957e85` and set honest attempt **3/4**.

---

### Section Cross-Reference
- §1: Executive Summary & Call-Site Inventory (MF-1)
- §2: Ground-Truth Verbatim Code Citations (`origin/p7-v8.9` @ `4d17ca5e`) (MF-1)
- §3: Reconciling Five Call Sites & Virtual-Child Navigation Identity (MF-2 & MF-5)
- §4: Public Catalog Entry Binding & Projections
- §5: Single Owner/Guest × Field × Source Privacy & Valuation Matrix
- §6: Laws Provenance, Web Links & Unified Precedence (MF-3)
- §7: Rich-Content Sandbox, Typography & Storage Security
- §8: High-Contrast WCAG AAA & Senior Collector Accessibility
- §9: Rollback, Hosting Restore & Operational Kill-Switch (MF-6)
- §10: Implementable Offline Test Plan & Complete Test Suite (MF-4 & MF-5)
- §11: Operational Gate Table & Critical Path Checkpoints
- §12: Handoff Integrity & Authorship (MF-6)
