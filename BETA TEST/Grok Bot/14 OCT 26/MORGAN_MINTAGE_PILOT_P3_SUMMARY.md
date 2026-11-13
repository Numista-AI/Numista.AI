# MORGAN MINTAGE PILOT P3: SUMMARY (14 Oct 2026, ET)
Baton: `8 OCT 26\BATONS\BATON_P3_MORGAN-MINTAGE-PILOT_AGCOS_WAIT-OUT.md` (ref NET-070). Builds on `13 OCT 26\MORGAN_VERTEX_PILOT_*`.
**Files only.** No Firestore or collection writes, no deploy. No Vertex/GCP calls were made today (gcloud auth has expired; see Blockers). GCP spend today: $0.

## What the baton asked
The baton itself is short: Morgan owns the mintage pilot and builds on the 13 Oct pilot. Mint/Treasury beat PCGS/NGC, every figure is cited, legal tender only, UNKNOWN rather than a made-up number, files only. The 13 Oct summary had said the next step was the **mintage-number** packs, because the 48 AWQ rows held no mintage figures. So this pilot covers every mintage, product-limit and Mint-sales figure across Morgan's 25 sourced packs.

## Method
1. I pulled every quoted figure (a number of 1,000 or more in a mintage, limit, sold or production quote) from `EVIDENCE_PACK_2026-10-06_*_SOURCED.csv`, plus every Mint cumulative-sales figure cited in the pack notes.
2. **Re-check:** each quote was matched word-for-word against the saved page copies (`audit/*_tierA_pages`, `audit/src_pages`). Each sales figure was matched against the saved usmint.gov cumulative-sales data (saved 2 Oct 2026).
3. Live usmint.gov returns 403, so the Mint pages are **Wayback copies**. The sales data is a saved copy of the Mint endpoint and isn't re-fetchable live.
4. This is a deterministic re-check, not a Vertex Check Grounding run (no auth).

## Counts (results file: 291 figure rows, from 208 pack rows in 15 programs)
| Source tier | Figure rows |
|---|---|
| MINT, product page or press release quote (Tier A) | 72 |
| MINT, cumulative sales report (Tier A) | 135 (134 matched to saved sales data, 0 mismatches, plus the accepted 187,893 ruling) |
| PCGS/NGC only (Tier B) | 83 (ATB 66, ASE 9, Kennedy 4, AID 1, Proof Sets 1, Roosevelt 1, SemiQ Collectibles 1) |
| UNKNOWN | 1 (2025 Silver Proof Set 25RH product limit; no Mint limit found) |

Quote re-check: all 154 page quotes were found verbatim in the saved copies (one, the 25RG "Mintage Limit: 420,002", is split by page markup). There were 0 fabricated or missing quotes.

## Findings / contradictions
- **13 Oct Vertex results:** 0 contradictions. The 13 Oct pilot tested no mintage figures, so nothing overlaps; its 48 AWQ verdicts are unaffected.
- **Mint vs PCGS on the same row:** 0 numeric conflicts. AID row 2 (75,000) and SemiQ Collectibles row 2 (250,000) agree.
- **FLAG, ASE row 26 (26RF 2026 Congratulations Set):** Mint sales of 60,012 are above the Mint's quoted production limit of 60,000. This is a tension inside the Mint's own data (sales may include cancelled orders), not a pack error. Record the limit; don't call 60,012 a mintage.
- **CAUTION, Proof Sets row 34:** the 25,008 limit belongs to the 2025 Limited Edition Silver Proof Set (25RC) only. Sales for 2016-2022 were about 49-50k, so earlier years had different limits that still need sourcing.
- **Sales vs mintage:** Mint cumulative sales are units of product sold, not struck mintage. They're labeled that way in every row.
- **Accepted ruling kept:** 2021-W Burnished ASE Type 2 = 187,893, with no Type 1. 174,933 (21EGN alone) and 187,891 (Wikipedia) are kept for reference only.

## Remaining work
- 83 PCGS-only figures, mostly ATB circulating mintages, should get Mint figures from the Mint's circulating-coin production reports. That needs live usmint.gov or Wayback copies of those reports.
- Optional: a Vertex Check Grounding pass on these 291 rows in `numista-morgan-pilot`, after Eric re-authenticates and reviews the 13 Oct Billing > Reports figure (the worst case there was about $5.85, already near the $5 budget).
