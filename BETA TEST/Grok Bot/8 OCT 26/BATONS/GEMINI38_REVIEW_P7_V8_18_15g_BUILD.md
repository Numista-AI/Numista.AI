# GEMINI38 BUILD REVIEW: P7 V8.18.15g (Commit 597e74a7)
**Reviewer:** Gemini 3.8 Flash (AG CoS)  
**Date:** 2026-10-23 ~14:25 ET  
**Target Commit:** `597e74a711a9ee7570c45f58609335cac0836a3b`  
**Base Commit:** `ba37c03e` (p7-v8.9)  
**Track:** Tier 1 (P7 Add-Coins Flow / Review Hub Commit)  

---

## 1. Verbatim Code Inspection vs `git show 597e74a7`

### Check 1: `numista_backend/main.py:3583` (commit_reviews import path)
```diff
@@ -3580,7 +3580,7 @@ async def commit_reviews(request: CommitReviewsRequest, _user: dict = Depends(ge
                 if not is_definite_dupe:
                     # Attribute-based check: Year + Mint + normalized Denomination
                     # MUST NEVER delete queue doc without committing! Flag as possible_duplicate.
-                    from numista_backend.services.duplicate_check import check_and_flag_duplicate
+                    from services.duplicate_check import check_and_flag_duplicate
                     if check_and_flag_duplicate(coins_ref, data, exclude_ids=request.review_ids):
                         is_possible_dupe = True
```
- **Verification:** Line 3583 replaces `from numista_backend.services.duplicate_check` with `from services.duplicate_check`. In container runtime (`/app`), `sys.path` contains `/app` where `services` is a direct top-level directory. Matches container environment specification.

### Check 2: `numista_backend/main.py:6543` (identify_coin_photo scan-save import path)
```diff
@@ -6540,7 +6540,7 @@ async def identify_coin_photo(
             "Added":                 firestore.SERVER_TIMESTAMP,
         }
 
-        from numista_backend.services.duplicate_check import check_and_flag_duplicate
+        from services.duplicate_check import check_and_flag_duplicate
         coins_ref = db.collection(f"users/{user_email}/coins")
         if check_and_flag_duplicate(coins_ref, coin_doc):
             ai_coin["possible_duplicate"] = True
```
- **Verification:** Line 6543 updated to `from services.duplicate_check import check_and_flag_duplicate`. Prevents `ModuleNotFoundError` on photo-scan save.

### Check 3: `numista_backend/routes/cert_routes.py:361` (cert_save import path)
```diff
@@ -358,7 +358,7 @@ def cert_save(
     dup_flag = None
     if req.coin_data and isinstance(req.coin_data, dict):
         try:
-            from numista_backend.services.duplicate_check import check_and_flag_duplicate
+            from services.duplicate_check import check_and_flag_duplicate
             if check_and_flag_duplicate(coins_ref, req.coin_data):
                 possible_dup = True
                 dup_flag = req.coin_data.get("duplicate_flag")
```
- **Verification:** Line 361 updated to `from services.duplicate_check import check_and_flag_duplicate`. Prevents silent catch/failure in cert_save dupe flagging.

### Check 4: `numista_backend/routes/import_routes.py:272` (commit_batch import path)
```diff
@@ -269,7 +269,7 @@ async def commit_batch(req: CommitBatchRequest, user: Dict[str, Any] = Depends(g
             coin_data["imported_at"] = datetime.now(timezone.utc).isoformat()
             coin_data["import_session_id"] = req.import_session_id
 
-            from numista_backend.services.duplicate_check import check_and_flag_duplicate
+            from services.duplicate_check import check_and_flag_duplicate
             check_and_flag_duplicate(coins_ref, coin_data)
 
             # Write to collection
```
- **Verification:** Line 272 updated to `from services.duplicate_check import check_and_flag_duplicate`. Staging batch import correctly references `services`.

### Check 5: `numista_backend/tests/test_container_import_path.py` (New Container Mode Test)
```python
def test_container_import_path():
    """Verify that under container runtime conditions (cwd=numista_backend,
    sys.path holding ONLY numista_backend, no repo root),
    importing main, importing services.duplicate_check, importing routes,
    and calling commit_reviews succeed without any ModuleNotFoundError.
    """
```
- **Verification:** Spawns subprocess with `cwd=numista_backend/` and stripped `sys.path` (excluding parent repo root). Verifies `main`, `routes.import_routes`, `routes.cert_routes`, `services.duplicate_check`, non-test source import scanning, and executes `commit_reviews` end-to-end. Passes 100%.

### Check 6: Version Bump in `constants.dart` & `pubspec.yaml`
```diff
diff --git a/numista_mobile/lib/constants.dart b/numista_mobile/lib/constants.dart
-const String kAppVersion = 'v8.18.15f';
+const String kAppVersion = 'v8.18.15g';

diff --git a/numista_mobile/pubspec.yaml b/numista_mobile/pubspec.yaml
-version: 8.18.15+81816
+version: 8.18.15+81817
```
- **Verification:** Correctly bumped to `v8.18.15g` and build `81817`.

---

## 2. Quality Gate Verification
- `flutter analyze lib/`: 0 errors, 0 warnings.
- `flutter test --reporter compact`: 645 passed, 0 failed.
- `pytest numista_backend/tests/ -q`: 613 passed, 0 failed.
- CRLF audit: 0 CRLF bytes (100% pure LF across all modified files).

---

## 3. Review Verdict
**VERDICT: PASS**  
The commit satisfies NET-448 completely, touches only the 4 specified import statements, adds the container test, bumps the version cleanly, and passes all gates.
