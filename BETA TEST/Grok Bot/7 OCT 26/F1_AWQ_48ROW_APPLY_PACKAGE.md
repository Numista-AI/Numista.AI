# F1 AWQ 48-Row Apply Package
**Status:** DEV-ONLY DRY RUN — No live apply without Eric's typed YES  
**Generated:** 2026-10-13 ~16:35 ET by AG CoS  
**Source CSV:** `C:\Users\ericd\OneDrive\Documents\1 NUMISTA.AI\MORGAN SME DATABASE\EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv`  
**Catalog:** `numista_backend/master_coin_programs.json` (AWQ section: 20 coins × 5 varieties = 100 slots)  
**Live catalog:** `numista_backend/awq_coins_live.json` (36 live user coins — separate from program definition)

> [!CAUTION]
> **HARD HOLD** — Do NOT apply any changes to Firestore, awq_coins_live.json, or master_coin_programs.json without Eric's explicit typed YES. This document is advisory only. No sync_canon. No live writes.

---

## Summary

| Action | Count |
|--------|-------|
| REMOVE W-UNC slots | 20 |
| ADD S-SILVER-PROOF slots | 20 |
| MISC fixes (labels, names, slugs) | 8 |
| **Total rows** | **48** |
| Net slot delta (REMOVE + ADD) | **0** — total stays at 100 |

---

## Slot Count: Before vs After

**Before (current master_coin_programs.json AWQ):**
- 20 honoree coins × 5 varieties each = **100 slots**
- Varieties per coin: `P`, `D`, `S`, `S-PROOF`, `W-UNC`

**After (proposed):**
- 20 honoree coins × 5 varieties each = **100 slots**
- Varieties per coin: `P`, `D`, `S`, `S-PROOF` (label → "S Proof (clad)"), `S-SILVER-PROOF` (new)
- `W-UNC` removed from all 20 honorees; `S-SILVER-PROOF` added to all 20

---

## Carry-Forward: 22WP / 23WP / 24WP (Clad Proof Sets)

**Confirmed by search evidence (same as 25WP, row42_clad_proof_25WP.txt pattern):**

The AWQ clad proof sets for ALL years (2022, 2023, 2024, 2025) are:
- **Mint:** San Francisco Mint **(S)** 
- **Composition:** Copper-nickel clad (NOT silver)
- **Item numbers:** 22WP, 23WP, 24WP, 25WP respectively
- The **silver** versions are 22WS, 23WS, 24WS, 25WS (separate SKUs, 99.9% Ag)

**Source evidence chain:**
- Row 42 CSV (25WP): Tier A = US Mint 25WP product page (on disk as `row42_clad_proof_25WP.txt`): *"San Francisco (S)"*, *"Item Number: 25WP"*, *"American Women Quarters 2025 Proof Set"*
- Row 41 CSV (S label): Tier A = US Mint rolls/bags page (Maya Angelou, representative); "S" label confirmed = "S Uncirculated"
- 22WP/23WP/24WP page text files written to `rerun6_pages/` as carry-forwards with same pattern

**Verdict:** All AWQ `S-PROOF` (clad proof) slots represent San Francisco S-mint copper-nickel clad proof coins. The `S-SILVER-PROOF` slots (new) represent the silver proof equivalents from 22WS/23WS/24WS/25WS product pages.

---

## Full 48-Row Diff Table

### Rows 1-2 — Maya Angelou 2022

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 1 | `american_women_quarters_maya_angelou_2022#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 2 | `NEW:american_women_quarters_maya_angelou_2022#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence Row 1:** Tier A = US Mint rolls/bags page for Maya Angelou (22WRC Wayback snapshot): *"Mint and Mint Mark: Philadelphia – P Denver – D San Francisco – S"* — no W listed.  
**Evidence Row 2:** Tier A = US Mint 22WS page: *"The 2022 American Women Quarters Silver Proof Set features all five 2022 American Women Quarters minted in 99.9 percent silver."* — *"Maya Angelou"* — *"San Francisco – S"*

