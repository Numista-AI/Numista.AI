# GEMINI38_REVIEW — P7 V8.18.6 Build
**Reviewed by:** Gemini 3.8 Flash (AG CoS pipeline)  
**Rule 9.3:** One review per build version — this is the V8.18.6 review.  
**Code commit SHA:** `4c42d1f50ff1875143b469fc5ec4b7d526fa9c8f`  
**Base commit SHA:** `4531f45d2a765ec8308145eec67deb3de5e9de7d`  
**Branch:** `origin/p7-v8.9`  
**Review date:** 2026-10-19  

---

## Verification Method

All cited lines verified with:
```bash
git show 4c42d1f50ff1875143b469fc5ec4b7d526fa9c8f:<filepath>
```
and:
```bash
git diff 4531f45d2a765ec8308145eec67deb3de5e9de7d 4c42d1f50ff1875143b469fc5ec4b7d526fa9c8f
```
**EVERY cite below includes verbatim quoted lines from the commit diff.** No invented code.

---

## Summary of Results

| Suite / Gate | Result | Details |
|--------------|--------|---------|
| `flutter analyze lib/` | ✅ PASS | 0 issues found |
| `flutter test test/p7_v8_ux_safety_test.dart` | ✅ PASS | 75/75 passed (0 failures) |
| `flutter test --reporter compact` (full suite) | ✅ PASS | 595/595 passed (0 failures) |
| `py -m pytest numista_backend/tests/test_cert_lookup.py` | ✅ PASS | 20/20 passed (8.53s) |
| Git Hygiene | ✅ PASS | Pushed to `origin/p7-v8.9`, 0 changes to `main`, no deployment |

---

## Must-Fix Item 2 — Same Cert Reader Inside the Budget (NET-357 Order)

**Files Modified:**
- `numista_backend/routes/cert_routes.py`
- `numista_backend/main.py`
- `numista_backend/tests/test_cert_lookup.py`

### Condition 1: Friendly User Error Message Restored (No Raw Exception Text)
**File:** `numista_backend/routes/cert_routes.py:448-456`

Verbatim code from `git show 4c42d1f5:numista_backend/routes/cert_routes.py`:
```python
448:    except Exception as e:
449:        logger.warning(f"extract_cert_from_image failed: {e}")
450:        return {
451:            "cert_number": None,
452:            "grader": None,
453:            "confidence": "LOW",
454:            "message": "Scan failed — please enter cert # manually.",
455:        }
```
- Replaced `f"Scan failed: {e}"` with `"Scan failed — please enter cert # manually."`.
- Exception details logged server-side via `logger.warning`.

### Condition 2: Non-Blocking Helper with Request Budget Timeout
**File:** `numista_backend/main.py:6156-6178`

Verbatim code from `git show 4c42d1f5:numista_backend/main.py`:
```python
6156:async def _extract_cert_with_budget(
6157:    image_bytes: bytes,
6158:    mime_type: str = "image/jpeg",
6159:    timeout: float = 10.0,
6160:) -> Dict[str, Any]:
6161:    """
6162:    Executes extract_cert_from_image in a worker thread with timeout,
6163:    keeping the event loop unblocked and respecting the request budget.
6164:    """
6165:    if timeout <= 0.1 or not image_bytes:
6166:        return {}
6167:    try:
6168:        return await asyncio.wait_for(
6169:            asyncio.to_thread(extract_cert_from_image, image_bytes, mime_type=mime_type),
6170:            timeout=timeout,
6171:        )
6172:    except asyncio.TimeoutError:
6173:        logger.warning(f"Shared cert extractor timed out after {timeout:.1f}s")
6174:        return {}
6175:    except Exception as exc:
6176:        logger.warning(f"Shared cert extractor error: {exc}")
6177:        return {}
```
- Uses `asyncio.to_thread` to run OCR in worker thread pool without blocking asyncio event loop.
- Uses `asyncio.wait_for` with dynamic budget timeout.

### Condition 3: Concurrently Started with Pass 1
**File:** `numista_backend/main.py:6247-6254, 6282-6294`

Verbatim code from `git show 4c42d1f5:numista_backend/main.py`:
```python
6247:    # -- 2. Start shared cert reader concurrently with Pass 1 (NET-357 / Item 2)
6248:    _elapsed_so_far = time.monotonic() - _req_start
6249:    _cert_budget_a = max(0.0, GEMINI_IDENTIFY_BUDGET - _elapsed_so_far)
6250:    cert_task: Optional[asyncio.Task] = None
6251:    if _cert_budget_a > 0.5:
6252:        cert_task = asyncio.create_task(
6253:            _extract_cert_with_budget(bytes_a, mime_type=mime_a, timeout=_cert_budget_a)
6254:        )
```
```python
6282:    except asyncio.TimeoutError:
6283:        if cert_task and not cert_task.done():
6284:            cert_task.cancel()
6285:        raise HTTPException(status_code=408, detail="Image identification timed out. Please try again.")
6286:    except HTTPException:
6287:        if cert_task and not cert_task.done():
6288:            cert_task.cancel()
6289:        raise
6290:    except Exception as e:
6291:        if cert_task and not cert_task.done():
6292:            cert_task.cancel()
6293:        logger.exception("Coin ID pass 1 error")
6294:        raise HTTPException(status_code=500, detail="AI identification failed. Please try again.")
```
- Started via `asyncio.create_task` before Pass 1 so both run concurrently; adds zero wall-clock time.
- Cancelled cleanly in Pass 1 error handling.

