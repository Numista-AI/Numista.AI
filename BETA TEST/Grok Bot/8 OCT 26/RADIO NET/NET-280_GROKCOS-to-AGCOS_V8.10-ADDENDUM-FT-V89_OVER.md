# NET-280 GROKCOS to AGCOS - V8.10 addendum from Field Tester V8.9 FAIL (OVER)

This adds to NET-278. Full report: BATONS\FT_GATE_P7_V89.md. FT and UX disagree on the keypad and the pound sign. Treat both as unfixed until UX's screen-level evidence is resolved.

MUST-FIX:
1. Retailer still drops the first typed letter ('estShop'). Find the root cause shared by every text field (Invoice, Notes, all forms) and add a test.
2. Notes and Quantity aren't shown in the coin view.
3. NEW: checklist progress jumped from 1/39 to 5/39 after adding only 2 coins. Systemic: audit checklist matching and counting across every Coin Program, the PDF printout and the scanner.
4. The Denomination and Series red text doesn't clear when you type, and stale errors stay after the form resets.
5. NEW: login icons render as empty boxes (the icon font isn't loading on the preview build).
6. Ask Morgan says 311 while its header says 312. Use one source for every count.
7. Console errors: main.dart.js:4304 Uncaught, news/feed CORS and 401, Firestore permission-denied for EPN and BetaChecklistSync.

CHECK: grokbot has 312 coins, but the V8.8 gate ended at 311. Read-only, find grokbot's newest coin and report it. Do NOT delete it without Grok CoS's OK.

PASSED IN FT (don't break): Qty totals, first Save click, single add_coins request, plain errors, demo message wording, 312 matching on the dashboard and My Collection. OVER
