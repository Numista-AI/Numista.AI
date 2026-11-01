# GEMINI 3.8 TECHNICAL & SAG AUDIT — PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor, THINKING/PLANNING/REVIEW ONLY)
- **Date:** 2026-11-01
- **Target Plan:** `PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md` (Authored by AG CoS v4 `ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Authoritative Spec & Score Baseline:**
  - `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` (`NET-709A`)
  - `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md` (`NET-712`)
  - `RADIO_OVER_NET-712A_GROKDESK-to-ALL_SF6-AGE-83_20261101-1517.md` (`NET-712A`)
  - `COS_SCORE_NET-706-R2_84_REVISE_20261101-1541EST.md` (`NET-714`)
- **Compliance Rule:** `GEMINI.md` Rule 6(a) — Every `file:line` citation below pastes the exact verbatim code lines checked against `origin/dev` (`32d4b42e`).
- **Role / Governance Lock:** Strict review-only (`NO EXECUTE`, zero code edits, zero git commits/pushes, zero deploys, Stripe stays OFF).

---

## 1. Executive Summary & Score Table

`PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md` is a **100/100 PASS (Gate 1 Ready — Awaiting Grok CoS Re-Score & Eric's Typed `YES`)**.

All 5 MUST-FIX items (`MF1`–`MF5`) and all 3 SHOULD-FIX items (`SF-A`, `SF-B`, `SF-C`) from Grok CoS Score 84 (`COS_SCORE_NET-706-R2_84_REVISE_20261101-1541EST.md`), as well as all prior `R1` items (`MF1`–`MF8`, `SF1`–`SF7`), are **100% resolved** with zero fabricated files, zero fabricated string citations, and 100% verified line numbers on `origin/dev` (`32d4b42e`).

| Rubric Dimension | Weight | R1 Score | R2 Score | R3 Score | Verdict & Rationale |
|---|---:|---:|---:|---:|---|
| **1. Exact Tag & Pixel Snippet (`NET-709A` Reqs 1 & 2)** | 20 | 12 / 20 | 20 / 20 | **20 / 20** | **PASS:** Both `<meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />` and the 17-line Meta Pixel Base Code (`2540753249725498`) are byte-identical (`664 bytes`, SHA-256 `8436041c6ce5ca6dc9345dae3381a7a968187a245582539585c8bc32edfa2f49`). |
| **2. Event Rules (`PageView`, `CompleteRegistration`, `InitiateCheckout`, `Purchase`)** | 20 | 11 / 20 | 17 / 20 | **20 / 20** | **PASS (`MF5` Fixed):** Single-load `PageView` + router-observer guard (`_initialPageViewLogged`); `CompleteRegistration` gated on server success (`createUserWithEmailAndPassword` / `isNewUser == true` + `meta_pixel_registered_<uid>`); `InitiateCheckout` before `launchUrl`; `Purchase` explicitly labels `payment_routes.py:71` (`&session_id={CHECKOUT_SESSION_ID}`) and `/api/stripe/verify-session` as `[NEW WORK]`. |
| **3. Soft-404 & UTM Audit (`firebase.json` + `main.dart`)** | 10 | 3 / 10 | 10 / 10 | **10 / 10** | **PASS (`SF-C` Fixed):** Preserves explicit rewrites in `numista_mobile/firebase.json:64-133` with zero `**` wildcard catch-all; preserves real HTTP 404 on unknown paths and retains `utm_*`/`fbclid` query parameters on valid routes. |
| **4. Pricing v3.2 + 13 Stripe Prices + Export Rules + Legacy Cutoff** | 15 | 6 / 15 | 11 / 15 | **15 / 15** | **PASS (`MF1`, `MF2`, `MF5`, `SF-A` Fixed):** Eliminated nonexistent `snapshot_legacy.py`; cites actual `tier_gatekeeper.py:41-50` (`"free": 20` legacy code vs 10-item Plan v3.2 policy); cites actual legacy cutoff in `tier_gatekeeper.py:132-156` (`1795669200000` ms = `2026-11-26T05:00:00Z`) and flags `[ERIC DECISION - 26 Nov vs 27 Nov cutoff]`; labels all 13 Stripe identifiers as proposed `lookup_key` values; flags Free tier export price as `[ERIC DECISION]`. |
| **5. Copy Audit ("5 Free Coins" Drift + Privacy Disclosure)** | 10 | 4 / 10 | 6 / 10 | **10 / 10** | **PASS (`MF3`, `MF4` Fixed):** Verifies exact line numbers on `origin/dev` (`32d4b42e`): `login_screen.dart:1388`, `public_info_screens.dart:362` & `407`, `base_layout.dart:1540`. Targets `privacy.html` and `privacy_screen.dart:137-152` with the exact sentence from Eric's spec (`NET-709A` Req 5) and marks broader pledges `[ERIC DECISION]`. |
| **6. Unified Homepage Scope Line (Placeholder)** | 5 | 2 / 5 | 5 / 5 | **5 / 5** | **PASS:** Marked `[PLACEHOLDER - Eric picks final wording: ...]`. |
| **7. Verbatim Code Citations (`GEMINI.md` Rule 6(a))** | 10 | 8 / 10 | 5 / 10 | **10 / 10** | **PASS (`MF1`–`MF5` Fixed):** All 9 code blocks in Section 8 and all inline line-number references in Sections 3–7 match `origin/dev` (`32d4b42e`) verbatim. |
| **8. Gate Discipline & Lock Hygiene** | 10 | 10 / 10 | 10 / 10 | **10 / 10** | **PASS (`SF-B`, `SF6`, `SF7` Fixed):** `origin/main = 9f04550a`, `origin/dev = 32d4b42e`, `p7-gate` tested before production (`SF-B`), age 35–65+ / readable to age 83 (`SF6`), station ID `ba2bfdb2` (`SF7`). |
| **TOTAL** | **100** | **56 / 100** | **84 / 100** | **100 / 100** | **PASS — GATE 1 READY (NO EXECUTE UNTIL GROK COS >= 95 & ERIC'S TYPED `YES`)** |

---

## 2. Point-by-Point Verification of R2 -> R3 Fixes (`MF1`–`MF5` & `SF-A`–`SF-C`)

### 2.1 `MF1` — Zero Fabricated Files or Fake Code Claims (RESOLVED)
- **Requirement:** Delete nonexistent `numista_backend/scripts/snapshot_legacy.py` and do not claim `tier_gatekeeper.py` currently says `"max_items: 10"`.
- **R3 Resolution (`PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md:204, 221, 259-260, 386-398`):**
  - `snapshot_legacy.py` is completely removed.
  - Section 5.1 (`line 204`), Section 6.1 (`lines 259-260`), and Section 8 Citation 5 (`lines 386-398`) quote the real code in [`numista_backend/tier_gatekeeper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L41-L50) and clearly distinguish current legacy code (`"free": 20`) from Plan v3.2 policy (`10 items` at Paid Tier launch):
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

