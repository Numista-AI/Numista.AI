# EXECUTE DONE — P7 V8.18.6
Builder: AG CoS | 2026-10-19 ~16:20 ET | Worktree: `C:\Users\ericd\AppData\Local\Temp\p7v89_build`

## Commit SHA
**Code (p7-v8.9):** `4c42d1f50ff1875143b469fc5ec4b7d526fa9c8f`  
Parent: `4531f45d2a765ec8308145eec67deb3de5e9de7d`  
Branch: `origin/p7-v8.9` (NEVER main)

## Test Counts
- `flutter analyze lib/` → **0 errors, 0 warnings**
- `flutter test test/p7_v8_ux_safety_test.dart` → **75 pass, 0 failures**
- `flutter test --reporter compact` → **595 pass, 0 failures**
- `py -m pytest numista_backend/tests/test_cert_lookup.py` → **20 passed** (8.53s)

---

## Item 2 Fix — Unified Cert Reader Inside Request Budget with Precedence

### Root Cause in V8.18.5
In V8.18.5, `identify_coin_photo` called `extract_cert_from_image` synchronously after Pass 2 only `if not final_cert:`. This caused:
1. When Pass 1/2 found a cert, the old reader won, allowing the endpoints to disagree.
2. Synchronous execution in an async endpoint blocked the event loop.
3. It ran outside the 28s request budget clock, risking timeouts and incurring redundant Gemini cost on non-slab photos.
4. Error handling returned `f"Scan failed: {e}"`, exposing raw exception text to users.

### Fix Implementation in V8.18.6

#### 1. Non-Blocking Helper with Budget Timeout
**File:** `numista_backend/main.py:6156-6178`
```python
async def _extract_cert_with_budget(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """
    Executes extract_cert_from_image in a worker thread with timeout,
    keeping the event loop unblocked and respecting the request budget.
    """
    if timeout <= 0.1 or not image_bytes:
        return {}
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(extract_cert_from_image, image_bytes, mime_type=mime_type),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        logger.warning(f"Shared cert extractor timed out after {timeout:.1f}s")
        return {}
    except Exception as exc:
        logger.warning(f"Shared cert extractor error: {exc}")
        return {}
```

#### 2. Start Concurrently with Pass 1
**File:** `numista_backend/main.py:6247-6254, 6282-6294`
- Launched via `asyncio.create_task` before Pass 1 so it runs in parallel in the thread pool, adding zero wall-clock time.
- Cleanly cancelled in Pass 1 `except` blocks if Pass 1 fails or times out.

#### 3. Image B Gated Behind Remaining Budget (>= 3s)
**File:** `numista_backend/main.py:6408-6418`
- If Image A yields no cert, Image B is only queried if `not single_image_mode` AND remaining budget `>= 3.0s`.
- If budget is `< 3.0s`, Image B is skipped with an info log, protecting the 28s budget.

#### 4. Shared Reader Precedence Over Pass 1 / Pass 2
**File:** `numista_backend/main.py:6420-6435`
- Shared reader cert and grader win:
  ```python
  if shared_cert:
      final_cert = shared_cert
      final_service = shared_service or pass_service
  else:
      # Fallback to Pass 1 / Pass 2 if shared reader returned no cert
      final_cert = pass_cert
      final_service = pass_service
  ```

#### 5. Friendly User Error Message Restored
**File:** `numista_backend/routes/cert_routes.py:448-456`
```python
    except Exception as e:
        logger.warning(f"extract_cert_from_image failed: {e}")
        return {
            "cert_number": None,
            "grader": None,
            "confidence": "LOW",
            "message": "Scan failed — please enter cert # manually.",
        }
```
No raw exception strings are exposed; details are logged server-side only.

---

## Pytests Added

### 1. Precedence Test: Pass 1 says X, Shared Reader says Y → Both Endpoints Return Y
**File:** `numista_backend/tests/test_cert_lookup.py:459-537` (`test_shared_cert_reader_wins_over_pass1`)
- Pass 1 mocked to return cert `"PASS1-CERT-11111"` and grader `"NGC"`.
- Shared reader mocked to return cert `"53652580"` and grader `"PCGS"`.
- Verifies `/api/scan_cert_number_upload` returns `"53652580"`.
- Verifies `/api/identify_coin_photo` returns `"53652580"` and `"PCGS"`, overriding Pass 1.
- Both endpoints assert equal output.

### 2. Budget Timeout Test: Shared Reader Sleeps Past Budget → Returns < 28s, No Cert, No 500
**File:** `numista_backend/tests/test_cert_lookup.py:540-600` (`test_shared_cert_reader_budget_timeout_no_500`)
- `extract_cert_from_image` mocked to sleep 1.5s.
- `GEMINI_IDENTIFY_BUDGET` monkeypatched to 0.4s.
- Measures response time: `elapsed < 28.0s`.
- Verifies HTTP 200 (no 500), coin returned cleanly, `cert_number` empty (no cert).

---

## Preserved Code
All previous V8.18.5 fixes (One error card, ValueKey finders, camera header, localhost HttpOverrides proof, config test glob, morgan avatar path) remain 100% intact.
