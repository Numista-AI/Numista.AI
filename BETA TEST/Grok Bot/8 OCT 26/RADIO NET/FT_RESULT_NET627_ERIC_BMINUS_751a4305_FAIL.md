# FT_RESULT — NET-627 / Eric B− Mint FT_RETEST_CHECKLIST — OVERALL FAIL
**Filed:** 2026-10-27 ~5:18 PM ET by Field Tester  
**Preview:** https://numista-vault--p7-gate-8avtpz22.web.app (Hosting fea58d8f2ab345ef)  
**Backend:** numista-backend-00497-xej tag p7gate (0% prod)  
**Code SHA:** 751a4305 on origin/dev (docs bb6e0017)  
**Account:** grokbot@numista.ai only · Live/main OFF · Never opened live

## BLUF
**OVERALL FAIL** — two P0 FAIL-the-build gates missed:
1. **I-07 / PM-01** — after Commit, 26RJ still **Valuation Pending** / Est. Value $0.00 and **Image unavailable** (~3 min wait).
2. **I-04b** — 26SQRP pack/roll Hub **Fee $0.00** with invoice S&H $9.95 (expected Fee $9.95).

Do **not** prompt Eric founder retest until FAIL-FIX + PREVIEW_READY + FT PASS.

## Checkoffs

| Item | Result | Notes |
|---|---|---|
| Smoke: preview + grokbot | PASS | Splash hang → one reload; signed in |
| Smoke: Add Coins | PASS | |
| Smoke: PDF upload path | PASS | Bulk Import |
| Smoke: Invoice # on Hub | PASS | USM23493262 (26RJ); USM24086141 (26SQRP) |
| I-04b Fee S&H (26RJ Hub) | PASS | Fee $9.95 on 26RJ Unc Set |
| I-04b Fee S&H (26SQRP) | **FAIL** | Fee $0.00 on qty25 roll; expected $9.95 |
| I-04c Edit Cancel | PASS | Variety edit + X; Hub unchanged |
| I-05 Select All | PASS | Distinct Add Selected vs Delete Selected |
| I-06 Commit readable | PASS | Committed 26RJ only; toast Added 1 coin |
| I-07 / PM-01 images+vals | **FAIL** | Pending + placeholder after ~3 min; detail $0 / Image unavailable |
| I-08 / PM-02 duplicate | PASS | Amber Possible Duplicate (SKU 26RJ); left uncommitted |
| SAG1 dup sweep | PASS | Amber banner + reason text (SKU already in collection) |
| SAG2 26RJ enrich | PARTIAL | Theme stamped; Condition Uncirculated; **images not filled** |
| SAG3 light cream contrast | PASS (limited) | Dark text on cream; no theme toggle found; OwnerPhotoHero/AI Insights not deep-checked |
| SAG4 20-coin strip | PARTIAL | 20 tiles wrapped grid no clip; all placeholders (grid not horizontal strip) |
| P1 Google Images | PASS | Absent on Coin Inspector |
| P1 two-SKU distinguish | SKIP | |
| P1 AI Report CTA | SKIP | |
| Innovation / Proof PDFs | SKIP | |

## Caveats
- Pre-existing grokbot 26RJ ($198, no photo, Valuation Pending) already in collection — new upload amber from start. Not wiped.
- ALT PDF overlay invoice USM99988776 **not** captured by OCR (Hub still USM23493262); duplicate still caught by SKU vs collection.
- Hub badge 132–134 vs ~4–6 listed rows (stale badge note).
- Collection 352→353 after one 26RJ commit.
- Pending left: ALT 26RJ dup, 26SQRP qty25, plus 3 stale ASE/Dime rows untouched.

## Shots
`/workspace/p7gate/net627/shots/` 01–13_*.webp (also copied to RADIO NET).

## OUT
FAIL report → CoS + Desk. Live/main locked. No founder retest prompt.

OVER.
