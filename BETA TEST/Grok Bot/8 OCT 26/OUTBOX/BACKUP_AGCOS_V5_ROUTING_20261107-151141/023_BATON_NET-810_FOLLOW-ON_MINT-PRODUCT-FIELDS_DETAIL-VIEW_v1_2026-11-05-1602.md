# BATON_NET-810 — FOLLOW-ON (v2 item) — Mint product fields in coin detail view
**From:** Antigravity Desk (per Chief of Staff)  
**To:** AG CoS v4 (ba2bfdb2 / PAYG numista-qc)  
**When filed:** 5 Nov 2026 ~4:02 PM ET  
**Type:** FOLLOW-ON plan only — **NO EXECUTE / NO CODE / NO DEPLOY / NO MERGE**  
**Queue position:** **LAST** — after NET-808, NET-809, NET-806/807 (Argon), and the five 26 Nov must-ships. Do not start this before those are clear of the active queue.

## Origin
Eric asked Catalog Builder at 4:01 PM ET (5 Nov 2026) for Mint product fields in the coin detail view. CoS handed Desk the box paths and display rules. Desk copied the source files into this baton package.

## Fields (all optional)
1. `product_price_usd`
2. `mint_schedule_status`
3. `product_availability`
4. `release_time_et`

## Display rules (must appear in the AG plan)
- Detail view only (not on cards).
- Label price **"U.S. Mint issue price"** — never "value" or market price.
- No buy links and no urgency wording.
- Hide a field when it is null or `UNKNOWN`.
- Prefer `mint_schedule_status` when both status fields are set.
- `release_time_et`: show with `release_date` only when both are set (e.g. "Nov 12, 2026, noon ET").
- These 4 fields go on the publish allow-list only after the normal Review Cycle. Until then they are dropped by default.

## Attached sources (copied into this baton package)
- `SCHEMA_DIFF_product_price_mint_schedule_20261105.json` (from `/workspace/catalog-preview/`)
- `Plan.v1_catalog_Mint_product_fields_excerpt.md` — section **"5 Nov update: Mint product fields"** from `/workspace/catalog-builder/Plan.v1_catalog.md`

## Review Cycle (standing rule — no shortcuts)
1. AG writes plan (plan only)
2. Argon review
3. GB CoS score **95+**
4. SAG
5. Eric's **typed YES**
6. Only then EXECUTE (separate baton) — **not this baton**

## Locks
- `origin/main` stays at `9f04550a`
- Stripe OFF
- No Firestore without separate Eric YES
- No PII / AJ identifiers
- No auto-GO / Always Proceed

## Deliverable for this baton
Write a plan-only doc (suggested name: `PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.md`) that:
- Incorporates the schema diff and display rules above
- States detail-view-only UX
- States Review Cycle gate before any fold into production
- Does **not** claim code already removed/added on live/dev without proof
- Files DONE + Argon review baton when plan is ready

## ACK
AG CoS v4: ACK this baton on RADIO NET / WHOSE_TURN when you pick it up — only after 808 → 809 → 806/807 clear + five 26 Nov must-ships ahead of it.
