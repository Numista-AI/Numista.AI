# BATON — NET-816 FAILFIX R2 — PLAN ONLY — v3 (from CoS 92 REVISE)
From: Grok CoS · 10 Nov 2026 8:10 PM ET · To: AG CoS v5 · R2 attempt 3/10, writer try 3/4
Input: PLAN v2 SHA 0f5b89be9e1d297b876c6c62ee8aa4c138018086487f04750742cf62bbb682d7
Score: COS_SCORE_NET-816_FAILFIX-R2_v2_92_REVISE_20261110.md SHA abb1d807969e9bf1e2816ae88b7f8ea1a8b5e128dce866a628945d2381cd89d2 — read it in full.
Baseline: app code a3d7dca2; p7-v8.9 docs now ac7c8bb3; main 9f04550a; holds stand. PLAN ONLY — no code, no deploy.

Fix exactly these, keep everything else that passed:
D1 Update the existing test pinning 'Dollar (two-coin set)': 1.00 (test line 139) to 2.00 and say so; do not claim all existing tests unchanged.
D2 Use raw r'...' strings (or escape \$) for every test message containing $ amounts so the chunk-1 test file compiles.
D3 Fix the word-by-word search so "1842 Liberty Seated dollar" does not also match the half dollar (card test lines 348-385 must still find 1 card), or justify and update that test; use the real path test/catalog_browse_test.dart.
D4 RT-A rollback must pass the full 40-char a3d7dca2... commit ID; add post-deploy checks that live is unchanged and preview serves the stamped version.json; restore v5 safety steps ($ErrorActionPreference='Stop', Set-Location repo root, checked folder removal, no blind force-delete).
C1 (CoS correction, not charged): only 166 coins + 1 medal have a displayable image URL; 1,047 records hold a bare file name, so ~2,799 coins still show "No photo yet". State this and cover the 1,047 (separately gated filename-to-URL step or in the Chunk 2 image plan); the current Chunk 2 search misses 81 of them.

Return DONE with file name, byte size and SHA-256 of the exact on-disk file.
