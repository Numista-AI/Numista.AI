**STATUS: CLOSED 2026-11-01 4:46 PM ET by Grok CoS - scored 92 REVISE (COS_SCORE_NET-706-R4_92_REVISE_20261101-1650EST.md); passed to AG CoS v4 via BATON_NET-719_AGCOS-V4_NET-706-R5-FIX-ONLY_20261101.md.**

# BATON - NET-716 / NET-717 - Grok CoS & Argon (SAG Auditor) - NET-706 R4 PLAN REVIEW - 2026-11-01 16:35 EST

**Current Holder:** Grok CoS & Argon (SAG Auditor)  
**Passed By:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Task:** Review and score `PRELAUNCH_PLAN_NET-706_R4_META-AD_20261101.md` (Target >= 95/100 for Gate 1 clearance).  
**Scope Covered (Fix-Only addressing MF-A and SF-D from Score 93):**
1. **MF-A (Harmonized Privacy Integration):**
   - In Section 7, extended existing Section 4 and Section 3 policy text without duplicating sections.
   - Quoted exact BEFORE and AFTER lines for `privacy_screen.dart:139` and `web/privacy.html:325`.
   - Harmonized "No data is shared with third-party advertisers" by clarifying Meta Pixel event data is used for advertising campaign measurement and conversion attribution, while reiterating that beyond this measurement, no personal data is shared with third-party advertisers or marketers.
   - Dropped duplicate non-sale pledge marker.
   - Codified explicit invariant: No home-address collection anywhere in the service or data model.
2. **SF-D (Exact Firebase Rewrite Route List):**
   - In Section 4.2, detailed the exact route sources from `firebase.json:64-133`:
     - Static HTML rewrites: `/privacy` (:64-67), `/terms` (:68-71).
     - SPA index rewrites (`/index.html`): `/about` (:72), `/pricing` (:76), `/features` (:80), `/faq` (:84), `/login` (:88), `/reset-password` (:92), `/signup` (:96), `/demo` (:100), `/` (:104), `/index.html` (:108), `/wishlist` (:112), `/wishlist/**` (:116), `/attorney_portal` (:120), `/claim` (:124), `/claim/**` (:128).
     - Explicitly clarified `/app` and `/blog` are 301 redirects (:24-33) outside the rewrite block, and there is no `/attorney` rewrite (route is `/attorney_portal` at :120).
     - Invariant preserved: Zero `**` catch-all wildcard rewrite; real 404 behavior intact.
3. **Settled Decisions (NET-714A):**
   - Replaced all 3 `[ERIC DECISION]` markers with settled decisions: privacy line approved with no home address; legacy cutoff settled at `2026-11-26T05:00:00Z` (Thanksgiving morning); Free tier full export price approved at `$95.94`.
4. **Meta Pixel Base Snippet:**
   - 100% byte-identical to spec (664 bytes, SHA-256 `8436041c6ce5ca6dc9345dae3381a7a968187a245582539585c8bc32edfa2f49`).

**Mode:** DOCS-ONLY (`NO EXECUTE`). Zero code changes, zero deploys.  
**Locks:** origin/main `9f04550a`, origin/dev tip `32d4b42e` (catalog `9b55f3d9`), Stripe OFF, live site 200 OK.

