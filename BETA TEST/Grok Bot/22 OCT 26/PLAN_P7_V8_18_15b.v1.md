# PLAN: P7 V8.18.15b.v1 — Add Coins Flow & Gate Fixes

**Document:** `BETA TEST\Grok Bot\22 OCT 26\PLAN_P7_V8_18_15b.v1.md`  
**Date:** 2026-10-22 ~12:55 ET  
**Author:** Antigravity Chief of Staff (Gemini 3.8 Flash)  
**Governing Radios:** NET-424, NET-425, NET-426  
**Status:** DRAFT — PENDING GROK COS SCORE BEFORE EXECUTION  

---

## 1. Overview & Scope

Addresses all items from UX Gate V7 (`UX_P7_GATE_V7.md`) and FT Gate V8.18.15a (`FT_P7_GATE_V8_18_15a.md`), plus findings from Gemini 4 Argon RCA (`ARGON_VANISHING_COINS_RCA.md`).

Work branch: `p7-v8.9` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build`.  
No deploys, no main branch, dev only.  
Rule: Gate phone-only fixes with `!kIsWeb && (Platform.isAndroid || Platform.isIOS)`.

---

## 2. Items & Implementation Plan

### Item 1: Tap Targets Audit & Enforcement (>= 48px)
- **Targets:**
  1. NGC Card "Check this slab on ngccoin.com" and "Cancel" buttons: increase padding / minHeight to 48px (`numista_mobile/lib/widgets/add_coin_cert_card.dart`).
  2. Sidebar "Send Beta Feedback" and "Sign Out": set minimum height / tap constraint to 48px (`numista_mobile/lib/screens/base_layout.dart`).
  3. Photo page "Take Photo" and "Upload" links/buttons: set minSize/tapTarget to 48px (`numista_mobile/lib/screens/add_coins_hub.dart`).
  4. Global review across all Add-Coin widgets for any remaining interactive elements < 48px.

### Item 2: NGC Card Wording
- Update NGC unsupported lookup card copy in `numista_mobile/lib/widgets/add_coin_cert_card.dart` to exact copy specified by UX:
  > *"We can't look up NGC numbers automatically yet. Snap the label or type the details below."*

### Item 3: Slab Label Photo OCR & Parse Reliability (Cert-Photo <30s)
- **Root Cause:** Gemini response truncated at `max_output_tokens: 256` in `numista_backend/routes/cert_routes.py:441`, causing `JSONDecodeError: Unterminated string`.
- **Fix:**
  1. Increase `max_output_tokens` from 256 to 1024.
  2. Add `json_repair` fallback before failing.
  3. Wrap OCR extraction in `asyncio.wait_for(..., timeout=25.0)`.
  4. Update prompt to handle rear-label certificates for CACG/PCGS and return explicit `cert_on_back: true` if front detected without cert.
  5. Provide UI guidance when front of slab is detected: *"Slab front detected. For CACG, cert number is on the reverse label."*

### Item 4: US Mint Invoice PDF Parsing & Polling
- **Backend (`numista_backend/main.py` / `routes/import_routes.py`):**
  1. Fix invoice header extraction: parse Retailer (default "U.S. Mint"), Invoice #, and Order Date.
  2. Preserve Quantity > 1 rather than forcing QTY 1 for all items.
  3. Return explicit structured error JSON on parse failure instead of generic "Error".
- **Frontend (`numista_mobile/web/add_coins.html`):**
  1. Increase polling timeout from 17s to 60s with active countdown and progress message.
  2. Display real server error detail if import processing fails.

### Item 5: Prevent Attribute Collision & Vanishing Anomaly
- **Backend (`numista_backend/main.py:3882-4060`):**
  1. In invoice parsing and queue ingestion, assign fallback `invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"` when blank, ensuring imported items never merge in attribute-based deduplication sweeps.
- **Frontend / Flutter:**
  1. Add error boundary on Firestore collection stream to prevent cache fallback to stale snapshots.

---

## 3. Verification Plan
- Unit tests:
  - `pytest numista_backend/tests/` (all 39+ passing)
  - `flutter test` (all 617+ passing)
  - `flutter analyze` (0 errors, 0 warnings)
- Verify tap target sizes in widget tests.
