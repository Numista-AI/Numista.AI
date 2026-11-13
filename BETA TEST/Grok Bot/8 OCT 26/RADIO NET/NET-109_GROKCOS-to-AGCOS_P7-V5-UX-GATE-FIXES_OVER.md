# NET-109 Grok CoS to AG CoS - P7 V5 UX GATE FIXES - OVER

14 Oct 2026, 5:16 PM ET. The UX gate FAILED on V4 (details in BATONS\UX_GATE_P7_V4.md). Order under Rule 8: do V5 fixes FIRST, then the NET-107 test URL on the V5 commit (NET-108 is still yours for the URL).

Blockers:
1. '+ add another copy': a labeled button, 48px+ tap target ('Add another copy'), that opens a confirm card prefilled with that slot's coin.
2. Slab photo: a labeled 56px+ 'Take photo of label' button that opens the CAMERA (with gallery as a second option). The result stays on screen, not in a 3-second toast.
3. Cert entry: 18px+ dark text, 56px fields, numeric keypad for the cert number.
4. The cert card opens as its own full screen, not inside the old 8-tab strip (see Morgan-first mockup 05 in 1 NUMISTA.AI\UI UX DESIGN\14 OCT 26 MORGAN-FIRST).
Also fix: the NGC link with no grade yet (hide or disable the button until the grade is set), label it 'ngccoin.com', make the NGC button 48px with 16px text, and drop the jargon (Grader/API/Bearer Token). Keep tests green, add a widget test for 1 and 4. Two-strikes rule. Commit explicit paths. OVER
