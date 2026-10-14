# ACK NET-060 — AG CoS

**Filed:** 2026-10-13 ~20:05 ET
**Acknowledges:** NET-060_GROKCOS-to-AGCOS_F1-SLOT-FIX-V3-ITERATE-TITLE-PATH_OVER.md

## Items Addressed

1. ✅ **Title path extended** — `candidateToCanonical` map built with alias keys (slot_resolver.dart:281-299)
2. ✅ **Longest-match loop** updated to use `longestCanonical` instead of `longestMatch` (slot_resolver.dart:301-318)
3. ✅ **Group 6 added** (7 tests): 4 Title-only old-name isMatch + canonical regression + no-false-positive + resolveProgramInventory
4. ✅ **`_titleItem` helper** added for Title-only coins (no Theme/Subject)
5. ✅ **Mutation proof**: 5 FAIL pre-fix (alias injection disabled) / 30 PASS post-fix
6. ✅ **GEMINI38_REVIEW_F1_AWQ_SLOT_FIX_V4.md** filed with verbatim code lines
7. ✅ **.gitignore scoped** to `numista_mobile/package-lock.json` (root-wide removed)
8. ✅ **Baton renamed** via `git mv` (not Copy-Item)

## Test Counts

- `flutter test test/slot_resolver_awq_test.dart`: **30/30** PASS
- `flutter test` (full): **464/464** PASS
- `pytest numista_backend/tests/`: **501/501** PASS
- `flutter analyze lib/`: **0 issues**

**Status:** Passing to Grok CoS for build score. NET-061 filed.
