# BATON: GROK BOT CoS REVIEW — FAILFIX PLAN NET-777 CATALOG v1.11 (NET-816)

- **From:** AG CoS v4 Work / Catalog Day Team (`ba2bfdb2`)
- **To:** Grok Bot CoS (GROKCOS), Task Master, Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **Timestamp:** 2026-11-07T15:15:00-05:00 (ET)
- **Track:** NET-816 (Thanksgiving Critical Path FIRST — Public Catalog Browse FAILFIX Plan)
- **Target Score:** >=95/100 (Pass required before SAG review and Eric typed YES)
- **Delivered Plan:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.11.md`
- **SHA256:** 4260A171348430A5A5D9013DD3609BBBD8AC94F6CF2A96F934C0C50EE52CE71C
- **Proword:** OVER

## Delivered Artifacts
1. `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.11.md` (and identical mirrors in BATONS/, RADIO NET/, INBOX/, OUTBOX/, and 1 NUMISTA.AI/INBOX)
2. Closed all 9 numbered must-fixes from `COS_SCORE_NET-816_CATALOG_v1.10_20261107.md` and `RADIO_NET-829`:
   - Must-Fix 1 (Retail Grounding): Stated plainly retail prices absent at launch; face value dynamically parsed via `MeltValueService.parseFaceValue`; amber chip "Value pending AI estimate"; join strictly on `nac_code`.
   - Must-Fix 2 (Real Bucket & Image Allowlist): Real bucket `studio-9101802118-8c9a8.firebasestorage.app` (`firebase_options.dart:55`); image self-host / manifest step sequenced BEFORE guard activation; real `_CatalogCard` (lines 1069/1106) patch code; modal "Representative photo — date may differ" label (931–935) preserved.
   - Must-Fix 3 (CoinModel Type Checking): `int.tryParse(coin.year)` int matching; non-nullable `programSeries`/`variety`/`strikeType` blank checks; `MintError.fromFirestore` patched for `series`/`coinTypes`; `GreysheetErrorService.get_error_entries` signature, filter, and cache key updated without silent `[]`.
   - Must-Fix 4 (Navigation): Real `_showItemDetailModal` (line 810); web interop via `web_meta.dart`; lifecycle wiring in `initState`/`dispose` (50–55); deep-link contract `?item=` / `initialNacCode` (`main.dart:163–164`); real lines 71–82 quote.
   - Must-Fix 5 (Ask Morgan): Standalone catalog mode detection; `await launchUrl`; `main.dart` and `WelcomeScreen` consume `prompt`; guest sign-in flow with return-to-item link.
   - Must-Fix 6 (Deletions): Call site line 3454 deleted on both dev and p7; dev loader coordinates lines 5205–5231; p7 orphan comment line 5548 deleted; eBay preserved.
   - Must-Fix 7 (Precious Metals & Legislation): Extended existing `MeltValueService`; historical alloy corrections (1943 steel, 1944–46 brass, 1962–82 no tin, post-1982 zinc core / copper plating, pre-1932 silver quarters, 40% and silver proofs); history sanitization for lines 865–873; legislation grounded on `congress_url` and tuples with key in Secret Manager; 1796–97 and mint plate manifests.
   - Must-Fix 8 (Executable Tests): Package `package:numista_ai/...`; testable card; String `year` fixtures; new file `numista_mobile/test/catalog_browse_v1_11_test.dart` (preserving existing 91-line test); complete suite.
   - Must-Fix 9 (Ops & Gates): Exact cherry-pick command for `origin/dev`; split YES gates; Eric-YES row before preview deploy; restored NET-818 Stripe promo owner; accurate DTG.

## Standing Boundaries
Strict PLAN ONLY. origin/main locked at `9f04550a`. Stripe strictly OFF. Alerts only ($20/mo), ZERO caps. Cycle has no Argon. WAKE/revise never authorizes live deploy or main merge.

OVER — Antigravity CoS v4 Work (`ba2bfdb2`)
