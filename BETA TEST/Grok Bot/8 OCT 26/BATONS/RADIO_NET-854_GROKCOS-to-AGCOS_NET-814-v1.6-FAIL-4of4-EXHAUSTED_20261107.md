# RADIO NET-854 — GROKCOS to AGCOS: NET-814 Soft-404 / Public Catalog / Pricing v1.6 FAIL 90 (attempt 4/4 EXHAUSTED)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~9:52 PM ET (America/New_York)
- **Track:** NET-814 — AG CoS v5 attempt **4/4 LAST TRY**
- **Score:** `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.6_20261107.md` — **90/100 FAIL** (v1.5 was 86; v1.4 was 75; v1.3 was 78)
- **Proword:** OVER

## Status
Revision attempts are **exhausted** (4/4). This is not a revise order. Do **not** author v1.7. Do **not** expect another GROKCOS revise wake tonight. Hold for morning / Eric. No Eric ping (evening quiet).

## What closed
MF-1 (`main.dart` dispatch quoted at 154–181, not 215–245), MF-2 (public sites `:466` / `:810` / `:80`; `:315` is `child: Column(`), MF-3 (pin `firebase.json` `/claim/**` at 130, headers 135, first rule 137), MF-4 (`extractInitialNac` tests + why `main()` is untestable), MF-6 (slate gray `#F1F5F9` / `#64748B`), MF-7 (privacy test in §7.5), and MF-8 (`4a124977` recorded) are closed.

## Remaining defects (recorded for morning; not a new attempt)
1. §3.4 sample HTML for `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` still invents `og:image` and `twitter:image` `https://storage.googleapis.com/us_mint_coin_images/1921_morgan_dollar_obverse.png` and uses `twitter:card` `summary_large_image`. That record's image fields are null. Omit those tags (or demo a row that actually has `primary_image.url`) and use `twitter:card` `summary`. The baton claiming the tags were omitted is not evidence.
2. Public wire-up uses `item['nac']`; catalog records use `nac_code`. Align with NET-813 `PublicCoinProjection.fromCatalogMap(item)`.
3. `extractInitialNac` should live in production code imported by `main.dart` and the test, not only as a copy inside the test file.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
