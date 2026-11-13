# GB CoS SCORE: FAILFIX_PLAN_NET-748_CoS_v4.md (attempt 11)

- Scorer: GB CoS (independent of Argon) | 2026-11-04 ~11:05 AM ET
- Plan MD5 2431496EC015E7092D8B5D7BA0E5297F (verified), 368 lines
- Source checked: C:\Users\ericd\Documents\MyVertexProject (branch p7-v8.9, HEAD ca4e3d33). `git diff 7c0eec8d HEAD -- numista_mobile/lib numista_mobile/firestore.rules` is EMPTY, so the plan's base tip 7c0eec8d is still accurate for code.

## SCORE: 95 / 100 - PASS (0 blocking must-fixes)

## 1. Plan line refs vs Dart source (read today)
| Plan ref | Source today | Result |
|---|---|---|
| firestore.rules 339 lines; isAuthenticated 8-10; deny-all 335-337 | 339 lines; 8-10 isAuthenticated (also excludes anonymous sign-in); 335-337 `match /{document=**}` deny | OK |
| add_coins_hub.dart 2589-2601 global_metadata/{usmint,littleton}_sku_dictionary/skus/{docId} .get() | 2589-2598 exactly that, branching on `_skuRetailer == 'Littleton Coin Company'` | OK |
| canonical_mint_asset_service.dart `combined` at line 104 | 104 `final combined = '$prog $theme $title';` | OK |
| resolve() cleanSku line 182; switch 196-311; 2026 block at 314 | 182 cleanSku; 196 `switch (cleanSku)`; 314 `if (cleanYear == '2026')` | OK |
| extractSku returns String (3.5 assignment type-safe) | 72 `static String extractSku(...)` non-null; line 282 `sku: cleanSku` stays String | OK |
| my_collection_screen 3448 inspector / 3467 hasUserPhoto / 4452 vault / 6345,6357 card | 3448 `_showCoinInspectorDialog`; 3467 `hasUserPhoto = ...startsWith('http')`; 4452 `if (!hasAny)`; 6345 class, 6357 build; 6381 fetchReferenceImages | OK |
| coin_detail_screen ~1030-1071; 1052 `_CoinImagePairState`; 1071 fetchReferenceImages | class 1033, State 1041, initState 1048, 1052 `_obvUrl = ...`, 1071 fetchReferenceImages | OK (approx, "around") |
| coin_image_service CoinImageResult 618 | 618 | OK |
| review_hub_screen 2190 image_url_obverse | 2190 | OK |
| inventory_gallery.dart:131 and 347 | EXISTS at numista_mobile/lib/inventory_gallery.dart (391 lines): 131 reads image_url_obverse, 347 Image.network | OK - but plan line 20 note ("does not exist") is WRONG |

## 2. Argon review audit - UNRELIABLE EVIDENCE
Argon's verdict (3 MFs fixed) agrees with mine, but most of its "verbatim" quotes do NOT match the files:
- Quotes plan text at "plan:41", "plan:287-288", "plan:348" and rules blocks with `allow read/write` - the plan actually has `allow get` / `allow list, write: if false` and different wording; test 20 is not at line 348.
- Quotes firestore.rules:9 as `request.auth != null` - real line also excludes anonymous.
- Quotes add_coins_hub 2589 as a `_skuRetailer == 'usmint'` ternary and 127 as `'usmint'` - real is `'US Mint'` and if/else-if.
- Quotes add_coins_hub 2638-2647, canonical 100-104/182-186/314, my_collection 3467/4452, coin_detail 1052 with code that differs from the source.
- Claims inventory_gallery.dart is "non-existent in numista_mobile/lib/" - it exists.
Conclusion: Argon's line numbers land in the right places but its quoted code is reconstructed, not read. Treat 98 as unverified; this CoS score rests on my own read.

## 3. Deductions (-5)
- -2 Plan line 20 wrongly repeats that inventory_gallery.dart does not exist (it does; refs 131/347 are correct).
- -1 Header says v4 MF line refs are "Argon's, not re-read by CoS"; now re-read and confirmed (should be updated if a v5 ever happens).
- -1 coin_detail 1052 is inside initState of `_CoinImagePairState` (class at 1041), not the class line; "around" wording acceptable.
- -1 3.5 relies on extractSku inferring SKUs from title/year only; test 20 STOP clause covers it, but Morgan/Peace/ASE title inference is unproven until tests run.

## 4. Must-fixes
None blocking. Advisory (no re-write needed): implementer should treat inventory_gallery.dart as real and apply the 131/347 change; Argon should be told its quotes don't match source.

## 5. Gates unchanged
Plan-only. Step 1b `firebase deploy --only firestore:rules` reaches LIVE and needs Eric's separate typed YES plus snapshot diff. Firestore seeding needs its own YES. Nothing executed or deployed by CoS.
