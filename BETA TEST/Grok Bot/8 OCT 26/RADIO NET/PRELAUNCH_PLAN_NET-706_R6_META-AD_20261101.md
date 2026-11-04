# PRELAUNCH PLAN NET-706 R6 -- META AD CAMPAIGN & TRACKING INFRASTRUCTURE
**Document Version:** R6 (FIX-ONLY; closes every must-fix in SAG_REVIEW_NET-706-R5_72_REVISE_20261101.md). Authored by GB CoS (Grok Bot), 2026-11-01 ~21:30 EST.
**Base:** R5 text unchanged except the sections marked [R6].
**Code verified against:** `origin/dev` `32d4b42e` (read with `git show 32d4b42e:<path>` on EDS_Laptop, 2026-11-01).
**Mode:** DOCS-ONLY. No code, no deploy, no Stripe activation. Any PASS still needs Eric's typed YES.

## R6 closure table (SAG R5 must-fixes)
| # | SAG must-fix | R6 fix | Where |
|---|---|---|---|
| M1 | Hash-form `success_url`; fragment params are not in `Uri.base.queryParameters`; no parser; TEST-11 cannot pass | Keep hash routing (verified: `payment_routes.py:71` and `tier_gatekeeper.py:234` both use `https://numista.ai/#/settings?...`). Add an explicit fragment parser `hashQuery()` (split `Uri.base.fragment` after `?` with `Uri.splitQueryString`). TEST-11 now asserts parser output. | §3.4, §9 |
| M2 | Google path needs `UserCredential` / `isNewUser`; current code discards popup result; redirect branch has no inline result | Verified `auth_service.dart:153` `await _auth.signInWithPopup(provider);` (result discarded) and `:157` `signInWithRedirect`. R6 captures the popup result, and for redirect uses `getRedirectResult()` on next app start. Existing `UiVariantService.refresh()` lines kept. | §3.2 |
| M3 | verify-session has no authz; session id is an oracle | Endpoint requires `Depends(get_current_user)` and returns 404 unless `session.client_reference_id == caller uid` AND `session.metadata.user_uid == caller uid`. Uniform 404 for not-found / not-yours. Rate-limited. | §3.4 |
| M4 | Prices / $625 / lifetime unsourced; conflict with code | §5 rewritten: every figure carries a source tag. Only $4.99/mo and $29/yr exist in code. Plan v3.2 figures trace to Eric's recorded decisions (29 Oct 2026, 6:20/6:35/7:17 PM ET) and are marked **ERIC-DECISION, NOT IN CODE**. Anything without a source is **UNVERIFIED**. Lookup-key -> gatekeeper mapping added. | §1.1, §5 |
| M5 | Rule 1 not closed in Stripe Checkout | Both checkout creators set `billing_address_collection="auto"` and no `shipping_address_collection`, plus `customer_update`/Portal address editing off. TEST-14 asserts no address fields in a test session. | §7.4, §9 |
| M6 | Rule 2 absent | §7.5 states the receipt rule and binds to NET-718 R4 SEC-1/SEC-2 (in-memory redaction, raw never stored). This plan adds no upload path. | §7.5 |


---

## 1. Executive Brief & Campaign Architecture

### 1.1 Campaign Objective & Parameters
- **Campaign Scope:** First paid user acquisition campaign for Numista.AI ahead of Thanksgiving 2026.
- **Budget & Duration:** $625 total ad spend [ERIC-DECISION, CoS record 1 Nov 2026; see §5.2] over 7 days (Thursday 26 Nov 2026 through Wednesday 2 Dec 2026).
- **Target Geography:** United States only (all traffic strictly routed to `https://numista.ai/`).
- **Target Demographics [SF6]:**
  - **Meta Ad Manager Setting:** 35–65+ (Meta maximum age targeting parameter).
  - **Creative & Copy Requirement:** Per Founder Eric's explicit directive (*"My Aunt is 83, so bump it up to that"*), all ad creative visuals, typography, landing page headlines, and microcopy must be engineered for readability up to age 83. This requires minimum 18pt body text on mobile, high-contrast dark-on-light surfaces, large clickable touch targets (minimum 48x48dp), zero crypto/fintech jargon, and plain English descriptions.
