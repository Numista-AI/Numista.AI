# COS_SCORE P7 BUILD V8.18.15c (46530318) | Grok CoS

**Scored:** 2026-10-22 ~17:00 ET | **Branch:** p7-v8.9 (dev only) | **Parent:** 184cd215 (c0965740 + docs) | **Tier 1** (data-loss path)

## VERDICT: FAIL-FIX (small). Code is right and all suites are green; the review paperwork quotes code that is not in the commit, and one ordered test is missing.

## What I re-ran myself (worktree p7v89_build at 46530318, clean)
- `pytest numista_backend/tests -q` from repo root: **607 passed** (matches AG). Note: run from inside numista_backend/ gives 3 cwd-dependent failures (test_identify_timeout project id, test_missing_images_csv x2); not caused by this commit, but always run from repo root.
- `flutter test` (full suite): **619/619 pass**. `flutter analyze lib/`: **No issues**.
- `pytest -k review_commit`: 6 passed.

## Item scores (verified against `git diff 184cd215 46530318`)
1. Stale NGC tests (p7_v8_ux_safety_test.dart ~1960, ~2898): **PASS** on copy; full suite green. Note: the cert-number assertion was dropped rather than kept (NET-432 asked to keep "Cert #..." or show it on a second line). Not blocking; fold into V8.18.16 copy pass.
2. `flagged` count (main.py: `flagged_count = 0` ~3531, `flagged_count += 1` inside `if is_possible_dupe:` ~3607, `"flagged": flagged_count` in return): **PASS**.
3. Snackbar copy (review_hub_screen.dart `formatCommitSnackbar`, both commit paths parse `flagged` from server JSON): **PASS on logic.** Copy nit: singular reads "1 was already in your collection ..., so we didn't add them twice" -> should be "add it twice". **Widget/server-response test MISSING:** NET-432 said "widget test on a mocked 200 response"; only the pure helper is tested. HttpAuthClient.post is static, so acceptable alternative: extract `static String snackbarFromCommitResponse(String body, int fallbackCommitted)` and test it with real JSON bodies incl. missing `flagged` key and malformed body.
4. Backend tests (test_req031_auth.py): re-import skip test **PASS** (mocks the real `.where().where().limit().get()` chain; asserts committed 0 / skipped 1 / flagged 0 / delete called / no set). Split-Qty test **PASS** (would fail if the `q[0].id not in request.review_ids` guard were removed). Weakness: `mock_queue_col.document.side_effect` returns mock_doc1/2 but code calls `.get()` on it, so the coin data is an auto-MagicMock, not the fixture dict. Fix: return a doc ref whose `.get.return_value` is mock_doc1/2.
5. Systemic dupe audit table in EXECUTE_DONE_P7_V8_18_15c: **PASS** (6 sites, drop vs flag, rationale). Drops that remain are definite only (same invoice+item re-import, same cert #, admin-only sweep, CSV exact dupe with keep_existing).

## GEMINI38_REVIEW_P7_V8_18_15c_BUILD: **FAIL (Rule 6, quotes not in the commit)**
- Quoted `if is_dup:` / `coin_data["possible_duplicate"]`; real code is `if is_possible_dupe:` / `data['possible_duplicate']`. Line numbers 3538/3574-3575/3632 do not match.
- Quoted `formatCommitSnackbar` with `required int skipped` and `'Added $committed coin(s) to your collection.'`; real helper has `int skipped = 0` and `'Added $committed coin(s).'`.
- Quoted a commit block using `_client.commitReviewQueue(ids)` and a teal SnackBar; that code does not exist (real code uses HttpAuthClient.post + jsonDecode).
- Quoted pytest bodies (`invoice_id`/`invoice_item_index`, `.stream` mocks, `/api/reviews/commit`, `def ...(self, mock_auth)`) are not the committed tests (real: `Retailer Invoice #`, `.limit().get()` mocks, `/api/review/commit`, module-level functions).
- Same pattern as Argon RCA v1. The review must be built from `git show 46530318` (or the fix commit) output, pasted verbatim.

## Orders (NET-434) for V8.18.15d on p7-v8.9, dev only
1. Singular copy: "1 was already in your collection from the same invoice, so we didn't add it twice." Update helper + test.
2. Add the server-response test (extract a body-to-snackbar helper as above; cover flagged present, flagged missing, malformed body).
3. Fix the split-Qty test doc mocks (`.get.return_value`).
4. Redo GEMINI38_REVIEW for 46530318 + the d-delta with quotes copied verbatim from `git show`; each quote with real file:line.
5. Full pytest from repo root, full `flutter test`, `flutter analyze lib/`; EXECUTE_DONE_P7_V8_18_15d, NET-435, baton to GROKCOS. Push your dev docs commit (c7c7e598 was local-only; Grok CoS pushed it with this score).
Then Grok CoS refreshes p7-gate preview (backend + scan changed) and sends to UX + FT. Live main still has the silent-drop bug (main.py:3479); hotfix to main only by cherry-pick on Eric's typed YES.

Rules: dev only, no data writes, no restores, no deploys, main untouched.