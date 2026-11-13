# COS_SCORE_F1_AWQ_SLOT_FIX_V3 - ITERATE (narrow: Title-path old-name coins still dark)
From: Grok CoS. 13 Oct 2026 7:40 PM ET. DEV ONLY. No Firestore / sync_canon / live deploy.

Scored: NET-059 (AGCOS) + GEMINI38_REVIEW_F1_AWQ_SLOT_FIX_V3.md + commit `435669c0` against NET-058 / COS_SCORE_F1_AWQ_SLOT_FIX_V2.md.

## Verdict: ITERATE (one narrow blocking item; Theme path PASSES)

### What passes (Grok CoS verified on EDS_Laptop, dev branch, tree clean after)
- Alias map `slot_resolver.dart:222-237` and theme-path wire-in `:272` match the Gemini 3.8 quotes verbatim.
- Grok CoS re-ran `test/slot_resolver_awq_test.dart`: 23/23 PASS.
- Grok CoS mutation: replaced `_canonicalizeAwqSubject(_normalizeSubject(theme))` with `_normalizeSubject(theme)`: 16 pass / 7 FAIL. Restored with `git checkout`: 23/23 PASS. Matches AG's paste.
- Grok CoS probe (scratch test, deleted after), full 20-slot program, Theme/Subject set: "Dr. Pauli Murray", "Patsy Mink", "Stacey Milbern", "Zitkala-Sa" and "2024 - Patsy Mink" all light their renamed slots (TRUE). "Dr. Pauli Murray" vs Dr. Vera Rubin slot = FALSE (no false positive).
- Gemini review header now reads Gemini 3.8; real clock times used. package-lock.json removed from numista_mobile/.
- Counts accepted as filed (flutter 457/457, pytest 501/501, analyze 0).

### Finding C (blocking): the Title path has no aliases
`_fastPathSubjectMatchesSlot` falls back to the Title / name / official_title path when Theme/Subject is blank (lines 276-299). That path only searches canonical slot names, so old names never match. Grok CoS probe, coins with Title only (no Theme/Subject):
- "2024 Patsy Mink Quarter" vs Patsy Takemoto Mink slot -> FALSE (dark)
- "2024 Dr. Pauli Murray Quarter" vs Rev. Dr. Pauli Murray -> FALSE (dark)
- "2025 Stacey Milbern Quarter" vs Stacey Park Milbern -> FALSE (dark)
- "2024 Zitkala-Sa Quarter" vs Zitkala-<U+0160>a -> FALSE (dark)
- Control: "2024 Celia Cruz Quarter" vs Celia Cruz -> TRUE (path is live)
Same systemic gap as Finding B, one path over (Eric's every-related-feature rule). Scanner or eBay-style adds with only a title would stay unchecked.

## Do (dev only)
1. Title path: also try each old-name alias key as a full-phrase candidate and map a hit to its canonical name before the longest-match compare (e.g. build candidates = slot names + alias keys whose value is that slot). Keep the longest-match rule so "dr. pauli murray" inside "rev. dr. pauli murray" can't cross-light.
2. Tests: Title-only isMatch TRUE for all 4 old names; Title-only canonical title still TRUE; one Title-only no-false-positive; one `resolveProgramInventory` with Title-only old-name coins OWNED.
3. Mutation proof (title aliases off -> FAIL; on -> PASS), Gemini 3.8 review with code quoted, full flutter / pytest counts, real clock.

### Minor (same pass)
- Root `.gitignore` now ignores `package-lock.json` everywhere. That would silently hide a new lockfile in numista_backend/functions or any Node service (deploys need them). Scope it to `numista_mobile/package-lock.json`.
- Baton hygiene: AG created `BATON_F1_RERUN6_GROKCOS_OVER.md` as a new file and left `BATON_F1_RERUN6_AGCOS_WILCO.md` behind. Grok CoS removed the stale duplicate this run. Please rename (git mv) the baton, don't copy it.
- NET-059 number was used by both CoS. Next free is NET-061.

Hard holds: dev only, no live data writes. Firestore sync / deploy each need a separate Eric typed YES.