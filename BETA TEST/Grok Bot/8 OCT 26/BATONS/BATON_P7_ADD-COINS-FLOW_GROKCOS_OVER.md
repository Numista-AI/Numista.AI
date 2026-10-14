# BATON P7 ADD-COINS FLOW (TOP PRIORITY - ahead of P2 and P4)
Holder: AG CoS. Ref: NET-076.

## Beta evidence
- Notes: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\14 OCT 2026\14 OCT Beta test.docx`
- Screenshots: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\14 OCT 2026\SS 1.png`, `SS 2.png`, `SS 3.png`, `SS 4A.png`, `SS 4B.png`; test inputs folder `Coins I tried to add` (same folder). Don't copy any collection values into prompts or files.

## Problem (Eric 10:35 AM ET beta: could not add NGC or CAC slabs)
1. First 'Add to Collection' screen (SS1) has no cert option.
2. Sidebar heading 'ADD NEW COINS/NOTES/ETC.' is not clickable; it lists only Microscope Scanner + Review Hub (SS2).
3. 'Add New Coins' hides cert lookup under 'More ways to add' (SS3).
4. Cert lookup is PCGS-only: no NGC, no CAC.
5. Folder-Drop Bulk Import scroll area is tiny and nearly unusable (SS4A/4B).

## Fix (dev only)
- ONE 'Add by Cert #' option, top level on the first Add screen AND Add New Coins. Supports PCGS, NGC, CAC. Auto-detects the grader from the number format, or lets the user pick it. Always shows a confirm screen before saving.
- Real grader lookups/APIs only. Where a grader has no usable API/lookup, fall back to manual entry with the cert # and grader prefilled. NEVER fake or guess coin data. Document which lookup each grader uses.
- Sidebar heading links to the Add screen. Merge the two Add screens into one.
- Bulk import area: full page height, usable scrolling.
- SYSTEMIC: audit EVERY add path (manual, cert, scanner, Microscope, Review Hub, bulk folder-drop, CSV/JSON import, mobile) for the same gaps; list each path + status in EXECUTE_DONE.
- Tests: widget tests for the cert flow per grader + fallback, and for nav. Full flutter test + pytest.

## Review gate before any YES
1. Gemini build review. 2. UX Designer review (one Add screen, discoverability, mobile). 3. Field Tester (grokbot test account) walkthrough of every add path on dev, with screenshots. Then pass to GROKCOS for score -> Eric for deploy YES (cherry-pick onto a branch from main).

## Limits
Dev only. Cherry-pick only. No deploy without Eric's typed YES. NO writes to Eric's collection (he is adding coins today); test only with the grokbot test account. No keys in files (masked input only).
## Log
- 2026-10-14 10:55 ET GROKCOS: issued from Eric's 10:35 beta test. TOP PRIORITY. OVER.
