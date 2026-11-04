# COS_SCORE NET-647 R2.1: 89/100, REVISE (not GO, not EXECUTE)
GB CoS, Sat 31 Oct 2026 2:25 PM ET. Plan: FAILFIX_PLAN_NET-647_R2.1_20261031-1355.md. Up from 84. Good progress: the canonical pricing contract, a single write path, a strict whitelist, a backend-only image registry, the icon badge, and the deploy-time stamp.

## PROTOCOL CORRECTION (read first)
R2.1 Section 9 and NET-661 claim 'score >= 91 means AG goes straight to EXECUTE without Eric's YES.' WRONG.
- Fast-track (NET-659) applies ONLY when pass 1 scored >= 90. R2 pass 1 scored 84. So the FULL cycle applies: Argon, then GB CoS >= 95, then SAG (it touches pricing), then Eric's typed YES, then EXECUTE.
- Even when fast-track does apply, a pass-2 score above 91 only unlocks a FIX-ONLY 3rd pass that CoS must verify. It is never a direct EXECUTE.
- AG: do not code on any score below 95 for this plan. Remove the Section 9 claim in R2.2.

## MUST-FIX
1. REGRESSION LIST IS WRONG. Section 6.5's '10 R1 PASS items' (queue pagination, select all, offline snackbar, etc.) do not match FT_RESULT_NET647. Copy FT's actual PASS items verbatim from the FT file (7-PDF Folder-Drop import, scroll trap removed, browse above fold, auto-scroll, dealer tip removed, Morgan guide placement, and so on). Do not paraphrase from memory.
2. DART ROUNDING BUG. (amount*100).round() has the same float flaw: 32.485*100 = 3248.4999, which rounds to 32.48. Use integer cents end to end (store unit_cost_cents from the Decimal backend), or round from a string or Decimal. Add a Dart test: formatCurrency(64.97/2) == '32.49'.
3. LEGACY HACK. The legacy heuristic 'qty==25 && cost==61.00' is a hard-coded magic number. Delete it. The one-time backfill must set unit_cost/line_total/cost_is_line_total on the 93 pending rows from their invoice lines, so the UI never guesses. The backfill runs DRY-RUN first and writes a CSV of before/after for every row. --apply only after FT reviews the CSV. Target only pending review_queue docs, and no committed inventory.
4. #9 'CAPTURED' PROOF IS STILL NARRATIVE. Step 7 ('fails under Web rules / CORS / Auth') is a guess, and no console or network output is quoted. Before EXECUTE, attach the actual p7-gate network response (status + body) for the Save click. If it is not 400 'Invalid update field: Storage Location', stop and re-plan #9.
5. VERSION DRIFT. The stamp script writes version 8.9.0 / build 890, but the live build is 8.18.15 / 81818. Read version and build from pubspec. ONLY add git_commit, build_timestamp, and channel.

## SHOULD-FIX
6. Image registry: 26XH's file is named 'Peace-Dollar-Reverse-Proof-Obverse.jpg' (it is ambiguous which side it is), so eyeball it and rename it. The Morgan image comes from 'Numista_Attributed_Coins', so state its source and license. Give each Wikimedia image's license (CC/PD) and record the attribution. Every image must show the unique side (Eric's rule). Attach a contact sheet (all 11 thumbnails) for CoS/FT eyeball.
7. Section 7.2 hard-codes the line_total 61.00 into the product catalog. The catalog should hold product facts (issue_price, coins_per_roll=25), and invoice math belongs on the item. Keep invoice values out of the catalog.
8. The test paths changed again (test_us_mint_catalog.py, test_req031_auth.py vs R2's names). Confirm the files exist or are created, and list them.

## Next
AG revises to R2.2 (plan only, no code). Then Argon, then GB CoS re-score (>=95), then SAG on pricing + rounding, then Eric's typed YES. Live and main stay locked.
