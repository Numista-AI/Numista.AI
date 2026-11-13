# BATON NET-813 - GROKCOS REVIEW: Unified Coin Details View Plan v1.5

- **Track ID:** NET-813 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Attempt:** AG CoS v5 attempt **2/4** on revision (prior v1.3 was 76 FAIL, v1.4 was 86 FAIL per `RADIO_NET-843`)
- **Date / DTG:** Saturday, 7 November 2026, 19:45 ET (`2026-11-07 19:45:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.5.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.5.md)
- **Status:** **DELIVERED FOR GROKBOT COS REVIEW ($\ge 95 / 100$)**
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's typed YES)

---

### Standing Operational Invariants & Pinned Boundaries
1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Direct pushes, merges, or cherry-picks to main are strictly prohibited.
2. **Stripe Lock:** Stripe strictly locked OFF across all environments.
3. **Budget Policy:** Governed strictly by an **alert-only threshold at $20.00/month** on Google Cloud Billing. Under no circumstances may any agent implement budget caps, hard limits, or automated Hosting teardowns.
4. **Zero Firestore Writes / Seeding:** Execution of this plan performs **0 writes, 0 updates, and 0 creates** in live Firestore or user collection documents.
5. **No Argon:** Cycle has NO Argon (Argon dropped permanently per Founder Eric typed YES 5 Nov 18:07 ET).
6. **Rule 6a Verbatim Code Citations:** All line references and code snippets are quoted verbatim from pinned commit `4d17ca5e` and `origin/dev` tip `6af2afb1`.

---

### Summary of Numbered Must-Fix Resolutions (Per Grok Bot CoS 86 FAIL Report)

1. **MF-1 (Map Projection & Tests to Real `CoinModel` / `CollectionRow`):**
   - Grounded strictly on `git show 4d17ca5e:numista_mobile/lib/models/coin_model.dart`.
   - Real fields used: `themeSubject` (no `name`), `year` as String, `mintMark` (camelCase), `imageUrlObverse`/`imageUrlReverse`, `personalNotes` (no `notes`), `metalContent` (no `composition`), `cpgRetail`, `storageLocation`.
   - `weightG` and `diameterMm` remain exclusively on `PublicCoinProjection` with `"Not Recorded"` fallback (zero invented constructor fields on `CoinModel`).
   - `CollectionRow` calls provide required `data: {'id': ...}`.
   - Deleted `showPublicWidget`; replaced with standard widget constructor `UnifiedCoinDetailScreen.public(projection: ...)`.

2. **MF-2 (Finish Harness & Implement Assertions That Can Fail):**
   - Authored full `UnifiedCoinDetailHarness` with injectable `fakeFirestoreService`, fake clock, write/read counters, URL launcher capture, and image loader capture.
   - Injected harness into tests so Test 11 genuinely asserts 0 writes against the injected service (`expect(harness.firestoreWriteCount, equals(0))`).
   - Added tests for Next navigation persistence (Test 5), guest eBay absence (Test 12), guest redactions (Test 12), user-photo priority over reference photos (Test 12), fake-clock laws timeout (Test 8), and Markdown `strong` contrast (Test 9).

3. **MF-3 (Fix Mid-Navigation Parent Identity & List Changes):**
   - In `_stepNavigation()`, if target parent is not in `filteredRows`, resolver passes `nextParentIndex = null` (standalone mode) — NEVER child's `targetIdx`.
   - Formally documented list-changes-while-open rule: modal retains captured `filteredRows` and `cachedCoinsDocs` instance from `UnifiedCoinNavigationContext` for modal session lifetime.

4. **MF-4 (Make Kill-Switch Loader Real & Fix Git Revert Loop):**
   - Updated kill-switch loader to load declared asset key `'assets/config/features.json'` directly without query strings (`?v=`).
   - Documented that cache busting occurs via Flutter web build hashing and live Hosting deploy.
   - Specified explicit shell loop over `scratch/revert_shas_net813.txt` asserting `git merge-base --is-ancestor "$sha" HEAD` before `git revert`.

5. **MF-5 (Correct Verbatim Cites, Restore Image/Link Defense, Drop Unverified Claims):**
   - Re-quoted verbatim markdown block from `git show 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart` `:2785–2805`.
   - Replaced contrast cite with `:59` (`_kDark`), `:892–893` (container), `:918–921` (title), `:925` (subtitle).
   - Restored defense-in-depth `imageBuilder: (uri, title, alt) => const SizedBox.shrink()` and `onTapLink: (text, href, title) {}` no-op.
   - Replaced sample legislation manifest with real `_kDefaultLaws` entries (HR 6184, 2414, 2764, 1923), marked verification pending.
   - Dropped unverified `/studio-9101802118-8c9a8-uploads/` prefix from `isOwnedStorageUrl`.

6. **MF-6 (Handoff Hygiene):**
   - Stamped plan and baton with honest wall-clock DTG matching file mtimes (`19:45 ET`).
   - Aligned every section cite in closeout table with actual document headings.
   - Explicitly stated attempt **2/4** on review baton.

---

### Section Cross-Reference
- §1: Executive Summary & Problem Statement
- §2: Ground-Truth Verbatim Code Citations (`origin/p7-v8.9` @ `4d17ca5e`)
- §3: Reconciling Five Call Sites & Virtual-Child Navigation Identity (MF-2 & MF-3)
- §4: Public Catalog Entry Binding & Projections (MF-1)
- §5: Single Owner/Guest × Field × Source Privacy & Valuation Matrix
- §6: Laws Provenance, Web Links & Unified Precedence (MF-5)
- §7: Rich-Content Sandbox, Typography & Storage Security (MF-4 & MF-5)
- §8: High-Contrast WCAG AAA & Senior Collector Accessibility
- §9: Rollback, Hosting Restore & Operational Kill-Switch (MF-4)
- §10: Implementable Offline Test Plan & Complete Test Suite (MF-1 & MF-2)
- §11: Operational Gate Table & Critical Path Checkpoints
- §12: Handoff Integrity & Authorship (MF-6)
