# COS SCORE - P7 ADD-COINS-FLOW V8.15 BUILD
Scorer: Grok CoS (watch) | 2026-10-18 08:32 ET | Reviewed: code `99773ac4` on origin/p7-v8.9 (parent f48d15e3) + EXECUTE_DONE_P7_V8_15.md + GEMINI38_REVIEW_P7_V8_15_BUILD.md + NET-314 (AGCOS) + independent read of `git show 99773ac4` and `git grep run.app 99773ac4` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (9 files).
Verdict: **PASS (code) WITH 1 SECURITY MUST-FIX + 1 SHOULD-FIX, both folded into V8.16.** GEMINI38 hygiene PASS. Dev only. No deploys.

| # | Item (NET-312) | Score | Independent check (99773ac4) |
|---|---|---|---|
| 1 | constants.dart `String.fromEnvironment` with byte-identical live defaults | **PASS** | Diff shows `API_BASE_URL` / `SCAN_SERVICE_URL` defaults are the exact old strings (`numista-backend-568985927038...` / `numista-scan-service-568985927038...`). |
| 2 | 5 Dart files use `kApiBaseUrl` | **PASS** | program_manager_screen `:2140`, family_subaccount_service `:48` (`'$kApiBaseUrl/api/v1/family'`), market_news_service `:44`, stripe_service `:9`, upcoming_releases_service `:78`. `git grep run.app` in lib/ now finds only constants.dart. No relative `/api` Uri in lib/. |
| 3 | Test proves defaults equal live | **PASS** | `p7_v8_ux_safety_test.dart:1867-1871` asserts both constants byte-for-byte (trivial const check; AG reports 581/581, not re-run by watch). |
| 4 | HTML pages reach test backend | **PASS (works) / FAIL (security) -> MUST-FIX in V8.16** | `add_coins.html:527-539`, `scraper_dashboard.html:522-534`. See below. |
| 5 | One GEMINI38 review, code verbatim | **PASS** | Quotes match `git show 99773ac4` line for line. |

## MUST-FIX (security, fold into V8.16 before any merge or wide preview use)
The `?api=` check is `/^https:\/\/[^\s]+\.run\.app/` with no end anchor and no host check. It accepts `https://evil.example/x.run.app` and any stranger's `*.run.app` service. `add_coins.html` sends the user's Firebase Bearer token to `API_BASE` (`:782-799` upload, `:834` process, `:896-898` status, `:943-945` and `:1006-1008` receipts). So a crafted link to a preview channel would hand the signed-in user's token to an outside host. Preview channels share Firebase Auth with live users, so this is real even though prod origins are locked out.
Fix: parse with `new URL(apiOverride)`, require `protocol === 'https:'`, require the hostname to match an exact allowlist (our services only: `numista-backend` / `numista-scan-service` on `-568985927038.us-central1.run.app` or `-qntvrqvxma-uc.a.run.app`, optional `<tag>---` prefix), and return `u.origin` (drop any path or query). Anchor the origin regexes with `^https://` too. Add a small JS or Dart-side test listing accepted and rejected examples (include `https://evil.example/x.run.app` and `https://attacker-xyz.a.run.app` as rejects).

## SHOULD-FIX (fold into V8.16)
- Behavior change on localhost: old add_coins.html used `''` (same-origin dev server) on localhost/127.0.0.1; new code sends localhost to the LIVE backend. That breaks "dev only, no live data writes" for anyone testing locally. Restore localhost/127.0.0.1 -> `''`.
- `web/index.html:76` preconnect still names the live backend. Harmless (hint only); leave or note.

## Gates / Next
- V8.15 code PASS with the fixes above riding in V8.16 (NET-314 GROKCOS, already queued). V8.16 also changes main.py (CORS outermost + import ownership), so the p7gate tagged backend must be redeployed from the V8.16 tip anyway. Build the ONE p7-gate preview from V8.16, not V8.15.
- Baton -> **AGCOS_OVER** for V8.16 (NET-314 GROKCOS + NET-315 additions). One GEMINI38 review. Explicit-path commits. No deploys, no main.
- Housekeeping: two files used NET-314 (GROKCOS 08:05 and AGCOS 08:13). Next number is NET-315.
- No ERIC baton. No live deploy YES pending. Deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.