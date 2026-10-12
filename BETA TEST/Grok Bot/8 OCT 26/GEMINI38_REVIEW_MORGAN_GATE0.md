# GEMINI 3.8 FLASH REVIEW — TRACK 2: PLAN_V1_MORGAN_GATE0.md
**Reviewer:** Gemini 3.8 Flash (Gatekeeper & Code Reviewer)  
**Date:** 2026-10-12  
**Target Document:** `BETA TEST\Grok Bot\8 OCT 26\PLAN_V1_MORGAN_GATE0.md`  
**Status:** **REVIEW COMPLETED — PASS WITH 3 TECHNICAL RECOMMENDATIONS**

---

## Executive Summary & Verdict

Antigravity CoS (Claude Opus 4.6 Thinking) has produced a thorough, safety-first specification for Morgan Gate 0. The plan addresses all 9 vulnerabilities identified in the joint UX/Morgan review, establishing the required safety harness (Confirm before write, server-resolved targets, soft delete trash, audit action logging, blocking rate caps, financial data stripping, prompt injection boundaries, and context reduction) before any capabilities expansion occurs.

Every file and line cited in the baseline was opened, read, and verified in the repository. The plan receives a **PASS**, with **3 crucial architectural recommendations** that must be reflected during implementation.

---

## 1. Verified Code Baseline (file:line Ground Truth)

Every baseline citation in Section 2 was directly inspected in the repository:

1. **`main.py:2909` — Prompt tells Morgan to write "immediately":**
   - **Verified:** Line 2909 explicitly states: `"- Only Year and Denomination (or coin name) are hard-required. If Year & Denomination are present, invoke add_coin_to_collection immediately with smart defaults."`
   - **Verdict:** Removing "immediately" and transitioning `add_coin_to_collection` from direct write to proposal generation is verified and necessary.

2. **`main.py:2618-2621` — Edit falls back to most-recently created coin:**
   - **Verified:** Lines 2618-2621 execute `col_ref.order_by('created_at', direction='DESCENDING').limit(1).stream()`, blindly selecting the last created document if no `coin_id` is supplied.
   - **Verdict:** Removing this fallback eliminates unintentional overwrites of user coins.

3. **`main.py:2651` — `INTERNAL_UNDO` hard-deletes document:**
   - **Verified:** Line 2651 executes `doc_ref.delete()` with zero audit trail or session scoping.
   - **Verdict:** Replacing with a soft-delete move to `users/{owner_key}/trash/{coin_id}` with a 30-day restore window ensures zero permanent accidental data loss.

4. **`logging_config.py:110-137` — `RateLimitTracker` logs only, never blocks:**
   - **Verified:** Line 113 states `"Does NOT block requests — only logs warnings when thresholds are exceeded."` Line 137 returns a boolean that callers merely log at warning level.
   - **Verdict:** Making this blocking (`raise HTTPException(status_code=429)`) is verified.

5. **`scan_service/collection_inventory.py:105, 156, 175` — Financial data sent by default:**
   - **Verified:** Lines 105, 156, 175 unconditionally extract `"ai_estimated_value"` and `"cost"` into every inventory dict passed to the model prompt.
   - **Verdict:** Stripping these fields unless `include_financial=True` (and Privacy Mode is OFF) is verified.

6. **`ai_chat_screen.dart:1169-1230` — UI Confirm Card Pattern:**
   - **Verified:** `_buildGroupProposalCard` and related methods already implement interactive proposal cards in Flutter. Reusing this for single/batch Morgan write proposals requires minimal client rework.

---

## 2. Critical Implementation Recommendations

### Recommendation 1: Cloud Run Architecture vs. In-Memory Daily Rate Caps (Item G0-5)
- **Issue:** In `logging_config.py:110-137`, `RateLimitTracker` maintains an in-memory dictionary `self._windows`.
- **Cloud Run Reality:** In production Cloud Run, instances scale horizontally and recycle frequently. An in-memory tracker is wiped on restart and cannot track **daily** quotas (e.g., 30 turns/day) across instances.
- **Solution:**
  - Keep `RateLimitTracker` for short-term RPM (requests per minute) sliding-window protection.
  - For the **daily caps** (30 Morgan turns, 20 confirms, 50 RAG queries), store a lightweight Firestore counter at `_rate_limits/{owner_key}/daily/{YYYY-MM-DD}`. Incrementing this counter atomically via Firestore transaction/increment ensures caps are globally enforced regardless of Cloud Run scaling.

### Recommendation 2: Proposal Document Location & Ownership (Item G0-1)
- **Issue:** The plan suggests `proposals/{uid}/pending/{proposal_id}`.
- **Solution:** Place proposals directly under the user's document tree: `users/{owner_key}/proposals/{proposal_id}`.
  - This guarantees alignment with Firestore security rules (`request.auth.token.email == userEmail` / `_collection_owner_from_token`).
  - Ensures all user-generated data resides cleanly within `users/{owner_key}/...`.

### Recommendation 3: Deep Discrepancy in `ai_routes.py` (Item G0-9)
- As documented during our code review, `ai_routes.py:107` has **two distinct errors**, not just uid-vs-email:
  1. **Wrong Path:** It queries `users/{user_id}/summary/stats`, whereas Flutter (`collection_stats_service.dart:106`) writes to `users/{owner_key}/metadata/collection_stats`.
  2. **Wrong Schema:** It looks for `total_coins` and `portfolio_value`, whereas the actual document stores `coin_count`, `item_count`, `est_value`, and `acquisition_cost`.
  - Item G0-9 must fix both the document path AND field mapping to `metadata/collection_stats`.

---

## 3. Review of Open / Integration Questions

1. **Coordination with REQ_031 Hotfix:**
   - REQ_031 must land on `dev` before Gate 0 begins touching `main.py` and `ai_routes.py`.
   - Gate 0 builds on the locked-down authentication foundations established by REQ_031.
2. **Acceptance Criteria Validation:**
   - Unit tests planned in `numista_backend/tests/test_morgan_gate0.py` cover all 9 gates.
   - Testing must include verifying that prompt injection strings in coin notes cannot coerce Morgan into generating rogue proposals without human confirmation.

---

## 4. Final Verdict

**PASS (CONDITIONAL ON IMPLEMENTATION RECOMMENDATIONS 1–3).**  
Antigravity CoS may proceed with Gate 0 implementation once REQ_031 is merged and scored.

*Gemini 3.8 Flash Gatekeeper review deposited at `BETA TEST\Grok Bot\8 OCT 26\GEMINI38_REVIEW_MORGAN_GATE0.md`.*
