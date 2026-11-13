# Architecture & Implementation Plan: NET-801 v1.1 (BATON_NET-807)
## Soft-404 Elimination, Public Catalog Architecture Decision (Options A/B/C), and Pricing Navigation Fix

- **Track ID:** NET-801 v1.1 / BATON_NET-807 (Launch Priority for Thanksgiving Meta Ads 26 Nov 2026)
- **Author:** Antigravity Chief of Staff (AG CoS v4 Work `ba2bfdb2`)
- **Review Cycle:** Argon Review (Gemini 3.8) -> GB CoS (>=95) -> SAG Review (>=95) -> Founder Eric's Explicit Typed Choice (Option A, B, or C) & Typed YES
- **Target Branch:** `p7-v8.9` (Aligned with `origin/dev` catalog architecture `18a8b8e5`)
- **Status:** **PLAN ONLY** — Zero code modifications, zero deployments, zero Firestore writes/seeding. `origin/main` locked at `9f04550a`; Stripe strictly OFF.
- **Date:** 5 November 2026, 3:50 PM ET
- **Reference Batons & Scores:**
  - `BATON_NET-807_REVISE_SOFT404-PUBLIC-CATALOG-PRICING_v1.1_PER-COS-78-SAG-52_2026-11-05-1455.md`
  - `COS_SCORE_NET-801_SOFT404-PUBLIC-CATALOG-PRICING_20261105.md` (CoS 95 PASS / SAG 68 FAIL on v1.0)
  - `FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` (Scored 98/100 PASS by Argon)

---

## 1. Executive Summary & Ground-Truth Alignment

This revised v1.1 plan addresses pre-launch discovery and routing friction on `numista-vault.web.app` ahead of the 26 November 2026 Meta ad launch, rebasing strictly on verified repo ground truth:

1. **Rebase on Actual `/catalog` Status:**
   - In production today, live `/catalog` returns **HTTP 200** via the Firebase Single-Page Application (SPA) rewrite to `index.html`.
   - On the `origin/dev` branch, the public catalog browse screen (`lib/screens/catalog/catalog_browse_screen.dart`) is **already built and integrated** under NET-747, NET-768, and NET-777 v1.4.
   - We strike the false premise of an HTTP 404 status code and **do not create duplicate catalog screens**. We rebase cleanly on `dev`'s existing `CatalogBrowseScreen` and deep-link routing (`/catalog/:nacCode`).

