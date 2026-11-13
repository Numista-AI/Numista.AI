# COS SCORE - P7 ADD-COINS-FLOW V6
Scorer: Grok CoS | 2026-10-14 ~19:15 ET | Reviewed: ae2b87bd on dev (vs V5 caa3c93f) + GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V6_BUILD.md
Verdict: **FAIL V6 (very close) - ITERATE to V7 (small).** Top data-integrity bug is fixed. Two V5 fix-list items are only half done.

Tests re-run by Grok CoS on EDS_Laptop: `flutter test test/p7_v5_ux_fixes_test.dart test/cert_flow_test.dart` -> **13/13 passed**.

| # | Item | Score | Evidence |
|---|------|-------|----------|
| B1a | Add another copy = plain confirm card | **PASS** | program_manager_screen.dart:1328 now opens `AddCoinsHub(showAddAnotherConfirm: true)`. `_buildAddAnotherConfirmCard()` (add_coins_hub.dart:341-513) shows name 22px, Year/Mint 18px #334155, 56px Save, "Has a slab cert # instead" 16px as second choice. `_saveAddAnotherCoin()` (515-573) writes `'Condition': 'Ungraded'`, no grader, no certNo, no verify_link, one `.add()`. initState (139) skips the cert preset when showAddAnotherConfirm, and only sets `_grader` when a certNo is present (152-158). |
| B1b | Save refuses empty cert # | **FAIL** | Guard was added only to `_lookupCertUnified()` (2991-2999). `_saveManualCertEntry(grader, certNo)` (3269+) still has no empty check and still builds a verify link from `$certNo`. Reachable: `_lookupCertUnified` sets `certClean = raw.split('/').last.trim()` (3016), so input like `123/` gives an empty certNo on the NGC/CAC manual card. V5 fix list item 1 asked for the guard in the save. |
| B1c | Empty-cert message | **FAIL (UX)** | The guard also sets `_pcgsLookupError = 'Please enter a cert number.'` (2998). That makes the cert view render `_buildCertLookupFallback` (2867-2868), which says "Automatic lookup unavailable right now / PCGS blocks automated lookups from our servers" and the "Upload PCGS CSV below" tip. Wrong message for an empty box, and it points to a section V6 removed from this screen. |
| B3 | 18px+ dark text on full-screen cert view | **FAIL (partial)** | Fixed: lines 2656-2657, chips 16px, result card 18px, footer 18px, PCGS Advanced Options removed from this view (the remaining one at 3524 is in `_buildPcgsImportTab`, OK). Still on this view: `_buildCertLookupFallback` (3701-3780) at 11-13px (header 13, body 12, button 12, tip 11) and the grader badge on the manual card at 14px (3065). |
| B3 | Verify labels | **PASS** | 3121-3125: ngccoin.com / cacgrading.com / pcgs.com. |
| Tests | New widget tests | **PASS (weak)** | blocker1AddAnotherPlainConfirm checks title, name, no TabBar, Save button, but never checks that "NGC" is absent. blocker1EmptyCertRefused tests the lookup only, not the save. |

## V7 fix list (P7 only, Rule 8, keep it small)
1. Put the empty-cert guard inside `_saveManualCertEntry` too: trim certNo; if empty, show "Enter a cert # before saving", reset `_certManualSaving`, return with no write. Also refuse an empty `certClean` in `_lookupCertUnified`.
2. Empty-cert guard must NOT set `_pcgsLookupError`. Show only the SnackBar or a short inline line under the field ("Type the cert # from the slab label"), 18px, #334155 or darker.
3. `_buildCertLookupFallback`: all text 18px+ dark (button 16px+ OK), plain words, drop the "Upload PCGS CSV below" tip on this view. Grader badge (3065) 16px+.
4. Tests: in blocker1AddAnotherPlainConfirm add `expect(find.text('NGC'), findsNothing)` and that saving does not need a cert field; add a test that `_saveManualCertEntry` with blank cert writes nothing; add a test that empty Look Up does NOT show "Automatic lookup unavailable". Full flutter test + analyze green.
5. Gemini38 BUILD review with code quoted, then NET to Grok CoS.

## Next
Baton -> AGCOS OVER for V7. After V7 code PASS: Grok CoS handles the Firebase re-login with Eric and the p7 preview deploy (NET-115 build/deploy info noted: FLUTTER_ENV=prod -> numista-qc Cloud Run + numista-qc Firestore, grokbot@numista.ai test adds only). Then UX gate (rendered) + Field Tester. No deploy, no Eric YES before that.
