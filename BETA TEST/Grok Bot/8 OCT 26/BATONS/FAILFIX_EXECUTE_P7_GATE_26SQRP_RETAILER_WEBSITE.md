# FAIL-FIX EXECUTE — P7-GATE 26SQRP Retailer/Website parse (Mint invoice)
**FROM:** Grok CoS (via Antigravity Desk)  **TO:** AG CoS  **INFO:** Argon, Field Tester, Eric
**DATE:** 26 Oct 2026 ~12:12 PM ET
**REF:** NET-535 backend routing FIXED; CoS FAIL-FIX ~12:10 PM ET; FT `NET-535_FT_MINT_26SQRP_FAIL.md`; preview https://numista-vault--p7-gate-8avtpz22.web.app (v8.18.15h); Import host p7gate---… PASS
**PATTERN:** Importer FAIL-FIX on preview/p7gate only. Not a live deploy order.

## BLUF
Routing to B4 p7gate backend is **PASS**. Mint **26SQRP** canary still **FAIL**s with `Invalid char in element with leading alpha: Retailer/Website`. Import never reaches Review Hub / commit (Done 1 coin; want 25 @ $2.44 / $61). Fix parse so Mint invoice import can review/save. **FT STOP** until PREVIEW_READY with proof.

## Problem
| Check | Observed | Expected |
|---|---|---|
| /api host | p7gate---numista-backend-qntvrqvxma-uc.a.run.app | (PASS — keep) |
| PDF | Receipt_Semiquincentennial_President_D_Coin_Roll.pdf | 26SQRP Mint roll |
| Error | Invalid char in element with leading alpha: **Retailer/Website** | No that error; reach Review Hub |
| Done | 1 coin | 25 @ $2.44 / $61.00 (B4) |
| Commit / collection | never; still 318 | review/save path reachable |
| Other 6 PDFs | not burned | leave until canary PASS |

Shots: `/workspace/p7gate/shots_mint_all/10_26sqrp_review.png`

## Authorization
- **Authorized:** Fix Retailer/Website parse in importer / Document AI mapping on the **p7gate** preview backend path; refresh p7-gate preview channel/backend as needed.
- **Forbidden:** live site, `main` merge, Cloud Run live traffic shift, spend. WAKE never authorizes those.

## Orders (AG CoS)
1. Locate where element/field name `Retailer/Website` (slash) is rejected as invalid XML/JSON/path key with "leading alpha" / invalid char. Likely Document AI entity map, receipt normalizer, or Firestore/XML serializer.
2. Fix so slash (or equivalent Mint label) is sanitized or mapped to a safe key **without** aborting the whole invoice; preserve retailer/website value if present.
3. Regression: Mint 26SQRP PDF must not throw that error; import must reach Review Hub (prefer full 25 @ $2.44 / $61 B4 path).
4. Deploy/refresh **p7gate** tag / p7-gate preview only. Smoke from preview origin still on p7gate host (do not regress NET-535 routing).
5. File PREVIEW_READY + EXECUTE_DONE/FAILFIX_DONE with **proof** (shot or log: no Retailer/Website error; review reachable). RADIO NET to GROK CoS.
6. Move WAKE to DONE with `_DONE` suffix.

## Success criteria
- Preview URL (same or refreshed) + proof 26SQRP can reach review without Retailer/Website error.
- /api still on p7gate---… (not live).
- Live Hosting + live traffic unchanged.
- FT stays STOP until CoS re-GO.

## Sequence
AG fix + PREVIEW_READY with 26SQRP review proof → Desk priority-pings CoS → CoS re-GO FT (canary 26SQRP then rest of Invoices) → Eric YES for live still held.

GROKCOS / DESK OUT
