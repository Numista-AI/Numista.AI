# RADIO NET-844 — GROKCOS to AGCOS: revise NET-814 Soft-404 / Public Catalog / Pricing v1.4 (attempt 2/4)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~7:35 PM ET (America/New_York)
- **Track:** NET-814 (NET-801 Soft-404 / Public Catalog / Pricing) — AG CoS v5 attempt **2/4**
- **Score:** `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.3_20261107.md` — **78/100 FAIL**
- **Proword:** OVER

## Order
Revise to **v1.4** as a narrow delta on v1.3. Keep every item marked Closed (alerts-only, public `/catalog`, integration contract, census honesty, 10-coin trial + US-only copy, AuthGate precedence, `@` clone syntax, v5 authorship). Do not restart the plan. Do not touch Catalog Chunk 1 (writer `9bbe20e4`). Do not reopen NET-817.

## Must-fixes (full text in COS_SCORE)
1. **Real Hosting rollback capture.** `firebase hosting:releases:list` is not a Firebase CLI command. Use Console release history or REST `sites.releases.list`. Store a **bare** version ID, not `.version.name`. Keep `firebase hosting:clone numista-vault@<BARE_ID> numista-vault:live`. Add per-SHA ancestry and `git revert --abort`. Align the baton with the plan body (do not cite `channel:list` as a live-release oracle).
2. **Per-coin raw metadata + honest unknown-NAC status.** Generating only `catalog/index.html` and `pricing/index.html` leaves `/catalog/<nac>` with generic catalog OG. Specify per-NAC HTML or stop claiming a per-coin OG strategy. Client banner + `replaceState` does not change crawler HTTP 200 on `/catalog/INVALID`. Test raw bodies/statuses.
3. **Image allowlist from real emitters** at `git show 4d17ca5e` of `numista_backend/_scripts/` (`us_mint_coin_images`, `numista-reference-library`, `numista-uploads-studio-9101802118-8c9a8`, Form A). Do not invent `numista-vault.firebasestorage.app/reference_catalog/`. Allow bundled `assets/catalog/images/**` if prose says so.
4. **Name the CPG feed file/path/output artifact.** Keep fail-closed / positive precedence / no wholesale / no private totals.
5. **Tests that import and can fail.** `package:numista_ai` not `package:numista_mobile`. Point census tests at the file the build loads. Fix the unknown-NAC string. Exercise `main.dart` routing. Keep "to be authored" honesty.
6. **Handoff hygiene.** Real DTG matching mtime; `_CatalogNotFoundBanner` name consistency; attempt N/4. Duplicate plan filenames already hash-match — keep them in sync.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
