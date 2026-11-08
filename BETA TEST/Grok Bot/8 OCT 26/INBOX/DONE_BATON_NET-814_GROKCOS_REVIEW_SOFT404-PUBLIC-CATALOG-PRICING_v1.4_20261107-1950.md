# BATON: GROKCOS Review Request – NET-814 Soft-404 / Public Catalog / Pricing Plan v1.4

**Baton Identifier:** `BATON_NET-814_GROKCOS_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_v1.4_20261107-1950.md`  
**Track:** NET-814 (Public Catalog Direct Route, Soft-404 Elimination, Static Entry Generation, Retail Pricing Projection & Pricing Surface Plan)  
**Deliverable Plan:** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.4.md`  
**Byte-Identical Mirror:** `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.4.md`  
**Author / Sender:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Recipient / Next Reviewer:** Grok Bot Chief of Staff (`GROKCOS`)  
**Review Target:** Score $\ge 95 / 100$ PASS (Prior attempt v1.3 scored 78 FAIL per `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.3_20261107.md`)  
**Attempt Count:** **2/4**  
**Date & Timestamp:** 2026-11-07 19:50:00 -05:00 (America/New_York)  

---

## 1. Operational Context & Standing Locks
- **Codebase Pin:** `4d17ca5e`
- **Target Integration Branch:** `origin/dev`
- **Production Lock:** `origin/main` strictly locked at commit `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- **Stripe Status:** Strictly locked OFF (zero active keys or checkout endpoints).
- **Execution Gate:** Strict PLAN ONLY (preview gate only; zero code edits, builds, Firestore writes/seeding, or live production deployments without Founder Eric's typed YES).
- **Spending Posture:** Alert-only threshold at **$20.00/month** in Google Cloud Billing. **NEVER budget caps or automated Hosting shutdowns.**
- **Argon Status:** Permanently dropped from stack (Eric typed YES 5 Nov 18:07 ET).
- **Rule 6a Verbatim Cites:** Every `file:line` citation quotes actual source lines from `git show 4d17ca5e:<path>` or `git show origin/dev:<path>`.

---

## 2. CoS-78 Must-Fix Resolution Matrix

| # | CoS-78 Must-Fix Item | v1.4 Resolution & Implementable Evidence |
|---|---|---|
| **MF-1** | **Make Hosting rollback commands real & match plan** | Replaced non-existent `firebase hosting:releases:list` with supported methods: Primary official capture via Firebase Console Release History (`https://console.firebase.google.com/project/studio-9101802118-8c9a8/hosting/sites/numista-vault/releases`); automated CLI/REST capture via Cloud Hosting REST API (`sites.releases.list`) under Eric's credentials, extracting the **bare version ID** (stripping `sites/numista-vault/versions/` prefix). Kept `firebase hosting:clone numista-vault@$PRE_DEPLOY_VERSION_ID numista-vault:live`. Clarified that `channel:list` lists preview channels, not live release IDs. Enhanced git rollback with per-SHA ancestry checks (`git merge-base --is-ancestor`) and immediate `git revert --abort` on any merge conflict. |
| **MF-2** | **Specify per-coin raw HTML metadata & honest unknown-NAC status story** | Pre-generates static per-coin entry HTML files at `build/web/catalog/<nac>/index.html` during build step (`tool/generate_catalog_html.dart`). Valid coins (e.g. `/catalog/US-1921-MORGAN`) serve raw static HTML with exact per-coin `<title>`, `<link rel="canonical">`, `og:title`, `og:description`, `og:url`, and verified first-party `og:image`. **Honest Unknown-NAC Disclosure:** Documented that crawlers requesting unknown NACs receive HTTP 200 via rewrite `{"source": "/catalog/**", "destination": "/catalog/index.html"}` with catalog-level metadata. **Client-side:** Flutter Web detects missing NAC, renders persistent in-screen `_CatalogNotFoundBanner` (`Reference code "NONEXISTENT-CODE-999" was not found in the public catalog.`), and calls `window.history.replaceState({}, '', '/catalog')`. True 404 preserved for non-catalog unknown paths via `build/web/404.html`. Widget name strictly aligned to `_CatalogNotFoundBanner` everywhere. |
| **MF-3** | **Ground images on real first-party emitters** | Aligned `isApprovedCatalogImageUrl` strictly with verified emitters from `git show 4d17ca5e`: `storage.googleapis.com/{us_mint_coin_images,numista-reference-library,numista-uploads-studio-9101802118-8c9a8}`, Firebase Storage Form A on `studio-9101802118-8c9a8.firebasestorage.app`, and bundled `assets/catalog/images/**`. Struck invented bucket `numista-vault.firebasestorage.app/reference_catalog/` (`numista-vault` is the Hosting site, not a Storage bucket). Replaced external `launchUrl` hyperlink on mintage `source_url` with plain-text attribution (`(source: US Mint Records)`) in the public modal. |
| **MF-4** | **Name the CPG feed artifact** | Specified on-disk source feed path `numista_backend/data/cpg_retail_feed_v2026.11.json`, JSON schema with `nac_code`, `cpg_retail_usd`, and `as_of`, offline join script `numista_backend/_scripts/join_cpg_catalog_feed.py`, and output runtime bundle `numista_mobile/assets/catalog/catalog_public_v1.json` with fields `"cpg_retail"` and `"cpg_as_of"`. Enforced fail-closed rule (`null` renders `'Valuation Pending'`), positive precedence (`>0` formatted as `$XX.XX`), and complete exclusion of wholesale or private data. |
| **MF-5** | **Make tests importable and able to fail** | All Dart imports use `package:numista_ai/...` (matching `pubspec.yaml:1`). Pointed census tests directly at `assets/catalog/catalog_public_v1.json`. Fixed unknown-NAC string matching to include quotes: `find.textContaining('Reference code "NONEXISTENT-CODE-999" was not found in the public catalog.')`. Exercised `main.dart` routing directly. Specified static HTML tests in `test/web/static_route_html_test.py` inspecting per-coin files, catalog root, pricing, and 404. Maintained honest "To be authored upon Founder Eric typed YES" status. |
| **MF-6** | **Handoff hygiene** | Wall-clock DTG `2026-11-07 19:50:00 -05:00` aligned with file mtime. Stated Attempt **2/4** on review baton. Both plan filenames (`docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.4.md` and `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.4.md`) verified byte-identical. Aligned `_CatalogNotFoundBanner` naming throughout. |

---

## 3. Review Request & Next Turn
Antigravity Chief of Staff v5 requests Grok Bot Chief of Staff (`GROKCOS`) review of `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.4.md`.  
Target: Score $\ge 95 / 100$ PASS, clearing Track NET-814 for Stand Alone Grok (SAG) independent review and subsequent Founder Eric typed YES.
