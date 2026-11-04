# COS SCORE - NET-706 R2 META AD PRE-LAUNCH PLAN - 84/100 - REVISE - 2026-11-01 15:41 EST
Scorer: Grok CoS (independent re-verification; no plan claim trusted). Mode: DOCS-ONLY, read-only git fetch + HTTP HEAD.
Plan scored: RADIO NET\PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md (485 lines). Baton: BATON_NET-712_GROKCOS-ARGON_NET-706-R2-REVIEW. Prior: 55 REVISE (R1).
Argon GEMINI38_REVIEW_NET-706 / NET-712B cover R1 only - no Argon review of R2 yet.

## Verdict: REVISE (84). Big improvement; SAG NOT run (gate >=95). Remaining defects are invented file/code facts in changed sections.

## What I verified myself
- Locks: origin/dev = 32d4b42e (plan correct), origin/main = 9f04550a.
- Pixel snippet byte-diff vs Eric's spec (INBOX copy): 664 bytes each, case-sensitive equal, SHA-256 8436041c...2f49 identical. Domain tag line present verbatim exactly once.
- HEAD: numista.ai/us-coins 404; /zzz-unknown?utm_source=meta 404; /?utm_source=meta&utm_campaign=thanksgiving 200 (no redirect); /pricing?utm_source=meta&fbclid=abc 200 (no redirect, params kept).
- Citations vs origin/dev: Cit 1 index.html 113-121 OK; Cit 2 main.dart 119-149 OK; Cit 3 auth_service.dart 130-161 OK; Cit 4 firebase.json 125-135 OK; Cit 5 tier_gatekeeper 41-50 OK; Cit 6 payment_routes.py 65-75 OK; Cit 7 stripe_service.dart 10-20 OK; Cit 8 base_layout.dart 52-60 OK; Cit 9 tier_gatekeeper 132-152 OK.
- Copy strings in 6.1: text is real, but 3 line numbers are wrong (see MF3).
- NOT FOUND in repo: numista_backend/scripts/snapshot_legacy.py; "max_items: 10" in tier_gatekeeper.py; /api/stripe/verify-session endpoint; session_id in success_url.
- Epoch 1795669200000 = 2026-11-26T05:00:00Z.

## R1 items re-verified
MF1 soft-404: FIXED (no ** rewrite; real 404 kept; TEST-12/13 correct). MF2 pixel verbatim: FIXED. MF3 PageView double-fire: FIXED (first route skipped; TEST-03/04). MF4 CompleteRegistration: FIXED (shared UID-guarded helper; email + Google isNewUser; TEST-05..09). MF5 export = 6 months of plan: FIXED for Copper/Silver/Platinum/Gold/Legacy (see SF-A for Free). MF6 invented SKUs removed; AI top-up labelled correctly: FIXED (but see MF5 below on IDs). MF7 "5 free coins" fabrication retracted: FIXED (new line-number errors -> MF3). MF8 homepage placeholder, one version: FIXED. MF9 savings math: FIXED (Copper 16.5%, Silver 16.6%, Platinum 17.3%, Gold 21.8% all correct).
SF1 Lifetime no price: FIXED. SF2 Purchase from amount_total: FIXED in intent (plumbing -> MF5). SF3 locks: FIXED. SF4 Legacy: NOT FIXED - now worse (MF1/MF2). SF5 InitiateCheckout test: FIXED (TEST-10). SF6 age band: RESOLVED per Eric (Meta 35-65+, creative readable to age 83) - plan matches. SF7 station ba2bfdb2: FIXED.
Prices vs v3.2: Free 10; Copper $4.99/$49.99; Silver $8.99/$89.99; Platinum $10.99/$109; Gold $15.99/$150; AI top-up $5/1,000; export 6 months ($95.94 Legacy) - all EXACT. 13 prices = 8 subs + 1 top-up + 4 exports.

## MUST-FIX (plain English)
MF1 Two invented facts: numista_backend/scripts/snapshot_legacy.py does not exist, and tier_gatekeeper.py has no "max_items: 10". Delete both or cite real files/lines.
MF2 Legacy cutoff contradicts the code: plan says 2026-11-27T05:00Z; tier_gatekeeper.py:136/145/149 says 2026-11-26T05:00Z (1795669200000). Quote the code value, or mark the cutoff "[ERIC DECISION]" if it is meant to change - do not state 27 Nov as fact.
MF3 Wrong line numbers on 3 copy citations: login_screen.dart is line 1388 (not 456); public_info_screens.dart "Pricing TBA" is 362 and "open public beta" is 407 (not 181); base_layout.dart demo banner is 1540 (not 444).
MF4 New wording not approved: the privacy text now adds "We do not sell your personal data or coin collection details to third parties" and a dataset ID - a new legal promise. Mark it "[ERIC DECISION]" or use the spec's plain sentence. Also R2 moved the in-app privacy target to public_info_screens.dart; the real file is lib/screens/privacy_screen.dart.
MF5 New code presented as existing: /api/stripe/verify-session does not exist and success_url (payment_routes.py:71) has no session_id. Label both as NEW work with the exact change to line 71. Stripe IDs like prod_copper_sub/price_copper_monthly are made up (Stripe generates IDs) - call them proposed lookup_keys.

## SHOULD-FIX
SF-A Free-tier export at $95.94 ("Gold / Never-Paid Legacy / Free") - v3.2 only sets $95.94 for never-paid Legacy. Mark Free-tier export "[ERIC DECISION]".
SF-B TEST-01/02 curl live numista.ai - run them on p7-gate first; live only after the deploy YES.
SF-C Section 4.2 lists firebase.json known routes "/about,/pricing,..." - confirm against actual rewrites list (not cited); cite lines.

## Score breakdown
Tag/pixel 20/20 A· Event logic 18/20 A· Privacy 2/5 A· Pricing/Stripe 12/15 A· Homepage placeholder 5/5 A· Soft-404/UTM 10/10 A· Gates/locks 10/10 A· Citation honesty 7/15 = 84/100
