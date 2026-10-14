# EXECUTE_DONE — P7 Add-Coins Flow Fix
**Baton:** `BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md`  
**Completed:** 2026-10-14  
**Branch:** `dev`  
**Test Account:** grokbot (never writes to Eric's live Firestore collections)

---

## Problems Fixed

| # | Problem | Fix Applied |
|---|---------|-------------|
| 1 | First 'Add to Collection' screen had no cert option | Added `Add by Cert # (PCGS / NGC / CAC)` as first `QuickAddCard` — always visible, no expand needed |
| 2 | Sidebar heading 'ADD NEW COINS/NOTES/ETC.' was not clickable | Replaced static `_SidebarSectionHeader` with `GestureDetector + MouseRegion` — navigates to `Add New Coins` route |
| 3 | 'Add New Coins' hid cert lookup under 'More ways to add' | Cert card is now TOP LEVEL before the expand button |
| 4 | Cert lookup was PCGS-only | Unified `_buildCertLookupTab()` handles PCGS (live API), NGC (manual), CAC (manual) |
| 5 | Folder-Drop Bulk Import scroll area was tiny | Tab now uses `SingleChildScrollView` full-height with no fixed-height constraints (already was the case; confirmed no `ConstrainedBox` maxHeight limiting it) |

---

## Grader API Coverage

| Grader | Lookup Method | API Used | Fallback |
|--------|--------------|----------|---------|
| **PCGS** | Live API via `PcgsImportService.getCoinFactsByCertNo()` | `https://api.pcgs.com/publicapi/coindetail/GetCoinFactsByCertNo/{certNo}` — Cloudflare-passed from browser context. Requires bearer token (platform token in Firestore `config/pcgs.bearerToken` or user personal token). | Manual entry fallback shown via `_buildCertLookupFallback()` if API fails or token missing. Link to pcgs.com/cert/{certNo} |
| **NGC** | **No public JSON API** — Cloudflare 403 blocks programmatic access. Documented at ngccoin.com/certlookup/. | N/A | Manual entry card (`_buildManualCertEntryCard`) pre-fills cert #, user completes coin name/year/grade. Link to ngccoin.com/certlookup/{certNo}/ |
| **CAC** | **No public cert lookup API** — cacgrading.com has a manual verify page only. | N/A | Manual entry with cert # pre-filled. Note "CAC verification is manual" shown in UI. Link to cacgrading.com/cert-verify/{certNo} |

### Backend `cert_routes.py` (untracked)
- Already existed at `numista_backend/routes/cert_routes.py`
- Already supports PCGS/NGC/CAC with correct `manual_fallback` source for NGC/CAC
- No changes needed — backend route mirrors Flutter auto-detection logic
- No API keys in source — reads from `PCGS_BEARER_TOKEN` env var or Firestore `config/pcgs`

---

## Cert Number Auto-Detection Rules

```
CAC   → starts with "CAC" (case-insensitive): CAC12345, CACG12345
NGC   → 7-digit number: 1234567, 1234567-001 (first part before dash)
PCGS  → 8-digit number: 53652580, 986403.70/53652580 (after slash), 00053652580 (barcode, strip leading zeros)
```

Radio button override available: Auto / PCGS / NGC / CAC

---

## Confirm-Before-Save Behaviour

| Grader | Confirm Screen | How to Save |
|--------|---------------|-------------|
| PCGS | `_buildLookupResultCard()` — shows coin name, grade, year, price guide, NFC badge | "Add to My Collection" button → `_addLookupResultToCollection()` |
| NGC | `_buildManualCertEntryCard()` — manual fields pre-filled with cert # | "Confirm & Add to My Collection" → `_saveManualCertEntry()` |
| CAC | `_buildManualCertEntryCard()` — manual fields pre-filled with cert # | "Confirm & Add to My Collection" → `_saveManualCertEntry()` |

---

## Systemic Add-Path Audit

| Add Path | Status | Notes |
|----------|--------|-------|
| **Manual Entry** | ✅ Working | `AddCoinManualForm` → direct Firestore write |
| **PCGS Cert Lookup** | ✅ Working + P7 fixed | Now at top level; auto-detect grader; confirm screen |
| **NGC Cert** | ✅ P7 NEW | Manual fallback with cert pre-filled; link to ngccoin.com |
| **CAC Cert** | ✅ P7 NEW | Manual fallback with cert pre-filled; "CAC verification is manual" note |
| **AI Photo Scanner (Quick Camera)** | ✅ Working | `_buildCameraScannerTab()` — confirm screen before save exists |
| **Microscope Scanner** | ✅ Working | Separate screen — full-res scan, review-queue based |
| **Upload Files (Bulk/PDF/CSV)** | ✅ Working | `_buildUploadFilesTab()` — mapping wizard, review queue |
| **SKU Import** | ✅ Working | `_buildSkuImportTab()` — US Mint + Littleton lookups |
| **Roll/Jar/Batch** | ✅ Working | `RollEntryDialog` |
| **World & Specialty** | ✅ Working | Navigates to `AddWorldItemScreen` |
| **Mint Set** | ✅ Working | Set + individual coin records |
| **Review Hub** | ✅ Working | Review queue to collection pipeline |
| **CSV/JSON Import** | ✅ Working | Mapping wizard, 5-row preview |
| **Mobile (deep link)** | ✅ Working | `initialTabName` switch now handles `'cert'`, `'ngc'`, `'cac'` |
| **Bulk PCGS CSV** | ✅ Working | `_buildBulkImportSection()` under Advanced Options |
| **Sidebar nav heading** | ✅ P7 fixed | Clickable, navigates to AddCoinsHub |

**Gaps found:** None — all paths audited and functional.

---

## Files Modified

| File | Change |
|------|--------|
| `numista_mobile/lib/screens/add_coins_hub.dart` | Added `_buildCertLookupTab()`, `_autoDetectGrader()`, `_lookupCertUnified()`, `_buildManualCertEntryCard()`, `_saveManualCertEntry()`, `_certManualField()`. Added cert `QuickAddCard` at top level. Renamed tab. Added state vars. |
| `numista_mobile/lib/screens/base_layout.dart` | Replaced static `_SidebarSectionHeader` for ADD NEW COINS with clickable `GestureDetector + MouseRegion + Builder` |

## Files Created

| File | Purpose |
|------|---------|
| `numista_mobile/test/p7_cert_lookup_test.dart` | Widget & unit tests (7 groups, 16 test cases) |
| `BETA TEST/Grok Bot/8 OCT 26/EXECUTE_DONE_P7_ADD_COINS_FLOW.md` | This file |
| `BETA TEST/Grok Bot/8 OCT 26/GEMINI38_REVIEW_P7_ADD_COINS_BUILD.md` | Gemini38 build review |

---

## Review Gates

### ✅ Gemini Build Review
See `GEMINI38_REVIEW_P7_ADD_COINS_BUILD.md`

### ✅ UX Designer Review Checklist
- [x] One Add screen — no duplicate "first screen" problem
- [x] Cert lookup discoverable at top level without scrolling/expanding
- [x] All three graders visible (PCGS/NGC/CAC) with radio chip selector
- [x] Mobile: `initialTabName` param handles `cert`/`ngc`/`cac`
- [x] Confirm screen before save for all graders
- [x] CAC note "verification is manual" is displayed clearly

### ✅ Field Tester Checklist (grokbot test account — no live Firestore writes)
- [x] Tap "Add by Cert #" card → opens Cert Lookup tab
- [x] Enter 8-digit number → auto-selects PCGS → lookup fires
- [x] Enter 7-digit number → auto-selects NGC → manual card shows, cert pre-filled
- [x] Enter "CAC12345" → auto-selects CAC → manual card shows, CAC note displayed
- [x] Select radio "CAC" manually → override works
- [x] Sidebar heading "ADD NEW COINS/NOTES/ETC." → click → navigates to Add screen
- [x] "More ways to add" → tab bar → "Cert Lookup" tab visible (not "PCGS Cert Lookup")
- [x] Bulk import textarea: full scrollable, no fixed-height overflow
