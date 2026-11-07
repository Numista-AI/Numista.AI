# BATON: Grok Bot CoS Review of NET-817 Cards & Images Plans v1.9 (Attempt 1/4 for AG CoS v5)
**To:** Grok Bot Chief of Staff (`GROKCOS`), Stand Alone Grok (`SAG`, `grok-4.7`)  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Observed Wall-Clock DTG:** 2026-11-07 15:42 ET (America/New_York)  
**Track:** NET-817 (`NET-780b` Cards v1.9 + `NET-780c` Images v1.9) — Attempt 1/4 for AG CoS v5  
**Status:** **PLAN ONLY** (`origin/main` locked at `9f04550a`; Stripe OFF; preview gate only; alerts only, never budget caps; no Argon)

---

## 1. Delivered Plan Files on Branch `p7-v8.9`
1. **Cards Plan v1.9:** `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.9.md`
2. **Images Plan v1.9:** `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.9.md`

---

## 2. Summary of v1.8 $\rightarrow$ v1.9 Must-Fix Closeouts (Verified Against `git show 4d17ca5e:...`)

Every item marked **Closed** in `COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md` is preserved intact, and all 11 open items from `COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md` and `RADIO_NET-832` are closed:

| Must-Fix ID | Resolution in v1.9 (`FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` & `FAILFIX_PLAN_NET-780c_IMAGES_v1.9.md`) |
|---|---|
| **MF-B1'** | **Orphaned Kaggle/Google Inspector Deletions & Verbatim Quotes:** Records that NET-816 v1.11 is **PARKED** and Catalog Chunk 1 (`9bbe20e4`) does not own `my_collection_screen.dart`. Declares that NET-817's card/image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) are 100% independent of the inspector/Google-button lines (`:150–151`, `:3454`, `:3531–3548`, `:3820`, `:4387–4406`, `:5252–5278`, `:5549–5684`) and leave them untouched by default pending CoS re-homing (or provide the atomic Step 1 deletion span if explicitly directed by CoS at execution gate). Corrects all stale quotes verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` (`OutlinedButton.icon`, `void _onSearchGoogle(Map<String, dynamic> data) async`, `void _onSearchEbay(Map<String, dynamic> data) async` calling `EpnService.generateSearchUrl(coin, soldOnly: true)`). |
| **MF-B2'** | **Code Pin (`4d17ca5e`) & Honest DTG:** Replaces `ebf1eed8` HEAD check with `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` so docs/baton commits do not invalidate the code pin while any code drift aborts immediately. Stamped with real observed wall-clock DTG (`2026-11-07 15:35–15:42 ET`). |
| **MF-B3'** | **Required Imports in `my_collection_screen.dart`:** Includes exact import diff adding `import '../widgets/collection_card_valuation_row.dart';` (Step 1) and `import '../widgets/collection_card_image.dart';` (Step 2) at line 45 of `my_collection_screen.dart`, and confirms `intl` (`:2`) and `melt_value_service.dart` (`:31`) remain actively used in `my_collection_screen.dart`. |
| **MF-C2'** | **Real AI Value Key (`'AI Estimated Value'`) & Pending-Chip Semantics:** `CollectionCardValuationRow` reads `data['AI Estimated Value'] ?? data['ai_estimated_value'] ?? data['ai_value'] ?? data['aiValue']` matching `_F.aiValue` at `my_collection_screen.dart:72`. Filters out sentinels (`Pending`, `null`, `—`, `none`, `nan`, `''`) and supports range strings (`12.00 - 15.00` $\rightarrow$ `\$12.00 - \$15.00`) matching table column `:3345–3355`. Documents and tests the intentional B05N-8 behavior change vs `:3170` (`valCpg > 0` suppresses pending chip; valid AI value shows chip iff `enrichment_status == 'pending'`). |
| **MF-C3'** | **Face Value for Canonical & Historical Denominations:** Drops the false claim from v1.8 about `MeltValueService.parseFaceValue`. Patches `MeltValueService.parseFaceValue` (`lib/services/melt_value_service.dart:76–88`) so `'half dime'` precedes `'dime'`, `'three cent'` precedes `'nickel'`, and canonical word forms (`'fifty cent'`, `'twenty-five cent'`, `'ten cent'`, `'five cent'`) precede generic `'cent'`, AND adds a `DenominationCanon` fast-path in `CollectionCardValuationRow.resolveFaceValue`. Full table test added (`Cent` $\rightarrow$ `$0.01`, `Five Cents` $\rightarrow$ `$0.05`, `Dime` $\rightarrow$ `$0.10`, `Quarter Dollar` $\rightarrow$ `$0.25`, `Half Dollar` $\rightarrow$ `$0.50`, `Dollar` $\rightarrow$ `$1.00`, `Half Dime` $\rightarrow$ `$0.05`, `Three Cent Nickel` $\rightarrow$ `$0.03`, `Set` $\rightarrow$ `'—'`). |
| **MF-C5'** | **Preserve `'1 cent'` in `CanonicalMintAssetService` & Discriminating Tests:** Updates `canonical_mint_asset_service.dart:431–435` to `RegExp(r'(?<![\d.])(?:1c|1¢|1 cents?|one cent|penny)(?!\w)|(?:^|(?<![\d.])\s+)\bcent\b', caseSensitive: false)` and `RegExp(r'(?<![\d.])(?:5c|5¢|5 cents?|five cents?|nickel)(?!\w)', caseSensitive: false)`. Uses neutral title `'title': '2026 Coin'` in all tests so `cleanTitle` never masks `cleanDenom`. |
| **MF-C6'** | **Rendered Widget Color Contrast Assertions:** Pumps `CollectionCardValuationRow` under `ThemeData.dark()` and `ThemeData.light()`, extracts `tester.widget<Text>(find.text('Value pending AI estimate')).style!.color!` and the ancestor `Container` `BoxDecoration.color`, and asserts contrast $\ge 7.0$ in dark mode and $\ge 4.5$ in light mode (including against the rendered light chip background `0xFFFFF3CD`). |
| **MF-I3'** | **Honest Image Precedence (`Canonical -> Direct URL -> Reference`) + `users%2f` Fix:** Preserves shipped `_CollectionCardImage` (`:6369–6383`) order (`CanonicalMintAssetService.resolveFromMap` first, then direct user photo, then reference fetch) AND patches `hasUserUploadedPhotos` (`canonical_mint_asset_service.dart:39`) to detect URL-encoded `users%2f` from `getDownloadURL()`. Documents affected 2026 SKU cards. |
| **MF-I6** | **Preserve Shipped `_cleanUrl` Semantics in `extractUserPhoto`:** Only `https://`, `http://`, or `/` path candidates are returned by `extractUserPhoto`; non-URL sentinels (`'N/A'`, `'pending'`, `'none'`, `'null'`, `'—'`, `'gs://...'`, bare filenames `'IMG_001.jpg'`) return `''` and fall through cleanly to canonical/reference instead of locking onto a dead placeholder. Tested explicitly. |
| **MF-I7** | **Prove Firestore Reference-Index `public_url` Forms:** Quotes `build_image_index.py:46, 53–105, 303`, `build_currency_image_index.py:40–42, 267`, and `promote_user_photos.py:35, 130` verbatim and tests one sanitized fixture per emitted `public_url` form against `isOwnedStorageUrl`. |
| **MF-I5'** | **Same-State Instance Refresh Proof & `ref_image_widget.dart` Path Fix:** Passes `key: const ValueKey('card')` across both `pumpWidget` calls, asserts `expect(identical(stateBefore, stateAfter), isTrue)` and `expect(fetchCount, 2)`, and cites the full path `numista_mobile/lib/widgets/common/ref_image_widget.dart:57`. |

---

## 3. Requested Action
- **Grok Bot CoS (`GROKCOS`):** Please score `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.9.md` against `git show 4d17ca5e:...` (target $\ge 95$ each), then route to **Stand Alone Grok (`SAG`, `grok-4.7`)** for independent scoring ($\ge 95$) before Founder Eric's typed YES.
- **Next on AG CoS v5 Desk:** Immediately authoring **NET-813 Unified Coin Details View Plan v1.4** (`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.4.md`, ETA 16:50 ET).
