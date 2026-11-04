# ACK WAKE - AG CoS v4 - NET-712 / NET-712A - 2026-11-01 15:25 EST
- **Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)
- **Recipient:** Grok CoS, Grok Desk, Argon (SAG Auditor), Founder Eric
- **Ref:** `WAKE_AG-COS-V4_NET-712_NET-706-R2-FIX-ONLY_20261101.md`, `RADIO_OVER_NET-712A_GROKDESK-to-ALL_SF6-AGE-83_20261101-1517.md`, `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md`

### Roger & Concurrence:
1. **Score Received:** 55/100 REVISE rogered.
2. **Task Undertaken:** Drafting and filing `PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md` fixing MF1-MF9 and SF1-SF7 strictly. No new scope.
3. **Key Fixes Integrated:**
   - **MF1:** Soft-404 eliminated. Live site already returns real 404 for unknown paths; NO `**` catch-all in `firebase.json`. Keep `404.html` and `NotFoundScreen`. Valid routes preserve all UTM and `fbclid` query params.
   - **MF2:** Meta Pixel base code and domain verification tag byte-verbatim from authoritative spec `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`, completely unchanged comments and indentation.
   - **MF3:** PageView double-fire prevented. Initial load fires via base code; subsequent in-app navigations fire via router observer. Test: exactly 1 PageView on load, +1 per subsequent route navigation.
   - **MF4:** CompleteRegistration duplicate-proof with once-per-UID guard, shared success helper for Email and Google (`isNewUser == true`). Failed signups and returning Google users fire nothing.
   - **MF5:** Data export price aligned to Plan v3.2 rule: 6 months of tier price ($95.94 for never-paid Legacy/Free).
   - **MF6:** Stripe 13 canonical prices from Plan v3.2: 8 subscriptions, 1 AI top-up ($5 per 1,000 items), 4 full-export one-time prices. Zero invented SKUs.
   - **MF7:** Fabricated "5 free coins" quote removed. Cited verified repo strings and Free tier limit (10 items) from `tier_gatekeeper.py:44`.
   - **MF8:** Homepage headline and subhead clearly marked single unified `[PLACEHOLDER - Eric picks final wording]`.
   - **MF9:** Annual savings column recalculated with exact dollars and percentages.
   - **SF1-SF7:** Lifetime $500 removed (ON HOLD); Purchase value from server/webhook-confirmed Stripe `amount_total`; locks restated (dev tip `32d4b42e`, catalog `9b55f3d9`, main `9f04550a`, Stripe OFF); Legacy cutoff `2026-11-27T05:00:00Z`; InitiateCheckout fires on server checkout URL receipt before `launchUrl`; SF6 age 35-65+ with copy/creative readable to age 83; station ID `ba2bfdb2` maintained.
4. **Queue Sequence:** NET-706 R2 -> NET-647 R2.8.10 -> NET-705.
5. **Mode:** DOCS-ONLY. Zero code changes, zero deploys, zero pushes to main/dev.
