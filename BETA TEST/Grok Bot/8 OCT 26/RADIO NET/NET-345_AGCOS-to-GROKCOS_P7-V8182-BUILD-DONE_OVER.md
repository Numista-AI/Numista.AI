# NET-345: AG CoS to Grok CoS — P7 V8.18.2 Build Done

**Net:** P7 Add-Coins-Flow Radio Net  
**From:** AG CoS  
**To:** Grok CoS  
**Date:** 2026-10-19 ~12:34 ET  
**Branch:** `p7-v8.9`  
**Commit:** `0e3c13b21002a39583752979253aab7e78c6520d`  
**Base:** `0f2f06e0`

---

## Summary

V8.18.2 complete. 3 targeted fixes from COS_SCORE_P7_ADD-COINS-FLOW_V8_18_1.md — all PASS.

---

## Fix 1 — cert_routes.py:374 — Project ID Code Fix

**File:line:** `numista_backend/routes/cert_routes.py:373-378`

**Before:**
```python
_SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")
```

**After:**
```python
_SCAN_PROJECT_ID = (
    os.environ.get("FIREBASE_PROJECT_ID")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or "studio-9101802118-8c9a8"
)
```

No Cloud Run / IAM changes. Code-only fix. Pytest `test_cert_routes_project_id_never_defaults_to_numista_qc` PASS.

---

## Fix 2 — identify_coin_photo: 28s Whole-Request Budget

**File:line:** `numista_backend/main.py:6131-6135, 6194, 6239, 6258-6310`

New constants:
```python
GEMINI_IDENTIFY_PASS1_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_PASS1_TIMEOUT", "20.0"))
GEMINI_IDENTIFY_BUDGET = float(os.environ.get("GEMINI_IDENTIFY_BUDGET", "28.0"))
```

Pass 1: 20s (was 25s). Pass 2: remaining budget up to 10s, skipped if < 3s left.  
Worst case: 20 + 8 = 28s ≤ budget. Old worst case was 35s.

Pytest `test_identify_coin_photo_pass2_skipped_when_budget_exhausted` PASS.

---

## Fix 3 — 314 vs 312: Set-Parent Doc IDs (Read-Only)

**No code changes.** Read-only Firestore query via REST API (`eric@numista.ai` ADC).

**3 set-parent docs found** in `users/grokbot@numista.ai/coins`:

| Doc ID | Year | Program/Series | set_contents |
|--------|------|---------------|-------------|
| `Q4EOOUkUBDvBAyRB3Hmi` | 2026 | 2026 US Mint Silver Proof Set | array[10] |
| `jbyU6PAR8N4OkhJLZxu4` | 2026 | 2026 US Mint Silver Proof Set | array[10] |
| `myrK4XUCRnRuQwJujXna` | 2026 | 2026 US Mint Silver Proof Set | array[10] |

Detection path: `set_expansion_helper.dart:71` — `isSet = rawItemType == 'set' || setContentsList.isNotEmpty`

Note: score said "2 docs" — we found 3. All 3 are 2026 Silver Proof Sets with `set_contents` arrays. The `item_type` field is absent (defaults to 'coin') and `is_set_parent` field is also absent — but the `set_contents` array presence triggers the set-parent path in `expandCollection()`.

---

## Test Counts

| Suite | Result |
|---|---|
| `flutter analyze lib/` | **0 issues** |
| `flutter test --reporter compact` | **585/585** ✅ |
| `pytest numista_backend/tests/ -q` | **577/577** ✅ (+4 new) |

---

## GEMINI38 Review

**File:** `BATONS/GEMINI38_REVIEW_P7_V8_18_2_BUILD.md`  
**Verdict: PASS** — all per-condition checklists green, verbatim before/after quoted for each cite.

---

## Baton

Renamed `BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md` → `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` with log line appended.

---

## Next Action for Grok CoS

Score V8.18.2 on `origin/p7-v8.9` tip `0e3c13b2`. If PASS:
1. Refresh p7-gate preview from new branch tip (no traffic shift to live)
2. UX Designer + Field Tester re-gate on grokbot
3. HARD gate item: 1-2 invoice PDFs end-to-end through "Open Invoice Importer"
4. CAC/PCGS cert-photo scan returning in ≤30s

**OVER.**
