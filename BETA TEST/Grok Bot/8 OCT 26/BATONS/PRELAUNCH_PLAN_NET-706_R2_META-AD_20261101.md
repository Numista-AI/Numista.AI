# PRELAUNCH PLAN NET-706 R2 — META AD CAMPAIGN & TRACKING INFRASTRUCTURE
**Document Version:** R2 (Fix-Only addressing MF1–MF9 and SF1–SF7 from Grok CoS Score 55)  
**Date:** 2026-11-01 15:30 EST  
**Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)  
**Target Audience:** Founder Eric, Grok CoS, Argon (SAG Technical Auditor), Antigravity Desk  
**Authority:** `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` (NET-709A), `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md` (NET-712), `RADIO_OVER_NET-712A_GROKDESK-to-ALL_SF6-AGE-83_20261101-1517.md`  
**Mode:** DOCS-ONLY (Strictly Planning & Verification; zero code execution, zero deployment, zero Stripe live activation)

---

## 1. Executive Brief & Campaign Architecture

### 1.1 Campaign Objective & Parameters
- **Campaign Scope:** First paid user acquisition campaign for Numista.AI ahead of Thanksgiving 2026.
- **Budget & Duration:** $625 total ad spend over 7 days (Thursday 26 Nov 2026 through Wednesday 2 Dec 2026).
- **Target Geography:** United States only (all traffic strictly routed to `https://numista.ai/`).
- **Target Demographics [SF6]:**
  - **Meta Ad Manager Setting:** 35–65+ (Meta maximum age targeting parameter).
  - **Creative & Copy Requirement:** Per Founder Eric's explicit directive (*"My Aunt is 83, so bump it up to that"*), all ad creative visuals, typography, landing page headlines, and microcopy must be engineered for readability up to age 83. This requires minimum 18pt body text on mobile, high-contrast dark-on-light surfaces, large clickable touch targets (minimum 48x48dp), zero crypto/fintech jargon, and plain English descriptions.
- **Unified Homepage Scope [MF8]:**
  - **Headline:** `[PLACEHOLDER - Eric picks final wording: Numista.AI — AI-Powered Coin Collection Manager]`
  - **Subhead:** `[PLACEHOLDER - Eric picks final wording: AI-powered cataloging, grading, and valuation for 400 years of American coinage — from 17th-century pre-colonial silver to 2026 US Mint master releases.]`

### 1.2 System Locks & Deployment Guardrails [SF3]
- **Live Production Lock (`origin/main`):** Locked at commit `9f04550a`. Absolutely no direct commits or merges without Eric's explicit typed `YES`.
- **Development Branch Lock (`origin/dev`):** Dev tip is at commit `32d4b42e` (with catalog frozen at ancestor `9b55f3d9`).
- **Feature & Execution Branch:** All implementation work occurs exclusively on branch `p7-v8.9`.
- **Pre-Production Testing Channel:** Staged exclusively on Firebase Hosting preview channel `p7-gate` (`https://numista-vault--p7-gate-*.web.app`).
- **Stripe Lock:** Stripe remains locked OFF in live production. Test/Sandbox pricing only; live cutover strictly gated on Eric's separate typed `YES` before Thanksgiving.
- **Repository Hygiene:** Untracked commercial assets in `Commercials/Facebook commercial/` must NEVER be staged or committed (retained locally only).

---

## 2. Meta Domain Verification & Meta Pixel Base Code (Byte-Verbatim) [MF2]

