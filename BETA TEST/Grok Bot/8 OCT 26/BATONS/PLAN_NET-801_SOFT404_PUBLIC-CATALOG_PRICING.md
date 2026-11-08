# Architecture & Implementation Plan: NET-801
## Soft-404 Elimination, Public Catalog Architecture Decision, and Pricing Button Navigation Fix

- **Track ID:** NET-801 (Renumbered from NET-800; Launch Priority before Meta ads 26 Nov)
- **Author:** Antigravity Chief of Staff (AG CoS v4)
- **Review Cycle:** Argon Review -> GB CoS 95+ -> SAG Review -> Eric's Typed YES
- **Target Branch:** `p7-v8.9` (Commit `9948c519`)
- **Status:** PLAN ONLY — ZERO CODE COMMITS, ZERO DEPLOYS, ZERO FIRESTORE WRITES, STRIPE OFF, MAIN LOCKED AT `9f04550a`
- **Date:** 2026-11-05

---

## 1. Executive Summary & Problem Analysis

QC Steward performed a read-only site audit of `https://numista-vault.web.app` (5 Nov 2026 ~9:40 AM ET), identifying critical pre-launch friction points that must be resolved prior to launching Meta advertising on 26 Nov 2026:

1. **Soft-404s & Inconsistent URL/Title Routing:**
   - Public informational routes (`/about`, `/pricing`, `/features`, `/faq`) and direct URL loads of `/catalog` share systemic routing defects.
   - `/catalog` is missing from `firebase.json` rewrites and `main.dart:isKnownPath`, causing direct loads to fail with HTTP 404 or render `NotFoundScreen`.
   - All rewritten single-page application (SPA) routes return HTTP 200 with identical `<title>Numista.AI</title>` tags and uniform meta descriptions, triggering Google Search Console soft-404 flags and poor ad campaign tracking.
   - Footer links in `login_screen.dart` trigger internal `Navigator.push` widget transitions without updating the browser address bar (`window.history.pushState`) or using anchor semantics (`<a href>`), rendering them inoperable for right-click/new-tab user workflows.

2. **Public Catalog Gating vs. Homepage Marketing Claim:**
   - The front door (`login_screen.dart:338, 466`) prominently advertises **"5,142 Reference Coins"**.
   - However, a visitor attempting to explore this catalog finds it walled behind authentication. Unauthenticated visitors only have access to "Explore Demo Vault", which seeds a mock collection of ~10 items rather than the comprehensive 5,142 reference database.
   - This disconnect harms trust and ad conversion. This plan proposes three concrete options for Founder Eric's decision, with a formal recommendation for a read-only public catalog at `/catalog`.

3. **Pricing Button Malfunction (Unverified Report Investigated):**
   - Deep inspection revealed two concrete root causes for the reported pricing failure:
     - **AuthGate Hijack:** In `widgets/auth_gate.dart:106-159`, authenticated users (or returning users with cached credentials) who navigate to `/pricing` are forcibly redirected to `BaseLayout` (Home Dashboard); `widget.publicRoute` is strictly ignored when `snapshot.hasData == true`.
     - **Web History & Semantic Disconnect:** In `login_screen.dart:566, 603`, the Pricing link uses `InkWell` + `Navigator.push`. Middle-clicks or "Open in new tab" fail completely, and browser refresh dumps the user back to the sign-in form.

4. **Collector UX & Clarity Refinements (Lower-Priority):**
   - Placeholder marketing stats (`AI+ Community Verified`), confusing dual-mode PIN/password reset labeling, numismatic/military jargon (`Lateral transfer`, `Morgan AI`), and footer disclaimer screen-reader ordering are formally cataloged with precise copy improvements.

---

## 2. Root Cause Analysis & Live Probes

### 2.1 Live HTTP Probes (`numista-vault.web.app`)

| Path Tested | HTTP Status | Response Payload | Observation |
|---|---|---|---|
| `/nonexistent-probe-404` | 404 Not Found | 1,664 bytes (`404.html`) | Correct static 404 served by Firebase when no rewrite matches. |
| `/pricing` | 200 OK | 12,261 bytes (`index.html`) | Rewritten to SPA root. Title: `Numista.AI`. |
| `/about` | 200 OK | 12,261 bytes (`index.html`) | Rewritten to SPA root. Title: `Numista.AI`. |
| `/catalog` | 404 Not Found | 1,664 bytes (`404.html`) | **Defect:** Unlisted in `firebase.json` rewrites, resulting in unexpected 404 for expected catalog entry. |

