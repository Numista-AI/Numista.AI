# GB CoS score — NET-814 Soft-404 / Public Catalog / Pricing v1.4

**75/100 — FAIL.** Pass requires 95+. Not ready for SAG, Eric YES or execution.
Reviewed Sat 7 Nov 2026, ~7:55–8:00 PM ET (America/New_York). Baton `BATON_NET-814_GROKCOS_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_v1.4_20261107-1950.md` (mtime 19:52 ET, stamp 19:50 — fine). Plan `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.4.md` (875 lines, mtime 19:51 ET; mirror `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.4.md`). Delivery commit **24cbf812** (19:53 ET). Writer AG CoS v5 `cfe23a7a`, attempt **2/4** (v1.3 78 FAIL). Next: **v1.5 attempt 3/4**.

## Evidence
`git show 4d17ca5e:numista_mobile/firebase.json`, `git show origin/dev:numista_mobile/firebase.json`, `git show origin/dev:numista_mobile/assets/catalog/catalog_public_v1.json` (parsed: 3,202 records), `git cat-file -e` for every new artifact path. origin/main 9f04550a locked. Stripe OFF. PLAN ONLY. No builds/tests/writes/deploys/messages.

## Prior CoS-78 must-fix closeout
| # | Must-fix | v1.4 | Evidence |
|---|---|---|---|
| 1 | Real Hosting rollback | **Mostly closed** | Console release history + REST `v1beta1/sites/numista-vault/releases`, bare ID via `awk -F/ '{print $NF}'`, `hosting:clone numista-vault@<ID> numista-vault:live`. Gap: `.releases[1]` is the release *before* current live if captured pre-deploy (Gate) — capture `[0]` pre-deploy or say "post-deploy, previous = [1]". Revert loop has ancestry check + `--abort`, but reverts in file order — reverse it (newest first). |
| 2 | Per-coin raw HTML + honest unknown-NAC | **Partial** | Generator `tool/generate_catalog_html.dart` → `build/web/catalog/<nac>/index.html` with per-coin canonical/OG; honest statement that invalid NAC is HTTP 200 + noindex. Gaps: generator does not exist at pin or dev (OK if marked To be authored — it is not marked); tests only check files exist in `build/`, not served status/body on preview for valid coin, invalid NAC, `/catalog`, `/pricing`, and an unrelated bad path (404). `trailingSlash: false` + directory `index.html` resolution must be proven on the preview channel. |
| 3 | Real image emitters | **Closed** | `isApprovedCatalogImageUrl` = the three verified GCS buckets + Form A on `studio-9101802118-8c9a8.firebasestorage.app` + `assets/catalog/images/`. Invented `numista-vault` bucket struck. Mintage `source_url` → plain text kept. |
| 4 | Name the CPG feed artifact | **Not closed** | `numista_backend/data/cpg_retail_feed_v2026.11.json` and `numista_backend/_scripts/join_cpg_catalog_feed.py` do **not exist** at pin or origin/dev. "CDN Publishing CPG® data reference agreement" is asserted with no document — do not claim a license that has not been shown. Dev public JSON has **0** non-null `cpg_retail`. Either name a real file, or mark feed + license as **to be acquired (Eric decision)** and ship "Valuation Pending" for all rows until then. |
| 5 | Importable tests that can fail | **Partial** | `package:numista_ai/` imports and census on `catalog_public_v1.json` — good. But routing test pumps `CatalogBrowseScreen` directly, not `main.dart` dispatch; static HTML Python test asserts on `build/web/catalog/US-1921-MORGAN/index.html` — that NAC does not exist (see must-fix 2). |
| 6 | Handoff hygiene | **Closed** | Stamp ≈ mtime; attempt 2/4 stated; mirrors named; `_CatalogNotFoundBanner` consistent. |

## Numbered blocking must-fixes (v1.5)
1. **Do not replace `firebase.json` — merge into it.** §3.4 publishes a full `rewrites` and `headers` array that **drops** pin rewrites `/add_coins.html`, `/scraper_dashboard.html`, `/privacy → /privacy.html`, `/terms → /terms.html`, `/index.html` (pin lines ~58–72, 110) and pin headers for `/index.html`, `/`, `/flutter_service_worker.js`, `/flutter_bootstrap.js` (no-cache). Losing `/privacy` and `/terms` breaks legal pages (Play listing); losing SW/bootstrap no-cache risks stale app shells. Show a minimal diff vs `git show 4d17ca5e:numista_mobile/firebase.json` (and reconcile dev's `/catalog`, `/catalog/** → /index.html` at dev 132–139) that only adds the catalog/pricing entries.
2. **Use real NAC codes everywhere.** `US-1921-MORGAN` and `US-1909-S-VDB-CENT` are not in `catalog_public_v1.json`; real codes look like `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3`. Fix the sample HTML, feed schema, smoke URLs and the Python test. Sample OG copy claims mintage 44,690,000 and "CPG retail pricing", but that record's `mintage.value` is null and no record has CPG — generate description only from non-null fields.
3. **CPG feed/licence honesty** (prior MF-4): see table. No licence claim without a document; mark acquisition as an Eric decision; keep fail-closed "Valuation Pending".
4. **Census description:** the 3,202 records are 2,965 coins / 181 notes / 56 medals, not only "coinage… proof/mint sets"; §5.2 status badges have no source field in the JSON — name the field or drop the badge claim. "Foreign excluded" needs a check (country field or NAC `.US.` segment test).
5. **Served-response tests on the preview channel:** curl/raw-body checks for one real per-coin URL (200 + per-coin canonical), invalid NAC (200 + `noindex`), `/catalog`, `/pricing`, `/privacy`, `/terms` (200), and an unrelated bad path (404). Add a `main.dart` routing test (or state why the dispatch is untestable and cover it in preview smoke).
6. **Rollback nits:** capture `releases[0]` pre-deploy (or document ordering); reverse revert order; mark generator/feed/join script **To be authored** in a file manifest.

## Rubric
| Dimension | v1.3 | v1.4 |
|---|---:|---:|
| Ground truth / census / marketing | 18 | 15/20 |
| User direction / options / launch fit | 16 | 16/20 |
| Routing / AuthGate / static HTML | 16 | 13/20 |
| Public privacy / retail / images | 15 | 15/20 |
| Rollback / alerts-only / implementability | 13 | 16/20 |
| **Total** | **78** | **75/100 FAIL** |

Real closes: Hosting REST capture + `@` clone, image emitters, honest crawler status, per-coin HTML concept, package imports. The score drops because the firebase.json block would delete live legal/tool rewrites and no-cache headers, the examples and tests use NAC codes that do not exist, and the CPG feed/licence is still not a real artifact.

No AJ PII found. No authority granted. Sequence: CoS 95+ → SAG 95+ → Eric typed YES; separate preview/live gates. No messages sent, no Eric ping.
