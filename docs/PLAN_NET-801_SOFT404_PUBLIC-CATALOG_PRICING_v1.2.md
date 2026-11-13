# Architecture & Implementation Plan: NET-801 v1.2 (BATON_NET-814)
## Soft-404 Elimination, Public Catalog Architecture Decision (Options A/B/C), and Pricing Navigation Fix

- **Track ID:** NET-801 v1.2 / BATON_NET-814 (Thanksgiving Critical Path Launch Priority for Meta Ads 26 Nov 2026)
- **Author:** Antigravity Chief of Staff (AG CoS v4 / Catalog Night Team `ba2bfdb2`)
- **Review Cycle:** Grok Bot CoS (>=95) -> SAG Review (grok-4.7 >=95) -> Founder Eric Explicit Typed Choice (Option A, B, or C) & Typed YES
- **Target Branch:** `origin/p7-v8.9` (Integrating catalog architecture from `origin/dev` @ `b0b05808`)
- **Status:** **PLAN ONLY** — Zero code modifications, zero deployments, zero Firestore writes/seeding. `origin/main` locked at `9f04550a`; Stripe strictly OFF. Cycle has NO Argon (Argon dropped per Eric typed YES 5 Nov 18:07 ET).
- **Date:** 6 November 2026, 10:30 PM ET
- **Reference Batons & Reviews:**
  - `BATON_NET-814_REVISE_SOFT404-PUBLIC-CATALOG-PRICING_v1.2_PER-COS-76-SAG-64_2026-11-05-1705.md`
  - `COS_SCORE_NET-807_SOFT404-PUBLIC-CATALOG-PRICING-v1.1_20261105.md` (CoS 76 FAIL on v1.1)
  - `SAG_SCORE_NET-807_20261105.md` (SAG 64 FAIL on v1.1)
  - `RADIO_NET-818_TASKMASTER_20261106-1845.md` (Thanksgiving Critical Path: Catalog Live 13 Nov, Meta Ads 26 Nov)

---

## 1. Executive Summary & Ground-Truth Alignment (Resolving CoS-76 & SAG-64 Must-Fixes)

This revised v1.2 plan resolves all blocking defects from previous reviews, rebasing strictly on verified repository ground truth:

1. **Target Tree Branch Alignment & Soft-404 Resolution (CoS #1, SAG #3):**
   - In production today, live `/catalog` returns HTTP 200 via Firebase SPA rewrite to `index.html`.
   - However, on the target branch `p7-v8.9` (`main.dart` lines 119–140), `/catalog` and `/catalog/:nacCode` are **absent from `isKnownPath`**, causing the Flutter client to render `NotFoundScreen` (lines 142–148) — a client-side soft-404. Furthermore, `numista_mobile/firebase.json` on `p7-v8.9` lacks `/catalog` rewrite rules.
   - On `origin/dev` (@ `b0b05808`), `CatalogBrowseScreen` (`lib/screens/catalog/catalog_browse_screen.dart`), `main.dart` `/catalog` handling, and `firebase.json` rewrites already exist.
   - We specify the exact, non-destructive integration from `origin/dev` (`b0b05808`) to `p7-v8.9`, eliminating the in-app soft-404 without creating duplicate screens.
2. **Correct Master Data Sourcing (CoS #4, SAG #2):**
   - Strike the non-existent path `numista_backend/entries_master_20261103.jsonl`.
   - The verified repository master input is located strictly at `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` containing exactly **3,202 verified master reference entries** (2,965 coins + 181 notes + 56 medals).
   - Reconcile marketing badge copy (`login_screen.dart:338, 466`) from `"5,142"` to `"3,202 Verified US Reference Coins & Currency"` (or `"~3,200 Reference Coins & Currency"`). Remove unsourced statistics (`99.4%`, "5,000+ indexable pages", "advisory board", "Sheldon grading", "Passport Protocol").
3. **Options A, B, and C for Founder Eric's Explicit Typed Choice:**
   - Present three distinct architectural paths (A: Full Public `/catalog`, B: Homepage Search Popup Modal, C: Keep Gated Behind Authentication).
   - **Founder Eric must explicitly type his choice ("Option A", "Option B", or "Option C") along with his typed YES before any build execution or deployment occurs.**
4. **Per-Route Static HTML & OpenGraph (OG) Meta Tags (CoS #2, SAG #6):**
   - A single SPA `web/index.html` cannot provide route-specific OpenGraph meta tags for `/`, `/catalog`, and `/pricing`.
   - We specify generated static entry points (`web/catalog/index.html` and `web/pricing/index.html`) pre-rendered with route-specific `<title>`, `<meta property="og:title">`, `<meta property="og:description">`, and `<link rel="canonical">`.
   - Use strictly verified same-party OG image asset `https://numista.ai/icons/Icon-512.png` with local fallback. Strike unprovisioned GCS bucket hotlinks.
5. **AuthGate Signed-In Bypass Fix (CoS #3, SAG #7):**
   - In `numista_mobile/lib/widgets/auth_gate.dart`, signed-out sessions already wait on `authStateChanges()` and honor `publicRoute` (lines 157–159). However, signed-in sessions enter lines 106–148 and return `BaseLayout()` or `WelcomeScreen`, completely bypassing and ignoring `widget.publicRoute`.
   - We move `if (widget.publicRoute != null) return PublicInfoShell(targetRoute: widget.publicRoute!);` ahead of the signed-in branch (after connection state waiting), ensuring both signed-in and signed-out sessions navigating to `/pricing` render `PublicInfoShell` cleanly.
6. **Public Sourced Migration & Image Hygiene (CoS #4, SAG #5):**
   - Existing `catalog_public_v1.json` lacks `cpgRetail` and `ai_replica` keys.
   - Define a fail-closed sourced join/migration: missing retail values stay pending (styled gold `'Valuation Pending'` chip); positive `cpgRetail` is never displaced. Zero wholesale pricing.
   - AI replicas: allowed strictly inside labeled `ai_replica_images`, never primary, card, or index image.
   - Prerequisite to Option A: Foreign Coins and source links must be removed from `origin/dev` catalog data.
7. **Real Ancestor Rollback & Egress Spending Controls (CoS #1, SAG #1, SAG #4):**
   - Strike forbidden `9f04550a` non-ancestor revert point.
   - Dynamic pre-execute SHA capture on `origin/p7-v8.9` (`PRE_EXEC_SHA=$(git rev-parse HEAD)`). Revert command: `git revert --no-edit $PRE_EXEC_SHA..HEAD`.
   - Named Firebase Hosting preview channel delete / release restore.
   - Strike claims of nonexistent `stop-public-egress` Cloud Function. Implement cost control via Google Cloud Billing Pub/Sub budget alerts ($20 alert / $25 hard limit) paired with human Hosting channel deletion / site disable procedures.

---

## 2. Catalog Census & Ground-Truth Reconciliation (S404-3)

### 2.1 The 5,142 vs 3,202 Discrepancy
- **Legacy Marketing Badges:** In `numista_mobile/lib/screens/login_screen.dart` lines 338 and 466:
  ```dart
  338: _StatBadge(value: '5,142', label: 'Reference\nCoins'),
  ...
  466: _StatBadge(value: '5,142', label: 'Reference\nCoins'),
  ```
- **Verified Repository Master:** Ground truth input is located strictly at:
  `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl`
  Census: Exactly **3,202 verified master reference entries**:
  - Federal & Pre-Federal Coins: 2,965
  - Paper Currency & Notes: 181
  - Official US Mint Medals: 56
  - Total: 3,202 entries.

### 2.2 Verbatim Copy Reconciliation Actions
1. **Update Stat Badges:** In `login_screen.dart:338, 466`, replace `'5,142'` with `'3,202'` and label with `'Verified\nEntries'` (or `'Reference\nCoins & Notes'`).
2. **Remove "World" Claims:** The master catalog is strictly US-focused (federal coinage, pre-federal colonials/tokens, and official US Mint medals and currency). Foreign coins and world references are completely removed from public catalog copy and filters.
3. **Delete Unsourced Statistics:**
   - Delete unsourced `99.4%` accuracy claim.
   - Delete claims of "5,000+ indexable pages".
   - Delete unsourced marketing claims: "advisory board", "Sheldon grading standard guarantee", "100% Private & Secure", and "Passport Protocol".

---

## 3. Options A, B, and C for Founder Eric's Explicit Typed Choice

Founder Eric must decide the public accessibility architecture for the reference catalog ahead of the 26 November Meta ad launch:

| Option | Architectural Description | Pros | Cons / Constraints | Launch Readiness |
|---|---|---|---|---|
| **Option A (Recommended)** | **Full Public `/catalog` Browse Screen:** Anyone can browse the verified 3,202 reference catalog at `/catalog` and `/catalog/:nacCode` without signing in. Clicking "Add to My Collection" prompts login/signup modal. | • Directly fulfills homepage promise.<br/>• Gives Meta ads a dedicated, high-converting landing page.<br/>• Fully leverages already-built `CatalogBrowseScreen` on `origin/dev`. | • Requires count reconciliation (3,202).<br/>• Requires strict CDN CPG retail-only pricing.<br/>• Requires per-route static OG tags for Meta crawler.<br/>• Requires Foreign Coins removal. | High (Critical path for 26 Nov Thanksgiving ad). |
| **Option B** | **Homepage Search Popup Modal:** An `"Explore ~3,200 Reference Coins"` button on the homepage opens an in-modal search dialog without creating a standalone public URL. | • Fast to integrate.<br/>• Keeps visitors on homepage.<br/>• Avoids deep-linking complexity. | • Zero SEO value.<br/>• No deep-linked catalog landing pages for Meta ads.<br/>• Weak ad conversion. | Medium. |
| **Option C** | **Keep Gated Behind Sign-In; Update Copy:** Catalog remains strictly gated behind authentication. Homepage copy is updated to `"~3,200 Reference Coins & Currency (Members Only)"`. | • Smallest architectural footprint.<br/>• Zero public surface data exposure. | • Fails to provide an ad landing experience.<br/>• Leaves visitors unable to preview database coverage.<br/>• Weakest for Thanksgiving launch. | Low (Not recommended). |

> **MANDATORY GATE:** AG CoS recommends **Option A**. However, **Founder Eric must explicitly type his choice ("Option A", "Option B", or "Option C") along with his typed YES** before any code modifications, merges, or deployments occur.

---

## 4. Public Surface Data Hygiene & Privacy Protections (Option A)

If Option A is selected by Founder Eric:
1. **Valuation Source:** Valuation figures displayed on public catalog cards are sourced strictly and exclusively from **CDN CPG retail** (`cpgRetail`).
   - Zero wholesale prices (no dealer ask/bid, no Greysheet wholesale).
   - Zero user cost basis, purchase prices, or collection valuations displayed.
   - Missing or zero pricing renders a styled gold `'Valuation Pending'` chip. Positive `cpgRetail > 0` is **never** displaced by `'Valuation Pending'`.
2. **Sourced Migration from `catalog_public_v1.json`:**
   - Existing public catalog JSON lacks `cpgRetail` and `ai_replica` keys.
   - Perform a fail-closed sourced join/migration from verified pricing master into public catalog assets.
   - Records with no matched retail figure default cleanly to `cpgRetail: null` (rendering `'Valuation Pending'`). Zero fabricated prices.
3. **Image Sourcing & CSP Compliance:**
   - Sourced from first-party assets with valid CSP allowlist (`storage.googleapis.com` own-origin buckets).
   - AI replica images: allowed strictly inside labeled `ai_replica_images`, never primary, card, or index image.
   - Missing images render clean local SVG placeholders with zero external hotlinks and zero CanvasKit CSP violations.
4. **Outbound Links:** Zero outbound links to external coin pricing or cert verification sites (PCGS, NGC, eBay). In-app plain text citations only.
5. **Foreign Coins Prerequisite:** All foreign coin stubs and third-party scraping source links must be removed from `origin/dev` catalog data prior to Option A release.

---

## 5. Target Tree Branch Integration (`origin/dev` @ `b0b05808` $\rightarrow$ `p7-v8.9`)

To eliminate the soft-404 on `p7-v8.9`, the following assets must be cleanly integrated from `origin/dev` (@ `b0b05808`):

### 5.1 Route Whitelist in `main.dart`
In `numista_mobile/lib/main.dart` lines 119–140:
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
      normalizedPath == '/catalog' ||        // INTEGRATED FROM DEV b0b05808
      path.startsWith('/catalog/') ||        // INTEGRATED FROM DEV b0b05808
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

### 5.2 Direct Entry Dispatch in `main.dart`
In `numista_mobile/lib/main.dart`:
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
    runApp(MaterialApp(
      title: 'Numista.AI Public Catalog',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFD4AF37),
          surface: Color(0xFF1E293B),
        ),
      ),
      home: CatalogBrowseScreen(initialNacCode: initialNacCode),
    ));
    return;
  }
```

### 5.3 Firebase Hosting Rewrites in `numista_mobile/firebase.json`
Add catalog rewrite rules matching `origin/dev`:
```json
        {
          "source": "/catalog",
          "destination": "/index.html"
        },
        {
          "source": "/catalog/**",
          "destination": "/index.html"
        }
```

---

## 6. Static OpenGraph (OG) Meta Tags & Pre-Rendered Route HTML (S404-2)

Meta's advertising preview scraper (`facebookexternalhit`) and Googlebot initial crawl do not execute Flutter's CanvasKit WebAssembly/JS engine. A single SPA `web/index.html` cannot provide distinct metadata across `/`, `/catalog`, and `/pricing`.

### 6.1 Per-Route Static HTML Entry Points
Generate static entry files deployed alongside SPA assets:
1. **Catalog Entry (`web/catalog/index.html`):**
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <title>Numista.AI — Verified US Coin & Currency Catalog</title>
     <meta name="description" content="Explore verified reference specifications, mintage figures, and CDN CPG retail values across 3,202 US coins, notes, and medals." />
     <meta property="og:title" content="Numista.AI — Verified US Coin & Currency Reference Catalog" />
     <meta property="og:description" content="Explore verified reference specifications, mintage figures, and CDN CPG retail values across 3,202 US coins, notes, and medals." />
     <meta property="og:image" content="https://numista.ai/icons/Icon-512.png" />
     <meta property="og:url" content="https://numista.ai/catalog" />
     <meta property="og:type" content="website" />
     <link rel="canonical" href="https://numista.ai/catalog" />
     <!-- Flutter web bootstrap script follows -->
   </head>
   ```
2. **Pricing Entry (`web/pricing/index.html`):**
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <title>Numista.AI — Collector & Professional Membership Pricing</title>
     <meta name="description" content="Transparent, flat-rate pricing for numismatic collectors, estate planners, and legal professionals. Zero hidden fees." />
     <meta property="og:title" content="Numista.AI — Pricing Plans" />
     <meta property="og:description" content="Transparent, flat-rate pricing for numismatic collectors, estate planners, and legal professionals." />
     <meta property="og:image" content="https://numista.ai/icons/Icon-512.png" />
     <meta property="og:url" content="https://numista.ai/pricing" />
     <meta property="og:type" content="website" />
     <link rel="canonical" href="https://numista.ai/pricing" />
     <!-- Flutter web bootstrap script follows -->
   </head>
   ```
3. **OG Image Sourcing:** Sourced strictly from verified same-party origin (`https://numista.ai/icons/Icon-512.png`). Zero unverified GCS bucket hotlinks.

---

## 7. Pricing Button Navigation & AuthGate Fix

### 7.1 AuthGate Fix (`numista_mobile/lib/widgets/auth_gate.dart`)
In `auth_gate.dart`, move public route evaluation **ahead** of the signed-in `hasData` check:

```dart
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: widget.authStream ?? FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // Still waiting for Firebase to initialise — show branded splash
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _buildSplash();
        }

        // 1. PUBLIC ROUTE PRECEDENCE:
        // Honored for BOTH signed-in and signed-out sessions (e.g. /pricing, /about)
        if (widget.publicRoute != null) {
          return PublicInfoShell(targetRoute: widget.publicRoute!);
        }

        // 2. Signed in -> show welcome screen on first launch, then main app
        if (snapshot.hasData && snapshot.data != null) {
          final isRealUser = !snapshot.data!.isAnonymous;
          ...
```
- **Result:** Authenticated users who click `/pricing` or open `https://numista.ai/pricing` see `PublicInfoShell(targetRoute: '/pricing')` instead of being silently hijacked into `BaseLayout()` or `WelcomeScreen`.

### 7.2 Semantic HTML Anchors
In `login_screen.dart`, replace raw `InkWell` + `Navigator.push` on public links (Pricing, About, FAQ, Features) with Flutter's semantic `Link` widget:
```dart
Link(
  uri: Uri.parse('/pricing'),
  builder: (context, followLink) => TextButton(
    onPressed: followLink,
    child: const Text('Pricing'),
  ),
)
```
- Emits real `<a href="/pricing">` DOM nodes, enabling right-click "Open in new tab", middle-click, and crawler indexability.

---

## 8. Standing Controls, Rollback, Preview Channel & Spend Cap

### 8.1 Non-Destructive Deployment & Preview Channel
- Mandatory deployment to an isolated Firebase Hosting preview channel:
  ```bash
  firebase hosting:channel:deploy preview-net801
  ```
- Full browser verification of `/`, `/catalog`, `/pricing`, and `/catalog/:nacCode` before any merge to `dev`.

### 8.2 Real Ancestor Git Rollback Procedure (Resolving CoS #1, SAG #1)
- **Forbidden:** `git revert HEAD...9f04550a` is permanently struck and banned.
- **Pre-Execute Anchor Capture:**
  ```bash
  PRE_EXEC_SHA=$(git rev-parse HEAD)
  echo "Pre-execute baseline SHA: $PRE_EXEC_SHA"
  ```
- **Clean Git Revert:**
  ```bash
  git revert --no-edit $PRE_EXEC_SHA..HEAD
  git push origin p7-v8.9
  ```
- **Firebase Hosting Release Restore:**
  ```bash
  # Delete preview channel
  firebase hosting:channel:delete preview-net801 --force
  # Or restore live channel if deployed by mistake:
  firebase hosting:clone <site-id>:live <site-id>:rollback-temp
  ```

### 8.3 Real Dollar Spend Cap & Egress Monitoring (Resolving CoS #1, SAG #4)
- Strike claims of nonexistent `stop-public-egress` Cloud Function.
- Programmatic cost protection:
  - Google Cloud Billing budget Pub/Sub alert at **$20.00/month**.
  - Strict human Hosting kill switch procedure: If monthly budget threshold ($25.00/month) is reached, immediately delete preview channels (`firebase hosting:channel:delete preview-net801 --force`) or disable site hosting in Firebase Console.

---

## 9. Automated Testing Strategy (Machine-Checkable Verification)

Authored in `numista_mobile/test/screens/catalog_soft404_routing_test.dart` and `numista_mobile/test/widgets/auth_gate_public_route_test.dart`:

1. **Routing & Known Path Test:**
   - Assert `normalizedPath == '/catalog'` and `path.startsWith('/catalog/')` evaluate to `isKnownPath == true`.
   - Assert that navigating to `/catalog` does NOT render `NotFoundScreen`.
2. **AuthGate Public Route Test:**
   - Signed-out session: Assert `AuthGate(publicRoute: '/pricing')` renders `PublicInfoShell`.
   - Signed-in session (`User` present in stream): Assert `AuthGate(publicRoute: '/pricing')` renders `PublicInfoShell` and does NOT hijack to `BaseLayout`.
3. **Static OG HTML Raw Body Test:**
   - Fetch or inspect `web/catalog/index.html` and `web/pricing/index.html`.
   - Assert `<title>` contains `"Numista.AI"`.
   - Assert `<link rel="canonical">` has distinct route URLs (`/catalog`, `/pricing`).
   - Assert `<meta property="og:image">` points strictly to same-party `https://numista.ai/icons/Icon-512.png`.
4. **Marketing Census Consistency Test:**
   - Assert `login_screen.dart` contains no instance of `'5,142'`.
   - Assert stat badges render `'3,202'`.

---

## 10. Multi-Agent Review Chain & Approvals

In compliance with Founder Eric's binding review sequence (Argon dropped entirely per typed YES 5 Nov 18:07 ET):
1. **Author:** Antigravity CoS v4 / Catalog Night Team (`ba2bfdb2`)
2. **Reviewer 1:** Grok Bot Chief of Staff (Target: `>= 95 / 100`)
3. **Reviewer 2:** Stand Alone Grok (SAG grok-4.7, Target: `>= 95 / 100`)
4. **Founder Gate:** Founder Eric explicitly types his choice (**"Option A"**, **"Option B"**, or **"Option C"**) and types **YES** prior to any build execution or deployment.

**Locks Remaining Enforced:** `origin/main` locked at `9f04550a`; Stripe strictly OFF; strict PLAN ONLY mode.
