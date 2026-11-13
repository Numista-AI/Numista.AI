# NET-706 — PRE-LAUNCH IMPLEMENTATION PLAN: META ADS & MONETIZATION READINESS

**Author:** AG CoS v4 (station `ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**Date:** 2026-11-01  
**Status:** DRAFT FOR MULTI-AGENT REVIEW (Argon, Grok CoS, SAG, Founder Eric)  
**Target Delivery:** LIVE on `numista.ai` before **Thursday, November 26, 2026** (Thanksgiving Meta Ad Launch)  
**Baton Reference:** `NET-706` / `NET-709` / `NET-709A`  
**Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF; Live site 200 OK.  
**Mode:** DOCS-ONLY (`NO EXECUTE`). Zero code commits, zero deployments, zero Stripe activation until full review cycle passes.

---

## 1. Executive Summary & Strategic Context

Founder Eric is launching the platform's first paid Meta advertising campaign on **Thursday, November 26, 2026** (running through December 2, 2026, $625 spend, US only, targeted at coin collectors aged 35–65+). Every ad directs prospective collectors to `https://numista.ai/`.

To ensure maximum campaign return-on-ad-spend (ROAS), zero ad budget wastage, and rock-solid conversion tracking, this plan defines the complete pre-launch architectural, UI, pricing, and analytics roadmap:

1. **Meta Domain Verification & Pixel Integration (Authoritative Spec `NET-709A`):**
   - Verification Tag: `<meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />` placed directly in the static served HTML `<head>` of `web/index.html`.
   - Pixel ID: `2540753249725498` base code placed site-wide in static `<head>`.
   - Conversions API & Event Tracking: Client-side routing `PageView`, strictly server-confirmed `CompleteRegistration`, checkout handoff `InitiateCheckout`, and confirmed payment `Purchase`.
2. **Pricing Structure (Plan v3.2):**
   - Exact tier matrix: Free (10 items), Copper ($4.99/mo, $49.99/yr), Silver ($8.99/mo, $89.99/yr), Platinum ($10.99/mo, $109/yr), Gold ($15.99/mo, $150/yr). Display ordered by metal value.
   - Comprehensive copy audit eliminating obsolete "5 items" trial text across web and mobile.
   - Preserves v3.2 structural rules: guest cap 5 items + $0.10 AI; Legacy accounts unlimited; set coin = 1/4 item; top-ups $5 per 1,000 items.
3. **Homepage Scope & Commercial Ad Alignment:**
   - Seamless transition from Meta ad creative to site hero: *"AI-powered collection management for 400 years of American coinage — from pre-colonial silver through modern US Mint releases."*
4. **Soft-404 Elimination:**
   - Architecture hardening in `firebase.json` and Flutter `main.dart` ensuring paid traffic with ad query parameters (`fbclid`, UTM tags) or mistyped subpaths never lands on a blank canvas or 404 error.
5. **Stripe Sandbox to Live Pathway:**
   - Creation of the 13 canonical Stripe price objects in test mode.
   - Strict sandbox testing milestone completed by **Friday, November 6, 2026**.
   - Production cutover gated by Founder Eric's explicit typed `YES` immediately prior to Thanksgiving.

---

## 2. Milestone Countdown Timeline (Working Back from Nov 26 Launch)

```
[Nov 1] Plan Filed (NET-706) ──> [Nov 2] Argon & Grok CoS Review (Target >=95)
                                          │
                                          ▼
[Nov 3] SAG Review & Eric Typed YES ──> [Nov 4] Code Implementation on branch p7-v8.9
                                          │
                                          ▼
[Nov 5] p7-gate Preview Deploy & Pixel Helper / Events Manager Verification
                                          │
                                          ▼
[Nov 6] Stripe Sandbox E2E Verification Milestone & Field Tester Pass
                                          │
                                          ▼
[Nov 7–20] Buffer & Staging Hardening (No code drift; live site untouched)
                                          │
                                          ▼
[Nov 23] Production Release PR Prepared (dev -> main)
                                          │
                                          ▼
[Nov 24] Eric "Prepare to Deploy" Gate & Final Stripe Live Key Switch
                                          │
                                          ▼
[Nov 25] Production Sanity Verification (Live Pixel 200, Meta Domain Verified)
                                          │
                                          ▼
[Nov 26] 00:01 AM ET: Meta Ad Campaign LIVE ($625 Budget / US Traffic Active)
```

| Date | Milestone Target | Verification Gate |
| :--- | :--- | :--- |
| **Sun Nov 1** | NET-706 Plan Filed & Synced | Grok CoS & Argon ingest |
| **Mon Nov 2** | Technical Review & Plan Score $\ge 95/100$ | Independent review files |
| **Tue Nov 3** | SAG Concurrence & Founder Eric Typed `YES` | Formal sign-off in radio net |
| **Wed Nov 4** | Branch `p7-v8.9` Implementation (Docs & Code) | Rule 8 analyzer & test suite 100% PASS |
| **Thu Nov 5** | Preview Deployment to `p7-gate` channel | Meta Pixel Helper & Events Manager Test Events PASS |
| **Fri Nov 6** | **CRITICAL MILESTONE:** Stripe Sandbox E2E Verified | 13 test prices, mock checkout, webhook 200 OK |
| **Thu Nov 19** | Field Tester Formal Sign-Off | Full regression verification |
| **Tue Nov 24** | Deploy Gate: PR `dev` $ightarrow$ `main` | Owner's separate typed `YES` in Deploy Chat |
| **Wed Nov 25** | Live Meta Domain Verification in Business Manager | Meta Business Settings shows "Domain Verified" |
| **Thu Nov 26** | **Meta Paid Ad Campaign Starts** | Ad clicks land on `https://numista.ai/` with 0 errors |

---

## 3. Scope 1: Pricing Page & Tier Matrix (Plan v3.2)

### 3.1 Canonical Tier Specifications
The pricing structure follows **Plan v3.2**, strictly ordered by metal value:

| Tier | Item Capacity | Monthly Price | Annual Price | Annual Savings | Primary Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Free** | Up to 10 items | **$0.00** | **$0.00** | — | Trial collectors, casual searchers |
| **Copper** | 11 – 100 items | **$4.99 / mo** | **$49.99 / yr** | ~17% (2 mos free) | Active hobbyists & beginners |
| **Silver** | 101 – 249 items | **$8.99 / mo** | **$89.99 / yr** | ~17% (2 mos free) | Core numismatists |
| **Platinum** | 250 – 500 items | **$10.99 / mo** | **$109.00 / yr** | ~17% (2 mos free) | Advanced series builders |
| **Gold** | 501+ items | **$15.99 / mo** | **$150.00 / yr** | ~22% savings | High-volume & estate holders |

*Note:* Lifetime $500 tier is **ON HOLD** and will not be displayed or purchasable in this release.

### 3.2 Plan v3.2 Business Rules
1. **Free Trial Limit:** Fixed at **10 items lifetime** (upgraded from legacy 5 items).
2. **Guest Cap:** Unauthenticated guests may catalog up to **5 items** and receive **$0.10 in AI processing** before account creation prompt.
3. **Legacy Account Protection:** Legacy grandfathered accounts created prior to October 2026 retain **unlimited** capacity without forced subscription downgrade.
4. **Item Equivalence Rule:** Sets and rolls are measured fairly: 1 individual set coin = **0.25 items** (4 set coins count as 1 item towards tier ceiling).
5. **Add-on Storage Top-Ups:** Users who reach their tier cap may purchase storage top-ups at **$5.00 per 1,000 items** without forced tier bump.
6. **Data Export Pricing:** Full CSV & PDF appraisal export is included in all paid tiers (Copper through Gold); available as a **$4.99 one-time purchase** for Free accounts.

### 3.3 Site-Wide Trial Copy Audit
Every occurrence of obsolete "5 items" trial copy across the frontend and documentation will be systematically replaced with "10 items":
- `lib/screens/login_screen.dart`: Update guest onboarding modal from "Start with 5 free coins" $ightarrow$ "Start with 10 free coins".
- `web/index.html`: Update structured data and meta descriptions.
- `web/terms.html` & `web/privacy.html`: Synchronize tier allowance definitions.

---

## 4. Scope 2: Homepage Scope & Ad Alignment

### 4.1 Narrative Consistency
Meta ad creative highlights the vast historical depth of the platform. To eliminate bounce rate caused by cognitive dissonance, the homepage headline and subhead will explicitly match the campaign hook:

> **Homepage Headline:**  
> *"Your Coin Collection, Mastered with Gemini AI."*  
>   
> **Homepage Scope Subhead:**  
> *"AI-powered cataloging, grading, and valuation for 400 years of American coinage — from 17th-century pre-colonial silver to 2026 US Mint master releases."*

### 4.2 Targeted Ad Landing Context
Visitors arriving with Meta campaign tags (`?utm_source=meta&utm_medium=cpc&utm_campaign=thanksgiving2026`) will be greeted seamlessly on the front door without intrusive blocking modals, allowing immediate 1-click exploration of the collection manager or Morgan AI greeter.

---

## 5. Scope 3: Soft-404 Elimination Architecture

### 5.1 Root-Cause Analysis of Landing Drop-Offs
Currently, `numista_mobile/firebase.json` defines discrete rewrite destinations for individual routes (`/about`, `/pricing`, `/features`, etc.) but lacks a terminal catch-all rewrite rule. Any ad or external referral landing on an unmapped path (e.g., `https://numista.ai/us-coins`, `https://numista.ai/coins`, or URL parameters corrupted by aggressive mobile webview wrappers) is served `404.html` or a blank viewport.

Furthermore, `numista_mobile/lib/main.dart` lines 114–149 enforce a strict whitelist `isKnownPath`. Unmatched routes construct `NotFoundScreen(attemptedPath: path)`.

### 5.2 Two-Layer Hardening Strategy

#### Layer 1: Firebase Hosting Catch-All (`firebase.json`)
Append a terminal catch-all rewrite to `firebase.json` so that all unmatched HTTP GET requests serve `index.html` (the Flutter app shell):
```json
{
  "source": "**",
  "destination": "/index.html"
}
```
*Static asset exemption:* Existing rules for `/api/**`, `**/*.js`, `**/*.css`, and image assets remain higher in precedence, ensuring API routing and caching headers are completely unaffected.

#### Layer 2: Flutter Front-Door Graceful Fallback (`main.dart`)
Instead of abruptly rendering `NotFoundScreen` for incoming traffic containing advertising campaign parameters or unknown deep-links:
1. Preserve all query parameters (`fbclid`, `utm_source`, `utm_campaign`).
2. Log unrecognized paths for telemetry.
3. Automatically route unknown public URLs to the **Home Front Door / Welcome Screen**, displaying a gentle banner: *"Welcome to Numista.AI! Explore our collection manager below."*
4. Reserve `NotFoundScreen` strictly for clearly broken intra-app navigation.

---

## 6. Scope 4: Meta Pixel & Domain Verification Spec (Authoritative `NET-709A`)

Per authoritative specification `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` provided by Founder Eric (Dataset/Pixel ID: `2540753249725498`):

### 6.1 Domain Verification Meta Tag (Static `<head>`)
Placed verbatim inside `<head>` of `numista_mobile/web/index.html` (line 114, immediately above `</head>`):
```html
  <!-- Meta Domain Verification (Authoritative NET-709A) -->
  <meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />
```
> **CRITICAL REQUIREMENT:** The verification tag MUST reside in the raw static HTML served by Firebase Hosting. Under no circumstances will it be injected via JavaScript or Flutter bootstrap.

### 6.2 Meta Pixel Base Code (Static `<head>`)
Placed verbatim inside `<head>` of `numista_mobile/web/index.html` (immediately following the domain verification tag):
```html
  <!-- Meta Pixel Code (Authoritative NET-709A) -->
  <script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '2540753249725498');
  fbq('track', 'PageView');
  </script>
  <noscript><img height="1" width="1" style="display:none"
  src="https://www.facebook.com/tr?id=2540753249725498&ev=PageView&noscript=1"
  /></noscript>
  <!-- End Meta Pixel Code -->
```

### 6.3 Dart JS-Interop Tracking Service Architecture
To enable robust, type-safe event dispatching from Flutter without breaking cross-platform compilation (iOS/Android/Desktop), create `lib/services/meta_pixel_service.dart`:

```dart
// lib/services/meta_pixel_service.dart
import 'package:flutter/foundation.dart';
import 'meta_pixel_stub.dart'
    if (dart.library.js_interop) 'meta_pixel_web.dart';

class MetaPixelService {
  static void trackPageView() {
    if (!kIsWeb) return;
    metaPixelTrack('PageView');
  }

  static void trackCompleteRegistration() {
    if (!kIsWeb) return;
    metaPixelTrack('CompleteRegistration');
  }

  static void trackInitiateCheckout() {
    if (!kIsWeb) return;
    metaPixelTrack('InitiateCheckout');
  }

  static void trackPurchase({required double value, String currency = 'USD'}) {
    if (!kIsWeb) return;
    metaPixelTrackPurchase(value, currency);
  }
}
```

And in `web/index.html`, add a lightweight global bridge:
```html
<script>
  window._numistaPixelTrack = function(eventName, params) {
    if (typeof window.fbq === 'function') {
      if (params) {
        window.fbq('track', eventName, params);
      } else {
        window.fbq('track', eventName);
      }
    }
  };
</script>
```

### 6.4 Event Triggering Rules & Invariants
1. **`PageView`:**
   - Automatically dispatched once on initial static HTML load.
   - Dispatched on Flutter client-side route changes within `BaseLayout`.
2. **`CompleteRegistration` (Highest Priority Conversion Event):**
   - **Trigger:** Fired **ONLY** when an account creation call successfully resolves with a valid user UID from Firebase Authentication.
   - **Location:** Inside `AuthService.createAccount` (on success) and `AuthService.signInWithGoogle` (only when `userCredential.additionalUserInfo?.isNewUser == true`).
   - **Guards:** NEVER fire on button clicks, form renders, password-reset requests, login attempts, failed signups, or Demo Vault exploration. Exactly 1 event per created user.
3. **`InitiateCheckout`:**
   - **Trigger:** Fired when a signed-in user clicks to subscribe to any paid tier (Copper, Silver, Platinum, Gold) and `StripeService.launchCheckoutSession` receives a valid checkout URL from the backend.
   - **Guards:** Does not fire if checkout session generation returns 502 or network error.
4. **`Purchase`:**
   - **Trigger:** Fired **ONLY** after payment is confirmed by Stripe.
   - **Location:** On the return URL landing page (`/#/settings?stripe=success`), validated against a Firestore subscription document timestamp to prevent duplicate event firing on browser reloads.
   - **Payload:** `{ value: <charged_amount>, currency: 'USD' }`.

### 6.5 Privacy Policy Update (`web/privacy.html`)
Add the following plain-language cookie disclosure in Section 3 of `web/privacy.html` and `lib/screens/privacy_screen.dart`:
> *"Numista.AI uses cookies and privacy-respecting analytics technologies, including the Meta Pixel, to measure advertising performance and understand how visitors engage with our application. You can manage or block cookies at any time through your browser settings."*

---

## 7. Scope 5: Stripe Sandbox to Live Architecture

### 7.1 Creation of the 13 Canonical Stripe Prices
Founder Eric will be guided through creating the exact 13 catalog objects in the Stripe Dashboard (Test Mode):

| # | Product Name | Type | Price | Stripe Interval | Target Plan |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Numista Copper (Monthly) | Recurring | **$4.99** | Monthly | Copper |
| **2** | Numista Copper (Annual) | Recurring | **$49.99** | Yearly | Copper |
| **3** | Numista Silver (Monthly) | Recurring | **$8.99** | Monthly | Silver |
| **4** | Numista Silver (Annual) | Recurring | **$89.99** | Yearly | Silver |
| **5** | Numista Platinum (Monthly) | Recurring | **$10.99** | Monthly | Platinum |
| **6** | Numista Platinum (Annual) | Recurring | **$109.00** | Yearly | Platinum |
| **7** | Numista Gold (Monthly) | Recurring | **$15.99** | Monthly | Gold |
| **8** | Numista Gold (Annual) | Recurring | **$150.00** | Yearly | Gold |
| **9** | Storage Top-Up (1,000 Coins) | One-time | **$5.00** | One-time | All Tiers |
| **10** | Full Collection Export Pass | One-time | **$4.99** | One-time | Free Tier |
| **11** | Single Estate Valuation Package | One-time | **$49.00** | One-time | Add-on |
| **12** | Family Estate Linked Seat Add-on | Recurring | **$3.99** | Monthly | Gold Add-on |
| **13** | 30-Day Unlimited AI Pass | One-time | **$9.99** | One-time | Top-up |

### 7.2 Backend Configuration & Webhook Handling
- Update `numista_backend/routes/payment_routes.py` and `tier_gatekeeper.py` to map the new tier identifiers (`copper`, `silver`, `platinum`, `gold`) to exact coin limits (`100`, `249`, `500`, `999999`).
- Stripe Webhook listener (`/api/stripe/webhook`) handles `checkout.session.completed`, `customer.subscription.updated`, and `customer.subscription.deleted`, safely writing updated tier state to `users/{uid}` in Firestore.

### 7.3 Standing Security Lock & Production Cutover Rule
- **STANDING LOCK:** Stripe remains **OFF** in production. All development, staging, and preview testing runs exclusively against the Stripe Sandbox (`pk_test_...` / `sk_test_...`).
- **SEPARATE OWNER APPROVAL:** Production Stripe API keys will NOT be loaded until immediately prior to Thanksgiving, following a separate, explicit typed `YES` from Founder Eric.

---

## 8. Verbatim Repository Code Citations (Rule 6(a) Compliance)

In compliance with `GEMINI.md` Rule 6(a), the following citations represent the exact verbatim lines of code targeted for modification:

### Citation 1: `numista_mobile/web/index.html` (Lines 113–118)
```html
  }
  </script>

</head>
<body>
  <noscript>
```
*Modification:* Insert Meta domain verification tag, Meta Pixel base snippet, and JS event bridge immediately preceding line 116 (`</head>`).

### Citation 2: `numista_mobile/lib/main.dart` (Lines 119–149)
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
      path.startsWith('/claim') || // L5: reserved — falls through to home, not NotFoundScreen
      path.startsWith('/privacy') ||
      path.startsWith('/terms') ||
      path.startsWith('/add_coins') ||
      path.startsWith('/scraper_dashboard') ||
      path.startsWith('/api/');

  if (!isKnownPath) {
    runApp(MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      home: NotFoundScreen(attemptedPath: path),
    ));
    return;
  }
