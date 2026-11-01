**STATUS: CLOSED 2026-11-01 4:25 PM ET by Grok CoS - R3 scored 93 REVISE (Argon 100 PASS not accepted); superseded by BATON_NET-716**

# BATON - NET-714 / NET-715 - Grok CoS & Argon (SAG Auditor) - NET-706 R3 PLAN REVIEW - 2026-11-01 16:00 EST

**Current Holder:** Grok CoS & Argon (SAG Auditor)  
**Passed By:** AG CoS v4 (a2bfdb2-60a1-47d5-befb-78ea742d3dc3)  
**Task:** Review and score PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md (Target >= 95/100 for Gate 1 sign-off).  
**Scope Covered (Fix-Only addressing MF1-MF5 and SF-A, SF-B, SF-C from Score 84):**
1. **MF1 (No Fabricated Files):** Completely eliminated nonexistent snapshot_legacy.py. Accurately cited 	ier_gatekeeper.py:41-50 existing code (ree: 20 legacy) and labeled 10-item cap as Plan v3.2 policy to take effect upon Paid Tier launch.
2. **MF2 (Legacy Cutoff Invariant):** Code-level invariant cited from 	ier_gatekeeper.py:136, 145, 149 as creation_timestamp < 1795669200000 ms epoch = 2026-11-26T05:00:00Z (Thanksgiving morning). Explicitly marked [ERIC DECISION - 26 Nov vs 27 Nov cutoff].
3. **MF3 (Accurate Line Numbers on origin/dev 32d4b42e):** Verified citations: login_screen.dart:1388, public_info_screens.dart:362 and 407, ase_layout.dart:1540.
4. **MF4 (Privacy Disclosure Scope):** Reverted in-app privacy policy addition to the exact sentence from Founder Eric's spec (META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md Req 5). Target files: 
umista_mobile/lib/screens/privacy_screen.dart:137-152 and 
umista_mobile/web/privacy.html. Broader statements flagged [ERIC DECISION - privacy commitment].
5. **MF5 (Stripe Plumbing & Proposed Lookup Keys):** Explicitly marked /api/stripe/verify-session as [NEW WORK]; marked payment_routes.py:71 success_url session_id appending as [NEW WORK]. Labeled all 13 Stripe IDs as proposed lookup_key values.
6. **SF-A (Free Tier Export Price Decision):** Flagged [ERIC DECISION - Free tier export price: .94 Gold baseline vs other].
7. **SF-B (Preview Testing Before Live):** TEST-01/02 runs against Firebase preview channel p7-gate (https://numista-vault--p7-gate-*.web.app/) first; production only post-deploy upon Eric's typed YES.
8. **SF-C (Rewrite Citation):** Explicitly cited 
umista_mobile/firebase.json lines 64-133.

**Mode:** DOCS-ONLY (NO EXECUTE). Zero code changes, zero deploys.  
**Locks:** origin/main 9f04550a, origin/dev tip 32d4b42e (catalog 9b55f3d9), Stripe OFF, live site 200 OK.

---
## NET-714A ADDENDUM (Desk, 4:02 PM ET 1 Nov 2026) - Eric's decisions, typed in CoS chat 4:02 PM ET
1. PRIVACY: APPROVED. Add: "We do not sell your personal data or coin collection details to third parties." Eric's principle: Numista.Ai deliberately does NOT collect users' home addresses, so no collection's value can ever be tied to a location. The plan must NOT add any address collection; privacy text may say so. AG must check for an existing privacy statement (lib/screens/privacy_screen.dart and the web) and EXTEND it, not duplicate it.
2. LEGACY CUTOFF: 26 Nov 2026 05:00 UTC, matching tier_gatekeeper.py lines 136, 145, 149.
3. FREE-TIER FULL EXPORT: $95.94 APPROVED.
All other NET-714 must-fixes still stand (invented snapshot_legacy.py and max_items, line numbers, privacy_screen.dart target, label new endpoints and Stripe keys as PROPOSED). Plan-only; full review cycle; locks unchanged (main 9f04550a, dev 32d4b42e, Stripe OFF).

