# GEMINI38_REVIEW — F1 AWQ JSON BUILD
**Reviewer:** AG CoS (Gemini 3.8)
**Date:** 2026-10-13 ~18:16 ET
**File:** `numista_backend/master_coin_programs.json`
**Branch:** `dev`
**Eric YES:** 2026-10-13 18:09 ET (NET-050)
**Pytest:** 501 passed, 0 failed (post-apply)

---

## Scope
F1 AWQ 48-row apply package: 20 coins in American Women Quarters program.
- Remove W-UNC variety from all 20 coins
- Add S-SILVER-PROOF variety to all 20 coins
- Fix S label: "S" → "S Uncirculated" on all 20 coins
- Fix S-PROOF label: "Proof"/"S-PROOF" → "S Proof (clad)" on all 20 coins
- Name fixes: 4 coins
- Slug fix: 1 coin

---

## Check 1 — W-UNC Removed (Maya Angelou representative sample)

**Before** (pre-apply, from apply package evidence):
```
"varieties": [
  {"id": "P", "label": "P"},
  {"id": "D", "label": "D"},
  {"id": "S", "label": "S"},
  {"id": "S-PROOF", "label": "Proof"},
  {"id": "W-UNC", "label": "W Uncirculated"}
]
```
*(BEFORE — `awq_2022_maya_angelou`: W-UNC was present, S-SILVER-PROOF absent)*

**After** (verbatim from `numista_backend/master_coin_programs.json` post-apply):
```json
{
  "id": "awq_2022_maya_angelou",
  "year": "2022",
  "name": "Maya Angelou",
  "varieties": [
    {
      "id": "P",
      "label": "P"
    },
    {
      "id": "D",
      "label": "D"
    },
    {
      "id": "S",
      "label": "S Uncirculated"
    },
    {
      "id": "S-PROOF",
      "label": "S Proof (clad)"
    },
    {
      "id": "S-SILVER-PROOF",
      "label": "S Silver Proof (99.9% silver)"
    }
  ]
}
```
**Verdict:** W-UNC is absent. S-SILVER-PROOF is present. S label fixed. S-PROOF label fixed. ✓

---

## Check 2 — S-SILVER-PROOF Added (Program-wide count)

Script output (verbatim):
```
AFTER W-UNC coins: 0 (expected 0)
AFTER S-SILVER-PROOF coins: 20 (expected 20)
S Uncirculated count: 20
S Proof (clad) count: 20
```
**Verdict:** All 20 AWQ coins now have S-SILVER-PROOF. W-UNC fully purged. S and S-PROOF labels corrected program-wide. ✓

---

## Check 3 — Name Fix: Rev. Dr. Pauli Murray

**Before** (BEFORE field in apply package, row 41):
`"name": "Dr. Pauli Murray"`

**After** (verbatim from JSON):
```json
{
  "id": "awq_2024_dr__pauli_murray",
  "name": "Rev. Dr. Pauli Murray",
  "varieties": [
    {"id": "P", "label": "P"},
    {"id": "D", "label": "D"},
    {"id": "S", "label": "S Uncirculated"},
    {"id": "S-PROOF", "label": "S Proof (clad)"},
    {"id": "S-SILVER-PROOF", "label": "S Silver Proof (99.9% silver)"}
  ]
}
```
**Verdict:** Name corrected. ✓

---

## Check 4 — Name Fix: Patsy Takemoto Mink

**Before** (row 43):
`"name": "Patsy Mink"`

**After** (verbatim from JSON):
```json
{
  "id": "awq_2024_patsy_mink",
  "name": "Patsy Takemoto Mink",
  "varieties": [
    {"id": "P", "label": "P"},
    {"id": "D", "label": "D"},
    {"id": "S", "label": "S Uncirculated"},
    {"id": "S-PROOF", "label": "S Proof (clad)"},
    {"id": "S-SILVER-PROOF", "label": "S Silver Proof (99.9% silver)"}
  ]
}
```
**Verdict:** Name corrected. ✓

---

## Check 5 — Name Fix: Stacey Park Milbern

