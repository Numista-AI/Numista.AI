# NET-496 GROKCOS to AGCOS / ARGON / FT: P7 V8.18.15i PREVIEW READY (OVER)

Filed 2026-10-24 ~6:14 PM ET. Authorized: Eric YES refresh p7-gate from `6ee3de89`. **Live NOT approved.**

- Build: V8.18.15i QTY one-fix, commit `6ee3de89` (`p7-v8.9`). Diff vs `72cb6c0f` = 3 files (main.py + 2 tests). UI label still v8.18.15h (NET-492 scope lock).
- Preview URL: https://numista-vault--p7-gate-8avtpz22.web.app (channel `p7-gate`, expires 31 Oct 2026 ~6:13 PM ET, hosting `950c3aa7fd3f00da`)
- Backend p7gate: `numista-backend-00487-hub` (**0% traffic**) — https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app
- Scan p7gate unchanged: `numista-scan-service-00344-cas`
- Live traffic unchanged: backend `00479-beg` 100%, scan `00337-vqk` 100%
- Smoke: preview / + p7gate backend / + https://numista.ai all 200; bundle has p7gate API URL, 0 live backend refs
- Detail: `BETA TEST/Grok Bot/8 OCT 26/BATONS/PREVIEW_READY_P7_V8_18_15i.md`
- Argon NET-494 PASS + CoS NET-495 BUILD PASS stand. No data written by GROKCOS.

## FT re-gate (grokbot@numista.ai ONLY) — frozen pass list
1. Invoice **092052** upload → **14 rows** / 17 coins; **1964-D, 1982-S, 2001-P** each a **single row with QTY 2** (+ exact Cost); per-page invoice # and date present.
2. No 60s timeout on multipage import.
3. Review Hub commit: saves with no error.
4. Manual duplicate add: duplicate is flagged.
5. **OUT OF SCOPE (NET-492):** Hub/commit paths that consume Qty>1 beyond import→single-row Qty=N. Track separately (15j+).

Any regression on the frozen list = REJECT. Report PASS/FAIL with screenshots back to GROKCOS. Live YES held. OVER.