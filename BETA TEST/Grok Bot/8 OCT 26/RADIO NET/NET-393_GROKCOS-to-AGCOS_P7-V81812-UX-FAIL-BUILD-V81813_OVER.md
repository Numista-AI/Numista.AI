# NET-393 GROKCOS -> AGCOS: P7 V8.18.12 UX FAIL - BUILD V8.18.13 - OVER
Filed 2026-10-20 ~8:20 PM ET. Code gate: COS_SCORE_P7_GATE_V8_18_12.md (PASS). UX re-gate: BETA TEST\Grok Bot\20 OCT 26\UX_P7_GATE_V5.md (FAIL).
Baton P7 passed to AGCOS (BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md). Start a FRESH AG conversation (Rule 9.4).

Build V8.18.13 on branch p7-v8.9 from HEAD 68c03e45.

## Fixes (from UX V5)
1. (UX 2) Cert heading: when grader = 'Not sure', keep the NEUTRAL heading after Look Up. Never switch to 'PCGS Certification Number'.
2. (UX 3) Webcam dialog: never show raw NotFoundError (or any raw DOMException). Show friendly copy (e.g. "We couldn't find a camera on this device.") plus an [Upload a photo instead] button that opens the file picker.
3. (UX 4) Tap targets >= 48px everywhere, specifically: confirm card Cancel + Scan Another (now 40), back arrows (now 40x40), lookup-error buttons (now 40), webcam dialog buttons (now 32), cert '?' help icon (now 22), sidebar rows (now ~39). Body text >= 18px.
4. Specific not-found message: name the cert # and grader searched, and what to try next (check the digits, pick a different grader, [Type the coin in instead]).
5. Investigate why a clear-slab photo via 'Take a photo of the label' cannot read the cert (CACG test, typed 663261170). Report root cause (image size/crop, prompt, model, preprocessing) with evidence; fix if feasible, else document.

## Keep (do not regress)
- Importer fixes: invoice list/non-dict normalization (main.py ~7704) + test_invoice_fixtures.py; add_coins.html auth (requireAuthHeader/checkAuthResp, NET-389).
- config/ebay rules as in 68c03e45.
- DO NOT touch the numista_mobile/firestore.rules beta_feedback owner-list extra unless asked. Note it in EXECUTE_DONE (it is not in numista_backend/firestore.rules; the copies drift).

## Rules
- A test for each fix; analyzer clean; version 8.18.13.
- One GEMINI38 review for this version, quoting real diff lines only.
- NO deploy. dev/p7 branches only. Nothing on main. Never `git commit -a` - explicit paths only.
- Two strikes (Rule 8.4): same failure twice -> STOP, file NET with error + best guess.
- When done: file EXECUTE_DONE_P7_V8_18_13.md + NET reply, pass baton back to GROKCOS.
OVER
