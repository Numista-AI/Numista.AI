# UX GATE P7 V8.8 (NET-269) - FAIL
**Tester:** UX Designer | **Filed by:** Grok CoS, 2026-10-16 08:57 ET
**Preview:** p7-v88-gate (origin/dev e104ee0f, incl. 6b94654e)
**Method:** signed-out demo only. Nothing saved, no sign-in.
**Main gate: 1025 + 1280. Phone (389) is nice-to-have per Eric 16 Oct.**
Screenshots: UX Designer box /workspace/numista-ux/p7v88/

## PASS
- View Checklist + 'Advances overall record' caption inside card at all sizes.
- No Ask Morgan overlap at tablet/computer.
- Demo caption matches the demo block.
- Sidebar 'Ask Morgan' contrast.
- Sign-in logo present after reload.
- Tablet/computer card titles wrap, no ellipsis.
- Checkboxes 48px; helper text ~18px.
- All prior passes hold: demo add blocked ('Create a free account to save'), no add_coins POST, no /assets 404, no Firestore 403, no mint-releases spam, $ on one line, 'Type it in' full screen with 56px Save, tablet Manual Entry full screen, single scrollbar on sign-in.

## FAIL
1. **Numeric keypad INVERTED (worse).** All inputs type=text. On focusing Year, inputmode=numeric is added to the OTHER fields (Mint Mark, Denomination, Retailer, Invoice, Storage) and removed from the focused one. Year/Cost/Qty never get a number pad; text fields do.
2. **Checklist.** Print + Download PDF 40px tall (need 48). At 1025 title truncated ('Numismatic Colle...'). Mint column truncated at 1280 ('struck at West Point; c...'); names + mints truncated at 1025 ('Congratula...', 'On sale Sept...'). Rows must wrap.
3. **Pound sign mojibake** in Collection list at 1280 ('2022 United Kingdom Â£2 Silver'). Dashboard correct -> per-screen encoding. Systemic rule: audit every screen + PDF + CSV export.
4. **Demo calls /api/news/feed** - CORS-blocked on load and on return to dashboard.

## NEW BUGS
- My Collection shows 'COIN COLLECTION 0 Items' (portfolio for 5 items) vs dashboard 100 coins; empty card with spinner; 'ESTIMATED PORTFOLIO VA...' truncated. Count mismatch - systemic check.
- At 1025 the demo session dropped back to sign-in on its own once.
- Demo snackbar spans full width and covers bottom sidebar buttons.

## VERDICT: FAIL -> V8.9 orders NET-270.