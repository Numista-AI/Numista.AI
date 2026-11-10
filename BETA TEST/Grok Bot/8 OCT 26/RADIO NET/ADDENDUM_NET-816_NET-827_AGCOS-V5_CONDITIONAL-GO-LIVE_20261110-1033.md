# ADDENDUM — NET-816 + NET-827 CONDITIONAL GO-LIVE (AG CoS v5)
Filed: 2026-11-10 10:33:34 EST by Grok Bot Desk. **CONDITIONAL / NOT ACTIVE. No WAKE.**
Desk files this addendum only — Desk does **not** deploy, run git, Firebase, Stripe, or Secret Manager, and does not start production work.
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)

**This addendum does not amend the two referenced baton files** (their bytes stay unchanged) and **does not activate anything now.**

## Referenced batons (Desk-verified on disk; unchanged)
1. `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md`  
   SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c` — MATCH (box evnote; 3663 B)
2. `BATON_NET-827_AGCOS-V5_QUEUED-PREVIEW-BUILD_STRIPE-CHECKOUT-PREVIEW_v1.2_p7-gate_20261110-1031.md`  
   SHA-256 `6693232a39993ddb3e4b678d439a0cd37a91217a148f0fcb8e6d4ed0ec2c1175` — MATCH (box evnote; 3938 B)

Those batons remain preview-only / queued preview-build as filed. This addendum is a **later, conditional** production path only.

## Authority (provenance stated honestly)
**(a) Desk-verified primary** — Eric's typed text in Chief of Staff chat, transcript position **9501**, **2026-11-10 10:29:50 AM ET**, owner message `t2465u`:
> A, but if Field Tester passes it in the 90+ range, lets go live, we need to start testing stuff 'Real World'

**(b) CoS-relayed, NOT independently visible to Desk** — Eric's answer to CoS card `t2465s9506` at **10:32 AM ET**, to the card question “If Field Tester scores 90 or higher, what goes live?”:
> If Field Tester scores 90+, deploy both to live numista.ai and turn on real Stripe payments

Treat **(b)** as **CoS-relayed**, not Desk-verified card/widget text. The production-scope details below (targeted fold to main, Secret Manager, prerequisites, stop rule) are **CoS-specified implementation** of that answer, not a new Desk-invented authority.

## STATUS: CONDITIONAL / NOT ACTIVE
**Trigger:** Field Tester files a result of **90+** on each preview, **NET-816 then NET-827**.
AG may **NOT** start production on its own reading of an FT result. **CoS confirms each trigger in a written file first**; only then may that production step begin.
Filing this addendum ≠ trigger confirmation, ≠ accepted/started, and ≠ go-live authorization today.

## Production scope (only after CoS written trigger confirmation for that step)
1. Fold **only** the exact FT-tested commits into **main** as a targeted change. **Never** merge all of dev into main. **Never** rewrite history or force-push. Record main SHA **before** (currently locked `9f04550a`, source-stated) and **after**.
2. Deploy to **live numista.ai** hosting.
3. Switch Stripe to **live mode** with live keys held in **Secret Manager only**.

## Stripe live prerequisites
Any missing item means a named **BLOCKED** — never a workaround:
- Stripe account activated for live charges
- Live keys and live webhook secret in Secret Manager, supplied by Eric or his own Stripe login; **no agent creates or reads them in chat**
- Live webhook endpoint registered

Christmas promotion code **must not** be active in live mode before **26 Nov 2026 00:00:00 UTC**.

## Still excluded
- Catalog fold
- Live Firestore data migrations beyond what the tested plans require
- Any spend
- Argon Reviewer
- No workaround if blocked

## Required DONE evidence (only if a confirmed step actually runs)
- Main SHA before and after
- Live hosting release hash and ET / America/New_York time
- Stripe live mode confirmed on, with webhook endpoint ID
- Prepared rollback command
- Smoke check that numista.ai, /catalog, and checkout load
- Agent charges **no** real card

## STOP RULE
If Field Tester names any defect that could charge someone the wrong amount, give wrong access, or lose data, **do not ship even at 90+**. File **BLOCKED** and CoS takes it to Eric.

## Required returns
1. **ACK** of this addendum as received/understood: **conditional / not active**; no production start until CoS written trigger confirmation.
2. After a CoS written trigger: **PROGRESS** / **DONE** with the evidence above, or **BLOCKED** with a named blocker (no workaround; no peer contact).
