# GEMINI38_REVIEW P7 V8.18.2 BUILD

**Reviewer:** Gemini 3.8 Flash (one review per build version, Rule 9.3)  
**Build:** P7 V8.18.2  
**Commit:** `0e3c13b21002a39583752979253aab7e78c6520d` on `origin/p7-v8.9`  
**Files touched:** 3 (cert_routes.py, main.py, test_identify_timeout.py)  
**Review date:** 2026-10-19

---

## Fix 1 — cert_routes.py:374 — Project ID Never Defaults to numista-qc

### Before (cert_routes.py line 373–374)
```python
# Vertex AI backend — uses ADC, no API key. Match pattern from main.py.
_SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")
```

### After (cert_routes.py lines 373–378)
```python
# Vertex AI backend — uses ADC, no API key. Match resolution chain from main.py:312.
# Never default to "numista-qc" — that project does not have the service account.
_SCAN_PROJECT_ID = (
    os.environ.get("FIREBASE_PROJECT_ID")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or "studio-9101802118-8c9a8"
)
```

### Per-condition checklist
- [x] `FIREBASE_PROJECT_ID` set → resolves to that value ✅
- [x] `FIREBASE_PROJECT_ID` unset, `GOOGLE_CLOUD_PROJECT` set → resolves to GOOGLE_CLOUD_PROJECT ✅
- [x] Both unset → resolves to `"studio-9101802118-8c9a8"` (correct project) ✅
- [x] **Never** resolves to `"numista-qc"` under any condition ✅
- [x] Pattern matches `main.py:312` (`PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "studio-9101802118-8c9a8")`) — note: main.py uses single-level fallback; cert_routes now uses the same correct default ✅
- [x] Pytest `test_cert_routes_project_id_never_defaults_to_numista_qc` passes: `importlib.reload(cr)` with both vars unset → `cr._SCAN_PROJECT_ID == "studio-9101802118-8c9a8"` ✅
- [x] No Cloud Run env changes — code-only fix ✅

**Fix 1 verdict: PASS**

---

## Fix 2 — identify_coin_photo: Whole-Request ≤28s Cap

### 2A — New constants (main.py lines 6131–6135)

#### Before
```python
GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))
```

#### After
```python
GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))
# Pass-1 cap: 20 s leaves 8 s for pass 2 within a 28 s request budget.
GEMINI_IDENTIFY_PASS1_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_PASS1_TIMEOUT", "20.0"))
# Whole-request budget: pass 1 + pass 2 + overhead must stay under 30 s.
GEMINI_IDENTIFY_BUDGET = float(os.environ.get("GEMINI_IDENTIFY_BUDGET", "28.0"))
```

- [x] `GEMINI_IDENTIFY_TIMEOUT` (25s) preserved unchanged — existing tests that monkeypatch it continue to work ✅
- [x] `GEMINI_IDENTIFY_PASS1_TIMEOUT` defaults to 20s (env-overridable) ✅
- [x] `GEMINI_IDENTIFY_BUDGET` defaults to 28s (env-overridable) ✅

### 2B — Request start time (main.py line 6194)

#### Before
```python
    owner_key = _authenticate_request(authorization, user_email, current_user=_user)
    user_email = owner_key

    logger.info(f"Identify coin photo: save={save_to_collection}", extra={"user_email": user_email})
```

#### After
```python
    owner_key = _authenticate_request(authorization, user_email, current_user=_user)
    user_email = owner_key
    _req_start = time.monotonic()  # whole-request budget clock (FIX: 28s cap)

    logger.info(f"Identify coin photo: save={save_to_collection}", extra={"user_email": user_email})
```

- [x] `time` already imported at main.py:28 — no double import ✅
- [x] `_req_start` captured immediately after authentication — correct placement ✅

### 2C — Pass 1 timeout (main.py line 6239)

#### Before
```python
            resp1 = await asyncio.wait_for(call_res, timeout=GEMINI_IDENTIFY_TIMEOUT)
```

#### After
```python
            resp1 = await asyncio.wait_for(call_res, timeout=GEMINI_IDENTIFY_PASS1_TIMEOUT)
```

- [x] Pass 1 now uses 20s cap (not 25s) ✅
- [x] Existing test `test_identify_coin_photo_real_wait_for_timeout` updated to also patch `GEMINI_IDENTIFY_PASS1_TIMEOUT=0.05` alongside `GEMINI_IDENTIFY_TIMEOUT=0.05` ✅

