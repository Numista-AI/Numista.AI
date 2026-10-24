# PREVIEW_READY — P7 V8.18.15h (p7-gate)

**When:** 2026-10-24 8:09 AM ET (America/New_York)
**Authorized:** Eric typed YES preview when Argon PASSes (chat 24 Oct 2026). Live deploy NOT approved.

## Build
- Commit: `72cb6c0ff2358251999ff227fd5209bb43928749` (branch `p7-v8.9`)
- Version: v8.18.15h
- Scope: multi-page per-page invoice metadata + qty/unit cost + 180s polling; frontend version bump + `add_coins.html` poll timeout

## Preview (channel only — NOT live)
- Preview URL: https://numista-vault--p7-gate-8avtpz22.web.app
- Channel: `p7-gate` on site `numista-vault`, project `studio-9101802118-8c9a8`
- Expires: 2026-10-31 ~8:08 AM ET
- Hosting version: `9b7308b3f1f4e71a`
- Bundle check: `Numista.AI v8.18.15h` + baked `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app`

## Backend (0% traffic)
- Revision: `numista-backend-00486-giy`
- Tag: `p7gate` → https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app
- Traffic: **0%** on 00486-giy
- Live traffic unchanged: **100%** on `numista-backend-00479-beg`
- Scan p7gate left unchanged: `numista-scan-service-00344-cas` (scan not in 15h diff); live scan **100%** `00337-vqk`

## Smoke (24 Oct 2026 ~8:09 AM ET)
- Preview GET / → 200
- Live https://numista.ai → 200
- p7gate backend GET / → 200
- Cloud Run traffic map unchanged except p7gate tag moved 00485-vav → 00486-giy

## FT re-gate next (grokbot@numista.ai ONLY)
Frozen pass list + invoice **092052** multipage case (all coins, correct QTY, invoice #, date). OVER.
