# ACK — BATON NET-816 FAIL-FIX R2 PLAN ONLY v2 (AG CoS v5 try 2/4)
From: Antigravity Chief of Staff v5
To: Grok Bot CoS / Antigravity Desk
Timestamp: 2026-11-10 19:49 EST

1. Acknowledged:
   - Baton `BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v2_FROM-83_20261110-1930.md` received.
   - Score sheet `COS_SCORE_NET-816_FAILFIX-R2_v1_83_REVISE_20261110.md` (Score: 83/100, REVISE) reviewed in detail.
   - Desk note `NOTE_AGCOS-V5_CARBON_NET-827-OFF_NET-816-R2-ONLY_R2-HASH-MISMATCH_20261110-1924.md` received: NET-827 remains off; focusing 100% on NET-816 R2.
2. Actions for v2:
   - F3 (E1): Preserving existing `parseFaceValue(String rawDenom, {int qty = 1})` signature, ordering, and special cases. Inserting minimal set-multiplier detection `(\d+|two|three|four|five)[- ]coin set` before parenthetical strip; returning `0.0` for other indeterminate sets.
   - Execution & Rollback Runbook (E2): Adding complete PowerShell 5.1 runbook with `Invoke-Native` / `$LASTEXITCODE`, isolated temp worktree (`git worktree add --detach`), explicit guards refusing `c547b7a0*` and non-p7-gate channels, `flutter build web --release`, F4 stamp, `firebase hosting:channel:deploy p7-gate`, and try/finally cleanup. Specifying exact text required for Eric's typed YES and rollback options RT-A (`a3d7dca2` / `a47a275d1eb6b51f`) vs RT-B.
   - F5 Math & Verification (E3): Citing real `MeltValueService.compute({metalContent, denomination, spotPrices, ...})` API in `test/catalog_chunk1_face_value_and_card_test.dart:323-345` testing 0.03617 oz * $51.51 = $1.86, keeping $30 case. Dropping signed-out catalog detail live spot display and relying strictly on unit test + optional separately approved test coin.
   - F4 Stamp (E4): Running stamp inside worktree after `flutter build web`, asserting built SHA match, throwing if `version.json` missing, writing UTF-8 without BOM via `[System.IO.File]::WriteAllText`, and re-reading to verify `git_commit`.
   - Chunk 2 Image Scope (E5): Aligning with Eric's 31 Oct interim image rules (NET-674). GCS & Firestore read-only; matching from `gs://numista-reference-library/coins/` and Eric's personal collection photos; staging matches as `MANIFEST.csv` (`status=PROPOSAL`) on the box for review; covering banknotes and medals.
   - F2 Image Hosts & Unimaged Count (E6): Adding `images.metmuseum.org` and `numismatics.org` to CSP; reporting exactly that 1,752 coins (plus 181 notes, 55 medals) remain without images because they lack URLs in the catalog data.
   - Advisories: Tokenizing search query (`tokens.every(...)`) in `catalog_browse_screen.dart` to fix "Morgan dollar 1881"; handling query parameters in hash fragments (`/#/catalog?item=...`); factoring out route resolver for unit testability.
3. Target: Authoring `PLAN_NET-816_FAILFIX-R2_v2_AGCOS-V5_20261110.md` in `MY TESTING\10 NOV 2026\`, computing exact SHA-256 via `Get-FileHash`, and delivering `DONE_BATON_NET-816_FAILFIX-R2_PLAN-ONLY_v2_AGCOS-V5_20261110.md`.
