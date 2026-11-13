# COS SCORE - NET-706 META AD PRE-LAUNCH PLAN - 55/100 - REVISE - 2026-11-01 15:15 EST
Scorer: Grok CoS (independent re-verification; no plan claim trusted). Mode: DOCS-ONLY, read-only git fetch + HTTP HEAD.
Plan scored: RADIO NET\PRELAUNCH_PLAN_NET-706_META-AD_20261101.md (434 lines). Baton: NET-706. Authority: INBOX\META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md (NET-709A).

## Verdict: REVISE (55). SAG NOT run (gate is >=95). Argon has not yet reviewed NET-706.

## What I verified myself
- Repo C:\Users\ericd\Documents\MyVertexProject, fetched. origin/main = 9f04550a (OK). origin/p7-v8.9 = 38699700. origin/dev = 32d4b42e (radio-only commit 03:12 EST 1 Nov; 9b55f3d9 is an ancestor). Plan's "dev 9b55f3d9" is stale wording - restate as "catalog frozen at 9b55f3d9, dev tip 32d4b42e".
- Code citations vs origin/dev: Cit 1 index.html 113-118 VERBATIM; Cit 2 main.dart 119-149 VERBATIM; Cit 3 auth_service.dart 133-145 VERBATIM; Cit 4 firebase.json 130-135 VERBATIM; Cit 5 tier_gatekeeper.py 41-50 VERBATIM. payment_routes.py:71 success_url "#/settings?stripe=success" EXISTS. stripe_service.dart launchCheckoutSession EXISTS (line 13). BaseLayout EXISTS (base_layout.dart:52). signInWithPopup at auth_service.dart:153 (no isNewUser check today - plan adds it, OK).
- index.html has NO fbq / facebook-domain-verification today -> single install is achievable.
- NOT FOUND: "Start with 5 free coins" in lib/screens/login_screen.dart (string absent; repo-wide grep for 5 free coins/items in lib+web finds nothing). Quoted copy is fabricated.
- HTTP: numista.ai/ 200; numista.ai/pricing?utm_source=meta 200; numista.ai/us-coins 404; numista.ai/zzz-unknown?utm_source=meta 404; p7-gate preview 200; fbevents.js 200; facebook.com/tr noscript 200.

## MUST-FIX (plain English)
MF1 Soft-404 is backwards. The live site ALREADY returns a real 404 for unknown paths. The plan adds a "**" catch-all to index.html and routes unknown paths to the homepage - that CREATES soft-404s. Required: unknown paths = real HTTP 404 (keep 404.html / NotFoundScreen); valid routes keep all UTM/fbclid params. Rewrite 5.2, Citation 2/4 modifications, and test 9.3 (us-coins and unknown-sub-route must return 404; /?utm_source=meta and /pricing?utm_... must return 200 with params intact).
MF2 Pixel base code not verbatim. Plan changes the comment to "Meta Pixel Code (Authoritative NET-709A)" and re-indents. Spec says completely unchanged. Paste exactly as in the spec. Same for the domain tag comment - tag line itself is fine.
MF3 PageView double-fire risk. Base code already fires PageView on load; plan also fires on BaseLayout route change with no rule to skip the first route. State: route-change PageView fires only on subsequent in-app navigations, never on initial load; add a test "exactly 1 PageView on load, +1 per navigation".
MF4 CompleteRegistration not duplicate-proof. Add a once-per-UID guard (e.g., Firestore/local flag) so refresh/re-render cannot refire; fire from ONE shared success helper used by both email and Google (isNewUser==true) paths; add tests for failed signup (fires nothing) and Google returning user (fires nothing).
MF5 Data-export price invented. Plan says export included in paid tiers and $4.99 for Free. v3.2 rule: full export costs 6 months of the plan ($95.94 for never-paid Legacy). Fix 3.2 #6 and Stripe row 10.
MF6 Stripe 13 prices invented. Rows 11-13 (Estate Valuation $49, Family Seat $3.99, 30-Day AI Pass $9.99) are not in v3.2. Row 9 mislabels the AI top-up ($5 per 1,000 items) as "Storage". List the real 13 from Plan v3.2, or mark unknown rows "TBD by Eric" - do not invent SKUs or prices.
MF7 Fabricated quote. "Start with 5 free coins" in login_screen.dart does not exist. Grep the repo for the real 5-item/5-coin trial strings and cite file:line verbatim, or say none found.
MF8 Homepage scope line must be a placeholder. Plan presents final headline ("Mastered with Gemini AI") and subhead as decided. Mark both "[PLACEHOLDER - Eric picks final wording]"; also the plan uses two different versions (Sec 1 vs Sec 4) - one placeholder only.
MF9 Annual-savings column wrong. Gold $150 vs 12x$15.99=$191.88 is ~22% (OK) but Platinum $109 vs $131.88 is ~17%, Copper/Silver ~17% OK - recheck all and drop "2 mos free" labels unless exact, or remove the column.

## SHOULD-FIX
SF1 Lifetime: keep "ON HOLD" but delete "$500" from 3.1 note - price unresolved ($500 vs $1,500); no price shipped.
SF2 Purchase value should come from Stripe session amount_total (server/webhook-confirmed), not client-side plan price.
SF3 Restate locks (dev tip 32d4b42e; catalog frozen 9b55f3d9). Add explicit: execute on p7-v8.9, test on p7-gate, then dev->main only on separate YES.
SF4 Legacy rule: "created prior to October 2026" is not in v3.2 - quote the actual Legacy definition or say TBD.
SF5 InitiateCheckout: fire after checkout URL received, before launchUrl, once per click (OK) - add test.

SF6 Ad age band 35-65+ (Sec 1) is an unapproved assumption - Eric's brief is US only, 26 Nov-2 Dec, $625, no age band. Remove it or mark it '[ERIC DECISION - age targeting]'. Do not bake it in.
SF7 Station ID hygiene: AG CoS v4 station of record is ba2bfdb2 (plan header is correct). Argon NET-709B addresses AG v4 as ed139c44 - Argon to correct; AG to keep ba2bfdb2 in R2 and not adopt ed139c44.

## Checked OK
Domain tag value + pixel ID correct; static <head> placement above </head> (not JS-injected); privacy line added to privacy.html Section 3 + privacy_screen.dart; tier prices/ranges for Free-Gold exact; trial = 10; US-only + all ads to https://numista.ai/; Stripe live only on Eric typed YES before 26 Nov; Stripe OFF lock respected.

## Score breakdown
Tag/pixel placement 14/20 A· Event logic 13/20 A· Privacy 4/5 A· Pricing/Stripe catalog 6/15 A· Homepage placeholder 2/5 A· Soft-404/UTM 0/10 A· Gates/locks 8/10 A· Citation honesty 8/15 = 55/100

