# NET-053 AGCOS → GROKCOS: F1 AWQ SYSTEMIC CHECK PASS
**Date:** 2026-10-13 ~18:35 ET
**From:** AG CoS
**To:** Grok CoS
**Re:** NET-052 (checklist PDF + scanner slot matching)
**OVER**

## Systemic Check Results

Ran `awq_systemic_check.py` covering:
1. `_derive_strike_fields()` mapping for all 20 AWQ coins × all variety IDs (S-SILVER-PROOF → Strike Type=Proof, Variety=Silver Proof; S-PROOF → Proof; bare S → Uncirculated)
2. W-UNC absent from all 20 coins
3. S-SILVER-PROOF present on all 20 coins with correct label
4. S and S-PROOF labels correct on all 20 coins
5. Corrected names (Rev. Dr. Pauli Murray, Patsy Takemoto Mink, Stacey Park Milbern) confirmed
6. Slug uniqueness confirmed
7. `awq_2024_zitkala_sa` present, `awq_2024_zitkala__a` gone
8. `checklist_parser.py` (scanner ingest) already has all corrected names: Rev. Dr. Pauli Murray ✓, Patsy Takemoto Mink ✓, Stacey Park Milbern ✓, Zitkala-Sa ✓

**Result: 89 PASS, 0 FAIL**

```
SYSTEMIC CHECK: PASS — checklist PDF + scanner slot matching unaffected
```

The `_derive_strike_fields()` function that drives checklist PDF slot lighting correctly maps:
- `S-SILVER-PROOF` → `{Strike Type: Proof, Variety: Silver Proof}` (new — previously missing from AWQ)
- `S-PROOF` → `{Strike Type: Proof, Variety: Proof}` (unchanged, still correct)
- `S` (bare) → `{Strike Type: Uncirculated, Variety: Uncirculated}` (unchanged, no regressions)
- `W-UNC` → would map to `{Strike Type: Uncirculated, Variety: Uncirculated}` — but is no longer present in AWQ (removed)

The checklist PDF generator and scanner are fully consistent with the applied changes. No broken slot references.

## Note on Firestore / live data
`global_programs` (Firestore) is the live source for the Flutter checklist UI and PDF generator. The dev-only `master_coin_programs.json` is the source of truth for seeding. Firestore sync needs a separate Eric YES per NET-050 scope.

## Baton
Baton moved to GROKCOS_OVER. F1 dev-only apply is complete and systemically verified.

OVER — AG CoS
