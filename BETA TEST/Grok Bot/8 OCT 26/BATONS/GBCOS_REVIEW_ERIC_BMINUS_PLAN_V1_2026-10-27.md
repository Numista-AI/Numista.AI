# GB CoS REVIEW - Eric B- Live Mint Plan.v1 (NET-602 / NET-606)
- Reviewer: Grok Bot Chief of Staff (GB) | DTG: 2026-10-27 14:20 ET
- Input: ARGON_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md (58/100 HOLD)

## Verdict: CONCUR HOLD - Plan.v1 NOT executable. AG CoS v2 writes Plan.v2 (round 2 of max 4).

## GB spot-check of Argon citations (real code, dev branch)
- us_mint_catalog_service.py:175 - "theme_subject": "Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)"  -> CONFIRMED (I-04a)
- us_mint_catalog_service.py:328 - if not item.get("Mint Mark") and "mint_mark" in catalog_match:  -> CONFIRMED (catalog does not override LLM mint mark)
- us_mint_catalog_service.py:380 - item["Allocated Fees"] = 0.0  -> CONFIRMED (I-04b)
- add_coins_hub.dart:818 label: 'Upload a list' / :1288 'Open Invoice Importer' -> CONFIRMED (I-01/I-02 extra click)
- main.py:7653 fee overwrite: not independently re-found by GB grep; Plan.v2 must quote it verbatim.

## GB requirements for Plan.v2 (in addition to Argon section 3)
1. Every fix cites real Flutter (numista_mobile/lib/screens/...) or FastAPI (numista_backend/...) file:line with verbatim code (Rule 6a). Zero React/TSX paths.
2. Treat as systemic (Eric rule): catalog override fix must cover ALL matched SKUs, not just 26SQRP; Proof inference must cover every proof set/roll SKU.
3. Mint figures win over grader/dealer data for any condition/mintage text touched.
4. Invoice upload stays working end to end (must-keep). I-01 adds a 1-click Upload an Invoice card.
5. Per-issue FT retest line mapped to FT_RETEST_CHECKLIST_NET602.md.
6. Preview-only; live/main needs Eric typed YES. Cherry-pick approved commits only.

Next: AG CoS v2 -> Plan.v2 -> Argon -> GB -> Stand Alone Grok -> EXECUTE.
