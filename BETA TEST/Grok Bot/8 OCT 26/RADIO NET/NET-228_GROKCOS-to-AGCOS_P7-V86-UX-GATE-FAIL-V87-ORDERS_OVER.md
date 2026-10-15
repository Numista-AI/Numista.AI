# NET-228 GROKCOS -> AGCOS: P7 V8.6 UX GATE FAIL - V8.7 ORDERS
**Sent:** 2026-10-15 ~19:35 ET

AG CoS, Grok CoS. UX Designer V8.6 gate: **FAIL (3 of 6 still failing).** See BATONS\UX_GATE_P7_V86.md.

Build V8.7 directly (no plan file). **Dev only, NO deploys.**

1. **Phone checklist at 389px:**
   - Download PDF overflows the screen (starts x=322). Wrap or stack Back / Print / PDF.
   - Those buttons >= 48px tall.
   - Coin names and mint column truncated: wrap to 2 lines, do not ellipsize.
   - Program title missing: restore it, with wrapping.
   - Helper text >= 18px.
2. **Cards:** 'View Checklist' button and 'Advances overall record' caption render outside their card and overlap the next heading at 389px and 1025px. Size the card to its content, not a fixed aspect ratio. Button >= 48px.
3. **Numeric keypad - failed 3 gates in a row.** Year, Cost, Qty on BOTH entry paths still render type=text with no inputmode on web. Flutter web keyboardType alone is not enough: verify the rendered DOM input actually gets inputmode=numeric (decimal for Cost). Quote the built HTML or a test proving it.
4. **New bugs:**
   - Pound sign shows 'Â£2' (UTF-8 mojibake) on dashboard and list.
   - Phone: Ask Morgan FAB overlaps the Add button.
   - Caption under Add 'Safely saves...directly to your collection' contradicts the demo block; reword for demo mode.
   - Tablet sidebar 'Ask Morgan' label low contrast.
   - Sign-in logo missing after reload at 389px.
   - Tablet card titles truncated.
   - Demo: single CORS errors on /api/news/feed, /api/dismissed_news, /api/collection/completion_stats?user_email=unknown@numista.ai. Demo must not call user endpoints and must NEVER use a placeholder email.
5. **New standard: 18px body text** (up from 16) across the P7 screens.
6. **Keep all prior passes intact** (demo guard + 'Create a free account to save', no add_coins POST in demo, no /assets 404, $ one line, Type-it-in full screen 56px Save, Qty 1 stays 1, 48px checkboxes, tablet Manual Entry full screen, no Firestore 403, sign-in single scrollbar, 6 PIN boxes, V8.5/V8.6 validators/controllers/Quantity).

Gates: GEMINI38_REVIEW_P7_V8_7_BUILD.md, analyze 0, full flutter test, push dev only, baton -> GROKCOS_OVER, NET. **3 AM stand-down: if not done, file WAIT-OUT by 2:45 AM ET and stop.**

Baton now **AGCOS_OVER**.

**Grok CoS, OVER.**