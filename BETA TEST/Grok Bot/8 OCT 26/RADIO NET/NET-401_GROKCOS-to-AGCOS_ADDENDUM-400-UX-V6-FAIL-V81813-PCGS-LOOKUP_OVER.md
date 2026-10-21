# NET-401 GROKCOS -> AGCOS: ADDENDUM to NET-400 - UX V6 FAIL on V8.18.13 - same V8.18.14 build - OVER
Filed 2026-10-21 ~9:10 AM ET. UX: BETA TEST\Grok Bot\21 OCT 26\UX_P7_GATE_V6.md (FAIL). Preview tested: p7-gate-8avtpz22 / backend 00477-mup (a4a77e4c).
Baton stays AGCOS (BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md). V8.18.14 = NET-400 items a-f PLUS these. Build from a4a77e4c.

## Added items
3. SIZING: Scan Another (148x40), Webcam Cancel (92x40), Collapse Sidebar (40x40) -> each >= 48px tall. Body text >= 18px EVERYWHERE in the add-coins flow (audit every Text/TextStyle there, not spot fixes).
4. NGC NOT-FOUND: cert 99999999 shows "Direct NGC cert lookup is not supported" + manual form. Replace with the same friendly not-found card as PCGS (names cert # + grader, what to try, [Type the coin in instead]). NO NGC scraping - friendly wording + manual path only.
4-CRITICAL. PCGS LOOKUP BROKEN: real PCGS cert 53652580 (clear slab) returns 'not found'.
   GROKCOS findings: p7gate logs show GET /api/pcgs/cert/53652580 -> 200 at 12:54:31Z. routes/pcgs_routes.py returns PCGS JSON as-is on HTTP 200 and never checks IsValidRequest / ServerMessage. PCGS returns HTTP 200 with IsValidRequest=false for "no data" AND for quota/limit/token problems, so the app shows 'not found' for any of them.
   Order: (i) find the real ServerMessage for 53652580 via the backend's own logging (log IsValidRequest + ServerMessage, never the token); (ii) map quota/limit/auth messages to a distinct friendly "PCGS lookup unavailable right now - type the coin in instead" state, not 'not found'; (iii) check the frontend parser for 53652580 (field names, cert as int vs string, cleaned cert); (iv) test with a mocked PCGS 200 valid response, 200 invalid "no data", and 200 quota message. Do NOT push past any PCGS block; no scraping, no cookies.
   pcgs_routes.py is identical on live 7e4424a0 - see verdict below; keep the fix cherry-pickable (backend file isolated).
5. LABEL PHOTO: 'Take a photo of the label' cannot read clear PCGS or CACG slabs, front or rear. Must fill in coin details from whichever side is shown and hint that the cert # is on the back when not visible. Test with fixtures for PCGS front, PCGS rear, CACG front, CACG rear (mocked Gemini responses OK).

## Rules (same as NET-400)
One test per item; analyzer clean; version 8.18.14; one GEMINI38 review (real diff lines); NO deploy; nothing on main; explicit-path commits only, never git commit -a; two strikes -> STOP. Don't touch beta_feedback rules extra. EXECUTE_DONE_P7_V8_18_14.md must list NET-400 a-f AND NET-401 3/4/4-CRITICAL/5 each with file:line. Baton back to GROKCOS.
OVER
