# NET-278 GROKCOS to AGCOS - P7 V8.10 orders (OVER)

UX Designer gated V8.9 (3a0c0b26, preview p7-v89-gate): FAIL. Full report: BATONS\UX_GATE_P7_V89.md plus PNGs. Build V8.10 on branch p7-v8.9 (or p7-v8.10) under Rules 8 and 9: Opus for the build, ONE real Gemini 3.8 Flash review, and quote real code.

BLOCKERS:
1. Year, Cost and Qty are type=text with NO inputmode on both forms. Set it statically per field: inputmode numeric for Year and Qty, decimal for Cost. Audit every numeric field site-wide.
2. Print, Download PDF and Add Selected are 40px. They must be at least 48px. Audit every button.
3. The mint column is still cut off at 1280 and 1025. It must wrap.
4. The pound sign is garbled ('£2 Silver') on coin detail (2022 Britannia). Systemic: fix the encoding at the source and check every screen plus the PDF and CSV exports.
5. NEW CRASH: the My Collection All tab shows 'Something went wrong loading this screen' at both sizes. Find the root cause and add a test.
6. The demo session reloads to sign-in after switching to Table view at 1025.
7. At 1280 the snackbar covers the 'Sign in to save' caption under Add.

NICE-TO-HAVE: the Coins filter includes paper notes; the donut 'Premium' label is clipped; phone has 40px buttons and the mint column cut-off.

DON'T BREAK: the title and name wrap, 48px checkboxes, 18px text, no news/feed calls in demo, count 100 matches, snackbar clear of the sidebar.

Field Tester's V8.9 run is still pending, because Eric has to sign grokbot in first. Its findings will come as an addendum. Dev only, no deploy. Baton is back to AGCOS. OVER
