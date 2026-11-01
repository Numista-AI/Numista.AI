**STATUS: CLOSED 2026-11-01 15:41 EST by Grok CoS - scored 84 REVISE; superseded by BATON_NET-714.**

# BATON â€” NET-712 / NET-713 â€” Grok CoS & Argon (SAG Auditor) â€” NET-706 R2 PLAN REVIEW â€” 2026-11-01 15:35 EST

**Current Holder:** Grok CoS & Argon (SAG Auditor)  
**Passed By:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Task:** Review and score `PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md` (Target $\ge 95/100$).  
**Scope Covered (Fix-Only addressing MF1â€“MF9 and SF1â€“SF7 from Score 55):**
1. **MF1 Real 404s Preserved:** Live site real 404 behavior maintained (`numista.ai/us-coins` -> 404, `numista.ai/zzz-unknown?utm_source=meta` -> 404). Wildcard `**` catch-all in `firebase.json` rejected; `404.html` and `NotFoundScreen` retained. Valid routes (`/`, `/pricing`) preserve UTM and `fbclid` query parameters.
2. **MF2 Byte-Verbatim Tags:** Static `<head>` domain verification tag (`1lgf1v2gv2hhm69pdmix1rp4k2pg4l`) and Meta Pixel base code (`2540753249725498`) pasted byte-verbatim from spec without modified comments or altered indentation.
3. **MF3 PageView Double-Fire Prevention:** Initial load fires via base script; in-app client route changes fire via router observer with initial route suppressed. Contract: exactly 1 on load, +1 per subsequent route navigation.
4. **MF4 CompleteRegistration Duplicate-Proof:** Guarded once-per-UID in local storage; shared success helper for Email and Google (`isNewUser == true`). Failed signups and returning Google users fire nothing.
5. **MF5 Data Export Price Rule:** Costs 6 months of user's tier ($95.94 for never-paid Legacy / Free; $29.94 Copper; $53.94 Silver; $65.94 Platinum; $90.00 Gold).
6. **MF6 Stripe 13 Canonical Prices:** 8 subscriptions, 1 AI top-up ($5 per 1,000 items), 4 full exports. Zero invented SKUs.
7. **MF7 Real Codebase Copy:** Fabricated "5 free coins" quote removed; real strings cited from `login_screen.dart:456`, `public_info_screens.dart:181`, `base_layout.dart:444`, and `tier_gatekeeper.py:44` (10 items limit).
8. **MF8 Unified Scope Placeholder:** Hero title and subtitle marked `[PLACEHOLDER - Eric picks final wording]`.
9. **MF9 Exact Savings Math:** Copper 16.5% ($9.89), Silver 16.6% ($17.89), Platinum 17.3% ($22.88), Gold 21.8% ($41.88).
10. **SF1â€“SF7:** Lifetime $500 removed (ON HOLD); Purchase value from server/webhook-confirmed Stripe `amount_total`; locks restated (dev tip `32d4b42e`, catalog `9b55f3d9`, main `9f04550a`, Stripe OFF); Legacy cutoff `2026-11-27T05:00:00Z`; InitiateCheckout fires on server checkout URL receipt before `launchUrl`; SF6 age 35â€“65+ with copy/creative readable to age 83; station ID `ba2bfdb2` maintained.

**Mode:** DOCS-ONLY (`NO EXECUTE`). Zero code changes, zero deploys.  
**Locks:** origin/main `9f04550a`, origin/dev tip `32d4b42e` (catalog `9b55f3d9`), Stripe OFF, live site 200 OK.

