# COS_SCORE — NET-814 Soft-404 / Public Catalog / Pricing v1.5
- **Track:** NET-814
- **Artifact:** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.5.md` (byte-identical `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.5.md`)
- **Review baton:** `BATON_NET-814_GROKCOS_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_v1.5_20261107-2045.md`
- **Scorer:** Grok Bot CoS (GROKCOS)
- **DTG:** 2026-11-07 ~8:55 PM ET (America/New_York)
- **Pin:** `git show 4d17ca5e`. Public routing / catalog cites vs `git show origin/dev`.
- **Attempt:** 3/4
- **Prior:** v1.3 **78** FAIL; v1.4 **75** FAIL
- **Result:** **86 / 100 FAIL** (pass threshold 95)

## Rubric
1. Ground truth, census, and marketing honesty — **17 / 20**
2. User direction, options, and launch-week fit — **16 / 20**
3. Routing, AuthGate, and static HTML plan — **17 / 20**
4. Public privacy, retail values, and images — **18 / 20**
5. Rollback, alerts-only, and implementability — **18 / 20**

**Total: 86 / 100 FAIL**

## What closed vs CoS-75
- **MF-1 largely CLOSED.** This is a surgical merge, not a full `firebase.json` replacement. Quoted pin rewrites correctly include `/add_coins.html`, `/scraper_dashboard.html`, `/privacy` → `/privacy.html`, `/terms` → `/terms.html`, `/index.html`, and `/pricing` → `/index.html`. No-cache headers for `/index.html`, `/`, `flutter_service_worker.js`, `flutter_bootstrap.js`, `version.json`, and `main.dart.js` are preserved. The proposed diff only adds `/catalog` and `/catalog/**` rewrites plus cache headers for `/catalog/**/index.html` and `/pricing/index.html`.
- **MF-2 largely CLOSED.** Invented sample NACs (`US-1921-MORGAN`, `US-1909-S-VDB-CENT`) are struck and appear only as "struck" mentions. Real codes `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` and `NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2` are used throughout and exist in `catalog_public_v1.json`.
- **MF-3 CLOSED.** Plan honestly says the CPG feed and join script do not exist at pin or on origin/dev; no executed CDN licence; acquisition is an Eric decision; fail-closed "Valuation Pending" until then.
- **MF-4 CLOSED (verified this run).** `git show origin/dev:numista_mobile/assets/catalog/catalog_public_v1.json` is 3,202 rows = 2,965 `coin`/`CN` + 181 `note`/`BN` + 56 `medal`/`MD`. `status_badge`: Needs source 1,724 / Details coming 950 / Pre-Federal 9 / null 519. Foreign check `parts[2]=='US'` matches the file (0 foreign). `cpg_retail` is non-null on 0 rows, which matches the fail-closed story. Marketing "3,200+" vs 3,202 is fine.
- **MF-6 largely CLOSED.** Pre-deploy capture is `releases[0]`; revert is newest-first with ancestry + abort; file manifest marks the generator and tests as To be authored and the CPG feed as To be acquired.
- **AuthGate and public_info cites match pin.** `public_info_screens.dart` `:362` / `:396` / `:407` / `:412` and `auth_gate.dart` `:101–103` / `:106–148` / `:157–159` match `git show 4d17ca5e`. Moving `publicRoute` immediately after waiting is the right fix.
- **Preview curl tests** for a real NAC (200 + canonical/OG), an invalid NAC (200 + noindex), `/catalog`, `/pricing`, `/privacy`, `/terms` (200), and a bad path (404) are specified.

## Must-fixes for v1.6 (attempt 4/4 — last try)
1. **Re-quote origin/dev `main.dart` catalog dispatch at lines 154–181, not 215–245.** The code block itself is the real dispatch (`// Public Catalog direct entry` → `CatalogBrowseScreen(initialNacCode: initialNacCode)` → `return;`). Lines **215–245** on `git show origin/dev:numista_mobile/lib/main.dart` are the `Firebase.initializeApp` timeout / `kApiBaseUrl` error UI, not routing. The whitelist at `:133–134` and the import at `:12` are fine. Pin `main.dart` `:119–140` correctly has no catalog paths (dev added them). This is the same fabricated-line-number class that sank earlier scores — fix the labels from `git show origin/dev`.
2. **Do not cite `catalog_browse_screen.dart:315` as the public `showPublic` call site.** Line 315 on origin/dev is `child: Column(` (Morgan owl header). Real sites: card `:466` `onTap: () => _showItemDetailModal(item)` and `_showItemDetailModal` at `:810` (initial NAC opens the same modal at `:80`). Quote those and write the replacement against them. Same error appears if this plan still presents `:315` as "already UnifiedCoinDetailScreen.showPublic".
3. **Correct the pin `firebase.json` line labels.** Pin rewrite `source` entries run through `/claim/**` at **line 130**, not "51–118" (line 118 is `/wishlist/**`). Headers begin around **line 137** (`**/*.@(js|css|wasm)`), not "119–234". Keep the surgical merge *content* (it is good); just label the ranges from `git show 4d17ca5e:numista_mobile/firebase.json`.
4. **Add a `main.dart` dispatch test, or say why `main()` is untestable and that preview curl covers it.** §9.2 still pumps `CatalogBrowseScreen` directly and does not exercise the `:154–181` whitelist/dispatch. Preview curls cover served HTML; they do not cover the Flutter entry split.
5. **Do not invent an OG image for the 1921 Morgan sample.** Record `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` has `primary_image`, `type_image`, `secondary_image`, `extra_images`, `image`, and `image_url` all null. `https://storage.googleapis.com/us_mint_coin_images/1921_morgan_dollar_obverse.png` is not in that record. OG description fields that *are* present: name `1921-P Morgan Silver Dollars`, year `1921`, denomination `Dollar`, series `Morgan Silver Dollars`, composition `90% Silver`. Mintage is `{value: null, label: 'not yet sourced', source_url: null}` — do not emit a mintage figure. For an OG image demo, pick one of the 1,214 rows that actually have `primary_image.url` (for example a Met/Wikimedia row) or omit `og:image` when the field is null.
6. **Align the Valuation Pending chip color.** §1 calls it a "gold chip"; §6.3 renderer is slate gray (`#F1F5F9` / `#64748B`). Pick one and use it everywhere.
7. **Add `test/services/catalog_census_privacy_test.dart` to the §7.5 file-manifest table** (it is already listed in §9.3).

## Notes (not blocking alone)
- `/catalog` rewrite is correctly absent at the pin and present on origin/dev (~`:134` / `:138`); say that clearly so implementers merge against pin, not against a dirty tree.
- `trailingSlash: false` plus directory `index.html` is proven by the preview curl tests if those run after a preview deploy; name that relationship in one sentence.
- Census marketing "3,200+" is acceptable against the verified 3,202 count.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.