2. **Catalog Census & Homepage Reconciliation (Resolution of Must-Fix #1 / S404-3):**
   - The marketing badge on `login_screen.dart:338, 466` currently claims `"5,142 Reference Coins"`.
   - Ground truth in `numista_backend/entries_master_20261103.jsonl` contains exactly **3,202 verified master reference entries** (2,965 coins + 181 notes + 56 medals), perfectly matching the 3,202 rows in `docs/MISSING_IMAGES.csv`.
   - We eliminate the unsupported 5,142 figure, reconcile all marketing badges and meta titles to **"3,202 Verified US Reference Entries"** (or `"~3,200 Reference Coins & Currency"`), and remove "World" claims (catalog scope is strictly US federal, pre-federal, and official US Mint medals/currency).
   - We delete unsourced claims: `99.4%` accuracy/coverage, "5,000+ indexable pages", "advisory board", "Sheldon grading", "100% Private & Secure", and "Passport Protocol".

3. **Options A, B, and C for Founder Eric's Explicit Typed Choice (Resolution of Must-Fix #5 & #8):**
   - We lay out three explicit architectural paths (A: Full Public `/catalog`, B: Homepage Search Popup Modal, C: Keep Gated Behind Authentication).
   - **Founder Eric must explicitly type his choice ("Option A", "Option B", or "Option C") along with his typed YES before any build execution or deployment occurs.**

4. **Public Valuations & Image Hygiene (Resolution of Must-Fix #3 & #4):**
   - Public catalog valuation displays are bound strictly to **CDN CPG retail** (`cpgRetail`). Zero wholesale prices. Zero user cost/ownership/valuation data. Missing or zero pricing renders a styled gold `'Valuation Pending'` chip.
   - AI replica images are allowed strictly inside labeled `ai_replica_images`, never primary or index.
   - Strict in-memory own-origin allowlist guard before fetch; zero external hotlinks or outbound links. Missing images render local SVG placeholders with zero CanvasKit CSP violations.

5. **Static OpenGraph (OG) Meta Tags for Meta Ads Crawler (Resolution of Must-Fix #2 / S404-2):**
   - Client-side JavaScript `document.title` and `pushState` are invisible to non-JS web scrapers (specifically Meta's `facebookexternalhit` and initial search engine crawler passes).
   - We specify static `<title>`, `<meta property="og:title">`, `<meta property="og:description">`, `<meta property="og:image">`, and `<link rel="canonical">` tags on pre-rendered entry points for ad landing pages (`numista.ai`, `/catalog`, `/pricing`).

6. **Pricing Button AuthGate Hijack & HTML Anchor Semantics (Resolution of Must-Fix #7):**
   - Fix AuthGate race condition in `widgets/auth_gate.dart`: Ensure `AuthGate` awaits initial authentication state restoration before redirecting, honoring `widget.publicRoute` for `/pricing` even for authenticated sessions.
   - Replace raw `InkWell` + `Navigator.push` in footer and pricing buttons with semantic HTML anchor elements via Flutter's `Link` widget (`package:url_launcher/link.dart`), restoring middle-click, right-click "Open in new tab", and crawler indexability.

7. **Standing Controls: Rollback, Preview Channel, $ Cap (Resolution of Must-Fix #6):**
   - Mandatory Firebase Hosting preview channel verification before production release.
   - Reversible via `firebase.json` and git revert pinned to `9f04550a`.
   - Public catalog traffic inherits the NET-804/NET-777 $25.00/month hard budget egress cap + $20.00/month Cloud Monitoring alert with `stop-public-egress` Cloud Function.
   - Automated test files explicitly marked as to-be-created implementation artifacts (`test/route_test.dart`, `test/auth_gate_test.dart`).

---

## 2. Catalog Census & Ground-Truth Reconciliation (S404-3)

### 2.1 The 5,142 vs 3,202 Discrepancy
- **Legacy Marketing Claim:** `login_screen.dart:338` (`"Explore 5,142 Reference Coins"`) and line 466 (`"5,142 Reference Coins"`).
- **Verified Repository Master:** `numista_backend/entries_master_20261103.jsonl` contains exactly **3,202** verified records:
  - Coins: 2,965
  - Notes: 181
  - Medals: 56
- **Missing Images Census:** `docs/MISSING_IMAGES.csv` contains exactly **3,202** rows (one per master record).

### 2.2 Reconciliation Actions
1. **Homepage Badge & Button:** Update `login_screen.dart` copy from `"5,142 Reference Coins"` to `"3,202 Verified US Reference Coins & Currency"` (or `"~3,200 Reference Coins & Currency"`).
2. **Remove "World" Claims:** The master catalog is strictly US-focused (federal coinage, pre-federal colonials/tokens, and official US Mint medals and currency). Foreign and world references are completely removed from public catalog copy.
3. **Delete Unsourced Statistics:**
   - Delete unsourced `99.4%` accuracy/coverage stat.
   - Delete claims of "5,000+ indexable pages" (an SPA rewrite to `index.html` does not constitute indexable pages without static pre-rendering).
   - Delete unsourced marketing fluff: "advisory board", "Sheldon grading standard guarantee", "100% Private & Secure", and "Passport Protocol".

---

## 3. Options A, B, and C for Founder Eric's Explicit Typed Choice

Founder Eric must decide the public accessibility architecture for the reference catalog:

| Option | Architectural Description | Pros | Cons / Constraints | Launch Readiness |
|---|---|---|---|---|
| **Option A (Recommended)** | **Full Public `/catalog` Browse Screen:** Anyone can browse the verified 3,202 reference catalog at `/catalog` and `/catalog/:nacCode` without signing in. Clicking "Add to My Collection" prompts login/signup. | • Directly fulfills homepage promise.<br/>• Gives Meta ads a dedicated, high-converting landing page.<br/>• Fully leverages already-built `CatalogBrowseScreen` on `dev`. | • Requires count reconciliation (3,202).<br/>• Requires strict CDN CPG retail-only pricing.<br/>• Requires static OG tags for Meta crawler. | High (Critical path for 26 Nov Thanksgiving ad). |
| **Option B** | **Homepage Search Popup Modal:** An `"Explore ~3,200 Reference Coins"` button on the homepage opens an in-modal search dialog without creating a standalone public URL. | • Fast to integrate.<br/>• Keeps visitors on homepage.<br/>• Avoids deep-linking complexity. | • Zero SEO value.<br/>• No deep-linked catalog landing pages for Meta ads.<br/>• Weak ad conversion. | Medium. |
| **Option C** | **Keep Gated Behind Sign-In; Update Copy:** Catalog remains strictly gated behind authentication. Homepage copy is updated to `"~3,200 Reference Coins & Currency (Members Only)"`. | • Smallest architectural footprint.<br/>• Zero public surface data exposure. | • Fails to provide an ad landing experience.<br/>• Leaves visitors unable to preview database coverage.<br/>• Weakest for Thanksgiving launch. | Low (Not recommended). |

> **MANDATORY GATE:** CoS recommends **Option A**. However, **Founder Eric must explicitly type his choice ("Option A", "Option B", or "Option C") along with his typed YES** before any code modifications, merges, or deployments occur.

---

## 4. Public Surface Data Hygiene & Privacy Protections

If Option A is selected by Founder Eric:
1. **Valuation Source:** Valuation figures displayed on public catalog cards are sourced strictly and exclusively from **CDN CPG retail** (`cpgRetail`).
   - Zero wholesale prices (no dealer ask/bid, no Greysheet wholesale).
   - Zero user cost basis, purchase prices, or collection valuations displayed.
   - Missing or zero pricing renders a styled gold `'Valuation Pending'` chip.
2. **Image Sourcing & CSP Compliance:**
   - High-resolution imagery is served exclusively from first-party GCS storage (`gs://numista-catalog-assets` / `gs://numista-reference-library`).
   - AI replica images are allowed strictly inside labeled `ai_replica_images`, never primary, card, or index.
   - Missing images render clean local SVG placeholders with zero external hotlinks and zero CanvasKit CSP violations.
3. **Outbound Links:** Zero outbound links to external coin pricing or cert verification sites (PCGS, NGC, eBay). In-app plain text citations only.

---

## 5. Routing, Soft-404, AuthGate & HTML Anchor Specifications

### 5.1 Static OpenGraph (OG) Meta Tags for Meta Ads Crawler (S404-2)
Meta's advertising preview scraper (`facebookexternalhit`) and Googlebot initial crawl do not execute Flutter's CanvasKit WebAssembly/JS engine. To prevent soft-404s and broken ad link previews:
1. In `numista_mobile/web/index.html` (and static route HTML fallbacks), provide static OpenGraph tags:
   ```html
   <title>Numista.AI — Verified US Coin & Currency Catalog</title>
   <meta name="description" content="Explore verified reference specifications, mintage figures, and CDN CPG retail values across 3,202 US coins, tokens, and currency." />
   <meta property="og:title" content="Numista.AI — Verified US Coin & Currency Reference Catalog" />
   <meta property="og:description" content="Explore verified reference specifications, mintage figures, and CDN CPG retail values across 3,202 US coins, tokens, and currency." />
   <meta property="og:image" content="https://storage.googleapis.com/numista-catalog-assets/branding/og-catalog-preview.png" />
   <meta property="og:url" content="https://numista.ai/catalog" />
   <meta property="og:type" content="website" />
   <link rel="canonical" href="https://numista.ai/catalog" />
   ```
2. Client-side title updates in Flutter web (`Title(title: '...', child: ...)`) continue to update the browser tab title dynamically for interactive users.

### 5.2 Pricing Button Navigation & AuthGate Fix
1. **AuthGate Race Condition Fix (`numista_mobile/lib/widgets/auth_gate.dart`):**
   - Ensure `AuthGate` properly awaits initial authentication state restoration from `FirebaseAuth.instance.authStateChanges()` before making redirection decisions.
   - When the user navigates directly to `/pricing` (or any whitelisted public route in `widget.publicRoute`), `AuthGate` must honor that route and render `PricingScreen` regardless of whether the session is authenticated or unauthenticated.
2. **Semantic HTML Anchor Semantics:**
   - In `login_screen.dart`, replace raw `InkWell` + `Navigator.push` on public links (Pricing, About, FAQ, Features) with Flutter's semantic `Link` widget:
   ```dart
   Link(
     uri: Uri.parse('/pricing'),
     builder: (context, followLink) => TextButton(
       onPressed: followLink,
       child: const Text('Pricing'),
     ),
   )
   ```
   - This ensures Flutter Web emits real HTML `<a href="/pricing">` DOM nodes, fully supporting middle-click, right-click "Open in new tab", browser history `pushState`, and search engine indexing.

---

## 6. Standing Controls, Rollback, Preview Channel & Spend Cap

1. **Feature Flag & Preview Channel:**
   - All routing and public catalog updates must be verified on an isolated Firebase Hosting preview channel (`firebase hosting:channel:deploy preview-net801`) prior to merging to `dev`.
2. **Rollback Strategy:**
   - Reversible cleanly via `firebase.json` rewrite configuration and git revert pinned to baseline commit `9f04550a`.
3. **Hard Dollar Spend Cap:**
   - Public catalog traffic inherits the NET-804/NET-777 programmatic spend controls: Google Cloud Billing budget Pub/Sub alert at $20.00/month and hard egress shutdown via Cloud Function `stop-public-egress` at **$25.00/month**.
4. **Automated Testing Suite (To-Be-Created Artifacts):**
   - `numista_mobile/test/route_test.dart`: Unit tests verifying URL normalization, public route allow-lists, and `isKnownPath` behavior.
   - `numista_mobile/test/auth_gate_test.dart`: Widget tests verifying that authenticated and unauthenticated sessions navigating to `/pricing` render `PricingScreen` without unwanted redirection.

---

## 7. Multi-Agent Review Chain & Approvals
- **Author:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Reviewer 1:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code & Data Auditor)
- **Reviewer 2:** Grok Bot Chief of Staff (Target: `>= 95 / 100`)
- **Reviewer 3:** Stand Alone Grok (SAG grok-4.7, Target: `>= 95 / 100`)
- **Founder Gate:** Founder Eric explicitly types his choice (**"Option A"**, **"Option B"**, or **"Option C"**) and types **YES** prior to any build execution or deployment.
