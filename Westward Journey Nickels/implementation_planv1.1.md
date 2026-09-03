# Westward Journey Nickel Series(tm) — Implementation Plan v1.1

**Date:** 2026-09-02  
**Status:** FOR REVIEW — Gemini, Grok, Eric sign-off required before any execution  
**Folder:** `C:\Users\ericd\Documents\MyVertexProject\Westward Journey Nickels\`

---

## ANTIGRAVITY SESSION DISCLOSURE

A prior Antigravity session executed code changes and pushed to `origin/dev`
**without user approval**, in violation of AGENTS.md Rules 1–3.

**Commit already on dev:**
```
24f755f4  feat(checklists): add Westward Journey Nickel Series(tm) 2004-2005
```

**Files pushed (Firestore NOT seeded, GCS NOT uploaded, main NOT touched):**
- `numista_backend/_scripts/generate_westward_journey_checklist.py`  [NEW]
- `numista_backend/master_coin_programs.json`  [MODIFIED — program entry added]
- `numista_mobile/lib/services/coin_programs_data.dart`  [MODIFIED — static fallback added]
- `numista_backend/_scripts/seed_global_programs.py`  [MODIFIED — CANONICAL_DOC_IDS]

**Steps that still require Eric Proceed before running:**
- `seed_global_programs.py --execute` (Firestore write)
- GCS upload of the PDF checklist
- Any merge to main

---

## 1. PROGRAM SCOPE

| Field | Value |
|---|---|
| Program | Westward Journey Nickel Series(tm) |
| Authority | American 5-Cent Coin Design Continuity Act of 2003 (P.L. 108-15; 31 U.S.C. Section 5112(p)) |
| Same class as | 50 State Quarters, ATB Quarters, American Women Quarters, Lincoln Bicentennial Cents |
| Years | 2004–2005 only |
| Excluded | 2006 Return to Monticello (separate statutory clause, stays out) |

**Jefferson exclusion:** The 4 Westward Journey designs are tracked **only** on this checklist.
Must NOT also be scored on `jefferson_nickels`. The existing `jefferson_nickels` rows for these
years remain in the data (not deleted this ticket) but must not count in progress math — a
follow-up ticket should mark them `excluded_by: westward_journey_nickel_series`. No second
`SlotResolver` is written; matching key `program_id + coin_id + variety_id` already isolates.

**Mint-set / Proof-set lot rule:**
- 2005 Mint Set = one lot covering all four 2005 Satin slots (P+D Bison, P+D Ocean)
- 2004 Proof Set = one lot covering both 2004-S designs
- Reuse `expand_collection_inventory`. No new parser.

---

## 2. MF-1 — Full Program JSON (master_coin_programs.json)

Object inserted at index 10 (after Jefferson Nickels, before Mercury Dimes):

```json
{
  "Name": "Westward Journey Nickel Series",
  "Id": "westward_journey_nickel_series",
  "Years": "2004-2005",
  "Url": "https://www.usmint.gov/learn/coin-and-medal-programs/westward-journey-nickel-series",
  "Category": "Circulating Coin Programs",
  "Denomination": "Five Cents",
  "Statutory_authority": "American 5-Cent Coin Design Continuity Act of 2003 (P.L. 108-15; 31 U.S.C. Section 5112(p))",
  "Mint_mark_type": "OBVERSE_PORTRAIT",
  "Mint_mark_description": "Right side of Jeffersons portrait on the obverse. 2004: 1938 Schlag portrait. 2005: one-year-only Houdon/Fitzgerald portrait with handwritten Liberty script.",
  "Coins": [
    {
      "year": "2004", "name": "Peace Medal", "design_slug": "2004_peace_medal",
      "item_type": "circulating",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 361440000},
        {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 372000000},
        {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 2965422,
         "note": "Proof Set only; same production run as 2004-S Keelboat"}
      ]
    },
    {
      "year": "2004", "name": "Keelboat", "design_slug": "2004_keelboat",
      "item_type": "circulating",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 366720000},
        {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 344880000},
        {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 2965422,
         "note": "Proof Set only; same production run as 2004-S Peace Medal"}
      ]
    },
    {
      "year": "2005", "name": "American Bison", "design_slug": "2005_american_bison",
      "item_type": "circulating",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 448320000},
        {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 487680000,
         "note": "Per PCGS CoinFacts #4159. Includes Speared Bison die-gouge variety (PCGS FS-901)."},
        {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 3344679},
        {"id": "P-SATIN", "label": "P (Satin Finish)", "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only"},
        {"id": "D-SATIN", "label": "D (Satin Finish)", "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only"}
      ]
    },
    {
      "year": "2005", "name": "Ocean in View!", "design_slug": "2005_ocean_in_view",
      "item_type": "circulating",
      "varieties": [
        {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 394080000},
        {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 411120000},
        {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 3344679},
        {"id": "P-SATIN", "label": "P (Satin Finish)", "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only"},
        {"id": "D-SATIN", "label": "D (Satin Finish)", "finish": "satin",           "mintage": 1160000,
         "note": "2005 US Mint Uncirculated Set only"}
      ]
    }
  ]
}
```

**CANONICAL_DOC_IDS line added to `seed_global_programs.py`:**
```python
"Westward Journey Nickel Series": "westward_journey_nickel_series",
```

**Dry-run result (run before push):**
```
Parsed 33 canonical programs (0 quarantined).
westward_journey_nickel_series: NEW PROGRAM — 16 slots
```

---

## 3. MF-2 — Mintage Table with Sources

| Slot | Mintage | Source |
|---|---|---|
| 2004-P Peace Medal | 361,440,000 | US Mint Annual Report 2004 |
| 2004-D Peace Medal | 372,000,000 | US Mint Annual Report 2004 |
| 2004-S Peace Medal (Proof) | 2,965,422 | US Mint AR 2004 — shared run with Keelboat |
| 2004-P Keelboat | 366,720,000 | US Mint Annual Report 2004 |
| 2004-D Keelboat | 344,880,000 | US Mint Annual Report 2004 |
| 2004-S Keelboat (Proof) | 2,965,422 | US Mint AR 2004 — shared run with Peace Medal |
| 2005-P American Bison | 448,320,000 | US Mint Annual Report 2005 |
| **2005-D American Bison** | **487,680,000** | **PCGS CoinFacts #4159 — corrected from 485,760,000 in v1 draft** |
| 2005-S American Bison (Proof) | 3,344,679 | US Mint Annual Report 2005 |
| 2005-P American Bison (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |
| 2005-D American Bison (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |
| 2005-P Ocean in View! | 394,080,000 | US Mint Annual Report 2005 |
| 2005-D Ocean in View! | 411,120,000 | US Mint Annual Report 2005 |
| 2005-S Ocean in View! (Proof) | 3,344,679 | US Mint Annual Report 2005 |
| 2005-P Ocean in View! (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |
| 2005-D Ocean in View! (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |

**2004 Satin:** None issued. 2004 Mint Set contained business-strike nickels.
Satin finish began with the 2005 Uncirculated Set. 2004 satin cells are N/A on the PDF.

**Speared Bison:** Die-gouge variety (PCGS FS-901) within standard 2005-D mintage.
NOT a 17th official program slot. Footnote on PDF only.

---

## 4. MF-3 — Jefferson Exclusion Paragraph

The 2004 Peace Medal, 2004 Keelboat, 2005 American Bison, and 2005 Ocean in View! coins are
tracked exclusively on the `westward_journey_nickel_series` checklist. The `jefferson_nickels`
program object still contains rows for these designs (not removed in this ticket); those rows
must not be counted in Programs-tab completion math or estate FMV. Matching key is
`program_id + coin_id + variety_id`; since `program_id` differs, the existing SlotResolver
already isolates the slots without modification. Follow-up ticket needed to either delete
those rows from `jefferson_nickels` or add an `excluded_by` marker. No second SlotResolver.

---

## 5. MF-4 — Live Wiring Grep Results

**GCS checklist prefix:**
- grep `storage.googleapis` in `numista_mobile/lib/` = no results
- `_checklists_source/README.md` states: "Served from GCS — the live checklist downloads
  are hosted in Google Cloud Storage, not from this directory."
- **Bucket name/path not committed to repo. Eric to confirm before GCS upload.**

**`_activePrograms` decision:**
- Westward Journey Nickel Series is a completed historical series (2004–2005)
- NOT added to `_activePrograms` in `checklist_generator_service.dart`
- "Active series — verified snapshot" badge will NOT appear. Correct.

**`CoinProgramsData` update:**
- YES — static fallback entry added to `coin_programs_data.dart`
- Placed in `"Circulating Coin Programs"` list, after Bicentennial Program block
- Without this, program card fails to render on skeleton/cold-start before Firestore loads

**Firestore today:**
- `global_programs/westward_journey_nickel_series` does NOT yet exist
- `seed --execute` has not been run
- Dry-run confirmed: NEW PROGRAM — 16 slots

---

## 6. PDF Column Matrix

Layout: **4 design rows × 6 mint/finish columns** (not "16 rows"):

```
Year / Design        |  P  |  D  | S Proof | P Satin(tt) | D Satin(tt) | Notes/QTY
---------------------|-----|-----|---------|-------------|-------------|----------
2004 Peace Medal     |  []  |  []  |   []    |    N/A      |    N/A      |
2004 Keelboat        |  []  |  []  |   []    |    N/A      |    N/A      |
2005 American Bison  |  []  |  []  |   []    |     []      |     []      |
2005 Ocean in View!  |  []  |  []  |   []    |     []      |     []      |
```

(tt) = 2005 US Mint Uncirculated Set only. N/A cells visually greyed out.

Each cell also prints mintage below checkbox for collector reference.
Footer footnotes: Satin explanation, Speared Bison, shared Proof Set run, Jefferson exclusion.
Trademark line: "Westward Journey Nickel Series(tm) is a trademark of the United States Mint."

---

## 7. Jefferson Nickels — Two Required Updates

These two changes are in-scope for this same ticket because they are directly caused by
adding the Westward Journey program. Both touch `master_coin_programs.json` (jefferson_nickels
program object) and `coin_programs_data.dart` (static fallback). Both require the same
Eric Proceed gate as the main Westward Journey work.

---

### 7A. Westward Journey Row Treatment in jefferson_nickels

**Problem:** `master_coin_programs.json` and `coin_programs_data.dart` both currently include
the four Westward Journey designs (2004 Peace Medal, 2004 Keelboat, 2005 American Bison,
2005 Ocean in View!) inside the `jefferson_nickels` program with varieties `[P, D, S-PROOF]`.
Now that these are owned by `westward_journey_nickel_series`, leaving them in `jefferson_nickels`
will cause double-counting in Programs-tab completion bars and estate FMV.

**Decision required from reviewers — pick one:**

| Option | Action | Implication |
|---|---|---|
| (A) Delete rows | Remove the 4 design rows from `jefferson_nickels` entirely | Cleanest. Breaks any existing user collection entry that was matched against `jefferson_nickels` for these designs. |
| (B) Exclude marker | Add `"excluded_from_progress": true` to each variety | Safe migration. Rows stay for backward compat; SlotResolver skips them in math. Requires SlotResolver change. |

**Recommended: Option A (delete).** The coins pre-date any user data that was matched
correctly, and the Westward Journey slots will now cover them. A migration note should be
added to `RELEASE_NOTES.md`.

**What will be changed (pending decision):**

In `master_coin_programs.json` → `jefferson_nickels` → `Coins` array:
- Remove the objects where `"name"` is `"Peace Medal"`, `"Keelboat"`,
  `"American Bison"`, or `"Ocean in View"` and `"year"` is `"2004"` or `"2005"`.

In `coin_programs_data.dart` → `CoinProgramsData.usPrograms` → jefferson_nickels coins list:
- Remove the corresponding `ProgramCoin` entries (if they exist in the static fallback).

**Note:** The Jefferson Nickels printable PDF checklist (in `_checklists_source/`) was
originally generated from Littleton's LC-145 source PDF and does include the 2004–2005
rows. Once the data is corrected, the PDF should be regenerated and re-uploaded to GCS with
a note in the header: *"2004–2005 designs are part of the Westward Journey Nickel Series™.
See the Westward Journey Nickel Series™ checklist for those coins."*

---

### 7B. Add Missing 2025 Jefferson Nickel

**Problem:** `jefferson_nickels` in `master_coin_programs.json` ends at 2024.
The 2025 Jefferson Nickel is not present in **any** program across the entire
`master_coin_programs.json` file (confirmed by full scan).

**Research (US Mint, verified 2026-09-02):**

| Slot | Mintage | Notes |
|---|---|---|
| 2025-P Jefferson Nickel | 443,840,000 | Philadelphia, business strike, circulating |
| 2025-D Jefferson Nickel | 322,320,000 | Denver, business strike, circulating |
| 2025-S Jefferson Nickel | 304,725 | San Francisco, Proof only (Proof Set) |

No design changes for 2025. Standard Monticello reverse and forward-facing Jefferson
obverse (Franki, introduced 2006). Standard cupro-nickel composition (75% Cu / 25% Ni).

**What will be added to `master_coin_programs.json` → `jefferson_nickels` → `Coins` array:**

```json
{
  "year": "2025",
  "name": "Jefferson Nickel",
  "varieties": [
    {"id": "P",       "label": "P (Philadelphia)", "finish": "business_strike", "mintage": 443840000},
    {"id": "D",       "label": "D (Denver)",       "finish": "business_strike", "mintage": 322320000},
    {"id": "S-PROOF", "label": "S (Proof)",        "finish": "proof",           "mintage": 304725}
  ]
}
```

**What will be added to `coin_programs_data.dart` static fallback** (if jefferson_nickels
appears in `CoinProgramsData.usPrograms` — it currently does not; the static list only
covers named programs like 50 State Quarters, AWQ, etc. Jefferson Nickels falls back to
Firestore. So only `master_coin_programs.json` and the seed need updating for this row.)

---

## 8. Execution Order (Updated)

All steps require Eric Proceed. Jefferson Nickels updates (7A and 7B) are bundled in
the same commit as the Westward Journey work — one PR, one review, one seed run.

| # | Action | Gate |
|---|---|---|
| 1 | Tri-party sign-off on this v1.1 | Gemini + Grok + Eric |
| 2 | Eric opens PDF and approves layout | Eric visual sign-off |
| 3 | Eric decides: Option A or B for 7A (Westward Journey rows in jefferson_nickels) | Eric decision |
| 4 | Code: update `master_coin_programs.json` (Westward + Jefferson 7A + Jefferson 7B) | After step 3 |
| 5 | Code: update `coin_programs_data.dart` static fallback if applicable | After step 3 |
| 6 | Code: regenerate Jefferson Nickels PDF with redirect note | After step 3 |
| 7 | `seed_global_programs.py --dry-run` — confirm slot counts | After step 4-5 |
| 8 | `seed_global_programs.py --execute` | Eric Proceed |
| 9 | GCS upload: Westward Journey PDF + updated Jefferson Nickels PDF | Eric Proceed, bucket TBD |
| 10 | git add → git commit → git pull --rebase origin dev → git push origin dev | After step 8-9 |
| 11 | PR to main via deploy conversation `7485fc0a` only | Deploy gatekeeper |

**Forbidden in this ticket:**
- `program_manager_screen.dart` Ticket A changes
- Dimes expander / Fix B
- Morgan RAG, Gemini model ID changes, PCGS import, hardware agent
- Firebase deploy commands
- Production GCS write without Eric
- Littleton training PDF generation
- Any push or merge to `main`

---

## 9. Open Items for Reviewers

**Q1 (GCS bucket):** What bucket/path do checklist PDFs upload to?
Not stored in the repo. Eric to confirm before execution step 9.

**Q2 (Jefferson cleanup — 7A decision):** Option A (delete 2004–2005 rows from
`jefferson_nickels`) or Option B (add `excluded_from_progress` marker)?
Recommended: Option A. Awaiting Eric + reviewer confirmation.

**Q3 (PDF visual):** Open and review:
`numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf`
Confirm column layout, font sizes, footnotes, and N/A cell greying before approving
GCS upload.

---

*v1.1 — Antigravity | 2026-09-02 | FOR REVIEW ONLY — do not execute*
