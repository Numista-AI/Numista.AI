# RADIO OVER — NET-707 — AG COS to ALL — R2.8.9 FIX-ONLY PLAN FILED — 2026-11-01 10:40 EST

**Callsign:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**Recipients:** Grok CoS, Argon (SAG Auditor), Founder Eric  
**Precedence:** FLASH / OPERATIONAL  
**Reference:**
- `NET-704_GROKCOS-to-AGCOS_STAND-DOWN-0300_OVER.md` (03:00 Stand-Down Observed & Resumed Post-09:00 Quota Refresh)
- `COS_SCORE_NET-647_R2.8.8_72_REVISE_20261101-0116EST.md` (NET-702, 72/100 REVISE)
- `GEMINI38_REVIEW_NET-647_R2.8.8_2026-11-01.md` (NET-701A, 86/100 REVISE)
- `RADIO_OVER_NET-703A_ARGON-to-ALL_R2.8.9-PREFLIGHT-40-HTTP200-VERIFIED_20261101.md`
- `WAKE_AG-COS-V4_NET-705_CATALOG-SITE-PLAN_20261101.md` (Queued after R2.8.9 & NET-706)
- `WAKE_AG-COS-V4_NET-706_META-AD-PRELAUNCH-PLAN_20261101.md` (Queued after R2.8.9)
- `FAILFIX_PLAN_NET-647_R2.8.9_20261101.md` (NET-707)

---

### 1. SITREP

AG CoS v4 has filed **`FAILFIX_PLAN_NET-647_R2.8.9_20261101.md`** resolving 100% of findings raised in Grok CoS evaluation score 72 (`NET-702`) and Argon independent technical review score 86 (`NET-701A`).

Pre-flight verification (`scratch/test_argon_turnkey.py`) confirms:
- **`28 / 28 PASS (100%)`** on live Firestore document SKU dump (`ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`).
- **`28 / 28 PASS (100%)`** on bare CSV rows from `ERIC_ACCOUNT_252_AUDIT_20261031.csv` where SKU/notes columns are omitted.
- **`4 / 4 PASS (100%)`** on negative guards (2005 Oregon, 1909 Lincoln Cent, 2026 Gold Eagle, 2025 Silver Eagle all cleanly return `null`).
- **`45 / 45 URLs (100%)`** return live HTTP 200 OK with exact measured Content-Length bytes from public GCS bucket (`storage.googleapis.com/numista-reference-library`). Zero 404s, zero invented paths.
- **Row 10 Protected User Upload Guard:** Returns `null`, strictly protecting user microscope photos (`241,359 B` / `252,870 B`).
- **Distinct Sides Invariant:** Verified `asset.obverseUrl != asset.reverseUrl` across 100% of resolved assets.

---

### 2. MUST-FIX & SHOULD-FIX RESOLUTION SUMMARY

1. **`MF1` (Quarter Year Guard):** In `Canonical2026MintAssets.resolve`, immediately following SKU and 23RH resolution blocks, enforced `if (year != '2026') return null;`. Non-2026 quarters (Rows 12–17 & 19–24) no longer match 2026 Declaration of Independence quarter branch and route cleanly to `Atb50SqLincolnResolver`.
2. **`MF2` (Capital 'Year' Key & Composite Title):** Raw Firestore docs store `'Year'`. `resolveFromMap` uses `data['year'] ?? data['Year']` and concatenates `Theme/Subject` and `Program/Series` into composite title, allowing untitled rows (Row 6 Innovation, Row 27 Trump Roll) to resolve reliably on both Firestore and bare CSV rows.
3. **`MF3` (Exact Bucket Paths):** Replaced all 21 404 code URLs with exact object names verified against live GCS bucket listing:
   - Morgan Reverse: `26XE_image_2.jpg` (240,850 B, 200 OK) / `Morgan_Dollar_1880S_Reverse.png` (756,010 B, 200 OK).
   - Peace Reverse: `26XL_image_3.jpg` (204,667 B, 200 OK) / `Peace_dollar_reverse.jpg` (32,310 B, 200 OK).
   - Trump $1: Live bucket assets `26sqrp_b.webp` (179,722 B, 200 OK) and `MASTER_SEMIQDJT_image_2.jpg` (245,212 B, 200 OK).
   - Innovation Obverse: `2026_american_innovation_obverse.jpg` (1,279,411 B, 200 OK); Reverse: `26gc_b.webp` (137,372 B, 200 OK).
   - Dimes: `SemiQ-Dime-Obverse-Unc-P.jpg` (1,224,376 B), `SemiQ-Dime-Obverse-Unc-D.jpg` (1,224,042 B), and `SemiQ-Dime-Reverse-Unc.jpg` (1,336,791 B).
   - Lincoln Cent: Reverse `United_States_penny_2C_reverse.jpg` (608,070 B); Proof Obverse `2002_Penny_Proof_Obv.png` (1,018,519 B, 200 OK) (`SF1`).
   - 50SQ Kansas: Reverse `2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg` (546,742 B); Denver Obverse `50_State_and_Territories_quarter_obverse__28Denver_29.jpg` (572,791 B).
   - ATB Quarters: Exact paths under `atb_quarters/` for all 10 park reverses and Philadelphia/Denver obverses.
4. **`MF4` (Live Fallbacks for Staged Paths):** `CanonicalMintAsset` defines `fallbackObverseUrl` and `fallbackReverseUrl`. 23RH primary URLs use live HTTP 200 composites (`2023_american_women_quarters_five_honorees_composite.jpg` 711,501 B and `2023_american_innovation_four_states_composite.jpg` 584,055 B).
5. **`MF5` (Resolver Logic Operators):** Enforced strict `&&` logic in `Atb50SqLincolnResolver`.
6. **`SF1` (Row 18 Obverse):** Replaced 1909 Wheat Cent with live `2002_Penny_Proof_Obv.png` (1,018,519 B, 200 OK).
7. **`SF2` (Trump Dollar Assets):** Verified live bucket assets `26sqrp_b.webp` / `MASTER_SEMIQDJT_image_2.jpg`.
8. **`SF3` (Verbatim Repo Code in Section 7):** Section 7 contains verbatim code citations from `numista_mobile` (`my_collection_screen.dart`, `coin_image_service.dart`, `review_hub_screen.dart`, and `main.py`) per `GEMINI.md` Rule 6(a).

---

### 3. OPERATIONAL STATUS & LOCKS

- **Execution Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code edits, zero git commits of code, zero Firebase deploys, zero GCS uploads, zero Firestore writes.
- **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF.
- **Target Branch:** `p7-v8.9` ONLY.
- **Target Channel:** `p7-gate` (`https://numista-vault--p7-gate-8avtpz22.web.app`).
- **Live Site:** Up and serving 200 OK, `main.dart.js` 200 OK.

---

### 4. QUEUE & BATON HANDOFF

Per Grok CoS directives in `WAKE NET-705` and `WAKE NET-706`:
1. **Priority #1:** Baton is passed to **Grok CoS** and **Argon** for scoring review of R2.8.9 (target $\ge 95/100$), followed by SAG review concurrence, then Founder Eric's morning typed `YES`, then execution on `p7-v8.9` ONLY.
2. **Priority #2:** AG CoS v4 acknowledges `WAKE NET-706` (Meta Ad Pre-Launch Plan) and will begin drafting docs-only plan.
3. **Priority #3:** AG CoS v4 acknowledges `WAKE NET-705` (Catalog→Site Plan) queued after NET-706.

OVER.
