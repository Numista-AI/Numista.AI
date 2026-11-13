# UX Gate: P7 V8.9 (commit 3a0c0b26)
Preview: https://numista-vault--p7-v89-gate-cyzolm0n.web.app
Gated 16 Oct 2026 by UX Designer, using the signed-out demo only. Nothing was saved and there was no sign-in.
Main gate: 1025px and 1280px. Phone (389px) is nice-to-have. Body text standard: 18px.

## VERDICT: FAIL

## What passes
- Checklist title wraps in full. Coin names wrap. Checkboxes have a 48px tap target. Helper text is about 18px.
- No calls to /api/news/feed or other user endpoints, and no CORS errors.
- Coin count matches: My Collection's Coins tab shows 100, the same as the dashboard.
- Everything that passed in V8.8 still holds:
  - View Checklist and its caption sit inside the card.
  - Card titles wrap.
  - The demo add is blocked ("Create a free account to save") and sends no add_coins POST.
  - No /assets 404 and no Firestore 403.
  - Type it in and Manual Entry open full screen with a 56px Save.
  - The money value stays on one line.

## What fails (blockers)
1. **Number keypad.** Year, Cost and Qty are `type="text"` with no `inputmode`, on both entry forms. Fix: Year and Qty get `inputmode="numeric"`, and Cost gets `inputmode="decimal"`. Set them on each field directly, with no logic that changes them on focus.
2. **Checklist buttons.** Print, Download PDF, and "Add N Selected Coins" are 40px tall. They need to be at least 48px.
3. **Mint column is cut off instead of wrapping.**
   - At 1280: "Enhanced Uncirculated (struck at West Point; c…"
   - At 1025: "(struck a…", "Congratula…"
4. **£ sign is garbled on the coin detail screen.** The 2022 Britannia shows "Â£2 Silver" there. The dashboard and collection table show it correctly. Under the systemic rule, check every screen, the PDF and the CSV export.
5. **My Collection "All" tab crashes.** It shows "Something went wrong loading this screen" with a main.dart.js stack trace, at both 1025 and 1280.
6. **Demo session dropped out.** At 1025, switching to Table view reloaded the page and landed on the sign-in screen.
7. **Snackbar covers text.** At 1280 the demo snackbar covers the "Sign in to save…" caption under the Add button. It no longer covers the sidebar.

## Nice-to-have
- The "Coins" filter includes paper notes.
- The "Premium" label on the dashboard donut chart is clipped at the left edge.
- Phone: Print and PDF are also 40px, and the mint column is cut off.

## Evidence
21 PNGs are in the box folder /workspace/numista-ux/p7v89/. The key ones are copied alongside this file as UX_GATE_P7_V89_*.png.