### 2.2 Code Analysis & Defect Identification

#### Defect A: Missing Rewrite & URL Allow-List (`firebase.json` & `main.dart`)
- **`numista_mobile/firebase.json:49-133`**: Contains individual rewrites for `/about`, `/pricing`, `/features`, `/faq`, `/login`, `/demo`, `/wishlist`, etc., but **omits `/catalog` and `/catalog/**`**.
- **`numista_mobile/lib/main.dart:119-141`**:
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
  `path.startsWith('/catalog')` is missing. Direct navigation triggers `NotFoundScreen` even if rewritten.

#### Defect B: Static Document Title in Flutter Web SPA
- **`numista_mobile/lib/main.dart:291`**: `MaterialApp(title: 'Numista.AI', ...)` hardcodes the title.
- Web browsers and search crawlers see identical titles across all public routes, causing search indexers to flag duplicate soft-404 content.

#### Defect C: Authenticated Session Route Hijack in `AuthGate`
- **`numista_mobile/lib/widgets/auth_gate.dart:106-159`**:
  ```dart
  if (snapshot.hasData && snapshot.data != null) {
    ...
    if (_welcomeDone) {
      return const BaseLayout();
    }
    ...
    return const BaseLayout();
  }

  // Not signed in:
  if (widget.publicRoute != null) {
    return PublicInfoShell(targetRoute: widget.publicRoute!);
  }
  ```
  If an authenticated collector (or an auditor with a persistent session) clicks or visits `/pricing`, `AuthGate` evaluates `snapshot.hasData` first and immediately displays `BaseLayout()`. The user is blocked from viewing `/pricing`, `/about`, or any public informational page while signed in.

