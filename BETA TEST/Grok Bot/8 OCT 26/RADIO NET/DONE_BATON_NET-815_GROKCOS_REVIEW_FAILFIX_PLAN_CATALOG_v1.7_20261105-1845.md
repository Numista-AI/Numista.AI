# BATON NET-815 — Grok Bot CoS Review: Catalog FAILFIX Plan v1.7 (Thanksgiving Critical Path)
**From:** Antigravity CoS v4 (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Date:** 5 November 2026, 6:45 PM ET  
**Plan Deliverable:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md` (and mirror in `BATONS/` & `RADIO NET/`)  
**Previous Scores on v1.6:** Grok Bot CoS: 64 FAIL; SAG: 74 FAIL.  
**Review Gate:** Grok Bot CoS (>= 95 PASS) -> Stand Alone Grok (SAG, >= 95 PASS) -> Founder Eric typed YES.  
**Protocol Note:** Argon is DROPPED per Founder Eric typed YES 6:07 PM ET in FIN OPS. Forward baton is filed directly to GROKCOS_REVIEW.  
**Mode:** PLAN ONLY. Zero code changes, zero deployments, zero Firestore writes/seeding or security rules changes.

---

## Deliverables for Review:
1. `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md`
2. `BETA TEST/Grok Bot/8 OCT 26/BATONS/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md`
3. `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md`

## 6 Blocking Must-Fix Verification Points:
1. **Retail Attachment to Real Card Widget (`_CatalogCard.build`):**
   - Grounded in `_CatalogCard.build` (`origin/dev:1079–1150`).
   - Extracts `valCpg = (item['cpgRetail'] as num?)?.toDouble()`.
   - Displays formatted CDN CPG retail (`$XX.XX`) unconditionally when `valCpg > 0`.
   - Displays gold `'Valuation Pending'` chip strictly when `valCpg <= 0` or null.
   - Sourced migration defined for `catalog_public_v1.json` (currently 3,202 entries, zero `cpgRetail`).
   - Strictly zero wholesale, zero AI valuations, zero melt, zero cost fallback.
2. **Close Real Image Path & Correct CSP Citation:**
   - Grounded in real schema: `item['primary_image']` and `item['type_image']` maps, NOT `primary_image_url`.
   - Real CSP cited accurately at `firebase.json:283–284` (lines 275–276 is `Strict-Transport-Security`).
   - Strict pre-fetch host guard in `_CatalogCard.build`: all 167 external URLs fail closed before network fetch and render `_buildPlaceholder()`.
   - AI replicas strictly restricted to `ai_replica_images`; never in primary/type/card/index slots.
   - Institutional credit attribution only; collector personal names scrubbed.
3. **B05N-14: Coin Type AND Series Matching in Known Errors:**
   - Patched `MintErrorService.getErrorsForCoin` to require `series` and `coinType`.
   - Error matching requires same coin type AND series. Empty years/unknown series fail closed.
   - Patched `_KnownErrorsTabState` (`coin_detail_screen.dart:3470–3520`) and Greysheet request path to pass `series` and `coin_type`.
   - Regression tests: 1999 NJ state quarter clipped-planchet error cannot match 1958 Washington quarter; positive same-series case included.
4. **B05N-15: Complete Removal of Google Images Search & Kaggle Fallbacks:**
   - Deleted Google Images button from `my_collection_screen.dart:3531–3538`.
   - Deleted `_onSearchGoogle` method from `my_collection_screen.dart:4387–4405`.
   - Deleted "Similar in Reference Library" / Kaggle panel from `my_collection_screen.dart:5560–5639`.
   - Bounded terminal state replaces indefinite loading spinner.
   - Scrubbed Kaggle text from `microscope_scan_screen.dart:1335` and `lib/widgets/common/ref_image_widget.dart:47`.
   - Zero off-site photo actions; only permitted outbound link is Congress.gov on the Laws tab.
5. **Spend Readiness Operational Runbook:**
   - Automated $20 email via Cloud Function / PubSub labeled honestly as UNBUILT.
   - Pre-ad runbook established: Founder Eric (Primary Operator) + Grok Bot CoS (Backup Operator).
   - GCP budget thresholds mapped at $10 (40%), $18 (72%), $20 (80%).
   - Hourly monitoring cadence during active ad traffic.
   - Verified manual shutoff commands: `firebase hosting:channel:delete pre-ads-preview` / `firebase hosting:disable`.
   - Zero shutoff commands executed during plan review or testing.
6. **Target Branch Pinned & Clean Revert Scope:**
   - Execution target pinned to `origin/dev` pre-execute HEAD `b0b058087f1492244a0c0b769e126b38ac1ba06c`.
   - Deep-link citation corrected to lines 71–81 in `catalog_browse_screen.dart`.
   - Rollback specification: `git revert <execute commit set>` cleanly returning `dev` to `b0b05808`, plus Firebase Hosting release rollback. Zero checkouts of stale `18a8b8e5` or locked `9f04550a`.

---

## Standing Locks:
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- PLAN ONLY.
