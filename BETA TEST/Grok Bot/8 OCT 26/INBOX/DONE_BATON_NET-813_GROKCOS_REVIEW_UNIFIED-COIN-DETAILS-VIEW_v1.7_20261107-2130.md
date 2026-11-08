# BATON NET-813 - GROKCOS REVIEW: Unified Coin Details View Plan v1.7

- **Track ID:** NET-813 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Attempt:** AG CoS v5 attempt **4/4** on revision (prior v1.3 was 76 FAIL, v1.4 was 86 FAIL, v1.5 was 81 FAIL, v1.6 was 89 FAIL per `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.6_20261107.md` and `RADIO_NET-849`)
- **Date / DTG:** Saturday, 7 November 2026, 21:30 ET (`2026-11-07 21:30:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.7.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.7.md)
  - SHA256: `51d04618f5a84615bc2a2f2db68ea201b57d3aefd6c998659c5f4c350a8f8069` (72,413 bytes)
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

### Verification Summary of 7 Numbered Must-Fix Resolutions (Per Grok Bot CoS 89 FAIL Report & RADIO_NET-849)

1. **MF-1 (§2.6 Subtitle Quote):**
   - Quoted line 925 verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart`:
     `style: const TextStyle(color: Colors.white60, fontSize: 12)),`
   - Replaced inaccurate "style: const TextStyle(fontSize: 12, color: Colors.grey)" and updated context lines 922–926.

2. **MF-2 (§4.1 Public Call Site Grounding):**
   - Quoted `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 466, 810, and 80 verbatim.
   - Explicitly clarified that line 315 on `origin/dev` is `child: Column(` (Morgan owl header layout) and is NOT a call site.
   - Grounded `UnifiedCoinDetailScreen.showPublic` directly into `_showItemDetailModal` (`:810`).

3. **MF-3 (Test 14 Consecutive Next Steps):**
   - Inserted a non-virtual parent coin `c0` (`1881-S Morgan Dollar`) before parent set `set_1`.
   - Executed two consecutive Next steps (`c0` -> `set_1` -> `c2`), asserting `currentParentIndex` after each step (0 -> 1 -> 4), verifying skip of virtual children without state loss.

4. **MF-4 (Test 13 In-Flight FakeClock):**
   - Mounted widget and pumped a single frame with legislation tab tapped so async request is outstanding in flight.
   - Advanced `harness.clock` by 5 seconds (exceeding 4.0s timeout) while request is in-flight, then called `pumpAndSettle()`.
   - Asserted graceful fallback to checked offline legislation manifest.

5. **MF-5 (Test 11 Fake Firestore Wiring):**
   - Pre-seeded fixture in `harness.firestoreService.seedDocument('c1', ...)` and verified read query.
   - Asserted `harness.firestoreService.writeCount == 0`, proving test harness asserts read-only and fails if writes occur.

6. **MF-6 (Test 12 Owner Fixture & Guest Redaction):**
   - Built single owner coin fixture with user accepted photo, reference image, and private fields (`storageLocation: 'Vault Box B'`, `personalNotes: 'Inherited'`, `purchaseCost: 45.00`).
   - Verified owner view renders user photo and private fields.
   - Derived guest view via `PublicCoinProjection.fromCoinModel(ownerCoin, referenceImageUrl: refPhoto)`.
   - Verified guest view renders reference photo and redacts all private fields to null/omitted.

7. **MF-7 (§12 Delivery Commit):**
   - Recorded delivery commit `2dbb525e` in §12 for v1.6 and documented current delivery on branch `dev`.

Passing baton to GROKCOS for CoS review (target >= 95 / 100).
