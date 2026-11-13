# COS_SCORE P7 GATE V8.18.15i (6ee3de89) - Grok CoS, 24 Oct 2026 ~6:35 PM ET

Source: NET-497 (Field Tester, grokbot, p7-gate preview https://numista-vault--p7-gate-8avtpz22.web.app). Backend under test: numista-backend-00487-hub (p7gate tag). Argon NET-494 PASS + CoS NET-495 BUILD PASS stand.

## VERDICT: GATE PASS

| Check | FT NET-497 | CoS |
|---|---|---|
| Backend = p7gate not live during gate | PASS | PASS |
| 092052 no 60s timeout | PASS (~2.5 min) | PASS |
| ~14 rows / 17 coins | PASS (+14 Hub) | PASS |
| 1964-D / 1982-S / 2001-P each ONE row Qty=2 | PASS | PASS |
| Per-page invoice # / date | PASS (p1 67000011/2024-11-07; p2 67226944/2025-01-23) | PASS |
| Review Hub commit | PASS | PASS |
| Manual duplicate | PASS | PASS |

**Caveat (non-blocking):** importer red banner after Done — `Invalid char in element with leading alpha: Retailer/Website`. Rows still landed; FT did not retry. Track separately; does not fail QTY gate.

**Out of scope (NET-492):** Hub/commit consumers of Qty>1 beyond import → single-row Qty=N (15j+). Melt under-count on main: after this live path.

## Live YES
Eric typed YES ~6:28 PM ET 24 Oct: live cherry-pick / deploy of tip `6ee3de89` tonight. 48h ceiling for Mint invoice Go (~Mon 26 Oct 6:32 PM ET) — shipping tonight under that YES.

## Deploy path note
Aborted main+3-file checkout: tip `main.py` imports `routes.cert_routes` and `services.duplicate_check` missing from `origin/main` (would crash). Prior SOP (importer-auth PR #267): leave main PR unmerged when merge triggers CI redeploy. Live path = Cloud Run traffic shift of FT-tested revision `00487-hub` (built from tip) to 100%. See DEPLOY_DONE_P7_V8_18_15i.md + NET-498.
