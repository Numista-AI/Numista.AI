# Independent SAG review chunk1

Full plan submitted; packet chars 296912
Usage: {"prompt_tokens": 85449, "completion_tokens": 1482, "total_tokens": 125133, "prompt_tokens_details": {"text_tokens": 85449, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 1152}, "completion_tokens_details": {"reasoning_tokens": 38202, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}, "num_sources_used": 0, "cost_in_usd_ticks": 4072740000}

## Score / verdict

| Item | Result |
|---|---|
| Verdict | **PASS** |
| Score | **96 / 100** |
| Pass bar | ≥ 95 |
| Review type | Plan readiness only. No tools, tests, builds, or applies were run |
| Baseline split | Shared files checked against **4d17ca5e**. Catalog tree checked against **b0b05808** and treated as absent on 4d17ca5e |
| Execution | **Not authorized** |

No blocking must-fix. Verifiable pins, hunks, parser outcomes, privacy locks, and rollback match the supplied evidence. Deductions are residual risk and polish, not contradicted facts.

## What checked out

- **4d17ca5e** `main.dart`, `pubspec.yaml`, `melt_value_service.dart:53-99`, `header_stats_bar.dart:92` and `:106-109`, and `home_dashboard.dart:299-301`, `:415`, `:440`, `:472`, `:746`, `:760` match the plan’s before-text and line numbers.
- Catalog sources are correctly taken from **b0b05808**, not from 4d17ca5e. Line counts for the shown catalog files match the packet (browse 1232, us-numismatics 598, service 865, and the smaller dependents).
- `pubspec` hunk `@@ -94,6 +94,7 @@` and the three `main.dart` hunks line up with 4d17ca5e. `/catalog` is added to `isKnownPath` before the soft-404 return, then handled before normal app startup.
- Card hunks line up with b0b05808 `catalog_browse_screen.dart` (`@@ -2,6`, `@@ -1085,6`, `@@ -1147,6 +1155,46 @@`; 40 added lines). Import `../../services/melt_value_service.dart` is the right relative path. `url_launcher` and `web` are already on the 4d17ca5e pubspec.
- Traced planned `parseFaceValue` against the old 4d17ca5e body: half-dime before dime, `3 cents` → 0.03, N-dollar and `$1000` / `G$2½` / `2 1/2 Dollars` fixes, multi-denom / planchet / candareen → 0.0, and the five call sites. Qty example 50.88 and the three `compute` expectations follow the patched parser plus the existing oz tables.
- 66-key map has no duplicate `$50`. 66 strings + 4 shared type pairs + medal null = 71 pairs. That arithmetic is consistent.
- Locks hold: plan only; `p7-v8.9` two-commit landing; `git revert` only; main left at `9f04550a45fa4da082ba8948c2d89a521a90fa45`; Stripe OFF; alerts not caps; no private collection fields, promo tokens, or user identifiers in the delta; Firestore/deploy still need a separate Founder YES.

## Must-fixes

None. Nothing in the supplied git-show evidence contradicts a cited path, line, or planned output enough to block the gate.

## Deductions (non-blocking)

| Severity | Deduction | Item |
|---|---:|---|
| Low / residual | −2 | Shared-parser hyphen/en-dash guard is broader than the one catalog range, and zero-face non-medals still get the amber “Face value” chip. Both are disclosed and out of the narrow delta. No negative test locks a non-catalog string such as a date-range denomination. |
| Low / polish | −1 | Caller “regression” reimplements the sum and calls `MeltValueService` directly. It does not import `HeaderStatsBar` or `home_dashboard`. Acceptable given Firestore snapshots, but it will not catch a caller that stops using the parser. |
| Low / polish | −1 | No explicit `cd numista_mobile && flutter test …` / repo-root `git apply` instruction. `File('assets/catalog/…')` depends on package cwd. `Uri.decodeComponent` on the new public route can throw on a bad `%` sequence. §2/§4 still say “v2.1” in a v2.2 plan. |

## Uncertainties (not scored as defects)

- Blob SHAs, `git apply --check` exit 0, and tip `d873ab9f` identity were not re-verified here. The **text** of the 4d17ca5e and b0b05808 excerpts does match. Landing must re-check those files at the real `p7-v8.9` tip before Commit 1; the plan’s own pin is ancestor `4d17ca5e`, not the observed tip.
- Widget fixtures “1842 Liberty Seated dollar” and “Libertas Americana medal”, the 2,965/181/56 split, and 0/3202 AI keys are writer claims. The packet only proves 3202 rows and two other public rows. If either search string is not unique, the widget tests fail as written.
- `pumpLoadedCatalog` depends on `rootBundle` being a caching bundle whose preload survives `runAsync`. Those SDK line citations are not in the packet. If that assumption is wrong, the widget tests fail at execution; that does not make the plan internally inconsistent.
- `b0b05808` `main.dart` line cites and `nac_code_parser_test.dart` were not in the packet.

## Next gate

SAG pass is not execution approval and is not a Founder YES.

1. If GB CoS has not scored this v2.2 text, that score is still open. Do not treat the writer’s 95 as either gate.
2. Founder must type **YES** before any checkout, patch, test run, or commit.
3. Then only `p7-v8.9`: Commit 1 = the 12-path checkout from `b0b058087f1492244a0c0b769e126b38ac1ba06c` plus the pubspec and main hunks; Commit 2 = parser, card, and the new test file. Re-pin the tip first.
4. Run the new tests from `numista_mobile` and record real results. Do not claim the inherited CoS-80 numbers as a fresh run.
5. Rollback is `git revert` of Commit 2, then Commit 1, on `p7-v8.9` only. No reset, no force-push, no main, no deploy, no Firestore/GCS write, Stripe remains OFF. Any deploy or Firestore write needs its own Founder YES.