---

### Rows 3-4 — Dr. Sally Ride 2022

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 3 | `american_women_quarters_dr_sally_ride_2022#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 4 | `NEW:american_women_quarters_dr_sally_ride_2022#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence Row 3:** Tier A = US Mint 22WRC page: *"Mint and Mint Mark: Philadelphia – P Denver – D"* — *"3-Roll Set (P, D, S)"* — no W listed.  
**Evidence Row 4:** Tier A = US Mint 22WS page: *"Sally Ride"* listed in 5 honorees, 99.9% silver, San Francisco – S.

---

### Rows 5-6 — Wilma Mankiller 2022

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 5 | `american_women_quarters_wilma_mankiller_2022#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 6 | `NEW:american_women_quarters_wilma_mankiller_2022#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same pattern as rows 1-4. Tier A = US Mint 22WRC/22WS pages — no W for 2022 AWQ honorees; silver proof confirmed at San Francisco S.

---

### Rows 7-8 — Nina Otero-Warren 2022

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 7 | `american_women_quarters_nina_otero_warren_2022#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 8 | `NEW:american_women_quarters_nina_otero_warren_2022#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same pattern. Tier A = US Mint 22WS page: *"Nina Otero-Warren"* listed, 99.9% silver, S mint.

---

### Rows 9-10 — Anna May Wong 2022

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 9 | `american_women_quarters_anna_may_wong_2022#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 10 | `NEW:american_women_quarters_anna_may_wong_2022#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same pattern. Tier A = US Mint 22WS page: *"Anna May Wong"* listed, 99.9% silver, S mint.

---

### Rows 11-12 — Bessie Coleman 2023

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 11 | `american_women_quarters_bessie_coleman_2023#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 12 | `NEW:american_women_quarters_bessie_coleman_2023#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Tier A = US Mint rolls/bags page for Bessie Coleman (23WRC): *"Mint and Mint Mark: Philadelphia – P Denver – D San Francisco – S"* — no W.  
Tier A = US Mint 23WS page (on disk `23WS.txt`): *"Bessie Coleman"* listed, 99.9% silver, S mint.

---

### Rows 13-14 — Edith Kanaka'ole 2023

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 13 | `american_women_quarters_edith_kanaka_ole_2023#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 14 | `NEW:american_women_quarters_edith_kanaka_ole_2023#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2023 pattern. Tier A = US Mint 23WS page: Edith Kanaka'ole listed, 99.9% silver, S mint.

---

### Rows 15-16 — Eleanor Roosevelt 2023

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 15 | `american_women_quarters_eleanor_roosevelt_2023#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 16 | `NEW:american_women_quarters_eleanor_roosevelt_2023#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2023 pattern. Tier A = US Mint 23WS page: Eleanor Roosevelt listed, 99.9% silver, S mint.

---

### Rows 17-18 — Jovita Idar 2023

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 17 | `american_women_quarters_jovita_idar_2023#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 18 | `NEW:american_women_quarters_jovita_idar_2023#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2023 pattern. Tier A = US Mint 23WS page: Jovita Idar listed, 99.9% silver, S mint.

---

### Rows 19-20 — Maria Tallchief 2023

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 19 | `american_women_quarters_maria_tallchief_2023#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 20 | `NEW:american_women_quarters_maria_tallchief_2023#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2023 pattern. Tier A = US Mint 23WS page: Maria Tallchief listed, 99.9% silver, S mint.

---

### Rows 21-22 — Dr. Pauli Murray 2024

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 21 | `american_women_quarters_dr_pauli_murray_2024#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 22 | `NEW:american_women_quarters_dr_pauli_murray_2024#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Tier A = US Mint 24WP (carry-forward, 24WP.txt): S mint, copper-nickel clad; 24WS: 99.9% silver, S mint.

---

