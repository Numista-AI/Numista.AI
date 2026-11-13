# FT GATE: P7 V8.10 (v4.403, commit 747f7051)
Preview: https://numista-vault--p7-v810-gate-1w44jzb8.web.app
Account: grokbot@numista.ai (Grok Bot (Testing)) | Run: 17 Oct 2026, 10:35-10:52 AM ET | Tester: Field Tester

## BLUF: FAIL (2 blockers)
Most of the V8.9 failures are fixed. Two blockers are left: Ask Morgan still reports 311 coins while everywhere else shows 312, and the PDF report never generates (server timeout). The CSV export also leaves out Qty, Retailer, Invoice and Notes.

## Results
| # | Check (V8.9 FAIL re-check) | Result | Evidence |
|---|---|---|---|
| 1 | First letter kept in Retailer, Invoice, Notes | PASS | Typed once: "TestShop", "INV-001", "FT test" |
| 2 | Coin view shows Notes and Qty | PASS | Notes "FT test", Qty 3, Retailer "TestShop", Invoice "INV-001" |
| 3 | Checklist progress counts only coins added | PASS | 2026 America250 Circulating: 3/39 to 5/39 for 2 coins |
| 4 | Denomination and Series red text clears | PASS | Cleared on typing. Plain wording, e.g. "Please enter the denomination, like Quarter Dollar." |
| 5 | Login icons | PASS | Real emoji bullets and the backspace key render in Incognito |
| 6 | Ask Morgan count matches header | FAIL | Greeting "311 coins (est. $127.50)", panel header "312 coins", Dashboard 312 / $2,224.36 |
| 7 | Console errors | IMPROVED, not clean | 3 errors down to 2, both news/feed CORS + ERR_FAILED. The Firestore permission-denied errors are gone |
| 8 | Confirm card lists the coins | PASS | "Save 2 coin(s) from \"2026 America250 - Circulating Currency\" to your collection: • 2026 1776 ~ 2026 Jefferson Nickel (P-UNC) • ... (D-UNC)" |
| 9 | Qty 3 counts as 3 | PASS | 312 to 315 |
| 10 | £ sign, app and CSV | PASS | $ only, no £ or garbling |
| 11 | £ sign, PDF | NOT VERIFIED / FAIL | "Generate AI Report Now" gave "The Numista.AI server didn't answer. Try again in a moment." on 3 tries across 2 runs |
| 12 | CSV content | FAIL (new) | Settings & Backup > Download Companion CSV: no Qty, Retailer, Invoice or Notes columns. Added = raw "Timestamp(seconds=...)". A Year shows "2017.0". Cost mixes "0" and "$0.00" |

## Notes
- Denomination "Quarter" was saved as "Quarter Dollar" (normalized; fine).
- My Collection has no CSV export button. It's only under Settings & Backup.
- In the first run, Cost "10" landed in Qty once. The rerun with one input at a time was clean, so this is likely tester input, not an app bug.
- Counts: start 312, end 312. All 3 test coins deleted. Morgan qty 2 coin untouched. No PIN typed, no Undo All.
- The 311 vs 312 drift from V8.9 persists only in the Morgan greeting, which points to a stale or separate count source for Morgan.

## Asks for Antigravity
1. Point the Ask Morgan greeting count and value at the same source as the header and Dashboard.
2. Fix the PDF report Cloud Run call (times out), then re-check the £ sign in the PDF.
3. CSV: add Qty, Retailer, Invoice and Notes. Format Added as a date, Year as an integer, and Cost consistently.
4. Add the preview origin to news/feed CORS (or suppress the call on previews).
