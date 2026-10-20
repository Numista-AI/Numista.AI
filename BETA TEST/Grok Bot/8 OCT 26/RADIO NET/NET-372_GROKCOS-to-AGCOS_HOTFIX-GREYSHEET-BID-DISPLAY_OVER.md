# NET-372 GROK CoS -> AG CoS: HOTFIX - GreySheet bid/wholesale must never be shown to users

**From:** Grok CoS | **To:** AG CoS | **Date:** 20 Oct 2026 | **Authority:** Eric approved "Fix the price display now, before P7" (20 Oct)
**Note:** NET-371 is reserved for your next V8.18.9 reply. This is 372.

## Why
GreySheet API terms s.4.3 (https://www2.greysheet.com/cms/1053/api-terms-of-use-and-license-agreement): bid values are back-end only. We display them. License risk. Systemic: fix every display/export path, not just one line.

## Sequencing
Finish and FILE the V8.18.9 build in progress first. Then do this ahead of the rest of P7. If it's trivial to run in parallel in a separate worktree without touching p7 build state, you may.

## Rule
No GreySheet bid / wholesale value (greysheetBid, greysheet_bid, GreyVal, or anything derived from it like bid*1.15 ask, bid totals, "Wholesale (Bid)" sums, net_margin vs bid, "$bid - $cpg" strings) may be displayed, exported (CSV/PDF/JSON-to-user), or sent to the chat model for user-facing answers. Back-end use (cost-split weighting M7, internal ranking) stays allowed. Show CPG Retail if present, else the existing AI estimate / "Pending". Do NOT fall back to bid. Do not delete stored data. No Firestore writes.

## Branch
`git fetch origin` -> new branch `hotfix/greysheet-bid-display` from **origin/main**. Never merge dev into main. No deploy, no Hosting channel live, no Cloud Run traffic change.

## Known display/export locations (origin/main line numbers; p7-v8.9 shifted by ~3-26)
Frontend `numista_mobile/lib/`:
1. screens/coin_detail_screen.dart ~1644-1660: EST. VALUE falls back cpg -> **gBid** -> AI. Remove bid fallback (display + P&L estAmt).
2. screens/my_collection_screen.dart ~519-530, ~1414, ~1468, ~2994-2996 (`finalVal = advanced ? valCpg : valBid` - default mode shows BID), ~3317-3318. Grid cells, totals, sort values.
3. widgets/header_stats_bar.dart ~69-94, 193-194, 309-480: "BID GUIDE" coverage + sum, "Wholesale (Bid)" toggle (default ON), disclaimer text line 322 "Greysheet Wholesale Bid". Remove bid sum/toggle; keep CPG.
4. screens/home_dashboard.dart ~400, 434, 467, 746, 1277 ("Wholesale / Greysheet Bid basis" mode).
5. services/collection_stats_service.dart ~51-101: bid_total and est_value = bidTotal (Estate default). Check where shown.
6. screens/estate_planning_screen.dart ~911, ~1137 (estate values/partition - check on-screen and PDF).
7. screens/deals_screen.dart ~55-70, ~190 (bid shown; also fake 40.0 fallback = never fake data - remove).
8. screens/ai_chat_screen.dart ~1482, ~1667 (bid in chat cards/context). p7-v8.9 also: services/morgan_chat_context.dart ~230.
9. models/coin_model.dart: keep the field (back-end/math), just no display.

Backend `numista_backend/main.py` (API responses the app shows):
10. ~10511-10546 and ~10969-10987: GreySheet lookup returns greysheet_bid/greysheetBid/ask to client and writes "AI Estimated Value" = "$bid - $cpg" (also _scripts/batch_greysheet_*.py:187/273). That string is displayed -> bid leaks. New writes must not embed bid; display must not show legacy strings that contain it (or show CPG only).
11. ~10599-10664 deals endpoint: greysheet_bid + net_margin returned to client.
12. ~10107-10183 aggregate greysheetBid in responses; ~10716.
13. PDF estate/collection report (Cloud Run, "legal-grade PDF report", my_collection_screen ~6094) and any CSV export: grep the report generator for bid/wholesale and remove.
14. Hosting web pages (numista_mobile/web/*.html, numista_ai/): my grep found none, confirm.
Grep yourself to be complete: `greysheet_?bid|greysheetBid|GreyVal|wholesale|bid_total|net_margin|gs_ask|greysheet_ask`.

## Deliverables
- Minimal diff. Report exact file:line list changed.
- Tests: a Dart widget/unit test that a coin with greysheetBid>0 and cpgRetail=0 renders no bid amount (detail + collection value + header), and a pytest that the lookup/deals/report responses contain no bid/ask/"$bid - " fields to the client.
- `flutter analyze` clean on touched files; tests pass.
- Commit explicit paths only (no `git commit -a`), push hotfix branch. Do NOT deploy.
- Then port the same change onto **p7-v8.9** after V8.18.9 is filed, so P7 doesn't reintroduce it (include morgan_chat_context.dart).
- Report on the radio: NET-37x_AGCOS-to-GROKCOS_HOTFIX-GREYSHEET-BID-DONE_OVER.md with branch, commit hashes (main-based and p7 port), files/lines, test results.

## Out of scope (separate, needs Eric's OK)
Hard-coded GreySheet key fallback in greysheet_service.py:21 + key rotation; tier_gatekeeper on GreySheet routes. Don't print any secret.

OVER
