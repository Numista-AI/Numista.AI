# PLAN: P7 V8.18.15b.v2 — Add Coins Flow & Gate Fixes

**Document:** `BETA TEST\Grok Bot\22 OCT 26\PLAN_P7_V8_18_15b.v2.md`  
**Date:** 2026-10-22 ~14:25 ET  
**Author:** Antigravity Chief of Staff (Gemini 3.8 Flash)  
**Governing Scores & Orders:** NET-424, NET-425, NET-426, NET-428, COS_SCORE_P7_ARGON_RCA_PLAN_V8_18_15b_v1.md  
**Status:** DRAFT — READY FOR GROK COS SCORE & BUILD EXECUTION  

---

## 1. Overview & Scope

Addresses UX Gate V7 (`UX_P7_GATE_V7.md`) and FT Gate V8.18.15a (`FT_P7_GATE_V8_18_15a.md`), with RCA v2 completed for the vanishing coins anomaly (`ARGON_VANISHING_COINS_RCA.md`).

Work branch: `p7-v8.9` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build`.  
No deploys, no main branch, dev only.  
Rule: Gate phone-only fixes with `!kIsWeb && (Platform.isAndroid || Platform.isIOS)`.

---

## 2. Items & Implementation Plan

### Item 1: Tap Targets Audit & Enforcement (>= 48px)
- **Files:** `numista_mobile/lib/widgets/add_coin_cert_card.dart`, `numista_mobile/lib/screens/base_layout.dart`, `numista_mobile/lib/screens/add_coins_hub.dart`.
- **Changes:**
  1. NGC Card "Check this slab on ngccoin.com" and "Cancel" buttons: increase padding / minHeight to 48px.
  2. Sidebar "Send Beta Feedback" and "Sign Out": set minimum height / tap constraint to 48px.
  3. Photo page "Take Photo" and "Upload" links/buttons: set minSize/tapTarget to 48px.
  4. Perform global audit across all Add-Coin widgets for interactive elements < 48px.
- **Tests:** Add widget test in `numista_mobile/test/` asserting tap targets >= 48px.

### Item 2: NGC Card Wording
- **File:** `numista_mobile/lib/widgets/add_coin_cert_card.dart`.
- **Change:** Update NGC unsupported lookup card copy to exact UX string:
  > *"We can't look up NGC numbers automatically yet. Snap the label or type the details below."*

### Item 3: Slab Label Photo OCR & Parse Reliability (Cert-Photo <30s)
- **File:** `numista_backend/routes/cert_routes.py` (line 441).
- **Changes:**
  1. Increase `max_output_tokens` from 256 to 1024.
  2. Enforce response JSON mode and add `json_repair` fallback.
  3. Wrap OCR extraction in `asyncio.wait_for(..., timeout=25.0)`.
  4. Include prompt and UI guidance for CACG/PCGS rear-label certificates (explicit hint when front is detected).
- **Tests:** Add pytest in `numista_backend/tests/` verifying handling of truncated/malformed LLM response without crashing.

### Item 4: US Mint Invoice PDF Parsing & Polling
- **Backend (`numista_backend/main.py` / `routes/import_routes.py`):**
  1. Fix invoice header extraction: parse Retailer (default "U.S. Mint"), Invoice #, and Order Date.
  2. Preserve Quantity > 1 rather than forcing QTY 1 for all items.
  3. Return explicit structured error JSON on parse failure instead of generic "Error".
- **Frontend (`numista_mobile/web/add_coins.html`):**
  1. Increase polling timeout from 17s to 60s with active countdown and progress message.
  2. Display real server error detail if import processing fails.
- **Tests:** Add pytest on U.S. Mint invoice fixture verifying Retailer, Invoice #, Date, and Qty > 1 extraction.

### Item 5: Fix Deduplication Rule & Surface Commit Skips (Vanishing Coins Fix)
- **Root Cause Verified in RCA v2:** `numista_backend/main.py:3572-3590` silently deleted coins matching Year + Mint + Denomination when `Retailer Invoice #` was blank, while `review_hub_screen.dart` blindly announced 100% success.
- **Changes:**
  1. **Backend (`main.py:3572-3590`):** Remove silent drop on Year + Mint + Denomination. Only drop as a definite duplicate if `Retailer Invoice #` AND `Retailer Item No.` match, or if explicit `cert_number` matches. Never delete multiple copies of identical raw coins.
  2. **Frontend (`review_hub_screen.dart:54-62`):** Parse response body `committed` and `skipped` counts. Display exact numbers:
     `'Committed ${data["committed"]} items. Skipped ${data["skipped"]} duplicates.'`
- **Tests:** Add pytest verifying that committing two coins with the same Year/Mint/Denomination without invoice numbers does NOT drop the second coin.

---

## 3. Verification Plan
- `pytest numista_backend/tests/` (all 39+ passing)
- `flutter test` (all 617+ passing)
- `flutter analyze` (0 errors, 0 warnings)
