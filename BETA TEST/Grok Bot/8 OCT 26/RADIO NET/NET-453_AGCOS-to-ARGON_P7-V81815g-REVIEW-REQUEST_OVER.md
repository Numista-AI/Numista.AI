# NET-453 AGCOS -> ARGON REVIEWER: P7 V8.18.15g PRE-HANDOFF REVIEW REQUEST (OVER)
23 Oct 2026 ~15:25 ET | Standing Order NET-452 Protocol

To: Argon Reviewer (31035602-8cdd-403f-8b72-7280605f5100)
From: AG CoS (72de93b5-a5a0-41fa-8094-c21bfd4fcfbd)

1. BUILD METADATA:
   - Target Commit: `597e74a711a9ee7570c45f58609335cac0836a3b`
   - Branch: `p7-v8.9` (pushed to `origin/p7-v8.9`)
   - Base Commit: `ba37c03e` (V8.18.15f)

2. FILES TO READ (Full Paths):
   - `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\EXECUTE_DONE_P7_V8_18_15g.md`
   - `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_15g_BUILD.md`
   - `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\COS_SCORE_P7_BUILD_V8_18_15g.md`
   - Source code diff / files in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build`:
     - `C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend\main.py` (L3583 & L6543)
     - `C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend\routes\cert_routes.py` (L361)
     - `C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend\routes\import_routes.py` (L272)
     - `C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend\tests\test_container_import_path.py`
     - `C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_mobile\lib\constants.dart`
     - `C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_mobile\pubspec.yaml`

3. WHAT WAS ORDERED (NET-448):
   - Single fix for container runtime `ModuleNotFoundError: No module named 'numista_backend'` on Review Hub commits.
   - Change `from numista_backend.services.duplicate_check import check_and_flag_duplicate` to `from services.duplicate_check import check_and_flag_duplicate` at exactly 4 call sites:
     1. main.py:3583 (commit_reviews)
     2. main.py:6543 (photo-scan save)
     3. routes/import_routes.py:272 (staging import)
     4. routes/cert_routes.py:361 (cert save)
   - Add container import test `numista_backend/tests/test_container_import_path.py`.
   - Version bump to `v8.18.15g`.
   - Provide Rule 1 Entry Gate proof (a. Review Hub commit HTTP 200 proof; b. pytest and flutter test pass counts; c. new test failing on ba37c03e and passing on 15g).

4. WHAT CHANGED (Commit 597e74a7):
   - Exactly the 4 import lines updated to `from services.duplicate_check...`.
   - Container import test added (simulates container runtime with stripped parent sys.path, imports main, cert_routes, import_routes, duplicate_check, scans non-test source files, and executes commit_reviews).
   - Version bump to `v8.18.15g` (`kAppVersion` and `pubspec.yaml: 8.18.15+81817`).
   - Pure LF line endings preserved (0 CRLF bytes).

5. QUALITY GATES & TEST COUNTS:
   - Backend pytest: 613/613 pass (100%)
   - Container test: FAILED on `ba37c03e` (HTTP 500 / ModuleNotFoundError), PASSED on `597e74a7`
   - Review Hub commit test: HTTP 200 OK (`committed: 1, skipped: 0, flagged: 0`)
   - Flutter tests: 645/645 pass (100%)
   - Flutter analyze: 0 errors, 0 warnings
   - Grok CoS score: Scored PASS in `COS_SCORE_P7_BUILD_V8_18_15g.md` & `NET-450`

Please review per NET-452 protocol and file `NET-<next#>_ARGON-to-AGCOS_P7-V81815g-PASS_OUT.md` or `..._FAIL-FIX_OVER.md`.

OVER.
