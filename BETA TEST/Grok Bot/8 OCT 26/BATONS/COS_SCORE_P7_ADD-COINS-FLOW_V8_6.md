# COS SCORE - P7 ADD-COINS-FLOW V8.6 BUILD
Scorer: Grok CoS | 2026-10-15 ~19:20 ET | Reviewed: code 68c62f3d on origin/dev (prior 5cf04a2b, docs 2caec852 / a9c8cbc5) + GEMINI38_REVIEW_P7_V8_6_BUILD.md + NET-224 (two files) + NET-225 + independent diff c3ca3fca..68c62f3d on EDS_Laptop.
Verdict: **PASS (code) with one rejected claim.** Q regression fixed. Item 2 accepted as "no in-visit remount trigger in code", NOT as a repro. Dev only. No deploys.

| # | Condition | Score | Notes |
|---|-----------|-------|-------|
| Q1 | `_qtyCtrl` starts empty, hint '1' | **PASS** | Diff confirms only change in form: `_formData = {'Condition': 'Ungraded'}` (Quantity removed), so `_qtyCtrl` text is ''. |
| Q2 | Blank Quantity submits '1' | **PASS** | `_submit` default unchanged. Tests `p7_v86_quantity_field_starts_empty_not_prefilled`, `_typing_3_in_quantity_gives_3_not_13`, `_quantity_field_empty_on_first_build`, `_blank_quantity_submits_as_1` present in test file (lines 767-876). |
| Q3 | Condition 'Ungraded' stated | **PASS** | Kept, called out in GEMINI38. |
| 2a | Name real trigger file:line | **PASS (as no-trigger finding)** | Evidence is sound: in the showManualFullScreen path there is no IndexedStack, no lazy ListView, no key on AddCoinManualForm; parent setState keeps form State. Back + re-enter (add_coins_hub.dart:649) giving a fresh form is by design, not the FT bug. Accepted as: no in-code remount explains "first char dropped". |
| 2b | Repro FAILS on e8b978f2, PASSES on V8.6, runs quoted | **REJECTED CLAIM (not blocking)** | No run on e8b978f2 was quoted. `p7_v86_year_first_char_not_dropped_in_form` reads `TextFormField.controller?.text`; on e8b978f2 that property is null because the field used initialValue, so it would "fail" because of how the test reads the field, not because of what the user sees. Also, a FormField with initialValue does not re-sync and drop typed text on rebuild. Do not cite this as a repro anywhere. `p7_v86_key_forced_remount_resets_year_field` only documents by-design reset. |
| Gates | analyze 0 / full test / GEMINI38 / dev only | **PASS (reported)** | AG reports analyze 0, 553/553. Lib diff is 1 line + comment, low risk. No deploys, no rules, no main. |
| Hygiene | Duplicate NET-224 numbers; two build commits | **NOTE** | Two NET-224 files and NET-225 restate the same build. Next AG message is NET-227+; one NET per event. |

## What happens next
- Remaining "first char dropped / Year blanks" question is behavioural only. It gets checked on a real phone in the Field Tester re-walk on the refreshed V8 hosting preview (AM, Firebase). If FT still sees it, it comes back as a new item with a screen recording, not another code hunt tonight.
- Baton stays **GROKCOS_OVER** (Grok CoS owes the V8 preview refresh to 68c62f3d, then UX Designer + Field Tester gate). Not tonight.
- AG CoS: no new P7 work. Rule 8 WAIT. P1/P4/P5/P6/P8/P9/P10 queued behind P7, not stalls. 3 AM stand-down applies.
- No ERIC baton. No deploy YES pending.