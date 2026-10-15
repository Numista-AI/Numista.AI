# NET-218 GROKCOS: P7 backend CORS deploy (Eric YES 15 Oct) - BLOCKED on gcloud auth

- Branch: deploy/cors-preview-20261015 (from origin/main 3c1bacf5), commit b611eaca, pushed. NOT merged to main.
- Change: numista_backend/main.py only (+ new test tests/test_cors_preview_regex.py). Minimal CORS lines from c3ca5ccb:
  ALLOWED_ORIGIN_REGEX = ^https://numista-vault--[a-z0-9-]+\.web\.app$ ; allow_origin_regex on CORSMiddleware; identify_group_photo uses _is_allowed_origin. Existing ALLOWED_ORIGINS list unchanged. No wildcard. No frontend, no firestore.rules, no 578b374a.
- Tests: pytest tests -> 513 passed, 3 failed (test_missing_images_csv x2, test_usmint_releases_scraper::test_load_local_catalog; local data-file tests, unrelated to CORS). New CORS tests pass.
- Deploy: NOT done. Merging to main fires deploy-production.yml, which also redeploys Hosting + Firestore rules (outside the YES). Backend-only path is DEPLOYMENT_SOP emergency gcloud deploy of numista-backend, but gcloud on EDS_Laptop needs re-login (gcloud auth login - interactive, Eric only).
- Live Cloud Run revision unchanged. Nothing rolled back.
OVER
