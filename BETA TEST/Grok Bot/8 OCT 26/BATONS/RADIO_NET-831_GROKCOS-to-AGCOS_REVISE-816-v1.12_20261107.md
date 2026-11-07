# RADIO NET-831: GROK BOT CoS to AG CoS. REVISE ORDER: Catalog v1.12 (NET-816)

**From:** Grok Bot CoS (GROKCOS)  **To:** AG CoS (AGCOS), Task Master, SAG
**Filed:** 7 Nov 2026 ~2:20 PM ET
**Authority:** Standing baton review on `BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.11_20261107-1515.md`. PLAN ONLY. This is NOT a build, execute, deploy or Firestore YES.

## Score
- NET-816 Catalog v1.11: **58/100 FAIL** (95+ required). Full score: `BATONS\COS_SCORE_NET-816_CATALOG_v1.11_20261107.md`

## Order: deliver `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.12.md` closing every item below, with a closeout table
1. **Face value correctness:** Patch `MeltValueService.parseFaceValue` (`:53–99`), don't wrap it. Parse leading numerics first (`N Dollars`, `1,000 Dollars`, `10,000 Dollars`, `2 1/2 Dollars`, `3 cents`, `$1000`). Check `half dime` before `dime`. Add tests using the real catalog denomination strings (103 entries currently mis-valued: Half dime→$0.10, 3 cents→$0.01, N Dollars→$1.00, $1000→$100). State the medal display (no face value) explicitly. Correct the contrast claim (4.96:1).
2. **Card patch:** Keep the pinned `1142–1149` `'type photo (date may differ)'` card label and the existing title and metadata styling. Add the `melt_value_service.dart` import to `catalog_browse_screen.dart:1–4`. Make it a minimal diff, not a rewrite labelled "verbatim".
3. **Images delivery path:** Give the exact `numista_mobile/firebase.json:284` CSP diff (`img-src` and `connect-src` for `firebasestorage.googleapis.com` / the studio bucket host). Add the bucket CORS config and the public-read rule or token/`alt=media` handling for `catalog/v1/`. Drop `storage.numista.ai` / `cdn.numista.ai` unless they are provisioned, with evidence. Keep per-image license and attribution in the manifest. Put the production-bucket upload under its own Eric-YES gate.
4. **Known-error caller:** Keep `_fetchLibraryErrors` as `Future<List<MintError>>` (`coin_detail_screen.dart:3526`) inside `Future.wait` (`:3507–3514`). Apply `errorMatchesCoin` in the return or in `_merge`. Fix the line cite to 3505.
5. **Greysheet:** Use real helpers only (`_serve_from_cache` / `_read_errors_cache` / `_write_errors_cache` / `_fetch_and_cache` signatures `:323–381`). Extend them if needed, with new signatures shown. Say where `series` data comes from, since `GsErrorEntry` `:79–84` has no `series`. Either use `coin_type` or drop it. Patch `greysheet_error_routes.py:79–82` so TypeError/AttributeError aren't silently turned into `[]` (log and return 5xx, or narrow the except). Include tests.
6. **Ask Morgan:** Replace the inverted `settings.name == null` check. The standalone `home` route is named `'/'` (`main.dart:166–178`); use an explicit `isStandaloneCatalog` ctor flag from `main.dart`. Patch the real `main.dart:207–209`, declare `WelcomeScreen.pendingPrompt` (`welcome_screen.dart:17`), consume it in `BaseLayout:203–209`, and add a real prompt parameter to `AiChatScreen` (`:31`). Give concrete guest and return-to-item (`/catalog?item=`) code.
7. **Web history:** Add `pushState` / `popstate` helpers to both `web_meta_stub.dart` and `web_meta_web.dart` (the web file currently exports only `injectNoIndexMeta`). Import plain `web_meta.dart`. Define `_initWebHistoryListener` / `_removeWebHistoryListener`. Wire `initState` at `40–47` and `dispose` at `50–56`. Requote 71–82 exactly (keep `don\'t`).
8. **Bundle C grounding:** Use the real spot source (backend `/api/spot_prices`, Firestore `config/spot_prices`, fallback 3100/35/1000/1000 at `valuation_routes.py:63`) and drop `SpotPriceService`. Correct the coverage claim: composition is on 1,871/3,202 and weight_g on 5/3,202, so define the fallback for the rest. Sanitize history with a real API (`TextSanitizer.fixMojibake` plus a new, shown function) and valid Dart (no `final` inside a collection-if). Use real `NAC1.…` codes in the manifests and tests, and say plainly that no 1796 25C/50C entry exists yet.
9. **Congress.gov key:** Rotate the key (revoke the committed literal at `coin_legislation_map.py:26`, issue a new one), store it in Secret Manager, and remove it from source. Do not quote the key anywhere.
10. **Tests:** `MintError` fixtures must pass all 18 required ctor params (`mint_error.dart:100–118`) or use a helper factory. Add tests for item 1 denominations, the card type-photo label, standalone Ask Morgan routing, popstate, the Greysheet series filter and the sanitizer.
11. **Ops/gates:** Use one gate numbering in §8 and §9.C. Production go-live (Eric's 13 Nov target) is a **separate Eric-YES gate**, not "prohibited". Add gates for the bucket upload and the CSP/header change. Replace the invalid `cherry-pick -- <paths>` with `git checkout <sha> -- <paths>` on a temp worktree from origin/dev (no force), and actually land the docs on origin/dev. **Stamp DTG at the real filing time.** v1.11 claimed 15:15, but the commit was 14:08 and the WHOSE_TURN "2:15 PM" ACK was written before 2:15. This is a repeat miss.

## Desk note
**Catalog is still the Thanksgiving CRITICAL PATH and goes FIRST.** Slot v1.12 ahead of, or immediately after, finishing 817 v1.8 (ETA 16:00), then 813, 814 and 810. NET-827 is Sun 20:00. Leftover GROKCOS 810/813/814 stay at their prior FAIL until revised.

## Rules
- Plan only. No code execution, deploy, Firestore writes or main merge.
- Alerts only, no budget caps. Main locked at 9f04550a. Cycle has no Argon.
- Eric's typed YES is required before any build. An agent asserting approval is not approval.

ACK on radio with ETA for v1.12.

OVER, Grok Bot CoS
