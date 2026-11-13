# COS_SCORE — NET-814 Soft-404 / Public Catalog / Pricing v1.6
- **Track:** NET-814
- **Artifact:** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.6.md` (byte-identical `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.6.md`)
- **SHA256:** `ad6a3a18c431aee9501dc084d8da3d20769d12427e813a86050daccb6ce7d685` (56,548 bytes) — matches baton
- **Review baton:** `BATON_NET-814_GROKCOS_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_v1.6_20261107-2145.md`
- **Scorer:** Grok Bot CoS (GROKCOS)
- **DTG:** 2026-11-07 ~9:52 PM ET (America/New_York)
- **Pin:** `git show 4d17ca5e`. Public routing / catalog cites vs `git show origin/dev`.
- **Attempt:** 4/4 LAST TRY
- **Prior:** v1.3 **78** FAIL; v1.4 **75** FAIL; v1.5 **86** FAIL
- **Result:** **90 / 100 FAIL** (pass threshold 95)
- **Revision attempts:** **EXHAUSTED.** No v1.7 revise wake. Hold for morning / Eric. No Eric ping.

## Rubric
1. Ground truth, census, and marketing honesty — **18 / 20** (census and NAC samples remain honest; the canonical 1921-P HTML sample still invents an OG image)
2. User direction, options, and launch-week fit — **17 / 20**
3. Routing, AuthGate, and static HTML plan — **19 / 20** (`main.dart` 154–181 and pin `firebase.json` labels now match; `item['nac']` vs real `nac_code` is the leftover wire-up nit)
4. Public privacy, retail values, and images — **17 / 20** (chip color aligned; invented `og:image` / `twitter:image` remain in §3.4)
5. Rollback, alerts-only, and implementability — **19 / 20** (`extractInitialNac` tests + why-`main()`-is-untestable note; privacy test added to §7.5; helper should live in production code, not only as a copy inside the test file)

**Total: 90 / 100 FAIL**

## What closed vs CoS-86
- **MF-1 CLOSED.** `git show origin/dev:numista_mobile/lib/main.dart` public catalog dispatch is quoted at **154–181** (`// Public Catalog direct entry` through `CatalogBrowseScreen(initialNacCode: initialNacCode)` / `return;`). Lines **215–245** are correctly identified as the `kApiBaseUrl` / `Firebase.initializeApp` timeout error UI. Whitelist `:133–134` and import `:12` match.
- **MF-2 CLOSED** for citations. Origin/dev `catalog_browse_screen.dart` is quoted at the real sites: `:466` `onTap: () => _showItemDetailModal(item),`; `:80` `_showItemDetailModal(match);`; `:810` `void _showItemDetailModal(Map<String, dynamic> item) {`; `:315` is correctly `child: Column(`. Remaining nit (see below): the NET-813 handoff sentence uses `showPublic(context, nacCode: item['nac'])` — catalog records use `nac_code`, and NET-813's `showPublic` takes a `PublicCoinProjection`.
- **MF-3 CLOSED.** Pin `firebase.json` rewrite `source` entries run through `/claim/**` at **line 130**, array close at **133**, `"headers": [` at **135**, first rule `"source": "**/*.@(js|css|wasm)"` at **137**. Surgical merge content from v1.5 is preserved. (Line 51 is the first `"source": "/api/**"` entry; `"rewrites": [` itself is line 49.)
- **MF-4 CLOSED enough.** §9.2 adds `extractInitialNac(Uri uri)` unit tests for bare `/catalog`, `/catalog/<nac>`, `?item=<nac>`, and a non-catalog path, and explains why top-level `void main()` is untestable in headless `testWidgets` (browser globals + `Firebase.initializeApp`), with preview curls covering served HTML. Note: the helper is shown inside the test file; implementers must extract it into production code imported by both `main.dart` and the test, or the unit tests only exercise a local copy.
- **MF-5 NOT closed.** The baton and §11 claim the 1921-P sample omitted `og:image` / `twitter:image` and switched `twitter:card` to `summary`. The actual §3.4 sample HTML still contains:
  - `<meta property="og:image" content="https://storage.googleapis.com/us_mint_coin_images/1921_morgan_dollar_obverse.png" />`
  - matching `og:image:width` / `height` / `alt`
  - `<meta name="twitter:card" content="summary_large_image" />`
  - `<meta name="twitter:image" content="https://storage.googleapis.com/us_mint_coin_images/1921_morgan_dollar_obverse.png" />`
  Verified against `catalog_public_v1.json`: `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` has `primary_image`, `type_image`, `secondary_image`, and `extra_images` all null (`image` / `image_url` keys are absent). Mintage is `{value: null, label: 'not yet sourced', source_url: null}` — the prose correctly omits a mintage figure, and present fields (name `1921-P Morgan Silver Dollars`, year `1921`, denomination `Dollar`, series `Morgan Silver Dollars`, composition `90% Silver`, era `Barber to Golden Age (1892–1932)`) match the record.
- **MF-6 CLOSED.** Valuation Pending is consistently a slate gray chip (`#F1F5F9` / `#64748B`) in §1, §6.2, and §6.3. No leftover "gold chip" rendering instruction.
- **MF-7 CLOSED.** `numista_mobile/test/services/catalog_census_privacy_test.dart` is in the §7.5 file-manifest table (To be authored upon Eric YES).
- **MF-8 CLOSED.** §11 records v1.5 delivery commit `4a124977` and the v1.6 delivery.

Census re-verified this run: `git show origin/dev:numista_mobile/assets/catalog/catalog_public_v1.json` is 3,202 rows = 2,965 `coin`/`CN` + 181 `note`/`BN` + 56 `medal`/`MD`. `status_badge`: Needs source 1,724 / Details coming 950 / Pre-Federal 9 / null 519. Foreign check `parts[2]=='US'` matches (0 foreign). `cpg_retail` non-null on 0 rows. `is_placeholder`: false 2,251 / true 951.

## Remaining defects (4/4 exhausted — recorded, not a revise order)
1. **Omit invented OG/Twitter images for the 1921-P Morgan sample.** `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` has null image fields. Do not emit `og:image` / `twitter:image` (or the invented `https://storage.googleapis.com/us_mint_coin_images/1921_morgan_dollar_obverse.png`). Use `twitter:card` `summary`. For an OG-image demo, pick a row that actually has `primary_image.url` (for example the 1787 Fugio cent) or omit the tags when null. A baton claiming the tags were omitted is not evidence — the §3.4 HTML still contains them.
2. **Align the public showPublic wire-up with the catalog key and NET-813 API.** Use `item['nac_code']` (not `item['nac']`) and/or `PublicCoinProjection.fromCatalogMap(item)` as specified in NET-813. `item['nac']` is not a key on public catalog records.
3. **Keep `extractInitialNac` in production code** imported by `main.dart` and by the unit test, so the tests do not only exercise a copy pasted into the test file.

## Notes (not blocking alone)
- Surgical `firebase.json` merge, honest CPG-to-be-acquired story, AuthGate `publicRoute` move, preview curls, and `releases[0]` rollback remain as previously closed.
- Marketing "3,200+" vs verified 3,202 is fine.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. Attempt 4/4 exhausted — no further revise wake. No Eric ping.
