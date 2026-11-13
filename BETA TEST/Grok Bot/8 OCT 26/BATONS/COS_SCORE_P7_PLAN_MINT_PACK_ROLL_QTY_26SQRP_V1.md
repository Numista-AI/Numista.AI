# COS_SCORE -- PLAN.v1 Mint pack/roll Qty expand (26SQRP) -- AG CoS submission
**Scorer:** Grok CoS (Desk, handoff watch)  **Filed:** Sun 25 Oct 2026 ~9:15 AM ET
**Ref:** NET-502 (AGCOS), `BATONS\PLAN_MINT_PACK_ROLL_QTY_26SQRP_V1_AGCOS.md`, CoS brief `PLAN_MINT_PACK_ROLL_QTY_26SQRP_V1.md`
**Type:** Plan score (no code yet -> GEMINI38_REVIEW required at EXECUTE_DONE, not now)

## Score: 8/10 -- ACCEPT WITH CONDITIONS (build may start on dev)
Covers all 5 Monday acceptance items; scope/non-goals match the CoS brief; live stays held for Eric YES.

## Binding conditions (C1-C6) for the build
- **C1 Cost semantics (most important).** Backend already has `cost_total` vs `cost_per_coin` split (main.py ~L5755-6075). State and test which one the Hub row carries once Quantity=25: either line total $61.00 with Qty 25, or per-coin $2.44 x 25. Must NOT end as $61.00 per coin x 25 (= $1,525 basis). Add a pytest assert on the resulting cost field. S&H ($70.95 total) stays note-only unless trivial (brief).
- **C2 Expansion guard.** `current_qty < pack_qty` multiplies any 2..24 (e.g. a mis-read 24 -> 600). Only multiply when qty is a plausible Ship-roll count (<= 10, or from Ship column) AND not already a multiple of pack_qty; else leave and add a note. Must be idempotent if enrich runs twice (add `pack_expanded` marker or equivalent).
- **C3 Prompt alignment.** Brief step 3 (LLM prompt line for 26SQRP, main.py ~L2162) is missing from Plan.v1. Either leave prompt saying Ship count and expand only in enrich, or change prompt -- not both without the C2 guard. Say which.
- **C4 Systemic (Eric rule 3 Oct).** Audit every catalog SKU that is a roll/bag/pack of identical coins and list them (add `pack_quantity` where data allows, else follow-up list). Multi-coin SETS of different coins (proof/mint sets) must NOT pack-expand. Also grep every consumer of `coins_identified` / Done count (Add Coins, CSV/Excel import, scanner) so the sum change doesn't break them.
- **C5 Tests.** Add: 1 roll -> 25; 2 rolls -> 50; invoice already 25 -> 25 (no re-multiply); non-pack SKU unchanged; V8.18.15i Nx-line rollup regression; cost assert (C1).
- **C6 Branch.** Name ONE branch (plan says `dev / p7-v8.9`). Preview + FT with Eric's PDF; >2 files -> GEMINI38_REVIEW with code quoted; then CoS build score. No main merge / Cloud Run shift without Eric typed YES (WAKE never authorizes deploy).

## Argon
Argon review optional in parallel; if Argon files a conflicting finding, CoS reconciles before build score.

GROKCOS OUT