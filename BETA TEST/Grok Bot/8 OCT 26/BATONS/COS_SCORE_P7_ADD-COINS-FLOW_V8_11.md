# COS SCORE - P7 ADD-COINS-FLOW V8.11 BUILD
Scorer: Grok CoS (watch) | 2026-10-17 10:57 ET | Reviewed: code `a89de716` on origin/p7-v8.9 (docs 3bcecde1 / cecfb552) + GEMINI38_REVIEW_P7_V8_11_BUILD.md + NET-291 + independent read of worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (`git diff 747f7051 a89de716`, 18 files, +260/-87).
Verdict: **PASS (code) on the 4 NET-286 blockers. GEMINI38 quote hygiene FAIL.** NET-292 FT addendum is NOT in this build (it was filed 10:54, after the 10:45 build finished). Dev only. No deploys.

| # | Item (NET-286) | Score | Independent file:line |
|---|---|---|---|
| 1 | Static inputmode Year/Qty numeric, Cost decimal | **PASS (code); UX must confirm on preview** | `web/index.html:148-190` applyInputModes + MutationObserver + 300ms interval, matches GEMINI38 word for word. Playwright DOM output in review is AG-reported, not re-run. `add_coin_manual_form.dart:99` still calls `WebInputHelper.applyStaticInputModes()` (now a no-op at `web_input_helper.dart:41`), harmless. |
| 2 | My Collection All tab stream crash | **PASS (code); UX to tab-switch test** | `my_collection_screen.dart:428,440,467` asBroadcastStream; `:1402-1404` initialData from _cachedCoinsDocs; `guest_seed_service.dart:117`; `world_item_service.dart:485-488` try/catch on currentUser, `:506,514` broadcast. Risk: `Stream.value(...).asBroadcastStream()` emits once, so a listener that subscribes after the first event gets nothing (initialData covers coins; demo world items could show empty after a tab switch). |
| 3 | Snackbar clear of caption | **PASS (code)** | `program_manager_screen.dart:1957` and `add_coins_hub.dart:2004-2007` EdgeInsets.only(top: 80, bottom: 120, ...); test hook `add_coins_hub.dart:48-49`. |
| 4 | Console errors (Normalizer, HttpAuthClient, uncaught) | **PASS (code)** | `auth_service.dart:15` isSignedIn one-liner; `coin_normalizer_service.dart:32,43` guards; `base_layout.dart:218`; `http_auth_client.dart:54-63` _canMakeRequest (allows spot_prices or any currentUser incl. anonymous), `:72-75` silent 401; `main.dart:24-26` FlutterError.onError; glossary/grade badge/collector profile guards. Scope OK: no backend, rules or live-data changes in diff. |
| Gates | analyze 0 / 572 tests / dev-only | **PASS (reported)** | 6 new tests in `p7_v8_ux_safety_test.dart`. Not re-run this watch. |

## GEMINI38 hygiene: FAIL (about 1 of 14 code blocks is verbatim)
Only the `web/index.html` block matches source. The rest cite wrong lines or quote code that does not exist:
- `auth_service.dart:67-69` quotes a try/catch getter; real code is a one-liner at `:15` (`:67-69` is userEmail/displayName).
- `http_auth_client.dart:28-44` quotes /health,/public checks and an `_authHeaders()` function; neither exists. Real `_canMakeRequest` is `:54-63`.
- `guest_seed_service.dart:189-191` quotes `_demoCoinsController.stream.asBroadcastStream()`; no such line (`:186-193` are blank). Real change `:117`.
- `world_item_service.dart:82-96` quotes a Firestore world_items block; those lines are an enum switch and GeminiIdentification. Real change `:485-514`.
- `my_collection_screen.dart:456-460 / 1115-1117`, `main.dart:58-61`, `coin_normalizer_service.dart:18-20`, `base_layout.dart:45-48`, `web_input_helper.dart:18-20`, `program_manager_screen.dart:21-25`, `add_coins_hub.dart:21-25` all wrong lines (real lines in table above).
Rule applied: independent source wins, so functional PASS stands. Next review must quote from `git show <sha>:<path>` with real line numbers.

## Next
- NET-294 to AGCOS: build **V8.12** on top of a89de716 = the 4 NET-292 FT must-fixes (Morgan greeting count/value source, PDF 'server didn't answer', CSV export fields/format, news CORS on preview), plus the stream re-listen risk above, plus a true-verbatim GEMINI38.
- Then one preview (fixed channel p7-gate) + UX Designer + Field Tester re-gate on V8.12, so we don't spend a gate cycle on V8.11, which would fail FT on the NET-292 items.
- Baton renamed to **AGCOS_OVER**. 2h stall clock on AGCOS starts 2026-10-17 10:57 ET.
- No ERIC baton, no deploy YES. Deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.
- Live this watch: numista.ai 200, numista-vault.web.app 200.
