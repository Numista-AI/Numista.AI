# NET-417 GROKCOS -> AGCOS: Mobile phone audit #3 (emulator 360dp portrait, grokbot account) - OVER
Filed 2026-10-21 ~1:25 PM ET. Baton stays AGCOS. Source: Mobile agent audit #3 (emulator, 360dp portrait, grokbot test account, browse only).
NUMBERING: NET-416 stays reserved for your V8.18.15 done report. Reply to THIS order = next free NET after 416.

## DO NOT DISTURB V8.18.15
The V8.18.15 build in progress continues as scoped (NET-411/413). QUEUE everything below for V8.18.16, unless an item is truly trivial and fits V8.18.15 with no risk. List any you pulled forward in NET-416.

## HARD RULE (NET-410)
ALL layout fixes are NATIVE-APP ONLY, gated by `!kIsWeb && (Platform.isAndroid || Platform.isIOS)`. numista.ai must look IDENTICAL in every browser, mobile browsers included.

## A. APP-ONLY items
1. BLOCKER - Settings: AI Memory card title row overflows 346px; Target Grades text squeezed to 1 char wide; rest of Settings incl. the account section unreachable.
2. Collection: All/Coins filter row overflows 300px. Feedback FAB + Morgan bubble + '+' button stack over the Other Items card. Tapping a Recent Additions row does not open coin detail (3 tries).
3. Name dialog overflows 103px with keyboard open, covering Skip; Skip does not close the dialog.
4. Beta welcome dialog: badge overflows; no close button.
5. Morgan welcome options: all ellipsis-truncated.
6. Feedback FAB covers a control on every screen, incl. the Add Coins camera tab.
7. Add Coins landscape: 157px bottom overflow, no scroll; desktop side panel takes ~30% width. 'More ways' offers Folder-Drop Bulk Import on phone and says 'click' -> on phone say 'tap' and hide folder-drop.
8. AI Chat renders raw markdown.

## B. SYSTEMIC DATA ISSUES (likely backend/shared - CHECK WEB TOO)
Treat as systemic per Eric's rule. INVESTIGATE AND REPORT ROOT CAUSE BEFORE FIXING. NO Firestore writes. NO writes to Eric's collections.
- Totals disagree on grokbot: Home breakdown $2,235.03 vs Collection $2,897.87 vs AI Chat header '311 coins · $127.50'.
- Green box says '0 awaiting AI valuation' while also showing '15 pending'.
- Checklist says 18 steps but shows 14/20.
- Coin cards show a generic gold icon, not the coin's unique-side image (Eric rule: unique side always).
- Malformed titles: '2006.0 Denomination Missing?', '2016.0 Quarter', 'Coin' (year float bug).
- Most values $0.00.
- App Check: 'No AppCheckProvider installed' in app logs.
- Related known leftovers: phantom Recent Additions 318 vs 311; Unknown cent/nickel bug.

## Evidence
Screenshots on EDS_Laptop: C:\Users\ericd\emu_shots\ . Some show the test email - DO NOT copy into docs.

Rules unchanged (NET-400..413): one test per item, analyzer clean, one GEMINI38 review (real diff lines), NO deploy, nothing on main, explicit-path commits only, never git commit -a, two strikes -> STOP. Report item by item with file:line, gate status and (for B) root cause. Baton back to GROKCOS.
OVER
