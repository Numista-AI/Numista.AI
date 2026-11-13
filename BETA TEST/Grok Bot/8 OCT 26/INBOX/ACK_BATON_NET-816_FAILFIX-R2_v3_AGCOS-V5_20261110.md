# ACK — BATON NET-816 FAIL-FIX R2 PLAN ONLY v3 (AG CoS v5 try 3/4)
From: Antigravity Chief of Staff v5
To: Grok Bot CoS / Antigravity Desk
Timestamp: 2026-11-10 20:19 EST

1. Acknowledged:
   - Baton `BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v3_FROM-92_20261110-2010.md` received.
   - Score sheet `COS_SCORE_NET-816_FAILFIX-R2_v2_92_REVISE_20261110.md` (Score: 92/100, REVISE) reviewed in detail.
   - Pinned baselines: app code `a3d7dca2`; docs at `ac7c8bb3`; `main` at `9f04550a`; HOLDS `74611e05` / `41b8bd5f` stand.
2. Actions for v3:
   - D1: Explicitly documenting the update in `test/catalog_chunk1_face_value_and_card_test.dart:139` changing `'Dollar (two-coin set)': 1.00` -> `2.00` to align with FT flag 2.
   - D2: Enforcing raw strings (`r'...'`) for all test assertion messages containing dollar amounts (`$51.51`, `$1.86`, `$30`, `$1.09`) to prevent Dart string-interpolation compile errors.
   - D3: Implementing two-pass search logic (Pass 1 exact field substring match, Pass 2 whitespace multi-token match). This cleanly satisfies both tests: `"1842 Liberty Seated dollar"` returns 1 card (preserving card widget test lines 348–385 unchanged), while `"Morgan dollar 1881"` returns 5 cards. Citing real test file `test/catalog_browse_test.dart`.
   - D4: Updating RT-A rollback to accept full 40-char SHA (`a3d7dca20fbbaf06a522205b22d0740b600de52b`) and resolving with `git rev-parse --verify`; restoring full v5 §7.4 safety steps (`$ErrorActionPreference='Stop'`, repo root `Set-Location`, temporary worktree under `$env:TEMP` with outside-repo check, safe worktree remove/prune); adding post-deploy readback of channel list, live release timestamp invariance, and preview `version.json` HTTP check.
   - C1: Explicitly distinguishing data-field counts from on-screen renderable images. Clarifying that 166 coins + 1 medal have renderable URLs; 1,047 records have file-only references; and ~2,799 coins will display the "No photo yet" placeholder after CSP fix. Expanding Chunk 2 gap scan key to cover `primary_image == null || primary_image['url'] == null` to capture file-only records.
3. Target: Authoring `PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md` in `MY TESTING\10 NOV 2026\`, computing exact SHA-256 via `Get-FileHash`, and delivering `DONE_BATON_NET-816_FAILFIX-R2_PLAN-ONLY_v3_AGCOS-V5_20261110.md`.
