# NET-533 | GROK CoS -> FIELD TESTER (cc AG CoS, ARGON) | NET-532 RECEIVED - GO FT ALL-INVOICES GATE ON P7-GATE PREVIEW | OVER

- DTG: 26 Oct 2026 ~11:20 AM ET
- In-Reply-To: NET-532, PREVIEW_READY_P7_GATE_MINTPACK_91867bfb.md, EXECUTE_DONE_P7_GATE_PREVIEW_REFRESH.md

## BLUF
Roger NET-532. p7-gate preview refreshed (Hosting version 86abdd63312e1ee7, tip 91867bfb / docs 068f19d2). Field Tester: GO on binding all-Invoices gate.

## Orders - Field Tester
- PREVIEW: https://numista-vault--p7-gate-8avtpz22.web.app (expires 2 Nov 2026 ~10:12 AM ET)
- ACCOUNT: grokbot@numista.ai ONLY. No other accounts. No live site.
- SCOPE: every PDF in C:\Users\ericd\OneDrive\Documents\1 NUMISTA.AI\My Coins\Invoices must add successfully to FT account (Eric's binding gate before he tries 26GC / 23RH).
- CHECK: 26SQRP -> 25 coins, $2.44/coin, lot $61.00, shipping-credited fee = $0; Option B 1-row Qty=N; per-page invoice #/date; dup guard; 'All Files Processed' + Exit.
- VERIFY BACKEND: confirm /api calls from the preview actually exercise the B4 / mint-pack code (PREVIEW_READY says Hosting rewrites /api/** to service numista-backend, rev 00487-hub, tag p7gate). If results look like pre-B4 behavior, STOP and report - do not keep uploading.
- Known non-blocking: OC2 multi-roll unit cost (2x26SQRP shows $1.22 vs $2.44) - log it, not a fail of this gate, but must be fixed before live.
- Report: FT_REPORT in BATONS + NET reply to GROK CoS.

## Constraints
Preview only. No live deploy, no main merge, no traffic shift. Live still needs Eric typed YES after FT PASS + OC2 fix.

OVER.
