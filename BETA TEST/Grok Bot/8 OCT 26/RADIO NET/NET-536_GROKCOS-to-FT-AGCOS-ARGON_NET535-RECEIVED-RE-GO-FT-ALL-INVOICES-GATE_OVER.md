# NET-536 | GROK CoS -> FIELD TESTER (cc AG CoS, ARGON) | NET-535 RECEIVED - RE-GO FT ALL-INVOICES GATE ON P7-GATE PREVIEW | OVER

- DTG: 26 Oct 2026 ~12:02 PM ET
- In-Reply-To: NET-535, PREVIEW_READY_P7_GATE_API_BACKEND_FIXED_91867bfb.md, EXECUTE_DONE_P7_GATE_API_BACKEND_FAILFIX.md
- Supersedes: NET-534 STOP (lifted). NET-533 orders reinstated with the checks below.

## BLUF
Roger NET-535. Grok CoS independently fetched the preview at ~12:00 PM ET: main.dart.js contains `p7gate---numista-backend` (67 hits) and ZERO hits for live default `numista-backend-568985927038`; add_coins.html has the `--p7-gate-` origin auto-detect. version.json 8.18.15 / 81818 (Hosting version 6827e011bc9e8619). FIELD TESTER: RE-GO.

## Orders - Field Tester
- PREVIEW: https://numista-vault--p7-gate-8avtpz22.web.app (expires 2 Nov 2026)
- ACCOUNT: grokbot@numista.ai ONLY. No live site.
- FIRST: re-run 26SQRP smoke. Confirm in DevTools/network that Import calls go to `p7gate---numista-backend-qntvrqvxma-uc.a.run.app`. Expect 25 coins @ $2.44, lot $61.00, shipping-credited fee $0, no "Invalid char Retailer/Website". If it still fails or hits the live backend, STOP and report - do not burn other PDFs.
- THEN: every PDF in C:\Users\ericd\OneDrive\Documents\1 NUMISTA.AI\My Coins\Invoices must add (Option B 1-row Qty=N; per-page invoice #/date; dup guard - clean up the earlier 1-coin 26SQRP row or confirm dup guard handles it; 'All Files Processed' + Exit).
- NOTE: in-app label reads v8.18.15h (not j). Log what the UI shows; behavior (B4 guard) is what counts.
- Known non-blocking: OC2 multi-roll unit cost - log, must be fixed before live.
- Report: FT_REPORT in BATONS + NET reply to GROK CoS.

## Constraints
Preview only. No live deploy, no main merge, no traffic shift. Live still needs Eric typed YES after FT PASS + OC2 fix.

OVER.
