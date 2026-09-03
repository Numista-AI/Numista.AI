# Westward Journey Nickel Series(tm) — Implementation Plan v1.2-final

**Date:** 2026-09-02
**Status:** READY TO BUILD — waiting for Eric "go"
**Verdict:** ADOPT (Grok v1.2 review). MINOR tweaks applied below. No v1.3.

---

## What Changed from v1.2 (Three Tweaks Only)

### Tweak 1 — C-1: Program wrapper keys corrected to match live file

v1.2 used `Name`, `Id`, `Years`, `Url`, `Category`. Live siblings (Jefferson Nickels,
ATB) use: `Name`, `Years`, `Mint_mark_locations`, `Category`, `Mint_mark_type`,
`Mint_mark_description`. No `Id` or `Url` at the top level. WJNS wrapper now cloned
exactly from the live Jefferson Nickels shape. `Coins[]` children stay lowercase
(`id`, `year`, `name`, `varieties`), matching ATB coin children.

### Tweak 2 — C-1/MF-B: `item_type` removed from all Coins[] entries

`item_type: "circulating"` was not present in any sibling ATB/AWQ/50-State coin
children. Removed from all 4 WJNS coin objects.

### Tweak 3 — MF-C: 2004-S Peace Medal mintage corrected to 2,992,069

Was 2,965,422 (incorrect copy of Keelboat figure). Corrected per PCGS CoinFacts #4155.
PDF generator must also be updated to show 2,992,069 before Eric visual sign-off.

---

## Final Program JSON (ready for re-commit)

```json
{
  "Name": "Westward Journey Nickel Series",
  "Years": "2004-2005",
  "Mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S (Proof) | Philadelphia - P (Satin) | Denver - D (Satin)",
  "Category": "Nickel",
  "Mint_mark_type": "OBVERSE_PORTRAIT",
  "Mint_mark_description": "Look on the FRONT (obverse) of the coin. The mint mark appears to the RIGHT of Jefferson's portrait. 2004 coins use the 1938 Schlag portrait. 2005 coins use a unique one-year-only close-up portrait (Houdon/Fitzgerald) with handwritten Liberty script.",
  "Statutory_authority": "American 5-Cent Coin Design Continuity Act of 2003 (P.L. 108-15; 31 U.S.C. Section 5112(p))",
  "Coins": [
    {
      "year": "2004",
      "name": "Peace Medal",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 361440000},
        {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 372000000},
        {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 2992069,
         "note": "2004 Proof Set. Both Peace Medal and Keelboat S appear in every 2004 Proof Set."}
      ]
    },
    {
      "year": "2004",
      "name": "Keelboat",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 366720000},
        {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 344880000},
        {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 2965422,
         "note": "2004 Proof Set. Both Peace Medal and Keelboat S appear in every 2004 Proof Set."}
      ]
    },
    {
      "year": "2005",
      "name": "American Bison",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)",     "finish": "business_strike", "mintage": 448320000},
        {"id": "D",       "label": "D (Denver)",           "finish": "business_strike", "mintage": 487680000,
         "note": "Per PCGS CoinFacts #4159. Includes Speared Bison die-gouge variety (PCGS FS-901)."},
        {"id": "S-PROOF", "label": "S (Proof)",            "finish": "proof",           "mintage": 3344679,
         "note": "2005 Proof Set. Both Bison and Ocean in View S appear in every 2005 Proof Set."},
        {"id": "P-SATIN", "label": "P (Satin Finish)",     "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only. One lot covers all four 2005 satin slots."},
        {"id": "D-SATIN", "label": "D (Satin Finish)",     "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only. One lot covers all four 2005 satin slots."}
      ]
    },
    {
      "year": "2005",
      "name": "Ocean in View!",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)",     "finish": "business_strike", "mintage": 394080000},
        {"id": "D",       "label": "D (Denver)",           "finish": "business_strike", "mintage": 411120000},
        {"id": "S-PROOF", "label": "S (Proof)",            "finish": "proof",           "mintage": 3344679,
         "note": "2005 Proof Set. Both Bison and Ocean in View S appear in every 2005 Proof Set."},
        {"id": "P-SATIN", "label": "P (Satin Finish)",     "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only. One lot covers all four 2005 satin slots."},
        {"id": "D-SATIN", "label": "D (Satin Finish)",     "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only. One lot covers all four 2005 satin slots."}
      ]
    }
  ]
}
```

