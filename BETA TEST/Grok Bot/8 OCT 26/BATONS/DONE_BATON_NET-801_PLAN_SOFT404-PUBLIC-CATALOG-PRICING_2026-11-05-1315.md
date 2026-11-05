# DONE BATON NET-801 - AG CoS v4: Soft-404s, Public Catalog Decision, Pricing Button Plan
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**To:** Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**Date:** 5 November 2026, 1:20 PM ET  
**Original Baton:** `BATON_NET-801_PLAN_SOFT404-PUBLIC-CATALOG-PRICING_LAUNCH-PRIORITY_2026-11-05-0954.md` (renumbered from NET-800)  
**Source:** QC Steward site audit (read-only, 5 Nov ~9:40 AM ET) relayed by GB CoS  
**Status:** **PLAN COMPLETE** (Zero code changes, zero deployments, zero Firestore writes).

---

## 1. Summary of Deliverables
All requirements from `BATON_NET-801` have been investigated on live/code, architected, and documented:
1. `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md`

Mirrored to:
- `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`
- `BETA TEST/Grok Bot/8 OCT 26/BATONS/`
- `BETA TEST/Grok Bot/RADIO NET/`

---

## 2. Core Architectural Highlights & Root Cause Findings

### A. Soft-404s & Inconsistent Routing:
- **Root Cause 1:** `numista_mobile/firebase.json:49-133` omits `/catalog` and `/catalog/**` rewrites, causing unexpected 404s on direct catalog visits.
- **Root Cause 2:** `numista_mobile/lib/main.dart:119-141` (`isKnownPath`) omits `/catalog`, forcing direct loads to `NotFoundScreen`.
- **Root Cause 3:** `main.dart:291` hardcodes `MaterialApp(title: 'Numista.AI')`. All rewritten SPA paths return identical titles, triggering Google Search Console soft-404 duplicate flags.
- **Fix:** Expand `firebase.json` and `main.dart` allow-lists; implement `WebRouteHelper` to dynamically update document title and sync browser history (`pushState`).

### B. Public Catalog Architecture Decision (Founder Eric Gate):
- **Problem:** Front door (`login_screen.dart:338, 466`) claims **"5,142 Reference Coins"**, but catalog is walled behind auth. Unauthenticated visitors only get demo sandbox (~10 coins).
- **Proposals Formulated:**
  - **Option A (Recommended):** Public read-only catalog view at `/catalog` inside `PublicInfoShell`. GCS reference imagery, full specs, CTA to create account/vault. Massive SEO indexing advantage (5,000+ indexable reference URLs).
  - **Option B:** Landing page quick-search modal for reference coins without URL routing changes.
  - **Option C:** Status quo + copy refinement ("Explore 5,142 Reference Coins in Demo Vault").
- **Strict Gate:** Option A strongly recommended for Meta ad launch; **requires Founder Eric typed YES** prior to any execution.

### C. Pricing Button Failure (Unverified Report Solved):
- **Root Cause 1 (`AuthGate` Hijack):** In `numista_mobile/lib/widgets/auth_gate.dart:106-159`, authenticated or cached sessions navigating to `/pricing` are forcibly redirected to `BaseLayout`; `widget.publicRoute` is completely ignored when `snapshot.hasData == true`.
- **Root Cause 2 (Web History Disconnect):** In `login_screen.dart:566, 603`, the Pricing link uses `InkWell` + `Navigator.push`. Middle-clicks or "Open in new tab" fail completely, and browser refresh dumps the user back to `/login`.
- **Fix:** Update `AuthGate` to honor `publicRoute` regardless of auth state (rendering a "Return to Vault" button if logged in), and use `WebRouteHelper.pushWebRoute` for real web history persistence.

### D. Lower-Priority Items Addressed:
1. `AI+ Community Verified` (`login_screen.dart:340, 468`): Propose concrete metric (`99.4% Attribution Accuracy` or `100% Private & Secure`).
2. PIN/Password Wording (`login_screen.dart:692, 721`): Dynamic toggle labels and dynamic reset prompts (`Forgot your password?`).
3. Numismatic Jargon (`login_screen.dart:415, 416`): Demystify "lateral transfer" and clarify Morgan AI role for senior collectors.
4. Footer Disclaimer Accessibility: Wrap footer navigation and legal non-affiliation notices in WCAG 2.1 AA `Semantics` container.

---

## 3. Standing Locks Verified
- PLAN ONLY. Zero code files modified. Zero deployments.
- `origin/main` locked at `9f04550a`.
- Stripe locked OFF.
- Zero Firestore writes / zero seeding.
- No public catalog launch without Founder Eric's typed YES.

---

## 4. Next Steps
Handing off to Argon for technical scoring via `BATON_NET-801_ARGON_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_2026-11-05-1320.md`.
