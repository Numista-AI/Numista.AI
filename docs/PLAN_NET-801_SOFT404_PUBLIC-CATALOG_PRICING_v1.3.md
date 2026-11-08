# Architecture & Implementation Plan: NET-801 v1.3 (BATON_NET-814)
## Public Catalog Direct Route, Soft-404 Elimination, Static Entry Generation, Retail Pricing Projection & Pricing Surface Plan v1.3

- **Track ID:** NET-801 v1.3 / BATON_NET-814 (Critical Path for Catalog Live ~13 Nov 2026 ahead of Meta Ads 26 Nov 2026)
- **Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Review Cycle:** Grok Bot Chief of Staff (Target: $\ge 95/100$) $\rightarrow$ Stand Alone Grok (SAG grok-4.7 Target: $\ge 95/100$) $\rightarrow$ Founder Eric Explicit Typed YES
- **Target Branch:** `origin/p7-v8.9` (Dual-synced with `origin/dev` @ `48bb1427`)
- **Filing DTG:** Saturday, 7 November 2026, 19:35 ET (`2026-11-07 19:35:00 -05:00`)
- **Status:** **STRICT PLAN ONLY** — Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero deployments without Founder Eric's explicit typed YES.
- **Standing Operational Boundaries:**
  - `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Zero direct merges, pushes, or PR merges to `main`.
  - Stripe strictly locked OFF (zero active API keys, zero live checkout endpoints).
  - Cost control is **ALERTS ONLY** ($20.00/month Google Cloud Billing alert threshold); **NEVER budget caps, hard limits, or automated Hosting shutdowns**.
  - Cycle has **NO Argon** (Argon permanently dropped per Founder Eric typed YES 5 Nov 18:07 ET).
  - Reference Pin for Verbatim Quotes: `4d17ca5e` (`origin/p7-v8.9`) and `origin/dev`.

---

## 1. Executive Summary & Ground-Truth Alignment (Resolving CoS-66 Must-Fixes)

This revised v1.3 plan systematically resolves all eight numbered blocking must-fixes from `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.2_20261106.md` (66/100 FAIL), rebasing strictly on verified repository ground truth:

1. **Remove the Cap; Preserve the Already-Approved Public Catalog (MF-1):**
   - Strike all "$25 hard limit", mandatory hosting shutdowns, and automated budget caps from P50, P280, and P309–313.
   - Cost protection is established strictly via an **alert-only threshold at $20.00/month** through Google Cloud Billing Pub/Sub alerts. The notification owners are Founder Eric and AG CoS Desk, with measured operational escalation (cache hit verification, CDN rate limiting), never automated site destruction or budget shutdowns.
   - Strike all reopening of Options A/B/C, modal-only popups, and gated catalog detours (P31–33, 83–91, 344). **Founder Eric has already approved `/catalog` remaining PUBLIC when signed out.** We preserve this architectural decision unconditionally without any prerequisite architectural vote or authentication barrier.

2. **Route HTML and Hosting Agreement, Including Per-Coin URLs (MF-2):**
   - Real target `firebase.json` serves `build/web` (line 8) with `"trailingSlash": false` (line 9). Rewriting `/catalog` and `/pricing` to `/index.html` causes client-side routing conflicts and deprives search/social crawlers of static metadata.
   - We specify a deterministic generator script (`numista_mobile/web/templates/generate_static_routes.py`) run as a build-copy step into `build/web/catalog/index.html` and `build/web/pricing/index.html`.
   - Specify ordered `firebase.json` rewrites and exact Cache-Control headers (`no-cache` for HTML; long-term immutable caching for static hashes).
   - Guarantee root base resolution with `<base href="/">` in all HTML heads so nested catalog requests (`/catalog/US-1921-MORGAN`) never fail to load root scripts or assets.
   - Provide distinct per-route OpenGraph (OG) metadata, canonical tags, and same-party OG image (`https://numista.ai/icons/Icon-512.png` at 512x512 with descriptive alt text).
   - In `catalog_browse_screen.dart`, resolve the unknown NAC soft-404 risk by rendering a dedicated in-screen `_CatalogNotFoundView` rather than a transient SnackBar over a 200 OK catalog.

3. **Complete Branch Integration Contract (MF-3):**
   - Ground truth check confirms target `4d17ca5e:numista_mobile/lib/main.dart:122-148` lacks `/catalog` and renders `NotFoundScreen`, while `origin/dev:numista_mobile/lib/main.dart:133-180` contains public direct entry.
   - Specify the exact integration manifest:
     * Line 12: `import 'screens/catalog/catalog_browse_screen.dart';`
     * Asset declaration: Add `- assets/catalog/` to `pubspec.yaml` (matching `dev` line 97; target lines 92–96 lack it).
     * Route whitelist: Add `normalizedPath == '/catalog' || path.startsWith('/catalog/')` to `isKnownPath`.
     * Direct entry dispatch: Preserve dev's exact light theme (`ThemeData(brightness: Brightness.light, scaffoldBackgroundColor: Colors.white, ...)`), query parameter fallback (`?item=`), and `Uri.decodeComponent`.
     * Preserve all unrelated routes (`/wishlist`, `/attorney_portal`, `/about`, `/pricing`, `/login`, etc.) and preserve true 404 behavior for unknown paths.
     * Reconcile NET-816 ownership: Catalog Chunk 1 is strictly owned by writer `9bbe20e4` (attempt 3/4 per `RADIO_NET-839/841`); NET-814 coordinates route dispatch, static HTML, and pricing surface only.

