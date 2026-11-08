# BATON NET-814 — GROKCOS REVIEW — SOFT404-PUBLIC-CATALOG-PRICING v1.7

- **Writer:** GB CoS fresh writer (writer-cap rule; AG CoS v5 `cfe23a7a` exhausted 4/4). Eric GO Sun 8 Nov 07:27 ET.
- **Plan:** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.7.md` — 58097 bytes, SHA-256 `dd462ae5ba72b29f398bdc8be677335098416b209aaf076f79ae9bcdabcc7d84`
- **Filed:** Sun 8 Nov 2026 07:34 ET
- **Mode:** PLAN ONLY. No code edits, no Firestore, no deploy, no push to main (locked `9f04550a`). Stripe OFF. Alerts only, never caps. No PII.
- **Writer self-score (not independent; needs GB CoS scorer pass, then SAG, then Eric typed YES):** 96/100

## Changes (only the CoS remaining defects)
E1 og:image*/twitter:image removed for 1921-P (all image fields null, verified), twitter:card summary; E2 showPublic uses PublicCoinProjection.fromCatalogMap(item) reading nac_code (3,202/3,202 rows have nac_code, 0 have nac); E3 extractInitialNac in production lib/routing/public_catalog_route.dart, imported by main.dart and test. Mirror PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.7.md byte-identical.