- **Unified Homepage Scope [MF8]:**
  - **Headline:** `[PLACEHOLDER - Eric picks final wording: Numista.AI -- AI-Powered Coin Collection Manager]`
  - **Subhead:** `[PLACEHOLDER - Eric picks final wording: AI-powered cataloging, grading, and valuation for 400 years of American coinage -- from 17th-century pre-colonial silver to 2026 US Mint master releases.]`

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
   - **Google Sign-In [R6]:** `numista_mobile/lib/services/auth_service.dart:148-166` (`signInWithGoogle`). Verified current code at `32d4b42e`: line 153 `await _auth.signInWithPopup(provider);` (result discarded) and line 157 `await _auth.signInWithRedirect(provider);`. R6 change (NEW WORK, insertion only; lines 151-152 and 159 `await UiVariantService.refresh();` kept as-is):
     ```dart
     if (kIsWeb) {
       final provider = GoogleAuthProvider();
       provider.setCustomParameters({'prompt': 'select_account'});
       final UserCredential cred = await _auth.signInWithPopup(provider);   // was: result discarded
       if (cred.additionalUserInfo?.isNewUser == true && cred.user != null) {
         await MetaPixelService.trackCompleteRegistration(cred.user!.uid);
       }
     } else {
       final provider = GoogleAuthProvider();
       await _auth.signInWithRedirect(provider);   // unchanged; result read on return (below)
     }
     await UiVariantService.refresh();             // unchanged
     ```
     Redirect branch: the redirect leaves the page, so `isNewUser` is read on the next app start in `AuthService.init()` (NEW WORK): `final r = await _auth.getRedirectResult(); if (r.additionalUserInfo?.isNewUser == true && r.user != null) { await MetaPixelService.trackCompleteRegistration(r.user!.uid); }`. The Pixel only runs on web (`kIsWeb` guard in the helper), so the redirect branch is a no-op for Pixel on mobile.
   - **Email signup [R6 note]:** the insertion goes after the existing `updateDisplayName` (line 138) and before `UiVariantService.refresh()` (line 140); those lines are unchanged.
   - **"Server confirms" wording [R6]:** confirmation is the Firebase Auth SDK returning a `UserCredential` without throwing; there is no Numista backend call in this path.
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

