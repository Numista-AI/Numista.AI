# GEMINI 3.8 TECHNICAL REVIEW — `PRELAUNCH_PLAN_NET-706_META-AD_20261101.md` (`NET-706` / `NET-711` / `NET-712`)

- **Reviewer:** `Argon` (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)
- **Plan Under Review:** `PRELAUNCH_PLAN_NET-706_META-AD_20261101.md` (filed by `AG CoS v4` — Station ID `ba2bfdb2-b91e-4444-80bb-bc4a82ff528e` / `ba2bfdb2`)
- **Authoritative Spec & Score References:**
  - `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` (`NET-709A`)
  - `WAKE_AG-COS-V4_NET-706_META-AD-PRELAUNCH-PLAN_20261101.md` (`NET-706`)
  - `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md` (Grok CoS Score: **55/100 — REVISE**)
  - `WAKE_AG-COS-V4_NET-712_NET-706-R2-FIX-ONLY_20261101.md` & `RADIO_OVER_NET-712A_GROKDESK-to-ALL_SF6-AGE-83_20261101-1517.md`
- **Timestamp:** `2026-11-01 15:22 EST`
- **Mode:** `THINKING / PLANNING / REVIEW ONLY` (`NO EXECUTE` — Zero code edits, zero git commits/pushes, zero deploys, Stripe OFF)
- **Active Locks:** `origin/main` frozen at `9f04550a`; `origin/dev` tip at `32d4b42e` (catalog frozen at `9b55f3d9`); `origin/p7-v8.9` at `38699700`; Stripe OFF (`$0` live charges until Eric's typed `YES` before 26 Nov 2026).

---

## 1. Executive Verdict & Score Alignment

- **Argon Technical Score:** **56 / 100 — REVISE** (Concurring with Grok CoS Score **55 / 100 — REVISE** in `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md`).
- **Station ID Correction (`SF7`):** `AG CoS v4` station of record is confirmed as **`ba2bfdb2-b91e-4444-80bb-bc4a82ff528e`** (`ba2bfdb2`). Argon has updated all headers and routing references accordingly.
- **Why R1 Requires Revision (`PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md`):**
  1. **`MF1` (Soft-404 Regression):** `PRELAUNCH_PLAN_NET-706_META-AD_20261101.md` Section 5.2 & Section 8.4 propose adding `{"source": "**", "destination": "/index.html"}` to `numista_mobile/firebase.json` and redirecting unknown paths (`default:`) to the homepage in `numista_mobile/lib/main.dart`. That **creates** soft-404s where the live site currently returns a real HTTP 404 (`404.html` / `NotFoundScreen`).
  2. **`MF2` (Meta Pixel Snippet Modified):** Requirement 2 of `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` states: *"Add the following code, completely unchanged (including the `<noscript>` part), inside the `<head>` of every page of the site"*. R1 altered the HTML comment (`<!-- Meta Pixel Code (Authoritative NET-709A) -->`) and indentation.
  3. **`MF3` (`PageView` Double-Fire on Initial Load):** The base snippet in `<head>` already calls `fbq('track', 'PageView');` on initial page load. Firing `MetaPixelService.trackPageView()` unconditionally on `BaseLayout` initial route load without skipping the initial load causes 2 `PageView` events on landing.
  4. **`MF4` (`CompleteRegistration` Deduplication & Shared Helper):** `CompleteRegistration` must use a single shared helper with a per-UID idempotency guard (`SharedPreferences` + Firestore `users/{uid}.meta_registration_tracked == true`) called only after confirmed new-account creation (`createAccount` success or `signInWithPopup` where `cred.additionalUserInfo?.isNewUser == true`), never on failed signup or returning Google login.
  5. **`MF5` & `MF6` (Invented Export Price & Invented Stripe SKUs):** R1 invented `$4.99` Free export and invented Rows 11–13 (`$49.00 Estate Valuation`, `$3.99 Family Seat`, `$9.99 30-Day AI Pass`) and mislabeled Row 9 (`$5.00` per 1,000 items) as "Storage" instead of AI Top-Up. Per Plan v3.2, Full Data Export is **6 months of the user's plan** (`$95.94` for never-paid Legacy = `6 × $15.99`), and any unconfirmed Stripe rows must be marked `[TBD by Eric]` rather than invented.
  6. **`MF7` (Fabricated `"Start with 5 free coins"` Quote + Missed Real Trial/Beta Strings):** R1 claimed `"Start with 5 free coins"` existed in `lib/screens/login_screen.dart`. Repo-wide grep confirms that string does **not** exist anywhere in `numista_mobile/lib/` or `numista_mobile/web/`. Below in Section 2, Argon provides the **exact verbatim `file:line` citations** for all real Beta/Trial strings in the repository (`public_info_screens.dart:359-415`, `home_dashboard.dart:565-591`, `beta_welcome_dialog.dart:91-106`, and `tier_gatekeeper.py:41-50, 132-157`).
  7. **`MF8` (Homepage Scope Line Placeholder):** R1 presented two different final hero strings in Section 1 vs Section 4. Must use a single unified placeholder marked `[PLACEHOLDER - Eric picks final wording]`.
  8. **`MF9` (Annual Savings Column Math):** Platinum `$109.00/yr` vs `12 × $10.99 = $131.88/yr` is `17.35%` (`$22.88`), not `"2 mos free"`; Gold `$150.00/yr` vs `12 × $15.99 = $191.88/yr` is `21.83%` (`$41.88`). Either state exact dollar/percentage savings or drop the column.
  9. **`SF1`–`SF7` + `NET-712A` (Age 83 Readability):**
     - `SF1`: Keep `"Lifetime — ON HOLD"` and remove `"$500"` (`$500` vs `$1,500` unresolved).
     - `SF2`: `Purchase` `value` must come from server/webhook-confirmed Stripe `amount_total / 100.0` (with `session_id` deduplication), never unverified client-side plan constants or URL spoofing.
     - `SF3`: Restate locks (`origin/main = 9f04550a`, `origin/dev tip = 32d4b42e`, catalog frozen at `9b55f3d9`, execute on `p7-v8.9`, test on `p7-gate`, merge `dev -> main` only on separate typed `YES`).
     - `SF4`: Quote the actual Legacy cutoff from `numista_backend/tier_gatekeeper.py:135-150` (`beta_tester == True` or `creation_timestamp < 1795669200000` / `2026-11-26T05:00:00Z`), not `"prior to October 2026"`.
     - `SF5`: Add unit test verifying `InitiateCheckout` fires once per click after checkout URL is received and before `launchUrl`.
     - `SF6` (`NET-712A` Resolution): Per Eric's instruction (*"My Aunt is 83, so bump it up to that"*), Meta ad setting stays `35–65+` (Meta platform max) and creative/landing copy must be readable for collectors up to **age 83** (large type, high contrast, plain English).

---

## 2. Verbatim Code Citations Audited Against `origin/dev` (`32d4b42e`) — Rule 6(a) Compliance

Every file and line range below was read directly from the workspace (`origin/dev` `32d4b42e`) and is pasted verbatim. `AG CoS v4 (ba2bfdb2)` may copy these citations directly into `PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md`.

### 2.1 `numista_mobile/web/index.html` (Lines 110–119) — Static `<head>` & `<body>` Boundary
- **File:** [`numista_mobile/web/index.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/index.html#L110-L119)
```html
110:       document.addEventListener('keydown', unlockAudio, { capture: true, once: true });
111:     })();
112:   </script>
113:   <!-- Build version: 2026-04-17T06:00Z — P4.4R cache-control split + SW kill-switch -->
114:   <meta name="build-version" content="2026-04-17T06:00Z">
115: </head>
116: <body>
117:   <!-- Loading indicator while Flutter initializes -->
118:   <div class="loading" id="loading">
119:     <div class="spinner"></div>
```

### 2.2 `numista_mobile/web/privacy.html` (Lines 1–15 & Lines 324–333) — Static Privacy Page `<head>` & Section 4 Sharing
- **File:** [`numista_mobile/web/privacy.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/privacy.html#L1-L15)
```html
1: <!DOCTYPE html>
2: <html lang="en">
3: <head>
4:     <meta charset="UTF-8">
5:     <meta name="viewport" content="width=device-width, initial-scale=1.0">
6:     <title>Privacy Policy — Numista.AI</title>
7:     <link rel="canonical" href="https://numista.ai/privacy.html">
8:     <link rel="icon" type="image/png" href="favicon.png">
9:     <!-- Google Fonts -->
10:     <link rel="preconnect" href="https://fonts.googleapis.com">
11:     <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
12:     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;800;900&display=swap" rel="stylesheet">
```
- **File:** [`numista_mobile/web/privacy.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/privacy.html#L324-L333)
```html
324:             <h2>4. Sharing Your Information</h2>
325:             <p>We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
326:             <ul>
327:                 <li><strong>Cloud Infrastructure Providers:</strong> Your account details, coin collection, and estate profiles are stored securely on <strong>Google Firebase</strong> (Google Cloud Firestore and Google Cloud Storage).</li>
328:                 <li><strong>Global Reference Library Index:</strong> If you explicitly opt-in to contribute images, your anonymized coin photos (stripped of all user identifiers, costs, and personal notes) are hosted in our public reference library bucket on Google Cloud Storage to populate the canonical catalog for all users.</li>
329:                 <li><strong>AI and Numismatic Enrichment Partners:</strong> Scanned images are transmitted securely to <strong>Google Cloud's Gemini enterprise platform</strong> (via the Google Gen AI SDK) for image classification, structural analysis, and variety detection. Because we utilize Google Cloud's enterprise infrastructure, your uploaded images and metadata are strictly protected under enterprise data governance policies and are <strong>never</strong> used by Google to train public machine learning models. Coin metadata is sent to PCGS APIs to retrieve coin records. These partners do not use your data for any purposes outside of performing these services for Numista.AI.</li>
330:                 <li><strong>Affiliate Integration Partners:</strong> When viewing or interacting with your collection wishlist, the Service integrates with the <strong>eBay Partner Network (EPN)</strong> to surface live product availability cards. Interacting with these features utilizes standard affiliate tracking identifiers to manage campaign routing, strictly isolated from your personal estate data.</li>
331:                 <li><strong>Legal Compliance:</strong> We may disclose your information if required to do so by law or in the good faith belief that such action is necessary to comply with a legal obligation, protect our rights, or prevent fraud.</li>
332:             </ul>
```
- **Audit Note on `privacy.html`:** Requirement 5 of `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` adds the Meta Pixel sentence to Section 3/4, AND line 325 (`"We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers"`) must be qualified so it does not contradict the Meta Pixel disclosure: *"We do not sell, rent, or trade your personal collection data or estate records. For website campaign measurement, we use Meta Pixel (ID 2540753249725498) to log standard conversion events (PageView, CompleteRegistration, Purchase) as described below; your private vault inventory, coin photos, and estate planning records are never shared with Meta."*

### 2.3 `numista_mobile/lib/screens/privacy_screen.dart` (Lines 137–152) — In-App Flutter Privacy Screen
- **File:** [`numista_mobile/lib/screens/privacy_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/privacy_screen.dart#L137-L152)
```dart
137:                     _SectionHeader(title: '4. Sharing Your Information'),
138:                     Text(
139:                       'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
140:                       style: TextStyle(color: _text, fontSize: 14, height: 1.5),
141:                     ),
142:                     SizedBox(height: 10),
143:                     _BulletPoint(
144:                       boldText: 'Global Reference Library Index: ',
145:                       text: 'If you explicitly opt-in to contribute images, your anonymized coin photos (stripped of all user identifiers, costs, and personal notes) are hosted in our public reference library bucket on Google Cloud Storage to populate the canonical catalog for all users.',
146:                     ),
147:                     SizedBox(height: 8),
148:                     _BulletPoint(
149:                       boldText: 'Affiliate Integration Partners: ',
150:                       text: 'When viewing or interacting with your collection wishlist, the Service integrates with the eBay Partner Network (EPN) to surface live product availability cards. Interacting with these features utilizes standard affiliate tracking identifiers to manage campaign routing, strictly isolated from your personal estate data.',
151:                     ),
```
- **Audit Note on `privacy_screen.dart`:** Clicking `"Privacy"` in the footer of `LoginScreen` (`login_screen.dart:576-580`) opens `PrivacyScreen` (`privacy_screen.dart`). Therefore, `privacy_screen.dart:139-151` MUST also be updated to replace `'No data is shared with third-party advertisers.'` and add the exact Meta Pixel bullet (`"We use Meta Pixel (ID 2540753249725498) to measure ad performance and log page views, sign-ups, and purchases. You can opt out via your browser settings or Meta Ad Preferences."`).

### 2.4 `numista_mobile/lib/main.dart` (Lines 119–150) & `numista_mobile/firebase.json` (Lines 125–140) — Real 404 + UTM Preservation (`MF1`)
- **File:** [`numista_mobile/lib/main.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart#L119-L150)
```dart
119:       onGenerateRoute: (settings) {
120:         final rawName = settings.name ?? '/';
121:         final uri = Uri.tryParse(rawName);
122:         final path = (uri?.path.isEmpty ?? true) ? '/' : uri!.path;
123:         final qp = uri?.queryParameters ?? const <String, String>{};
124:         final isDemoParam = qp['demo'] == '1' || qp['demo'] == 'true';
125: 
126:         switch (path) {
127:           case '/':
128:             return MaterialPageRoute(
129:               settings: settings,
130:               builder: (_) => AuthGate(isDemo: isDemoParam),
131:             );
132:           case '/demo':
133:             return MaterialPageRoute(
134:               settings: settings,
135:               builder: (_) => const AuthGate(isDemo: true),
136:             );
137:           case '/login':
138:           case '/signin':
139:             return MaterialPageRoute(
140:               settings: settings,
141:               builder: (_) => const AuthGate(initialAuthTab: 0),
142:             );
143:           case '/signup':
144:           case '/register':
145:             return MaterialPageRoute(
146:               settings: settings,
147:               builder: (_) => const AuthGate(initialAuthTab: 1),
148:             );
149:           case '/reset-password':
150:           case '/forgot-password':
```
- **File:** [`numista_mobile/lib/main.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart#L161-L177)
```dart
161:           case '/about':
162:           case '/features':
163:           case '/pricing':
164:           case '/faq':
165:             return MaterialPageRoute(
166:               settings: settings,
167:               builder: (_) => AuthGate(publicRoute: path),
168:             );
169:           default:
170:             return MaterialPageRoute(
171:               settings: settings,
172:               builder: (_) => NotFoundScreen(attemptedPath: path),
173:             );
174:         }
175:       },
```
- **File:** [`numista_mobile/firebase.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firebase.json#L125-L140)
```json
125:       {
126:         "source": "/pricing",
127:         "destination": "/index.html"
128:       },
129:       {
130:         "source": "/faq",
131:         "destination": "/index.html"
132:       },
133:       {
134:         "source": "/404",
135:         "destination": "/index.html"
136:       }
137:     ]
138:   }
139: }
```
- **How `R2` Must Fix `MF1`:**
  - **DO NOT** add `{"source": "**", "destination": "/index.html"}` to `firebase.json` and **DO NOT** change `default: NotFoundScreen(attemptedPath: path)` in `main.dart:169-173`!
  - Why: Firebase Hosting already serves `index.html` (HTTP 200) for `/`, `/about`, `/features`, `/pricing`, `/faq`, `/login`, `/signup`, `/demo`, etc., WITH all query parameters (`?utm_source=meta&utm_medium=paid_social&utm_campaign=...&fbclid=...`) intact in `window.location.search` (which `fbevents.js` reads directly from `window.location.href`), while returning a real HTTP 404 (`404.html`) for unknown paths like `/us-coins` or `/unknown-sub-route`!
  - In `main.dart:120-124`, `settings.name` on Flutter Web hash/path routing preserves `settings` on `MaterialPageRoute(settings: settings, ...)`, and for `default:` (`main.dart:169-173`), `NotFoundScreen(attemptedPath: path)` renders the 404 UI for any unknown in-app route. Adding a small non-destructive UTM/fbclid capture helper (`MetaPixelService.captureLandingParams(Uri.base)`) on startup preserves UTM parameters across in-app tab changes without touching `firebase.json` rewrites or breaking real 404s.

### 2.5 `numista_mobile/lib/services/auth_service.dart` (Lines 133–166) — `CompleteRegistration` Hooks (`MF4`)
- **File:** [`numista_mobile/lib/services/auth_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/auth_service.dart#L133-L166)
```dart
133:       // Ensure user document has email and role so admin stats & rules work
134:       await _db.collection('users').doc(cred.user!.uid).set({
135:         'email': email.trim(),
136:         'display_name': displayName.trim(),
137:         'role': 'collector',
138:         'created_at': FieldValue.serverTimestamp(),
139:       }, SetOptions(merge: true));
140: 
141:       return AuthResult.ok();
142:     } on FirebaseAuthException catch (e) {
143:       return AuthResult.fail(_friendlyError(e.code));
144:     } catch (e) {
145:       return AuthResult.fail('Account creation failed: $e');
146:     }
147:   }
148: 
149:   /// Sign in with Google (Popup on Web, Redirect on mobile/desktop)
150:   static Future<AuthResult> signInWithGoogle() async {
151:     try {
152:       final googleProvider = GoogleAuthProvider();
153:       if (kIsWeb) {
154:         await _auth.signInWithPopup(googleProvider);
155:       } else {
156:         await _auth.signInWithRedirect(googleProvider);
157:       }
158:       return AuthResult.ok();
159:     } on FirebaseAuthException catch (e) {
160:       return AuthResult.fail(_friendlyError(e.code));
161:     } catch (e) {
162:       return AuthResult.fail('Google Sign-In failed: $e');
163:     }
164:   }
```

### 2.6 Real Beta/Trial Copy in Repository (`MF7` Resolution — Replacing Fabricated `"Start with 5 free coins"`)
Repo-wide grep confirms `"Start with 5 free coins"` does **not** exist anywhere in `numista_mobile/lib/` or `numista_mobile/web/`. The actual files and lines containing Beta/Trial copy that must be updated for Scope 3 (`"30-day no-card full trial, then Free tier (10 items)"`) are:

1. **[`numista_mobile/lib/screens/public_info_screens.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/public_info_screens.dart#L351-L423) (Lines 351–423, `_PricingView`):**
```dart
351: class _PricingView extends StatelessWidget {
352:   const _PricingView();
353: 
354:   @override
355:   Widget build(BuildContext context) {
356:     return Column(
357:       crossAxisAlignment: CrossAxisAlignment.start,
358:       children: [
359:         _tagBadge('BETA PRICING'),
360:         const SizedBox(height: 12),
361:         const Text(
362:           'Free During Beta — Pricing TBA',
363:           style: TextStyle(
364:             color: Color(0xFF0F172A),
365:             fontSize: 32,
366:             fontWeight: FontWeight.bold,
367:             height: 1.25,
368:           ),
369:         ),
...
406:               const Text(
407:                 'Numista.AI is currently in open public beta. During this phase, collection tracking, AI photo identification, and market value estimates are completely free for registered participants.',
408:                 style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
409:               ),
410:               const SizedBox(height: 16),
411:               const Text(
412:                 'Long-term pricing and plans will be announced prior to general release. Existing beta accounts will be grandfathered—you will not be asked to pay for your active beta access.',
413:                 style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
414:               ),
```

2. **[`numista_mobile/lib/screens/home_dashboard.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/home_dashboard.dart#L564-L592) (Lines 564–592, Home Dashboard Top Banner):**
```dart
564:                                       children: [
565:                                         const Text('👋 Welcome Beta Tester!',
566:                                             style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
567:                                         Container(
568:                                           padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
569:                                           decoration: BoxDecoration(
570:                                             color: const Color(0xFF166534),
571:                                             borderRadius: BorderRadius.circular(4),
572:                                           ),
573:                                           child: const Text('FOUNDING BETA ⭐ FREE FOREVER',
574:                                               style: TextStyle(color: Color(0xFF86EFAC), fontSize: 9, fontWeight: FontWeight.bold)),
575:                                         ),
576:                                       ],
577:                                     )
578:                                   : Row(
579:                                       children: [
580:                                         const Text('👋 Welcome Beta Tester!',
581:                                             style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
582:                                         const SizedBox(width: 8),
583:                                         Container(
584:                                           padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
585:                                           decoration: BoxDecoration(
586:                                             color: const Color(0xFF166534),
587:                                             borderRadius: BorderRadius.circular(4),
588:                                           ),
589:                                           child: const Text('FOUNDING BETA ⭐ FREE FOREVER',
590:                                               style: TextStyle(color: Color(0xFF86EFAC), fontSize: 9, fontWeight: FontWeight.bold)),
591:                                         ),
592:                                       ],
```

3. **[`numista_mobile/lib/widgets/beta_welcome_dialog.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/beta_welcome_dialog.dart#L90-L107) (Lines 90–107, Auto-Popup Welcome Modal):**
```dart
90:               // Title
91:               Text(
92:                 'Welcome, Beta Tester! 👋🎉',
93:                 style: TextStyle(
94:                   color: text,
95:                   fontSize: 24,
96:                   fontWeight: FontWeight.bold,
97:                 ),
98:               ),
99:               const SizedBox(height: 8),
100:               Text(
101:                 'Founding Beta Member — Free Forever ⭐',
102:                 style: TextStyle(
103:                   color: sub,
104:                   fontSize: 13,
105:                   fontWeight: FontWeight.w500,
106:                 ),
107:               ),
```
- **Why #2 and #3 Are Critical for Scope 3:** Unless gated by the Legacy cutoff (`beta_tester == true` or `user.metadata.creationTime < DateTime.utc(2026, 11, 26, 5, 0)`), every new user arriving from the Nov 26 Meta Ad campaign who signs up for the `"30-day no-card full trial, then Free tier (10 items)"` will immediately see `'FOUNDING BETA ⭐ FREE FOREVER'` on `HomeDashboard` (`home_dashboard.dart:573, 589`) and `BetaWelcomeDialog` (`beta_welcome_dialog.dart:101`). For post-cutoff accounts, that badge/subtitle must display `'30-DAY FULL TRIAL • NO CARD REQUIRED (THEN FREE TIER: 10 ITEMS)'`, while Legacy pre-Facebook Beta accounts continue to see `'FOUNDING BETA ⭐ FREE FOREVER'`.

### 2.7 `numista_mobile/lib/screens/login_screen.dart` (Lines 303–316 & Lines 395–418) — Homepage Scope Placeholder (`MF8`) & Public Pages Audit (`Scope 5`)
- **File:** [`numista_mobile/lib/screens/login_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L303-L316)
```dart
303:                                     Text(
304:                                       'NUMISTA.AI',
305:                                       style: TextStyle(
306:                                         color: _text,
307:                                         fontSize: 24,
308:                                         fontWeight: FontWeight.w900,
309:                                         letterSpacing: 1.5,
310:                                       ),
311:                                     ),
312:                                     Text(
313:                                       'AI-Powered Coin Collection Manager',
314:                                       style: TextStyle(color: _sub, fontSize: NumistaTheme.textBodySm),
315:                                     ),
```
- **File:** [`numista_mobile/lib/screens/login_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L395-L418)
```dart
395:             const Text(
396:               'NUMISTA.AI',
397:               style: TextStyle(
398:                 color: _text,
399:                 fontSize: 40,
400:                 fontWeight: FontWeight.w900,
401:                 letterSpacing: 2,
402:               ),
403:             ),
404:             const SizedBox(height: 6),
405:             const Text(
406:               'AI-Powered Coin Collection Manager',
407:               style: TextStyle(color: _sub, fontSize: 16),
408:             ),
409:             const SizedBox(height: 32),
410: 
411:             // Feature bullets
412:             ...const [
413:               ('🤖', 'AI-estimated values for every coin in your collection'),
414:               ('📊', 'Organize thousands of coins instantly'),
415:               ('📋', 'Estate documentation, reports, and lateral transfer'),
416:               ('💬', 'Morgan AI numismatic assistant — research any coin'),
417:               ('🧑‍🏫', 'Human AI Trainer Review Board — community-powered accuracy'),
418:             ].map((f) => Padding(
```

### 2.8 `numista_backend/tier_gatekeeper.py` (Lines 41–50 & Lines 132–158) — Legacy Beta Cutoff (`SF4`) & Tier Limits
- **File:** [`numista_backend/tier_gatekeeper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L41-L50)
```python
41: TIER_COIN_LIMITS = {
42:     "free": 20,
43:     "pro": 100,
44:     "numismatist": 250,
45:     "dealer": 500,
46:     "estate": 1000,
47:     "family_estate": 2500,
48:     "sovereign": float("inf"),
49:     "power_user": float("inf"),
50: }
```
- **File:** [`numista_backend/tier_gatekeeper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L132-L158)
```python
132: def get_user_tier(user_profile: dict) -> str:
133:     """Resolves subscription tier (stripe_tier -> tier -> beta/lifetime flags -> 'free').
134: 
135:     Beta access NEVER expires on the server — the cutoff (accounts created before
136:     2026-11-26T05:00Z) is enforced on the client by account creationTime.
137:     The server treats beta_tester=True as permanent family_estate regardless of any
138:     beta_access_expires field written by the Aug 2026 backfill script.
139:     """
140:     if user_profile.get("is_lifetime_family_estate") or user_profile.get("is_ai_qc_account"):
141:         return "family_estate"
142:     if user_profile.get("beta_tester"):
143:         return "family_estate"  # permanent — do NOT check beta_access_expires
144: 
145:     # Also grant beta tier if account was created before the Facebook ad launch (1795669200000 ms epoch)
146:     creation_ts = user_profile.get('creation_timestamp')
147:     if creation_ts is not None:
148:         try:
149:             if int(creation_ts) < 1795669200000:
150:                 return 'family_estate'
151:         except (ValueError, TypeError):
152:             pass
153: 
154:     tier = user_profile.get("stripe_tier") or user_profile.get("tier")
155:     if tier:
156:         return str(tier).lower().strip()
157:     return "free"
```

### 2.9 `numista_backend/routes/payment_routes.py` (Lines 47–75 & Lines 220–226) & `numista_mobile/lib/services/stripe_service.dart` (Lines 13–45) — `InitiateCheckout` (`SF5`) & Server-Confirmed `Purchase` (`SF2`)
- **File:** [`numista_backend/routes/payment_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L47-L75)
```python
47:         user_uid = _user.get("uid") or _user.get("user_id") or ""
48:         user_email = (_user.get("email") or "").strip().lower()
49:         tier = req.tier.lower()
50:         unit_amount = 2900 if tier in ["estate", "family_estate"] else 499
51:         interval = "year" if tier in ["estate", "family_estate"] else "month"
52:         
53:         session = stripe.checkout.Session.create(
54:             payment_method_types=['card'],
55:             mode='subscription',
56:             customer_email=user_email,
57:             client_reference_id=user_uid,
58:             allow_promotion_codes=True,
59:             line_items=[{
60:                 'price_data': {
61:                     'currency': 'usd',
62:                     'product_data': {
63:                         'name': f"Numista.AI {req.tier.capitalize()} Tier Subscription",
64:                         'description': "AI Grading, Unlimited Checklists & Legal Estate Suite"
65:                     },
66:                     'unit_amount': unit_amount,
67:                     'recurring': {'interval': interval}
68:                 },
69:                 'quantity': 1,
70:             }],
71:             success_url="https://numista.ai/#/settings?stripe=success",
72:             cancel_url="https://numista.ai/#/settings?stripe=cancel",
73:             metadata={"user_uid": user_uid, "target_tier": tier}
74:         )
75:         return {"checkout_url": session.url, "session_id": session.id}
```
- **File:** [`numista_backend/routes/payment_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L220-L226)
```python
220:         if event_type in ["checkout.session.completed", "customer.subscription.updated", "invoice.paid"]:
221:             tier_val = data_obj.get("metadata", {}).get("target_tier", "pro")
222:             update_payload["stripe_tier"] = tier_val
223:             update_payload["subscription_status"] = "active"
224:             update_payload["grace_period_until"] = None
225:             user_doc_ref.set(update_payload, merge=True)
226:             unlock_user_coins(target_id)
```
- **File:** [`numista_mobile/lib/services/stripe_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/stripe_service.dart#L13-L45)
```dart
13:   static Future<bool> launchCheckoutSession({
14:     required String userEmail,
15:     required String tier,
16:     http.Client? client,
17:   }) async {
18:     try {
19:       final response = await HttpAuthClient.post(
20:         Uri.parse('$_baseUrl/api/stripe/create-checkout-session'),
21:         client: client,
22:         body: jsonEncode({
23:           'tier': tier,
24:           // user_email kept for backwards compat — server should prefer token
25:           'user_email': userEmail,
26:         }),
27:       );
28: 
29:       if (response.statusCode == 200) {
30:         final data = jsonDecode(response.body);
31:         final urlString = data['checkout_url'] as String?;
32:         if (urlString != null && urlString.isNotEmpty) {
33:           final uri = Uri.parse(urlString);
34:           if (await canLaunchUrl(uri)) {
35:             await launchUrl(uri, mode: LaunchMode.externalApplication);
36:             return true;
37:           }
38:         }
39:       }
40:       return false;
41:     } catch (e) {
42:       debugPrint('[StripeService] Checkout session failed: $e');
43:       return false;
44:     }
45:   }
```

---

## 3. Turnkey R2 Resolution Blueprint for `AG CoS v4 (ba2bfdb2)` (`MF1`–`MF9` & `SF1`–`SF7`)

To achieve **$\ge 95/100$** on `PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md`, `AG CoS v4 (ba2bfdb2)` should incorporate the following exact fixes:

### Fix `MF1` — Real HTTP 404 for Unknown Paths + UTM/fbclid Preservation
- **Do NOT modify `numista_mobile/firebase.json`:** Keep `firebase.json` lines 125–138 unchanged (no `**` catch-all). Unknown URLs like `https://numista.ai/us-coins` or `https://numista.ai/unknown-sub-route?utm_source=meta` continue to return a real **HTTP 404** (`404.html`), while `https://numista.ai/?utm_source=meta&fbclid=IwAR...` and `https://numista.ai/pricing?utm_source=meta` return **HTTP 200** with query parameters intact in `window.location.search`.
- **Do NOT remove `NotFoundScreen` from `numista_mobile/lib/main.dart:169-173`:** Keep `default: return MaterialPageRoute(settings: settings, builder: (_) => NotFoundScreen(attemptedPath: path));`.

### Fix `MF2` — Byte-Verbatim Domain Tag & Meta Pixel Base Code (`NET-709A`)
Insert the exact lines from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` into `<head>` of `numista_mobile/web/index.html` (immediately above `</head>` at line 115) and `numista_mobile/web/privacy.html` (immediately above `</head>` at line 254), **completely unchanged** (zero comment edits, zero re-indentation):

```html
<meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />
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

### Fix `MF3` — Prevent `PageView` Double-Fire on Initial Load
- Because `index.html` already fires `fbq('track', 'PageView');` on initial page load, `MetaPixelService.trackPageView()` must skip the initial route load and fire **only on subsequent in-app route transitions**:
```dart
static bool _initialPageViewHandled = false;

static void onRouteChanged(String routeName) {
  if (!_initialPageViewHandled) {
    _initialPageViewHandled = true;
    return; // Base HTML snippet already fired the initial PageView on load
  }
  trackPageView();
}
```
- **Required Test:** Verify that initial app boot results in **0** extra Dart-triggered `PageView` calls (1 total from `<head>`), and each subsequent in-app navigation adds **+1** `PageView`.

### Fix `MF4` — Duplicate-Proof `CompleteRegistration` via Shared Helper
- Create a single shared helper `MetaPixelService.trackCompleteRegistrationOnce(String uid)` used by both `AuthService.createAccount()` (`auth_service.dart:141`) and `AuthService.signInWithGoogle()` (`auth_service.dart:154`, only when `cred.additionalUserInfo?.isNewUser == true`):
```dart
static final Set<String> _registeredUidsInMemory = <String>{};

static Future<void> trackCompleteRegistrationOnce(String uid) async {
  if (uid.isEmpty || _registeredUidsInMemory.contains(uid)) return;
  final prefs = await SharedPreferences.getInstance();
  final prefKey = 'meta_pixel_complete_reg_$uid';
  if (prefs.getBool(prefKey) == true) return;

  _registeredUidsInMemory.add(uid);
  await prefs.setBool(prefKey, true);
  _callFbq('track', 'CompleteRegistration');
}
```
- In `AuthService.signInWithGoogle()` (`auth_service.dart:153-155`):
```dart
      if (kIsWeb) {
        final cred = await _auth.signInWithPopup(googleProvider);
        if (cred.additionalUserInfo?.isNewUser == true && cred.user != null) {
          await MetaPixelService.trackCompleteRegistrationOnce(cred.user!.uid);
        }
      }
```
- **Required Tests:**
  1. Email signup success -> fires `CompleteRegistration` exactly once; calling `trackCompleteRegistrationOnce(uid)` a second time for the same `uid` (refresh/re-render) fires **nothing**.
  2. Failed email signup (`FirebaseAuthException`) -> fires **nothing**.
  3. Returning Google user (`isNewUser == false`) -> fires **nothing**.

### Fix `MF5`, `MF6`, `MF9`, `SF1`, `SF4` — Accurate Plan v3.2 Pricing Table, Savings Math, Legacy Rule & 13 Stripe Prices
- **Tier Matrix (`MF9` & `SF1`):**
  | Tier | Item Range | Monthly | Annual | Exact Annual Savings vs 12× Monthly |
  | :--- | :--- | :--- | :--- | :--- |
  | **Free** | `1 – 10 items` | `$0.00` | `$0.00` | — |
  | **Copper** | `11 – 100 items` | `$4.99 / mo` | `$49.99 / yr` | Save `$9.89/yr` (`16.5%`) |
  | **Silver** | `101 – 249 items` | `$8.99 / mo` | `$89.99 / yr` | Save `$17.89/yr` (`16.6%`) |
  | **Platinum** | `250 – 500 items` | `$10.99 / mo` | `$109.00 / yr` | Save `$22.88/yr` (`17.3%`) |
  | **Gold** | `501+ items` | `$15.99 / mo` | `$150.00 / yr` | Save `$41.88/yr` (`21.8%`) |
  | **Lifetime** | — | **ON HOLD** | **ON HOLD** | Price unresolved (`ON HOLD` — no price displayed) |
- **Plan v3.2 Rules (`MF5`, `SF4`):**
  - **Trial Copy:** `"30-day no-card full trial, then Free tier (10 items)"` everywhere.
  - **Guest / Demo Cap:** `5 items` max + `$0.10` AI allowance.
  - **Legacy Beta Grandfathering (`SF4`):** Per `numista_backend/tier_gatekeeper.py:135-150`, accounts with `beta_tester == True` or `creation_timestamp < 1795669200000` (`2026-11-26T05:00:00Z`, pre-Facebook ad launch) retain permanent Legacy unlimited access.
  - **Set Coin Weighting:** `1 set coin = 1/4 item` (`0.25` item toward tier item cap).
  - **First-Month AI Cap:** Enforced per Plan v3.2 on initial subscription month.
  - **AI Top-Ups (`MF6`):** `$5.00` per `1,000 items` (AI Top-Up Pack, **not** "Storage").
  - **Full Data Export Pricing (`MF5`):** Full data export costs **6 months of the user's plan** (`$95.94` for never-paid Legacy = `6 × $15.99`; `$29.94` Copper; `$53.94` Silver; `$65.94` Platinum; `$95.94` Gold).
- **13 Stripe Prices Table (`MF6`):**
  - Rows 1–8: Copper, Silver, Platinum, Gold × (Monthly, Annual) = 8 recurring subscription prices.
  - Row 9: AI Top-Up (`$5.00` per 1,000 items, one-time).
  - Row 10: Full Data Export — Never-Paid Legacy / Gold (`$95.94` = 6 months of `$15.99/mo`).
  - Rows 11–13: `[TBD by Eric — confirm whether Rows 11–13 are the remaining 3 tier-specific 6-month Full Data Export prices (Copper $29.94, Silver $53.94, Platinum $65.94) or other Plan v3.2 SKUs; zero invented SKUs]`.

### Fix `MF8` & `SF6` (`NET-712A`) — Single Homepage Scope Placeholder & Age-83 Readability
- **Single Homepage Scope Placeholder (`MF8`):**
  - `[PLACEHOLDER - Eric picks final wording]: "Modern U.S. Coins (1964–Present) in Public Beta — Classic U.S., Bullion & World Coins Coming Next"` (used identically in Section 1 and Section 4; no competing variations).
- **Age 35–65+ Targeting & Age-83 Readability (`SF6` / `NET-712A`):**
  - Per `RADIO_OVER_NET-712A_GROKDESK-to-ALL_SF6-AGE-83_20261101-1517.md` (Eric: *"My Aunt is 83, so bump it up to that"*): Meta ad targeting stays `35–65+` (Meta platform max), and all landing page/pricing/hero typography and copy must be designed for effortless readability up to **age 83** (minimum 16px body text on landing/pricing cards, high-contrast `#0F172A` on `#FFFFFF` / `#F8FAFC`, clear plain-English labels, zero tiny low-contrast disclaimers).

### Fix `SF2` & `SF5` — Server-Confirmed `Purchase` Value + `InitiateCheckout` Test
- **`InitiateCheckout` (`SF5`):** Fires in `StripeService.launchCheckoutSession()` (`stripe_service.dart:34`) only after HTTP 200 and non-empty `checkout_url`, immediately before `launchUrl()`, once per click.
- **`Purchase` (`SF2`):**
  - In `payment_routes.py:71`, set `success_url="https://numista.ai/#/settings?stripe=success&session_id={CHECKOUT_SESSION_ID}"`.
  - In `payment_routes.py:220-225`, when `checkout.session.completed` or `invoice.paid` is processed by the Stripe webhook, persist `"last_paid_session_id": data_obj.get("id")` and `"last_paid_amount_usd": round((data_obj.get("amount_total") or 0) / 100.0, 2)` on `users/{target_id}` and expose both in `/api/stripe/subscription-status`.
  - On `/#/settings?stripe=success&session_id=...`, the client queries `/api/stripe/subscription-status`, verifies `subscription_status == 'active'`, `last_paid_session_id == session_id`, `last_paid_amount_usd > 0`, and `SharedPreferences.getBool('meta_pixel_purchase_$session_id') != true`, then fires `fbq('track', 'Purchase', {value: lastPaidAmountUsd, currency: 'USD'})` and records `meta_pixel_purchase_$session_id = true`.

---

## 4. Summary Checklist for `PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md`
- [x] `MF1`: Keep `firebase.json` without `**` catch-all; keep `NotFoundScreen` in `main.dart`; unknown routes return real HTTP 404; valid routes keep UTM/`fbclid` params.
- [x] `MF2`: Paste Domain Verification `<meta>` tag and Meta Pixel base code (`2540753249725498`) byte-for-byte unchanged from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`.
- [x] `MF3`: Skip initial load in `MetaPixelService.onRouteChanged()` so `<head>` fires the sole initial `PageView` and SPA navigations add `+1` per navigation.
- [x] `MF4`: Deduplicate `CompleteRegistration` once per UID via shared helper; test failed signup (`0` fires) and returning Google user (`0` fires).
- [x] `MF5`: Full data export = 6 months of the user's plan (`$95.94` for never-paid Legacy).
- [x] `MF6`: Row 9 = AI Top-Up (`$5.00` / 1,000 items); no invented SKUs in Rows 11–13 (mark `[TBD by Eric]`).
- [x] `MF7`: Remove fabricated `"Start with 5 free coins"` quote; cite verbatim `public_info_screens.dart:359-415`, `home_dashboard.dart:565-591`, and `beta_welcome_dialog.dart:91-106`.
- [x] `MF8`: Single homepage scope placeholder marked `[PLACEHOLDER - Eric picks final wording]`.
- [x] `MF9`: Exact annual savings math in pricing table.
- [x] `SF1`–`SF7` + `NET-712A`: Lifetime `ON HOLD` (no `$500`), server-confirmed `Purchase` `amount_total`, restated git locks (`origin/dev` `32d4b42e`, catalog `9b55f3d9`, `origin/main` `9f04550a`), real Legacy cutoff (`tier_gatekeeper.py:135-150`), `InitiateCheckout` test, age-83 readability (`35-65+` Meta max per Eric's Aunt rule), and station ID `ba2bfdb2`.
