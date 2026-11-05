# ARGON TECHNICAL REVIEW: Soft-404s, Public Catalog Decision & Pricing Button Plan (`NET-801`)

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)
- **Author Reviewed:** Antigravity CoS v4 (`ba2bfdb2`)
- **Timestamp:** 2026-11-05 1:56 PM ET
- **Reference Baton:** [`BATON_NET-801_ARGON_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_2026-11-05-1320.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-801_ARGON_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_2026-11-05-1320.md)
- **Target Document Audited in This Turn:**
  - [`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md) (lines 1–323)
- **Codebase Files Verified in This Turn:**
  - [`numista_mobile/firebase.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firebase.json) (lines 49–133)
  - [`numista_mobile/lib/main.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart) (lines 119–173, 288–296)
  - [`numista_mobile/lib/widgets/auth_gate.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/auth_gate.dart) (lines 105–160)
  - [`numista_mobile/lib/screens/login_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart) (lines 335–345, 410–472, 560–612, 688–725)
  - [`numista_mobile/lib/screens/public_info_screens.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/public_info_screens.dart) (lines 1–46)
- **Technical Score:** **96 / 100 (`PASS — 0 Blocking Must-Fixes; 3 Non-Blocking Execution Safeguards S404-1..S404-3 Logged`)**
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero source code changes, zero deploys, zero Firestore writes, Stripe OFF, `origin/main` locked at `9f04550a`.

---

## 1. Executive Summary & Scorecard

| Audit Dimension (`BATON_NET-801`) | Weight | Score | Verdict |
|---|---|---|---|
| **1. Soft-404 Root Cause Analysis & Routing Fix (`firebase.json`, `main.dart`, `WebRouteHelper`)** | 25 | **24 / 25** | **PASS** — Verified `/catalog` and `/catalog/**` omissions in `firebase.json:49-133` and `main.dart:119-141`, plus hardcoded `title: 'Numista.AI'` at `main.dart:291`. `WebRouteHelper` syncs `document.title` and `history.pushState`. Safeguard `S404-2` logged for non-JS crawler/Meta ad preview tags. |
| **2. Public Catalog 3 Architectural Proposals & Founder Eric Typed YES Gate** | 25 | **24 / 25** | **PASS** — Presents Option A (`/catalog` read-only view), Option B (Landing Page modal), and Option C (Copy alignment) with trade-off matrix (`PLAN_NET-801:135-169`) and strict Founder Eric typed YES gate. Safeguard `S404-3` logged to reconcile `5,142` vs `3,202` reference coins count. |
| **3. Pricing Button Malfunction Root Cause Analysis (`AuthGate` + `login_screen.dart`)** | 25 | **25 / 25** | **PASS** — Pinpoints both root causes: (1) `AuthGate` (`auth_gate.dart:106-159`) returns `BaseLayout()` when signed in before checking `widget.publicRoute`; (2) `_footerLink('Pricing', ...)` (`login_screen.dart:566, 585-609`) pushes an in-memory route without `history.pushState` or anchor semantics. |
| **4. Lower-Priority Collector UX Items (`AI+`, PIN/Password Toggle, Jargon, Footer Accessibility)** | 15 | **14 / 15** | **PASS** — Verified all 4 items in `login_screen.dart` (`lines 340, 468`, `lines 692, 721`, `lines 415-416`, and footer semantics) with concrete collector-friendly copy replacements. |
| **5. Machine-Checkable Verification Commands & Standing Locks** | 10 | **9 / 10** | **PASS** — Includes `flutter analyze`, `flutter test`, `curl -I`, and Playwright checks. Cross-branch safeguard `S404-1` logged for merging with `dev`'s `CatalogBrowseScreen`. |
| **TOTAL** | **100** | **96 / 100** | **PASS (Ready for Grok Bot CoS `95+` -> SAG -> Founder Eric Typed YES)** |

---

## 2. Task-by-Task Verbatim Audit (Rule 6a / `NET-767`)

### Task 1: Soft-404 Analysis & Routing Fix (`PASS`)

- **Codebase Verification of `firebase.json` Omission ([`numista_mobile/firebase.json:73-92, 113-133`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firebase.json#L73-L133)):**
  ```json
  73:       {
  74:         "source": "/about",
  75:         "destination": "/index.html"
  76:       },
  77:       {
  78:         "source": "/pricing",
  79:         "destination": "/index.html"
  80:       },
  81:       {
  82:         "source": "/features",
  83:         "destination": "/index.html"
  84:       },
  85:       {
  86:         "source": "/faq",
  87:         "destination": "/index.html"
  88:       },
  ...
  125:       {
  126:         "source": "/claim",
  127:         "destination": "/index.html"
  128:       },
  129:       {
  130:         "source": "/claim/**",
  131:         "destination": "/index.html"
  132:       }
  133:     ],
  ```
- **Codebase Verification of `isKnownPath` Omission & Hardcoded Title ([`numista_mobile/lib/main.dart:119-149, 290-292`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart#L119-L292)):**
  ```dart
  119:   final isKnownPath = path.isEmpty ||
  120:       path == '/' ||
  121:       path == '/index.html' ||
  122:       normalizedPath == '/about' ||
  123:       normalizedPath == '/pricing' ||
  124:       normalizedPath == '/features' ||
  125:       normalizedPath == '/faq' ||
  ...
  139:       path.startsWith('/scraper_dashboard') ||
  140:       path.startsWith('/api/');
  141: 
  142:   if (!isKnownPath) {
  143:     runApp(MaterialApp(
  144:       title: 'Numista.AI',
  145:       debugShowCheckedModeBanner: false,
  146:       home: NotFoundScreen(attemptedPath: path),
  147:     ));
  148:     return;
  149:   }
  ...
  290:         return MaterialApp(
  291:           title: 'Numista.AI',
  292:           debugShowCheckedModeBanner: false,
  ```
- **Plan Verification ([`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md:179-210`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md#L179-L210)):**
  ```markdown
  197: 3. **Dynamic Browser Title & History Sync:**
  198:    Introduce a unified helper `WebRouteHelper.updateRouteAndTitle(String route, String title)`:
  199:    - Sets `SystemChrome.setApplicationSwitcherDescription(ApplicationSwitcherDescription(label: title))` across platforms.
  200:    - On web (`kIsWeb`), updates `web.document.title = title` and calls `web.window.history.pushState(null, title, route)`.
  ```
- **Audit Finding:** The root-cause diagnosis is 100% accurate on branch `p7-v8.9` (`9948c519`): `/catalog` and `/catalog/**` are omitted from both `firebase.json` rewrites and `main.dart:isKnownPath`, while `MaterialApp(title: 'Numista.AI')` serves an identical document title across `/pricing`, `/about`, `/features`, and `/faq`.

---

### Task 2: Public Catalog Proposals & Founder Eric Typed YES Gate (`PASS`)

- **Codebase Verification of Front-Door `5,142 Reference Coins` Claim ([`numista_mobile/lib/screens/login_screen.dart:336-341, 464-469`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L336-L469)):**
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
- **Plan Verification of 3 Options & Eric Gate ([`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md:159-170, 323`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md#L159-L323)):**
  ```markdown
  159: | Dimension | Option A: Public Catalog (`/catalog`) | Option B: Landing Page Modal | Option C: Status Quo + Copy Update |
  ...
  166: | **Execution Requirement** | **Requires Founder Eric typed YES**. | **Requires Founder Eric typed YES**. | Standard plan cycle. |
  167: 
  168: > [!IMPORTANT]
  169: > **CoS Recommendation:** We strongly recommend **Option A**. Exposing `/catalog` as a public read-only view directly fulfills the promise of the front-door copy, resolves the `/catalog` 404, and gives Meta ad campaigns a legitimate destination for numismatic enthusiasts. Under Rule 7, no code will be deployed without Eric's explicit typed YES.
  ...
  323: - **Launch Gate:** No public catalog deployment or route modifications will be deployed without Founder Eric's explicit typed YES.
  ```
- **Audit Finding:** All 3 options (Option A: Public Read-Only Catalog at `/catalog`, Option B: Landing Page Quick-Search Modal, Option C: Status Quo + Copy Alignment) are clearly structured with UX, SEO/Meta Ads, privacy, backend load, and complexity trade-offs, and strictly gated on Founder Eric's typed **YES**.

---

### Task 3: Pricing Button Root Cause Analysis (`PASS`)

- **Codebase Verification of Root Cause 1 — `AuthGate` Session Hijack ([`numista_mobile/lib/widgets/auth_gate.dart:106-159`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/auth_gate.dart#L106-L159)):**
  ```dart
  106:         if (snapshot.hasData && snapshot.data != null) {
  ...
  116:           if (GuestSeedService.isBrowseDemoMode || _cachedDemoActive) {
  117:             return const BaseLayout(isDemoMode: true);
  118:           }
  ...
  124:           if (_welcomeDone) {
  125:             return const BaseLayout();
  126:           }
  ...
  145:               return const BaseLayout();
  146:             },
  147:           );
  148:         }
  ...
  155:         // Not signed in:
  156:         // 1. If public route requested, show PublicInfoShell
  157:         if (widget.publicRoute != null) {
  158:           return PublicInfoShell(targetRoute: widget.publicRoute!);
  159:         }
  ```
- **Codebase Verification of `PublicInfoShell` ([`numista_mobile/lib/screens/public_info_screens.dart:6-9`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/public_info_screens.dart#L6-L9)):**
  ```dart
  6: class PublicInfoShell extends StatelessWidget {
  7:   final String targetRoute;
  8: 
  9:   const PublicInfoShell({super.key, required this.targetRoute});
  ```
- **Codebase Verification of Root Cause 2 — In-Memory `Navigator.push` Without Browser History Sync ([`numista_mobile/lib/screens/login_screen.dart:566, 585-609`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L566-L609)):**
  ```dart
  566:         _footerLink('Pricing', () => _openPublicRoute('/pricing')),
  ...
  585:   Widget _footerLink(String label, VoidCallback onTap) {
  586:     return InkWell(
  587:       onTap: onTap,
  ...
  603:   void _openPublicRoute(String route) {
  604:     Navigator.of(context).push(
  605:       MaterialPageRoute(
  606:         builder: (_) => PublicInfoShell(targetRoute: route),
  607:       ),
  608:     );
  609:   }
  ```
- **Plan Verification ([`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md:216-240, 246-269`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md#L216-L269)):**
  ```dart
  221:   if (widget.publicRoute != null) {
  222:     return PublicInfoShell(
  223:       targetRoute: widget.publicRoute!,
  224:       isAuthenticated: FirebaseAuth.instance.currentUser != null,
  225:     );
  226:   }
  ```
- **Audit Finding:** This is a textbook root-cause catch. Any collector or tester with an active Firebase session (or anonymous demo session) who visits `/pricing` is hijacked at `auth_gate.dart:106` into `BaseLayout()` before line `157` (`if (widget.publicRoute != null)`) is ever reached; meanwhile, clicking `Pricing` in the login footer pushes `PublicInfoShell` in-memory without updating `window.history.pushState`, so refreshing the page drops the user back to `/login`. Evaluating `if (widget.publicRoute != null)` at the top of `AuthGate.build` and syncing `WebRouteHelper.pushWebRoute` fixes both defects cleanly.

---

### Task 4: Lower-Priority Collector UX Items (`PASS`)

- **Codebase Verification ([`numista_mobile/lib/screens/login_screen.dart:340, 415-416, 468, 692-693, 720-723`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart#L340-L723)):**
  ```dart
  340:                                   _StatBadge(value: 'AI+', label: 'Community\nVerified'),
  ...
  415:               ('📋', 'Estate documentation, reports, and lateral transfer'),
  416:               ('💬', 'Morgan AI numismatic assistant — research any coin'),
  ...
  468:                   _StatBadge(value: 'AI+', label: 'Community\nVerified'),
  ...
  692:                 child: const Text('Forgot your PIN?',
  693:                     style: TextStyle(color: _grey, fontSize: NumistaTheme.textLg)),
  ...
  720:               child: Text(
  721:                 _usePasswordSignIn ? 'Sign in with 6-digit PIN' : 'Older account? Sign in with password',
  722:                 style: const TextStyle(color: Color(0xFF64748B), fontSize: NumistaTheme.textCaption),
  723:               ),
  ```
- **Plan Verification ([`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md:274-280`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md#L274-L280)):**
  ```markdown
  276: | **1. `AI+ Community Verified`** | `_StatBadge(value: 'AI+', label: 'Community\nVerified')` (`login_screen.dart:340, 468`) | `_StatBadge(value: '99.4%', label: 'Attribution\nAccuracy')` or `_StatBadge(value: '100%', label: 'Private &\nSecure')` | "AI+" reads like an ungrounded buzzword. A verified percentage or privacy guarantee builds trust with serious collectors. |
  277: | **2. PIN / Password Labeling** | `Forgot your PIN?` displayed even in password mode (`login_screen.dart:692`); toggle text reads `Older account? Sign in with password` (`line 721`). | - Dynamic text: `_usePasswordSignIn ? 'Forgot your password?' : 'Forgot your PIN?'`<br>- Clear toggle: `_usePasswordSignIn ? 'Sign in with 6-digit PIN' : 'Sign in with password'` | Eliminates user confusion when recovering passwords vs PINs. |
  278: | **3. Numismatic Jargon** | `Estate documentation, reports, and lateral transfer` (`line 415`); `Morgan AI numismatic assistant` (`line 416`). | - `Estate documentation, reports, and family transfers (Passport Protocol)`<br>- `Morgan — your AI numismatic expert & research assistant` | Demystifies military/enterprise jargon ("lateral transfer") for senior collectors and clarifies Morgan's role. |
  279: | **4. Footer Accessibility** | Disclaimer absent from public footer; loading screen disclaimer unread by screen readers. | Wrap public footer links and legal text in `Semantics(container: true, label: 'Legal and Navigation Footer', ...)` with clear linear tab order. | Ensures WCAG 2.1 AA screen-reader compliance for visually impaired collectors. |
  ```
- **Audit Finding:** All 4 lower-priority UX items are verified against the exact lines in `login_screen.dart` and paired with clear, senior-friendly copy updates.

---

## 3. Non-Blocking Execution Safeguards & Proactive No-Silo Observations (`RADIO_NET-790`)

Zero blocking plan defects exist. We log **3 non-blocking execution safeguards (`S404-1`..`S404-3`)** for the implementation phase:

1. **`S404-1` (Cross-Branch Merge Alignment With `dev` / `NET-777` `CatalogBrowseScreen`):**
   - `PLAN_NET-801` was authored against branch `p7-v8.9` (`9948c519`), whereas branch `dev` (`18a8b8e5` / `NET-768` / `NET-777`) already added `/catalog` and `/catalog/**` rewrites in `firebase.json` and routes `/catalog` and `/catalog/:nacCode` in `main.dart` directly to `CatalogBrowseScreen(initialNacCode: initialNacCode)`. When integrating `NET-801`, ensure `/catalog` and `/catalog/:nacCode` preserve deep-link support to `CatalogBrowseScreen` (either directly or embedded inside `PublicInfoShell`) rather than overwriting the `:nacCode` parameter handler.
2. **`S404-2` (Non-JS Link-Preview Crawlers for Meta Ads — Static `<title>` / OpenGraph Tags):**
   - Updating `web.document.title` via `WebRouteHelper` (`PLAN_NET-801:200`) fixes browser tab titles and JavaScript-executing crawlers (Googlebot), but non-JS social scrapers (such as Meta's `facebookexternalhit` crawler used for the 26 Nov Meta ad launch) read the initial static HTML response before Flutter CanvasKit executes. During execution, consider serving lightweight route-specific HTML entrypoints (`pricing.html`, `catalog.html`, `about.html`) or pre-rendered `<title>` and `<meta property="og:title">` tags so Meta ad link previews display route-specific titles and descriptions on initial HTTP 200 fetch.
3. **`S404-3` (Proactive No-Silo Alignment: `5,142 Reference Coins` Badge vs. `3,202` Catalog Master Entries):**
   - In `login_screen.dart:338, 466` and `PLAN_NET-801:205`, the front door advertises `"5,142 Reference Coins"`, whereas the scrubbed public reference catalog (`numista_mobile/assets/data/catalog_public_v1.json` and `docs/MISSING_IMAGES.csv` audited in `NET-788`/`NET-803`) contains **3,202** catalog entries. If Founder Eric approves Option A (Public Read-Only Catalog at `/catalog`), align the front-door stat badge and `/catalog` meta title with the exact verified catalog count (or clarify `3,202 US Coins & Sets` vs. total global database) so visitors never see a mismatch between the landing page badge and the `/catalog` item count.

---

## 4. Standing Locks & Final Verdict

- **Standing Locks Verified:**
  - **PLAN ONLY / REVIEW ONLY:** Zero application source code modified.
  - **`origin/main` Lock:** Strictly untouched at `9f04550a`.
  - **Stripe Lock:** Strictly OFF.
  - **Firestore Lock:** Zero Firestore writes or seeding.
- **Final Verdict:** **96 / 100 (`PASS`)**. Handing off to **Grok Bot CoS (`95+`) -> Stand Alone Grok (`SAG`) -> Founder Eric typed YES**.