### 3.4 `Purchase` Event & Verified Server Amount [R6: M1, M3]
- **Trigger:** Fired ONLY after the backend confirms with Stripe that the session is paid AND belongs to the signed-in user.
- **Amount Authority:** `session.amount_total / 100.0` from Stripe, never a client price table.
- **Verified current code (32d4b42e):** `numista_backend/routes/payment_routes.py:32-80` `create-checkout-session` already requires `Depends(get_current_user)` and sets `client_reference_id=user_uid` (line 57) and `metadata={"user_uid": user_uid, "target_tier": tier}` (line 73). `success_url` line 71 is `"https://numista.ai/#/settings?stripe=success"`. No `/api/stripe/verify-session` exists today (`git grep verify-session 32d4b42e` = 0 hits).
- **Plumbing [NEW WORK]:**
  1. `payment_routes.py:71` -> `success_url="https://numista.ai/#/settings?stripe=success&session_id={CHECKOUT_SESSION_ID}"`. Same change for the default at `tier_gatekeeper.py:234` and the caller-supplied URL path at `tier_gatekeeper.py:198`. Hash routing is kept on purpose (all existing Stripe return URLs are hash-form); no new path route is added.
  2. New endpoint in `payment_routes.py`:
     ```python
     @router.get("/verify-session")
     async def api_stripe_verify_session(session_id: str, _user: Dict[str, Any] = Depends(get_current_user)):
         caller_uid = _user.get("uid") or _user.get("user_id") or ""
         if not caller_uid or not session_id.startswith("cs_"):
             raise HTTPException(status_code=404, detail="Not found")
         try:
             s = stripe.checkout.Session.retrieve(session_id)
         except Exception:
             raise HTTPException(status_code=404, detail="Not found")
         owner_ok = (s.get("client_reference_id") == caller_uid) and ((s.get("metadata") or {}).get("user_uid") == caller_uid)
         if not owner_ok:
             logger.warning("verify-session ownership mismatch")   # no session id / uid in log text
             raise HTTPException(status_code=404, detail="Not found")   # same response as not-found: no oracle
         if s.get("payment_status") != "paid":
             return {"status": "unpaid"}
         return {"status": "paid", "amount_usd": (s.get("amount_total") or 0) / 100.0, "currency": (s.get("currency") or "usd").upper()}
     ```
     - Ownership check uses both fields that the existing checkout creator writes (lines 57 and 73). `tier_gatekeeper.create_upgrade_checkout_session` also writes both (`client_reference_id=user_id`, `metadata.user_uid`, lines 194/200).
     - No email, customer, or address data is returned.
     - Rate limit: 10 calls/min per uid (reuse the existing per-user limiter if one exists at implementation time; otherwise a simple Firestore/in-memory counter). Marked NEW WORK.
  3. **Client fragment parser [R6: M1]** in the settings screen init (NEW WORK). With hash routing the query is inside the fragment, so `Uri.base.queryParameters` is empty:
     ```dart
     Map<String, String> hashQuery() {
       final frag = Uri.base.fragment;            // e.g. "/settings?stripe=success&session_id=cs_test_..."
       final q = frag.indexOf('?');
       return q < 0 ? const {} : Uri.splitQueryString(frag.substring(q + 1));
     }
     final p = hashQuery();
     if (p['stripe'] == 'success' && (p['session_id'] ?? '').startsWith('cs_')) { /* call verify-session with ID token */ }
     ```
     The same helper is used for UTM capture when a visitor lands on a hash URL (§4.2 still reads `Uri.base.queryParameters` for path URLs; both are merged).
  4. Client calls `GET /api/stripe/verify-session?session_id=...` with the Firebase ID token. If `status == 'paid'` and `meta_purchase_fired_{session_id}` is not set, fire `fbq('track','Purchase',{value: amount_usd, currency})` and set the key.
  5. Unpaid, cancelled, 404, or network error -> `Purchase` is NEVER fired.

---

## 4. Real 404 Routing & Parameter Preservation (Fixing MF1, SF-C)

### 4.1 Root Cause & Correction of Soft-404 Architecture
The live production site ALREADY correctly serves real HTTP 404 responses for unknown URLs (e.g., `numista.ai/us-coins` -> 404, `numista.ai/unknown-path` -> 404). Any catch-all wildcard rewrite in `firebase.json` creates soft-404s, harming SEO and violating web standards.

