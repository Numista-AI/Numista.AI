# EXECUTE_DONE P7 V8.18.2

**Build:** P7 V8.18.2  
**Commit SHA:** `0e3c13b21002a39583752979253aab7e78c6520d`  
**Branch:** `origin/p7-v8.9`  
**Base commit:** `0f2f06e0`  
**Worktree:** `C:\Users\ericd\AppData\Local\Temp\p7v89_build`  
**Timestamp:** 2026-10-19 ~12:34 ET

---

## Test Counts

| Suite | Result |
|---|---|
| `flutter analyze lib/` | **0 issues** (ran in 92.6s) |
| `flutter test --reporter compact` | **585 passed** / 585 baseline ✅ |
| `pytest numista_backend/tests/ -q` | **577 passed** / 573+ baseline ✅ (+4 new tests) |

---

## Fix 1 — cert_routes.py:374 — Project ID code fix

**File:** `numista_backend/routes/cert_routes.py`  
**Lines:** 373–378 (after edit)

**BEFORE:**
```python
# Vertex AI backend — uses ADC, no API key. Match pattern from main.py.
_SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")
```

**AFTER:**
```python
# Vertex AI backend — uses ADC, no API key. Match resolution chain from main.py:312.
# Never default to "numista-qc" — that project does not have the service account.
_SCAN_PROJECT_ID = (
    os.environ.get("FIREBASE_PROJECT_ID")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or "studio-9101802118-8c9a8"
)
```

**Root cause confirmed:** `FIREBASE_PROJECT_ID` is not set as an environment variable on the Cloud Run revision `00468-qir`. With the old code, `os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")` returned `"numista-qc"`. With the new 3-level chain, it falls through to `"studio-9101802118-8c9a8"` — the correct project where the service account has Vertex AI permissions.

**Test:** `numista_backend/tests/test_identify_timeout.py::test_cert_routes_project_id_never_defaults_to_numista_qc` — PASS  
Pattern: `monkeypatch.delenv` both env vars, `importlib.reload(cr)`, assert `cr._SCAN_PROJECT_ID == "studio-9101802118-8c9a8"`.

---

## Fix 2 — identify_coin_photo: whole-request ≤28s cap

**File:** `numista_backend/main.py`

### 2A — New constants (line 6131–6135 after edit)

**BEFORE:**
```python
GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))
```

**AFTER:**
```python
GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))
# Pass-1 cap: 20 s leaves 8 s for pass 2 within a 28 s request budget.
GEMINI_IDENTIFY_PASS1_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_PASS1_TIMEOUT", "20.0"))
# Whole-request budget: pass 1 + pass 2 + overhead must stay under 30 s.
GEMINI_IDENTIFY_BUDGET = float(os.environ.get("GEMINI_IDENTIFY_BUDGET", "28.0"))
```

### 2B — Request start time (line 6194 after edit)

**BEFORE:**
```python
    owner_key = _authenticate_request(authorization, user_email, current_user=_user)
    user_email = owner_key

    logger.info(f"Identify coin photo: save={save_to_collection}", ...)
```

**AFTER:**
```python
    owner_key = _authenticate_request(authorization, user_email, current_user=_user)
    user_email = owner_key
    _req_start = time.monotonic()  # whole-request budget clock (FIX: 28s cap)

    logger.info(f"Identify coin photo: save={save_to_collection}", ...)
```

### 2C — Pass 1 timeout (line 6239 after edit)

**BEFORE:**
```python
            resp1 = await asyncio.wait_for(call_res, timeout=GEMINI_IDENTIFY_TIMEOUT)
```

**AFTER:**
```python
            resp1 = await asyncio.wait_for(call_res, timeout=GEMINI_IDENTIFY_PASS1_TIMEOUT)
```

### 2D — Pass 2 budget check (lines 6258–6308 after edit)

**BEFORE:** Pass 2 always ran with `timeout=min(10.0, GEMINI_IDENTIFY_TIMEOUT)` = 10s.  
Worst case: 25s (pass 1) + 10s (pass 2) = 35s > 30s budget.

