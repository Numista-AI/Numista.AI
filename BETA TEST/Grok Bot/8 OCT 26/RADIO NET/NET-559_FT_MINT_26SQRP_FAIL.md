# NET-559 FT — 26SQRP canary FAIL (strict Hub Package/Roll)

**When:** 26 Oct 2026 ~16:47 ET  
**Preview:** https://numista-vault--p7-gate-8avtpz22.web.app  
**Claimed backend:** p7gate 00493-saw  
**Account:** grokbot@numista.ai  
**PDF:** Receipt_Semiquincentennial_President_D_Coin_Roll.pdf (once, after clearing NET-545 stale)  
**Committed:** N  

## BLUF
FAIL strict: Hub row lacks Package/Roll wording (shows From Set banner + Cost `$61.00 (25 @ $2.44)` + Fee $0.00). Edit Coin PASS with `Package/Roll: $61.00 (25 @ $2.44) • Fee: $0.00`. Qty25 / $61 / 1 row / Mint / no illegal keys / no bad dupe all PASS. Big improvement vs NET-545.

## Pass/fail

| Check | Result |
|---|---|
| Illegal keys | PASS |
| 1 Hub pending | PASS |
| Qty 25 | PASS |
| Lot $61 / unit label | PASS — `$61.00 (25 @ $2.44)` |
| Fee $0 Hub | PASS |
| Fee $0 Edit Coin | PASS |
| Package+Fee Edit Coin | PASS |
| Package+Fee Hub | FAIL — no Package/Roll on Hub row |
| Mint | PASS |
| Bad dupe / phantoms | PASS |
| Commit | N |

## Shots
60–63 under /workspace/p7gate/shots_mint_all/