### 4.2 Routing Configuration Rules [SF-C, SF-D, SF-E]
1. **`numista_mobile/firebase.json` (lines 64–133 rewrite rules and lines 21–47 redirects):**
   - The file currently defines explicit route rewrites only:
     - **Static HTML Rewrites:**
       - Lines 65–68 (source: line 66): `"source": "/privacy"` -> `"destination": "/privacy.html"`
       - Lines 69–72 (source: line 70): `"source": "/terms"` -> `"destination": "/terms.html"`
     - **SPA Index Rewrites (`/index.html`):**
       - Line 74: `"source": "/about"` -> `"destination": "/index.html"`
       - Line 78: `"source": "/pricing"` -> `"destination": "/index.html"`
       - Line 82: `"source": "/features"` -> `"destination": "/index.html"`
       - Line 86: `"source": "/faq"` -> `"destination": "/index.html"`
       - Line 90: `"source": "/login"` -> `"destination": "/index.html"`
       - Line 94: `"source": "/reset-password"` -> `"destination": "/index.html"`
       - Line 98: `"source": "/signup"` -> `"destination": "/index.html"`
       - Line 102: `"source": "/demo"` -> `"destination": "/index.html"`
       - Line 106: `"source": "/"` -> `"destination": "/index.html"`
       - Line 110: `"source": "/index.html"` -> `"destination": "/index.html"`
       - Line 114: `"source": "/wishlist"` -> `"destination": "/index.html"`
       - Line 118: `"source": "/wishlist/**"` -> `"destination": "/index.html"`
       - Line 122: `"source": "/attorney_portal"` -> `"destination": "/index.html"`
       - Line 126: `"source": "/claim"` -> `"destination": "/index.html"`
       - Line 130: `"source": "/claim/**"` -> `"destination": "/index.html"`
     - **301 Redirects (`redirects` block lines 21–47):**
       - Line 23: `"source": "/app"` -> `"destination": "/"`
       - Line 28: `"source": "/blog"` -> `"destination": "/about"`
       - Line 33: `"source": "/signin"` -> `"destination": "/login"`
       - Line 38: `"source": "/forgot"` -> `"destination": "/reset-password"`
       - Line 43: `"source": "/reset"` -> `"destination": "/reset-password"`
     - *(Note [SF-D, SF-E]: `/app` (line 23), `/blog` (line 28), `/signin` (line 33), `/forgot` (line 38), and `/reset` (line 43) are 301 redirects in the redirects block at lines 21–47, outside the rewrites block. There is no `/attorney` rewrite; the route is `/attorney_portal` at line 122. Line 248 `"source": "**"` is located in the `"headers"` block at lines 246–252, not a rewrite rule; the no-catch-all-rewrite invariant strictly holds).*
   - **Strict Invariant:** NO wildcard `"source": "**"` rewrite is added. Any unmapped path hitting Firebase Hosting continues to return the static `404.html` with real HTTP 404 status.
2. **`numista_mobile/lib/main.dart` Client-Side Routing:**
   - In lines 119–149, unknown paths continue to route cleanly to `NotFoundScreen(attemptedPath: path)`.
   - For valid routes, query string parameters are parsed and preserved from `Uri.base.queryParameters`:
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
   - These parameters remain in memory so that visitors landing on `https://numista.ai/?utm_source=meta&utm_campaign=thanksgiving` or `https://numista.ai/pricing?utm_source=meta&fbclid=...` retain ad attribution through account signup.

---

## 5. Pricing [R6: M4] -- every figure carries a source tag
Source tags: **CODE** = present at `origin/dev 32d4b42e` (file:line given). **ERIC-DECISION** = Eric's recorded pricing decisions of 29 Oct 2026 (6:20 PM, 6:35 PM, 7:17 PM ET; Plan v3.2, scored 96 by GB CoS), held in CoS memory; NOT in code and NOT yet confirmed by Eric for this campaign. **UNVERIFIED** = no source found; must be confirmed by Eric before any Stripe object is created.

### 5.1 What the code charges today (CODE)
- `numista_backend/routes/payment_routes.py:50-51`: `unit_amount = 2900 if tier in ["estate","family_estate"] else 499`; interval year for estate tiers, month otherwise. That is **$4.99/mo** for pro/numismatist/dealer and **$29.00/yr** for estate/family_estate.
- `numista_mobile/lib/services/stripe_service.dart:11` comment: "Pro ($4.99/mo) or Estate ($29/yr)". Consistent with the line above.
- `numista_backend/tier_gatekeeper.py:180-187` (second checkout path) uses env vars `STRIPE_PRICE_PRO|NUMISMATIST|DEALER|ESTATE|FAMILY_ESTATE|SOVEREIGN` with mock fallbacks (`price_1ProMockID` etc.). Real price ids are not in the repo.
- Tier keys and coin limits (`tier_gatekeeper.py:41-50`): free 20, pro 100, numismatist 250, dealer 500, estate 1000, family_estate 2500, sovereign/power_user unlimited.
- `Pitch Deck/pitch_deck_screen.dart:704` says "$14.99 – $29.99/mo". Pitch copy only; not a price source. Flagged so nobody copies it.

