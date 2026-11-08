# ACK_BATON_NET-815_REVISE_FAILFIX_NET-777_CATALOG_v1.7_20261105-1830

- **To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 6:30 PM ET
- **Subject:** ACKNOWLEDGED BATON_NET-815 (Catalog FAILFIX v1.7 per CoS 64 / SAG 74 — Argon Dropped)

Acknowledged receipt of `BATON_NET-815_REVISE_FAILFIX_NET-777_CATALOG_v1.7_PER-COS-64-SAG-74_2026-11-05-1810.md` and `WAKE_AGCOS_v4_NET-815_FIRST_2026-11-05-1822.md`.
Acknowledged protocol change: **Argon Reviewer dropped per Eric typed YES in FIN OPS (6:07 PM ET 5 Nov)**. Forward chain is strictly AG CoS v4 $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES. On completion, filing `BATON_NET-815_GROKCOS_REVIEW_...`.

Priority execution: **`NET-815` Catalog FAILFIX v1.7 taken FIRST (Thanksgiving Critical Path)**. Pausing `NET-812` until `NET-815` is DONE.

Addressing all 6 blocking must-fixes in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md`:
1. **Retail Attached to Real Card Widget (`_CatalogCard.build`):** Grounding valuation in lines 1079–1150 of `catalog_browse_screen.dart`. In `_CatalogCard`, extracting `valCpg = (item['cpgRetail'] as num?)?.toDouble()`. Unconditionally rendering formatted CDN CPG retail price when `valCpg > 0`. Rendering gold `'Valuation Pending'` chip strictly when `valCpg <= 0` or null. Defining sourced retail migration/fallback for `catalog_public_v1.json` (3,202 entries); rejecting wholesale.
2. **Close Real Image Path:** Recognizing JSON structure uses `primary_image` / `type_image` maps (e.g. `imgMap['url']`), and card lines 1105–1109 feeds this to `Image.network`. Correcting CSP citation to `firebase.json:283-284`. Adding strict pre-fetch host/path validation; rejecting external URLs (155 upload.wikimedia, 10 thumb.wikimedia, 1 Met, 1 ANS) before network fetch and falling back to clean SVG silhouette placeholder. Confining AI replicas strictly to `ai_replica_images`.
3. **B05N-14 (Coin Type & Series Matching):** Specifying same coin type AND series matching in `MintErrorService.getErrorsForCoin`, `_KnownErrorsTab`, and Greysheet request path. Empty years / unknown series fail closed. Adding regression tests (e.g., 1999 NJ state quarter clipped-planchet error cannot match 1958 Washington quarter).
4. **B05N-15 (Remove Google Images External Search):** Removing Google Images button and `_onSearchGoogle` external action from `my_collection_screen.dart` (3531–3538, 4387–4405), Similar/Kaggle panel (5560–5639), and Kaggle references in `microscope_scan_screen.dart:1335` and `ref_image_widget.dart:47`. Bounded terminal state instead of spinner.
5. **Spend Readiness Runbook:** Labeling automated $20 email unbuilt until provisioned. Providing complete pre-ad runbook: verified budget mapping, test notification, accountable human owner (Eric) + backup (Grok Bot CoS), monitoring cadence, command verification.
6. **Branch Specification & Deep-Link Cite:** Grounding execution on `origin/dev` pre-execute HEAD `b0b058087f1492244a0c0b769e126b38ac1ba06c`. Deep-link cited at lines 71–81. Clean rollback via `git revert <execute commit set>` back to `b0b05808`.

Mode: STRICT PLAN ONLY. Locks intact (`origin/main` at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes).
