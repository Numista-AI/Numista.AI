# EXECUTE DONE: P7 V8.18.15g — DUPLICATE_CHECK IMPORT PATH FIX
**Date / Time:** 2026-10-23 ~14:25 ET  
**Base Commit:** `ba37c03e` (V8.18.15f)  
**Build Commit:** `597e74a7` (pushed to `origin/p7-v8.9`)  
**Order Reference:** `NET-448_GROKCOS-to-AGCOS_P7-V81815g-IMPORT-PATH-FIX_OVER.md` & `NET-449`  

---

## 1. Summary of Changes
Surgically resolved `ModuleNotFoundError: No module named 'numista_backend'` caused by container runtime execution (where `/app` contains `numista_backend/` directly and `sys.path` does not contain a top-level `numista_backend` package).

Replaced:
```python
from numista_backend.services.duplicate_check import check_and_flag_duplicate
```
with:
```python
from services.duplicate_check import check_and_flag_duplicate
```
at exactly the 4 requested call sites:
1. `numista_backend/main.py:3583` (`commit_reviews`)
2. `numista_backend/main.py:6543` (`identify_coin_photo` scan save)
3. `numista_backend/routes/import_routes.py:272` (`commit_batch` staging import)
4. `numista_backend/routes/cert_routes.py:361` (`cert_save`)

Added container-mode import test:
- `numista_backend/tests/test_container_import_path.py`

Version bump:
- `numista_mobile/lib/constants.dart`: `kAppVersion = 'v8.18.15g'`
- `numista_mobile/pubspec.yaml`: `version: 8.18.15+81817`

---

## 2. Rule 1 Entry Gate Proof

### (a) Review Hub Commit Proof (HTTP 200 + Committed Count)
Executed via FastAPI `TestClient` against `/api/review/commit` using `grokbot@numista.ai` account context:

```
INFO    [main] [9819659a] POST /api/review/commit -> 200 (50ms)
INFO:httpx:HTTP Request: POST http://testserver/api/review/commit "HTTP/1.1 200 OK"
HTTP_STATUS: 200
HTTP_RESPONSE: {'status': 'success', 'message': 'Committed 1 items. Skipped 0 duplicates. Flagged 0 possible duplicates.', 'committed': 1, 'skipped': 0, 'flagged': 0}
```

### (b) Quality Gate Test Counts
- **Backend pytest:** `613 passed, 258 warnings in 124.03s (0:02:04)` (100% pass across full suite)
- **Flutter tests:** `645 passed` (`01:06 +645: All tests passed!`)
- **Flutter analyze:** `0 errors, 0 warnings` (`No issues found! (ran in 553.9s)`)
- **Line endings:** Pure LF, 0 CRLF bytes across all 6 modified/created files.

### (c) Container Import Path Test: Before vs After Output

#### FAILING Output on `ba37c03e` (Base):
```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend
configfile: pytest.ini
plugins: anyio-4.12.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 1 item

numista_backend\tests\test_container_import_path.py::test_container_import_path FAILED [100%]

================================== FAILURES ===================================
_________________________ test_container_import_path __________________________
    ...
    AssertionError: Container import test failed (exit code 1):
    File "C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend\main.py", line 3583, in commit_reviews
        from numista_backend.services.duplicate_check import check_and_flag_duplicate
    ModuleNotFoundError: No module named 'numista_backend'
    fastapi.exceptions.HTTPException: 500: No module named 'numista_backend'
=========================== short test summary info ===========================
FAILED numista_backend\tests\test_container_import_path.py::test_container_import_path
============================== 1 failed in 42.16s ==============================
```

#### PASSING Output on `597e74a7` (V8.18.15g):
```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend
configfile: pytest.ini
plugins: anyio-4.12.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 1 item

numista_backend\tests\test_container_import_path.py::test_container_import_path PASSED [100%]

======================== 1 passed in 63.03s (0:01:03) =========================
```

---

## 3. Git Push Confirmation
- Target branch: `p7-v8.9`
- Base: `ba37c03e`
- Head: `597e74a7`
- Push status: `ba37c03e..597e74a7  p7-v8.9 -> p7-v8.9` (confirmed)
