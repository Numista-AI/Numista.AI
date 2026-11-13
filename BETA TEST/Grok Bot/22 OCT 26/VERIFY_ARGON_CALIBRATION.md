# VERIFY_ARGON_CALIBRATION — Gemini 4 Argon read-only review (22 OCT 26)
Verifier: Grok CoS. READ-ONLY. Compared against origin/main 3c1bacf5 (live) and 1058fe8b (V8.18.15d, branch p7-v8.9).

## Which version Argon reviewed
The **dev checkout at 6176a606** (laptop MyVertexProject working tree). Its line numbers match dev exactly (`if inv_no:` at L3524; snackbars L57/L119; badge L1250). dev does NOT contain 1058fe8b, so Argon reviewed **pre-fix code**, the same logic as live main (main has it at L3468). All quotes are real and word-for-word in that file; none were invented.

## Verdicts
| # | Finding | main (live) | 15d (1058fe8b) | Label |
|---|---|---|---|---|
| 1 | Y/M/Denom fallback batch.delete | L3478-3494 `if is_dupe:` / `batch.delete(queue_ref.document(doc_id))` | L3579-3607: sets `is_possible_dupe`, flags `possible_duplicate`, commits | REAL-on-main, FIXED-in-15d |
| 2 | `if inv_no:` not `if inv_no and item_no:` | L3468 `if inv_no:` + `.where('Retailer Item No.',  '==', item_no)` with item_no='' | L3564 `if inv_no and item_no:` (+ L3574 excludes current batch ids) | REAL-on-main, FIXED-in-15d |
| 3 | UI ignores committed/skipped | L56, L118, L1065 all hard-coded | Bulk + 100% flows now use `snackbarFromCommitResponse` (L113, L179). Single Save & Commit L1133 still `const SnackBar(content: Text('Coin saved and committed to collection!'))` | REAL-on-main, REAL-on-15d (1 of 3 remains) |
| 4 | Badge >=0.999 incl. quarantined vs commit >=0.95 | L1249 `return conf >= 0.999;` vs L88 `return conf >= 0.95;` | L1317 vs L151, unchanged; badge also reads only `confidence_score`, commit falls back to `composite_confidence` | REAL-on-main, REAL-on-15d (count/label mismatch, not data loss) |
| 5 | Edit dialog `if (ctrl.text.isNotEmpty)` keeps stale value | L960, L1022 | L1028, L1090 unchanged | REAL-on-main, REAL-on-15d (in 15d a stale Invoice#+Item# can still cause a definite-dupe drop; stale Mint only flags) |

## Argon accuracy score
- Quotes: 5/5 real, verbatim. Line numbers: exact for the file it read (dev).
- Findings: 5/5 real against the code it read. 0 false. 0 invented.
- Gap: it didn't know that file was pre-fix. That's our scoping error: the calibration prompt didn't pin 1058fe8b.
- Severity: #1/#2 are the data-loss bugs (fixed in 15d). #3-#5 are real but smaller.
- **Score: 9/10, high accuracy.** Recommend Argon for hard read-only reviews. Next time pin the commit/worktree in the prompt.

## Hotfix note
The live hotfix MUST carry both 15d changes in commit_reviews: no attribute-only delete (#1) **and** `if inv_no and item_no:` (#2). Fixing #1 alone still drops every coin after the first on an invoice with no item numbers.
