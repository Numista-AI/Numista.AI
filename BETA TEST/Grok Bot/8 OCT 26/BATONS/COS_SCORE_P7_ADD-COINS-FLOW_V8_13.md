# COS SCORE - P7 ADD-COINS-FLOW V8.13 BUILD
Scorer: Grok CoS (watch) | 2026-10-17 17:10 ET | Reviewed: code `86f646da` on origin/p7-v8.9 (parent 689e2ca1) + EXECUTE_DONE_P7_V8_13.md + NET-303 + independent read of `git show 86f646da` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (2 files: backup_export_service.dart, p7_v8_ux_safety_test.dart).
Verdict: **PASS (code).** The NET-298 must-fix is done. GEMINI38 correctly skipped (Rule 9.3, 2 files). Dev only. No deploys.

| # | Item (NET-298) | Score | Independent file:line (86f646da) |
|---|---|---|---|
| 1 | JSON backup full-fidelity again | **PASS** | `backup_export_service.dart` V8.12 `sanitizedCoins` block deleted; payload `collections.coins` and legacy `coins` are the raw Firestore maps (`:135`, `:160`); metadata counts from `coins` (`:126`, `:150`). No injected blank Retailer/Invoice/Notes/cost keys. |
| 2 | Full ISO timestamps in JSON | **PASS** | `generateJsonStringFromPayload` `:222-229`: Timestamp -> `toDate().toIso8601String()`, DateTime -> `toIso8601String()`. `exportJsonDownload` `:232-234` uses it. |
| 3 | Display formatting only in CSV | **PASS** | `generateCsvStringFromPayload` `:245-273` applies `_formatYear` / `_formatQuantity` / `_formatCost` / `_formatDate` per row; `exportCsvDownload` `:276-278` feeds it the raw payload. Fallback to `collections.coins` at `:246`. |
| 4 | Test | **PASS (re-run by Grok CoS)** | `p7_v8_ux_safety_test.dart:1738-1782` checks Cost stays num 15.5, no injected keys, Added keeps `2024-10-17T...`, CSV row `"$15.50"` and `"2024-10-17"`. Re-ran `flutter test --plain-name p7_v813` in p7v89_build: **+1 All tests passed**. Full 577/577 and analyze 0 as reported, not re-run. |

## Soft (not blocking, fold into V8.14 if cheap)
- The `mockCoins` test hook (`:18-58`) copies the whole payload shape inside production code, with a hard-coded `test@numista.ai` and `app_version`. It can drift from the real payload. Better: build the payload in one shared helper that both paths call, so the test exercises the real shape.

## Next (sequence change, Grok CoS call)
- Rather than spend a preview + UX + FT gate on V8.13 alone and then another for V8.14, AG builds **V8.14 (NET-299, Eric's 17 Oct live add-coins MUST-FIXES) now on top of 86f646da**, same branch p7-v8.9. Then ONE preview on the fixed channel `p7-gate` + UX Designer + Field Tester re-gate covering V8.10 through V8.14. This saves quota (Rule 8/9) and gets Eric's live failures fixed sooner.
- V8.14 touches more than 2 files, so it needs ONE GEMINI38 review with code quoted verbatim (Rule 9.3).
- PDF on preview still needs scan_service redeployed (live Cloud Run change, Eric's typed YES). Grok CoS asks Eric before the FT gate.
- Baton renamed to **AGCOS_OVER**. 2h stall clock on AGCOS starts 2026-10-17 17:10 ET.
- No ERIC baton, no deploy YES. Deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.