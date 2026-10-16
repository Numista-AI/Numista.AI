# FT Smoke: PR #258 Unified Bundle (live v4.403), 13 Oct 2026, grokbot@numista.ai only

**Bottom line:** CONDITIONAL. Auth/IDOR hardening and the 3-choice Add Coin pass, and Morgan does wait for Confirm before writing. But there is no single Undo after a save (only Undo All), the console shows a CORS error on /api/spot_prices, and two items weren't fully verified. No changes to Eric's collections. The test coin was deleted and the count is back to 313.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | PIN login, focus, readable text | PARTIAL | 01_login_screen: 6-digit PIN boxes and keypad work. The text looks small. Auto-focus after typing the email could not be confirmed. |
| 2 | Collection, cards and checklists load with no 401s | PASS | 21, 22, 07, 08, 10. The first pass showed "Could not load your collection" once (06) and a Review Hub spinner (09). Both were fine on 3 re-check cycles (23: Review Hub "All Caught Up"). No 401s in the console. |
| 3a | Add Coin shows 3 choices | PASS | 16 (Take a photo / Type it in / Upload a list). The older 6-choice modal (13) is still reachable. |
| 3b | Morgan confirm-before-write | PASS | 1964-D 1 Cent proposal. The count stayed at 313 before Save, then went to 314 after Save. |
| 3c | Undo | FAIL | After the save, only Undo All and View Binder were offered. There was no single Undo. I deleted the coin manually to clean up. |
| 4 | Admin with no token or a garbage token | PASS | /api/admin, /users, /stats, /health returned 401. /api/identify_group_photo returned 401 (it was 422 on 12 Oct). /admin returned 404. |
| 5 | Public pages signed out | PARTIAL | /terms and /privacy render (02, 03). / returns 200, but the signed-out home screenshot (04) was blank white. Needs recheck. |
| 6 | No console errors | FAIL | CORS blocked: https://numista-backend-568985927038.us-central1.run.app/api/spot_prices (no Access-Control-Allow-Origin). Also repeated main.dart.js:4427 and Firestore onSnapshot __PRIVATE__fail errors (24). |
| - | Review Hub invoice-scan path | NOT RUN | Carry this to the next run. |

Other notes: The sidebar shows two nav variants, the new 6-item nav (15) and the old long list (09). Counts: 313 at the start, 314 after the save, 313 at the end. The Morgan qty 2 coin was untouched.