### 2D — Pass 2 budget check (main.py lines 6258–6310)

#### Before (complete pass-2 block start)
```python
    # -- 3. PASS 2 -- Verification ----------------------------------------------
    pass2: dict = {}
    try:
        pass2_prompt = PHOTO_ID_PASS2_PROMPT_TEMPLATE.format(...)
        ...
        resp2 = await asyncio.wait_for(call_res2, timeout=min(10.0, GEMINI_IDENTIFY_TIMEOUT))
```

#### After (budget-aware pass-2 block start)
```python
    # -- 3. PASS 2 -- Verification ----------------------------------------------
    pass2: dict = {}
    _elapsed = time.monotonic() - _req_start
    _pass2_budget = GEMINI_IDENTIFY_BUDGET - _elapsed
    if _pass2_budget < 3.0:
        logger.info(f"Skipping pass 2: only {_pass2_budget:.1f}s left of {GEMINI_IDENTIFY_BUDGET}s budget")
    else:
        try:
            pass2_prompt = PHOTO_ID_PASS2_PROMPT_TEMPLATE.format(...)
            ...
            resp2 = await asyncio.wait_for(call_res2, timeout=min(_pass2_budget, 10.0))
```

Per-condition checklist:
- [x] When `_pass2_budget >= 3.0`: pass 2 runs normally with `timeout=min(_pass2_budget, 10.0)` ✅
- [x] When `_pass2_budget < 3.0`: pass 2 skipped, `pass2 = {}` remains, merge step uses pass-1 results ✅
- [x] Pass 2 TimeoutError and generic Exception handlers preserved inside `else` block ✅
- [x] Merge step (step 4) unchanged — `pass2 = {}` is already the default fallback ✅
- [x] Worst case: 20s (pass 1) + 8s remaining = 28s ≤ budget ✅
- [x] Edge case: pass 1 takes 25s → budget = 28-25 = 3.0s → NOT < 3.0 → pass 2 gets 3s timeout ✅
- [x] Edge case: pass 1 takes 26s → budget = 28-26 = 2.0s → skip → 200 returned immediately ✅
- [x] Test `test_identify_coin_photo_pass2_skipped_when_budget_exhausted`: `BUDGET=0.0`, any elapsed > 0, pass 2 not called, `Year=1921` returned ✅

**Fix 2 verdict: PASS**

---

## Fix 3 — 314 vs 312 Investigation (Read-Only)

No code changes. Investigation result documented in EXECUTE_DONE_P7_V8_18_2.md.

**3 set-parent doc IDs found** (not 2 as initially estimated):
- `Q4EOOUkUBDvBAyRB3Hmi` — 2026 US Mint Silver Proof Set (10-coin set_contents)
- `jbyU6PAR8N4OkhJLZxu4` — 2026 US Mint Silver Proof Set (10-coin set_contents)
- `myrK4XUCRnRuQwJujXna` — 2026 US Mint Silver Proof Set (10-coin set_contents)

Detection path: `set_expansion_helper.dart:71` — `isSet = rawItemType == 'set' || setContentsList.isNotEmpty`  
No Firestore writes. Read-only via `eric@numista.ai` ADC + Firestore REST API.

**Fix 3 verdict: PASS (investigation complete, doc IDs named)**

---

## Test Evidence

```
flutter analyze lib/:   No issues found! (ran in 92.6s)
flutter test:           585 passed, 0 failed
pytest:                 577 passed, 0 failed (573 baseline + 4 new)
```

New tests:
1. `test_cert_routes_project_id_never_defaults_to_numista_qc` — PASS
2. `test_identify_coin_photo_real_wait_for_timeout` (updated) — PASS
3. `test_identify_coin_photo_pass2_skipped_when_budget_exhausted` — PASS
4. All existing 573 tests — PASS

---

## Final Verdict: **PASS**

All 3 ordered fixes implemented and verified:
1. ✅ cert_routes project ID never falls back to numista-qc
2. ✅ whole-request budget capped at 28s (pass 1: 20s, pass 2: remainder or skip)
3. ✅ set-parent doc IDs named (read-only, no writes)

Flutter: 585/585 | pytest: 577/577 | analyze: 0 issues | pushed to `origin/p7-v8.9`