### 2.1 Placement Location
Both the Domain Verification Meta Tag and the Meta Pixel Base Code are installed in `numista_mobile/web/index.html` immediately before the closing `</head>` tag (lines 114–115).
- **Critical Requirement:** Must be present in the static served HTML initially delivered to the client. No client-side JavaScript injection post-load (which fails Meta's automated crawler).

### 2.2 Domain Verification Tag (Byte-Verbatim)
```html
<meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />
```

### 2.3 Meta Pixel Base Code (Byte-Verbatim from NET-709A Spec)
The snippet below is copied byte-verbatim from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`, preserving exact comments, indentation, whitespace, and the `<noscript>` fallback:

```html
<!-- Meta Pixel Code -->
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

---

## 3. Event Tracking Architecture & Deduplication Engine

### 3.1 `PageView` Lifecycle & Double-Fire Prevention [MF3]
1. **Initial Page Load:** The Meta Pixel Base Code in `index.html` automatically executes `fbq('track', 'PageView');` once when the HTML document loads.
2. **Single-Page In-App Routing:** To track subsequent in-app page navigations (e.g., navigating to `/pricing`, `/about`, `/features`) without double-firing on initial load:
   - In `numista_mobile/lib/screens/base_layout.dart` (or via a navigation observer):
   - Maintain a route initialization flag: `bool _initialPageViewLogged = false;`
   - When the app mounts the first route, check `_initialPageViewLogged`. Because the static HTML base code already fired the initial load `PageView`, the Flutter router skips the first route and sets `_initialPageViewLogged = true`.
   - On every subsequent route navigation or tab switch initiated by the user, Flutter triggers:
     ```dart
     if (kIsWeb) {
       js.context.callMethod('fbq', ['track', 'PageView']);
     }
     ```
   - **Verification Contract:** Exactly 1 `PageView` fires on initial URL load; exactly +1 `PageView` fires per subsequent in-app navigation.

### 3.2 `CompleteRegistration` Deduplication & Guardrail [MF4]
The registration event is the core campaign optimization signal and must be strictly protected against false positives and duplication:
1. **Trigger Condition:** Fired ONLY when the server confirms successful account creation.
2. **Unified Helper Function:** Both signup methods route through a single, shared helper method in `numista_mobile/lib/services/meta_pixel_service.dart`:
   ```dart
   class MetaPixelService {
     static Future<void> trackCompleteRegistration(String uid) async {
       if (!kIsWeb || uid.isEmpty) return;
       final prefs = await SharedPreferences.getInstance();
       final key = 'meta_pixel_registered_$uid';
       if (prefs.getBool(key) == true) {
         // Already recorded on this client for this UID
         return;
       }
       await prefs.setBool(key, true);
       js.context.callMethod('fbq', ['track', 'CompleteRegistration']);
     }
   }
   ```
3. **Execution Paths:**
   - **Email + PIN Signup:** In `numista_mobile/lib/services/auth_service.dart:131` (`createAccount`):
     ```dart
     final cred = await _auth.createUserWithEmailAndPassword(
         email: email.trim().toLowerCase(), password: pin.trim());
     if (cred.user != null) {
       await MetaPixelService.trackCompleteRegistration(cred.user!.uid);
     }
     ```
   - **Google Sign-In:** In `numista_mobile/lib/services/auth_service.dart:148` (`signInWithGoogle`):
     ```dart
     final UserCredential cred = await _auth.signInWithPopup(provider);
     // CRITICAL: Only fire for brand-new users, never returning users
     if (cred.additionalUserInfo?.isNewUser == true && cred.user != null) {
       await MetaPixelService.trackCompleteRegistration(cred.user!.uid);
     }
     ```
4. **Strict Negative Rules:**
   - Failed signups (`FirebaseAuthException`) -> NEVER fire `CompleteRegistration`.
   - Returning Google sign-in (`isNewUser == false`) -> NEVER fire `CompleteRegistration`.
   - Demo Vault exploration -> NEVER fire `CompleteRegistration`.
   - Page refresh after signup -> Blocked by `meta_pixel_registered_<uid>` guard.

### 3.3 `InitiateCheckout` Event [SF5]
- **Trigger:** Fired when a signed-in user selects a paid subscription tier or top-up.
- **Timing:** In `numista_mobile/lib/services/stripe_service.dart:13` (`launchCheckoutSession`), the client posts to `/api/stripe/create-checkout-session`. When the backend returns HTTP 200 with a valid `checkout_url`, immediately before calling `launchUrl(sessionUrl)`, Flutter invokes:
  ```dart
  if (kIsWeb) {
    js.context.callMethod('fbq', ['track', 'InitiateCheckout', js.JsObject.jsify({
      'content_name': tier,
      'currency': 'USD',
    })]);
  }
  ```
- **Guardrail:** Exactly one event per checkout button click that successfully generates a checkout session.

### 3.4 `Purchase` Event & Verified Server Amount [SF2]
- **Trigger:** Fired ONLY after Stripe confirms successful payment processing.
- **Amount Authority:** The transaction value must NOT be read from client-side hardcoded pricing tables. It must be read directly from the server-verified Stripe session `amount_total` (converted from cents to USD: `amount_total / 100.0`).
- **Workflow:**
  1. When payment completes, Stripe redirects to `https://numista.ai/#/settings?stripe=success&session_id={CHECKOUT_SESSION_ID}`.
  2. Flutter settings screen calls backend `/api/stripe/verify-session?session_id=...`.
  3. The backend queries Stripe API / webhook records. If `payment_status == 'paid'`, it returns `{ "status": "paid", "amount_usd": 49.99, "currency": "USD" }`.
  4. Flutter checks local storage key `meta_purchase_fired_{session_id}`. If not yet fired:
     ```dart
     if (kIsWeb) {
       js.context.callMethod('fbq', ['track', 'Purchase', js.JsObject.jsify({
         'value': amountUsd,
         'currency': 'USD',
       })]);
       prefs.setBool('meta_purchase_fired_$sessionId', true);
     }
     ```
  5. If payment failed, cancelled, or is pending, `Purchase` is NEVER fired.

---

## 4. Real 404 Routing & Parameter Preservation (Fixing MF1)

### 4.1 Root Cause & Correction of Soft-404 Architecture
In Plan R1, adding a `"source": "**", "destination": "/index.html"` catch-all rewrite to `firebase.json` was backwards. The live production site ALREADY correctly serves real HTTP 404 responses for unknown URLs (e.g., `numista.ai/us-coins` -> 404, `numista.ai/unknown-path` -> 404). Adding a catch-all creates soft-404s, harming SEO and violating web standards.

### 4.2 Routing Configuration Rules
1. **`numista_mobile/firebase.json`:**
   - Maintain strict, explicit URL rewrites for known valid endpoints only (`/`, `/about`, `/pricing`, `/features`, `/faq`, `/login`, `/signup`, `/terms`, `/privacy`, `/demo`, `/claim/**`).
   - DO NOT ADD any wildcard `**` rewrite.
   - Any unmapped URL hitting Firebase Hosting will correctly return the static `404.html` with HTTP status 404.
2. **`numista_mobile/lib/main.dart` Client-Side Routing:**
   - In lines 119–149, unknown paths continue to route cleanly to `NotFoundScreen(attemptedPath: path)`.
   - For valid routes, ensure full URL query string preservation:
     ```dart
     final uri = Uri.base;
     final utmParams = {
       'utm_source': uri.queryParameters['utm_source'],
       'utm_medium': uri.queryParameters['utm_medium'],
       'utm_campaign': uri.queryParameters['utm_campaign'],
       'utm_content': uri.queryParameters['utm_content'],
       'fbclid': uri.queryParameters['fbclid'],
     };
     ```
   - These parameters are retained in application state so that when a visitor lands on `https://numista.ai/?utm_source=meta&utm_campaign=thanksgiving` or `https://numista.ai/pricing?utm_source=meta&fbclid=...`, the attribution parameters remain intact throughout the session and attach to account creation.

---

## 5. Pricing Plan v3.2 & Stripe 13-Price Catalog (Fixing MF5, MF6, MF9, SF1, SF4)

### 5.1 Plan v3.2 Core Entitlements & Pricing Structure
- **Free Tier:** Includes up to 10 items (not 5).
- **Copper Tier:** $4.99 / mo | $49.99 / yr  
  - *Annual Savings:* $9.89/yr (16.5% discount vs $59.88/yr; equivalent to ~2 months free at $4.99/mo).
- **Silver Tier:** $8.99 / mo | $89.99 / yr  
  - *Annual Savings:* $17.89/yr (16.6% discount vs $107.88/yr; equivalent to ~2 months free at $8.99/mo).
- **Platinum Tier:** $10.99 / mo | $109.00 / yr  
  - *Annual Savings:* $22.88/yr (17.3% discount vs $131.88/yr; equivalent to ~2.08 months free).
- **Gold Tier:** $15.99 / mo | $150.00 / yr  
  - *Annual Savings:* $41.88/yr (21.8% discount vs $191.88/yr; equivalent to ~2.62 months free).
- **Lifetime Membership [SF1]:** Stays ON HOLD. Price ($500 vs $1,500) is unresolved; no price or SKU is shipped.
- **AI Top-Up:** $5.00 one-time purchase per 1,000 items (not labelled storage).
- **Data Export Pricing Rule [MF5]:** Full data export costs 6 months of the user's plan price:
  - Copper Export: $29.94 (6 x $4.99)
  - Silver Export: $53.94 (6 x $8.99)
  - Platinum Export: $65.94 (6 x $10.99)
  - Gold / Never-Paid Legacy / Free Export: $95.94 (6 x $15.99 Gold baseline)
- **Legacy Account Definition [SF4]:** Per Plan v3.2/v3.3, Legacy accounts are defined as non-anonymous accounts created prior to the hard cutoff timestamp `2026-11-27T05:00:00Z` (recorded via `numista_backend/scripts/snapshot_legacy.py`).

### 5.2 Canonical 13 Stripe Prices (Zero Invented SKUs) [MF6]
The Stripe product catalog is composed of exactly 13 canonical prices (8 subscriptions, 1 AI top-up, and 4 full exports):

| # | Product Name | Type | Billing / Price | Product Identifier |
|---|---|---|---|---|
| 1 | Copper Monthly | Subscription | $4.99 / month | `prod_copper_sub` / `price_copper_monthly` |
| 2 | Copper Annual | Subscription | $49.99 / year | `prod_copper_sub` / `price_copper_annual` |
| 3 | Silver Monthly | Subscription | $8.99 / month | `prod_silver_sub` / `price_silver_monthly` |
| 4 | Silver Annual | Subscription | $89.99 / year | `prod_silver_sub` / `price_silver_annual` |
| 5 | Platinum Monthly | Subscription | $10.99 / month | `prod_platinum_sub` / `price_platinum_monthly` |
| 6 | Platinum Annual | Subscription | $109.00 / year | `prod_platinum_sub` / `price_platinum_annual` |
| 7 | Gold Monthly | Subscription | $15.99 / month | `prod_gold_sub` / `price_gold_monthly` |
| 8 | Gold Annual | Subscription | $150.00 / year | `prod_gold_sub` / `price_gold_annual` |
| 9 | AI Top-Up (1,000 Items) | One-time | $5.00 | `prod_ai_topup` / `price_topup_1000_ai` |
| 10 | Full Export — Copper | One-time | $29.94 | `prod_export_copper` / `price_export_copper` |
| 11 | Full Export — Silver | One-time | $53.94 | `prod_export_silver` / `price_export_silver` |
| 12 | Full Export — Platinum | One-time | $65.94 | `prod_export_platinum` / `price_export_platinum` |
| 13 | Full Export — Gold / Legacy | One-time | $95.94 | `prod_export_gold_legacy` / `price_export_gold_legacy` |

*Note:* Absolutely no unapproved SKUs (e.g., Estate Valuation $49, Family Seat $3.99, 30-Day AI Pass $9.99) exist in this plan. All 13 prices are initially verified in Stripe Sandbox/Test mode; live activation remains locked OFF.

---

## 6. Real Copy Citations & Homepage Scope Line (Fixing MF7, MF8)

### 6.1 Audit of Existing Trial Strings (Eliminating Fabrications) [MF7]
A complete repository search confirms that the string `"Start with 5 free coins"` DOES NOT EXIST in `numista_mobile/lib/screens/login_screen.dart` or anywhere in the codebase.
The actual verified strings in the repository are:
- `numista_mobile/lib/screens/login_screen.dart:456`:
  `'Create a free account to track your collection, log values, and export estate plans.'`
- `numista_mobile/lib/screens/public_info_screens.dart:181`:
  `'Free During Beta — Pricing TBA'`
  `'Numista.AI is currently in open public beta. During this phase, collection tracking, AI photo identification, and market value estimates are completely free for registered participants.'`
- `numista_mobile/lib/screens/base_layout.dart:444`:
  `"You're browsing a read-only demo. Create a free account to add coins, use the scanner, and save your collection."`
- `numista_backend/tier_gatekeeper.py:44`:
  `"free": 20` (in legacy limits) and `max_items: 10` in updated gatekeeper logic.

*Policy:* Existing beta copy remains untouched prior to the formal Paid Launch cutover. When the 13-price catalog goes live, the Free tier copy will display: *"Free tier includes up to 10 items."*

### 6.2 Homepage Scope Line Placeholder [MF8]
To avoid premature assumptions about production branding, the homepage hero copy is explicitly designated as a placeholder subject to Eric's final selection:
- **Hero Title:** `[PLACEHOLDER - Eric picks final wording: Numista.AI — AI-Powered Coin Collection Manager]`
- **Hero Subtitle:** `[PLACEHOLDER - Eric picks final wording: AI-powered cataloging, grading, and valuation for 400 years of American coinage — from 17th-century pre-colonial silver to 2026 US Mint master releases.]`

---

## 7. Privacy Policy Compliance & Cookie Disclosure

To comply with Meta Business Tools Terms and data privacy standards, the following disclosure is added to `numista_mobile/web/privacy.html` (under Section 3 "Analytics & Advertising Technologies") and reflected in `numista_mobile/lib/screens/public_info_screens.dart`:

> *"Numista.AI uses cookies, web beacons, and similar tracking technologies (including the Meta Pixel, Dataset ID: 2540753249725498) to understand user engagement, measure conversion events from advertising campaigns, and optimize service delivery. These technologies collect pseudonymous usage data such as page views and registration status. We do not sell your personal data or coin collection details to third parties. You may manage or disable cookies through your individual web browser settings."*

---

## 8. Verbatim Code Citations Checked Against `origin/dev`

All citations below have been verified verbatim against `origin/dev` (commit `32d4b42e`):

### Citation 1: `numista_mobile/web/index.html` lines 113–121
```html
  </script>

</head>
<body>
  <noscript>
    <div style="padding: 20px; text-align: center; font-family: sans-serif;">
      <h1>Numista.AI — AI-Powered Coin Collection Manager</h1>
      <p>Numista.AI uses Google Gemini AI to identify, catalog, appraise, and track your coin collection.</p>
      <p><strong>Disclaimer:</strong> Numista.AI is an independent software application and is NOT affiliated, associated, authorized, endorsed by, or in any way officially connected with Numista (numista.com).</p>
```

### Citation 2: `numista_mobile/lib/main.dart` lines 119–149
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

### Citation 3: `numista_mobile/lib/services/auth_service.dart` lines 130–160
```dart
  // ─── Create Account ───────────────────────────────────────────────────────
  static Future<AuthResult> createAccount(
      String email, String displayName, String pin) async {
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
  }

  // ─── Google Sign-In (web popup) ───────────────────────────────────────────
  static Future<AuthResult> signInWithGoogle() async {
    try {
      if (kIsWeb) {
        final provider = GoogleAuthProvider();
        provider.setCustomParameters({'prompt': 'select_account'});
        await _auth.signInWithPopup(provider);
      } else {
        // Fallback for non-web (desktop/mobile) — redirect flow
        final provider = GoogleAuthProvider();
        await _auth.signInWithRedirect(provider);
      }
      await UiVariantService.refresh();
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
```

### Citation 4: `numista_mobile/firebase.json` lines 125–135
```json
      {
        "source": "/claim",
        "destination": "/index.html"
      },
      {
        "source": "/claim/**",
        "destination": "/index.html"
      }
    ],

    "headers": [
      {
        "source": "**/*.@(js|css|wasm)",
```

### Citation 5: `numista_backend/tier_gatekeeper.py` lines 41–50
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

### Citation 6: `numista_backend/routes/payment_routes.py` lines 65–75
```python
                    },
                    'unit_amount': unit_amount,
                    'recurring': {'interval': interval}
                },
                'quantity': 1,
            }],
            success_url="https://numista.ai/#/settings?stripe=success",
            cancel_url="https://numista.ai/#/settings?stripe=cancel",
            metadata={"user_uid": user_uid, "target_tier": tier}
        )
        return {"checkout_url": session.url, "session_id": session.id}
```

### Citation 7: `numista_mobile/lib/services/stripe_service.dart` lines 10–20
```dart
  /// Launches Stripe Checkout for Pro ($4.99/mo) or Estate ($29/yr) subscription tiers.
  /// Sends the Firebase Bearer token — the server reads user identity from the token.
  static Future<bool> launchCheckoutSession({
    required String userEmail,
    required String tier,
    http.Client? client,
  }) async {
    try {
      final response = await HttpAuthClient.post(
        Uri.parse('$_baseUrl/api/stripe/create-checkout-session'),
        client: client,
        body: jsonEncode({
```

### Citation 8: `numista_mobile/lib/screens/base_layout.dart` lines 52–60
```dart
class BaseLayout extends StatefulWidget {
  final bool isDemoMode;
  const BaseLayout({super.key, this.isDemoMode = false});

  @override
  State<BaseLayout> createState() => _BaseLayoutState();
}

class _BaseLayoutState extends State<BaseLayout> {
```

---


### Citation 9: `numista_backend/tier_gatekeeper.py` lines 132–156 (Legacy Cutoff Definition)
```python
def get_user_tier(user_profile: dict) -> str:
    """Resolves subscription tier (stripe_tier -> tier -> beta/lifetime flags -> 'free').

    Beta access NEVER expires on the server — the cutoff (accounts created before
    2026-11-26T05:00Z) is enforced on the client by account creationTime.
    The server treats beta_tester=True as permanent family_estate regardless of any
    beta_access_expires field written by the Aug 2026 backfill script.
    """
    if user_profile.get("is_lifetime_family_estate") or user_profile.get("is_ai_qc_account"):
        return "family_estate"
    if user_profile.get("beta_tester"):
        return "family_estate"  # permanent — do NOT check beta_access_expires

    # Also grant beta tier if account was created before the Facebook ad launch (1795669200000 ms epoch)
    creation_ts = user_profile.get('creation_timestamp')
    if creation_ts is not None:
        try:
            if int(creation_ts) < 1795669200000:
                return 'family_estate'
        except (ValueError, TypeError):
            pass
```

## 9. Test Verification Protocol & Acceptance Criteria [MF1, MF3, MF4, SF5]

| Test ID | Objective | Procedure | Expected Result | Pass Criteria |
|---|---|---|---|---|
| **TEST-01** | Domain Verification Tag Static Presence | Run `curl -s https://numista.ai/ \| grep facebook-domain-verification` | Tag string present verbatim in `<head>` | Exit 0, exact content match |
| **TEST-02** | Meta Pixel Base Snippet Static Presence | Run `curl -s https://numista.ai/ \| grep -E '2540753249725498\|fbevents.js'` | Base snippet and `<noscript>` image present | Exit 0, exact dataset ID match |
| **TEST-03** | PageView Single Fire on Load | Load `https://numista.ai/` in browser with Meta Pixel Helper extension | Exactly 1 `PageView` recorded on initial load | Zero double-fire on first render |
| **TEST-04** | PageView Incremental Navigation | Navigate from `/` to `/pricing`, then to `/about` | Exactly +1 `PageView` fired per navigation | Router observer suppresses initial route, logs on changes |
| **TEST-05** | CompleteRegistration on Email Signup | Complete new email registration with unique test address | Exactly 1 `CompleteRegistration` fired | Fired on server success |
| **TEST-06** | CompleteRegistration on Google Signup | Sign up with new Google account (`isNewUser == true`) | Exactly 1 `CompleteRegistration` fired | Fired on server success |
| **TEST-07** | Returning User No-Fire Verification | Sign in with existing Google account (`isNewUser == false`) | Zero `CompleteRegistration` fired | Helper skipped |
| **TEST-08** | Failed Signup No-Fire Verification | Submit invalid signup form (e.g., weak pin, existing email) | Zero `CompleteRegistration` fired | Helper skipped |
| **TEST-09** | Demo Vault No-Fire Verification | Click "Try It Free" and explore Demo Vault | Zero `CompleteRegistration` fired | Helper skipped |
| **TEST-10** | InitiateCheckout Verification | Click "Upgrade" on pricing tier to trigger checkout session | Exactly 1 `InitiateCheckout` fired on session URL receipt | Fired before `launchUrl` |
| **TEST-11** | Purchase Verification & Server Amount | Complete test Stripe payment and return to settings success URL | Exactly 1 `Purchase` fired with server `amount_total` | Fired only after payment status confirmed |
| **TEST-12** | Real 404 Verification (Unknown Paths) | Request `https://numista.ai/us-coins` and `https://numista.ai/zzz-unknown?utm_source=meta` | HTTP status 404 returned | Real 404 response (no soft-404) |
| **TEST-13** | UTM Preservation (Known Routes) | Request `https://numista.ai/?utm_source=meta&utm_campaign=thanksgiving` and `https://numista.ai/pricing?utm_source=meta&fbclid=abc` | HTTP status 200 returned; UTM and `fbclid` query params intact | Query params preserved in app state |

---

## 10. Execution Gates & Sign-Off Workflow

1. **Gate 1 (Plan Scoring):** Grok CoS score $\ge 95/100$ and Argon (SAG Auditor) score $\ge 95/100$.
2. **Gate 2 (Executive Approval):** Explicit typed `YES` from Founder Eric to execute the plan.
3. **Gate 3 (Staged Implementation):** Implementation on branch `p7-v8.9`, local verification (`flutter analyze`, `pytest numista_tests/test_set_pricing.py`).
4. **Gate 4 (Preview Verification):** Deployment to Firebase Hosting preview channel `p7-gate` (`https://numista-vault--p7-gate-*.web.app`). Full execution of Tests 01–13.
5. **Gate 5 (Production Release):** Verification report submitted to Founder Eric. Live merge from `p7-v8.9` to `origin/dev`, and from `dev` to `origin/main` strictly upon Eric's final typed `YES`. Live Stripe activation unlocked only after end-to-end sandbox verification.

---
**END PLAN NET-706 R2**
