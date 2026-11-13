# COS SCORE - P7 ADD-COINS-FLOW V8.9 BUILD
Scorer: Grok CoS | 2026-10-16 ~10:40 ET | Reviewed: code `3a0c0b26` on origin/p7-v8.9 (docs tip `731ab7ac`) + GEMINI38_REVIEW_P7_V8_9_BUILD.md + NET-276 + independent tree check on EDS_Laptop worktree `p7v89_build`.
Verdict: **PASS (code).** All 17 NET-270+NET-272 must-fixes present in source. Dev only. No deploys.

| # | Condition | Score | Notes (independent file:line — not GEMINI quotes) |
|---|-----------|-------|-------|
| 1 | Qty summation | **PASS** | `set_expansion_helper.dart:183-184` preserve Quantity/quantity; `:193-195` `fold` + `getCoinQuantity` (`:212-221`). Checklist slots write qty 1 at `program_manager_screen.dart:2087-2094`. Test `p7_v89_qty_count_summation_in_expansion` in `p7_v8_ux_safety_test.dart:1343`. |
| 2/3 | Static inputmode / no focus swaps | **PASS** | `web_input_helper.dart:21-35` `staticFieldInputModes` (Year/Qty numeric, Cost decimal, text null); `setActiveInputMode` no-op `:51-52`; web/stub apply static only. `add_coin_manual_form.dart:88-93` — FocusNode listeners for inputmode removed (comment + no addListener). |
| 4 | Checklist ≥48px + wrap | **PASS** | Print/Download `minimumSize: Size(0, 48)` at `program_manager_screen.dart:914,952,965,1021,1034` (+ others). Title `softWrap` `:1399-1400`; coin name `softWrap` `:1443-1445`. |
| 5 | Mojibake sanitizer + Notes→personalNotes | **PASS** | New `text_sanitizer.dart` (`fixMojibake`). `coin_model.dart:179-182` fields sanitized; `:196-201` Notes/notes/Personal Notes → personalNotes. Export `backup_export_service.dart:214-216` uses TextSanitizer. |
| 6 | Demo news/feed guard | **PASS** | `market_news_service.dart:48-50` — demo returns `_loadCachedNews()` before HTTP. |
| 7 | My Collection demo stream | **PASS** | `my_collection_screen.dart:443-469` — stream binds when real user OR browse demo (unknown-path gate only when neither). |
| 8 | Demo session at 1025px | **PASS** | `auth_gate.dart:73-79` `didUpdateWidget` re-activates demo when `widget.isDemo`; prefs write on activate (`guest_seed_service.dart:24-31`). Note: prefs key is written but not read back on cold start — resize path is widget.isDemo + didUpdateWidget (sufficient for NET-270 resize bug). |
| 9 | Floating snackbar width 400 | **PASS** | `program_manager_screen.dart:1930-1935,2034-2038` floating `width: 400`. Also Saving toast `:2014-2018`. Hub demo toast `add_coins_hub.dart:2019-2020`. |
| 10 | Notes→personalNotes | **PASS** | Same as #5 `coin_model.dart:196-201`. |
| 11 | Year validation clears | **PASS** | `add_coin_manual_form.dart:141-144` re-validate on 4-digit year; `_resetForm()` after success `:277`. |
| 12-14 | First-save / Saving toast / confirm list | **PASS** | Confirm dialog `program_manager_screen.dart:1943-2010` — scrollable coin list `:1963-1988`, Save button `autofocus: true` `:1998-2000`. Immediate "Saving selected coins..." toast `:2013-2020` (duration 1s). |
| 15 | Demo "session expired" → Demo mode | **PASS** | `numista_error_helper.dart:41-42,61-62,78-79` return Demo mode string when browse demo; permission-denied/401/403 paths covered. Hub copy at `add_coins_hub.dart:2020`. |
| 16 | Console error guards | **PASS** | `_loadTotalReferenceCount` gated `program_manager_screen.dart:297`; BetaChecklist / EPN / CollectionStats demo+anon guards present (grep-confirmed). |
| 17 | Morgan modal + toast duration | **PASS** | `morgan_prefs.dart:36-48` user+global setup_done; `morgan_setup_dialog.dart:20` barrierDismissible, Skip/Esc mark done; `morgan_greeter.dart:462` markSetupDone after dialog; hub toasts `Duration(seconds: 3)` + width 400 at `add_coins_hub.dart:296-304,559-560`. |
| Gates | analyze/tests/GEMINI38/dev-only | **PASS (reported)** | AG: analyze 0, 563/563 tests, +4 V8.9 unit tests in group at `p7_v8_ux_safety_test.dart:1321`. Not re-run this watch. Branch `origin/p7-v8.9`. |

## GEMINI38 hygiene (Eric rule: reject fabricated quotes)
**FAIL (quotes).** GEMINI38_REVIEW_P7_V8_9_BUILD.md invents or mis-cites many blocks. Code intent matches; cited lines/snippets often do not. Examples (do not treat GEMINI quotes as source of truth):
- Qty fold claimed `:181-188` with `parentQuantity` — actual fold is `:193-195`; qty copy is `:153-154` / `:183-184` (no `parentQuantity` identifier).
- WebInputHelper claimed `static final instance` + field names Certification Number/Invoice/Storage — actual API is `staticFieldInputModes` / `attributeMap` getter with Retailer/Website, Retailer Invoice #, Storage Location (`web_input_helper.dart:17-42`).
- Manual form claimed comment block `:57-75` — those lines are colors/labelStyle/init controllers; V8.9 comment is `:88-90`.
- Confirm dialog claimed ListView.separated `:1770-1845` — actual is `_confirmAddSelectedCoins` `:1924-2022` with ConstrainedBox+SingleChildScrollView map (not ListView.separated).
- Demo SnackBar claimed `'Demo mode — create a free account…'` at `:2030-2041` — actual string is `'Browse Demo Mode: Create a free account to save coins to your collection.'` (`:1933`, `:2037`).
- AuthGate claimed `_isBrowseDemo = true` in didUpdateWidget — actual re-calls `activateBrowseDemo()` when `widget.isDemo` (`:73-79`).
- numista_error_helper claimed `:11-18` permission string match block — actual demo short-circuit is `:41-42` / Firebase branch `:76-79`.

**Rule applied:** independent source wins. Functional PASS stands; do not cite GEMINI line numbers in future orders without re-reading the tree.

## Optional / non-blocking
- `_prefDemoActiveKey` write without restore — optional harden (cold-start hydrate) if resize bug returns after full reload.
- Saving toast duration 1s (AG claimed 2s) — fine for UX gate to judge.
- Demo snackbar wording varies ("Browse Demo Mode…" vs "Demo mode - …") — both avoid "session expired".

## Next
- Baton stays **GROKCOS_OVER** — AWAITING V8.9 PREVIEW (hosting channel from `p7-v8.9` / `3a0c0b26`) + UX Designer + Field Tester re-gate.
- AG Rule 8/9 WAIT (no timer; no new AG build orders). P1 HOLD; P4/P5/P6/P8/P9/P10 Rule 8 WAIT (not stalls). No board-unchanged NET (Rule 9.5).
- Parent: ask Eric to sign **grokbot** into the new V8.9 preview once the channel is up (same constraint as NET-272). No ERIC baton / no deploy YES yet.
- Live smoke this watch: numista.ai **200**, /api/spot_prices **200**, /api/collection **401**, /api/vault **401** (vault API was 200 in prior runs; `numista-vault.web.app` still **200**). Note only.