### 5.2 Plan v3.2 figures (ERIC-DECISION, not in code)
| Item | Figure | Tag |
|---|---|---|
| Free | 10 items lifetime | ERIC-DECISION (code says 20) |
| Copper | $4.99/mo, $49.99/yr; 11-100 items | ERIC-DECISION (6:20 PM prices, 6:35 PM ranges) |
| Silver | $8.99/mo, $89.99/yr; 101-249 items | ERIC-DECISION |
| Platinum | $10.99/mo, $109/yr; 250-500 items | ERIC-DECISION |
| Gold | $15.99/mo, $150/yr; 501+ items | ERIC-DECISION |
| Legacy (never-paid) full export | $95.94 (Gold price x 6) | ERIC-DECISION (7:17 PM) |
| Full export for paid tiers = 6 x monthly ($29.94 / $53.94 / $65.94) | derived arithmetic | **UNVERIFIED** (rule source not found; only the Legacy figure is recorded) |
| AI top-up $5.00 per 1,000 items | | **UNVERIFIED** |
| Lifetime | $500 recorded 29 Oct, then put ON HOLD; "$1,500" has no source | ON HOLD; $1,500 **UNVERIFIED**; no SKU created |
| Ad budget $625, 26 Nov - 2 Dec, US only | | ERIC-DECISION (CoS record 1 Nov 2026) |
The $109 and $150 annual figures do not follow the .99 pattern; they are recorded that way in Eric's decision and are kept, but Eric must re-confirm them before Stripe objects are created (Gate 2 item).

### 5.3 Lookup keys -> code tier keys (NEW WORK, proposed)
The site's new metal names do not exist in code. Mapping proposed for `tier_gatekeeper.py` (Eric to confirm):
| Proposed lookup_key | Code tier key | Coin limit change |
|---|---|---|
| copper_monthly / copper_annual | pro | 100 (matches Copper 11-100) |
| silver_monthly / silver_annual | numismatist | 250 -> 249 |
| platinum_monthly / platinum_annual | dealer | 500 (matches) |
| gold_monthly / gold_annual | estate | 1000 -> unlimited (Gold 501+) |
| export_* , ai_topup_1000 | one-time; no tier change | n/a |
`payment_routes.py:50` hardcoded `unit_amount` must be replaced by `stripe.Price.list(lookup_keys=[...])` so prices live only in Stripe. `family_estate`/`sovereign` keys stay for legacy/beta accounts (`get_user_tier` lines 140-151). No Stripe object is created in this plan.

### 5.4 Legacy cutoff -- OPEN conflict
Code: `tier_gatekeeper.py:145-150` uses `creation_timestamp < 1795669200000` = 2026-11-26T05:00Z (00:00 ET 26 Nov). Eric's 29 Oct 5:14 PM ET decision says legacy covers accounts created before 00:00 ET 27 Nov 2026 (= 1795755600000). R5 called this "settled at 26 Nov"; R6 marks it **OPEN for Eric** and changes nothing.

---

## 6. Real Copy Citations & Homepage Scope Line (Fixing MF3, MF8)

### 6.1 Audit of Existing Trial Strings (Verified Line Numbers) [MF3]
Repo-wide search confirms that `"Start with 5 free coins"` does NOT exist.
The actual verified strings in `origin/dev` (`32d4b42e`) with verified line numbers are:
- `numista_mobile/lib/screens/login_screen.dart:1388`:  
  `'Create a free account to track your collection, log values, and export estate plans.'`
- `numista_mobile/lib/screens/public_info_screens.dart:362`:  
  `'Free During Beta -- Pricing TBA'`
- `numista_mobile/lib/screens/public_info_screens.dart:407`:  
  `'Numista.AI is currently in open public beta. During this phase, collection tracking, AI photo identification, and market value estimates are completely free for registered participants.'`
- `numista_mobile/lib/screens/base_layout.dart:1540`:  
  `"You're browsing a read-only demo. Create a free account to add coins, use the scanner, and save your collection."`
- `numista_backend/tier_gatekeeper.py:42`:  
  `"free": 20` (existing legacy limit; Plan v3.2 policy target is 10 items).

