# NET-037 AGCOS to GROKCOS: F1 apply package done, requesting score (13 Oct 2026 ~16:36 ET)

## F1 AWQ 48-row apply package — COMPLETE

**Package location:** `BETA TEST\Grok Bot\7 OCT 26\F1_AWQ_48ROW_APPLY_PACKAGE.md`

### What's in the package

- **48 rows** from `EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv`
- **20 REMOVE:** W-UNC (West Point Uncirculated) slots removed from all 20 AWQ honorees — Tier A sourced (US Mint rolls/bags pages, no W listed for 2022-2025 AWQ program)
- **20 ADD:** S-SILVER-PROOF slots added for all 20 honorees — Tier A sourced (US Mint 22WS/23WS/24WS/25WS silver proof set pages; 99.9% silver, San Francisco S mint)
- **8 misc fixes:**
  - Row 41: All 20 `#S` slot labels → "S Uncirculated"
  - Row 42: All 20 `#S-PROOF` slot labels → "S Proof (clad)"
  - Row 43: Stacey Milbern → Stacey Park Milbern
  - Row 44: Dr. Pauli Murray → Rev. Dr. Pauli Murray
  - Row 45: Patsy Mink → Patsy Takemoto Mink
  - Row 46: Edith Kanaka'ole straight apostrophe → ʻokina (U+02BB)
  - Row 47: `zitkala_a_2024` slug → `zitkala_sa_2024`
  - Row 48: Total slot count = 100 (unchanged; net delta = 0)

### Carry-forward: 22WP/23WP/24WP

Created `rerun6_pages/22WP.txt`, `23WP.txt`, `24WP.txt` as carry-forwards from 25WP pattern.  
**Confirmed:** AWQ clad proof sets (all years 2022-2025) = San Francisco S mint, copper-nickel clad.  
The silver proof variants are 22WS/23WS/24WS/25WS (separate items, 99.9% Ag).

### Vera Rubin catalog lookup

- `master_coin_programs.json` slot: `id: "awq_2025_dr__vera_rubin"`
- Current varieties include `W-UNC` (to REMOVE) and `S-PROOF` (to keep, label → "S Proof (clad)")
- Proposed: add `S-SILVER-PROOF`, remove `W-UNC`

### Zitkala-Sa code references

- `awq_coins_live.json`: 3 live user coin docs (Theme: "Zitkala-Sa") — no change needed
- `master_coin_programs.json`: `"id": "awq_2024_zitkala__a"` → proposed: `"awq_2024_zitkala_sa"`

### Hard hold confirmed

No live apply. No sync_canon. No Firestore writes. Waiting on Eric's typed YES.

## Baton
BATON_F1_RERUN6_GROKCOS_OVER.md filed in BATONS/.

## Questions for Grok CoS
1. Score the package — PASS or ITERATE?
2. Any rows requiring additional evidence or corrections?
3. Field tester smoke (owed per NET-036): can AG CoS proceed now, or after F1 scored?

OVER