4. **Master Data Sourcing, Eligibility, and Strict Privacy Protection (MF-4):**
   - Ground truth census: Master input is located at `assets/catalog/catalog_master_3202.jsonl` (and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl`), verified at exactly **3,202 nonblank records, 3,202 unique NACs** (2,965 coins, 181 notes, 56 medals) with SHA256 `FBA6C66A107E5304D801997C01F22681E072FA7E8F8AA8761D5A2738ADE31BEF`.
   - Content eligibility: Acknowledge that all 3,202 entries are marked `proposal_status=PROPOSAL` and `needs_fact_check: true` (951 PLACEHOLDER, 2,231 PREVIEW_DRAFT, 13 PUBLISHED_ON_X, 7 DRAFT_POST).
   - Strike all blanket claims of "100% verified by US Mint" or "Mint-certified". Use neutral reference copy: `"Numista Reference Catalog Entry"`.
   - Update `login_screen.dart:338, 466` from `'5,142'` to `'3,202'` and label `'Reference\nCoins & Notes'`. Delete unsourced claims (`99.4%`, `5,000+ indexable pages`, `advisory board`, `Sheldon grading standard guarantee`, `Passport Protocol`).
   - Strict Privacy Prohibitions: Strictly prohibit AJ identifying information, user PII, private collection identifiers, purchase costs, internal acquisition notes, and user photos from public catalog assets, metadata, fixtures, and logs.

5. **Name the Real Retail Join and Complete Image/Data Projection (MF-5):**
   - Authorized retail join: Name the **CPG® Retail Price Guide Reference Feed (CDN Publishing, Version 2026.11)** joining strictly on `nac_code` (with fallback to `year + mint + variety + grade`).
   - Display currency: USD (`$`). Include source attribution and as-of timestamp.
   - Missing/invalid join policy: Fail closed to `cpgRetail: null` and render a styled gold chip: `'Valuation Pending'`. Positive `cpgRetail > 0` is never displaced.
   - Completely exclude wholesale pricing (dealer bid/ask) and private collection totals.
   - Images: Acknowledge 248 primary maps (167 URL-style, 81 file-style) and 966 type maps. Prohibit unguarded `Image.network` to arbitrary third-party URLs. All public catalog images must resolve to approved first-party Firebase Storage (`storage.googleapis.com/numista-vault.firebasestorage.app/reference_catalog/**`) or local bundled assets (`assets/catalog/images/**`). Missing images render `_buildPlaceholder()`.
   - Confine AI images strictly to labeled `ai_replica_images` sections; zero AI images in primary, type, card, or index slots.
   - Attribution: Remove the clickable outbound link in `catalog_browse_screen.dart:987-1017` (`InkWell` launching `source_url`); replace with plain text attribution (`Text('Source: ${mintage?['label'] ?? 'US Mint'}')`). Zero outbound links in public cards/modals.

6. **Finish Rollback; Real Git and Firebase Hosting Recovery (MF-6):**
   - Replace broad `$PRE_EXEC_SHA..HEAD` revert with targeted revert of exact feature commit SHAs: `git revert --no-edit <FEATURE_COMMITS>`.
   - Record pre-execution SHA anchor: `PRE_EXEC_SHA=$(git rev-parse HEAD)`. Verify branch ancestry before pushing.
   - Real Firebase Hosting rollback:
     * Capture pre-deploy release version ID: `PRE_DEPLOY_VERSION_ID=$(firebase hosting:channel:list --site numista-vault ...)` (or Firebase Console release version).
     * Real restore command: `firebase hosting:clone numista-vault@<PRE_DEPLOY_VERSION_ID> numista-vault:live`.
     * Preview channel teardown: `firebase hosting:channel:delete preview-net814 --site numista-vault --force`.
     * Automated post-rollback smoke probes hitting `https://numista.ai/`, `https://numista.ai/catalog`, and `https://numista.ai/pricing`.
     * Deployments strictly isolated to Hosting: `firebase deploy --only hosting --site numista-vault` to prevent rules, database, or function changes from riding along.

7. **Pricing Content, AuthGate Precedence, and Operational Gates (MF-7):**
   - Ground truth in `public_info_screens.dart:362-420`: Replace outdated "Free During Beta — Pricing TBA", "$0/month", and "entirely free features" with approved static copy covering:
     * **Free 10-Coin Trial:** `"Free 10-Coin Trial — Scan and evaluate your first 10 coins with full AI numismatic appraisal."`
     * **US-Only Coverage:** `"US-Only Reference Database — Currently supporting United States coinage, tokens, medals, and currency."`
     * **Grandfathered Beta Access:** `"Active Beta Participants Grandfathered — Continuous access to personal collection records."`
     * **Stripe Strictly OFF:** Zero payment inputs, zero checkout buttons. Notice: `"Subscription options will open at general release. No payment method required during preview."`
   - AuthGate Precedence (`widgets/auth_gate.dart`): Move `if (widget.publicRoute != null) return PublicInfoShell(targetRoute: widget.publicRoute!);` ahead of the signed-in `snapshot.hasData` check (after `ConnectionState.waiting`).
   - Semantic Link Widget in `login_screen.dart:585-608`: Replace raw `InkWell` + `Navigator.push` with Flutter `Link(uri: Uri.parse('/pricing'), builder: ...)` emitting native `<a href="/pricing">` DOM nodes.
   - Operational Gates: Require separate Eric typed YES for Firestore writes and separate Eric typed YES for rules deploys.
   - Dated Checkpoints: Schedule targeted for **Catalog Live ~13 Nov 2026** (inside 10–16 Nov build window) ahead of 26 Nov Meta Ads launch.

8. **Reproducible Verification Strategy (MF-8):**
   - Mark tests explicitly as **To be authored** (eliminating false completion claims).
   - Provide complete, runnable harness specifications (`PublicCatalogRoutingHarness`, `AuthGatePublicRouteHarness`, `StaticRouteHtmlHarness`, `CensusAndPrivacyHarness`) with offline fixtures, injected auth streams, fake clocks, zero-write counters (`expect(harness.firestoreWriteCount, equals(0))`), image host guards, and accessibility criteria (WCAG AA contrast, 48x48 tap targets).

---

## 2. Standing Operational Constraints & Pinned Boundaries

All work in this track is bound unconditionally by the following operational boundaries:

| Boundary | Pinned Invariant | Enforcement / Verification Command |
|---|---|---|
| **Production Branch** | `origin/main` locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45` | `git rev-parse origin/main` $\rightarrow$ must output `9f04550a...` |
| **Execution Mode** | **STRICT PLAN ONLY** (Preview gate only) | Zero code changes, zero builds, zero deploys without Eric typed YES |
| **Stripe Status** | **STRIPE STRICTLY OFF** | Zero live keys, zero active Stripe checkout endpoints |
| **Cost Controls** | **ALERTS ONLY** ($20.00/month threshold) | Google Cloud Billing alert notification; **NO budget caps or site shutdowns** |
| **Cycle Reviewers** | GB CoS $\ge 95 \rightarrow$ SAG $\ge 95 \rightarrow$ Eric typed YES | **NO ARGON** (Argon dropped per Eric typed YES 5 Nov 18:07 ET) |
| **Chunk 1 Ownership** | Catalog Chunk 1 owned by `9bbe20e4` | NET-814 coordinates routing/HTML/pricing only; does not touch Chunk 1 |
| **Privacy Safeguards** | Zero AJ PII / private collection data | Zero user acquisition costs, private notes, or user photos in public assets |

---

## 3. Route HTML and Firebase Hosting Agreement (Resolving MF-2)

### 3.1 Ground Truth in `numista_mobile/firebase.json`
Verbatim from `numista_mobile/firebase.json` lines 6–15:
```json
  "hosting": {
    "site": "numista-vault",
    "public": "build/web",
    "trailingSlash": false,
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
```
Verbatim from lines 77–80:
```json
      {
        "source": "/pricing",
        "destination": "/index.html"
      },
```

### 3.2 The Defect
1. `firebase.json` declares `"public": "build/web"`. Files authored or modified in `web/` are not served directly by Firebase Hosting; they must be processed or copied into `build/web/` during the build step.
2. In production, rewriting `/catalog` and `/pricing` to `/index.html` serves the single-page application entry point. Web crawlers (e.g. Meta's `facebookexternalhit`, Googlebot) inspecting raw HTTP responses receive generic root homepage meta tags rather than route-specific OpenGraph titles, descriptions, and canonical URLs.
3. Because `"trailingSlash": false` is set, a request to `https://numista.ai/catalog` looks for `build/web/catalog.html` or `build/web/catalog/index.html`. If physical files are present, Firebase Hosting serves the static file before evaluating general rewrites.

### 3.3 The Generator & Build-Copy Step
To guarantee deterministic static route serving, a Python generator script `numista_mobile/web/templates/generate_static_routes.py` will be authored and integrated into the web build pipeline:

```bash
# Web Build & Static Route Generation Pipeline
flutter build web --release --base-href "/"
python3 numista_mobile/web/templates/generate_static_routes.py \
  --template numista_mobile/web/templates/route_template.html \
  --output-dir numista_mobile/build/web
```

The generator produces:
- `numista_mobile/build/web/catalog/index.html`
- `numista_mobile/build/web/pricing/index.html`

### 3.4 Ordered Rewrites and Cache-Control Headers in `firebase.json`
In `numista_mobile/firebase.json`, update `rewrites` and add explicit `headers`:

```json
    "headers": [
      {
        "source": "**/*.@(html|json)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/assets/**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      }
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "numista-backend",
          "region": "us-central1"
        }
      },
      {
        "source": "/catalog",
        "destination": "/catalog/index.html"
      },
      {
        "source": "/catalog/**",
        "destination": "/catalog/index.html"
      },
      {
        "source": "/pricing",
        "destination": "/pricing/index.html"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
```

### 3.5 Root Base and Asset Resolution (`<base href="/">`)
To prevent nested routes (`/catalog/US-1921-MORGAN`) from resolving relative scripts (e.g., `flutter.js`, `main.dart.js`, favicon) against `/catalog/`, all generated HTML files must include `<base href="/">` immediately following `<meta charset="UTF-8">`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <base href="/">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Numista.AI Reference Catalog — US Coins & Currency</title>
  <meta name="description" content="Explore reference specifications, mintage data, and CPG retail pricing across 3,202 United States coins, notes, and medals." />
  
  <!-- OpenGraph Metadata for Crawlers & Social Previews -->
  <meta property="og:site_name" content="Numista.AI" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Numista.AI Reference Catalog — US Coins & Currency" />
  <meta property="og:description" content="Explore reference specifications, mintage data, and CPG retail pricing across 3,202 United States coins, notes, and medals." />
  <meta property="og:url" content="https://numista.ai/catalog" />
  <meta property="og:image" content="https://numista.ai/icons/Icon-512.png" />
  <meta property="og:image:width" content="512" />
  <meta property="og:image:height" content="512" />
  <meta property="og:image:alt" content="Numista.AI Reference Catalog — US Coin and Currency Reference" />
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Numista.AI Reference Catalog — US Coins & Currency" />
  <meta name="twitter:description" content="Explore reference specifications, mintage data, and CPG retail pricing across 3,202 United States coins, notes, and medals." />
  <meta name="twitter:image" content="https://numista.ai/icons/Icon-512.png" />
  
  <link rel="canonical" href="https://numista.ai/catalog" />
  <link rel="icon" type="image/png" href="favicon.png" />
  
  <!-- Flutter Web Bootstrap -->
  <script src="flutter.js" defer></script>
</head>
<body>
  <div id="flutter_host"></div>
</body>
</html>
```

### 3.6 Elimination of In-App Soft-404 on Unknown NAC Code
Verbatim from `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 86–98:
```dart
          } else {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'We don\'t have item "${widget.initialNacCode}" in our reference catalog yet.',
                      style: const TextStyle(fontSize: 16),
                    ),
                    backgroundColor: const Color(0xFF0B2545),
                    duration: const Duration(seconds: 4),
                  ),
                );
              }
            });
          }
```
**Defect:** If a user or crawler visits `https://numista.ai/catalog/INVALID-NAC`, the server returns HTTP 200 (via rewrite), and the client displays a brief SnackBar over the full catalog browse view. Search crawlers flag this as a soft-404 (an error message rendered on a 200 OK page with unchanged URL).

**Resolution:**
When `match.isEmpty`, `CatalogBrowseScreen` will:
1. Update browser history via `window.history.replaceState({}, '', '/catalog');` (on web) to cleanly normalize the canonical URL.
2. Render an explicit in-screen notice banner `_CatalogNotFoundBanner` at the top of the catalog:
   ```dart
   Container(
     margin: const EdgeInsets.all(16),
     padding: const EdgeInsets.all(16),
     decoration: BoxDecoration(
       color: const Color(0xFFFEF2F2),
       border: Border.all(color: const Color(0xFFEF4444)),
       borderRadius: BorderRadius.circular(8),
     ),
     child: Row(
       children: [
         const Icon(Icons.info_outline, color: Color(0xFFDC2626)),
         const SizedBox(width: 12),
         Expanded(
           child: Text(
             'Reference code "${widget.initialNacCode}" was not found. Browsing the full reference catalog.',
             style: const TextStyle(color: Color(0xFF991B1B), fontSize: 14, fontWeight: FontWeight.w500),
           ),
         ),
       ],
     ),
   )
   ```
This eliminates the crawler soft-404 trap while providing a graceful user fallback.

---

## 4. Target Tree Branch Integration Contract (Resolving MF-3)

### 4.1 Ground Truth Comparison: `4d17ca5e` vs `origin/dev`
- **Target (`4d17ca5e:numista_mobile/lib/main.dart` lines 122–148):**
  Lacks `/catalog` and `path.startsWith('/catalog/')` in `isKnownPath`. Unrecognized paths fall through to line 142:
  ```dart
  if (!isKnownPath) {
    runApp(MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      home: NotFoundScreen(attemptedPath: path),
    ));
    return;
  }
  ```
  Any visitor navigating to `https://numista.ai/catalog` sees `NotFoundScreen` — an immediate client-side 404!
- **Source (`origin/dev:numista_mobile/lib/main.dart` lines 135–175):**
  Includes `/catalog` and `/catalog/` in `isKnownPath`, and dispatches directly to `CatalogBrowseScreen`.

### 4.2 Exact Integration Manifest
To integrate public catalog routing into `origin/p7-v8.9` without regressions or unauthorized modifications:

1. **Import in `numista_mobile/lib/main.dart` line 12:**
   ```dart
   import 'screens/catalog/catalog_browse_screen.dart';
   ```

2. **Asset Registration in `numista_mobile/pubspec.yaml` lines 92–98:**
   Verbatim target `4d17ca5e:numista_mobile/pubspec.yaml`:
   ```yaml
     assets:
       - assets/
       - assets/data/
       - assets/fonts/
       - assets/mint_mark_diagrams/
   ```
   Add the catalog asset declaration matching `origin/dev:numista_mobile/pubspec.yaml` line 97:
   ```yaml
     assets:
       - assets/
       - assets/data/
       - assets/fonts/
       - assets/mint_mark_diagrams/
       - assets/catalog/
   ```

3. **Whitelist in `numista_mobile/lib/main.dart`:**
   ```dart
     final isKnownPath = path.isEmpty ||
         path == '/' ||
         path == '/index.html' ||
         normalizedPath == '/about' ||
         normalizedPath == '/pricing' ||
         normalizedPath == '/features' ||
         normalizedPath == '/faq' ||
         normalizedPath == '/login' ||
         normalizedPath == '/signup' ||
         normalizedPath == '/reset-password' ||
         normalizedPath == '/demo' ||
         normalizedPath == '/app' ||
         normalizedPath == '/blog' ||
         normalizedPath == '/catalog' ||        // INTEGRATED FROM DEV
         path.startsWith('/catalog/') ||        // INTEGRATED FROM DEV
         path.startsWith('/wishlist') ||
         path.startsWith('/attorney_portal') ||
         path.startsWith('/attorney') ||
         path.startsWith('/claim') ||
         path.startsWith('/privacy') ||
         path.startsWith('/terms') ||
         path.startsWith('/add_coins') ||
         path.startsWith('/scraper_dashboard') ||
         path.startsWith('/api/');
   ```

4. **Direct Entry Dispatch in `numista_mobile/lib/main.dart`:**
   ```dart
     // Public Catalog direct entry (zero auth required)
     if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
       String? initialNacCode;
       if (path.startsWith('/catalog/')) {
         final sub = path.substring('/catalog/'.length).trim();
         if (sub.isNotEmpty) {
           initialNacCode = Uri.decodeComponent(sub);
         }
       }
       if (initialNacCode == null && uri.queryParameters.containsKey('item')) {
         initialNacCode = uri.queryParameters['item'];
       }
       runApp(MaterialApp(
         title: 'Numista.AI Public Catalog',
         debugShowCheckedModeBanner: false,
         theme: ThemeData(
           brightness: Brightness.light,
           scaffoldBackgroundColor: Colors.white,
           primaryColor: const Color(0xFF0B2545),
           colorScheme: ColorScheme.fromSeed(
             seedColor: const Color(0xFF1F5FAD),
             primary: const Color(0xFF0B2545),
           ),
         ),
         home: CatalogBrowseScreen(initialNacCode: initialNacCode),
       ));
       return;
     }
   ```
   *Rationale for Theme Preservation:* Pinned `origin/dev` uses `Brightness.light` with `scaffoldBackgroundColor: Colors.white` and `primaryColor: const Color(0xFF0B2545)`. Retaining dev's theme avoids visual dissonance with `catalog_browse_screen.dart` card styling (`color: Colors.white`, border `Color(0xFFD6D6D6)`).
   *Query Parameter Compatibility:* Preserves `?item=` query parameter fallback for external marketing campaign links.

5. **True 404 Preservation:**
   All routes not recognized in `isKnownPath` continue to evaluate `!isKnownPath` and render `NotFoundScreen(attemptedPath: path)` with a clean, branded 404 UI.

---

## 5. Master Data Sourcing, Eligibility, and Strict Privacy Protection (Resolving MF-4)

### 5.1 Repository Master Census
Ground truth census verification of the master catalog file:
- **Location:** `assets/catalog/catalog_master_3202.jsonl` (and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl`).
- **Census:** Exactly **3,202 nonblank records**, **3,202 unique NAC codes**.
- **Breakdown:**
  * US Federal & Pre-Federal Coins: **2,965**
  * US Paper Currency & Fractional Notes: **181**
  * Official US Mint Medals: **56**
  * Foreign Coins: **0** (foreign coins strictly purged).
- **Cryptographic Checksum:** SHA256: `FBA6C66A107E5304D801997C01F22681E072FA7E8F8AA8761D5A2738ADE31BEF`.

### 5.2 Content Verification & Status Classification
Audit of the master records reveals:
- All 3,202 records carry `proposal_status: "PROPOSAL"`.
- All 3,202 records carry `needs_fact_check: true` (derived from numismatic collection indexes, awaiting final US Mint archival verification).
- Substatus breakdown:
  * `PLACEHOLDER`: 951
  * `PREVIEW_DRAFT`: 2,231
  * `PUBLISHED_ON_X`: 13
  * `DRAFT_POST`: 7

### 5.3 Copy Neutralization & Marketing Reconciliation
1. **Ban Blanket "Verified" Claims:** Prohibit copy claiming "100% verified by US Mint", "certified authentic specifications", or "guaranteed grade accuracy". Replace with neutral reference copy: `"Numista Reference Catalog Entry"`.
2. **Stat Badges in `numista_mobile/lib/screens/login_screen.dart` lines 338 and 466:**
   Verbatim current target `4d17ca5e`:
   ```dart
   338: _StatBadge(value: '5,142', label: 'Reference\nCoins'),
   ...
   466: _StatBadge(value: '5,142', label: 'Reference\nCoins'),
   ```
   Reconcile to:
   ```dart
   338: _StatBadge(value: '3,202', label: 'Reference\nCoins & Notes'),
   ...
   466: _StatBadge(value: '3,202', label: 'Reference\nCoins & Notes'),
   ```
3. **Purge Unsourced Marketing Claims:**
   - Remove `"99.4% accuracy"` claim.
   - Remove `"5,000+ indexable pages"` claim.
   - Remove unsourced mentions of an `"advisory board"`, `"Sheldon grading standard guarantee"`, `"100% Private & Secure"`, or `"Passport Protocol"`.

### 5.4 Strict Privacy Prohibitions (Zero AJ PII / Private Collection Exposure)
Under no circumstances may private user data or collection information appear in public assets:
- **Prohibited Identifiers:** Zero AJ user IDs, account emails, personal names, estate names, or attorney claim IDs.
- **Prohibited Valuation Data:** Zero user purchase prices, user acquisition costs, realized dealer invoices, or total collection valuations.
- **Prohibited User Media:** Zero raw user-submitted grading photos, slab scans, or collection staging photos.
- **Prohibited Notes & Metadata:** Zero private collector notes, provenance records, safe deposit box numbers, or grading submission tracking numbers.
- **Enforcement:** Automated offline test `CensusAndPrivacyHarness` asserts zero occurrences of private collection keys (`purchase_price`, `cost_basis`, `collector_notes`, `user_id`, `collection_id`) in public JSON assets.

---

## 6. Real Retail Join and Complete Image/Data Projection (Resolving MF-5)

### 6.1 Authorized Retail Join Specification
The public catalog requires authoritative, reference-grade retail pricing:
- **Authorized Dataset:** **CPG® Retail Price Guide Reference Feed (CDN Publishing)**.
- **License / Attribution:** Used under CDN Publishing CPG® data reference agreement for public numismatic educational lookup.
- **Feed Version:** `CPG_RETAIL_FEED_v2026.11`.
- **Join Key Precedence:**
  1. Exact `nac_code` match.
  2. Fallback compound key: `normalized_year` + `mint_mark` + `variety_code` + `canonical_grade`.
- **Display Currency:** United States Dollars (`USD`, `$`).
- **Required Metadata:** Every pricing projection must include:
  * `retail_estimate`: numeric retail value (e.g., `45.00`).
  * `retail_currency`: `"USD"`.
  * `as_of_date`: ISO 8601 date (e.g., `"2026-11-01"`).
  * `source_attribution`: `"CPG® Retail Price Guide (CDN Publishing)"`.

### 6.2 Missing & Invalid Join Policy ('Valuation Pending')
- If a coin record lacks a matched retail price in the CPG feed, or if the joined value is `null`, `0`, or negative:
  * The pricing field in the public model resolves strictly to `cpgRetail: null`.
  * The UI renders a styled gold status chip: `'Valuation Pending'` (or `'Retail Estimate Unavailable'`).
  * **Invariant:** Positive retail prices (`cpgRetail > 0`) are **never** displaced or overwritten by `'Valuation Pending'`.
  * **Strict Exclusion:** Wholesale pricing (Greysheet dealer bid/ask) and collector acquisition costs are strictly forbidden from public views.

### 6.3 Card and Modal Retail Renderers
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`:
1. **On `_CatalogCard` (lines 1069–1153):**
   Add the retail valuation display above the item denomination:
   ```dart
   Widget _buildRetailPrice(Map<String, dynamic> item) {
     final cpgRetail = item['cpg_retail'] as num?;
     if (cpgRetail != null && cpgRetail > 0) {
       return Text(
         '\$${cpgRetail.toStringAsFixed(2)} Retail Est.',
         style: const TextStyle(
           fontSize: 14,
           fontWeight: FontWeight.bold,
           color: Color(0xFF059669),
         ),
       );
     }
     return Container(
       padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
       decoration: BoxDecoration(
         color: const Color(0xFFFEF3C7),
         borderRadius: BorderRadius.circular(4),
         border: Border.all(color: const Color(0xFFF59E0B)),
       ),
       child: const Text(
         'Valuation Pending',
         style: TextStyle(
           fontSize: 11,
           fontWeight: FontWeight.bold,
           color: Color(0xFFB45309),
         ),
       ),
     );
   }
   ```

### 6.4 Image Sourcing, Guarded Fetch, and Outbound Link Stripping
1. **Image Host Audit:**
   The master catalog contains 248 primary maps (167 URL-style, 81 file-style) and 966 type maps. External hosts include `upload.wikimedia.org`, `thumb.wikimedia.org`, `images.metmuseum.org`, and `numismatics.org`.
2. **First-Party Bucket Invariant:**
   In web production, direct unvalidated `Image.network` calls to random third-party hosts cause CORS failures, CSP blocking, and broken UI tiles.
   All production images must be served from:
   - First-party Cloud Storage: `https://storage.googleapis.com/numista-vault.firebasestorage.app/reference_catalog/**`
   - Or local bundled assets: `assets/catalog/images/**`
3. **URL Guard Function:**
   ```dart
   bool isApprovedCatalogImageUrl(String url) {
     final uri = Uri.tryParse(url);
     if (uri == null) return false;
     if (!uri.isScheme('https')) return false;
     return uri.host == 'storage.googleapis.com' &&
            uri.path.startsWith('/numista-vault.firebasestorage.app/reference_catalog/');
   }
   ```
   If `!isApprovedCatalogImageUrl(url)`, the widget falls back cleanly to `_buildPlaceholder()`, avoiding unverified external network egress.
4. **AI Replica Image Policy:**
   AI-generated replicas are strictly forbidden from primary image slots, type image slots, catalog cards, and search index thumbnails. They may only appear in an explicitly labeled section titled `"AI Reconstructed Specimen"` inside the coin detail modal.
5. **Outbound Link Stripping in Mintage Row (lines 987–1017):**
   Verbatim current code:
   ```dart
   if (sourceUrl != null && sourceUrl.isNotEmpty) ...[
     const SizedBox(width: 8),
     InkWell(
       onTap: () async {
         final uri = Uri.tryParse(sourceUrl);
         if (uri != null) await launchUrl(uri);
       },
       child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)),
     ),
   ],
   ```
   **Replacement:** Strip the `InkWell` and `launchUrl`. Render plain text attribution only:
   ```dart
   if (sourceUrl != null && sourceUrl.isNotEmpty) ...[
     const SizedBox(width: 8),
     Text(
       '(${mintage?['label'] ?? 'Official Record'})',
       style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), fontStyle: FontStyle.italic),
     ),
   ],
   ```
   Zero outbound external links in public catalog cards and modals.

---

## 7. Operational Controls, Rollback, and Spending Protection (Resolving MF-1 & MF-6)

### 7.1 Permanent Removal of Budget Caps (Resolving MF-1)
- Strike all references to "$25 hard limit", mandatory hosting shutdowns, or programmatic billing kill switches.
- **Alert-Only Policy:**
  * Threshold: **$20.00/month Google Cloud Billing budget alert**.
  * Alert Recipient: Founder Eric (`deploy@numista.ai`) and AG CoS Desk.
  * Operational Response: Review Cloudflare cache hit rates, verify Google Cloud Storage egress metrics, and inspect Firebase Hosting analytics. **No automated site shutdowns or script-triggered outages.**

### 7.2 Non-Destructive Deployment via Preview Channel
All build verification occurs on an isolated preview channel before any live deployment:
```bash
# 1. Build release web bundle
flutter build web --release --base-href "/"

# 2. Deploy to isolated preview channel (Hosting only)
firebase hosting:channel:deploy preview-net814 --site numista-vault --expires 48h
```
Preview URL: `https://numista-vault--preview-net814-<hash>.web.app`.
No traffic is routed to `https://numista.ai` during preview testing.

### 7.3 Real Git Rollback Procedure (Resolving MF-6)
- **Pre-Execution Baseline Capture:**
  ```bash
  PRE_EXEC_SHA=$(git rev-parse HEAD)
  echo "Pre-execute baseline SHA: $PRE_EXEC_SHA"
  ```
- **Targeted Git Revert:**
  Never execute `git revert $PRE_EXEC_SHA..HEAD` indiscriminately across unrelated commits. Revert strictly the specific feature commit SHAs:
  ```bash
  git revert --no-edit <NET-814_COMMIT_SHAS>
  git pull --rebase origin p7-v8.9
  git push origin p7-v8.9
  ```

### 7.4 Real Firebase Hosting Release Restore (Resolving MF-6)
- **Pre-Deploy Version ID Capture:**
  Capture the currently active live release version ID from Firebase Hosting before initiating any live deployment:
  ```bash
  PRE_DEPLOY_VERSION_ID=$(firebase hosting:releases:list --site numista-vault --json | jq -r '.[0].version.name')
  echo "Pre-deploy version ID: $PRE_DEPLOY_VERSION_ID"
  ```
- **Live Channel Restore:**
  If an unintended issue is discovered on live Hosting, restore the exact pre-deploy release:
  ```bash
  firebase hosting:clone numista-vault@$PRE_DEPLOY_VERSION_ID numista-vault:live
  ```
- **Preview Channel Cleanup:**
  ```bash
  firebase hosting:channel:delete preview-net814 --site numista-vault --force
  ```
- **Automated Post-Rollback Smoke Probes:**
  Execute HTTP status checks against the live domain:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" https://numista.ai/               # Expect 200
  curl -s -o /dev/null -w "%{http_code}" https://numista.ai/catalog        # Expect 200
  curl -s -o /dev/null -w "%{http_code}" https://numista.ai/pricing        # Expect 200
  ```
- **Hosting Isolation:**
  Every Firebase deployment command must explicitly use `--only hosting --site numista-vault`. Firestore security rules, Cloud Storage rules, Cloud Functions, and Firestore indexes cannot ride along.

---

## 8. Pricing Content, AuthGate Precedence, and Operational Gates (Resolving MF-7)

### 8.1 Ground Truth in `public_info_screens.dart`
Verbatim target `4d17ca5e:numista_mobile/lib/screens/public_info_screens.dart` lines 360–415:
```dart
        const Text(
          'Free During Beta — Pricing TBA',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
...
                  const Text(
                    '\$0 / month',
                    style: TextStyle(
                      color: Color(0xFF0F172A),
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
...
              const Text(
                'Numista.AI is currently in open public beta. During this phase, collection tracking, AI photo identification, and market value estimates are completely free for registered participants.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
```

### 8.2 Approved Pricing Surface Copy Reconciliation
In `public_info_screens.dart`, replace outdated beta copy with approved static copy covering:
1. **Free 10-Coin Trial:**
   - Header: `"Free 10-Coin Trial"`
   - Body: `"Scan, identify, and appraise your first 10 coins completely free. Experience full AI-assisted numismatic identification, variety attribution, and reference retail valuation."`
2. **US-Only Reference Coverage:**
   - Header: `"United States Numismatic Focus"`
   - Body: `"Numista.AI currently covers United States federal coinage (1792–present), pre-federal colonials and tokens, official US Mint commemorative medals, and US paper currency."`
3. **Grandfathered Beta Access:**
   - Header: `"Active Beta Members Grandfathered"`
   - Body: `"Early beta participants maintain uninterrupted access to their existing collection inventories, custom coin records, and reference catalogs."`
4. **Stripe Strictly OFF:**
   - Stripe is strictly disabled. No credit card fields, no billing forms, no active checkout endpoints.
   - Informational notice: `"Paid subscription tiers and estate appraisal tools will launch at general availability. No credit card or payment method required during preview."`

### 8.3 AuthGate Public Route Precedence (`widgets/auth_gate.dart`)
Verbatim target `4d17ca5e:numista_mobile/lib/widgets/auth_gate.dart` lines 101–160:
```dart
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _buildSplash();
        }

        // Signed in -> show welcome screen on first launch, then main app
        if (snapshot.hasData && snapshot.data != null) {
          ...
          return const BaseLayout();
        }

        // Not signed in:
        // 1. If public route requested, show PublicInfoShell
        if (widget.publicRoute != null) {
          return PublicInfoShell(targetRoute: widget.publicRoute!);
        }
```
**Defect:** If an authenticated user navigates to `/pricing` or clicks a footer link to `/pricing`, `snapshot.hasData` evaluates to `true`, and the user is silently hijacked into `BaseLayout()` or `WelcomeScreen`. `widget.publicRoute` is never evaluated for signed-in sessions!

**Resolution:**
Move public route evaluation **ahead** of the signed-in branch:
```dart
        // Still waiting for Firebase to initialise — show branded splash
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _buildSplash();
        }

        // 1. PUBLIC ROUTE PRECEDENCE:
        // Honored for BOTH signed-in and signed-out sessions (e.g. /pricing, /about, /faq)
        if (widget.publicRoute != null) {
          return PublicInfoShell(targetRoute: widget.publicRoute!);
        }

        // 2. Signed in -> show welcome screen on first launch, then main app
        if (snapshot.hasData && snapshot.data != null) {
          final isRealUser = !snapshot.data!.isAnonymous;
          if (isRealUser && (GuestSeedService.isBrowseDemoMode || _cachedDemoActive)) {
            _cachedDemoActive = false;
            GuestSeedService.deactivateBrowseDemo();
            debugPrint('[AUTH] Demo mode cleared for real user ${snapshot.data!.uid}');
          }
          if (GuestSeedService.isBrowseDemoMode || _cachedDemoActive) {
            return const BaseLayout(isDemoMode: true);
          }
          if (_welcomeDone) {
            return const BaseLayout();
          }
          ...
```
This guarantees that authenticated users can review public pricing and informational documentation without losing their session context or being redirected into the collection dashboard.

### 8.4 Semantic HTML Anchors in `login_screen.dart`
Verbatim target `4d17ca5e:numista_mobile/lib/screens/login_screen.dart` lines 585–608:
```dart
  Widget _footerLink(String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(4),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
        child: Text(label, style: const TextStyle(color: _sub, ...)),
      ),
    );
  }

  void _openPublicRoute(String route) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => PublicInfoShell(targetRoute: route),
      ),
    );
  }
```
Replace with Flutter's semantic `Link` widget from `package:url_launcher/link.dart`:
```dart
  Widget _semanticFooterLink(String label, String route) {
    return Link(
      uri: Uri.parse(route),
      builder: (context, followLink) => InkWell(
        onTap: () {
          if (followLink != null) followLink();
          _openPublicRoute(route);
        },
        borderRadius: BorderRadius.circular(4),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
          child: Text(label, style: const TextStyle(color: _sub, fontSize: NumistaTheme.textBodySm, fontWeight: FontWeight.w500)),
        ),
      ),
    );
  }
```
This renders real `<a href="/pricing">` anchor elements in the DOM, enabling crawler indexing, right-click "Open in New Tab", and middle-click browsing.

### 8.5 Operational Gates & Thanksgiving Launch Checkpoints
- **Separate Production Gates:**
  * Firestore database writes require a separate explicit typed YES from Founder Eric.
  * Firestore security rules deployments require a separate explicit typed YES from Founder Eric.
- **Dated Launch Schedule:**
  * **7 Nov 19:35 ET:** NET-814 Plan v1.3 authored and delivered to Grok Bot CoS.
  * **8 Nov 12:00 ET:** Grok Bot CoS Review ($\ge 95$) $\rightarrow$ Stand Alone Grok Review ($\ge 95$).
  * **9 Nov 10:00 ET:** Founder Eric explicit typed YES for build execution.
  * **10–12 Nov:** Build verification on isolated preview channel `preview-net814`.
  * **13 Nov 2026:** **Catalog Live on live Hosting** with pre-deploy rollback version captured.
  * **26 Nov 2026 (Thanksgiving):** Meta Ads live campaign traffic directed to `https://numista.ai/catalog`.

---

## 9. Automated Testing Strategy (Machine-Checkable Verification)

All verification suites are specified below and marked **To be authored**:

### 9.1 `PublicCatalogRoutingHarness` (`test/screens/catalog_soft404_routing_test.dart`) — To Be Authored
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:numista_mobile/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_mobile/screens/not_found_screen.dart';

void main() {
  group('Public Catalog Routing & Soft-404 Elimination Tests', () {
    testWidgets('1. /catalog path evaluates to isKnownPath and renders CatalogBrowseScreen', (tester) async {
      const attemptedPath = '/catalog';
      final isKnown = attemptedPath == '/catalog' || attemptedPath.startsWith('/catalog/');
      expect(isKnown, isTrue);

      await tester.pumpWidget(const MaterialApp(
        home: CatalogBrowseScreen(),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(CatalogBrowseScreen), findsOneWidget);
      expect(find.byType(NotFoundScreen), findsNothing);
    });

    testWidgets('2. Deep link /catalog/US-1921-MORGAN parses initialNacCode', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: CatalogBrowseScreen(initialNacCode: 'US-1921-MORGAN'),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(CatalogBrowseScreen), findsOneWidget);
    });

    testWidgets('3. Unknown NAC code renders not-found notice banner without crashing', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: CatalogBrowseScreen(initialNacCode: 'NONEXISTENT-CODE-999'),
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('NONEXISTENT-CODE-999 was not found'), findsOneWidget);
    });
  });
}
```

### 9.2 `AuthGatePublicRouteHarness` (`test/widgets/auth_gate_public_route_test.dart`) — To Be Authored
```dart
import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:numista_mobile/widgets/auth_gate.dart';
import 'package:numista_mobile/screens/public_info_screens.dart';

class MockUser extends Fake implements User {
  @override
  bool get isAnonymous => false;
  @override
  String get uid => 'test_authenticated_user_123';
}

void main() {
  group('AuthGate Public Route Precedence Tests', () {
    testWidgets('1. Signed-out session with publicRoute: /pricing renders PublicInfoShell', (tester) async {
      final authController = StreamController<User?>();
      addTearDown(authController.close);

      await tester.pumpWidget(MaterialApp(
        home: AuthGate(
          authStream: authController.stream,
          publicRoute: '/pricing',
        ),
      ));

      authController.add(null);
      await tester.pumpAndSettle();

      expect(find.byType(PublicInfoShell), findsOneWidget);
    });

    testWidgets('2. Authenticated user with publicRoute: /pricing renders PublicInfoShell (no hijacking)', (tester) async {
      final authController = StreamController<User?>();
      addTearDown(authController.close);

      await tester.pumpWidget(MaterialApp(
        home: AuthGate(
          authStream: authController.stream,
          publicRoute: '/pricing',
        ),
      ));

      authController.add(MockUser());
      await tester.pumpAndSettle();

      // Invariant: Must NOT hijack to BaseLayout or WelcomeScreen
      expect(find.byType(PublicInfoShell), findsOneWidget);
    });
  });
}
```

### 9.3 `CensusAndPrivacyHarness` (`test/services/catalog_census_privacy_test.dart`) — To Be Authored
```dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Catalog Census & Privacy Invariant Tests', () {
    test('1. Master catalog contains exactly 3,202 records and unique NACs', () async {
      final file = File('assets/catalog/catalog_master_3202.jsonl');
      expect(file.existsSync(), isTrue, reason: 'Master catalog file must exist');

      final lines = await file.readAsLines();
      final nonBlankLines = lines.where((l) => l.trim().isNotEmpty).toList();
      expect(nonBlankLines.length, equals(3202));

      final nacSet = <String>{};
      for (final line in nonBlankLines) {
        final doc = jsonDecode(line) as Map<String, dynamic>;
        final nac = doc['nac_code'] as String?;
        expect(nac, isNotNull);
        expect(nacSet.contains(nac), isFalse, reason: 'Duplicate NAC: $nac');
        nacSet.add(nac!);
      }
      expect(nacSet.length, equals(3202));
    });

    test('2. Zero AJ PII or private collection keys in public assets', () async {
      final file = File('assets/catalog/catalog_master_3202.jsonl');
      final lines = await file.readAsLines();

      const forbiddenKeys = [
        'purchase_price',
        'cost_basis',
        'collector_notes',
        'user_id',
        'collection_id',
        'attorney_claim_id',
      ];

      for (final line in lines) {
        if (line.trim().isEmpty) continue;
        final doc = jsonDecode(line) as Map<String, dynamic>;
        for (final k in forbiddenKeys) {
          expect(doc.containsKey(k), isFalse, reason: 'Forbidden private key found: $k');
        }
      }
    });

    test('3. Marketing copy in login_screen.dart contains no 5,142 references', () async {
      final loginFile = File('lib/screens/login_screen.dart');
      final text = await loginFile.readAsString();
      expect(text.contains('5,142'), isFalse, reason: 'Outdated 5,142 badge must be purged');
    });
  });
}
```

### 9.4 `StaticRouteHtmlHarness` (`test/web/static_route_html_test.py`) — To Be Authored
A Python verification script to inspect pre-rendered static artifacts:
```python
import os
import re

def test_static_html_artifacts():
    catalog_html = "build/web/catalog/index.html"
    pricing_html = "build/web/pricing/index.html"
    
    assert os.path.exists(catalog_html), f"{catalog_html} must exist"
    assert os.path.exists(pricing_html), f"{pricing_html} must exist"
    
    with open(catalog_html, "r", encoding="utf-8") as f:
        c_body = f.read()
    with open(pricing_html, "r", encoding="utf-8") as f:
        p_body = f.read()
        
    # Verify base href
    assert '<base href="/">' in c_body, "Catalog HTML must include <base href='/'>"
    assert '<base href="/">' in p_body, "Pricing HTML must include <base href='/'>"
    
    # Verify canonical URLs
    assert '<link rel="canonical" href="https://numista.ai/catalog"' in c_body
    assert '<link rel="canonical" href="https://numista.ai/pricing"' in p_body
    
    # Verify same-party OG image
    assert 'content="https://numista.ai/icons/Icon-512.png"' in c_body
    assert 'content="https://numista.ai/icons/Icon-512.png"' in p_body

if __name__ == "__main__":
    test_static_html_artifacts()
    print("Static HTML artifact tests PASSED.")
```

---

## 10. Multi-Agent Review Chain & Operational Submission

In accordance with Founder Eric's binding review sequence (Argon dropped entirely per typed YES 5 Nov 18:07 ET):

```mermaid
flowchart TD
    AGCOS["Antigravity Chief of Staff v5<br/>(Author: cfe23a7a)"] -->|File Plan v1.3 & Baton| GBCOS["Grok Bot Chief of Staff<br/>(Reviewer 1, Target: >= 95)"]
    GBCOS -->|Review PASS >= 95| SAG["Stand Alone Grok<br/>(Reviewer 2, Target: >= 95)"]
    SAG -->|Review PASS >= 95| ERIC["Founder Eric<br/>(Explicit Typed YES)"]
    ERIC -->|Preview Deploy Approved| PREVIEW["Preview Channel Deployment<br/>(preview-net814)"]
    PREVIEW -->|Smoke Probes Verified| LIVE["Live Hosting Release<br/>(~13 Nov 2026 Target)"]
```

1. **Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
2. **Reviewer 1:** Grok Bot Chief of Staff (Target: $\ge 95 / 100$).
3. **Reviewer 2:** Stand Alone Grok (SAG grok-4.7, Target: $\ge 95 / 100$).
4. **Founder Gate:** Founder Eric explicit typed YES prior to any build execution or deployment.
5. **Locks Remaining Strictly Enforced:** `origin/main` locked at `9f04550a`; Stripe strictly OFF; alerts only ($20/mo threshold); strict PLAN ONLY mode.
