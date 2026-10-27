# NET-616 — 1351hrs PM beta amend for Plan.v2 (Eric B− Mint)

- **Filed by:** Grok Bot Chief of Staff
- **When:** 2026-10-27 ~2:20 PM ET
- **Source folder:** `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\1351hrs test`
- **Artifacts on box:** `/workspace/eric-bminus-27oct/1351hrs-test/` (`27_OCT_2026_v2.docx`, receipt PDF, SS 1–7)
- **Morning review re-read:** `27 OCT 2026.docx` / `27_OCT_2026_morning_review.docx` — item “How they appeared in my collection #1”: **None of the 3 had images or valuations** (SS 5). Eric: still broken at 1351hrs — **NOT GOOD**. P0.

## Status vs Plan.v1 / Argon
- Argon HOLD Plan.v1 **58/100** (Flutter paths; I-07/I-09/I-10 enrichment+images+vals already mapped).
- NET-615 Plan.v2 wake already out (no code until cycle complete).
- This NET **amends Plan.v2 must-folds** with afternoon evidence. Prep/plan only — **no EXECUTE**.

## Afternoon findings (must fold into Plan.v2)

| ID | Finding | Severity | Maps to |
|---|---|---|---|
| **PM-01** | Morning 3 invoices (26GC, Trump $1 roll, 2023 Proof / Innovation) **still no images, no valuations** in My Collection after hours | **P0** | Argon **I-09** (+ I-07 commit enrichment). Fix: `/api/review/commit` must enrich + baseline val + reference images; stop eternal “Valuation Pending”. |
| **PM-02** | Key Test **FAIL**: second upload of `Receipt_2026 Uncirculated Coin Set` (Mint **26RJ**, Invoice **USM23493262**, $134.45) → **0 Duplicates Flagged** though Eric already owns that set (intent: sell second) | **P0** | Argon **I-08** — also match by Retailer Item No. **and/or Invoice/Order #** vs vault + paper trail. Eric wants Invoice # as easy duplicate clue when Item # matches but Order dates differ. |
| **PM-03** | Invoice # **correctly recorded** (USM23493262) in Review Hub + Paper Trail | PASS (keep) | Schema/UI: keep Invoice #; use it in duplicate logic |
| **PM-04** | Cards + detail: **cannot tell** two `2026 Uncirculated Coin Set` rows apart | P1 | Show Invoice # / Order date / Cost on card face + detail header; qty or “copy 2” when Item # matches |
| **PM-05** | Theme/Subject inconsistent: older 26RJ had `250th Anniversary Uncirculated Coin Set`; new upload **blank** Theme; AI Value **$0.00** vs older **$36.40** | P0/P1 | I-03 + I-07 enrich_us_mint_item on commit; catalog entry for **26RJ** must stamp theme every time |
| **PM-06** | White text on off-white still unreadable on both sets (SS 6, SS 7); modal not resizable / Lincoln quarter cut off | P1 | I-13 / contrast audit; modal sizing |
| **PM-07** | Fee $9.95 captured on this 26RJ Review Hub row (contrast morning Trump roll Fee $0) | note | I-04b zero-fee on pack_expanded still required; 26RJ may not have hit that path |

## Plan.v2 extra requirements (on top of CoS NET-615)
1. Treat **images + valuations after invoice commit** as **systemic** across every Mint product (not one SKU).
2. Duplicate detection: Item # **OR** Invoice/Order # **OR** normalized identity; flag when adding a second identical Mint set with a **different** invoice (Eric’s sell-intent case).
3. Card/list must surface enough identity (Invoice #, purchase date, cost) to distinguish two identical SKUs.
4. Keep invoice upload working; Mint figures first; each fix → FT retest step (extend FT checklist with 1351hrs: re-upload 26RJ → expect duplicate amber + images/vals on morning three after fix).
5. **No code / no preview ship** until Argon→GB→SAG on Plan.v2.

## Desk actions
1. File NET-616 LIVE; copy this + `1351hrs-test/` note into `27 OCT 26\BATONS\INBOX\`.
2. Amend AG CoS v2 Plan.v2 wake: must include PM-01…PM-07; cite Argon I-07/I-08/I-09 paths.
3. Leave Argon NET-606 day baton as superseded by Plan.v2 round; do not EXECUTE v1.