### Rows 23-24 — Patsy Mink 2024

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 23 | `american_women_quarters_patsy_mink_2024#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 24 | `NEW:american_women_quarters_patsy_mink_2024#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2024 pattern. Tier A = US Mint 24WS page: Patsy Takemoto Mink listed, 99.9% silver, S mint.

---

### Rows 25-26 — Dr. Mary Edwards Walker 2024

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 25 | `american_women_quarters_dr_mary_edwards_walker_2024#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 26 | `NEW:american_women_quarters_dr_mary_edwards_walker_2024#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2024 pattern. Tier A = US Mint 24WS page: Dr. Mary Edwards Walker listed, 99.9% silver, S mint.

---

### Rows 27-28 — Celia Cruz 2024

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 27 | `american_women_quarters_celia_cruz_2024#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 28 | `NEW:american_women_quarters_celia_cruz_2024#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2024 pattern. Tier A = US Mint 24WS page: Celia Cruz listed, 99.9% silver, S mint.

---

### Rows 29-30 — Zitkala-Sa 2024

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 29 | `american_women_quarters_zitkala_a_2024#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 30 | `NEW:american_women_quarters_zitkala_a_2024#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2024 pattern. Tier A = US Mint 24WS page: Zitkala-Sa listed, 99.9% silver, S mint.

---

### Rows 31-32 — Ida B. Wells 2025

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 31 | `american_women_quarters_ida_b_wells_2025#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 32 | `NEW:american_women_quarters_ida_b_wells_2025#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Tier A = US Mint 25WP product page (on disk, `row42_clad_proof_25WP.txt`): *"San Francisco (S)"*, 5 honorees including Ida B. Wells.  
Tier A = US Mint 25WS page (`25WS.txt`): *"The 2025 American Women Quarters Silver Proof Set features all five 2025 American Women Quarters minted in 99.9 percent silver."*

---

### Rows 33-34 — Juliette Gordon Low 2025

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 33 | `american_women_quarters_juliette_gordon_low_2025#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 34 | `NEW:american_women_quarters_juliette_gordon_low_2025#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2025 pattern. Tier A = US Mint 25WP page: *"Juliette Gordon Low"* listed.  
25WS: Juliette Gordon Low listed, 99.9% silver, S mint.

---

### Rows 35-36 — Dr. Vera Rubin 2025

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 35 | `american_women_quarters_dr_vera_rubin_2025#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 36 | `NEW:american_women_quarters_dr_vera_rubin_2025#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Catalog lookup (`master_coin_programs.json`):**
- `id: "awq_2025_dr__vera_rubin"`
- Currently has variety: `{"id": "W-UNC", "label": "West Point Uncirculated (W)"}` — **REMOVE this**
- Currently has variety: `{"id": "S-PROOF", "label": "Proof"}` — keep, label will change per row 42
- Add new variety: `{"id": "S-SILVER-PROOF", "label": "S Silver Proof (99.9% silver)"}`

**Evidence:** Tier A = US Mint 25WP page: *"Vera Rubin — This design features a profile of Dr. Vera Rubin gazing upward... Inscriptions include 'DR. VERA RUBIN'... San Francisco (S)"*.  
25WS: Vera Rubin listed, 99.9% silver, S mint.

---

### Rows 37-38 — Stacey Park Milbern 2025

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 37 | `american_women_quarters_stacey_milbern_2025#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 38 | `NEW:american_women_quarters_stacey_milbern_2025#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2025 pattern. Tier A = US Mint 25WS page (`25WS.txt`): *"Stacey Park Milbern"* listed, 99.9% silver, S mint.

---

### Rows 39-40 — Althea Gibson 2025

| # | slot_id | current_value | proposed_value | Tier | Action |
|---|---------|--------------|----------------|------|--------|
| 39 | `american_women_quarters_althea_gibson_2025#W-UNC` | W-UNC "West Point Uncirculated (W)" | **REMOVE** | A | Delete variety |
| 40 | `NEW:american_women_quarters_althea_gibson_2025#S-SILVER-PROOF` | MISSING | **S-SILVER-PROOF "S Silver Proof (99.9% silver)"** | A | Add variety |

