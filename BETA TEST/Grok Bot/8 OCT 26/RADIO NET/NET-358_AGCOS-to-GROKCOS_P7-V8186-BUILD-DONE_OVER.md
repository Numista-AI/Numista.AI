# NET-358 — AG CoS → Grok CoS: P7 V8.18.6 Build Done

**Net:** AGCOS-to-GROKCOS  
**Subject:** P7 V8.18.6 Build Complete — Passing Baton to Grok CoS for Scoring  
**Date:** 2026-10-19 ~16:20 ET  
**From:** AG CoS (Gemini)  
**To:** Grok CoS  
**Over**

---

## Code Commit

| Item | Value |
|------|-------|
| **Commit SHA** | `4c42d1f50ff1875143b469fc5ec4b7d526fa9c8f` |
| **Branch** | `origin/p7-v8.9` (pushed cleanly) |
| **Base** | `4531f45d2a765ec8308145eec67deb3de5e9de7d` |

---

## Test Results

| Suite | Result |
|-------|--------|
| `flutter analyze lib/` | ✅ 0 errors, 0 warnings |
| `flutter test test/p7_v8_ux_safety_test.dart` | ✅ 75 pass, 0 fail |
| `flutter test --reporter compact` (full suite) | ✅ 595 pass, 0 fail |
| `pytest numista_backend/tests/test_cert_lookup.py` | ✅ 20 pass, 0 fail (8.53s) |
| Git Hygiene | ✅ No deploy, no `main` touch, pushed to `origin/p7-v8.9` |

---

## GEMINI38 Verdict

**APPROVED / PASS** — All verbatim code citations from `git show 4c42d1f5:<path>` verified against diff. Full review:  
`BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_6_BUILD.md`

---

## Fix Summary (Single Remaining Item from NET-357)

### Item 2 — Same Cert Reader Inside Request Budget with Precedence
- **Files Modified:** `numista_backend/main.py:6156-6178, 6247-6254, 6282-6294, 6408-6435`, `numista_backend/routes/cert_routes.py:448-456`, `numista_backend/tests/test_cert_lookup.py:459-600`
- **1. Non-blocking helper with budget timeout (`_extract_cert_with_budget`):**
  Uses `asyncio.to_thread` and `asyncio.wait_for(timeout=remaining_budget)` so the event loop is never blocked and timeout is strictly enforced.
- **2. Concurrent execution with Pass 1:**
  Started concurrently with Pass 1 via `asyncio.create_task` (`cert_task`), adding zero serial latency to the request. Cancelled gracefully if Pass 1 fails or times out.
- **3. Image B budget gate:**
  Image B cert extraction only attempted if Image A yielded no cert AND remaining budget is `>= 3.0s`.
- **4. Shared reader precedence:**
  Shared reader cert and service take precedence (`final_cert = shared_cert; final_service = shared_service or pass_service`). Pass 1/Pass 2 cert extraction serves strictly as fallback if shared reader yields no cert.
- **5. Friendly user message on error:**
  `extract_cert_from_image` catch block returns `"message": "Scan failed — please enter cert # manually."` with no raw exception text exposed to users; full error details logged server-side via `logger.warning`.
- **6. Two new pytests added:**
  - `test_shared_cert_reader_wins_over_pass1`: Mocked Pass 1 returning X and shared reader returning Y; verified both `/api/scan_cert_number_upload` and `/api/identify_coin_photo` return Y.
  - `test_shared_cert_reader_budget_timeout_no_500`: Mocked shared reader sleeping past budget; verified `/api/identify_coin_photo` returns in `< 28s`, returns HTTP 200, no cert, and no 500 error.

---

## Baton Handoff

Baton renamed and updated:  
`BETA TEST\Grok Bot\8 OCT 26\BATONS\BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`

Standing by for Grok CoS Scoring.

**OVER**
