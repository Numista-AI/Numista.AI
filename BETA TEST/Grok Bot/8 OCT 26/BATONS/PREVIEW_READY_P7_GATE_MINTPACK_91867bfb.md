# PREVIEW_READY — P7 Gate Mint-Pack & Invoice Refresh (V8.18.15j Reconciled)

**When:** 2026-10-26 ~11:15 AM ET (America/New_York)  
**Authorized:** Eric typed YES stage Mint-pack / Upload Invoice on `p7-gate` PREVIEW ONLY (chat 26 Oct 2026 ~10:52 AM ET, ref NET-531 / `COS_EXECUTE_NOW_P7_GATE_PREVIEW_REFRESH.md`). Live deploy NOT approved.

## Build & Topology
- **Lineage Tip:** `91867bfb` (product merge of `origin/p7-v8.9` `6ee3de89` into `dev`) + docs `068f19d2` on `origin/dev`
- **Scope Included:**
  - V8.18.15j Mint-Pack / Roll Quantity expansion: `26SQRP` -> 25 coins, unit cost $2.44, lot cost $61.00.
  - B4 / OC1 Shipping Credit Cap guard: when shipping credited (`grand_total <= subtotal`), `total_global_fees` capped at `0.0`, ensuring exact $61.00 landed cost ($2.44/coin).
  - Preserved all live `origin/p7-v8.9` features: Option B 1-row Qty=N invoice lines, per-page metadata linking, duplicate check guards, 180s poll timeout.
  - Web UI: `add_coins.html` header `✅ All Files Processed` and `Exit` button active.
- **Carry-Forward (Non-blocking):** OC2 multi-roll unit-cost noted in NET-531 for resolution before live multi-roll runs.

## Preview (channel only — NOT live)
- **Preview Channel URL:** https://numista-vault--p7-gate-8avtpz22.web.app
- **Channel:** `p7-gate` on site `numista-vault`, project `studio-9101802118-8c9a8`
- **Expires:** 2026-11-02 ~10:12 AM ET
- **Hosting Version:** `86abdd63312e1ee7`
- **Bundle Wiring Check:**
  - Hosting rewrites route `/api/**` directly to Cloud Run service `numista-backend` in region `us-central1`.
  - Preview channel serves refreshed web bundle and `add_coins.html`.

## Backend (0% new traffic move / live unchanged)
- **Active Backend Revision:** `numista-backend-00487-hub`
- **Tags Kept:**
  - `p7gate` → https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app (revision `00487-hub`)
  - `greysheet` → https://greysheet---numista-backend-qntvrqvxma-uc.a.run.app (revision `00472-roc`)
- **Live Traffic:** Unchanged, 0 traffic moves executed during this preview staging.

## Smoke Checks (26 Oct 2026 ~11:13 AM ET)
| Target | Check | Result |
|---|---|---|
| https://numista-vault--p7-gate-8avtpz22.web.app/ | GET / | **200 OK** |
| https://numista-vault--p7-gate-8avtpz22.web.app/add_coins.html | GET /add_coins.html | **200 OK** (`✅ All Files Processed` + `exitAddCoins` present) |
| https://numista.ai/ | GET / | **200 OK** (live site untouched) |
| https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app/api/spot_prices | GET /api/spot_prices | **200 OK** |

## Next Phase
Ready for Grok CoS to wake Field Tester (`grokbot@numista.ai` ONLY) to test Invoices-folder PDFs on the preview channel. Live deploy remains held awaiting test results and Eric's explicit typed YES.
