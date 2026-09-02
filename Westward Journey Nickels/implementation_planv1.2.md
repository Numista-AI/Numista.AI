# Westward Journey Nickel Series(tm) — Implementation Plan v1.2 (Addendum)

**Date:** 2026-09-02
**Status:** FOR REVIEW — Gemini, Grok, Eric sign-off required before any execution
**Scope:** Short addendum to v1.1. Closes all Grok v1.1 Must-Fixes. Does NOT re-open 7A, 7B,
Jefferson PDF, RELEASE_NOTES, or any path to main.

---

## CHANGES FROM v1.1

### PARKED (moved to named follow-up ticket "WJNS-followup")

| Item | Reason |
|---|---|
| 7A — Delete/exclude 2004-2005 rows from jefferson_nickels | Option A is a catalog delete with live matching side-effects. Option B needs a SlotResolver change not scoped here. Parked. |
| 7B — Add 2025 Jefferson Nickel | 2025-S mintage of 304,725 is uncited (far below recent proof-set levels). Not a WJNS blocker. Parked pending cited source. |
| Jefferson Nickels PDF regeneration | Depends on 7A decision. Parked. |
| RELEASE_NOTES.md update | Parked with 7A. |
| Step 11 / PR to main / 7485fc0a | Removed from this ticket entirely. Deploy conversation gates main. |
| GCS bucket name / upload | No live URL in repo. Removed from execution order. Eric-only when ready. |

---

## MF-A — 24f755f4 Diff vs. v1.1 JSON Object

**git show --stat 24f755f4 (the reverted, unauthorized commit):**

```
 numista_backend/_scripts/generate_westward_journey_checklist.py  | 434 +++
 numista_backend/_scripts/seed_global_programs.py                 |   1 +
 numista_backend/master_coin_programs.json                        | 149 +++
 numista_mobile/lib/services/coin_programs_data.dart              |  68 ++-
 4 files changed, 651 insertions(+), 1 deletion(-)
```

**Reconciliation against v1.1 JSON object:**

| Field | v1.1 JSON spec | 24f755f4 (reverted) | Match? |
|---|---|---|---|
| Doc ID | westward_journey_nickel_series | westward_journey_nickel_series | YES |
| Total slots | 16 | 16 | YES |
| 2005-D Bison mintage | 487,680,000 | 487,680,000 | YES |
| 2004 Satin | N/A (not a slot) | Not included | YES |
| 7A / 7B changes | Not in WJNS object | Not in WJNS object | YES |
| PR to main | Not in commit | Not in commit | YES |

**Current state of origin/dev:** The revert commit (94f94a65) removed all four files.
`master_coin_programs.json` on origin/dev does NOT contain WJNS today (confirmed by
local file scan). The v1.1 JSON object and 24f755f4 agreed on all fields; the revert
was a process correction, not a content correction. When Eric approves execution, the
same object will be re-committed.

---

## MF-B — Field Parity: Sibling Live JSON Object

Live example from `master_coin_programs.json` (America the Beautiful — same Circulating
Coin Program category, same seed path, same matcher):

```json
{
  "id": "atb_2010_hot_springs_national_park",
  "year": "2010",
  "name": "Hot Springs National Park (Arkansas)",
  "varieties": [
    {"id": "P",       "label": "P"},
    {"id": "D",       "label": "D"},
    {"id": "S",       "label": "S Clad Uncirculated"},
    {"id": "S-PROOF", "label": "S Clad Proof"}
  ]
}
```

**WJNS object uses the same field names** (`id`, `name`, `year`, `varieties[].id`,
`varieties[].label`) plus additional informational fields (`finish`, `mintage`, `note`)
that the seed script passes through and the matcher ignores when absent. The `item_type`
field used in 24f755f4 ("circulating") is an addition not present in sibling ATB objects.

**Action:** `item_type` will be removed from the WJNS Coins[] entries in the re-commit
to match the live ATB/AWQ/50-State field shape exactly. The top-level `"Category"`
field is present on other programs and is retained.

**User coins without program_id:** A user coin with Year=2005, Denomination=Nickel,
Theme=Bison, and no program_id will today match jefferson_nickels 2005 American Bison
row via the year+name matcher. After the WJNS seed, it will match BOTH programs unless
the SlotResolver is updated to prefer the more-specific program. This is the known
double-count risk. It is documented here; the fix is parked to WJNS-followup alongside 7A.

---

## MF-C — 2004-S Mintage Split and 2005 Proof Set Lot Rule

**2004-S mintage — corrected split:**

Standard catalog tables (PCGS CoinFacts, NGC) list:
- 2004-S Peace Medal Proof: **2,992,069**
- 2004-S Keelboat Proof: **2,965,422**

These are not identical. Both designs appear in every 2004 Proof Set product, but the
reported production figures differ by ~26,000 — likely reflecting destruction/QC rejects
counted differently by the Mint. The v1.1 draft used 2,965,422 for both (incorrect).

