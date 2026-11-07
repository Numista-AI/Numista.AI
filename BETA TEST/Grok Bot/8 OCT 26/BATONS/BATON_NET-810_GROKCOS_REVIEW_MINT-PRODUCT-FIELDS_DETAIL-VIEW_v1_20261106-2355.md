# BATON: NET-810 — Grok Bot CoS Review — Mint product fields in coin detail view (v1)

**DTG:** 2026-11-06 23:55 ET  
**From:** Antigravity Chief of Staff v4 / Catalog Night Team  
**To:** Grok Bot Chief of Staff (GB CoS), Stand Alone Grok (SAG, grok-4.7)  
**Deliverable Under Review:** `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.md`  
**Review Target:** Dual independent review scoring $\ge 95 / 100$  
**Action:** Audit and score `PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.md`. If $\ge 95$, pass forward for SAG review and Founder Eric typed YES.  

---

## 1. Scope & Verification Points Under Audit
1. **Schema Diff Fidelity:** Full alignment with `SCHEMA_DIFF_product_price_mint_schedule_20261105.json` for all 4 optional fields (`product_price_usd`, `mint_schedule_status`, `product_availability`, `release_time_et`).
2. **Display Rules Enforced:**
   - Detail view only (not on cards).
   - Price labeled strictly `"U.S. Mint issue price"` — never `"value"` or market price.
   - Zero buy links, zero urgency wording.
   - Hide fields when null, empty, `<= 0`, or `"UNKNOWN"`.
   - Prefer `mint_schedule_status` when both status fields are set.
   - `release_time_et`: show with `release_date` only when both are set (e.g. `"Nov 12, 2026, noon ET"`).
   - Publish allow-list gate enforced: fields dropped by default until Review Cycle and Founder Eric typed YES.
3. **Compiling Code Architecture:** Model parsing/serialization in `CoinModel`, resolution helper `MintProductHelper`, and widget layout in `_DetailsTab` (`coin_detail_screen.dart:1526`).
4. **Automated Test Coverage:** Unit and widget test suite in `numista_tests/mint_product_fields_test.dart`.
5. **Operational Boundaries:** Strict PLAN ONLY. `origin/main` locked at `9f04550a`. Stripe strictly OFF. Zero Firestore writes. Zero PII. Argon dropped per Eric 5 Nov 18:07 ET order. Zero pings to Eric overnight.
