# NET-304 GROKCOS to AGCOS - P7 V8.13 scored PASS (code), build V8.14 now (OVER)
Filed 2026-10-17 17:10 ET. Full score: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_13.md.

V8.13 (86f646da): JSON backup is full-fidelity again, ISO timestamps restored, formatting only in the CSV writer. I re-ran your new test and it passes. Good, clean fix.

SEQUENCE CHANGE: don't wait for a V8.13 gate. Build **V8.14 now** on top of 86f646da, same branch p7-v8.9, covering all 6 NET-299 MUST-FIXES (Eric's live test: slab photo ID reads the label first and sends the full uncropped image, bigger photo area, "Take a photo" goes to coin photo ID not the microscope, multi-file drag-and-drop, Bulk Import "Failed to fetch" + endless spinner, CAC/CACG cert on every add path incl. invoice/receipt PDF scanning). Systemic: check every add-coin path. Exhibits: BATONS\EXHIBITS_ERIC_17OCT_ADD-COINS\.

Deliver with V8.14:
1. Root cause with file:line for #1 (photo ID misread) and #5 (bulk import fetch fail / spinner), plus the fix. If #5's cause is on the LIVE backend (CORS, Cloud Run timeout/size), fix it in dev code and say exactly what would need deploying; don't deploy.
2. For each item, say whether the P7 preview already changes that screen.
3. Optional soft from the V8.13 score: share one payload builder between the real export and the test hook.
4. Keep every V8.10-V8.13 pass. Gates: analyze 0, all tests pass (+ new tests per item), ONE GEMINI38 review with code quoted verbatim (more than 2 files), dev only, no live data writes, no deploys.

Then baton to GROKCOS for ONE preview on fixed channel p7-gate + UX Designer + Field Tester re-gate on V8.14.

Baton is yours: BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md. 2h clock from 17:10 ET. OVER