# NET-437 — GROK CoS to UX Designer + Field Tester — P7 V8.18.15d PREVIEW UP — RE-GATE — OVER
Time: 22 Oct 2026, 8:05 PM ET. Eric approved this hidden no-traffic refresh in chat.

## What is up
- Preview: https://numista-vault--p7-gate-8avtpz22.web.app (expires 29 Oct 2026, 8:02 PM ET)
- Built from commit 1058fe8b (branch p7-v8.9, V8.18.15d; label still shows v8.18.15, as Eric accepted)
- Backend test copy: numista-backend-00483-mop (tag p7gate, 0% traffic)
- Scan test copy: numista-scan-service-00343-mof (tag p7gate, unchanged)
- Live untouched: backend 00479-beg 100%, scan 00337-vqk 100%
- WARNING: the preview uses the REAL database. Use the grokbot account only. No writes to Eric's collections.

## Re-gate checklist
1. U.S. Mint invoice test: import a U.S. Mint invoice PDF with no invoice number on grokbot. Every coin should be saved. The summary should show the real saved and skipped counts.
2. Duplicate Year/Mint/Denom import (grokbot ONLY): import a coin that matches the Year, Mint and Denom of a coin grokbot already owns. It must be SAVED and flagged as a possible duplicate, not silently dropped. Check that the snackbar counts match what actually landed. Check the singular "1 skipped" wording.
3. Tap targets: re-check sizes on mobile web on the import and review screens.
4. NGC wording: confirm the copy is correct and no NGC scraping is implied.
5. Label scans: PCGS and NGC slab label scans still work end to end (do not push past the PCGS block).

Report PASS or FAIL with screenshots to RADIO NET as NET-438 (UX) and NET-439 (FT). No deploys and no live changes. OVER
