# Morgan-First UX v3.2 — AG-0 Safety Close & Route Inventory

**Branch:** `test/morgan-first-ux-v3.2`  
**Worktree:** `C:\Users\ericd\Documents\wt-morgan-first-v32`  
**Date:** 2026-11-22  

## 1. Section 3a Safety Audit (Closed / Verified)

| Safety Requirement | Status | Code Evidence |
|---|---|---|
| No-confirm Morgan add/edit/delete tools (including "immediately" add) | **CLOSED** | `numista_backend/main.py:3450-3460`: `add_coin_to_collection` calls `propose_add_coin()` (`main.py:2748`), `update_coin_in_collection` calls `propose_update_coin()` (`main.py:2845`), `undo_add_coin` calls `execute_undo_add_coin()` (`main.py:2929`). All create proposals in `morgan_proposals` with `used: False`; none write to `coins`. Writes occur only in `POST /api/morgan/confirm` (`routes/morgan_routes.py:305`) inside a `@firestore.transactional` claim. |
| No most-recent-coin fallback on edit | **CLOSED** | `numista_backend/main.py:2866-2889`: if `coin_id` is omitted, `propose_update_coin` checks only `created_at >= ten_min_ago`; if `0` or `>1` docs match, it returns `status: "ambiguous"` asking the user to clarify. Never guesses the most recent coin. |
| No hard undo / hard delete (including `INTERNAL_UNDO`) | **CLOSED** | `numista_backend/main.py:3124-3185`: `INTERNAL_UNDO:` verifies `users/{owner_key}/morgan_action_log` (`action == "add"` and `who == caller_uid` or `is_admin`), copies the coin to `users/{owner_key}/trash/{verified_coin_id}` with `deleted_at` and `deleted_by: 'morgan'` (soft delete), deletes from `coins`, and logs `action: 'delete'`. `POST /api/morgan/confirm` for `delete_coin` (`routes/morgan_routes.py:454-478`) also soft-deletes to `trash`. |
| REQ_031 write-route token lockdown (no `user_email` without token) | **CLOSED** | `routes/deps.py:69-79` (`get_current_user`) and `main.py:3012-3046` (`_authenticate_request`) require `Authorization: Bearer <Firebase ID token>`. In production (`K_SERVICE` or `ENVIRONMENT=production`), `ALLOW_UNAUTHENTICATED` is ignored. Cross-user `user_email`/`uid` mismatches return `403`. |

## 2. Live-Write & Morgan-First Route Inventory (Exact P5 Contracts)

| Purpose | Method & URL | Auth Header | Identity Source | Notes / File:Line |
|---|---|---|---|---|
| **Add Coin (Propose)** | `POST /api/morgan/propose` | `Authorization: Bearer <idToken>` | Token (`get_current_user` -> `_get_user_email`) | Creates proposal in `morgan_proposals`; no write to `coins`. `routes/morgan_routes.py:281` |
| **Add / Edit / Delete Confirm** | `POST /api/morgan/confirm` | `Authorization: Bearer <idToken>` | Token (`get_current_user` -> `_get_user_email`) | Transactional single-use claim; idempotent on double-tap; logs to `morgan_action_log`. `routes/morgan_routes.py:305` |
| **Identify Coin Photo** | `POST /api/identify_coin_photo` | `Authorization: Bearer <idToken>` | Token (`_authenticate_request` + `get_current_user`) | Multipart form; Morgan-First sends `save_to_collection=false` so nothing is saved before Confirm Card. `main.py:6491` |
| **Morgan Chat (Type / Propose)** | `POST /api/deep_dive` | `Authorization: Bearer <idToken>` | Token (`fb_auth.verify_id_token`) | Returns `action_payload` with `status: "proposed"` + `proposal_id`. `main.py:3088` |
| **Morgan Home Flags Read** | `GET /api/morgan/home_flags` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | **New (AG-1).** Reads `app_config/morgan_first_flags` (all 3 flags default `false`) + user's `morgan_home_pref`. Client cannot mutate flags. |
| **Morgan Home Preference Save** | `POST /api/morgan/home_preference` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | **New (AG-1).** Saves `preferred_home` (`"morgan"` or `"full_site"`) to `users/{email}/settings/morgan_home_pref`. |
| **Legacy UI Variant Read** | `GET /api/user/ui_variant` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | Existing Phase A variant endpoint (unchanged). `main.py:439` |
| **Checklist Add Coins** | `POST /api/checklist/add_coins` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | Rejects body `user_email` mismatch (403). `main.py:9262` |
| **Review Commit** | `POST /api/review/commit` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | `main.py:3557` |
| **Binder Scan Analyze / Confirm** | `POST /api/analyze_binder_scan`, `POST /api/confirm_binder_scan` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | `main.py:4735`, `main.py:5451` |
| **Scan Document / Commit Session** | `POST /api/scan/upload_document`, `POST /api/scan/review/commit_session` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | `routes/scan_routes.py:84`, `routes/scan_routes.py:290` |
| **Import Upload / Start / Commit** | `POST /api/import/upload`, `POST /api/import/start`, `POST /api/v1/import/commit_batch` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | `main.py:7517`, `main.py:7620`, `routes/import_routes.py:289` |
| **RAG Query** | `POST /api/v1/rag/query` | `Authorization: Bearer <idToken>` | Token (`get_current_user`) | `main.py:361` |
