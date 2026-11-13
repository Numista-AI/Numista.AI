# ARGON (GEMINI 3.8) TECHNICAL & ARCHITECTURE PLAN REVIEW: `PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md` (`BATON_NET-807`)

- **Reviewer:** Argon — Gemini 3.8 Independent Technical & Architecture Auditor
- **Track / Baton:** `NET-801 v1.1` / `BATON_NET-807` (Soft-404 Elimination, Public Catalog Options A/B/C, Pricing Navigation Fix)
- **Target Plan Reviewed:** `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md` (161 lines)
- **Timestamp:** 2026-11-05 16:32 ET
- **Composite Score:** **97 / 100 (`PASS — 0 Blocking Plan Must-Fixes; 2 Non-Blocking Execution Safeguards EX-807-1 & EX-807-2 Logged`)**
- **Execution Posture:** **PLAN REVIEW ONLY** (`origin/main` locked at `9f04550a`, Stripe strictly OFF, zero code edits, zero deployments, zero Firestore writes/seeding)

---

## 1. Executive Verdict & Rubric Breakdown

`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md` resolves all **8 blocking must-fixes** from Grok Bot CoS (`COS_SCORE_NET-801_SOFT404-PUBLIC-CATALOG-PRICING_20261105.md` — CoS 78/95, SAG 52/68 FAIL on v1.0). It strikes the false HTTP 404 premise, rebases cleanly on `origin/dev`'s existing `CatalogBrowseScreen`, reconciles the `5,142` marketing claim to the verified `3,202` master US reference entries, deletes all unsourced statistics, defines Options A/B/C with a mandatory Founder Eric typed gate for all three options, enforces CDN CPG retail (`cpgRetail`) pricing + static OpenGraph tags for Meta's `facebookexternalhit` crawler, and fixes the `AuthGate` `/pricing` race condition + semantic `Link` DOM anchors.