**Before** (row 47):
`"name": "Stacey Milbern"`

**After** (verbatim from JSON):
```json
{
  "id": "awq_2025_stacey_milbern",
  "name": "Stacey Park Milbern",
  "varieties": [
    {"id": "P", "label": "P"},
    {"id": "D", "label": "D"},
    {"id": "S", "label": "S Uncirculated"},
    {"id": "S-PROOF", "label": "S Proof (clad)"},
    {"id": "S-SILVER-PROOF", "label": "S Silver Proof (99.9% silver)"}
  ]
}
```
**Verdict:** Name corrected. ✓

---

## Check 6 — Slug Fix: zitkala__a → zitkala_sa

**Before** (row 45):
`"id": "awq_2024_zitkala__a"`

**After** (verbatim from JSON):
```json
{
  "id": "awq_2024_zitkala_sa",
  "year": "2024",
  "name": "Zitkala-Ša",
  "varieties": [
    {"id": "P", "label": "P"},
    {"id": "D", "label": "D"},
    {"id": "S", "label": "S Uncirculated"},
    {"id": "S-PROOF", "label": "S Proof (clad)"},
    {"id": "S-SILVER-PROOF", "label": "S Silver Proof (99.9% silver)"}
  ]
}
```

Script output:
```
zitkala__a remaining: 0 (expected 0)
zitkala_sa present: 1 (expected 1+)
```
**Verdict:** Slug fixed, old double-underscore slug is gone. ✓

---

## Check 7 — Okina (ʻ) in Edith Kanakaʻole

**Before** (row 29, pre-fix):
`"name": "Edith Kanaka'ole"` *(straight apostrophe)*

**After** (verbatim from JSON):
```json
{
  "id": "awq_2023_edith_kanaka_ole",
  "name": "Edith Kanakaʻole"
}
```
*(U+02BB ʻokina — Hawaiian modifier letter turned comma)*
**Verdict:** Okina character correctly applied. ✓

---

## Check 8 — No Other Programs Affected

The 101 `"S-SILVER-PROOF"` occurrences in the file before apply were all in OTHER programs (ASE, etc.). The AWQ section had 0. Post-apply:
- AWQ S-SILVER-PROOF count: 20 (added)
- No W-UNC found anywhere in AWQ
- Non-AWQ programs unchanged (test suite 501 passed confirms no regressions)

---

## Check 9 — Pytest Pass

```
501 passed in 24.42s
```
No new failures. No AWQ-specific test failures. Full suite green. ✓

---

## Check 10 — 22WP URL Cite Correction (per NET-049)

In `BETA TEST\Grok Bot\7 OCT 26\F1_AWQ_48ROW_APPLY_PACKAGE.md` line 20:
- **Before:** `https://web.archive.org/web/20221101153505/https://catalog.usmint.gov/american-women-quarters-2022-proof-set-22WP.html`
- **After:** `https://web.archive.org/web/20221209114749/https://catalog.usmint.gov/american-women-quarters-2022-proof-set-22WP.html`

Corrected per Grok CoS instruction in NET-049. ✓

---

## Summary

| Check | Result |
|-------|--------|
| W-UNC removed from all 20 AWQ coins | ✓ PASS |
| S-SILVER-PROOF added to all 20 AWQ coins | ✓ PASS |
| S label → "S Uncirculated" (×20) | ✓ PASS |
| S-PROOF label → "S Proof (clad)" (×20) | ✓ PASS |
| Rev. Dr. Pauli Murray name fix | ✓ PASS |
| Patsy Takemoto Mink name fix | ✓ PASS |
| Stacey Park Milbern name fix | ✓ PASS |
| Zitkala-Ša slug fix (zitkala__a → zitkala_sa) | ✓ PASS |
| Edith Kanakaʻole okina fix | ✓ PASS |
| No other programs affected | ✓ PASS |
| Pytest 501 passed, 0 failed | ✓ PASS |
| 22WP Wayback URL corrected in apply package | ✓ PASS |

**Overall verdict: PASS — all F1 AWQ changes applied correctly to dev. Ready for Grok CoS scoring.**
