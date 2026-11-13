# FT_RESULT — NET-585 / NET-593 UX 3 FIXES — OVERALL PASS
**Filed:** 2026-10-27 ~10:28 AM ET by Field Tester  
**Preview:** https://numista-vault--p7-gate-8avtpz22.web.app (dev 2234f7e4)  
**Account:** grokbot@numista.ai only · Live/main OFF · Never opened live

## BLUF
**OVERALL PASS** (functional). Caveats: N2 View-on-toast not exercised (no View seen); cert-field Enter submit inconclusive (Look Up button worked).

| Item | Result | Notes |
|---|---|---|
| 1 Add-by-Cert once / no Cert Lookup tab | PASS | Card once above More ways to add. 7 tabs, no Cert Lookup. |
| 2 Autofocus + success close (+ View) | PASS* | Autofocus PASS. PCGS 53652580 → Coin Found 2025-W $1 PR70DCAM. Add → returned to hub with green "✅ Coin added to your collection!". *No View action seen on toast (N2 not exercised). Enter on cert field inconclusive. |
| 3 Hub storage without Edit Coin | PASS | "+ Set Location" on grokbot 2026-D Dime (dup_v81815f). Box 1 chip + Enter → badge "Box 1". Clear + Enter → cleared. Edit Coin never opened. |
| 4 Mint-pack spot-check | PASS (note) | Hub/Paper Trail lists 2026-10-26 Mint ingests. Invoice Importer not re-opened. |

## Notes
- N1 deep-link: not tested.
- Collection write: PCGS 53652580 added to grokbot (intentional).
- Hub badge 131 vs 3 visible leftover cards (stale badge note only).
- First load hung on splash until one reload.

## Shots (`shots_ux593/`)
90–98_net593_*.webp (Add, cert, found, toast, Hub storage before/after/clear, Paper Trail).

OVER.
