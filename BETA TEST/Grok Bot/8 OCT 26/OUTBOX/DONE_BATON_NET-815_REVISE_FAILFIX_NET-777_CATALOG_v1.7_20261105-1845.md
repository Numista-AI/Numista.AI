# DONE BATON NET-815 — AG CoS v4 Completed Catalog FAILFIX Plan v1.7
**From:** Antigravity CoS v4 (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Date:** 5 November 2026, 6:45 PM ET  
**Source Baton:** `BATON_NET-815_REVISE_FAILFIX_NET-777_CATALOG_v1.7_PER-COS-64-SAG-74_2026-11-05-1810.md`  
**Deliverable File:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md` (and mirrors in `BATONS/` and `RADIO NET/`)  
**Forward Review Baton:** `BATON_NET-815_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.7_20261105-1845.md`  
**Protocol:** Argon DROPPED per Eric YES 6:07 PM ET. Forward chain: AG plan -> GB CoS (>=95) -> SAG (>=95) -> Founder Eric typed YES.  
**Mode:** PLAN ONLY. Zero code execution, zero deployments, zero Firestore writes/seeding or security rules changes.

---

## Summary of All 6 Must-Fix Resolutions in Plan v1.7:

1. **Retail Attached Directly to Real Card (`_CatalogCard.build`, lines 1079–1150):**
   - Grounded in `_CatalogCard.build` on `origin/dev:1079–1150`.
   - Extracts `valCpg = (item['cpgRetail'] as num?)?.toDouble()`.
   - Unconditionally renders formatted CDN CPG retail (`$XX.XX`) when `valCpg != null && valCpg > 0`.
   - Renders gold `'Valuation Pending'` chip strictly when `valCpg == null || valCpg <= 0`.
   - Positive retail always wins over pending flag; zero or missing gets gold pending chip.
   - Sourced migration script `scripts/migrate_catalog_cpg_retail.py` defined to populate `catalog_public_v1.json` with CPG retail data.
   - Strictly ZERO wholesale, ZERO AI price, ZERO melt price, ZERO cost fallback.

2. **Real Image Path Closed, Host Guard & CSP Citation Corrected:**
   - Grounded in real schema: `item['primary_image']` and `item['type_image']` maps, not `primary_image_url`.
   - Accurately cites real CSP at `firebase.json:283–284` (`Strict-Transport-Security` is lines 275–276).
   - Card lines 1105–1109 patched with strict pre-fetch allowlist guard (`_isAllowedImageUrl(rawUrl)`): all 167 external URLs fail closed before network fetch and render `_buildPlaceholder()`.
   - AI replicas strictly restricted to `ai_replica_images`; never in primary/type/card/index slots.
   - Sanitized image credit strings: institutional attribution only; individual collector personal names scrubbed.

3. **B05N-14: Coin Type AND Series Matching in Known Errors:**
   - Patched `MintErrorService.getErrorsForCoin` to require `series` and `coinType`.
   - Filter requires coin type AND series to match error record.
   - Empty years / unknown series fail closed (return zero matches).
   - Patched `_KnownErrorsTabState` in `coin_detail_screen.dart:3470–3520` and Greysheet request path to pass `series` and `coin_type`.
   - Regression tests: 1999 NJ state quarter clipped-planchet error cannot match 1958 Washington quarter; positive same-series case included.

4. **B05N-15: Complete Removal of Google Images External Search & Kaggle Fallbacks:**
   - Deleted Google Images button from `my_collection_screen.dart:3531–3538`.
   - Deleted `_onSearchGoogle` method from `my_collection_screen.dart:4387–4405`.
   - Deleted "Similar in Reference Library" / Kaggle datasets panel from `my_collection_screen.dart:5560–5639`.
   - Replaced indefinite loading spinner with clean bounded terminal state ("No reference photos in official library").
   - Scrubbed Kaggle text from `microscope_scan_screen.dart:1335` and `lib/widgets/common/ref_image_widget.dart:47`.
   - Zero off-site photo actions; only permitted outbound link is Congress.gov on the Laws tab.

5. **Spend Readiness Operational Runbook:**
   - Labeled automated $20 email via Cloud Functions / PubSub honestly as UNBUILT / FUTURE INFRASTRUCTURE.
   - Pre-ad runbook established with Founder Eric as primary operator and Grok Bot CoS as backup.
   - GCP budget thresholds mapped at $10 (40%), $18 (72%), $20 (80%).
   - Hourly monitoring cadence during active ad traffic.
   - Exact manual shutoff commands verified: `firebase hosting:channel:delete pre-ads-preview` / `firebase hosting:disable`.
   - Zero shutoff commands executed during plan review or testing.

6. **Target Branch Pinned & Clean Revert Scope:**
   - Target branch: `origin/dev` at pre-execute HEAD `b0b058087f1492244a0c0b769e126b38ac1ba06c`.
   - Deep-link citation corrected to lines 71–81 in `catalog_browse_screen.dart`.
   - Rollback specification: `git revert <execute commit set>` cleanly returning `dev` to `b0b05808`, plus Firebase Hosting release rollback. Zero checkouts of stale `18a8b8e5` or locked `9f04550a`.

---

## Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- PLAN ONLY.
