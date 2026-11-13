# CoS review — Eric live Mint try 24 Oct 2026 (shut-down note)

**When:** ~7:40–7:53 PM ET. **Where:** live numista.ai (not preview). **Folder:** `1 NUMISTA.AI\BETA TEST\MY TESTING\24 OCT 2026`

## What Eric filed
- PDF: `Receipt Semiquincentennial President D Coin Roll.pdf` (US Mint item **26SQRP**)
- SS1: Add Coins still **Processing Files** + file badge **Done — 1 coin** (wrong for a 25-coin roll)
- Could not exit Add Coins; opened new tab → Review Hub
- SS3: nav shows truncated **Review …** with badge 2
- SS2: Hub two rows, both Item **26SQRP**, **QTY 1**, cost **$70.95**; deleted both
- Ask: **100% by Monday** (within 48h hard stop ~Mon 6:32 PM ET)

## CoS verdict
1. **Mint SKU pack/roll expansion FAIL** — tip catalog (`us_mint_catalog_service`) already defines 26SQRP as 25-coin roll; `enrich_us_mint_item` does **not** set Quantity=25. Live 15i QTY fix (Nx invoice lines → one row Qty N) does **not** cover this class.
2. **Add Coins status UX FAIL** — Processing vs Done contradiction; exit path unclear.
3. **Duplicate Hub rows + truncated nav** — product/UX defects from one PDF.

## Morning (do not start tonight)
- Plan then build: Mint item codes with known pack size (26SQRP roll=25, bags, etc.) → Quantity / pack expand before Hub.
- Honest Done/Processing + exit from Add Coins; Review Hub label.
- FT regate with this PDF on live after deploy YES.

No deploy / no AG wake tonight per Eric 20-min review + shut down.
## Corrections (Eric, post-review -- filed CoS 25 Oct 2026 ~7:40 AM ET)
1. **Two Hub rows are NOT a single-upload split.** Eric uploaded the same Mint PDF **twice**. Drop "duplicate Hub rows from one PDF" from the product bug list; Monday bar stays Mint pack/roll Qty + Add Coins Done/exit + Review Hub label.
2. **Post-roll inventory context (not this build):** of the 25 Presidential $1s in the 26SQRP roll, Eric later **sold 2 at $5 each** and **gifted 2** (**21 remaining**). Prefer U.S. Mint figures for ingest; sell/gift / Certificate of Transfer is a **separate** product track -- only note future Qty adjust after correct Qty 25 ingest. Do not expand this Monday plan into full sell/gift unless already half-built.
