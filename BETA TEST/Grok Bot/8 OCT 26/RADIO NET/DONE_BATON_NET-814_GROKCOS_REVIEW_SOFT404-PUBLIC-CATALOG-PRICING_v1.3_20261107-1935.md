# BATON NET-814 - GROKCOS REVIEW: Soft-404 / Public Catalog / Pricing Plan v1.3

- **Track ID:** NET-814 (Architecture Plan: NET-801 v1.3 / Thanksgiving Critical Path)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Date / DTG:** Saturday, 7 November 2026, 19:35 ET (`2026-11-07 19:35:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.3.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.3.md)
  - Mirror: [`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.3.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.3.md)
- **Status:** **DELIVERED FOR GROKBOT COS REVIEW ($\ge 95 / 100$)**
- **Mode:** **STRICT PLAN ONLY** — Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero deployments without Founder Eric's typed YES.

---

### Standing Operational Invariants & Pinned Boundaries
1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Zero direct commits, merges, or pushes.
2. **Stripe Lock:** Stripe strictly locked OFF (zero active API keys, zero live checkout endpoints).
3. **Budget Policy:** **ALERTS ONLY** ($20.00/month Google Cloud Billing alert threshold). **NEVER budget caps, hard limits, or automated Hosting shutdowns.**
4. **No Argon:** Cycle has NO Argon (Argon dropped entirely per Founder Eric typed YES 5 Nov 18:07 ET).
5. **Catalog Chunk 1 Isolation:** Catalog Chunk 1 (NET-777/816) is strictly assigned to separate writer `9bbe20e4`. AG CoS v5 does NOT touch, reassign, or overwrite Chunk 1 work.

---

### Summary of Numbered Must-Fix Resolutions (Per CoS 66 FAIL)

1. **MF-1 (Cap Removal & Approved Public Catalog Preservation):**
   - Struck all "$25 hard limit", mandatory hosting shutdowns, and automated budget caps from P50, P280, and P309–313.
   - Cost protection is established strictly via an **alert-only threshold at $20.00/month** through Google Cloud Billing Pub/Sub alerts with notification to Founder Eric and AG CoS desk.
   - Struck all reopening of Options A/B/C, modal-only popups, and gated catalog detours (P31–33, 83–91, 344). **Founder Eric has already approved `/catalog` remaining PUBLIC when signed out.** We preserve this architectural decision unconditionally without any prerequisite architectural vote or authentication barrier.

2. **MF-2 (Route HTML & Hosting Agreement, Including Per-Coin URLs):**
   - Grounded on real target `firebase.json` (`site: numista-vault`, `public: build/web`, `trailingSlash: false`).
   - Specified deterministic generator script (`numista_mobile/web/templates/generate_static_routes.py`) producing pre-rendered entry points in `build/web/catalog/index.html` and `build/web/pricing/index.html`.
   - Guaranteed root base resolution with `<base href="/">` in all HTML heads so nested catalog requests (`/catalog/US-1921-MORGAN`) never fail to load root scripts or assets.
   - Specified ordered `firebase.json` rewrites and exact Cache-Control headers (`no-cache` for HTML; immutable for static hashed assets).
   - Provided distinct per-route OpenGraph metadata, canonical tags, and same-party OG image (`https://numista.ai/icons/Icon-512.png` at 512x512 with descriptive alt text).
   - In `catalog_browse_screen.dart`, resolved the unknown NAC soft-404 risk by rendering a dedicated in-screen `_CatalogNotFoundBanner` rather than a transient SnackBar over a 200 OK catalog.

3. **MF-3 (Complete Branch Integration Contract):**
   - Ground truth check confirms target `4d17ca5e:numista_mobile/lib/main.dart:122-148` lacks `/catalog` and renders `NotFoundScreen`, while `origin/dev:numista_mobile/lib/main.dart:133-180` contains public direct entry.
   - Specified exact integration manifest:
     * Line 12: `import 'screens/catalog/catalog_browse_screen.dart';`
     * Asset declaration: Add `- assets/catalog/` to `pubspec.yaml` (matching `dev` line 97; target lines 92–96 lack it).
     * Route whitelist: Add `normalizedPath == '/catalog' || path.startsWith('/catalog/')` to `isKnownPath`.
     * Direct entry dispatch: Preserved dev's exact light theme (`ThemeData(brightness: Brightness.light, scaffoldBackgroundColor: Colors.white, ...)`), query parameter fallback (`?item=`), and `Uri.decodeComponent`.
     * Preserved all unrelated routes (`/wishlist`, `/attorney_portal`, `/about`, `/pricing`, `/login`, etc.) and preserved true 404 behavior for unknown paths.
     * Reconciled NET-816 ownership: Catalog Chunk 1 is strictly owned by writer `9bbe20e4` (attempt 3/4); NET-814 coordinates route dispatch, static HTML, and pricing surface only.

4. **MF-4 (Master Data Sourcing, Eligibility, and Strict Privacy Protection):**
   - Master input verified at `assets/catalog/catalog_master_3202.jsonl`, containing exactly **3,202 nonblank records, 3,202 unique NAC codes** (2,965 coins, 181 notes, 56 medals) with SHA256 `FBA6C66A107E5304D801997C01F22681E072FA7E8F8AA8761D5A2738ADE31BEF`.
   - Content eligibility: Acknowledged all 3,202 entries are marked `proposal_status=PROPOSAL` and `needs_fact_check: true`. Struck all claims of "100% verified by US Mint"; used neutral reference copy: `"Numista Reference Catalog Entry"`.
   - Updated `login_screen.dart:338, 466` from `'5,142'` to `'3,202'` and label `'Reference\nCoins & Notes'`. Purged unsourced claims (`99.4%`, `5,000+ indexable pages`, `advisory board`, `Sheldon grading standard guarantee`, `Passport Protocol`).
   - Strict Privacy Prohibitions: Strictly prohibited AJ identifying information, user PII, private collection identifiers, purchase costs, internal acquisition notes, and user photos from public catalog assets, metadata, fixtures, and logs.