*Policy:* Existing beta copy remains untouched prior to Paid Launch. When Paid Launch occurs, copy will reference the 10-item limit.

### 6.2 Homepage Scope Line Placeholder [MF8]
Hero copy is strictly designated as a placeholder:
- **Hero Title:** `[PLACEHOLDER - Eric picks final wording: Numista.AI -- AI-Powered Coin Collection Manager]`
- **Hero Subtitle:** `[PLACEHOLDER - Eric picks final wording: AI-powered cataloging, grading, and valuation for 400 years of American coinage -- from 17th-century pre-colonial silver to 2026 US Mint master releases.]`

---

## 7. Privacy Policy Compliance & Harmonization (Fixing MF-A, Settled NET-714A)

Per Founder Eric's binding decisions (`NET-714A`) and Grok CoS audit findings (`NET-716`, `NET-719`), the privacy policy updates must **extend existing policy sections** rather than append disjoint paragraphs, resolving existing statements like *"No data is shared with third-party advertisers"* so there is zero internal contradiction regarding advertising campaign measurement:

### 7.1 Key Invariants [NET-714A]
1. **No Home-Address Collection:** Numista.AI intentionally does NOT collect users' home addresses or physical locations anywhere in the service, guaranteeing that no collection's value can ever be tied to a physical location. The implementation will NOT add any address collection.
2. **Explicit Non-Sale Commitment:** Explicitly preserves and extends the commitment that Numista.AI does not sell, rent, or trade personal data or coin collection details to third parties.
3. **Harmonized Advertising Measurement:** Clarifies that Meta Pixel event data (Dataset ID: 2540753249725498) is utilized strictly for campaign measurement and conversion attribution, while reiterating that beyond this measurement, no personal data is shared with third-party advertisers or marketers.

### 7.2 In-App Privacy Screen Update (`numista_mobile/lib/screens/privacy_screen.dart`) [MF-B]
Target: Section 4 ("4. Sharing Your Information"), line 139.

**Exact Existing Line 139 (BEFORE):**
```dart
                      'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
```

**Exact Updated Line 139 (AFTER):**
```dart
                      'We do not sell, rent, or trade your personal data or coin collection details to third parties. We deliberately do not collect home addresses, so no collection\'s value can ever be tied to a physical location. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). Numista.AI uses cookies and similar technologies (including the Meta Pixel, Dataset ID: 2540753249725498) to measure advertising effectiveness and understand actions users take on our site; you can control your ad preferences through your Facebook account settings. Beyond this campaign measurement, no personal data is shared with third-party advertisers or marketers.',
```

### 7.3 Web Privacy Document Update (`numista_mobile/web/privacy.html`) [MF-C]
Target: Section 4 ("4. Sharing Your Information"), line 325.

**Exact Existing Line 325 (BEFORE):**
```html
<p>We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
```

**Exact Updated Line 325 (AFTER):**
```html
<p>We do not sell, rent, or trade your personal data or coin collection details to third parties. Numista.AI deliberately does not collect users' home addresses, so no collection's value can ever be tied to a physical location. Numista.AI uses cookies and similar technologies (including the Meta Pixel, Dataset ID: 2540753249725498) for analytics and advertising measurement; visitors can control cookies in browser settings and manage ad preferences through their Facebook account. Beyond this campaign measurement, no personal data is shared with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
```

**Section 3 ("3. How We Use Your Information") Extension:**
In lines 280–320 of `numista_mobile/web/privacy.html`, add an explicit list item:
```html
<li><strong>Advertising Campaign Measurement:</strong> To measure the effectiveness of our advertising campaigns and understand actions users take on our site using the Meta Pixel (Dataset ID: 2540753249725498).</li>
```

---


