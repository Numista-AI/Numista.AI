# FT_RESULT — NET-647 Mint FAIL-FIX (AG v4 / NET-654) — OVERALL FAIL
Filed 31 Oct 2026 ~12:25 PM ET · Field Tester · p7-gate preview only · grokbot@numista.ai · live/main untouched
Build: Hosting redeployed 11:57 AM ET; version.json 8.18.15 / 81818. Commit 30f851ac NOT stamped in bundle or UI — unconfirmed.

## BLUF
OVERALL FAIL — #6 QTY>1 "each" wrong on 26SQRP roll; #9 Set Location Save errors; #11 thumbnails partial; #8 / Fee $9.95 / dup amber unconfirmed.

| # | Item | Result |
|---|---|---|
| 1 | Upload an invoice launches importer | PASS |
| 2 | No scroll trap | PASS |
| 3 | Drop Zone/Browse above fold | PASS |
| 4 | Start Import auto-scroll | PASS |
| 5 | Go to Review Queue | PASS |
| 6 | $X.XX each when QTY>1 | FAIL — 26SQRP qty25 shows "$61.00 each" (line total; should be $2.44). Morgan x2 $169.00 each OK; Innovation qty2 $64.97 each (check) |
| 7 | Store/Dealer tip gone | PASS |
| 8 | Paper-trail not duplicated | UNCONFIRMED — one Scan File line per card; detail not opened |
| 9 | Storage chip out of title + Set Location | FAIL — chip out of title OK; Save "An unexpected error occurred"; location not persisted |
| 10 | Morgan guide step1 top-right | PASS |
| 11 | Review thumbnails | PARTIAL — new Mint rows gold "$" placeholder; only older 26RJ rows real images |
| 12 | Folder-Drop multi PDF | PASS — 7 PDFs Done |
| 13 | All-Invoices flow | PASS — 7 receipts, 33 coins, 2 dups flagged, $1,284.24, no errors (no folder-only picker; multi-select) |
| NG | Fee $9.95 | UNCONFIRMED — no fee field in Hub/Edit; paper trail $70.95 = 61.00+9.95 |
| NG | Amber dup | UNCONFIRMED — summary "2 Duplicates Flagged", no amber chip seen |
| NG | Cream contrast | PASS |

State: no commits, no deletes; Hub pending 93 (includes older runs).
Shots: shots/ *.webp
OVER.
