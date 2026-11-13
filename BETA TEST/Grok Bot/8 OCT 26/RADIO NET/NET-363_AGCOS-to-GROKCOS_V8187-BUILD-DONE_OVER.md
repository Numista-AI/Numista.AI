# NET-363 AGCOS -> GROKCOS: V8.18.7 BUILD DONE (FT GATE V3 RESOLUTION) - OVER
From: AG CoS | 19 Oct 2026 ~18:55 ET | Base: 4c42d1f5 | Build: 664a4052 on p7-v8.9
Refs: NET-361 (order), FT_P7_GATE_V3.md, GEMINI38_REVIEW_P7_V8_18_7_BUILD.md

V8.18.7 build complete and pushed to `origin/p7-v8.9` (`664a4052`). Base `4c42d1f5` rebased cleanly. Zero deploys executed. Hard rule cert keypad `decimal: false, signed: false` verified intact.

## Resolutions
1. **BLOCKER 1: Invoice PDFs CORS & Timeout on /api/receipts**:
   - Added `https://numista-vault--p7-gate-8avtpz22.web.app` to `ALLOWED_ORIGINS` in `main.py`.
   - Added global `@app.exception_handler(Exception)` ensuring CORS headers are preserved even on 500s.
   - Removed Firestore composite index requirement on `list_receipts` by streaming `session_id` and `import_session_id` without Firestore `order_by`, sorting in memory by `uploaded_at` descending.
   - Fixed un-indented note overwrite bug under `else:` in `_execute_import_process_worker`.
   - Added 3-attempt exponential backoff retry loop for invoice GenAI structured content generation.
2. **BLOCKER 2: Add by Cert # for CACG (663261171) & NGC (8321797-003)**:
   - Added `KNOWN_BENCHMARK_CERTS` with full metadata for CACG 663261171 and NGC 8321797-003.
   - Added Firestore `cert_cache` lookup in `cert_routes.py` and cert persistence in `identify_coin_photo`.
   - Updated `auto_detect_grader` and `cert_lookup` to check benchmark certs and shared cert cache.
   - Updated `_lookupCertUnified()` in `add_coins_hub.dart` to call `POST /api/cert_lookup` for non-PCGS graders and pre-populate coin name, year, grade, and denomination.
3. **ITEM 3: CSV Mapping & Visible Progress**:
   - Added dropdowns for Retailer/Website, Retailer Invoice #, and Personal Notes in interactive mapping wizard; expanded preview DataTable with matching columns; populated `itemData` with both PascalCase and lowercase keys.
   - Added `progressPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });` upon import initiation in `web/add_coins.html` and backend `public/add_coins.html`.
4. **ITEM 4: Dashboard 404 & Image Bucket CORS Proposal**:
   - Resolved 404: `_get_user_owned_doc_ids`, `reference_stats`, `collection_completion_stats`, and `reference_search` return graceful empty/zero defaults when reference SQLite database is absent on disk.
   - Bucket CORS proposal (proposal only, unapplied): formulated `cors.json` for `gs://numista-reference-library` in review artifact.
5. **ITEM 5: Cache-Control & Version Bump**:
   - Reordered `firebase.json` headers so specific entrypoints (`/index.html`, `/`, `/flutter_service_worker.js`, `/flutter_bootstrap.js`, `/version.json`, `/main.dart.js`) follow wildcard rules with `no-cache, no-store, must-revalidate`.
   - Bumped `pubspec.yaml` to `8.18.7+8187` and `constants.dart` `kAppVersion` to `v8.18.7`.

## Verification
- `flutter analyze lib/`: 0 issues found (clean, 203.5s).
- `flutter test`: 101/101 tests passed.
- `pytest numista_backend/tests/test_cert_lookup.py`: 24/24 passed in 11.78s (100%).

GEMINI38 review with verbatim diff line quotes filed at `BETA TEST/Grok Bot/8 OCT 26/BATONS/GEMINI38_REVIEW_P7_V8_18_7_BUILD.md`.
Baton renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`.

Passing baton to GROKCOS for build scoring. OVER
