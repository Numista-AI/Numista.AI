# BATON: GROKCOS Review Request — NET-813 Unified Coin Details View Plan v1.4

**To:** Grok Bot Chief of Staff (GROKCOS)  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**DTG:** 2026-11-07 19:25 ET (real clock, America/New_York)  
**Track:** NET-813 (Unified Coin Details View Plan v1.4)  
**Prior Score:** `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.3_20261107.md` (76/100 FAIL; 8 blocking must-fixes)  
**Code Pin:** `c294fd3c` (p7 branch)  
**Standing Locks:** `origin/main` locked at `9f04550a`; Stripe strictly OFF; strict PLAN ONLY; alerts only ($20/mo alert), never budget caps; no Argon.  

---

## 1. Deliverable for Review
- **Plan File:** [`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.4.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.4.md) (1,035 lines; 49.8 KB)

---

## 2. Surgical Resolution of the Eight Blocking Must-Fixes

1. **MF-1: Real Rollback & Flag Operations (§9):**
   - Replaced invalid `hosting:releases:list` with console release history and REST API `sites.releases.list` version capture at Gate 2.
   - Command: `firebase hosting:clone numista-vault@<PRE_DEPLOY_VERSION_ID> numista-vault:live` (bare version ID with `@` syntax).
   - Added `--site numista-vault` to channel deletion (`firebase hosting:channel:delete preview-unified-details --site numista-vault`).
   - Smoke tests hit `https://numista.ai/`, `https://numista.ai/catalog`, and known coin path `https://numista.ai/catalog/US-1921-MORGAN`.
   - Recorded SHA list artifact in `scratch/revert_shas_net813.txt` with per-SHA ancestry checks and conflict abort policy.
   - Kill-switch loader (`assets/config/features.json`) specifies cache-busting timestamp `?v=`, precedence over in-memory default, and notes rebuild/live-deploy gate.
   - `?unified_details=` query parameter rule: Can ONLY disable in production; NEVER enable (`kReleaseMode` guard).

2. **MF-2: Virtual-Child Navigation Identity (§3.1–3.5):**
   - When displayed coin is a parent, passes parent's filtered index: `docs.indexWhere((r) => r.id == parentDoc.id)` (or `null` for standalone), NOT child's `row` / `index`.
   - Actually passes `UnifiedCoinNavigationContext` into `show()` and `showPublic()`. Full signatures published in §3.1.
   - Transition resolver: Consecutive virtual children deduplicated to next distinct parent; parent cache miss mid-nav renders non-fatal in-modal warning banner; list changes retain loaded instance.
   - Unified missing-parent UX: Floating red SnackBar (`'Parent set details unavailable'`) across all 5 call sites.

3. **MF-3: Laws Provenance, Web Links & Unified Precedence (§6.1–6.4):**
   - Flutter Web renders links using `url_launcher` `Link` widget wrapping a validated `Uri` that passed `isValidCongressUrl`, never raw strings or bypasses.
   - Defined `_kCheckedLegislationManifest` in `assets/data/checked_legislation_manifest.json` with schema, review metadata, and unverified fallback badge.
   - Single unified precedence table in §6.4 covering Firestore success, timeout (>4s), errors, malformed data, and empty state. Contradiction between `_fallbackCheckedLaws` and empty state eliminated.

4. **MF-4: Rich-Content Boundary, Markdown & Storage Security (§3.5, §7.1–7.5):**
   - Added `strong`, `h3`, `listBullet`, `code` to theme-aware styleSheet, resolving inherited `Colors.white` (fixing real 2792).
   - Defined `sanitizeNotesText` stripping HTML, pseudo-protocols, and Markdown links. ZERO outbound links inside AI notes (Laws tab only).
   - Spec for amber callout banner: `"AI Analysis (Unverified Reference) — Valuation & attribution estimates must be independently verified"`.
   - Full `isOwnedStorageUrl` guard included with strict `/assets/` allowlist.
   - Restored rules prohibiting AI images in primary/card/index slots and prioritizing accepted user photos.

5. **MF-5: Public Entry Binding & Projections (§4, §5):**
   - Grounded on `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` (`_showItemDetailModal` line 810) and routes `/catalog` and `/catalog/<nacCode>`.
   - Defined NET-816 integration dependency (zero file transplants, zero main unlock).
   - Defined `PublicCoinProjection.fromCatalogItem` field by field with nullable `weightG`/`diameterMm` and `"Not Recorded"` display rules.
   - Guest sources: Verified catalog editorial text only; private-session AI insights strictly omitted.
   - Single Owner/Guest × Field × Source matrix in §5 resolving CPG vs AI value (guests see positive CPG only or "Valuation Pending").

6. **MF-6: Implementable Offline Test Plan (§10):**
   - Authored complete, compilable `UnifiedCoinDetailHarness` code with fake Firestore reads, clock, URL capture, and write counter.
   - Authored complete, non-truncated assertion bodies for all 11 unit/widget tests (zero comment stubs), covering contrast, navigation identity, value persistence, guest redaction, Congress link validation, Markdown sanitization, image security, and zero Firestore writes.

7. **MF-7: Ops Gates & Dated Checkpoints (§8, §11.1–11.3):**
   - Added dated checkpoints inside 10–16 Nov build window (10 Nov prep, 11 Nov preview, 12 Nov Field Test, 13 Nov Catalog live, 15 Nov Founder review, 16 Nov freeze).
   - Read-cost owner designated (AG CoS v5; target < 1 read/open; 0 on cache hit).
   - Laptop + GCS preservation precondition before reference library cleanup.
   - Separated "live Hosting deploy from p7" from "main merge" in Gate Table.

8. **MF-8: Handoff Integrity (§12):**
   - Real wall-clock DTG: `2026-11-07 19:25 ET`.
   - Baton sections verified 1:1 against plan headers.
   - Author line designated Antigravity Chief of Staff v5 (`cfe23a7a`).

---

## 3. Review Request
- Grok Bot CoS review requested for NET-813 v1.4 targeting $\ge 95/100$.
- Next step on $\ge 95$: SAG independent cross-review $\ge 95 \rightarrow$ Founder Eric typed YES preview gate.

OVER — Antigravity Chief of Staff v5 (`cfe23a7a`)
