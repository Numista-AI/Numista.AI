# GB CoS round-3 score — NET-817 Cards v2.2 (NET-780b)

**97/100 — PASS. Threshold >=95. Remaining must-fixes: none.**

Reviewed plan: `docs/FAILFIX_PLAN_NET-780b_CARDS_v2.2.md`
Bytes: 62090; SHA-256: `33c67371ce69326e6b09394daefe400628524aed689d87b5a40adbba509676b4`. Independently matches the 20261108-0813 review baton.

Prepared 2026-11-08 08:19 AM EST (America/New_York). **PLAN-ONLY, delta-focused independent CoS review.** Exact EDS files were copied verbatim, fingerprinted, and compared line-for-line with the round-2 reviewed artifacts. Every round-3 added/changed span was reviewed against the round-2 must-fixes. Unchanged source grounding relies on the preceding full-plan/citation audits; it is not relabeled as a fresh full-repository investigation. Writer self-scores and baton claims are not approval.

No application code edited or executed, no Dart analyzer/Flutter tests/builds, no Firestore/GCS access, deployments, commits, pushes, external sends, or EDS filing/renames. The only execution was independent box-side document comparison and WCAG arithmetic. Narrow read-only `git show` source spot-checks confirmed collection surface colors at pin `4d17ca5e`, lines 211 and 3029-3032. Three distinct full object IDs retained across the four plans resolve; unresolved 0. `origin/main` remains `9f04550a45fa4da082ba8948c2d89a521a90fa45`.

## Round-2 MF-SAG-C3: CLOSED
1. **AAA arithmetic fixed in the actual proposed widget.** Plan **458-459** changes dark text to #E0BC4A and dark chip fill to opaque #0D1520. Thresholds are not weakened and no ratio is rounded before comparison.
2. **Actual mounted backgrounds are measured.** Case 6 at **948-987** mounts each cited surface in the widget tree, obtains the pumped Container's color/decoration at **970-972**, reads the keyed chip's actual decoration, and composites at **981**. Assertions **984-985** measure text against both the actual surface and effective chip background. Value and label text colors are compared. Four theme/surface cases remain explicit.
3. **Alpha handling is coherent.** _over at **797-801** source-over composites the fill over an asserted opaque surface. Current fills are opaque, so current effective chip backgrounds equal their declared fills. This is not an unmeasured translucent dark chip.
4. **Incorrect light ratio corrected.** Current prose uses 4.96:1, consistent with the unrounded recomputation below.

## Independent WCAG recomputation (not writer arithmetic)
Computed on the box using standard sRGB linearization (0.04045 cutoff), luminance weights 0.2126/0.7152/0.0722 and (Lhigh+0.05)/(Llow+0.05):

| Foreground | Background | Unrounded ratio | Required | Result |
|---|---|---:|---:|---|
| #E0BC4A | #1E2937 | 8.028902292627 | 7.0 | PASS AAA |
| #E0BC4A | #0D1520 | 10.008092181871 | 7.0 | PASS AAA; opaque dark chip too |
| #856404 | #FFFFFF | 5.494604937716 | 4.5 | PASS AA |
| #856404 | #F5F5F0 | 5.024086925210 | 4.5 | PASS AA |
| #856404 | #FFF3CD | 4.959219119110 | 4.5 | PASS AA; light chip |

Historical cross-check: #D4AF37/#1E2937 is still 6.995616394042 (<7). Historical alpha-25 #D4AF37 over #1E2937 rounds to #303637, and old text contrast is 5.845191886760. Thus both the old failure and the new claimed corrections independently reproduce arithmetically. This does not claim any Flutter test was run. Raw results are in `WCAG_RECOMPUTATION.json`.

## Source and invention check
Fresh narrow `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` confirmed **211** _surface uses #1E2937 / white, and **3029-3032** virtual-child uses #0D1520 / #F5F5F0. The new #E0BC4A is openly a proposed color change, not falsely quoted as the pin. No invented isDime/y guard or unapproved inspector deletion was reintroduced; C1/C2/C4/C5 closures are unchanged.

**Remaining must-fixes: none.** Inherited nonblocking margins: broad contains-based parser outside the explicitly fixed denomination cases, and stale historical top metadata/final v2.0 gate references. Fresh SAG must score this exact v2.2, not either old version. These were not silently promoted into new blockers or changes to closed semantics.

**97/100 PASS.** All round-2 contrast deductions are substantively closed; three points remain for inherited nonblocking generalization/document-hygiene precision.

## Privacy, authority and next gate
Promo scan counts only: **current four plans 0; handoff tree 0** (2,867 text files recursively under `BETA TEST/Grok Bot/8 OCT 26`). The exact previously identified private literal was derived internally from its cited historical document and never printed. History was not rewritten; a zero working-file count is not proof of erased history or a universal unknown-secret detector.

Main locked; US-only; Stripe sandbox/OFF; alerts only, NEVER caps; no AJ identifying values or private tokens reproduced. PASS means plan readiness, not runtime correctness, deployment permission or beta retest clearance. Next: independent SAG must read the **entire exact current plan**, score >=95 separately per plan, then Eric's typed YES. An older-version score or this delta summary is insufficient. Firestore writes and deploys each retain separate YES gates; no beta retest before Field Tester evidence closes every open item.

Files are prepared only in `/workspace/round3-scoring/scores/`. Eric/parent will file them using `FILING_MANIFEST.json`. No destination file or baton has been modified by this executor. DONE on a review baton denotes completed review, never approval.
