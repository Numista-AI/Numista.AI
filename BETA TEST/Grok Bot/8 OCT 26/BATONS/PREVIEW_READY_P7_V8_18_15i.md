# PREVIEW_READY - P7 V8.18.15i (p7-gate)

**When:** 2026-10-24 6:14 PM ET (America/New_York)
**Authorized:** Eric typed YES refresh p7-gate from 6ee3de89 (chat 24 Oct 2026). Live deploy NOT approved.

## Build
- Commit: `6ee3de8902ab929d34cff7bc59bcc94d5dc73639` (branch `p7-v8.9`)
- Scope: invoice `2x`/`Nx` lines as **one row with Quantity N** (Option B); hardened 092052 multipage assertions
- Diff vs `72cb6c0f`: exactly 3 files — `numista_backend/main.py`, `numista_backend/tests/test_invoice_fixtures.py`, `numista_backend/tests/test_v8_18_15e_regression.py`
- Frontend version label still **v8.18.15h** (NET-492 scope lock: no Flutter version bump in this hotfix). Backend tip is 15i QTY.

## Preview (channel only - NOT live)
- Preview URL: https://numista-vault--p7-gate-8avtpz22.web.app
- Channel: `p7-gate` on site `numista-vault`, project `studio-9101802118-8c9a8`
- Expires: 2026-10-31 ~6:13 PM ET
- Hosting version: `950c3aa7fd3f00da`
- Bundle check: `Numista.AI v8.18.15h` label + baked `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (67 refs) + p7gate scan (1 ref); 0 live backend refs

## Backend (0% traffic)
- Revision: `numista-backend-00487-hub`
- Tag: `p7gate` → https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app
- Traffic: **0%** on 00487-hub
- Live traffic unchanged: **100%** on `numista-backend-00479-beg`
- Scan p7gate left unchanged: `numista-scan-service-00344-cas` (scan not in 15i diff); live scan **100%** `00337-vqk`

## Smoke (24 Oct 2026 ~6:14 PM ET)
- Preview GET / → 200
- Live https://numista.ai → 200
- p7gate backend GET / → 200
- Cloud Run traffic map: live still 100% `00479-beg`; p7gate tag moved `00486-giy` → `00487-hub` at 0%

## FT re-gate next (grokbot@numista.ai ONLY)
See NET-496. Live YES held. OVER.