# DONE BATON NET-807: `DONE_BATON_NET-807_REVISE_SOFT404-PUBLIC-CATALOG-PRICING_v1.1_2026-11-05-1550.md`

- **To:** Grok Bot CoS, Stand Alone Grok (SAG), Argon (Gemini 3.8), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 3:50 PM ET
- **Subject:** COMPLETION OF `BATON_NET-807` (Soft-404 / Public Catalog / Pricing Plan Revision v1.1)
- **Delivered Artifact:** `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md` (mirrored to `BATONS/`, `RADIO NET/`, and `INBOX/`)
- **Status:** **PLAN ONLY** (Zero code modifications, zero deployments, zero Firestore writes/seeding).

---

## Summary of Must-Fix Resolutions in v1.1:

1. **Rebase on Actual `/catalog` Status & Architecture (Must-Fix #1 & #6):**
   - Struck the false HTTP 404 premise; acknowledged that live `/catalog` returns 200 via SPA rewrite to `index.html`.
   - Rebased cleanly on `origin/dev`'s existing `CatalogBrowseScreen` (`lib/screens/catalog/catalog_browse_screen.dart` under NET-747/NET-768/NET-777). No duplicate screens or clobbered deep links (`/catalog/:nacCode`).

2. **Reconciliation of 5,142 vs 3,202 Master Census (Must-Fix #1 / S404-3):**
   - Aligned marketing badges (`login_screen.dart:338, 466`), page titles, and meta tags with ground truth: exactly **3,202 verified master reference entries** in `entries_master_20261103.jsonl` (2,965 coins + 181 notes + 56 medals) and `docs/MISSING_IMAGES.csv`.
   - Removed "World" claims (catalog is strictly US federal, pre-federal, and US Mint medals/currency).
   - Deleted unsourced marketing claims: 99.4% stat, 5,000+ indexable pages, advisory board, Sheldon grading, Passport Protocol, 100% Private & Secure.

3. **Options A / B / C for Founder Eric's Explicit Typed Choice (Must-Fix #5 & #8):**
   - Explicitly presented Options A (Full Public `/catalog`, Recommended for Thanksgiving Ads), B (Homepage Search Popup Modal), and C (Keep Gated Behind Sign-In).
   - Bound by strict gate: Founder Eric must explicitly type his choice ("Option A", "Option B", or "Option C") along with his typed YES before any build execution or deployment.

4. **Public Valuations & Image Hygiene (Must-Fix #3 & #4):**
   - Valuation source bound strictly to CDN CPG retail (`cpgRetail`).
   - Zero wholesale prices (no dealer ask/bid, no Greysheet wholesale).
   - Zero user cost/ownership/valuation data exposed publicly.
   - Missing/zero pricing renders styled gold `'Valuation Pending'` chip.
   - AI replica images allowed strictly inside labeled `ai_replica_images`, never primary or index.
   - In-memory own-origin allowlist guard before fetch; zero external hotlinks. Missing images render local SVG placeholders.

5. **Semantic HTML Anchors & AuthGate Fix (Must-Fix #7):**
   - Resolved AuthGate race condition in `widgets/auth_gate.dart`: Await auth state restoration before redirect; honor `publicRoute` for `/pricing` even for authenticated sessions.
   - Specified Flutter's semantic `Link` widget (`package:url_launcher/link.dart`) for footer links and Pricing button, generating real `<a href>` DOM nodes for middle-click, right-click, and crawler support.

6. **Static OpenGraph (OG) Tags for Meta Ads Crawler (Must-Fix #2 / S404-2):**
   - Specified static `<title>`, `<meta property="og:*">`, and `<link rel="canonical">` tags for non-JS scrapers (`facebookexternalhit` and Googlebot) on ad landing pages (`numista.ai`, `/catalog`, `/pricing`).

7. **Standing Controls: Rollback, Preview Channel, $ Cap (Must-Fix #6):**
   - Pinned rollback baseline commit `9f04550a`.
   - Mandatory Firebase Hosting preview channel verification before production release.
   - Public catalog traffic inherits the NET-804/NET-777 $25.00/month hard budget egress cap + $20.00/month Cloud Monitoring alert with `stop-public-egress` Cloud Function.
   - Test files explicitly marked as to-be-created implementation artifacts (`test/route_test.dart`, `test/auth_gate_test.dart`).
