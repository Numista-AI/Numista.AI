# FT Gate: P7 V8 (preview p7-v8-gate, dev 371989db, NET-194), 15 Oct 2026, grokbot@numista.ai only

**Bottom line:** FAIL. The manual form saved a coin with Year left blank and showed no error, and it drops characters as you type. The checklist add is BLOCKED-BY-CORS. Several items weren't reached and need a second pass. Total Coins was 311 at the start and 311 at the end; the junk coin was deleted. No writes to Eric's collections.

| # | Item | Result | Notes |
|---|---|---|---|
| 1 | Checklist, Add Selected Coins | BLOCKED-BY-CORS | In Network, add_coins shows a CORS error and the preflight returns 400. The app shows a generic "connection error" snackbar (exact wording not captured). Whether the confirm card appears first and the Cancel-sends-nothing check were NOT verified. |
| 2 | Demo-mode guard | NOT RUN | |
| 3 | Phone layout, $ wrap, PIN clip | NOT RUN | |
| 4 | Manual entry full screen | PARTIAL | Full screen on desktop. FAIL on input: fields often drop the first typed character, and Year went blank after entry. The save and +1 check couldn't be done. |
| 5 | Plain errors | FAIL | Year left blank gave no validation error; the form saved a junk coin (311 to 312). Deleted, back to 311. |
| 6 | Console | PARTIAL | 205 errors, 2 warnings, 102 issues. Firestore errors and CORS on add_coins seen. The /assets/assets 404s and the runAggregationQuery 403 weren't confirmed or cleared. |

## Fix list
1. Require Year (and the other key fields) with a plain-English message before saving.
2. Fix the form dropping typed characters and Year blanking.
3. CORS on the backend for the preview origin (needs Eric's YES), so the preflight stops returning 400.
4. Second FT pass for items 1 (confirm card and Cancel), 2, 3 and 6.