5. **MF-5 (Real Retail Join & Complete Image/Data Projection):**
   - Named authorized retail join: **CPG® Retail Price Guide Reference Feed (CDN Publishing, Version 2026.11)** joining strictly on `nac_code` (with fallback to `year + mint + variety + grade`).
   - Currency: USD (`$`). Includes source attribution and as-of timestamp.
   - Missing/invalid join policy: Fails closed to `cpgRetail: null` and renders a styled gold chip: `'Valuation Pending'`. Positive `cpgRetail > 0` is never displaced.
   - Completely excluded wholesale pricing (dealer bid/ask) and private collection totals.
   - Images: Acknowledged 248 primary maps and 966 type maps. Prohibited unguarded `Image.network` to arbitrary third-party URLs. All public catalog images must resolve to approved first-party Firebase Storage (`storage.googleapis.com/numista-vault.firebasestorage.app/reference_catalog/**`) or local bundled assets (`assets/catalog/images/**`). Missing images render `_buildPlaceholder()`.
   - Confined AI images strictly to labeled `ai_replica_images` sections; zero AI images in primary, type, card, or index slots.
   - Attribution: Removed clickable outbound link in `catalog_browse_screen.dart:987-1017` (`InkWell` launching `source_url`); replaced with plain text attribution (`Text('Source: ${mintage?['label'] ?? 'US Mint'}')`). Zero outbound links in public cards/modals.

6. **MF-6 (Targeted Git Rollback & Real Firebase Hosting Release Restore):**
   - Replaced broad `$PRE_EXEC_SHA..HEAD` revert with targeted revert of exact feature commit SHAs: `git revert --no-edit <FEATURE_COMMITS>`.
   - Recorded pre-execution SHA anchor: `PRE_EXEC_SHA=$(git rev-parse HEAD)`. Verified branch ancestry before pushing.
   - Real Firebase Hosting rollback:
     * Captured pre-deploy release version ID: `PRE_DEPLOY_VERSION_ID=$(firebase hosting:channel:list --site numista-vault ...)` (or Firebase Console release version).
     * Real restore command: `firebase hosting:clone numista-vault@<PRE_DEPLOY_VERSION_ID> numista-vault:live`.
     * Preview channel teardown: `firebase hosting:channel:delete preview-net814 --site numista-vault --force`.
     * Automated post-rollback smoke probes hitting `https://numista.ai/`, `https://numista.ai/catalog`, and `https://numista.ai/pricing`.
     * Deployments strictly isolated to Hosting: `firebase deploy --only hosting --site numista-vault` to prevent rules, database, or function changes from riding along.

7. **MF-7 (Pricing Content, AuthGate Precedence, and Operational Gates):**
   - Ground truth in `public_info_screens.dart:362-420`: Replaced outdated "Free During Beta — Pricing TBA", "$0/month", and "entirely free features" with approved static copy covering:
     * **Free 10-Coin Trial:** `"Free 10-Coin Trial — Scan and evaluate your first 10 coins with full AI numismatic appraisal."`
     * **US-Only Coverage:** `"US-Only Reference Database — Currently supporting United States coinage, tokens, medals, and currency."`
     * **Grandfathered Beta Access:** `"Active Beta Participants Grandfathered — Continuous access to personal collection records."`
     * **Stripe Strictly OFF:** Zero payment inputs, zero checkout buttons. Notice: `"Subscription options will open at general release. No payment method required during preview."`
   - AuthGate Precedence (`widgets/auth_gate.dart`): Moved `if (widget.publicRoute != null) return PublicInfoShell(targetRoute: widget.publicRoute!);` ahead of the signed-in `snapshot.hasData` check (after `ConnectionState.waiting`).
   - Semantic Link Widget in `login_screen.dart:585-608`: Replaced raw `InkWell` + `Navigator.push` with Flutter `Link(uri: Uri.parse('/pricing'), builder: ...)` emitting native `<a href="/pricing">` DOM nodes.
   - Operational Gates: Required separate Eric typed YES for Firestore writes and separate Eric typed YES for rules deploys.
   - Dated Checkpoints: Schedule targeted for **Catalog Live ~13 Nov 2026** (inside 10–16 Nov build window) ahead of 26 Nov Meta Ads launch.

8. **MF-8 (Reproducible Verification Strategy):**
   - Marked tests explicitly as **To be authored** (eliminating false completion claims).
   - Provided complete, runnable harness specifications (`PublicCatalogRoutingHarness`, `AuthGatePublicRouteHarness`, `StaticRouteHtmlHarness`, `CensusAndPrivacyHarness`) with offline fixtures, injected auth streams, fake clocks, zero-write counters (`expect(harness.firestoreWriteCount, equals(0))`), image host guards, and accessibility criteria (WCAG AA contrast, 48x48 tap targets).

---

### Handoff Request to Grok Bot CoS
Please review `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.3.md` against the above 8 must-fix resolutions. Target: **$\ge 95 / 100$ PASS**.
Upon PASS, route baton to SAG (`Stand Alone Grok`, grok-4.7) for independent review ($\ge 95$), followed by Founder Eric's explicit typed YES.
