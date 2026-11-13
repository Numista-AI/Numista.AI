# EXECUTE_DONE — NET-118 V2: Live Auth Headers Systemic Audit & Fix

**Code Commit:** `f55a11de04a3400722d8db255dda70e923f09107`
**Branch:** `dev`
**Pushed:** 2026-10-14 ~9:00 PM ET
**Engineer:** Antigravity / Gemini 3.8
**Follows Orders:** NET-121, COS_SCORE_NET118_LIVE-AUTH_V1

---

## 1. Cloud Run Log Evidence (Verbatim from Cloud Logging)

Queried via `gcloud logging read` against `projects/studio-9101802118-8c9a8` (service `numista-backend`, region `us-central1`) between 7:43 PM and 7:47 PM ET (23:43–23:47 UTC):

### Request Logs (`run.googleapis.com/requests`):
```json
{
  "httpRequest": {
    "latency": "0.004349251s",
    "protocol": "HTTP/1.1",
    "referer": "https://numista.ai/",
    "remoteIp": "24.246.177.193",
    "requestMethod": "OPTIONS",
    "requestSize": "691",
    "requestUrl": "https://numista-backend-568985927038.us-central1.run.app/api/checklist/add_coins",
    "responseSize": "338",
    "serverIp": "34.143.72.2",
    "status": 200,
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
  },
  "insertId": "6ad01420000e07a7fa4ef2a2",
  "logName": "projects/studio-9101802118-8c9a8/logs/run.googleapis.com%2Frequests",
  "severity": "INFO",
  "timestamp": "2026-10-14T23:45:36.912145Z"
}
```

```json
{
  "httpRequest": {
    "latency": "0.003688780s",
    "protocol": "HTTP/1.1",
    "referer": "https://numista.ai/",
    "remoteIp": "24.246.177.193",
    "requestMethod": "POST",
    "requestSize": "5944",
    "requestUrl": "https://numista-backend-568985927038.us-central1.run.app/api/checklist/add_coins",
    "responseSize": "174",
    "serverIp": "34.143.72.2",
    "status": 401,
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
  },
  "insertId": "6ad0142100009b755a0a08bd",
  "logName": "projects/studio-9101802118-8c9a8/logs/run.googleapis.com%2Frequests",
  "severity": "WARNING",
  "timestamp": "2026-10-14T23:45:37.032520Z"
}
```

```json
{
  "httpRequest": {
    "latency": "0.003817399s",
    "protocol": "HTTP/1.1",
    "referer": "https://numista.ai/",
    "remoteIp": "24.246.177.193",
    "requestMethod": "POST",
    "requestSize": "5944",
    "requestUrl": "https://numista-backend-568985927038.us-central1.run.app/api/checklist/add_coins",
    "responseSize": "174",
    "serverIp": "34.143.72.2",
    "status": 401,
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
  },
  "insertId": "6ad014320009b17e0270f9af",
  "logName": "projects/studio-9101802118-8c9a8/logs/run.googleapis.com%2Frequests",
  "severity": "WARNING",
  "timestamp": "2026-10-14T23:45:54.629052Z"
}
```

### Application stdout Logs (`run.googleapis.com/stdout`):
```
2026-10-14T23:45:37.032520Z INFO: 169.254.169.126:7780 - "POST /api/checklist/add_coins HTTP/1.1" 401 Unauthorized
jsonPayload: {"latency_ms": 0.399, "logger": "main", "message": "POST /api/checklist/add_coins -> 401 (0ms)", "method": "POST", "path": "/api/checklist/add_coins", "request_id": "1a40701b6c884e4a808b243e18381c9d", "status": 401, "timestamp": "2026-10-14T23:45:54.635148+00:00", "user_email": "-"}

2026-10-14T23:46:27.301527Z INFO: 169.254.169.126:24436 - "POST /api/checklist/add_coins HTTP/1.1" 401 Unauthorized
jsonPayload: {"latency_ms": 0.359, "logger": "main", "message": "POST /api/checklist/add_coins -> 401 (0ms)", "method": "POST", "path": "/api/checklist/add_coins", "request_id": "04b2fc5979264c5eaa3a79d2dbf515ea", "status": 401, "timestamp": "2026-10-14T23:46:27.302444+00:00", "user_email": "-"}
```

