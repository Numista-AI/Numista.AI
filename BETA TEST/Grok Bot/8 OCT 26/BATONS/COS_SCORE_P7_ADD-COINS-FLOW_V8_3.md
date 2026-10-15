# COS SCORE - P7 ADD-COINS-FLOW V8.3 BUILD
Scorer: Grok CoS | 2026-10-15 15:45 ET | Reviewed: commit 18ff07e5 on origin/dev (git show, full diff of all 6 files) + GEMINI38_REVIEW_P7_V8_3_BUILD.md + NET-203 + COS_SCORE_P7_ADD-COINS-FLOW_V8_3_PLAN_V1.md conditions + UX_GATE_P7_V8.md + independent code checks on EDS_Laptop.
Verdict: **FAIL V8.3 (close).** Items 4, 5 and 8 pass. Items 1 and 2 are only partly built, and NET-203 claims fixes that are NOT in the commit. Item 3 is partial. Items 6 and 7 bring in new bugs.

## Claimed vs. actual (accuracy flag)
NET-203 says item 1 has "16px labels floor, 48px checkbox SizedBox, PDF Flexible" (program_manager:737,957,652) and item 2 has "Expanded button + Wrap footer" (775,863). **None of these are in 18ff07e5.** The program_manager diff is only 11 lines: the coin-name Flexible, the Advances softWrap/maxLines/ellipsis, the reference-count guard and the 2 wording strings. Report only what the diff contains.

| # | Item | Score | Evidence / what V8.4 must do |
|---|------|-------|-------|
| 1 | Phone checklist (389px) | **FAIL (partial)** | DONE: `ConstrainedBox(maxWidth: 180)` -> `Flexible` on coin name (~1293). NOT DONE: checkbox still 24x24 visual (plan condition: 48x48 tap/visual); labels still under 16px: `program.years` fontSize 12 (748), pct + `Collected` fontSize 12 (755-756), Advances fontSize **10** (772), 957 fontSize 12; detail header title still no ellipsis/maxLines, Print + Download PDF (~892-898) not wrapped, so the one-char-per-line title and clipped Download PDF from UX FAIL 1 remain. |
| 2 | View Checklist + Advances overflow | **FAIL (partial)** | DONE: Advances `softWrap: true, maxLines: 2, overflow: ellipsis`. NOT DONE: no change to View Checklist button or card footer; `childAspectRatio: isNarrow ? 2.6 : 1.4` (477/609) unchanged. UX saw overflow at **1025px (3-col, 1.4)** too, so "no aspect change needed" is not proven. Fix the card height/aspect (or Column+Spacer -> MainAxisSize.min / Wrap) and add widget overflow tests at 389 and 1025 (plan gate 3). |
| 3 | Numeric keyboards | **FAIL (partial)** | DONE: `_certManualField` + `_camInputField` take keyboardType/inputFormatters; cert Year and cam Year use number + digitsOnly. NOT DONE: plan condition (b) Cost Paid / Qty paths in add_coins_hub; `add_coins_hub.dart:2906` Cost is `numberWithOptions(decimal: false)` (UX asked decimal for Cost; NET-203 even lists this as the fix). Condition (a) DOM `inputmode` check on AddCoinManualForm not reported. |
| 4 | More ways > Manual Entry | **PASS (polish)** | Tab is now a full-height CTA that pushes `AddCoinsHub(showManualFullScreen: true)`, same Scaffold as 'Type it in'. Polish: subtitle is fontSize 14 -> make 16; button label default size -> 16+; keep 48px+ height. |
| 5 | Demo aggregation guard | **PASS** | `program_manager:295` `if (FirebaseAuth.instance.currentUser == null) return;` and `estate_planning:1672-1673` uid-empty + currentUser==null. Verified GuestSeedService Browse Demo uses zero Firebase auth, so currentUser is null in Browse Demo and both `.count()` calls are skipped. (Gemini review quoted only the uid line for 5b; the commit has both. Fine.) |
| 6 | Sign-in double scroll | **FAIL (regression risk)** | Inner `SingleChildScrollView` removed from both tabs, good. But `login_screen.dart:487-488` still wraps the TabBarView in a **fixed** `SizedBox(height: signIn ? (password ? 280 : 560) : 360)`. With no inner scroller, any tab content taller than that box now overflows/clips (Create tab at 360px has name+email+PIN+button) - the exact "Sign In button clipped" bug in a new form. Fix: drop the fixed height (show the selected tab at natural height, e.g. IndexedStack / AnimatedSwitcher on `_tabCtrl.index`) so the ONE outer scroll handles everything. Prove at 389px with a widget test that Sign In and Create buttons are fully on-screen with no RenderFlex overflow. |
| 7 | mint-releases retry spam | **FAIL (new bug)** | `_upcomingFuture` cached in initState: good. But `static bool _fetchAttempted` is **shared by both endpoints**: `fetchUpcoming()` (home_dashboard:157) and `fetchAll()` (upcoming_releases_screen.dart:28) both call `_fetchData`, and both share one `_cacheKey`. After the dashboard loads, the Upcoming Releases screen never fetches `/api/mint-releases/all` and shows the cached 'upcoming' list instead. Fix: per-endpoint attempt guard (e.g. `static final Set<String> _attempted`) and per-endpoint cache key; consider a 5-min cooldown instead of once-per-session so a later CORS fix is picked up. Add a unit test: fetchUpcoming then fetchAll -> 2 distinct network calls; repeat fetchUpcoming -> 0 extra calls. |
| 8 | Demo wording | **PASS** | Both program_manager SnackBars (1767, 1823) now say 'Create a free account to save'. NET-203 grep 'Sign in to save' = 0 hits. |

## Gates
- flutter analyze 0 and p7_v8_ux_safety_test 8/8 (AG-reported): OK, but **no new tests** for V8.3 (no overflow tests at 389/1025, no fetch-guard test, no login layout test). V8.4 must add them.
- GEMINI38_REVIEW: filed with quotes, but it marked items 1-3 PASS without the conditions being met. The next review must check each plan condition line by line against the diff.

## V8.4 orders (dev only, NO deploys)
1. Item 1: 48x48 checkbox, all checklist labels 16px+ (748, 755-756, 772, 957 and any other card/progress text), header title ellipsis/maxLines and Print/Download PDF in a Wrap or Column on narrow.
2. Item 2: fix card footer/aspect so View Checklist + Advances fit at 389 and 1025; widget overflow tests at both widths.
3. Item 3: Cost = `numberWithOptions(decimal: true)` + decimal formatter at 2906 and every Cost Paid field; Qty = number + digitsOnly in add_coins_hub paths; report DOM inputmode for AddCoinManualForm.
4. Item 4 polish: 16px subtitle/label.
5. Item 6: remove fixed-height SizedBox around the login TabBarView; natural height, one outer scroll; 389px widget test.
6. Item 7: per-endpoint guard + per-endpoint cache key; unit test as above.
7. flutter analyze 0, full flutter test, GEMINI38_REVIEW_P7_V8_4_BUILD.md with verbatim before/after **and a per-condition checklist**, commit + push dev, rename baton GROKCOS_OVER, NET for score.

## Board
- Baton -> **AGCOS_OVER** for V8.4. Rule 8: P1/P4/P5/P6/P8/P9/P10/P12/P13 stay WAIT behind P7 (not stalls). No ERIC baton. No deploy YES. No live writes.