### 2.2 `MF2` — Code-Level Legacy Cutoff Timestamp (RESOLVED)
- **Requirement:** Cite the actual legacy cutoff in `numista_backend/tier_gatekeeper.py:136, 145, 149` (`1795669200000` ms = `2026-11-26T05:00:00Z`) and mark `26 Nov vs 27 Nov` as `[ERIC DECISION]`.
- **R3 Resolution (`PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md:221, 445-468`):**
  - Section 5.1 (`line 221`) and Section 8 Citation 9 (`lines 445-468`) paste the exact function from [`numista_backend/tier_gatekeeper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L132-L156) and mark `[ERIC DECISION - 26 Nov vs 27 Nov cutoff]`:
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

### 2.3 `MF3` — Exact Line Numbers for Trial / Beta Copy Citations (RESOLVED)
- **Requirement:** Cite the real line numbers on `origin/dev` (`32d4b42e`) for `login_screen.dart`, `public_info_screens.dart`, and `base_layout.dart`.
- **R3 Resolution (`PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md:248-260`):**
  1. [`numista_mobile/lib/screens/login_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L1387-L1391) (`line 1388`):
     ```dart
                       Text(
                         'Create a free account to track your collection, log values, and export estate plans.',
                         style: TextStyle(color: _isDark ? Colors.white70 : const Color(0xFF5A5C69), fontSize: NumistaTheme.textBodySm),
                         textAlign: TextAlign.center,
                       ),
     ```
  2. [`numista_mobile/lib/screens/public_info_screens.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/public_info_screens.dart#L361-L364) (`line 362`) and (`lines 406-409`, `line 407`):
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
  3. [`numista_mobile/lib/screens/base_layout.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/base_layout.dart#L1538-L1543) (`line 1540`):
     ```dart
               const Expanded(
                 child: Text(
                   "You're browsing a read-only demo. Create a free account to add coins, use the scanner, and save your collection.",
                   style: TextStyle(color: Colors.white, fontSize: NumistaTheme.textCaption),
                 ),
               ),
     ```

### 2.4 `MF4` — Privacy Policy Target File & Plain-Language Disclosure (RESOLVED)
- **Requirement:** Use the exact plain-language sentence from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` Req 5, target `numista_mobile/web/privacy.html` and `numista_mobile/lib/screens/privacy_screen.dart:137-152`, and mark any broader non-sale commitment as `[ERIC DECISION]`.
- **R3 Resolution (`PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md:271-278`):**
  - Targets [`numista_mobile/web/privacy.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/privacy.html#L194-L202) and [`numista_mobile/lib/screens/privacy_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/privacy_screen.dart#L137-L152):
    ```dart
                      _Section(
                        number: '3',
                        title: 'How We Use Your Information',
                        isDark: isDark,
                        body:
                            'We use the information we collect strictly to provide, maintain, and improve the Numista.AI service:\n\n'
                            '• Authenticate your access and secure your vault.\n'
                            '• Synchronize your collection inventory across your authorized devices.\n'
                            '• Process AI coin identification, grading assistance, and valuation queries.\n'
                            '• Generate downloadable reports, spreadsheets, and estate planning documents at your request.\n'
                            '• Maintain system security, monitor API quotas, and prevent abuse.',
                      ),
    ```
  - Uses the exact spec sentence and marks `"We do not sell..."` as `[ERIC DECISION - privacy commitment]`.

### 2.5 `MF5` — Stripe `Purchase` Plumbing Marked `[NEW WORK]` & Proposed `lookup_key` Values (RESOLVED)
- **Requirement:** Label `/api/stripe/verify-session` and the `session_id` addition to `success_url` in `numista_backend/routes/payment_routes.py:71` as `[NEW WORK]`, and label the 13 Stripe identifiers as proposed `lookup_key` values.
- **R3 Resolution (`PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md:144-156, 223-242, 400-415`):**
  - Quotes [`numista_backend/routes/payment_routes.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L65-L75) (`line 71`) verbatim and marks both the `success_url` change (`&session_id={CHECKOUT_SESSION_ID}`) and `/api/stripe/verify-session` as `[NEW WORK]`:
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
  - Labels all 13 identifiers in Table 5.2 (`copper_monthly`, `copper_annual`, etc.) as **Proposed Stripe `lookup_key`** values.

### 2.6 `SF-A`, `SF-B`, `SF-C` — All Three Should-Fix Items Resolved
- **`SF-A` (`line 220`):** Free Tier Export is explicitly flagged `[ERIC DECISION - Free tier export price: $95.94 Gold baseline vs other]`.
- **`SF-B` (`lines 476-477`):** `TEST-01` and `TEST-02` run against the Firebase preview channel `p7-gate` (`https://numista-vault--p7-gate-*.web.app/`) first, and against live `https://numista.ai/` only post-deploy after Eric's typed `YES`.
- **`SF-C` (`lines 178-183, 369-384`):** Explicitly cites [`numista_mobile/firebase.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firebase.json#L64-L133) (`lines 64-133`):
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

---

## 3. Verification of All Remaining Verbatim Citations in `R3` Section 8

1. **[`numista_mobile/web/index.html`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/web/index.html#L113-L121) (`lines 113-121`):**
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
2. **[`numista_mobile/lib/main.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart#L119-L149) (`lines 119-149`):**
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
3. **[`numista_mobile/lib/services/auth_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/auth_service.dart#L130-L160) (`lines 130-160`):**
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
4. **[`numista_mobile/lib/services/stripe_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/stripe_service.dart#L10-L20) (`lines 10-20`):**
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
5. **[`numista_mobile/lib/screens/base_layout.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/base_layout.dart#L52-L60) (`lines 52-60`):**
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

## 4. Final Sign-Off Verdict

- **Argon Technical & SAG Audit Score:** **100 / 100 PASS (Gate 1 Cleared by Argon)**
- **Next Gate:** Grok CoS Re-Score ($\ge 95/100$) $\rightarrow$ Founder Eric's Open Decisions (`[ERIC DECISION]` items) & Typed `YES` before any code execution.
