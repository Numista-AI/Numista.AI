# WAKE / BATON - NET-714 - AG CoS v4 (ba2bfdb2) - NET-706 R3 FIX-ONLY - 2026-11-01 15:41 EST
Passed by: Grok CoS. Grok CoS scored NET-706 R2 84/100 REVISE. See RADIO NET\COS_SCORE_NET-706-R2_84_REVISE_20261101-1541EST.md.
Task: file PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md fixing ONLY:
MF1 delete invented snapshot_legacy.py and "max_items: 10" (neither exists).
MF2 Legacy cutoff: code says 2026-11-26T05:00Z (tier_gatekeeper.py:136/145/149) - quote it or mark [ERIC DECISION].
MF3 line numbers: login_screen.dart:1388; public_info_screens.dart:362 and :407; base_layout.dart:1540.
MF4 privacy: remove/flag "We do not sell..." as [ERIC DECISION]; in-app target is lib/screens/privacy_screen.dart.
MF5 label /api/stripe/verify-session + session_id in success_url (payment_routes.py:71) as NEW work; Stripe IDs = proposed lookup_keys.
SF-A Free-tier export price -> [ERIC DECISION]. SF-B run TEST-01/02 on p7-gate first. SF-C cite firebase.json rewrite lines for 4.2.
Do not touch anything else (pixel, events, 404, pricing, placeholders all PASS). Verify every quote with git show origin/dev:<path> before filing.
Mode: DOCS-ONLY. No code commits, push, deploy, Stripe. Locks: main 9f04550a, dev 32d4b42e, Stripe OFF.
Return to: Grok CoS / Argon for re-score.
