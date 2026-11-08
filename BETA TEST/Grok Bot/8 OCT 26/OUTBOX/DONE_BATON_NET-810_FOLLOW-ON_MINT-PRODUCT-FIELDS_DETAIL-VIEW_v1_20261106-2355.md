# DONE_BATON: NET-810 — FOLLOW-ON — Mint product fields in coin detail view (v1)

**DTG:** 2026-11-06 23:55 ET  
**Original Baton:** `BATON_NET-810_FOLLOW-ON_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1_2026-11-05-1602.md`  
**Delivered By:** Antigravity Chief of Staff v4 / Catalog Night Team  
**Delivered Plan:** `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.md`  
**Review Baton Filed:** `BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1_20261106-2355.md`  

---

## Deliverables & Status
1. **Plan Authoring Complete:** Authored `PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.md` incorporating all schema diff elements from `SCHEMA_DIFF_product_price_mint_schedule_20261105.json` and rules from `Plan.v1_catalog_Mint_product_fields_excerpt.md`.
2. **Strict Display Rules Codified:**
   - **Detail View Only:** Displayed exclusively in `_DetailsTab` / Overview modal. Never rendered on collection cards, browse cards, or search cards.
   - **Exact Issue Price Label:** Labeled strictly `"U.S. Mint issue price"` — never `"value"`, `"market price"`, or `"retail price"`.
   - **No Buy Links / Urgency:** Zero external buy buttons, affiliate links, or urgency phrasing.
   - **Fail-Closed Null / UNKNOWN:** Null, empty, zero, or `"UNKNOWN"` values suppressed completely.
   - **Status Precedence:** `mint_schedule_status` preferred over `product_availability`.
   - **Release Timing:** `release_time_et` displayed exclusively when paired with a valid `release_date`.
   - **Publish Allow-List Gate:** All 4 fields dropped by default until Review Cycle completion and Founder Eric typed YES.
3. **Review Cycle (No Argon):** Forward baton filed for Grok Bot CoS review ($\ge 95$) followed by Stand Alone Grok review ($\ge 95$) and Founder Eric typed YES.
4. **Standing Locks:** `origin/main` locked at `9f04550a`; Stripe strictly OFF; zero Firestore writes/seeding; PLAN ONLY.
