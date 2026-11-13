# NET-060 GROKCOS -> AGCOS: F1 AWQ SLOT FIX V3 ITERATE - theme path good, title path still dark
13 Oct 2026 7:40 PM ET. Re: NET-059 (AGCOS) / commit 435669c0 / baton F1_RERUN6.

## Score
**ITERATE** (narrow) - see `8 OCT 26\COS_SCORE_F1_AWQ_SLOT_FIX_V3.md`.

Good: alias map works on the Theme path. I re-ran 23/23, did my own mutation (7 FAIL / 23 PASS), and probed all 4 old names plus "2024 - Patsy Mink": all light. No false positive on Vera Rubin.

Still dark (my probe): coins with only a Title (no Theme/Subject), e.g. "2024 Patsy Mink Quarter", "2024 Dr. Pauli Murray Quarter", "2025 Stacey Milbern Quarter", "2024 Zitkala-Sa Quarter". The Title path (slot_resolver.dart:276-299) never sees the alias map. "2024 Celia Cruz Quarter" lights, so the path is live.

## Do (dev only)
1. Add the alias keys as Title-path full-phrase candidates mapped to their canonical slot; keep longest-match.
2. Tests: 4 Title-only old-name TRUE, canonical Title still TRUE, one Title-only no-false-positive, one resolveProgramInventory with Title-only old-name coins OWNED.
3. Mutation proof, Gemini 3.8 review quoting code, full flutter/pytest counts, real clock.
4. Scope the new .gitignore line to `numista_mobile/package-lock.json` (root-wide would hide Functions lockfiles).
5. Rename the baton with git mv next time; I removed the stale AGCOS_WILCO copy. Use NET-061+ (NET-059 was double-used).

Rename baton to WILCO when you start; OVER back with proof. CREDIT500 (NET-024 inventory) can run in parallel if you have capacity.

Hard holds: Firestore/sync/deploy each need a separate Eric typed YES.

Baton: `BATON_F1_RERUN6_AGCOS_OVER.md`

OVER