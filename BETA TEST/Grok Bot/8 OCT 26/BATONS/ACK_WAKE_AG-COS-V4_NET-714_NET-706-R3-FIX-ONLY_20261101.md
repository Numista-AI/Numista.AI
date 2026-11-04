# ACK WAKE - AG CoS v4 - NET-714 - 2026-11-01 15:45 EST
- **Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)
- **Recipient:** Grok CoS, Grok Desk, Argon (SAG Auditor), Founder Eric
- **Ref:** `WAKE_AG-COS-V4_NET-714_NET-706-R3-FIX-ONLY_20261101.md`, `COS_SCORE_NET-706-R2_84_REVISE_20261101-1541EST.md`, `BATON_NET-714_AGCOS-V4_NET-706-R3-FIX-ONLY_20261101.md`

### Roger & Concurrence:
1. **Score Received:** 84/100 REVISE rogered.
2. **Task Undertaken:** Drafting and filing `PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md` fixing MF1–MF5 and SF-A, SF-B, SF-C strictly. Zero changes to passing sections (pixel, events, 404, pricing, placeholders all passed 100%).
3. **Surgical Fixes Integrated in R3:**
   - **MF1:** Deleted references to non-existent `snapshot_legacy.py` and deleted claim of `"max_items: 10"` in `tier_gatekeeper.py`. Cited actual `tier_gatekeeper.py:41-50` (`"free": 20`) and Plan v3.2 policy (10 items).
   - **MF2:** Quoted actual Legacy cutoff timestamp from codebase `tier_gatekeeper.py:136, 145, 149` (`creation_timestamp < 1795669200000` ms epoch = `2026-11-26T05:00:00Z`); marked 27 Nov as `[ERIC DECISION - 26 Nov vs 27 Nov cutoff]`.
   - **MF3:** Corrected copy citation line numbers to verified `origin/dev` positions: `login_screen.dart:1388`, `public_info_screens.dart:362` and `407`, `base_layout.dart:1540`.
   - **MF4:** Reverted privacy policy sentence to Eric's exact spec wording from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` (marked any third-party sale commitments `[ERIC DECISION]`), and targeted in-app privacy screen `numista_mobile/lib/screens/privacy_screen.dart:137-152`.
   - **MF5:** Labeled `/api/stripe/verify-session` as NEW endpoint and `session_id={CHECKOUT_SESSION_ID}` in `payment_routes.py:71` `success_url` as NEW work. Labeled Stripe IDs as proposed `lookup_key` values.
   - **SF-A:** Marked Free tier export price as `[ERIC DECISION - Free tier export price: $95.94 Gold baseline vs other]`.
   - **SF-B:** Directed TEST-01/02 verification to preview channel `p7-gate` first; live `https://numista.ai/` tested only post-production deployment upon Eric's typed YES.
   - **SF-C:** Cited exact rewrite lines in `numista_mobile/firebase.json` (lines 64–133).
4. **Mode:** DOCS-ONLY. Zero code changes, zero deploys, zero pushes to main. Locks holding.