### Condition 4: Image B Gated Behind Budget (>= 3s)
**File:** `numista_backend/main.py:6412-6418`

Verbatim code from `git show 4c42d1f5:numista_backend/main.py`:
```python
6412:    # Image B only if Image A found no cert and >= 3.0s budget remains
6413:    if not cert_read.get("cert_number") and not single_image_mode and bytes_b:
6414:        _rem_b = GEMINI_IDENTIFY_BUDGET - (time.monotonic() - _req_start)
6415:        if _rem_b >= 3.0:
6416:            logger.info(f"Image A had no cert; running shared cert reader on Image B ({_rem_b:.1f}s budget left)")
6417:            cert_read = await _extract_cert_with_budget(bytes_b, mime_type=mime_b, timeout=_rem_b)
6418:        else:
6419:            logger.info(f"Skipping Image B cert extraction: only {_rem_b:.1f}s left of {GEMINI_IDENTIFY_BUDGET}s budget")
```
- Only queries Image B if Image A had no cert and remaining budget is `>= 3.0s`.

### Condition 5: Shared Reader Cert Wins Over Pass 1 / Pass 2 Cert
**File:** `numista_backend/main.py:6420-6435`

Verbatim code from `git show 4c42d1f5:numista_backend/main.py`:
```python
6420:    pass_cert = pass2.get("cert_number") or pass1.get("cert_number") or ""
6421:    pass_service = pass2.get("grading_service") or pass1.get("grading_service") or ""
6422:
6423:    shared_cert = (cert_read.get("cert_number") or "").strip()
6424:    shared_service = (cert_read.get("grader") or "").strip()
6425:
6426:    if shared_cert:
6427:        final_cert = shared_cert
6428:        final_service = shared_service or pass_service
6429:    else:
6430:        # Fallback to Pass 1 / Pass 2 if shared reader returned no cert
6431:        final_cert = pass_cert
6432:        final_service = pass_service
6433:
6434:    if str(final_service).strip().lower() == "none":
6435:        final_service = ""
```
- When shared reader yields a cert, `shared_cert` wins unconditionally over Pass 1 / Pass 2.
- Pass 1 / Pass 2 cert is strictly fallback when shared reader finds none.

### Condition 6: Pytest (a) — Pass 1 says X, Shared Reader says Y → Both Endpoints Return Y
**File:** `numista_backend/tests/test_cert_lookup.py:459-537`

Verbatim code from `git show 4c42d1f5:numista_backend/tests/test_cert_lookup.py`:
```python
459:def test_shared_cert_reader_wins_over_pass1(monkeypatch):
460:    """
461:    NET-357 Item 2 (a):
462:    Pass 1 mock returns cert X ("PASS1-CERT-11111"),
463:    Shared reader mock returns cert Y ("53652580").
464:    Both /api/scan_cert_number_upload and /api/identify_coin_photo must return Y.
465:    """
```
```python
536:        # Both endpoints return Y
537:        assert data1.get("cert_number") == coin2.get("cert_number") == expected_cert
```
- Verified test passes: endpoint 1 returns `"53652580"`, endpoint 2 returns `"53652580"` and `"PCGS"`, overriding Pass 1's `"PASS1-CERT-11111"` and `"NGC"`.

### Condition 7: Pytest (b) — Shared Reader Sleeps Past Budget → Returns < 28s, No Cert, No 500
**File:** `numista_backend/tests/test_cert_lookup.py:540-600`

Verbatim code from `git show 4c42d1f5:numista_backend/tests/test_cert_lookup.py`:
```python
540:def test_shared_cert_reader_budget_timeout_no_500(monkeypatch):
541:    """
542:    NET-357 Item 2 (b):
543:    Shared reader sleeps past budget -> identify returns < 28 s, no cert, no 500.
544:    """
```
```python
592:    # Must return cleanly in < 28 s without 500
593:    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
594:    assert elapsed < 28.0, f"Took too long: {elapsed}s >= 28s"
595:    coin = resp.json().get("coin", {})
596:    # No cert extracted (timed out)
597:    assert not coin.get("cert_number")
598:    assert not coin.get("Certification Number")
```
- Verified test passes: reader sleeps past budget, endpoint cleanly returns HTTP 200 with empty cert in `< 28s` without a 500 error.

---

## Verdict

**Recommendation: APPROVED for Grok CoS Scoring.**  
All requirements from NET-357 / COS_SCORE V8.18.5 are completely resolved and verified against the live test suites. All 595 Flutter tests pass, 20 backend tests pass, and zero analyzer issues exist. Commit `4c42d1f50ff1875143b469fc5ec4b7d526fa9c8f` is cleanly pushed to `origin/p7-v8.9`.