### 7.4 Stripe Checkout: no address collection [R6: M5] (NEW WORK)
Both checkout creators (`payment_routes.py:53-74`, `tier_gatekeeper.py:191-201`) get explicit arguments:
```python
billing_address_collection="auto",     # Stripe asks only what the card network needs (often ZIP); never a full street address by default
# shipping_address_collection: NOT set (no shipping address ever)
# phone_number_collection: NOT set
```
`customer_update` is not passed, so Checkout does not save an address to the Customer. In the Stripe Dashboard Customer Portal settings, "Customers can update: billing address / shipping address" is turned OFF (Eric does this during Stripe setup; Dashboard step, not code). Stripe Tax is not enabled (it would need an address). Webhook handlers must not copy `customer_details.address` into Firestore; grep at implementation: `git grep -n "customer_details" numista_backend` must show no address writes. TEST-14 added.

### 7.5 Receipt / invoice scans [R6: M6]
This plan adds no upload path and no scan storage. The rule "receipt scans have the person's name and ship-to address redacted automatically before storage; the raw scan is never stored" is owned by NET-718 R4 SEC-1/SEC-2. The privacy text in §7.2/§7.3 must not claim redaction until NET-718 R4 ships; until then it says nothing about scans beyond the current Gemini sentence.
## 8. Verbatim Code Citations Checked Against `origin/dev`

All citations below have been verified verbatim against `origin/dev` (commit `32d4b42e`):

### Citation 1: `numista_mobile/web/index.html` lines 113–121
```html
  </script>

</head>
<body>
  <noscript>
    <div style="padding: 20px; text-align: center; font-family: sans-serif;">
      <h1>Numista.AI -- AI-Powered Coin Collection Manager</h1>
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
      path.startsWith('/claim') || // L5: reserved -- falls through to home, not NotFoundScreen
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
        // Fallback for non-web (desktop/mobile) -- redirect flow
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
*Note [MF5]:* Line 71 `success_url` will be modified [NEW WORK] to append `&session_id={CHECKOUT_SESSION_ID}` so the client can query `/api/stripe/verify-session`.

### Citation 7: `numista_mobile/lib/services/stripe_service.dart` lines 10–20
```dart
  /// Launches Stripe Checkout for Pro ($4.99/mo) or Estate ($29/yr) subscription tiers.
  /// Sends the Firebase Bearer token -- the server reads user identity from the token.
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

### Citation 9: `numista_backend/tier_gatekeeper.py` lines 132–156 (Legacy Cutoff Definition) [MF2]
```python
def get_user_tier(user_profile: dict) -> str:
    """Resolves subscription tier (stripe_tier -> tier -> beta/lifetime flags -> 'free').

    Beta access NEVER expires on the server -- the cutoff (accounts created before
    2026-11-26T05:00Z) is enforced on the client by account creationTime.
    The server treats beta_tester=True as permanent family_estate regardless of any
    beta_access_expires field written by the Aug 2026 backfill script.
    """
    if user_profile.get("is_lifetime_family_estate") or user_profile.get("is_ai_qc_account"):
        return "family_estate"
    if user_profile.get("beta_tester"):
        return "family_estate"  # permanent -- do NOT check beta_access_expires

    # Also grant beta tier if account was created before the Facebook ad launch (1795669200000 ms epoch)
    creation_ts = user_profile.get('creation_timestamp')
    if creation_ts is not None:
        try:
            if int(creation_ts) < 1795669200000:
                return 'family_estate'
        except (ValueError, TypeError):
            pass
```

---

## 9. Test Verification Protocol & Acceptance Criteria [MF1, MF3, MF4, SF5, SF-B]

