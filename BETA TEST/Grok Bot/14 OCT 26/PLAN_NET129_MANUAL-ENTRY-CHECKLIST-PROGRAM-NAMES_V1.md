# PLAN v1 — NET-129 Manual Entry / Checklist / Program Name Fixes
AG CoS, 2026-10-14 ~11:25 PM ET. For Grok CoS review before code starts.
Queued: starts after P7 full PASS (preview + UX + field gates). Dev only. No deploy without Eric's YES. No data migration without Eric's YES.

---

## Problem Summary (from NET-129)

**Bug 1 — Manual Entry form:**
- Storage and Notes don't save
- No Purchase Date field
- Typed values sometimes land in wrong field
- Form keeps previous coin's values (Monroe P saved as D)
- Partly filled form can be submitted (Jefferson D saved with no mint/program)
- Condition inconsistent (Raw vs Ungraded)

**Bug 2 — Checklist adds:**
- Save Condition "Ungraded" and no cost/date/storage/notes
- No way to add extra copies of a coin already owned

**Bug 3 — Program naming split:**
- Checklist adds → Program "Presidential Dollars"
- Older coins → "Presidential  Coin Program" (note double space)
- Need one canonical name across all programs

---

## Root Cause Analysis (from code read)

### Bug 1 — Manual Entry
- `add_coins_hub.dart:1931-1954`: `coinDoc` map does NOT include `Notes` or `Purchase Date`
- `Storage Location` IS in the map — but if `AddCoinManualForm` isn't returning it, it silently saves `''`
- Form is `AddCoinManualForm` widget — need to find its field list and controllers
- "Previous coin's values" = controllers not reset after save
- Partial submission = no required-field validation before `FirebaseFirestore.instance.add(coinDoc)`

### Bug 2 — Checklist adds
- `beta_checklist_service.dart` builds its own coin doc when adding from checklist — need to read it to confirm missing fields
- "Extra copies" = no quantity/duplicate-add path in the checklist add flow

### Bug 3 — Program naming
- `checklist_2026_service.dart` (and likely older checklist files) hardcodes `"Presidential Dollars"` as program string
- Older coins from review/bulk import have `"Presidential  Coin Program"` (with double space — possibly a data entry artifact)
- `program_model.dart:174` has an alias that fuzzy-matches both, but the stored string in Firestore varies → collection grouping is broken

---

## Proposed Fixes

### Fix 1a — Manual Entry: add Notes + Purchase Date to coinDoc
**File:** `add_coins_hub.dart:1931-1954`
- Add `'Notes': data['Notes'] ?? ''` to coinDoc
- Add `'Purchase Date': data['Purchase Date'] ?? ''` to coinDoc
- Verify `AddCoinManualForm` actually renders and returns these fields; add them if missing

### Fix 1b — Manual Entry: reset controllers after successful save
**File:** `AddCoinManualForm` widget (find file)
- After save callback succeeds, call `reset()` / clear all TextEditingControllers
- Or: re-key the form widget with a counter to force rebuild

### Fix 1c — Manual Entry: required-field validation
**File:** `add_coins_hub.dart` onSubmit handler OR `AddCoinManualForm`
- Before calling `FirebaseFirestore.instance.add(coinDoc)`:
  - Validate `Year` is non-empty
  - Validate `Denomination` is non-empty OR `Program/Series` is non-empty
  - Show inline error (not just snackbar) for missing required fields
- "Mint Mark" is optional (intentional — some coins have no mint mark)

### Fix 1d — Manual Entry: Condition canonical value
- Map "Raw" → "Ungraded" (or pick one and use it everywhere)
- Check `AddCoinManualForm` condition dropdown values vs what checklist adds use

### Fix 2a — Checklist adds: save all fields
**File:** `beta_checklist_service.dart` (read the add path)
- After reading, add missing fields: `Notes`, `Purchase Date`, `Storage Location`, `Cost`
- Set `Condition` to a canonical value matching manual entry

### Fix 2b — Checklist adds: extra copies
**File:** add_coins_hub.dart checklist confirm path
- If coin is already owned (check Firestore for matching Year+Denomination+Program+MintMark), show option: "Add another copy" with Quantity field
- Or simpler: always show a Quantity field (default 1) on the checklist confirm card

### Fix 3 — Program naming: one canonical name
**Canonical name:** `"Presidential Dollar Coins"` → **NO.** Use what the US Mint uses: `"Presidential $1 Coins"` → check the actual checklist service definition.

Actually reading `checklist_2026_service.dart` showed the 2026 checklist uses named programs. For Presidential Dollars specifically:
- **Canonical name to use:** `"Presidential Dollars"` (matches program_model.dart:174 alias, shorter, used by checklist)
- Fix old coins: need a **one-time migration** that reads every coin doc with `Program/Series` containing "Presidential" and normalizes to `"Presidential Dollars"` — **NEEDS ERIC'S YES before running**
- Fix code: ensure all code paths that set `Program/Series` for Presidential coins use the same constant

---

## Files to Change

| File | Change |
|------|--------|
| `add_coins_hub.dart` | Bug 1a: add Notes + Purchase Date to coinDoc |
| `AddCoinManualForm` widget (TBD) | Bug 1a/1b/1c/1d: fields, reset, validation, Condition |
| `beta_checklist_service.dart` | Bug 2a: add missing fields to checklist add doc |
| `add_coins_hub.dart` (checklist confirm) | Bug 2b: extra copies / quantity |
| `checklist_2026_service.dart` + any others | Bug 3: normalize program name constant |
| Firestore migration script (NOT now) | Bug 3: normalize existing docs — **NEEDS ERIC'S YES** |

---

## What Is NOT in This Plan

- No data migration without Eric's typed YES
- No changes to Firestore security rules
- No deploy without Eric's typed YES
- P7 cert-lookup tab is untouched

---

## Open Questions for Grok CoS

**Q1:** For Bug 3 canonical name — confirm "Presidential Dollars" as the one true name, OR specify the correct one. The double-space variant "Presidential  Coin Program" looks like a typo in old data; confirm AG should normalize it away.

**Q2:** For Bug 2b (extra copies) — is Quantity field on confirm card sufficient, or should there be a smarter "already owned" flow?

**Q3:** Should `Purchase Date` be a date picker or a free-text field? (Current form likely uses text; a date picker is more reliable but more work.)

**Q4:** Confirm stand-alone migration script is acceptable for Bug 3 (run separately on Eric's YES), vs. a backend migration route.

---

## Tests Planned

- `flutter test`: add tests for `AddCoinManualForm`:
  - Empty required fields → blocked (no Firestore write)
  - Notes and Purchase Date appear in submitted data
  - Reset after save: all fields empty on next open
- `flutter test`: checklist add coin doc contains all 6 fields
- Backend: no pytest needed (no backend changes)

---

## Estimated Scope

- Small-medium Flutter change (1-2 files, mostly form widget)
- No backend changes
- No new routes
- Flutter test additions only

PLAN v1 — AG CoS 2026-10-14 ~23:25 ET. Awaiting Grok CoS GO before code starts.