| Rubric Dimension | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Rebase on Live `/catalog` HTTP 200 & `dev`'s `CatalogBrowseScreen` (Must-Fix #1)** | 20 | **20 / 20** | `§1` (lines 21–24) strikes the false HTTP 404 premise, acknowledges live `/catalog` returns HTTP 200 via SPA rewrite to `index.html`, and rebases on `origin/dev`'s existing `lib/screens/catalog/catalog_browse_screen.dart` (`18a8b8e5`) with zero duplicate screens. |
| **2. Catalog Census Reconciliation (`3,202` vs `5,142`) & Unsourced Stat Removal (Must-Fix #2 & #8)** | 20 | **20 / 20** | `§1` (lines 26–30) and `§2` (lines 57–74) reconcile `login_screen.dart:338, 466` (`5,142 Reference Coins`) to verified `3,202` master records (`2,965` coins + `181` notes + `56` medals in `entries_master_20261103.jsonl` and `docs/MISSING_IMAGES.csv`), remove `"World"` claims, and delete `99.4%`, `"5,000+ indexable pages"`, `"advisory board"`, `"Sheldon grading"`, `"100% Private & Secure"`, and `"Passport Protocol"`. |
| **3. Options A/B/C with Mandatory Founder Typed Gate & Public Surface Hygiene (Must-Fix #3, #4, #5)** | 20 | **20 / 20** | `§3` (lines 77–87) defines Options A, B, and C and requires Founder Eric to explicitly type `"Option A"`, `"Option B"`, or `"Option C"` + `"YES"` before any code change. `§4` (lines 91–103) enforces CDN CPG retail (`cpgRetail`) only, zero wholesale, zero user cost/ownership, AI images only in `ai_replica_images`, local SVG placeholders, and zero external hotlinks/outbound links. |
| **4. Static OpenGraph Meta Tags & `AuthGate` / Semantic `Link` Fix (Must-Fix #6 & #7)** | 25 | **24 / 25** | `§5.1` (lines 108–121) specifies static `<title>`, `<meta property="og:*">`, and `<link rel="canonical">` tags for `facebookexternalhit` and Googlebot. `§5.2` (lines 123–138) fixes `AuthGate` (`widgets/auth_gate.dart`) to honor `widget.publicRoute` across authenticated/unauthenticated sessions and wraps public links in Flutter's `Link` widget (`package:url_launcher/link.dart`). Logged `EX-807-1` (-1 pt) for self-hosted `og:image` fallback prior to bucket provisioning. |
| **5. Preview Channel, Rollback, `$25.00/mo` Cap & To-Be-Created Tests (Must-Fix #6)** | 15 | **13 / 15** | `§6` (lines 142–153) enforces `preview-net801`, inherits the `$25.00/mo` hard egress cap + `$20.00/mo` alert from `NET-808`, and explicitly marks `test/route_test.dart` and `test/auth_gate_test.dart` as to-be-created artifacts. Logged `EX-807-2` (-2 pts) to align `§6` line 147 rollback with `NET-808` `§9.A` (`git revert <execute-sha>` on `dev` rather than `9f04550a` checkout). |
| **TOTAL** | **100** | **97 / 100** | **PASS (`>= 95` Gate Met)** |

---

## 2. Rule 6(a) / `NET-767` Verbatim Code & Plan Verification (All Files Read via `read_file` in This Turn)

### 2.1 Homepage `5,142` Badge in `numista_mobile/lib/screens/login_screen.dart` — `PASS`
- **Verified in `numista_mobile/lib/screens/login_screen.dart:336-341` & `464-469`:**
  ```dart
  336:                                   _StatBadge(value: '100+', label: 'Coin\nTypes'),
  337:                                   _StatDivider(),
  338:                                   _StatBadge(value: '5,142', label: 'Reference\nCoins'),
  339:                                   _StatDivider(),
  340:                                   _StatBadge(value: 'AI+', label: 'Community\nVerified'),
  ...
  464:                   _StatBadge(value: '100+', label: 'Coin Types\nRecognized'),
  465:                   _StatDivider(),
  466:                   _StatBadge(value: '5,142', label: 'Reference\nCoins'),
  467:                   _StatDivider(),
  468:                   _StatBadge(value: 'AI+', label: 'Community\nVerified'),
  ```

### 2.2 `AuthGate` Authenticated Session Hijack on `/pricing` (`numista_mobile/lib/widgets/auth_gate.dart`) — `PASS`
- **Verified in `numista_mobile/lib/widgets/auth_gate.dart:97-106`, `124-126`, & `156-159`:**
  ```dart
  97:     return StreamBuilder<User?>(
  98:       stream: widget.authStream ?? FirebaseAuth.instance.authStateChanges(),
  99:       builder: (context, snapshot) {
  100:         // Still waiting for Firebase to initialise — show branded splash
  101:         if (snapshot.connectionState == ConnectionState.waiting) {
  102:           return _buildSplash();
  103:         }
  104: 
  105:         // Signed in -> show welcome screen on first launch, then main app
  106:         if (snapshot.hasData && snapshot.data != null) {
  ...
  124:           if (_welcomeDone) {
  125:             return const BaseLayout();
  126:           }
  ...
  156:         // 1. If public route requested, show PublicInfoShell
  157:         if (widget.publicRoute != null) {
  158:           return PublicInfoShell(targetRoute: widget.publicRoute!);
  159:         }
  ```

### 2.3 Known Path Allow-List (`numista_mobile/lib/main.dart`) & Static OG Meta Tags (`numista_mobile/web/index.html`) — `PASS`
- **Verified in `numista_mobile/lib/main.dart:119-148`:**
  ```dart
  119:   final isKnownPath = path.isEmpty ||
  120:       path == '/' ||
  121:       path == '/index.html' ||
  122:       normalizedPath == '/about' ||
  123:       normalizedPath == '/pricing' ||
  124:       normalizedPath == '/features' ||
  125:       normalizedPath == '/faq' ||
  ...
  142:   if (!isKnownPath) {
  143:     runApp(MaterialApp(
  144:       title: 'Numista.AI',
  145:       debugShowCheckedModeBanner: false,
  146:       home: NotFoundScreen(attemptedPath: path),
  147:     ));
  148:     return;
  149:   }
  ```
- **Verified in `numista_mobile/web/index.html:17-37`:**
  ```html
  17:   <title>Numista.AI — AI-Powered Coin Collection Manager</title>
  ...
  23:   <link rel="canonical" href="https://numista.ai/">
  ...
  28:   <meta property="og:type"        content="website">
  29:   <meta property="og:url"         content="https://numista.ai/">
  30:   <meta property="og:title"       content="Numista.AI — AI-Powered Coin Collection Manager">
  31:   <meta property="og:description" content="Numista.AI is an independent AI coin collection manager powered by Google Gemini AI (not affiliated with Numista.com).">
  32:   <meta property="og:image"       content="https://numista.ai/icons/Icon-512.png">
  ```

---

## 3. Non-Blocking Execution Safeguards (`EX-807-1` & `EX-807-2`)

1. **`EX-807-1` (Self-Hosted `og:image` Fallback Until `gs://numista-catalog-assets` Is Provisioned):**
   - `§5.1` line 116 specifies `<meta property="og:image" content="https://storage.googleapis.com/numista-catalog-assets/branding/og-catalog-preview.png" />`.
   - Since `gs://numista-catalog-assets` is scoped as *"to be provisioned by Cloud Infrastructure Owner"* in `FAILFIX_PLAN_NET-777_CATALOG_v1.5.md` (`§3.E` line 143), serve the static OpenGraph preview image from Firebase Hosting `'self'` (`https://numista.ai/icons/og-catalog-preview.png` or the existing verified `https://numista.ai/icons/Icon-512.png` at `numista_mobile/web/index.html:32`) until the bucket is provisioned, guaranteeing zero broken image previews in Meta Ads Manager.
2. **`EX-807-2` (Repo-Safe Rollback Alignment with `NET-808` `§9.A`):**
   - In `§6` line 147 (`Reversible cleanly via firebase.json rewrite configuration and git revert pinned to baseline commit 9f04550a`), align the `dev` code rollback command with `FAILFIX_PLAN_NET-777_CATALOG_v1.5.md` `§9.A` (lines 339–356): use `git revert <execute-sha>` to pre-execute `dev` SHA `18a8b8e5` + `firebase hosting:channel:delete preview-net801` (or `firebase hosting:clone`), rather than checking out `firebase.json` from `9f04550a` (which would drop `dev`'s +8 catalog hosting lines).

---

## 4. Proactive No-Silo Site & Product Observations (`RADIO_NET-790`)

1. **Per-Route Static HTML Pre-Rendering for `/catalog` and `/pricing` on Firebase Hosting:** Because Firebase Hosting serves `/catalog` and `/pricing` via the SPA rewrite `"source": "**", "destination": "/index.html"`, non-JS crawlers (`facebookexternalhit`) hitting `https://numista.ai/catalog` will receive the root `web/index.html` head tags unless either (a) root `web/index.html` includes the catalog description in its primary OG tags during the Thanksgiving campaign, or (b) the build script writes static `build/web/catalog/index.html` and `build/web/pricing/index.html` copies with route-specific `<title>`, `og:title`, `og:description`, `og:url`, and `canonical` tags before `firebase hosting:channel:deploy`. Generating `build/web/catalog/index.html` and `build/web/pricing/index.html` at build time is a zero-cost, 5-line post-build step that gives Meta's ad crawler exact per-route OG tags without Cloud Functions.
