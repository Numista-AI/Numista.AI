# COS SCORE - P7 ADD-COINS-FLOW V8.5 BUILD
Scorer: Grok CoS | 2026-10-15 ~18:45 ET | Reviewed: commit c3ca3fca on origin/dev (+ docs f67c35ea) + GEMINI38_REVIEW_P7_V8_5_BUILD.md + NET-222 + independent diff check on EDS_Laptop against COS_SCORE_P7_ADD-COINS-FLOW_V8_5_PLAN_V1.md conditions.
Verdict: **FAIL (close).** Most conditions met. One real regression (Quantity) and the repro-test condition not met. Dev only. No deploys.

| # | Condition | Score | Notes |
|---|-----------|-------|-------|
| 1a | Year `^\d{4}$` + not-future | **PASS** | `_validatorFor` in add_coin_manual_form.dart: empty, regex, `> DateTime.now().year + 1`. Plain messages. Tests blank / non-4-digit / future. |
| 1b | Write-path guard in hub closure | **PASS** | add_coins_hub.dart onSubmit: refuses `.add` unless Year matches `^\d{4}$` and Denomination + Program/Series non-blank; resets `_isProcessing`; plain SnackBar. |
| 1c | List other blank-Year paths, no rules edit | **PASS** | GEMINI38 lists add-another, mint set (hardcoded 2026), manual cert, PCGS cert save, camera scanner, PCGS CSV import. firestore.rules untouched. Goes to Eric later as a decision. |
| 2a | Name the real trigger | **FAIL** | Not found. The new code comment says the trigger is the full-screen route being popped and re-pushed, which remounts the State. Controllers held in that same State cannot fix a remount, so this does not explain "first character dropped / Year blanks". Plan score already flagged that a plain parent setState does not remount the form. |
| 2b-repro | Test FAILS on e8b978f2, PASSES after; quote both runs | **FAIL** | `p7_v85_year_field_survives_setstate_rebuild` only does a parent `StatefulBuilder` setState around the same widget at the same spot. Flutter keeps the FormField State there, so on e8b978f2 (initialValue) this test would pass too. No failing run on e8b978f2 is quoted in GEMINI38 or NET-222. |
| 2c | Controllers from `_formData`, dispose all 13, none in build | **PASS w/ regression** | 13 controllers in initState, 13 disposes incl. `_mintCtrl`, `_submit` reads controllers. BUT see Q below. |
| Q | **REGRESSION - Quantity prefill** | **FAIL (must fix)** | New `_formData = {'Condition': 'Ungraded', 'Quantity': '1'}` and `_qtyCtrl = TextEditingController(text: _formData['Quantity'])`, so the Quantity box now starts with the text "1". A user who taps it and types 3 gets "13". This undoes the V8 item 4 fix (hint '1', default 1 on submit, never '11'; e8b978f2 had `'Quantity': ''`). Existing tests miss it because `tester.enterText` replaces the whole text. |
| 2b | Save all 13 fields | **PASS** | coinDoc now has Retailer/Website, Retailer Invoice #, Notes. `p7_v85_all_13_fields_in_submit_payload` asserts the form payload. Soft: it tests the form's onSubmit map, not the hub's coinDoc; hub mapping checked by diff. |
| 3a | Real before-quotes | **PASS** | GEMINI38 quotes the const SnackBar text and `_selectedToAdd` / `data`. Minor: header says "PLAN GO: NET-220"; the plan GO was NET-219. |
| 3b | Split CORS/web vs offline vs 4xx vs 5xx | **PASS** | XMLHttpRequest / Failed to fetch / typed ClientException = "server didn't answer"; SocketException / host lookup = offline; 401/403/5xx mapped. |
| 3c | FirebaseException codes | **PASS** | unavailable / deadline-exceeded = server didn't answer; permission-denied / unauthenticated = sign in. |
| 3d | Checklist count captured before request | **PASS** | `selectedCount` captured before try; "Couldn't add your N coins - ...". |
| 3e | Hub 1956 mint-set text | **PASS** | Now `toUserFriendlyWithContext(e, action: 'save your mint set')`. |
| 3f | Helper unit tests | **PASS** | numista_error_helper_test.dart covers each class + action prefix. |
| 4 | V8.4 intact | **PASS (except Q)** | Cert ~2906/2909 untouched. Quantity regression above is the only V8.x item undone. |
| Gates | analyze / tests / GEMINI38 / dev only | **PASS** | AG + Gemini report analyze 0, 547/547. No deploys, no rules edits. |

## V8.6 orders (dev only, small)
1. **Quantity:** `_qtyCtrl` starts EMPTY (hint '1'); `_submit` keeps the default-to-'1' when blank. Add a test that asserts the Quantity field's controller text is '' on first build, and that a blank Quantity submits '1'. Check Condition: prefilled 'Ungraded' text is the same as before V8.5 (OK to keep), but say so in GEMINI38.
2. **Real trigger:** Find what actually remounts or resets the field in the FT walkthrough (look at: whether the form sits in a lazy ListView / builder that disposes off-screen children, any changing Key or `UniqueKey()`, `showManualFullScreen` rebuilding a new `AddCoinManualForm` on each hub setState, layout switch at the phone breakpoint). Name it with file:line in GEMINI38.
3. **Repro test:** reproduce THAT trigger in a widget test. Run it on e8b978f2's form (git stash or temp worktree) and quote the FAIL, then quote the PASS on V8.6. If you prove no trigger exists in code, say so plainly with evidence instead of claiming a repro.
4. GEMINI38_REVIEW_P7_V8_6_BUILD.md (verbatim before/after, per-item checklist), flutter analyze 0, full flutter test, commit explicit paths, push dev only, rename baton GROKCOS_OVER, file NET.
5. **NO deploys**, no live writes, grokbot test account only. **3 AM AG stand-down applies** - if V8.6 is not done by ~2:45 AM ET, file WAIT-OUT and stop.

## Housekeeping
- Baton GROKCOS_OVER -> **AGCOS_OVER** (V8.6 build). No plan file needed for this size; go straight to build.
- Rule 8: P1/P4/P5/P6/P8/P9/P10/P12/P13 WAIT behind P7 - not stalls. No ERIC baton. No deploy YES pending.
- Backend CORS is LIVE (NET-219, rev 00465-xx7); main still lacks b611eaca - next main deploy must include it.