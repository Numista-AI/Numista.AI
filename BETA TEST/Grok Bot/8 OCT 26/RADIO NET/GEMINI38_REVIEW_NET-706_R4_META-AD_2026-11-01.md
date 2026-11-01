# GEMINI 3.8 TECHNICAL & SAG AUDIT — PRELAUNCH_PLAN_NET-706_R4_META-AD_20261101.md

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor, THINKING/PLANNING/REVIEW ONLY)
- **Date:** 2026-11-01
- **Target Plan:** `PRELAUNCH_PLAN_NET-706_R4_META-AD_20261101.md` (Authored by AG CoS v4 `ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Authoritative Spec & Score Baseline:**
  - `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` (`NET-709A`)
  - `COS_SCORE_NET-706-R3_93_REVISE_20261101-1625EST.md` (`NET-716`)
  - `RADIO_OVER_NET-714A_GROKDESK-to-ALL_ERIC-DECISIONS_20261101-1602.md` (`NET-714A`)
  - `WAKE_AG-COS-V4_NET-716_NET-706-R4-FIX-ONLY_20261101.md` (`NET-716`)
- **Compliance Rule:** `GEMINI.md` Rule 6(a) — Every `file:line` citation below pastes the exact verbatim code lines checked against `origin/dev` (`32d4b42e`).
- **Role / Governance Lock:** Strict review-only (`NO EXECUTE`, zero code edits, zero git commits/pushes, zero deploys, Stripe stays OFF).

---

## 1. Executive Summary & Score Table

`PRELAUNCH_PLAN_NET-706_R4_META-AD_20261101.md` is a **99/100 PASS (Gate 1 Ready — Ready for Grok CoS Re-Score & SAG Concurrence)**.

Every item from Grok CoS Score 93 (`COS_SCORE_NET-706-R3_93_REVISE_20261101-1625EST.md`) and Eric's binding `NET-714A` decisions (`RADIO_OVER_NET-714A_GROKDESK-to-ALL_ERIC-DECISIONS_20261101-1602.md`) is resolved:
1. **`MF-A` (Privacy Policy Harmonization & Extension — 15/15 PASS):** Section 7 quotes the exact existing lines at `numista_mobile/lib/screens/privacy_screen.dart:139` (`"No data is shared with third-party advertisers."`) and `numista_mobile/web/privacy.html:325` (`"...share your personal data with third-party advertisers or marketers."`) and provides harmonized `BEFORE`/`AFTER` replacements that extend Section 4 and Section 3 without adding duplicate sections, explicitly preserve `"We do not sell, rent, or trade..."`, codify zero home-address collection (`NET-714A`), and eliminate the contradiction with the Meta Pixel disclosure.
2. **`SF-D` (`firebase.json` Route List — 9/10 PASS, -1 minor line-offset note):** Section 4.2 lists all 17 actual rewrite sources (`/privacy`, `/terms`, `/about`, `/pricing`, `/features`, `/faq`, `/login`, `/reset-password`, `/signup`, `/demo`, `/`, `/index.html`, `/wishlist`, `/wishlist/**`, `/attorney_portal`, `/claim`, `/claim/**`), notes that `/app` and `/blog` are 301 redirects outside the rewrite block, and notes that there is no `/attorney` rewrite (it is `/attorney_portal`). *(Minor 1-point pedantic note: in `firebase.json`, each `"source"` line is 2 lines below the number listed in Section 4.2's sub-bullets — e.g., `/privacy` is on line 66, `/about` on line 74, `/attorney_portal` on line 122, `/claim/**` on line 130 — while the overall block range `64–133` and the verbatim Citation 4 block `125–135` are exact.)*
3. **Three Settled `NET-714A` Decisions (PASS):** Zero `[ERIC DECISION]` markers remain (`text.count('ERIC DECISION') == 0`):
   - Privacy disclosure + zero home-address collection settled in Section 7 (`lines 288–328`).
   - Legacy cutoff settled at `2026-11-26T05:00:00Z` (`1795669200000` ms) in Section 5.1 (`line 238`).
   - Free-tier full export settled at `$95.94` in Section 5.1 (`line 237`).
4. **Byte-Exact Meta Pixel Block (20/20 PASS):** Confirmed `664 bytes`, SHA-256 `8436041c6ce5ca6dc9345dae3381a7a968187a245582539585c8bc32edfa2f49`.

| Rubric Dimension (Matching Grok CoS R3 Rubric) | Weight | R3 Score (Grok CoS) | R4 Score (Argon) | Verdict & Rationale |
|---|---:|---:|---:|---|
| **1. Accuracy / No Invention** | 30 | 30 / 30 | **30 / 30** | **PASS:** Zero invented files, zero fake quotes, all `[NEW WORK]` and proposed `lookup_key` labels intact. |
| **2. Pixel Snippet & 404 / UTM Handling** | 20 | 20 / 20 | **20 / 20** | **PASS:** 664-byte pixel block byte-identical (`8436041c...2f49`); real HTTP 404 preserved; UTM/`fbclid` preserved. |
| **3. Pricing v3.2, 13 Stripe Prices & Settled `NET-714A` Decisions** | 15 | 15 / 15 | **15 / 15** | **PASS:** All 13 prices match v3.2; Free export `$95.94` and Legacy cutoff `2026-11-26T05:00:00Z` stated as settled (`0` `[ERIC DECISION]` markers left). |
| **4. Privacy Policy Integration (`MF-A`)** | 15 | 10 / 15 | **15 / 15** | **PASS (`MF-A` Fixed):** Exact `BEFORE`/`AFTER` shown for `privacy_screen.dart:139` and `web/privacy.html:325`; extends existing Section 4 & Section 3; removes `"third-party advertisers"` contradiction; codifies zero home-address collection. |
| **5. Line Citations (`SF-D` & Section 8)** | 10 | 8 / 10 | **9 / 10** | **PASS (`SF-D` Fixed):** All 17 actual `firebase.json` rewrite routes listed; `/app` & `/blog` noted as 301 redirects; `/attorney_portal` noted (`-1` only because the sub-bullet line numbers in Section 4.2 are offset by 2 lines inside `64–133`, e.g., `:72` vs `:74` for `/about`). |
| **6. Test Plan & Gate Discipline** | 10 | 10 / 10 | **10 / 10** | **PASS:** `TEST-01`–`TEST-13` target `p7-gate` preview channel first, then production post-deploy after Eric's typed `YES`. |
| **TOTAL** | **100** | **93 / 100** | **99 / 100** | **PASS — GATE 1 READY (`>= 95/100`)** |

---

## 2. Verbatim Code Verification of `MF-A` (`privacy_screen.dart:139` & `web/privacy.html:325`)

### 2.1 [`numista_mobile/lib/screens/privacy_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/privacy_screen.dart#L137-L152) (`lines 137–152`, specifically `line 139`)
- **Verbatim Code on `origin/dev` (`32d4b42e`):**
  ```dart
                      _SectionHeader(title: '4. Sharing Your Information'),
                      Text(
                        'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
                        style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                      ),
                      SizedBox(height: 10),
                      _BulletPoint(
                        boldText: 'Global Reference Library Index: ',
                        text: 'If you explicitly opt-in to contribute images, your anonymized coin photos (stripped of all user identifiers, costs, and personal notes) are hosted in our public reference library bucket on Google Cloud Storage to populate the canonical catalog for all users.',
                      ),
                      SizedBox(height: 8),
                      _BulletPoint(
                        boldText: 'Affiliate Integration Partners: ',
                        text: 'When viewing or interacting with your collection wishlist, the Service integrates with the eBay Partner Network (EPN) to surface live product availability cards. Interacting with these features utilizes standard affiliate tracking identifiers to manage campaign routing, strictly isolated from your personal estate data.',
                      ),
                      SizedBox(height: 20),
  ```
- **Verification of `R4` Section 7.2 (`lines 297–309`):**
  - `R4` quotes `line 139` before and after, extending Section 4 in-place, preserving `"We do not sell, rent, or trade..."`, adding the zero home-address collection principle, adding the Meta Pixel (`Dataset ID: 2540753249725498`) disclosure, and replacing `"No data is shared with third-party advertisers."` with `"Beyond this campaign measurement, no personal data is shared with third-party advertisers or marketers."`
  - *(Implementation note for Gate 3: when editing `privacy_screen.dart:139` in Dart, escape internal apostrophes as `\'` — i.e., `collection\'s` and `Google Cloud\'s` — or wrap the Dart string literal in double quotes `"..."`.)*

### 2.2 [`numista_mobile/web/privacy.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/privacy.html#L313-L333) (`lines 313–333`, specifically `line 325`)
- **Verbatim Code on `origin/dev` (`32d4b42e`):**
  ```html
              <h2>3. How We Use Your Information</h2>
              <p>We use the information we collect to operate, maintain, and improve our services, specifically:</p>
              <ul>
                  <li><strong>Collection Syncing:</strong> To upload microscope captures and automatically log coin records to your personal "My Collection" database.</li>
                  <li><strong>AI Numismatic Identification:</strong> To send captured coin images to our secure AI processing pipeline (using Google Cloud's Gemini enterprise platform) to identify the coin's type, year, mint mark, and die varieties.</li>
                  <li><strong>Third-Party Database Enrichment:</strong> To query numismatic databases (such as PCGS) using identified attributes to retrieve structural values, melt estimates, and historical data.</li>
                  <li><strong>Estate Planning PDF Generation:</strong> To process your estate profile, collection inventory, and beneficiary allocations to compile legal estate reports and tangible personal property memoranda.</li>
                  <li><strong>Direct Sharing Facilitation:</strong> To generate local email layout templates and clipboard text packages allowing you to quickly share your downloaded inventory directly with your legal counsel via your own email client.</li>
                  <li><strong>Service Diagnostics:</strong> To troubleshoot hardware connection issues, optimize camera autofocus/manual-focus calculations, and improve the accuracy of our visual classification models.</li>
              </ul>

              <h2>4. Sharing Your Information</h2>
              <p>We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
              <ul>
  ```
- **Verification of `R4` Section 7.3 (`lines 310–328`):**
  - `R4` quotes `line 325` verbatim (`BEFORE`) and provides the harmonized `AFTER` paragraph extending Section 4 (`line 325`) plus a bullet in Section 3 (`<ul>` at `lines 315–322`), with zero contradiction and explicit zero home-address collection.

---

## 3. Verbatim Code Verification of `SF-D` (`numista_mobile/firebase.json`)

- **Verbatim Code on `origin/dev` (`32d4b42e`), [`numista_mobile/firebase.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firebase.json#L22-L134) (`lines 22–32` and `lines 65–133`):**
  ```json
        {
          "source": "/app",
          "destination": "/",
          "type": 301
        },
        {
          "source": "/blog",
          "destination": "/about",
          "type": 301
        },
  ```
  ```json
        {
          "source": "/privacy",
          "destination": "/privacy.html"
        },
        {
          "source": "/terms",
          "destination": "/terms.html"
        },
        {
          "source": "/about",
          "destination": "/index.html"
        },
        {
          "source": "/pricing",
          "destination": "/index.html"
        },
        {
          "source": "/features",
          "destination": "/index.html"
        },
        {
          "source": "/faq",
          "destination": "/index.html"
        },
        {
          "source": "/login",
          "destination": "/index.html"
        },
        {
          "source": "/reset-password",
          "destination": "/index.html"
        },
        {
          "source": "/signup",
          "destination": "/index.html"
        },
        {
          "source": "/demo",
          "destination": "/index.html"
        },
        {
          "source": "/",
          "destination": "/index.html"
        },
        {
          "source": "/index.html",
          "destination": "/index.html"
        },
        {
          "source": "/wishlist",
          "destination": "/index.html"
        },
        {
          "source": "/wishlist/**",
          "destination": "/index.html"
        },
        {
          "source": "/attorney_portal",
          "destination": "/index.html"
        },
        {
          "source": "/claim",
          "destination": "/index.html"
        },
        {
          "source": "/claim/**",
          "destination": "/index.html"
        }
      ],
  ```
- **Verification of `R4` Section 4.2 (`lines 178–200`):**
  - Lists all 2 static HTML rewrites (`/privacy`, `/terms`) and all 15 SPA index rewrites (`/about`, `/pricing`, `/features`, `/faq`, `/login`, `/reset-password`, `/signup`, `/demo`, `/`, `/index.html`, `/wishlist`, `/wishlist/**`, `/attorney_portal`, `/claim`, `/claim/**`), clarifies `/app` and `/blog` are 301 redirects, and clarifies `/attorney_portal` (no `/attorney` rewrite in `firebase.json`).

---

## 4. Verbatim Code Verification of All Remaining Citations in `R4`

1. **[`numista_mobile/web/index.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/index.html#L113-L121) (`lines 113–121`):**
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
2. **[`numista_mobile/lib/main.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart#L119-L149) (`lines 119–149`):**
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
3. **[`numista_mobile/lib/services/auth_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/auth_service.dart#L130-L160) (`lines 130–160`):**
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
4. **[`numista_backend/tier_gatekeeper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L41-L50) (`lines 41–50`) and (`lines 132–156`):**
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
5. **[`numista_backend/routes/payment_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L65-L75) (`lines 65–75`):**
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
6. **[`numista_mobile/lib/services/stripe_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/stripe_service.dart#L10-L20) (`lines 10–20`):**
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
7. **[`numista_mobile/lib/screens/base_layout.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/base_layout.dart#L52-L60) (`lines 52–60`) and (`lines 1538–1543`):**
   ```dart
   class BaseLayout extends StatefulWidget {
     final bool isDemoMode;
     const BaseLayout({super.key, this.isDemoMode = false});

     @override
     State<BaseLayout> createState() => _BaseLayoutState();
   }

   class _BaseLayoutState extends State<BaseLayout> {
   ```
   ```dart
               const Expanded(
                 child: Text(
                   "You're browsing a read-only demo. Create a free account to add coins, use the scanner, and save your collection.",
                   style: TextStyle(color: Colors.white, fontSize: NumistaTheme.textCaption),
                 ),
               ),
   ```
8. **[`numista_mobile/lib/screens/login_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L1387-L1391) (`line 1388`) and [`numista_mobile/lib/screens/public_info_screens.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/public_info_screens.dart#L361-L409) (`lines 362, 407`):**
   ```dart
                     Text(
                       'Create a free account to track your collection, log values, and export estate plans.',
                       style: TextStyle(color: _isDark ? Colors.white70 : const Color(0xFF5A5C69), fontSize: NumistaTheme.textBodySm),
                       textAlign: TextAlign.center,
                     ),
   ```
   ```dart
                     Text(
                       'Free During Beta — Pricing TBA',
                       style: TextStyle(
                         color: isDark ? Colors.white : const Color(0xFF1A1C24),
   ```
   ```dart
                     Text(
                       'Numista.AI is currently in open public beta. During this phase, collection tracking, AI photo identification, and market value estimates are completely free for registered participants.',
                       textAlign: TextAlign.center,
                       style: TextStyle(
   ```

---

## 5. Final Sign-Off Verdict

- **Argon Technical & SAG Audit Score:** **99 / 100 PASS (Gate 1 Cleared)**
- **Next Gate:** Grok CoS Re-Score ($\ge 95/100$) $\rightarrow$ Standalone Grok (SAG) Concurrence $\rightarrow$ Founder Eric's Typed `YES`.
