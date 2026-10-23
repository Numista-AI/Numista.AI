# NET-448 GROKCOS -> AGCOS : P7 V8.18.15g ONE FIX - DUPLICATE_CHECK IMPORT PATH (OVER)
23 Oct 2026 ~11:25 AM ET | Base: branch p7-v8.9 @ ba37c03e (V8.18.15f) | Process: 1 NUMISTA.AI\BETA TEST\Grok Bot\23 OCT 26\FT_GATE_PROCESS_PLAN.md (Rule 1 + Rule 2)

MODEL / COST: Gemini Flash, LOW thinking. FRESH chat. Touch ONLY the files and lines named below. Do not read or refactor anything else.

WHY: V8.18.15f failed the gate. Every Review Hub commit (invoice, ASE, CSV) returns 500. Cloud Run log, p7gate revision numista-backend-00484-hiz, 23 Oct 11:08:12 AM ET:
  File "/app/main.py", line 3583, in commit_reviews
    from numista_backend.services.duplicate_check import check_and_flag_duplicate
  ModuleNotFoundError: No module named 'numista_backend'
The container copies numista_backend/ to /app and runs `uvicorn main:app`, so there is no `numista_backend` package at runtime. Tests passed only because pytest runs from the repo root.

THE ONE FIX (V8.18.15g). In numista_backend/, change
  from numista_backend.services.duplicate_check import check_and_flag_duplicate
to
  from services.duplicate_check import check_and_flag_duplicate
at exactly these 4 lines:
  1. main.py:3583              (commit_reviews)
  2. main.py:6543              (photo-scan save)
  3. routes/import_routes.py:272 (staging import)
  4. routes/cert_routes.py:361   (cert save; it is inside try/except, so it fails silently today)
ADD one test: numista_backend/tests/test_container_import_path.py. It runs a subprocess with cwd=numista_backend/ and sys.path holding ONLY numista_backend/ (no repo root, the way the container runs). It imports main and imports services.duplicate_check, and fails on any ModuleNotFoundError.
Version bump to v8.18.15g (kAppVersion + pubspec) is allowed. NOTHING ELSE.

RULE 1 ENTRY GATE (attach before handing to FT; no proof = the build goes back):
  a. Screenshot or log proof, using the grokbot account or the Firebase emulator ONLY, of a Review Hub commit that saves with no error (HTTP 200 plus the committed count).
  b. Full pytest output (pass count) and the full `flutter test` output (pass count). Report the exact counts you ran.
  c. The new test FAILING on ba37c03e and PASSING on 15g (paste both).
Put this proof in EXECUTE_DONE_P7_V8_18_15g.md in BATONS, then radio GROKCOS.

RULES: Commit to dev by EXPLICIT PATH only (never `git commit -a`). NO deploy, NO main, NO Firestore writes (the emulator or grokbot via the app UI only), NO sync_canon. Stand down by 3 AM.
Everything else in the baton QUEUE stays QUEUED. Do not start it.
OVER.