```
*Modification:* Add graceful fallback allowing campaign landing URLs with unknown parameters to route to the Front Door rather than displaying `NotFoundScreen`.

### Citation 3: `numista_mobile/lib/services/auth_service.dart` (Lines 133–145)
```dart
    try {
      final cred = await _auth.createUserWithEmailAndPassword(
          email: email.trim().toLowerCase(), password: pin.trim());
      // Store a display name so the sidebar shows a real name
      if (displayName.trim().isNotEmpty) {
        await cred.user?.updateDisplayName(displayName.trim());
      }
      await UiVariantService.refresh();
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code));
    }
```
*Modification:* Dispatch `MetaPixelService.trackCompleteRegistration()` inside the `try` block immediately preceding `return AuthResult.success();`.

### Citation 4: `numista_mobile/firebase.json` (Lines 130–135)
```json
      {
        "source": "/claim/**",
        "destination": "/index.html"
      }
    ],

    "headers": [
```
*Modification:* Insert catch-all rewrite rule `{ "source": "**", "destination": "/index.html" }` immediately before line 133 to eliminate soft-404s.

### Citation 5: `numista_backend/tier_gatekeeper.py` (Lines 41–50)
```python
TIER_COIN_LIMITS = {
    "free": 20,
    "pro": 100,
    "numismatist": 250,
    "dealer": 500,
    "estate": 1000,
    "family_estate": 2500,
    "sovereign": float("inf"),
    "power_user": float("inf"),
}
```
*Modification:* Synchronize `TIER_COIN_LIMITS` with Plan v3.2: `free: 10`, `copper: 100`, `silver: 249`, `platinum: 500`, `gold: float("inf")`.

---

## 9. Verification & Acceptance Testing Protocol

Prior to production promotion, the following machine-checkable gates must be executed and confirmed:

### 9.1 Static HTML & Tag Verification
1. Fetch `https://numista-vault--p7-gate-8avtpz22.web.app/` via HTTP GET.
2. Confirm raw response contains `<meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />`.
3. Confirm raw response contains `fbq('init', '2540753249725498')`.

### 9.2 Meta Pixel Helper & Events Manager Test Events
1. Open the preview URL with Chrome Meta Pixel Helper extension:
   - Confirm Pixel `2540753249725498` is detected with Green status.
   - Confirm 1 `PageView` event fires on load.
2. Create test user via email/PIN signup:
   - Confirm `CompleteRegistration` appears in Meta Events Manager Test Events tab.
3. Test guest demo vault:
   - Confirm NO `CompleteRegistration` event is fired.

### 9.3 Soft-404 URL Stress Testing
Test navigation to:
- `https://numista-vault--p7-gate-8avtpz22.web.app/us-coins?fbclid=test1234`
- `https://numista-vault--p7-gate-8avtpz22.web.app/?utm_source=meta`
- `https://numista-vault--p7-gate-8avtpz22.web.app/unknown-sub-route`
Confirm all URLs cleanly render the Numista.AI homepage/front door without white-screens or 404 errors.

### 9.4 Automated Flutter & Backend Regression
- Run `flutter analyze` in `numista_mobile/`: 0 errors.
- Run `flutter test` for auth and navigation suites: 100% PASS.
- Run backend pytest suite for payment routes: 100% PASS.

---

## 10. Multi-Agent Review Submission

This document is submitted for scoring and review per the standard Multi-Agent Review Protocol:

1. **Argon (SAG Technical Auditor):** Independent technical audit and verification of citations, JS bridge safety, and soft-404 mechanics.
2. **Grok CoS:** Independent scoring (target $\ge 95/100$) against requirements `NET-706` and `NET-709A`.
3. **SAG Concurrence:** Security and architectural sign-off (money-touching changes require full SAG audit).
4. **Founder Eric:** Morning typed `YES` to authorize execution on branch `p7-v8.9` only.

---

END PLAN NET-706