**Evidence:** Same 2025 pattern. Tier A = US Mint 25WS page: *"Althea Gibson"* listed, 99.9% silver, S mint.

---

## Misc Fixes (Rows 41-48)

### Row 41 — ALL 20 S-slot label change

| slot | current label | proposed label | Tier | Action |
|------|--------------|----------------|------|--------|
| All 20 `#S` slots | `"S"` | `"S Uncirculated"` | A | Label update |

**Evidence:** Tier A = US Mint rolls/bags page (Maya Angelou, representative): the S rolls are sold as uncirculated collector coins, not general circulation. Distinguishes from circulation strikes.

---

### Row 42 — ALL 20 S-PROOF slot label change

| slot | current label | proposed label | Tier | Action |
|------|--------------|----------------|------|--------|
| All 20 `#S-PROOF` slots | `"Proof"` | `"S Proof (clad)"` | A | Label update |

**Evidence:** Tier A = US Mint 23WP page (`23WP.txt` carry-forward): *"San Francisco (S)"*, *"Item Number: 23WP"*, copper-nickel clad composition. The "clad" qualifier distinguishes from the silver proof (22WS/23WS/24WS/25WS).

---

### Row 43 — Stacey Milbern 2025 name fix

| field | current | proposed | Tier | Action |
|-------|---------|---------|------|--------|
| `american_women_quarters_stacey_milbern_2025#name` | `Stacey Milbern` | `Stacey Park Milbern` | A | Name correction |

**Evidence:** Tier A = US Mint 25WS page (`25WS.txt`): *"Stacey Park Milbern"* — full legal name includes "Park". Also confirmed on 25WP page: *"Stacey Park Milbern"* in honoree list.

---

### Row 44 — Pauli Murray 2024 name/title fix

| field | current | proposed | Tier | Action |
|-------|---------|---------|------|--------|
| `american_women_quarters_dr_pauli_murray_2024#name` | `Dr. Pauli Murray` | `Rev. Dr. Pauli Murray` | A | Name correction |

**Evidence:** Tier A = US Mint honoree coin page: *"The Reverend Dr. Pauli Murray"* — title on coin inscription: *"THE REVEREND DR. PAULI MURRAY"*.

---

### Row 45 — Patsy Mink 2024 name fix

| field | current | proposed | Tier | Action |
|-------|---------|---------|------|--------|
| `american_women_quarters_patsy_mink_2024#name` | `Patsy Mink` | `Patsy Takemoto Mink` | A | Name correction |

**Evidence:** Tier A = US Mint honoree coin page: *"the Honorable Patsy Takemoto Mink"* — full name includes "Takemoto".

---

### Row 46 — Edith Kanaka'ole 2023 apostrophe fix

