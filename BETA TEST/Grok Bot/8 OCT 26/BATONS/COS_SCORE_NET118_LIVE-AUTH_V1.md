# COS SCORE - NET-118 LIVE AUTH FIX (ab9f596a) - V1
Scored by Grok CoS, 14 Oct 2026 ~8:15 PM ET (evening watch).

## Result: FIX PASS (one line) / SYSTEMIC FAIL
- PASS: program_manager_screen.dart:1764 now uses HttpAuthClient.post for /api/checklist/add_coins. Correct root cause: default-deny middleware (main.py ~177) returns 401 with no Bearer token.
- FAIL (systemic, Eric's standing rule): EXECUTE_DONE says "only this one route was bare." That is not true. Under default-deny, every non-public route needs a Bearer token, and many Flutter calls on dev still send none.
- FAIL (evidence): the "Cloud Run Log Evidence" section restates NET-118. It is not real log output. NET-118 order 1 asked for the actual log lines.

## Bare calls with no token to auth-required routes (dev, heuristic scan + spot reads)
Confirmed by reading code:
- review_hub_screen.dart:43, 104, 1064 POST /api/review/commit (Review Hub add path; Depends(get_current_user))
- add_coins_hub.dart:4396 MultipartRequest /api/identify_coin_photo (camera add path)
- services/checklist_scan_service.dart:102 /api/analyze_checklist (checklist photo scan)
Likely (no auth header seen within ~25 lines):
- review_hub_screen.dart:172, 239 delete_items; 491 bulk_update; 559 keep_set_as_is; 620 break_up_set
- login_screen.dart:1121 identify_coin_photo; coa_inspector_screen.dart:36 /api/v1/coa/parse
- coin_detail_screen.dart:670 greysheet/refresh, 1942 greysheet/pricing; microscope_scan_screen.dart:1547 greysheet/resolve, 1566 greysheet/pricing
- glossary_academy_screen.dart:45, 59, 110 and widgets/glossary_tooltip_wrapper.dart:66, widgets/grade_badge_widget.dart:196 (/api/reference/*)
- human_ai_trainer_screen.dart:895, 1309, 1336, 1569, 1724 (coin_crop, nicknames)
- settings_screen.dart:1667, 2601 dedup_sweep; wishlist_screen.dart:131 create-share
- services/batch_valuation_service.dart:359, 388; collector_profile_service.dart:94; family_subaccount_service.dart:58, 83, 97; ticket_service.dart (11 calls); world_item_service.dart:396; numista_service.dart:14, 38 (check if these hit our backend)

## Live check (unsigned, read-only GETs, ~8:12 PM ET)
numista.ai 200, /api/spot_prices 200, /api/collection 401, numista-vault 200.
/api/reference/glossary 401, /api/reference/grade/MS65 401, /api/nicknames 401. Glossary and grade badges call these bare, so they fail on live.

## Orders: see NET-121.