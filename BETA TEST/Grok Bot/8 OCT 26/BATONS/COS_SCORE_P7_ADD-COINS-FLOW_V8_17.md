# COS SCORE - P7 ADD-COINS-FLOW V8.17 BUILD
Scorer: Grok CoS (evening watch) | 2026-10-18 20:15 ET | Reviewed: code `dbda922f` on origin/p7-v8.9 (parent 7c5179cd) + EXECUTE_DONE_P7_V8_17.md + NET-328 + independent read of `git diff 7c5179cd dbda922f` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (2 files, +56/-142). Pinned regex re-tested by the watch in node (11 cases incl. userinfo, suffix, fragment and encoded-slash tricks): all pass.
Verdict: **PASS (code). V8.16 MUST-FIX and SHOULD-FIX both closed.** Dev only. No deploys.

| # | Item (NET-326) | Score | Independent check (dbda922f) |
|---|---|---|---|
| 1 | MUST-FIX: pin ALLOWED_HOST_RE to our project only | **PASS** | Both files use `^(?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-(?:568985927038\.us-central1\.run\.app|qntvrqvxma-uc\.a\.run\.app)$`. Old broad regex gone from both. Watch node test: accepts p7gate us-central1 form, p7gate uc.a form, untagged scan-service; rejects wrong project number, wrong region, wrong uc.a hash, `...run.app.evil.com`, `x@...evil.com`, `evil.com#@ours`, `%2F` trick. |
| 2 | SHOULD-FIX: one pure resolveApiBase(origin, search, liveUrl), getApiBaseUrl() delegates, asserts on the same function | **PASS** | Both files: getApiBaseUrl() is a 2-line wrapper; mockOrigin copy deleted; 12 asserts per file (4 accept, 8 reject incl. r6-r8 from NET-326) call resolveApiBase() directly. |
| 3 | Rule 9.3 (2 files, no GEMINI38), explicit-path commit on p7-v8.9, no deploys/main | **PASS** | 2 files only, pushed to origin/p7-v8.9. |

## Notes (no action now)
- PREVIEW_ORIGIN_RE still treats any `*.run.app` page origin as a preview. Harmless for token leakage (a page served from a stranger's origin has no Numista sign-in session), but tighten with the same project pin when convenient.
- Carry-over from V8.16: ServerErrorMiddleware outside CORS (unhandled 500 has no CORS headers); confirm ALLOW_UNAUTHENTICATED is not "1" on live and p7gate backends before the gate.

## Gates / Next
- Baton stays **GROKCOS** (preview build is Grok CoS work): ONE p7-gate Firebase preview (fixed channel `p7-gate`) + p7gate-tagged backend/scan_service revisions (no traffic) from the V8.17 tip dbda922f, then UX Designer + Field Tester re-gate on the grokbot test account.
- AG stands down (Rule 9.1; Eric's 8:30 PM stop). No ERIC baton. Live deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.