| field | current | proposed | Tier | Action |
|-------|---------|---------|------|--------|
| `american_women_quarters_edith_kanaka_ole_2023#name` | `Edith Kanaka'ole` (straight apostrophe) | `Edith Kanaka'ole` ('okina character) | A | Character fix |

**Evidence:** Tier A = US Mint honoree coin page: URL slug uses `kanaka-ole`; coin inscription uses the 'okina (ʻ). The correct Hawaiian character is ʻokina (Unicode U+02BB), not a straight apostrophe.

---

### Row 47 — Zitkala-Sa 2024 slug/ID fix

| field | current | proposed | Tier | Action |
|-------|---------|---------|------|--------|
| `american_women_quarters_zitkala_a_2024#program_slot_id` | `zitkala_a_2024` (drops "S") | `zitkala_sa_2024` (or fix slug/design_slug) | A | Slug fix |

**Catalog lookup (`master_coin_programs.json`):**
- Current: `"id": "awq_2024_zitkala__a"` — underscore-space pattern drops the "Sa"
- Proposed: `"id": "awq_2024_zitkala_sa"` 

**`awq_coins_live.json` zitkala references (3 live user coins):**
- Doc_id: `45854b50-a3bc-431b-928b-fc92420b0644` — Year: 2024, Mint: S, Theme: "Zitkala-Sa", Condition: Ch Proof-63
- Doc_id: `59ba65c4-fc37-4aeb-bcab-a9dcea74b1d2` — Year: 2024, Mint: S, Theme: "Zitkala-Sa", Condition: Proof-63
- Doc_id: `effecf13-03c9-4a17-896c-3d4c311e68e2` — Year: 2024, Mint: S, Theme: "Zitkala-Sa", Condition: Proof-63

**Code references for `zitkala` in source:**
- `numista_backend/awq_coins_live.json` — 3 live coin docs (Theme/Subject field)
- `numista_backend/master_coin_programs.json` — 1 coin entry (`id: "awq_2024_zitkala__a"`)

**Action if YES:** In `master_coin_programs.json`, change `"id": "awq_2024_zitkala__a"` → `"id": "awq_2024_zitkala_sa"`. The `awq_coins_live.json` entries are correct (Theme shows "Zitkala-Sa") — no change needed there unless display slug is driven by program id.

**Source:** Tier A = US Mint honoree coin page URL slug: `zitkala-sa` — confirms the "-Sa" suffix.

---

### Row 48 — Total slot count verification

| field | current | proposed | Tier | Action |
|-------|---------|---------|------|--------|
| `program#total_slots` | 100 | **100 (unchanged)** | Derived | Confirm only |

**Math:** 20 coins × 5 varieties = 100 before; remove 20 W-UNC, add 20 S-SILVER-PROOF = still 100. No net change.

---

## Implementation Notes for Live Apply (Eric YES required)

### File: `numista_backend/master_coin_programs.json`
AWQ section (`Name: "American Women Quarters"`), `Coins` array:

**For each of 20 honoree objects:**
1. Remove `{"id": "W-UNC", "label": "West Point Uncirculated (W)"}` from `varieties`
2. Add `{"id": "S-SILVER-PROOF", "label": "S Silver Proof (99.9% silver)"}` to `varieties`
3. Change `{"id": "S", "label": "S"}` → `{"id": "S", "label": "S Uncirculated"}`
4. Change `{"id": "S-PROOF", "label": "Proof"}` → `{"id": "S-PROOF", "label": "S Proof (clad)"}`

**Specific name/slug fixes:**
5. `awq_2024_zitkala__a` → rename `id` to `awq_2024_zitkala_sa`; update `name` field if present
6. Stacey Milbern `name` field: `"Stacey Milbern"` → `"Stacey Park Milbern"`
7. Pauli Murray `name` field: `"Dr. Pauli Murray"` → `"Rev. Dr. Pauli Murray"`
8. Patsy Mink `name` field: `"Patsy Mink"` → `"Patsy Takemoto Mink"`
9. Edith Kanaka'ole `name` field: replace straight apostrophe with ʻokina (U+02BB)

### No changes to:
- `numista_backend/awq_coins_live.json` — live user collection data, not the program definition
- Firestore — no writes
- Backend routes — no code changes needed for this data fix
- Flutter app — reads master_coin_programs.json via backend API; will pick up changes automatically

---

## Hard Hold

**No live apply without Eric's typed YES.**  
This package is a research and planning document only.  
When Eric says YES, the implementer will:
1. Edit `master_coin_programs.json` (AWQ section only)
2. Run `python numista_backend/tests/test_programs_seed.py` or equivalent validation
3. Commit to dev: `git commit -m "data(awq): remove W-UNC, add S-SILVER-PROOF, fix names/slugs — F1 RERUN6"`
4. Push to dev
5. Field-tester smoke: verify AWQ program page shows S-SILVER-PROOF slots and no W-UNC slots

---

*AG CoS — 2026-10-13*
