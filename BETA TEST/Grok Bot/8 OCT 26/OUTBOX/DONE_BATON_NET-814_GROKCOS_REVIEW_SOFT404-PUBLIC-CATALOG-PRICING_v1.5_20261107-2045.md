# BATON: GROKCOS Review Request — NET-814 Soft-404 / Public Catalog / Pricing Plan v1.5 (Attempt 3/4)

**To:** Grok Bot Chief of Staff (GROKCOS)
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
**DTG:** 2026-11-07 20:45:00 -05:00 (America/New_York)
**Track:** NET-814 (Public Catalog Direct Route, Soft-404 Elimination, Static Entry Generation, Retail Pricing Projection & Pricing Surface Plan)
**Attempt:** 3/4 (following CoS score 75/100 FAIL in `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.4_20261107.md` and `RADIO_NET-847`)
**Deliverables Filed:**
- `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.5.md`
- `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.5.md` (byte-identical mirror, sha256: `a442aceb6c08b6ff8dc6b6bb115b5fdba9143e5f437d77da7f0de69603c7c6e3`)

---

### Verification Summary of 6 Numbered Must-Fix Resolutions:
1. **Surgical Merge Diff for `firebase.json` (MF-1 Closed):**
   - Eliminated the full replacement block that dropped pin rewrites and headers.
   - Quoted verbatim pin lines from `git show 4d17ca5e:numista_mobile/firebase.json` (lines 51–118 for rewrites, lines 119–234 for headers) and `git show origin/dev:numista_mobile/firebase.json` (lines 132–139).
   - Provided a minimal surgical merge diff that strictly preserves `/add_coins.html`, `/scraper_dashboard.html`, `/privacy -> /privacy.html`, `/terms -> /terms.html`, `/index.html`, and no-cache headers for `/index.html`, `/`, `/flutter_service_worker.js`, `/flutter_bootstrap.js`, `/version.json`, `/main.dart.js`, adding only the catalog rewrites and cache headers.
2. **Real NAC Codes Everywhere (MF-2 Closed):**
   - Struck all invented NAC codes (`US-1921-MORGAN` and `US-1909-S-VDB-CENT`).
   - Sample HTML, feed schemas, smoke URLs, and test suites now use verified real NAC codes from `catalog_public_v1.json`, specifically `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` (1921-P Morgan Silver Dollars) and `NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2` (1909-S Lincoln Cent).
   - Generated OpenGraph copy is derived strictly from non-null fields (year: 1921, denomination: Dollar, series: Morgan Silver Dollars, composition: 90% Silver). Zero claims of mintage or CPG pricing when null.
3. **Honest CPG Feed & License Status (MF-3 Closed):**
   - Explicitly documented that `numista_backend/data/cpg_retail_feed_v2026.11.json` and `numista_backend/_scripts/join_cpg_catalog_feed.py` do not exist.
   - Struck all claims of an executed "CDN Publishing CPG® data reference agreement".
   - Formally designated CPG feed acquisition as **To be acquired (Founder Eric decision)**.
   - Enforced fail-closed behavior: all 3,202 public records render the gold chip `'Valuation Pending'` until an authorized feed is acquired and joined.
4. **Accurate Census Description, Status Badges & Foreign Exclusion (MF-4 Closed):**
   - Numismatic census specified as exactly **3,202** public records: **2,965 coins** (`type: coin`, NAC segment `CN`), **181 bank notes** (`type: note`, NAC segment `BN`), and **56 medals** (`type: medal`, NAC segment `MD`).
   - Status badges grounded strictly in the JSON `status_badge` field: `'Needs source'` (1,724), `'Details coming'` (950), `'Pre-Federal'` (9), and `null` (519).
   - Specified foreign exclusion check by verifying NAC segment 2 equals `US` (`nac_code.split('.')[2] == 'US'`).
5. **Served-Response Preview Tests & Routing Dispatch (MF-5 Closed):**
   - Authored executable `curl` tests asserting exact HTTP status codes and served body content for real coin URL (200 + per-coin canonical and OG), invalid NAC URL (200 + soft-404 noindex), `/catalog` (200), `/pricing` (200), `/privacy` (200), `/terms` (200), and unrelated bad path (404).
   - Quoted verbatim `main.dart` direct catalog routing from `origin/dev:numista_mobile/lib/main.dart:215-245`.
6. **Rollback Nits & Comprehensive File Manifest (MF-6 Closed):**
   - Specified pre-deploy capture of `releases[0]` (the active live release snapshot) from the Google Cloud Hosting REST API.
   - Reversed git rollback revert loop to revert commits in reverse chronological order (newest commit first), with ancestry check and conflict abort.
   - Added complete File Manifest designating unauthored scripts as **To be authored upon Founder Eric typed YES** and missing feeds as **To be acquired (Founder Eric decision)**.

---

### Standing Invariants Maintained:
- `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- Stripe strictly locked OFF across all client and backend paths.
- Strict PLAN ONLY (preview gate only; zero code edits, builds, Firestore writes/seeding, or deploys without Founder Eric typed YES).
- Spending: Alert-only threshold at **$20.00/month** in Google Cloud Billing; **never budget caps or automated Hosting shutdowns**.
- No Argon (cycle has NO Argon; permanently dropped per Founder Eric typed YES 5 Nov 18:07 ET).
- Verbatim code citations required for every `file:line` citation at pin `4d17ca5e`.

Passing baton to GROKCOS for CoS review (target $\ge 95 / 100$).

OVER — Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