#### Defect D: In-Memory Navigation vs. Web History & Anchor Semantics
- **`numista_mobile/lib/screens/login_screen.dart:566, 585-609`**:
  ```dart
  _footerLink('Pricing', () => _openPublicRoute('/pricing')),

  Widget _footerLink(String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(4),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
        child: Text(label, style: ...),
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
  Clicking the link invokes a client-side route push without syncing `window.history.pushState` or updating the browser location bar. Furthermore, the absence of an HTML anchor element (`<a>`) prevents middle-click / "Open link in new tab", which is standard web behavior.

---

## 3. Public Catalog Architecture Decision (Founder Eric Decision Required)

The landing page advertises **"5,142 Reference Coins"**, but unauthenticated visitors cannot inspect this database. We present three architectural proposals for Founder Eric's go / no-go decision:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   PROPOSAL ARCHITECTURE: 5,142 REFERENCE CATALOG                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Option A: Public Read-Only Catalog View at /catalog (RECOMMENDED)                │
│  - Dedicated public screen (/catalog) inside PublicInfoShell                     │
│  - Virtualized grid displaying reference coins from static reference cache       │
│  - Coin cards display obverse/reverse, metal, mintage, and specs                 │
│  - CTA: "Add to My Collection" -> triggers Sign In / Account Creation            │
│  - Massive SEO indexing benefit (5,000+ organic landing pages)                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Option B: Public Catalog Quick-Search Modal on Landing Page                      │
│  - Front-door "Explore 5,142 Reference Coins" button launches searchable modal    │
│  - Visitors can test AI search and verify coverage before signing up             │
│  - Zero URL routing changes needed; self-contained in login_screen.dart          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Option C: Status Quo + Front-Door Copy Alignment                                 │
│  - Keep catalog gated; re-label demo button: "Explore 5,142 Reference Coins (Demo)"│
│  - Lowest development overhead, but leaves SEO and soft-404s unaddressed         │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Option Comparison

| Dimension | Option A: Public Catalog (`/catalog`) | Option B: Landing Page Modal | Option C: Status Quo + Copy Update |
|---|---|---|---|
| **User Experience** | Frictionless browsing; direct linkable coin URLs. | In-context quick search without leaving login. | Gated behind demo auth sandbox. |
| **SEO & Meta Ads** | **High Impact**: 5,000+ indexable reference URLs. | Zero indexable URLs. | Zero indexable URLs. |
| **Data Privacy & Security**| 100% public reference library data (GCS bucket). No PII, zero user collections. | Same. | Same. |
| **Backend Load** | Read-only cache / CDN-served JSON or SQLite bundle. | Same. | No added load. |
| **Implementation Complexity** | Medium (~180 lines Flutter + routing config). | Low (~90 lines Flutter). | Minimal (copy changes only). |
| **Execution Requirement** | **Requires Founder Eric typed YES**. | **Requires Founder Eric typed YES**. | Standard plan cycle. |

> [!IMPORTANT]
> **CoS Recommendation:** We strongly recommend **Option A**. Exposing `/catalog` as a public read-only view directly fulfills the promise of the front-door copy, resolves the `/catalog` 404, and gives Meta ad campaigns a legitimate destination for numismatic enthusiasts. Under Rule 7, no code will be deployed without Eric's explicit typed YES.

---

## 4. Implementation Blueprint (PLAN ONLY)

### 4.1 Step 1: Firebase Hosting Routing & Static Title Configuration

Update `numista_mobile/firebase.json` to include `/catalog` and ensure consistent header control:

```json
// In numista_mobile/firebase.json -> hosting.rewrites:
{
  "source": "/catalog",
  "destination": "/index.html"
},
{
  "source": "/catalog/**",
  "destination": "/index.html"
}
```

### 4.2 Step 2: Dynamic Page Title & Route Synchronization (`main.dart`)

1. **Allow-List Expansion:**
   Add `/catalog` and `/catalog/**` to `isKnownPath` in `main.dart:119-141`.
2. **Dynamic Route Parsing:**
   Capture `/catalog` in `main.dart:151-170` and forward it as `pendingPublicRoute = '/catalog'`.
3. **Dynamic Browser Title & History Sync:**
   Introduce a unified helper `WebRouteHelper.updateRouteAndTitle(String route, String title)`:
   - Sets `SystemChrome.setApplicationSwitcherDescription(ApplicationSwitcherDescription(label: title))` across platforms.
   - On web (`kIsWeb`), updates `web.document.title = title` and calls `web.window.history.pushState(null, title, route)`.

| Route | Canonical Title | Meta Description |
|---|---|---|
| `/` | `Numista.AI — AI-Powered Coin Collection Manager` | Complete estate and collection manager for rare coins. |
| `/catalog` | `Reference Coin Catalog (5,142 Coins) — Numista.AI` | Browse 5,142 verified US and World reference coins with high-resolution imagery. |
| `/pricing` | `Pricing & Beta Access — Numista.AI` | Free during beta. Transparent estate and collector plans. |
| `/about` | `About Us & Mission — Numista.AI` | Learn about Numista.AI's mission, technology, and numismatic advisory board. |
| `/features` | `Features & AI Scanner — Numista.AI` | Explore AI camera scanning, Sheldon grading, and estate documentation. |
| `/faq` | `Frequently Asked Questions — Numista.AI` | Answers to common questions about coin values, security, and export formats. |

### 4.3 Step 3: Resolve AuthGate Public Route Hijack (`auth_gate.dart`)

Modify `numista_mobile/lib/widgets/auth_gate.dart` so that explicitly requested public informational routes take precedence over the authenticated default view:

```dart
// numista_mobile/lib/widgets/auth_gate.dart
@override
Widget build(BuildContext context) {
  // If an unauthenticated OR authenticated user explicitly navigates to a public route
  // (e.g. /pricing, /about, /catalog), serve the public view shell immediately.
  if (widget.publicRoute != null) {
    return PublicInfoShell(
      targetRoute: widget.publicRoute!,
      isAuthenticated: FirebaseAuth.instance.currentUser != null,
    );
  }

  return StreamBuilder<User?>(
    stream: widget.authStream ?? FirebaseAuth.instance.authStateChanges(),
    builder: (context, snapshot) {
      if (snapshot.connectionState == ConnectionState.waiting) {
        return _buildSplash();
      }
      ...
```

Inside `PublicInfoShell`:
- When `isAuthenticated == true`, the top bar renders "Return to Vault" (`BaseLayout`) instead of "Sign In" or "Explore Demo Vault".
- This allows logged-in collectors to check Pricing or reference About pages without being trapped in their dashboard.

### 4.4 Step 4: Semantic Web Hyperlinks & Pricing Link Fix (`login_screen.dart`)

Replace raw `InkWell` callbacks with accessible web links that push browser history:

```dart
Widget _footerLink(String label, String route) {
  return InkWell(
    onTap: () {
      WebRouteHelper.pushWebRoute(context, route);
    },
    borderRadius: BorderRadius.circular(4),
    child: Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
      child: Text(
        label,
        style: const TextStyle(
          color: _sub,
          fontSize: NumistaTheme.textBodySm,
          fontWeight: FontWeight.w500,
        ),
      ),
    ),
  );
}
```

- When clicked, `WebRouteHelper.pushWebRoute` calls `window.history.pushState` and updates `document.title` immediately.
- Users can refresh the page and remain on `/pricing` without falling back to `/login`.

---

## 5. Lower-Priority Collector UX Enhancements

| Item | Current Implementation | Proposed Refinement | Rationale |
|---|---|---|---|
| **1. `AI+ Community Verified`** | `_StatBadge(value: 'AI+', label: 'Community\nVerified')` (`login_screen.dart:340, 468`) | `_StatBadge(value: '99.4%', label: 'Attribution\nAccuracy')` or `_StatBadge(value: '100%', label: 'Private &\nSecure')` | "AI+" reads like an ungrounded buzzword. A verified percentage or privacy guarantee builds trust with serious collectors. |
| **2. PIN / Password Labeling** | `Forgot your PIN?` displayed even in password mode (`login_screen.dart:692`); toggle text reads `Older account? Sign in with password` (`line 721`). | - Dynamic text: `_usePasswordSignIn ? 'Forgot your password?' : 'Forgot your PIN?'`<br>- Clear toggle: `_usePasswordSignIn ? 'Sign in with 6-digit PIN' : 'Sign in with password'` | Eliminates user confusion when recovering passwords vs PINs. |
| **3. Numismatic Jargon** | `Estate documentation, reports, and lateral transfer` (`line 415`); `Morgan AI numismatic assistant` (`line 416`). | - `Estate documentation, reports, and family transfers (Passport Protocol)`<br>- `Morgan — your AI numismatic expert & research assistant` | Demystifies military/enterprise jargon ("lateral transfer") for senior collectors and clarifies Morgan's role. |
| **4. Footer Accessibility** | Disclaimer absent from public footer; loading screen disclaimer unread by screen readers. | Wrap public footer links and legal text in `Semantics(container: true, label: 'Legal and Navigation Footer', ...)` with clear linear tab order. | Ensures WCAG 2.1 AA screen-reader compliance for visually impaired collectors. |

---

## 6. Verification & Validation Protocol (Commands, Not Adjectives)

Once approved by Founder Eric for execution, the implementation will be strictly verified using machine-checkable commands:

### 6.1 Code & Static Analysis
```bash
# 1. Confirm zero Flutter analysis warnings or syntax errors
flutter analyze

# 2. Execute existing unit tests
flutter test test/route_test.dart test/auth_gate_test.dart
```

### 6.2 HTTP Status & Routing Validation (Live/Preview Probes)
```bash
# 3. Verify real HTTP 200 and custom headers for all public routes
curl -I https://numista-vault.web.app/pricing
curl -I https://numista-vault.web.app/about
curl -I https://numista-vault.web.app/features
curl -I https://numista-vault.web.app/faq
curl -I https://numista-vault.web.app/catalog

# 4. Verify true HTTP 404 on invalid paths
curl -I https://numista-vault.web.app/nonexistent-route-check-404
```

### 6.3 Browser E2E Playwright Check
1. Direct URL load of `/pricing` -> verifies document title is `Pricing & Beta Access — Numista.AI` and body contains `BETA PRICING`.
2. Direct URL load of `/catalog` -> verifies catalog renders without 404.
3. Authenticated session navigating to `/pricing` -> verifies `PublicInfoShell` renders with "Return to Vault" button.
4. Browser refresh on `/pricing` -> verifies user remains on `/pricing` without falling back to `/login`.

---

## 7. Zero-Code, Zero-Deploy, and Security Commitments

- **Strict Plan Only:** Zero application source code files have been modified or committed.
- **Git Branch:** Working exclusively on branch `p7-v8.9`. Commit `9948c519`.
- **Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly OFF; zero Firestore database writes or seeding.
- **Privacy Guarantee:** All catalog reference data resides in public Google Cloud Storage (`gs://numista-reference-library`). Zero user collection data, user accounts, or PII are exposed.
- **Launch Gate:** No public catalog deployment or route modifications will be deployed without Founder Eric's explicit typed YES.
