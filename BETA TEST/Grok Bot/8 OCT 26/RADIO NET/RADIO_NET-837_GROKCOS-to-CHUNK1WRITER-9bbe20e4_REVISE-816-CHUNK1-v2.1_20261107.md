# RADIO NET-837: GROK BOT CoS → Catalog Chunk 1 writer. REVISE ORDER: Chunk 1 v2.1 (NET-816)

**From:** Grok Bot CoS (GROKCOS)  **To:** Catalog Chunk 1 writer `9bbe20e4-a0d5-4a25-b16a-f616630ad4bb`, Task Master, SAG
**Filed:** 3:27 PM ET 7 Nov 2026 (America/New_York, observed clock)
**Authority:** Standing baton review on `BATON_NET-816_GROKCOS_REVIEW_CATALOG_CHUNK1_20261107-1516.md`. PLAN ONLY. This is NOT a build, execute, deploy or Firestore YES.
**Routing:** Same new writer. Attempt **2 of 4**. Do NOT send this revise to AG CoS v4 (parked) or v5 (different tracks).

## Score
- NET-816 Catalog Chunk 1 v2.0: **68/100 FAIL** (95+ required). Full score: `BATONS\COS_SCORE_NET-816_CATALOG_CHUNK1_v2.0_20261107.md`
- Parser logic is strong (simulated 0 mis-parses on the plan's expected map; Five Cents 0.01→0.05). Fail is landability + tests + blast-radius hygiene.

## Order: deliver `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.1.md` closing every item below
1. **Landing path (blocking).** Catalog tree / asset / pubspec `assets/catalog/` / `/catalog` route are absent on `p7-v8.9`. Either (a) prerequisite port from dev `b0b05808` via `git checkout b0b05808 -- <exact paths>` plus pubspec + main.dart route hunks against p7, or (b) state the real ship branch with evidence + Eric YES gate. Update §6 rollback to match. main stays 9f04550a.
2. **Test compile (blocking).** Remove duplicate `const` map key `r'$50'` (or key by `(type, denomination)`).
3. **Widget finders (blocking).** Scope title finders to the grid/card (`find.descendant(of: find.byType(GridView), …)`) so `initialQuery` in the search box does not double-match.
4. **Caller blast radius.** List every `parseFaceValue` caller (`home_dashboard.dart:300`, `header_stats_bar.dart:108`, `melt_value_service.dart:141/146/200`). State that user/collection face totals will change, with examples. Add regression tests for face-sum inputs.
5. **Face-value semantics.** Multi-denom sets and planchets: show `'—'` / "Set" / documented sum — never just the max. Update expected map.
6. **AI-estimate chip.** Name pipeline + key (align with NET-817 `'AI Estimated Value'`) and owning chunk, or replace with honest copy and no estimate promise.
7. **Hygiene.** Recount hunk headers so both diffs are `git apply`-clean. Correct 70→71 pairs / 67 strings. Record p7 tip at filing as `c8c4dbdd`.

## Desk note
Catalog remains Thanksgiving CRITICAL PATH. Chunks 2–6 stay parked. After 4 failed attempts on this writer, stop and notify Eric.

## Rules
- Plan only. No code execution, deploy, Firestore writes or main merge.
- Alerts only, no budget caps. Main locked at 9f04550a. Cycle has no Argon.
- Eric's typed YES is required before any build.

ACK on radio with ETA for v2.1.

OVER, Grok Bot CoS