**Corrected values for the re-commit:**

```json
{ "id": "S-PROOF", "label": "S (Proof)", "finish": "proof", "mintage": 2992069,
  "note": "2004 Proof Set. Both Peace Medal and Keelboat appear in every 2004 Proof Set." }

{ "id": "S-PROOF", "label": "S (Proof)", "finish": "proof", "mintage": 2965422,
  "note": "2004 Proof Set. Both Peace Medal and Keelboat appear in every 2004 Proof Set." }
```

**2005 Proof Set lot rule (added):** A 2005 Proof Set lot covers both the 2005-S
American Bison and 2005-S Ocean in View! designs — same as the 2004 rule. A user who
logs "2005 Proof Set" as one lot satisfies both S-PROOF slots without two separate
parent documents.

---

## MF-D — GCS Bucket

The string `gs://numista-uploads-studio-9101802118-8c9a8` (from an earlier Gemini session)
is **NOT** the live checklist-serving bucket and will not appear in any code or plan.

The live uploads bucket nickname from Architecture 3.4.2 is:
`studio-9101802118-8c9a8-uploads`
with a path pattern of `checklists/{program_id}/{page_n}.pdf`.

**No GCS upload will be executed in this ticket.** The PDF is generated locally for
visual review only. GCS upload is Eric-only on a separate Proceed after the checklist
layout is approved.

---

## Corrected Mintage Table (Full, v1.2)

| Slot | Mintage | Source |
|---|---|---|
| 2004-P Peace Medal | 361,440,000 | US Mint Annual Report 2004 |
| 2004-D Peace Medal | 372,000,000 | US Mint Annual Report 2004 |
| 2004-S Peace Medal (Proof) | **2,992,069** | PCGS CoinFacts #4155 (corrected from 2,965,422) |
| 2004-P Keelboat | 366,720,000 | US Mint Annual Report 2004 |
| 2004-D Keelboat | 344,880,000 | US Mint Annual Report 2004 |
| 2004-S Keelboat (Proof) | 2,965,422 | PCGS CoinFacts #4156 |
| 2005-P American Bison | 448,320,000 | US Mint Annual Report 2005 |
| 2005-D American Bison | 487,680,000 | PCGS CoinFacts #4159 |
| 2005-S American Bison (Proof) | 3,344,679 | US Mint Annual Report 2005 |
| 2005-P American Bison (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |
| 2005-D American Bison (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |
| 2005-P Ocean in View! | 394,080,000 | US Mint Annual Report 2005 |
| 2005-D Ocean in View! | 411,120,000 | US Mint Annual Report 2005 |
| 2005-S Ocean in View! (Proof) | 3,344,679 | US Mint Annual Report 2005 |
| 2005-P Ocean in View! (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |
| 2005-D Ocean in View! (Satin) | 1,160,000 | 2005 US Mint Uncirculated Set |

Both 2004-S designs appear in every 2004 Proof Set product.
Both 2005-S designs appear in every 2005 Proof Set product.
Both 2005 Satin designs appear in the 2005 US Mint Uncirculated Set (1,160,000 sets).

---

## Execution Order (v1.2 — ends at dry-run)

| # | Action | Gate |
|---|---|---|
| 1 | Tri-party sign-off on v1.2 | Gemini + Grok + Eric |
| 2 | Eric opens PDF and approves layout | Eric visual sign-off |
| 3 | Code: re-commit WJNS-only changes (remove item_type, fix 2004-S Peace Medal mintage to 2,992,069) | After steps 1-2 |
| 4 | `seed_global_programs.py --dry-run` — confirm NEW PROGRAM 16 slots, WOULD_WRITE=0 on second run | After step 3 |
| 5 | **STOP. All further steps are Eric Proceed on a separate ticket.** | — |

**Not in this ticket:** --execute, GCS upload, Jefferson PDF, 7A, 7B, RELEASE_NOTES,
any path to main, any reference to deploy conversation 7485fc0a.

---

## Open Items for Reviewers (v1.2)

**Q1 (2004-S Peace Medal mintage):** v1.2 uses 2,992,069 from PCGS CoinFacts #4155.
If Eric has a US Mint Annual Report 2004 PDF showing a different figure, that supersedes PCGS.

**Q2 (item_type field):** Should `item_type: "circulating"` be retained for BQ
filtering, or removed to match sibling ATB/AWQ objects exactly? Recommend: remove
(match sibling shape; BQ loader infers type from Category field).

**Q3 (PDF layout):** Open and review:
`numista_mobile/_checklists_source/westward_journey_nickels_checklist.pdf`
Confirm column layout, font sizes, N/A greying, footnotes. PDF uses 2,965,422 for both
2004-S slots (will be corrected to 2,992,069 Peace Medal before re-commit).

---

*v1.2 — Antigravity | 2026-09-02 | FOR REVIEW ONLY — do not execute*
