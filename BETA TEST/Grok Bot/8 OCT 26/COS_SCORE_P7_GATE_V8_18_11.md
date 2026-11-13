# COS SCORE - P7 GATE V8.18.11 (p7-v8.9 @ 65072e6f) - FAIL
Scored by GROKCOS, 2026-10-20 ~17:05 ET. Preview: https://numista-vault--p7-gate-8avtpz22.web.app (backend 00471-pec, scan 00342-kex). Live untouched.

## Verdict: FAIL -> rebuild as V8.18.12 (see NET-387)

## Sources
- UX Designer: BETA TEST\Grok Bot\20 OCT 26\UX_P7_GATE_V4.md - FAIL
- Field Tester (grokbot only, clean load, count 312 before/after): FAIL, 4 of 6 checks covered

## Field Tester matrix
| # | Check | Result |
|---|---|---|
| 1 | Invoice PDF adds coins | FAIL - 092052.pdf errors ~18 s, 0 coins, status poll `'list' object has no attribute 'get'` (old CORS error gone) |
| 2 | Cert # mismatch keeps typed number | NOT TESTABLE - photo OCR never reads cert on CACG clear-slab front; typed 663261170 not overwritten |
| 3 | S-mint slab in Collection/CSV/Morgan | NOT DONE - manual slab form kept stale cert after new number typed; Add Coin Manually input lag, keystrokes land in wrong field |
| 4 | Camera add | PASS (FT) / FAIL (UX: raw NotFoundError, no fallback button) |
| 5 | Add under 30 s | NOT MEASURED |
| 6 | No GreySheet bid | PASS (partial) |
Console: uncaught error main.dart.js:4303; Firestore permission-denied from [EPN] credential load.

## UX findings
1. Cert: not-found sends user to PCGS.com (dead end); heading says "PCGS Certification Number" with 'Not sure'; grader chips ~29px; label OCR fails on clear slab.
2. Confirm card: Mint 'W' PASS (show 'W (West Point)'); Confirm & Save 42px; no Cancel; Scan Another 32px; field text 12-13px; Variety cut off; 'reverse unobserved' jargon.
3. Invoice: two-PDF list works; no review card before save; Receipt Scan has extra hub/page hop.
4. Camera: raw NotFoundError text, no [Choose a photo instead], 32px buttons.
5. Recheck: blurred slab -> Cert='blurred', no error card; back/collapse arrows 40px. 404s/console clean on UX run.

## Passes kept
Mint fix (W), banner v8.18.11, GreySheet bid not shown, CORS on /api/receipts fixed, 404s clean.

## Blocking (P0): invoice/receipt PDF import - MUST-KEEP feature. No Eric YES request until FT check 1 passes.
