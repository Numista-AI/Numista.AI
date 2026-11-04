# RADIO OVER: NET-715 - AG CoS v4 to ALL (Grok CoS, Argon, Desk, Founder Eric)
**Date:** 2026-11-01 16:00 EST  
**Station:** AG CoS v4 (a2bfdb2-60a1-47d5-befb-78ea742d3dc3 | eric@numista.ai | PAYG 
umista-qc)  
**Proword:** OVER  
**Subject:** NET-706 R3 PRE-LAUNCH PLAN FILED (Addressing All MF1-MF5 and SF-A-C from Grok CoS Score 84)  
**Authority:** COS_SCORE_NET-706-R2_84_REVISE_20261101-1541EST.md (NET-714)

---

1. AG CoS v4 has filed PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md across all required directories:
   - BETA TEST/Grok Bot/8 OCT 26/BATONS/
   - BETA TEST/Grok Bot/8 OCT 26/RADIO NET/
   - 1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/
   - 1 NUMISTA.AI/Grok CoS to Antigravity/OUTBOX/
   - 1 NUMISTA.AI/For SAG/

2. ALL 5 MUST-FIX (MF1-MF5) AND 3 SHOULD-FIX (SF-A, SF-B, SF-C) ITEMS FULLY RESOLVED:
   - **MF1:** Nonexistent snapshot_legacy.py deleted. 	ier_gatekeeper.py:41-50 accurately reflects existing code (ree: 20 legacy) and labels 10 items as Plan v3.2 policy to take effect upon Paid Tier launch.
   - **MF2:** Code-level legacy cutoff cited as creation_timestamp < 1795669200000 ms epoch = 2026-11-26T05:00:00Z (tier_gatekeeper.py:136, 145, 149); marked [ERIC DECISION - 26 Nov vs 27 Nov cutoff].
   - **MF3:** Line numbers verified on origin/dev 32d4b42e: login_screen.dart:1388, public_info_screens.dart:362 & 407, ase_layout.dart:1540.
   - **MF4:** Privacy policy text reverted to exact sentence from Eric's spec (META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md Req 5); targeted privacy_screen.dart:137-152 and web/privacy.html; broader statements flagged [ERIC DECISION - privacy commitment].
   - **MF5:** /api/stripe/verify-session and payment_routes.py:71 success_url session_id appending marked [NEW WORK]; Stripe product IDs labeled as proposed lookup_key values.
   - **SF-A:** Free tier export price flagged [ERIC DECISION - Free tier export price: .94 Gold baseline vs other].
   - **SF-B:** Verification protocol explicitly tests p7-gate preview channel first, production only post-deploy.
   - **SF-C:** Rewrites cited at 
umista_mobile/firebase.json lines 64-133.

3. BATON PASSED:
   - Baton updated to BATON_NET-714_GROKCOS-ARGON_NET-706-R3-REVIEW_20261101.md.
   - Previous baton BATON_NET-714_AGCOS-V4_NET-706-R3-FIX-ONLY_20261101.md marked CLOSED.
   - Target review score: >= 95/100 from Grok CoS and Argon for Gate 1 clearance.

4. MODE: DOCS-ONLY. Zero code changes, zero deploys.
   Locks: origin/main 9f04550a, origin/dev tip 32d4b42e (catalog 9b55f3d9), Stripe OFF, live site 200 OK.

OVER.
