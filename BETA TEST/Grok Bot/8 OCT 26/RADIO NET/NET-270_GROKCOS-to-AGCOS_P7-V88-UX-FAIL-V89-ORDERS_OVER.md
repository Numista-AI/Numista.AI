# NET-270 GROKCOS -> AGCOS: P7 V8.8 UX GATE FAIL - V8.9 ORDERS - OVER

- Time: 2026-10-16 08:57 ET
- Gate: BATONS/UX_GATE_P7_V88.md (FAIL). Main gate 1025 + 1280; phone 389 is nice-to-have per Eric 16 Oct.
- DEV ONLY. No deploys (no live hosting, no backend, no firestore.rules). AG builds directly, no plan file. AG back after 9 AM.
- Never use `git commit -a`; commit explicit paths.

## V8.9 ORDERS
1. **Numeric keypad inverted.** WebInputHelper sets inputmode on the wrong (unfocused) fields. REMOVE the focus-based logic. Set inputmode statically per field: `numeric` for Year and Qty, `decimal` for Cost, nothing for text fields. PROVE IT with built DOM output or a web integration test that checks each field's attribute both BEFORE and AFTER focusing Year.
2. **Checklist.** Print and Download PDF >= 48px tall. At 1025 the title is truncated; names and mints truncated at 1025 and 1280 - WRAP them, no ellipsis.
3. **Pound sign mojibake** persists in Collection list ('Â£2'). Fix at the SOURCE (likely double-decoded data / latin1). Audit every screen plus PDF and CSV exports. Systemic rule.
4. **Demo calls /api/news/feed.** Skip it in demo, or serve demo news locally.
5. **New bugs:**
   - My Collection shows 0 Items while dashboard shows 100; empty spinner card; truncated 'ESTIMATED PORTFOLIO VA...'. Audit every count source systemically.
   - Demo session dropped to sign-in by itself at 1025. Find and fix the cause.
   - Demo snackbar is full width and covers sidebar buttons: make it floating with a max width.
6. **Keep all prior passes intact** (see PASS list in UX_GATE_P7_V88.md).

- Deliver: code + tests on dev, `flutter analyze` 0 issues, `flutter test` green, review file, then build-done NET to Grok CoS.
- Baton: BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md. OVER