---

## 2. Infrastructure Expansion: `HttpAuthClient`

To support all HTTP verbs and file uploads required across the mobile app, `numista_mobile/lib/services/http_auth_client.dart` was expanded with:
- `HttpAuthClient.patch(Uri url, {Map<String, String>? headers, Object? body, Encoding? encoding})`
- `HttpAuthClient.multipartPost(Uri url, http.MultipartRequest request)`

---

## 3. Call Site Audit & Resolution Table

Every call site contacting `numista-backend` in `numista_mobile/lib` has been audited and migrated to `HttpAuthClient`:

| File | Line | Route | Method | Status / Resolution |
| :--- | :--- | :--- | :--- | :--- |
| `screens/program_manager_screen.dart` | 1764 | `/api/checklist/add_coins` | POST | Fixed in ab9f596a (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 44 | `/api/review/commit` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 106 | `/api/review/commit` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 173 | `/api/review/delete_items` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 240 | `/api/review/delete_items` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 493 | `/api/review/bulk_update` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 562 | `/api/review/keep_set_as_is` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 624 | `/api/review/break_up_set` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 895 | `/api/review/revert_reconciliation` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 953 | `/api/review/break_up_set` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/review_hub_screen.dart` | 1066 | `/api/review/commit` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/add_coins_hub.dart` | 4386 | `/api/identify_coin_photo` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/add_coins_hub.dart` | 4867 | `/api/extract_raw_text` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/add_coins_hub.dart` | 4956 | `/api/checklist/detect_format` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `services/checklist_scan_service.dart` | 104 | `/api/analyze_checklist` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `services/checklist_scan_service.dart` | 140 | `/api/confirm_checklist_match` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/login_screen.dart` | 1121 | `/api/identify_coin_photo` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/microscope_scan_screen.dart` | 1546 | `/api/greysheet/resolve` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/microscope_scan_screen.dart` | 1566 | `/api/greysheet/pricing` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/human_ai_trainer_screen.dart` | 897 | `/api/crop_coin_photo` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/human_ai_trainer_screen.dart` | 1311 | `/api/nicknames` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/human_ai_trainer_screen.dart` | 1338 | `/api/nicknames/submit` | POST (Form) | Fixed (`HttpAuthClient.post` + urlencoded) |
| `screens/human_ai_trainer_screen.dart` | 1572 | `/api/nicknames/{doc_id}/vote` | POST (Form) | Fixed (`HttpAuthClient.post` + urlencoded) |
| `screens/human_ai_trainer_screen.dart` | 1729 | `/api/coin_crops/list` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/human_ai_trainer_screen.dart` | 1747 | `/api/coin_crops/sample` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/human_ai_trainer_screen.dart` | 1765 | `/api/coin_crops/approve` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/human_ai_trainer_screen.dart` | 1783 | `/api/coin_crops/reject` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/coin_detail_screen.dart` | 670 | `/api/greysheet/refresh` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/coin_detail_screen.dart` | 1943 | `/api/greysheet/pricing` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/coin_detail_screen.dart` | 2133 | `/api/market_history` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/coin_detail_screen.dart` | 2176 | `/api/auction_records` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/coin_detail_screen.dart` | 1863 | `imageUrl` (PCGS/NGC CDN) | GET | External 3rd-party image binary CDN; bare allowed |
| `screens/glossary_academy_screen.dart` | 46 | `/api/reference/glossary` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/glossary_academy_screen.dart` | 60 | `/api/reference/glossary/{term}` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/glossary_academy_screen.dart` | 111 | `/api/reference/grading_scale` | GET | Fixed (`HttpAuthClient.get`) |
| `widgets/glossary_tooltip_wrapper.dart` | 67 | `/api/reference/glossary/{term}` | GET | Fixed (`HttpAuthClient.get`) |
| `widgets/grade_badge_widget.dart` | 197 | `/api/reference/grade/{grade}` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/settings_screen.dart` | 1667 | `/api/dedup_sweep` | POST (Form) | Fixed (`HttpAuthClient.post` + urlencoded) |
| `screens/settings_screen.dart` | 1716 | `/api/dedup_sweep/auto_clean` | POST (Form) | Fixed (`HttpAuthClient.post` + urlencoded) |
| `screens/settings_screen.dart` | 2568 | `/api/collection/count` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/settings_screen.dart` | 2603 | `/api/sandbox/clear` | DELETE | Fixed (`HttpAuthClient.delete`) |
| `screens/wishlist_screen.dart` | 132 | `/api/wishlist/create-share` | POST | Fixed (`HttpAuthClient.post`) |
| `services/batch_valuation_service.dart` | 359 | `/api/estimate_value_text` | POST | Fixed (`HttpAuthClient.post`) |
| `services/batch_valuation_service.dart` | 388 | `/api/estimate_value_general` | POST | Fixed (`HttpAuthClient.post`) |
| `services/collector_profile_service.dart` | 75 | `/api/collector/profile` | GET | Fixed (`HttpAuthClient.get`) |
| `services/collector_profile_service.dart` | 110 | `/api/collector/profile` | POST | Fixed (`HttpAuthClient.post`) |
| `services/estate_report_service.dart` | 76 | `/api/estate/generate_report` | POST | Fixed (`HttpAuthClient.post`) |
| `services/family_subaccount_service.dart` | 58 | `/api/family/subaccount` | POST | Fixed (`HttpAuthClient.post`) |
| `services/family_subaccount_service.dart` | 83 | `/api/family/subaccounts` | GET | Fixed (`HttpAuthClient.get`) |
| `services/family_subaccount_service.dart` | 98 | `/api/family/subaccount/{id}` | DELETE | Fixed (`HttpAuthClient.delete`) |
| `services/ticket_service.dart` | 48 | `/api/tickets/` | POST | Fixed (`HttpAuthClient.post`) |
| `services/ticket_service.dart` | 75 | `/api/tickets/my-tickets` | GET | Fixed (`HttpAuthClient.get`) |
| `services/ticket_service.dart` | 93 | `/api/tickets/{id}/grants` | POST | Fixed (`HttpAuthClient.post`) |
| `services/ticket_service.dart` | 115 | `/api/tickets/{id}/grants/{gid}` | DELETE | Fixed (`HttpAuthClient.delete`) |
| `services/ticket_service.dart` | 133 | `/api/tickets/{id}` | PATCH | Fixed (`HttpAuthClient.patch`) |
| `services/ticket_service.dart` | 155 | `/api/tickets/{id}/messages` | POST | Fixed (`HttpAuthClient.post`) |
| `services/ticket_service.dart` | 177 | `/api/tickets/support/all` | GET | Fixed (`HttpAuthClient.get`) |
| `services/ticket_service.dart` | 200 | `/api/tickets/{id}/support-view` | GET | Fixed (`HttpAuthClient.get`) |
| `services/ticket_service.dart` | 222 | `/api/tickets/{id}/support-messages`| POST | Fixed (`HttpAuthClient.post`) |
| `services/ticket_service.dart` | 246 | `/api/tickets/{id}/status` | PATCH | Fixed (`HttpAuthClient.patch`) |
| `services/ticket_service.dart` | 266 | `/api/tickets/{id}/screenshots` | PATCH | Fixed (`HttpAuthClient.patch`) |
| `services/world_item_service.dart` | 396 | `/api/world/identify` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `services/world_item_service.dart` | 446 | `/api/spot_prices` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/my_collection_screen.dart` | 2333 | `/api/spot_prices` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/my_collection_screen.dart` | 2351 | `/api/convert_heic` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/ai_chat_screen.dart` | 1403 | `/api/identify_group_photo` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/ai_chat_screen.dart` | 1452 | `/api/chat/deep_dive` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/ai_chat_screen.dart` | 1548 | `/api/preview_cost_split` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/ai_chat_screen.dart` | 1618 | `/api/commit_group_photo` | POST | Fixed (`HttpAuthClient.post`) |
| `screens/coa_inspector_screen.dart` | 36 | `/api/v1/coa/parse` | POST (Multipart) | Fixed (`HttpAuthClient.multipartPost`) |
| `screens/home_dashboard.dart` | 139 | `/api/dismissed_news` | GET | Fixed (`HttpAuthClient.get`) |
| `screens/home_dashboard.dart` | 562 | `/api/spot_prices` | GET | Fixed (`HttpAuthClient.get`) |
| `services/error_message_service.dart` | 60 | `/api/telemetry/silent-error` | POST | Fixed (`HttpAuthClient.post`) |
| `services/numista_service.dart` | 14, 38 | `api.numista.com/api/v3` | GET | External Numista API (uses Numista-API-Key header, not numista-backend) |
| `services/ebay_scraper_service.dart` | 42 | `ebay.com` | GET | External 3rd party web scraping |

---

## 4. Guard Test Added

Created `numista_mobile/test/auth_guard_test.dart`:
- Scans every `.dart` file under `numista_mobile/lib/` (screens, services, widgets, etc.)
- Asserts that no bare `http.get`, `http.post`, `http.put`, `http.delete`, `http.patch`, or `http.MultipartRequest` calls target backend URLs (`kApiBaseUrl`, `_apiUrl`, `_baseUrl`, `_backendBaseUrl`).
- Validates that only `HttpAuthClient` methods are used for backend communication.
- Runs in CI on every test pass.

---

## 5. Verification & Test Results

1. **Flutter Analyze:**
   ```
   Analyzing lib...
   No issues found! (ran in 6.1s)
   ```
   - 0 errors, 0 warnings.
   - Cleaned unused imports and variables in `human_ai_trainer_screen.dart`, `error_message_service.dart`, `ai_chat_screen.dart`.

2. **Flutter Tests:**
   ```
   00:33 +510: All tests passed!
   ```
   - 510/510 tests passed (including new `auth_guard_test.dart`).

3. **Backend Python Tests (pytest):**
   - `test_default_deny_auth.py`: 20/20 passed
   - `test_cors_public_paths.py`: 7/7 passed
   - `test_req031_auth.py`: 35/35 passed
   - Total auth backend tests: 62/62 passed.

---

## 6. Public Paths Note for Grok CoS

Per NET-121 instruction 2 ("Don't widen `_PUBLIC_PATHS`; any 'should this be public?' idea goes to Grok CoS as a note"):
- `/api/reference/glossary`, `/api/reference/glossary/{term}`, and `/api/reference/grade/{grade}` currently return 401 without Bearer tokens. We migrated all client calls to use `HttpAuthClient` so authenticated sessions fetch them with Bearer tokens cleanly.
- If unauthenticated guest users / landing page visitors ever need to browse the glossary or see grade badges without logging in, Grok CoS / Eric can decide whether `/api/reference/*` should eventually be considered for `_PUBLIC_PATHS`. In the meantime, `HttpAuthClient` provides full coverage for authenticated app users.

---

## 7. Deploy Note

- Code commit is pushed to `dev` only (`f55a11de04a3400722d8db255dda70e923f09107`).
- **NEVER pushed to main.**
- Per standing orders, deploy to live site (`numista-vault.web.app`) requires Eric's typed YES.
