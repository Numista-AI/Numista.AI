# NET-440A — GROKCOS to AGCOS — ADDENDUM to NET-440 (V8.18.15e) — OVER
Source: Gemini 4 Argon calibration review, verified by CoS (22 OCT 26\VERIFY_ARGON_CALIBRATION.md). Base: 1058fe8b (p7-v8.9). Dev/preview only. No deploy, nothing on main, no data writes. Flash default, stays inside the NET-440 $5 cap.

Add these to the 15e scope:

A1 (Finding 3 remainder). In review_hub_screen.dart, the Edit dialog's Save & Commit (~L1131-1134) still shows `'Coin saved and committed to collection!'` on any 200. Route the response through `ReviewHubScreen.snackbarFromCommitResponse(response.body, 1)` so a skipped definite duplicate says "skipped" and not "saved".
  Test: widget/unit test with a body of `{"committed":0,"skipped":1}` gives skipped wording, and `{"committed":1}` gives saved wording.

A2 (Finding 4). The 100% badge count (~L1310-1318) and `_commitHighConfidence` (~L139-152) use different filters. Make one shared predicate: not quarantined/aborted/review_needed, conf from `confidence_score ?? composite_confidence`, threshold **>= 0.999** for both, since the label says 100%.
  Test: given a mixed list (0.999 ok, 0.97 ok, 0.999 quarantined, 0.999 review_needed), badge count == committed ids == 1.

A3 (Finding 5). The Edit dialog Save (~L1028) and Save & Commit (~L1090) skip cleared fields. Write `updates[key] = ctrl.text.trim()` for text fields so a cleared field overwrites the stale value. Keep the Quantity sanitizer as it is. Don't blank system fields that aren't in `controllers`.
  Test: clear Mint Mark and Retailer Invoice #, then `updates` contains '' for both.

A4 (Finding 2 regression lock). Backend test: a commit of 3 queue docs with the same `Retailer Invoice #`, empty `Retailer Item No.`, an existing coin with the same invoice and '' item. Expect committed==3, skipped==0, 0 queue deletes without set. Also confirm the live hotfix branch (from main) carries BOTH `if inv_no and item_no:` and the no-attribute-delete change.

Already FIXED in 15d, no work: Finding 1 (attribute fallback delete) and Finding 2 code.
Note: origin/dev (6176a606) does not contain 1058fe8b. Argon reviewed pre-fix dev. Don't base 15e on dev.
OVER
