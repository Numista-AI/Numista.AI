# UX GATE P7 V8.6 (NET-227) - FAIL (3 of 6 still failing)
**Tester:** UX Designer | **Filed by:** Grok CoS, 2026-10-15 ~19:35 ET
**Preview:** p7-v86-gate (origin/dev f6cfedbd, incl. 68c62f3d)
**Method:** signed-out demo only, 389px phone + 1025px tablet. Nothing saved, no sign-in.
Screenshots: UX Designer box /workspace/numista-ux/p7v86/

## FAIL
1. **Phone checklist (389px).** Checkboxes now PASS (48x48, 76px rows). Still failing: Download PDF starts x=322 and overflows (only 'D' visible); Back/Print/PDF 32px tall; coin names truncated ('1878 8 Tail F...', '2021-CC Pri...'); mint column clipped ('Philadelph'); program title missing; helper text ~12-13px.
2. **Cards (389 + 1025).** 'View Checklist' (40px) and 'Advances overall record' caption render below card and overlap next heading (389: card ends y610, button y651; 1025: card ends y522, button y568).
3. **Numeric keypad.** Year, Cost, Qty still type=text, no inputmode, both entry paths. Third gate in a row.

## PASS
4. Tablet More ways > Manual Entry opens full screen (Save 56px).
5. No Firestore 403. NEW: one CORS error each on /api/news/feed, /api/dismissed_news, /api/collection/completion_stats?user_email=unknown@numista.ai.
6. Phone sign-in single scrollbar, Sign In not clipped, 6 PIN boxes visible.

Prior passes hold: demo add blocked with 'Create a free account to save' + no add_coins POST; no /assets 404; $ value one line; 'Type it in' full screen, 56px Save, Qty 1 stays 1. Mint-releases CORS spam gone (0).

## New bugs
- Pound sign renders 'Â£2' (mojibake) on dashboard and list.
- Phone: Ask Morgan FAB covers end of Add button.
- Caption under Add 'Safely saves...directly to your collection' contradicts demo block.
- Tablet sidebar 'Ask Morgan' label white on pale bg, low contrast.
- Sign-in logo missing after reload at 389px.
- Tablet card titles truncated.

## Standards
Eric's UX rule is now 18px body text (labels currently ~16px = old bar).

## Not covered
Confirm card / Cancel-sends-nothing (signed-in) is Field Tester's item.

**Result: FAIL. V8.7 orders -> NET-228.**