# BATON — NET-827 Stripe Checkout Preview v1.2 QUEUED PREVIEW-BUILD (AG CoS v5)
Filed: 2026-11-10 10:31:00 EST by Grok Bot Desk. **QUEUED. PREVIEW CHANNEL ONLY. Stripe TEST mode only. No WAKE.**
Desk files this baton only — Desk does **not** deploy, run Firebase, run git, touch Stripe or accounts, or start the build.
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
Track: NET-827 Stripe Checkout Preview v1.2 — p7-gate preview build/deploy, **queued** behind NET-816 field test.

## Authority
- Transcript: Chief of Staff `87de4a6a-9522-4ece-bdfb-87ad19298514` position **9501**.
- Time: **2026-11-10 10:29:50 AM ET** (America/New_York).
- Owner message `t2465u` on CoS card `t2462s9497`.
- Actual Eric typed reply, verbatim:
  > A, but if Field Tester passes it in the 90+ range, lets go live, we need to start testing stuff 'Real World'

- **Option A text as relayed by CoS** (card body **not independently visible** to Desk; treat as **CoS-relayed**, not Desk-verified card text):
  > YES, build NET-827 v1.2 on the p7-gate preview after the Catalog Chunk 1 field test; Stripe test mode only, live OFF, no main, no production

**The “go live” / “Real World” clause is NOT authorized by this baton.** CoS is confirming its meaning with Eric separately. Live payments / production are a **separate later gate**. This baton authorizes only the **queued** p7-gate preview build in Stripe **test mode**, after the start conditions below.

## Plan (AG must verify SHA before building)
- Plan: NET-827 Stripe Checkout Preview **v1.2**
- Desk-verified box file: `/workspace/net827-sag-v12/src/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md`
- SHA-256 `273a3268933f9bc1dba25812deecec6c761b3e8de58fa23b45844f1e409ed39d` (28,899 B, 425 lines) — MATCH
- CoS **96 PASS**; SAG **96 PASS** — record `/workspace/net827-sag-v12/sag-result/SAG_REVIEW_NET-827_v1.2_96_PASS_20261110.md` SHA-256 `dfb0140188de46625d42b8ea7295ad4af2fc15c8b582659a38e4783fd7c05463` (Desk-verified hash). Dual plan gate is recorded as met; that is **not** execution of live payments.

## STATUS: QUEUED — start condition
Begin build/deploy **only after both**:
1. NET-816 Catalog Chunk 1 p7-gate preview deploy **DONE** is filed; **and**
2. Field Tester has filed its result on that preview.

Until then: **read/prepare only** — no code changes, no deploy — so the two tracks do not overwrite each other on p7-gate.
Filing this baton ≠ accepted/started, and does **not** mean the start condition has been met.

## Scope (only after start condition)
- Build **exactly** per v1.2 plan on `origin/p7-v8.9`.
- Record **base SHA** and **built SHA**.
- Plan pin `56701f92` is **writer-asserted**; current tip per CoS is `999daf14`. AG must verify actual refs at build time (no Desk live git query).
- Deploy to **p7-gate preview channel only**, project `studio-9101802118-8c9a8`.
- Stripe **TEST mode only**: test keys from Secret Manager; test-mode Stripe objects only where the plan specifies.

## Excluded (hard holds)
- Stripe **live** keys / live mode.
- **main** stays `9f04550a` (source-stated).
- No production / live hosting.
- No live Firestore data.
- No catalog fold.
- No spend.
- No workaround if blocked — file a named **BLOCKED**.

## Required completion evidence — DONE
File a DONE record with:
1. Built commit SHA
2. Preview URL
3. Firebase release/version hash
4. Deploy time (ET / America/New_York)
5. List of Stripe **test-mode** objects created (IDs)
6. Confirmation **no live keys** were used and live / numista.ai / main were **untouched**

If anything blocks, file a named **BLOCKED** instead; no workaround.

## Required returns
1. **ACK** — queued behind the start condition (or start only if both conditions are already actually met); honest ETA or ETA unknown.
2. **PROGRESS** as needed after start.
3. **DONE** with the evidence listed above, or **BLOCKED** with a named blocker (no workaround; no peer contact).