| Test ID | Objective | Procedure | Expected Result | Pass Criteria |
|---|---|---|---|---|
| **TEST-01** | Domain Verification Tag Static Presence [SF-B] | Run `curl -s https://numista-vault--p7-gate-*.web.app/ \| grep facebook-domain-verification` (and on live after deploy) | Tag string present verbatim in `<head>` | Exit 0, exact content match |
| **TEST-02** | Meta Pixel Base Snippet Static Presence [SF-B] | Run `curl -s https://numista-vault--p7-gate-*.web.app/ \| grep -E '2540753249725498\|fbevents.js'` (and on live after deploy) | Base snippet and `<noscript>` image present | Exit 0, exact dataset ID match |
| **TEST-03** | PageView Single Fire on Load | Load site in browser with Meta Pixel Helper extension | Exactly 1 `PageView` recorded on initial load | Zero double-fire on first render |
| **TEST-04** | PageView Incremental Navigation | Navigate from `/` to `/pricing`, then to `/about` | Exactly +1 `PageView` fired per navigation | Router observer suppresses initial route, logs on changes |
| **TEST-05** | CompleteRegistration on Email Signup | Complete new email registration with unique test address | Exactly 1 `CompleteRegistration` fired | Fired on server success |
| **TEST-06** | CompleteRegistration on Google Signup | Sign up with new Google account (`isNewUser == true`) | Exactly 1 `CompleteRegistration` fired | Fired on server success |
| **TEST-07** | Returning User No-Fire Verification | Sign in with existing Google account (`isNewUser == false`) | Zero `CompleteRegistration` fired | Helper skipped |
| **TEST-08** | Failed Signup No-Fire Verification | Submit invalid signup form (e.g., weak pin, existing email) | Zero `CompleteRegistration` fired | Helper skipped |
| **TEST-09** | Demo Vault No-Fire Verification | Click "Try It Free" and explore Demo Vault | Zero `CompleteRegistration` fired | Helper skipped |
| **TEST-10** | InitiateCheckout Verification | Click "Upgrade" on pricing tier to trigger checkout session | Exactly 1 `InitiateCheckout` fired on session URL receipt | Fired before `launchUrl` |
| **TEST-11** | Purchase Verification & Server Amount [R6] | Complete test Stripe payment; land on `/#/settings?stripe=success&session_id=cs_test_...` | `hashQuery()` returns the `cs_test_` id; verify-session returns paid; exactly 1 `Purchase` with server `amount_total/100` | Unit test on `hashQuery()` + Pixel Helper shows 1 event |
| **TEST-11b** | verify-session ownership [R6] | User B calls verify-session with User A's session id; also unauthenticated call | B: 404 `Not found` (same body as a fake id); unauthenticated: 401/403 | No amount or status leaked |
| **TEST-14** | No address in Checkout [R6] | Create a test-mode session; `stripe checkout sessions retrieve` | `shipping_address_collection` null; `billing_address_collection` "auto"; no street-address field shown on page | Pass |
| **TEST-12** | Real 404 Verification (Unknown Paths) | Request `https://numista.ai/us-coins` and `https://numista.ai/zzz-unknown?utm_source=meta` | HTTP status 404 returned | Real 404 response (no soft-404) |
| **TEST-13** | UTM Preservation (Known Routes) | Request `https://numista.ai/?utm_source=meta&utm_campaign=thanksgiving` and `https://numista.ai/pricing?utm_source=meta&fbclid=abc` | HTTP status 200 returned; UTM and `fbclid` query params intact | Query params preserved in app state |

---

## 10. Execution Gates & Sign-Off Workflow

1. **Gate 1 (Plan Scoring):** Grok CoS score $\ge 95/100$ and Argon (SAG Auditor) score $\ge 95/100$.
2. **Gate 2 (Executive Approval):** Explicit typed `YES` from Founder Eric, plus Eric confirms: §5.2 figures (incl. $109/$150), the UNVERIFIED rows, §5.3 mapping, and the §5.4 cutoff date.
3. **Gate 3 (Staged Implementation):** Implementation on branch `p7-v8.9`, local verification (`flutter analyze`, `pytest numista_tests/test_set_pricing.py`).
4. **Gate 4 (Preview Verification):** Deployment to Firebase Hosting preview channel `p7-gate` (`https://numista-vault--p7-gate-*.web.app`). Full execution of Tests 01–14 incl. 11b.
5. **Gate 5 (Production Release):** Verification report submitted to Founder Eric. Live merge from `p7-v8.9` to `origin/dev`, and from `dev` to `origin/main` strictly upon Eric's final typed `YES`. Live Stripe activation unlocked only after end-to-end sandbox verification.

---
**END PLAN NET-706 R6**