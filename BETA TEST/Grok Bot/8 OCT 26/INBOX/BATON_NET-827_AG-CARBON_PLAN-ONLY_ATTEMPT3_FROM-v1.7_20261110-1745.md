# BATON — NET-827 Stripe fail-fix PLAN ONLY — attempt 3 of 10
From: Grok Bot CoS, 10 Nov 2026 ~5:45 PM ET
Writer: Antigravity, model Gemini 4 Carbon (Eric's choice, 10 Nov 5:43 PM ET, his own chat t2528u: "Lets try Carbon in Antigravity")
Why a new writer: Claude used both allowed tries (v1.6 84 REVISE, v1.7 86 REVISE). Eric's 4/10 rule applies: this is track attempt 3/10, Carbon writer try 1/4.

## Start from
- PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.7_CLAUDE_20261110.md (53,625 B, SHA-256 B3F956534A7AF2DE67CD6F8D897E18CAE7B7B375E0DBDF93724CEC56EA2D8650), in MY TESTING\10 NOV 2026
- CoS score record COS_SCORE_NET-827_FAILFIX-B1B5_v1.7_86_REVISE_20261110.md (17,838 B, SHA-256 E824859910136284854C688CB2E2033B75F8BC0E8755F456BE2A352CDBB33BBA), same folder. Read the whole record, including its advisories.
- Code base: a3d7dca2 on p7-v8.9.
Keep everything v1.7 got right (D2–D8 closed, Eric's binding decisions, Gold 501+, Christmas window 26 Nov 12:01 AM ET to 25 Dec 11:59:59 PM ET).

## Must close (material)
- N1: The preview backend still reaches production. main.py builds its own production Firestore and storage clients; subaccount_routes.py hard-codes production Firestore. Route every connection (all four) through the environment guard, allow the needed main.py edits, put the lock checks on the main.py coin routes, name the client the CSV route uses, and add a check that proves no preview path can reach production.
- N2: The preview app writes production Firestore directly (app Firebase config is fixed to production). The preview app must use a separate Firebase project/config, or the plan must prove that test users cannot create production data. Cleanup must cover any data, not just the login accounts.
- N3: "Locked in the app" can't work while the app reads coins straight from Firestore and the rules let owners read, create and delete. Enforce lock and coin limit in Firestore security rules (or move reads/writes behind the server), and make the lock and the CSV include coins stored under the user's email as well as their user ID.
- Advisories worth fixing: no payment ID for subscription checkouts at grant time (ledger key); existing lock function skips coins with no created_at and fails open (must fail closed).

## Limits
PLAN ONLY. No code, commits, pushes, deploys, Firestore, Stripe or Cloud Run actions. Holds 74611e05 and 41b8bd5f stand; live stays off. 3 AM ET stand-down applies.
Save the plan as PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.8_AG-CARBON_20261110.md in MY TESTING\10 NOV 2026, and file DONE with name, size and SHA-256. Next gate: CoS 95, then full-plan SAG 95, then Eric's typed YES.
