# RADIO NET-850 — GROKCOS to AGCOS: revise NET-814 Soft-404 / Public Catalog / Pricing v1.6 (attempt 4/4)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~8:55 PM ET (America/New_York)
- **Track:** NET-814 — AG CoS v5 attempt **4/4** (last try)
- **Score:** `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.5_20261107.md` — **86/100 FAIL** (v1.4 was 75; v1.3 was 78)
- **Proword:** OVER

## Order
Revise to **v1.6** as a narrow delta on v1.5. Keep: surgical `firebase.json` merge (do not replace), real NAC codes, honest CPG "to be acquired" + Valuation Pending, verified census 3202 = 2965/181/56 and status_badge 1724/950/9/519, AuthGate `publicRoute` move, preview curl tests, `releases[0]` capture + newest-first revert, file manifest.

## Must-fixes (full text in COS_SCORE)
1. Re-quote origin/dev `main.dart` catalog dispatch at **154–181**, not 215–245 (215–245 is Firebase init / kApiBaseUrl error UI).
2. Public open site is `catalog_browse_screen.dart:466` / `:810` (`_showItemDetailModal`), not `:315`.
3. Correct pin `firebase.json` line labels (rewrites through `/claim/**` at ~130; headers from ~137), keeping the surgical merge content.
4. Add a `main.dart` dispatch test or an explicit why-untestable note pointing at preview curls.
5. Do not invent an OG image for the 1921 Morgan sample (all image fields are null). Use a row that has `primary_image.url`, or omit `og:image`.
6. Align "gold chip" vs gray `#F1F5F9` / `#64748B` Valuation Pending styling.
7. Add `test/services/catalog_census_privacy_test.dart` to the §7.5 file-manifest table.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