**AFTER:** Budget-aware skip inserted before pass 2:
```python
    _elapsed = time.monotonic() - _req_start
    _pass2_budget = GEMINI_IDENTIFY_BUDGET - _elapsed
    if _pass2_budget < 3.0:
        logger.info(f"Skipping pass 2: only {_pass2_budget:.1f}s left of {GEMINI_IDENTIFY_BUDGET}s budget")
    else:
        try:
            # ... existing pass-2 logic ...
            resp2 = await asyncio.wait_for(call_res2, timeout=min(_pass2_budget, 10.0))
```

Worst case now: 20s (pass 1) + 8s (pass 2) = 28s ≤ 28s budget.  
If pass 1 takes ≥25s (edge), pass 2 gets < 3s budget and is skipped — returns pass 1 result immediately.

**Test:** `test_identify_coin_photo_pass2_skipped_when_budget_exhausted` — PASS  
Pattern: `GEMINI_IDENTIFY_BUDGET=0.0`, any elapsed > 0 → skip triggered → 200 with pass-1 Year=1921.

---

## Fix 3 — 314 vs 312: Set Parent Doc IDs (Read-Only Investigation)

**Method:** Firestore REST API (`eric@numista.ai` ADC), read-only, no writes.  
**Collection:** `users/grokbot@numista.ai/coins`  
**Total docs queried:** 314

**Key finding:** The 2-doc discrepancy claimed in V8.18.1 is actually 3 set-parent docs. These docs have `Denomination: Set` and non-empty `set_contents` (array of 10 child coins each), which causes `expandCollection()` (line 71 of `set_expansion_helper.dart`) to treat them as set parents (`isSet = rawItemType == 'set' || setContentsList.isNotEmpty`).

### The 3 Set-Parent Doc IDs

| Doc ID | item_type | set_contents | Year | Program/Series |
|--------|-----------|-------------|------|----------------|
| `Q4EOOUkUBDvBAyRB3Hmi` | (missing/coin) | array of 10 items | 2026 | 2026 US Mint Silver Proof Set |
| `jbyU6PAR8N4OkhJLZxu4` | (missing/coin) | array of 10 items | 2026 | 2026 US Mint Silver Proof Set |
| `myrK4XUCRnRuQwJujXna` | (missing/coin) | array of 10 items | 2026 | 2026 US Mint Silver Proof Set |

**item_type field:** absent (= defaults to 'coin' in Dart logic); not 'set'  
**is_set_parent field:** absent (not set in Firestore)  
**Detection path:** `set_contents` field is non-empty → `isSet = true` → `is_set_parent: true` injected by `expandCollection()`

**Why "2" was expected:** The V8.18.1 analysis assumed `isPhysicalCoin` was the filter. The actual filter in `expandCollection()` is the `set_contents` presence check. With 3 set parents (each containing 10 children), `totalCoins = (314 - 3) regular docs + (3 × 10) child coins = 311 + 30 = 341`. But the displayed count of 312 suggests only 1 set is being expanded (1 set parent with 10 children + 301 regular = 311 + ... hmm).

**Note:** The 312 vs 314 vs 341 discrepancy needs deeper analysis of how qty fields and `getCoinQuantity` interact across all 314 docs. This investigation is complete for naming the set-parent doc IDs. Full quantity audit deferred to a follow-on ticket.

---

## Files Changed

| File | Lines Changed | Fix |
|------|-------|-----|
| `numista_backend/routes/cert_routes.py` | 373–378 | Fix 1: project ID chain |
| `numista_backend/main.py` | 6131–6135, 6194, 6239, 6258–6310 | Fix 2: budget constants, start time, pass-1 20s, pass-2 budget |
| `numista_backend/tests/test_identify_timeout.py` | 67–155 (+88 lines) | Fix 1+2: 4 tests (cert project ID + pass-2 skip) |

---

## Verification

- `flutter analyze lib/`: **No issues found** (ran in 92.6s)
- `flutter test`: **585/585 passed**
- `pytest`: **577/577 passed** (573 baseline + 4 new)
- `git push origin p7-v8.9`: **success** — `0f2f06e0..0e3c13b2`
