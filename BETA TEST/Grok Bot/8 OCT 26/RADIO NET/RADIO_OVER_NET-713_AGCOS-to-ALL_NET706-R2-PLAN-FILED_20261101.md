# RADIO OVER NET-713 — AG CoS v4 → ALL — NET-706 R2 PLAN FILED — 1 Nov 2026 3:35 PM ET

1. **FILED:** `PRELAUNCH_PLAN_NET-706_R2_META-AD_20261101.md` across BATONS, RADIO NET, INBOX, OUTBOX, and For SAG.
2. **ALL MUST-FIX (MF1–MF9) & SHOULD-FIX (SF1–SF7) RESOLVED:**
   - **MF1:** Real HTTP 404 for unknown paths preserved (NO wildcard `**` rewrite in `firebase.json`; `404.html` and `NotFoundScreen` intact; query params preserved on valid routes).
   - **MF2:** Meta Pixel base code and domain verification tag byte-verbatim from NET-709A spec, unchanged comments and whitespace.
   - **MF3:** PageView double-fire eliminated. Initial load fires via base code; in-app client routing skips initial route, fires +1 per subsequent route change.
   - **MF4:** CompleteRegistration duplicate-proof (once-per-UID local guard; single shared helper for email and Google `isNewUser == true`; failed signups and returning Google users fire nothing).
   - **MF5:** Data export price = 6 months of user tier ($95.94 for never-paid Legacy / Free).
   - **MF6:** Stripe 13 canonical prices from Plan v3.2 (8 subscriptions, 1 AI top-up, 4 full exports; zero invented SKUs).
   - **MF7:** Fabricated "5 free coins" quote removed; real strings cited from `login_screen.dart`, `public_info_screens.dart`, `base_layout.dart`, and `tier_gatekeeper.py:44`.
   - **MF8:** Single unified hero placeholder `[PLACEHOLDER - Eric picks final wording]`.
   - **MF9:** Annual savings column recalculated with exact dollars and percentages.
   - **SF1–SF7:** Lifetime $500 removed (ON HOLD); Purchase value from server/webhook-confirmed Stripe `amount_total`; locks restated (dev tip `32d4b42e`, catalog `9b55f3d9`, main `9f04550a`, Stripe OFF); Legacy cutoff `2026-11-27T05:00:00Z`; InitiateCheckout fires on server checkout URL receipt before `launchUrl`; SF6 age 35–65+ with copy/creative readable to age 83; station ID `ba2bfdb2` maintained.
3. **BATON PASSED:** `BATON_NET-712_GROKCOS-ARGON_NET-706-R2-REVIEW_20261101.md`.
4. **TURN:** Grok CoS and Argon for review and scoring ($\ge 95/100$).
5. **NEXT IN AG COS QUEUE:** NET-647 R2.8.10 Fix-Only Plan.
6. **MODE:** DOCS-ONLY. Zero code edits, zero deploys. Locks holding.

OVER.
