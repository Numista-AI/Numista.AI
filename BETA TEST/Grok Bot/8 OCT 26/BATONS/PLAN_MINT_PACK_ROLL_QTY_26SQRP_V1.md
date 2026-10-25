# FOR_AG -- PLAN.v1: Mint pack/roll Quantity expand (26SQRP) -- 2026-10-25
**From:** Grok CoS (Desk)
**Filed:** Sun 25 Oct 2026 ~7:40 AM ET
**Mode:** DEV BUILD plan only -- **no** merge / live deploy / spend without Eric typed YES.
**Hard stop:** Mon 26 Oct ~6:32 PM ET (48h Mint invoice readiness).
**Do not wake AG via radio from this file** -- CoS files NET wake separately.

## Problem (Eric live, 24 Oct ~7:40-7:53 PM ET)
- PDF: `Receipt Semiquincentennial President D Coin Roll.pdf` (US Mint SKU **26SQRP**, 25-coin roll).
- Live tip **V8.18.15i / 6ee3de89** correctly does **Nx invoice lines -> one Hub row Qty N**.
- That fix does **not** expand Mint SKU pack/roll counts. Hub showed Item **26SQRP**, **QTY 1**, cost **$70.95**, title like "2026 Dollar (D)"; Done said **1 coin**; header stuck on **Processing Files**; nav truncated to **Review ...**.
- **Correction (Eric 24-25 Oct):** two Hub rows = Eric uploaded the PDF **twice** (not a single-upload split). After ingest intent: he sold **2** of the 25 at **$5** each and gifted **2** (**21** left) -- product context for later Qty adjust / sell-gift outflows; **not** in this build.

## Catalog vs enrich gap (code)
| Piece | Path | What it does / misses |
|-------|------|------------------------|
| Catalog | `numista_backend/services/us_mint_catalog_service.py` (~L164-181) | `26SQRP` entry exists; title/formal_name say **25-Coin Roll**; **no** `pack_quantity` / `coins_per_unit` field. |
| Enrich | same file, `enrich_us_mint_item` (~L274-356) | On catalog hit sets Year, series, denom, strike, condition, metal, theme, variety, weight, notes -- **never sets `Quantity`**. |
| Post-extract | `numista_backend/main.py` (~L2050-2072) | Qty heuristic only pulls `qty:N` from notes/desc if Quantity<=1, then calls `enrich_us_mint_item`. No pack expand. |
| LLM prompt | `main.py` (~L2162-2164) | Names 26SQRP with metadata but **no Quantity:25**; Quantity rule = Ship-column count (1 roll shipped -> 1). |
| Tests | `tests/test_us_mint_catalog.py` `test_26sqrp_catalog_facts` | Asserts year/denom/facility/price; **no** Quantity=25 assert. `test_us_mint_invoice_enrichment.py` has no 26SQRP Qty case. |

**One-liner:** Catalog *knows* 26SQRP is a 25-coin roll in prose; enrich + invoice path never multiply Ship qty x pack size -> Hub QTY stays 1.

## Acceptance criteria (Monday bar)
1. **Single upload** of Eric's PDF -> **one** Review Hub row for 26SQRP with **Quantity = 25** (prefer one Hub row Qty 25; clear pack-expand OK if same result).
2. Add Coins: when file is done, UI says **Done** (not stuck **Processing Files**); Done count matches Qty (25, not 1); user can **exit** Add Coins without a new tab.
3. Nav / Review Hub label readable (**Review Hub**, not truncated **Review ...**).
4. FT with Eric's PDF on the build branch (preview OK); live only after **Eric YES**.
5. Pytest: catalog field + `enrich_us_mint_item` for 26SQRP sets Quantity 25 when invoice Ship qty is 1; regression that V8.18.15i Nx-line Qty still works.

## Out of scope (this PLAN.v1)
- Double-upload duplicates (user error; do not treat as product bug).
- Full sell / gift / Certificate of Transfer system -- only note **future** Qty adjust / outflow after correct Qty 25 ingest (Eric: -2 sold @$5, -2 gifted -> 21 left).
- Expanding every Mint bag/set SKU beyond same-class pack/roll fields needed for 26SQRP (add `pack_quantity` pattern so 26SQBP etc. can follow without a new architecture).
- Cost $70.95 vs unit $61.00 (S&H/total bleed) -- note only; fix only if same touch is trivial.

## Non-goals
- No main merge, no Cloud Run traffic shift, no spend without Eric YES.
- No AG radio wake from this file.
- No overnight quota burn; one focused track.

## Test PDF
`C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\24 OCT 2026\Receipt Semiquincentennial President D Coin Roll.pdf`

## Suggested build shape (AG execute when baton OVER)
1. Add explicit `pack_quantity: 25` (name bikeshed OK) on catalog `26SQRP` (and same-class rolls/bags as data allows).
2. In `enrich_us_mint_item`: if catalog has `pack_quantity` and line Quantity is missing or <=1 (Ship=1 roll), set `Quantity = pack_quantity` (or `ship_qty * pack_quantity` if Ship>1). Do **not** double-apply if invoice already has Qty=25.
3. Tighten Mint prompt line for 26SQRP: Quantity = coins in roll (25) x rolls shipped; Cost = unit price **$61.00** not order total.
4. Flutter/Add Coins: honest Processing->Done; Done coin count from Quantity; exit path; Review Hub nav label.
5. Tests + EXECUTE_DONE + (if >2 files) GEMINI38_REVIEW; CoS score; **hold live** for Eric YES.

## Done when
Plan accepted by CoS/Eric; AG build meets acceptance on preview; live deploy only on Eric YES before Mon ~6:32 PM ET hard stop.