---

## Constraints C-1 / C-2 / C-3 (bind the re-commit)

**C-1:** Top-level wrapper keys match live Jefferson Nickels shape exactly
(`Name`, `Years`, `Mint_mark_locations`, `Category`, `Mint_mark_type`,
`Mint_mark_description`). No `Id` or `Url` at wrapper level. `item_type` absent
from all `Coins[]` entries.

**C-2:** Dry-run receipt must show: `westward_journey_nickel_series`, `16 slots`,
Peace Medal S `2992069`, Bison D `487680000`, `item_type` absent from diff.
Two consecutive dry-runs will both print `NEW PROGRAM` because `--execute` is not
run in this ticket. That is correct, not an error.

**C-3:** The diff touches exactly four files — same set as reverted commit 24f755f4:
- `numista_backend/master_coin_programs.json`
- `numista_backend/_scripts/seed_global_programs.py`
- `numista_backend/_scripts/generate_westward_journey_checklist.py`
- `numista_mobile/lib/services/coin_programs_data.dart`

Must NOT touch: jefferson_nickels 2004-2005 rows, any 2025 Jefferson data,
`program_manager_screen.dart`, Dimes files, RAG, model IDs, GCS CLI commands,
any GCS bucket string in code, or anything targeting `main`.

---

## Parked (WJNS-followup — separate ticket, separate conversation)

- 7A: Jefferson Nickels 2004-2005 row cleanup / SlotResolver double-count fix
- 7B: 2025 Jefferson Nickel addition (pending cited mintage source)
- Jefferson Nickels PDF regeneration
- `RELEASE_NOTES.md` update
- GCS upload of PDF
- `seed_global_programs.py --execute` (Firestore write)
- PR to main (deploy conversation `7485fc0a` only, on explicit "Prepare to Deploy")

---

## Known Residual (documented, not fixed here)

A user coin with Year=2005, Denomination=Nickel, Theme=Bison, and no `program_id`
will match `jefferson_nickels` today and will match both `jefferson_nickels` AND
`westward_journey_nickel_series` after the WJNS seed. This double-count is accepted
as a residual. Fix is parked to WJNS-followup alongside 7A. No silent Jefferson delete
will be performed to paper over it.

---

## ✅ Ready to Build — Checklist

### Files I will touch (exactly four, matching C-3)

| File | Change |
|---|---|
| `numista_backend/master_coin_programs.json` | Insert WJNS program object (wrapper keys cloned from Jefferson Nickels shape; item_type absent; 2004-S Peace Medal = 2,992,069) |
| `numista_backend/_scripts/seed_global_programs.py` | `CANONICAL_DOC_IDS` entry already present — verify it survived revert; re-add if stripped |
| `numista_backend/_scripts/generate_westward_journey_checklist.py` | Update Peace Medal S mintage from 2,965,422 to 2,992,069; regenerate PDF |
| `numista_mobile/lib/services/coin_programs_data.dart` | Static fallback CoinProgram entry — wrapper Id matches JSON Name slug; item_type absent |

### First thing you can check in the browser

Open the regenerated PDF:
`numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf`

Confirm:
1. Four rows — Peace Medal, Keelboat, American Bison, Ocean in View!
2. Six columns — P | D | S Proof | P Satin | D Satin | Notes/QTY
3. 2004 Satin cells show **N/A** (greyed)
4. Peace Medal S cell shows **2,992,069** (not 2,965,422)
5. American Bison D cell shows **487,680,000**
6. Speared Bison footnote present
7. Trademark line: "Westward Journey Nickel Series™"

### What I will NOT touch

- `users/{uid}/coins` — zero writes, zero reads, zero mutations
- `jefferson_nickels` rows in `master_coin_programs.json` — untouched
- `program_manager_screen.dart` — untouched
- Any Dimes, RAG, model ID, or Firebase file
- Any GCS bucket or CLI command
- `main` branch — not referenced

---

*v1.2-final — Antigravity | 2026-09-02 | Waiting for Eric "go"*
