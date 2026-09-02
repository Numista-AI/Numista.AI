# Westward Journey Nickel Series™ — Checklist Implementation Plan

## Background

The **Westward Journey Nickel Series™ (2004–2005)** is a Congressionally-authorized coin program
(P.L. 108-15) that is **completely absent** from our checklist ecosystem. Research was done in a
prior session and saved to:
- `Westward Journey Nickels/Westward_Journey_Nickel_Series_Program_Reference.md`

The reference confirms 16 distinct collector slots across 4 designs, 3 mint facilities, and
2 strike types (Business Strike, Proof, and Satin Finish Mint Set).

The folder the user referred to is: `C:\Users\ericd\Documents\MyVertexProject\Westward Journey Nickels\`

---

## Current State Audit

| Layer | Status |
|---|---|
| Reference doc (`Westward_Journey_Nickel_Series_Program_Reference.md`) | ✅ Exists |
| `master_coin_programs.json` (Firestore data source) | ❌ Missing — no entry |
| `_checklists_source/` PDF (printable checklist) | ❌ Missing |
| `US Mint Coin Programs/` (Littleton-style training PDFs) | ❌ Missing |
| `numista_mobile/lib/services/checklist_generator_service.dart` — `_activePrograms` set | N/A (not an active series) |
| `CANONICAL_DOC_IDS` map in `seed_global_programs.py` | ❌ Not present (will fall back to `slugify()` which is fine) |
| GCS hosted checklist PDF (for app download) | ❌ Missing |
| `home_dashboard.dart` changelog entry | Partially — a TODO line exists at line 1560 but no actual program data |

---

## Proposed Changes

### Component 1 — Data Layer: `master_coin_programs.json`

Add the Westward Journey Nickel Series program object with all 16 collector slots
(4 designs × P/D/S + 2005 Satin Finish P/D).

#### [MODIFY] [master_coin_programs.json](file:///C:/Users/ericd/Documents/MyVertexProject/numista_backend/master_coin_programs.json)
- Append new program object `"westward_journey_nickel_series"` with full coin list
- The program will be picked up by `seed_global_programs.py` on next `--execute` run
- No changes to the seeding script itself are needed

---

### Component 2 — Printable Checklist PDF

Generate a Numista.AI native-format checklist PDF (`westward_journey_nickels_checklist.pdf`),
matching the exact visual style and column layout of the existing checklists in
`_checklists_source/` (e.g., the Jefferson nickels, American Innovation, Presidential dollars checklists):

- **Header:** `WESTWARD JOURNEY NICKEL SERIES™ (2004–2005)` + `Numista.AI Checklist` branding
- **Columns:** `Year / Design` | `P` | `D` | `S (Proof)` | `P-Satin` | `D-Satin` | `Notes / QTY`
- **16 rows**, one per collector slot (business strikes and mint set satins)
- **Mint mark location box** (right side of Jefferson's portrait on obverse)
- **Additional Notes section** (3 ruled lines) at the bottom
- Output: `numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf`

The PDF will be generated with a Python `reportlab` script (consistent with how all other
checklists in `_checklists_source/` are generated), using the same design spec defined in
`NUMISTA_AI_CHECKLIST_DESIGN_SPEC.md`.

#### [NEW] Script: `numista_backend/_scripts/generate_westward_journey_checklist.py`
Python script that generates the checklist PDF using `reportlab`.

#### [NEW] PDF output: `numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf`
_(Gitignored per `_checklists_source/README.md` — local only, serve from GCS)_

---

### Component 3 — GCS Upload

After generation, the PDF needs to be uploaded to the GCS bucket that serves downloadable
checklists to the app. This follows the same pattern as all other checklists.

> [!IMPORTANT]
> The exact GCS bucket path for checklist PDFs is not something I can confirm from the repo
> alone — the `_checklists_source/README.md` says they are "served from GCS" but the upload
> target URL is not committed to the repo. You may want to confirm the upload bucket/path or
> let the agent upload it using the existing `sync_local_images_to_gcs.py` pattern.

---

### Component 4 — App Program Data (Firestore via seed script)

After `master_coin_programs.json` is updated, run:
```bash
python numista_backend/_scripts/seed_global_programs.py --dry-run
python numista_backend/_scripts/seed_global_programs.py --execute
```

This seeds the new program into Firestore `global_programs` with doc ID
`westward_journey_nickel_series`, making it available to the app's checklist generator.

---

## Open Questions

> [!IMPORTANT]
> **Q1: GCS upload destination** — What bucket and path should the generated PDF be uploaded to?
> (The `_checklists_source/README.md` confirms it's served from GCS but doesn't name the bucket.)

> [!IMPORTANT]
> **Q2: Satin Finish inclusion** — The 2005 Satin Finish coins (P and D) were only available
> in official US Mint Sets. Should those 4 slots be included in the standard printable checklist,
> or should they be footnoted as "Mint Set only"? The reference doc lists them as full slots.
> **Current plan:** Include them with a `†` footnote marker.

> [!NOTE]
> **Q3: "Speared Bison" variety** — The 2005-D American Bison has a famous die-gouge error
> variety ("Speared Bison"). Should this be listed as a separate row in the checklist (like
> a key date footnote), or just referenced in the Notes column description?

---

## Verification Plan

### Automated
```bash
# Confirm PDF generates without error
python numista_backend/_scripts/generate_westward_journey_checklist.py

# Dry-run the Firestore seed
python numista_backend/_scripts/seed_global_programs.py --dry-run
```

### Manual
- Open the generated PDF and confirm it visually matches the style of
  `_checklists_source/jefferson_nickels_checklist.pdf` (same header layout, same column structure)
- Confirm 16 rows (or 17 if Speared Bison is included) render correctly

---

## 16 Collector Slots (from Reference Doc)

| # | Year | Design | Mint | Strike Type | Mintage |
|---|---|---|---|---|---|
| 1 | 2004 | Peace Medal | P | Business Strike | 361,440,000 |
| 2 | 2004 | Peace Medal | D | Business Strike | 372,000,000 |
| 3 | 2004 | Peace Medal | S | Clad Proof | 2,965,422 |
| 4 | 2004 | Keelboat | P | Business Strike | 366,720,000 |
| 5 | 2004 | Keelboat | D | Business Strike | 344,880,000 |
| 6 | 2004 | Keelboat | S | Clad Proof | 2,965,422 |
| 7 | 2005 | American Bison | P | Business Strike | 448,320,000 |
| 8 | 2005 | American Bison | D | Business Strike | 485,760,000 |
| 9 | 2005 | American Bison | S | Clad Proof | 3,344,679 |
| 10 | 2005 | American Bison | P | Satin Finish (Mint Set) | 1,160,000 |
| 11 | 2005 | American Bison | D | Satin Finish (Mint Set) | 1,160,000 |
| 12 | 2005 | Ocean in View! | P | Business Strike | 394,080,000 |
| 13 | 2005 | Ocean in View! | D | Business Strike | 411,120,000 |
| 14 | 2005 | Ocean in View! | S | Clad Proof | 3,344,679 |
| 15 | 2005 | Ocean in View! | P | Satin Finish (Mint Set) | 1,160,000 |
| 16 | 2005 | Ocean in View! | D | Satin Finish (Mint Set) | 1,160,000 |
