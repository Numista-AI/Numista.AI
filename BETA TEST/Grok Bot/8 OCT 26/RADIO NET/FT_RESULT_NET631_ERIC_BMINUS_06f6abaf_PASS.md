# FT_RESULT — NET-631 / Eric B− Mint FT_RETEST_CHECKLIST — OVERALL PASS
**Filed:** 2026-10-27 ~7:00 PM ET by Field Tester  
**Preview:** https://numista-vault--p7-gate-8avtpz22.web.app (Hosting ee3a6f79658feee4)  
**Backend:** numista-backend-00498-kek tag p7gate (0% prod)  
**Code SHA:** 06f6abaf on origin/dev  
**Account:** grokbot@numista.ai only · Live/main OFF · Never opened live

## BLUF
**OVERALL PASS** — both prior P0 FAIL-the-build gates now green:
1. **I-04b** — 26SQRP Hub **Fee $9.95** (Invoice USM24086141); 26RJ Fee preserved at $9.95.
2. **I-07 / PM-01** — after Commit, 26RJ shows **real Mint set image** and Est. Value **$124.50** (not Valuation Pending / $0). 20-coin tiles filled within ~20–30s.

Dup amber / SAG1, SAG3 cream contrast, and SAG4 20-coin wrap stayed PASS. CoS may prompt Eric founder retest on the same path. Live/main still LOCKED until explicit CoS live YES.

## Checkoffs

| Item | Result | Notes |
|---|---|---|
| 1 Smoke: preview + grokbot | PASS | Splash ~8s; Good evening Grok; grokbot@numista.ai |
| 1 Smoke: Add Coins / PDF path | PASS | Bulk Import Browse Files / Start Import |
| 2 I-04b Fee (26SQRP) | **PASS** | Fee $9.95; Cost $61.00 (25@$2.44); Invoice USM24086141; left uncommitted |
| 2 I-04b Fee preserve (26RJ) | PASS | Fee $9.95 on primary + ALT Hub rows |
| 3 I-07 / PM-01 images+vals | **PASS** | Card image + Est. $124.50 Uncirculated; detail Acquisition $134.45 / Est $124.50; Invoice USM23493262; Item 26RJ |
| 3 Caveat | note | Detail header thumbnail still generic folder ("Add where this is stored"); card + 20 tiles have real images |
| 4 Dup amber / SAG1 | PASS | Amber Possible Duplicate SKU 26RJ / Invoice USM23493262; ALT USM99988776 pending; not committed |
| 5 SAG3 light cream contrast | PASS | Dark text on cream Hub/collection/inspector |
| 5 SAG4 20-coin wrap | PASS | 20 tiles 2×10 none clipped; images filled ~20–30s |
| 6 Firestore vault doc id | SKIP | UI shows no doc id; identify by Item 26RJ / Invoice USM23493262 / cost $134.45 / mint P & D |

## Caveats
- Pre-existing grokbot 26RJ (cost $198, Valuation Pending, no image) still in collection — new commit identified as only 26RJ with invoice + P & D mint.
- Collection showed 353 after commit; before-count not captured (delta likely +1 unverified).
- Pending left: 26SQRP (25), ALT 26RJ dup, 3 stale 2026-W ASE dup.csv rows — untouched.
- Bulk import page is plain HTML (`add_coins.html`); PDFs fed to file input directly.
- OCR worked on both PDFs this run.

## Shots
`/workspace/p7gate/net631/shots/` 01–11_*.webp (also RADIO NET + tar.gz).

## OUT
PASS report → CoS + Desk. Live/main locked. CoS prompts Eric founder retest after this PASS.

OVER.
