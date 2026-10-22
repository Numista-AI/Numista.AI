# FT P7 GATE V8.18.15a — OVERALL FAIL
Preview: numista-vault--p7-gate-8avtpz22.web.app. Label v8.18.15 (commit not shown in UI). Account: grokbot only.

| Check | Result | Evidence |
|---|---|---|
| 1 Mint invoice PDF end to end (REQUIRED) | FAIL | 092052: run A = Error with no text; run B stuck at "Processing 0/1" >90s and polling stopped. Rows still landed in Review Hub (17 per run, QTY 1, Retailer/Invoice/Date N/A). Commit worked: 312 -> 346. |
| 2 Cert lookup | PASS | PCGS 53652580 = 2025-W $1 PR70DCAM |
| 3 Cert-photo scan <30s | FAIL | 60-100s, then "Couldn't read a cert number" |
| 4 Bulk Import on preview backend | PASS | all calls to p7gate---numista-backend |
| 5 Spot price / console | PASS (spot) / WARN | No spot timeouts. CORS on storage.googleapis images and Firestore Listen errors. |

Cleanup anomaly: the 34 coins disappeared by themselves (346 -> 312) without my action. Totals moved: cost 951.59 -> 946.87, melt 2197.76 -> 2187.13. Morgan qty 2 not verified.
