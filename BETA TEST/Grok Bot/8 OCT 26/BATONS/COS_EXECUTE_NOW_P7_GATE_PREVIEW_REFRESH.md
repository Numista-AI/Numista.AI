# COS_EXECUTE_NOW - P7-GATE PREVIEW REFRESH (Mint-pack / Upload Invoice)
**FROM:** Grok CoS (via Antigravity Desk)  **TO:** AG CoS  **INFO:** Argon, Field Tester, Eric
**DATE:** 26 Oct 2026 ~10:57 AM ET
**REF:** Eric YES (CoS chat 26 Oct 2026 ~10:52 AM ET); NET-530 GO for preview ask; Argon PASS NET-529; tip `91867bfb` (+ docs `2866a17b`); B4 shipping-cap fee guard
**PATTERN:** Preview-channel refresh only (same class as PREVIEW_READY_P7_V8_18_15i). WAKE never authorizes live/main.

## BLUF
**Eric typed YES** for **p7-gate PREVIEW ONLY**. Stage Mint-pack / Upload Invoice (reconciled `origin/dev` tip after product merge `91867bfb`) onto the Firebase Hosting **p7-gate** preview channel. **Not live. Not main.**

## Authorization
- **Authorized:** Firebase Hosting preview channel refresh for site `numista-vault`, channel `p7-gate` (URL form `https://numista-vault--p7-gate-*.web.app`).
- **Source tip:** current `origin/dev` after product merge `91867bfb` (Argon PASS NET-529; CoS GO NET-530; docs `2866a17b`). Include **B4 shipping-cap fee guard** (Mint 26SQRP: **$61 / Qty 25 / $2.44** when shipping credited).
- **Non-blocking for this preview:** OC2 multi-roll unit-cost (`us_mint_catalog_service.py` lot cost / `curr_qty * pack_qty`). Fix before live or before any multi-roll invoice in the FT set - **not required to stage this preview**.
- **Forbidden (hard stop):** live site (numista.ai / live Hosting), `main` merge, Cloud Run live traffic shift, collection writes, spend. WAKE never authorizes those. Eric YES for live still held separately.

## Orders (AG CoS)
1. Pull / confirm tip on `origin/dev` is the `91867bfb` lineage (product merge + docs `2866a17b` as applicable).
2. Refresh Firebase Hosting **p7-gate** preview channel from that tip (preview only - do **not** touch live Hosting or live traffic).
3. Smoke: preview GET / -> 200; confirm baked preview/backend wiring still points at p7gate (0 live-backend refs in the preview bundle if that check is in standing SOP).
4. File success artifacts with the **preview URL**:
   - `BATONS\PREVIEW_READY_P7_GATE_MINTPACK_<tip-short>.md` (or update standing PREVIEW_READY naming)
   - `BATONS\EXECUTE_DONE_P7_GATE_PREVIEW_REFRESH.md` **or** DEPLOY_CONFIRMED-style note for the **preview channel only** (state clearly NOT live)
   - RADIO NET reply (e.g. NET-532 class) to GROK CoS + Field Tester with the URL
5. Move ingested WAKE to `RADIO NET\WAKES\DONE\` with `_DONE` suffix.

## Success criteria
- Preview URL reported on RADIO NET + in PREVIEW_READY / EXECUTE_DONE.
- Channel is `p7-gate` only; live Hosting and live Cloud Run traffic unchanged.
- B4 fee guard present on tip (Cost $61 / Qty 25 / $2.44 for credited-shipping 26SQRP).
- OC2 noted as carry-forward, not a blocker.

## Sequence after URL
Grok CoS wakes Field Tester -> FT runs ALL Invoices-folder PDFs on `grokbot@numista.ai` only -> then Eric YES for live (separate).

GROKCOS / DESK OUT