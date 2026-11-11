# BATON — NET-816 FAIL-FIX R2 — PLAN ONLY — v3.1 narrow fix (from CoS 96)
From: Grok Bot CoS, 10 Nov 2026 ~8:55 PM ET (America/New_York). To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
**Count: R2 track attempt 4 of 10; AG CoS v5 try 4 of 4 (your last).** If v3.1 misses, stall rule t2564u hands the fix to SAG via the API.

## Base and score
- Base: PLAN v3 `PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md`, 35,380 B, SHA-256 `e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75`.
- Score: `MY TESTING\10 NOV 2026\COS_SCORE_NET-816_FAILFIX-R2_v3_96_PASS_20261110.md`, 10,419 B, SHA-256 `9d3e8c07108000284821c1329c6d493cfeaa3c59212d545c05a807647667d3d7`. Read D3′ and D4′ in full.
- Baseline: app code `a3d7dca20fbbaf06a522205b22d0740b600de52b`; `p7-v8.9` docs tip `e55302e2`; main `9f04550a`.

## Allowed changes (ONLY these two)
1. **D3′, search.** "1842 Liberty Seated dollar" must return exactly 1 card. Either run the two passes across the whole filtered list in `_applyFilters()` (`catalog_browse_screen.dart:112-200`: direct substring matches first, token matches only if the direct list is empty), or fix the 1842 test on its real screen. Cite the real test file and helper: `test/catalog_chunk1_face_value_and_card_test.dart` with `pumpLoadedCatalog` + `CatalogBrowseScreen(initialQuery: …)` (`:348-385`). Don't use the non-existent `search()` helper, and don't use `catalog_browse_test.dart` (it tests `us_numismatics_catalog_screen.dart`). Show evidence from the real `assets/catalog/catalog_public_v1.json` at a3d7dca2 that 1842 → 1, "Morgan dollar 1881" → 5, "1816" → 0 under the new logic (command and output).
2. **D4′, runbook readback (§2.2).**
   - Use the preview host prefix `https://numista-vault--p7-gate-` (site `numista-vault`; regex `https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`).
   - If no URL is found, or any check can't run, **throw**. It must never print "verified" after skipping.
   - Real live-unchanged check: before the deploy, capture the live channel release time from `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json` (check the exit code). After the deploy, re-read it and throw if the live time changed or p7-gate is missing.
   - Fix or drop the no-op `Set-Location $repoRoot`. If you keep it, use the fixed repo path `C:\Users\ericd\Documents\MyVertexProject` and assert `git rev-parse --show-toplevel`.

**Everything else stays byte-for-byte as in v3.** No other edits, rewording or "improvements". The header iteration/date line and a short v3.1 change note are the only other permitted lines.

## DONE must include
New file name `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md` in `MY TESTING\10 NOV 2026\`, final byte size and `Get-FileHash` SHA-256 of the on-disk file; a closure map (D3′, D4′ → plan lines); and the line diff against v3 `e7c54bab…7f75` (it must show changes only in the allowed areas).

## Limits
PLAN ONLY, with no grade or self-score. No code, commits, builds, deploys, Firestore, GCS or Stripe, and no spend. HOLDs `74611e05` and `41b8bd5f` stand; main stays `9f04550a`; go-live addendum NOT ACTIVE. Stand down by 3 AM ET.
The v3 SAG packet (`cb83f4ea…d5ea`) is SUPERSEDED and won't be submitted.
