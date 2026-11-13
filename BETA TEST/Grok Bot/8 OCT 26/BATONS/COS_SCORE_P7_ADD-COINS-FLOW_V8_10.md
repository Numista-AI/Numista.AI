# COS SCORE - P7 ADD-COINS-FLOW V8.10 BUILD
Scorer: Grok CoS | 2026-10-16 ~15:40 ET | Reviewed: code `747f7051` on origin/p7-v8.9 (docs a8cab08e / f6a01460 on dev) + GEMINI38_REVIEW_P7_V8_10_BUILD.md + NET-284 + independent read of worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` @ 747f7051 (clean).
Verdict: **PASS (code).** All 7 NET-278 blockers + 7 NET-280 FT must-fixes present in source. Dev only. No deploys.

| # | Item (NET-278 / NET-280) | Score | Independent file:line |
|---|---|---|---|
| 278-1 | Static inputmode Year/Qty numeric, Cost decimal | **PASS (code); confirm in DOM on preview** | `web/index.html:148-173` MutationObserver + 500ms interval tags year/qty/quantity numeric, cost/price decimal; `web_input_helper_web.dart:5-26` static apply; `add_coin_manual_form.dart:98-100` post-frame apply; keyboardType numberWithOptions at `:156,222,235`. Label-matching depends on Flutter exposing aria-label/placeholder - UX must verify the attribute on the live input. |
| 278-2 | Print / Download PDF / Add Selected >= 48px | **PASS** | `program_manager_screen.dart:933-957` Print (SizedBox 48 + minimumSize 48), `:958+` Download PDF (SizedBox 48); Add Selected `:1667-1669` height 52. No `Size(0, 40)` / `height: 40` left in file. |
| 278-3 | Mint column wraps at 1280/1025 | **PASS** | `program_manager_screen.dart:1501,1568,1592` BoxConstraints maxWidth 380; `:1630-1641` Flexible + softWrap Text 18px. |
| 278-4 | Pound mojibake on detail + exports | **PASS (code)** | `coin_detail_screen.dart:69` and `:1004-1012` TextSanitizer.fixMojibake; PDF `checklist_generator_service.dart:29-32`; CSV `backup_export_service.dart` sanitizer from V8.9 kept. Test `p7_v810_checklist_generator_service_sanitizes_mojibake`. |
| 278-5 | My Collection All tab crash | **PASS (code)** | `my_collection_screen.dart:1390-1411` isUnauthOrDemo gates stats, currency and world streams to Stream.empty(). No dedicated crash test found in the 3 new tests - UX to confirm screen loads at both sizes. |
| 278-6 | Demo session survives Table view at 1025 | **PASS** | `auth_gate.dart:61` static _cachedDemoActive, `:66-85` initState + didUpdateWidget re-activate; cold-start restore `main.dart:225-233` reads `browse_demo_active` (same key written at `guest_seed_service.dart:24,31`). Closes the V8.9 optional hydrate note. |
| 278-7 | Snackbar clear of 'Sign in to save' | **PASS (code)** | `program_manager_screen.dart:1952-1955` _floatingSnackBarMargin (left inset to ~400px wide, bottom 24); `add_coins_hub.dart:558-561` same. |
| 280-1 | First letter dropped (Retailer etc.) | **PASS (code); FT must re-test** | `add_coin_manual_form.dart:84-96` 13 persistent FocusNodes; `:418-421` ValueKey('manual_field_$key') + controller + focusNode. Plausible root cause; only FT on the preview can prove it. |
| 280-2 | Notes + Quantity in coin view | **PASS** | `coin_detail_screen.dart:1527-1528`; `my_collection_screen.dart:3968,3988`. Note: `:1529-1530` filter still hides blank Notes (fine). |
| 280-3 | Checklist progress 1/39 -> 5/39 | **PASS (code)** | `slot_resolver.dart:379-399` _matches2026CurrencySlot with exclusive denom gates; cent/nickel slots reject other denoms `:401-417`; wired at `:509,652`. Test `p7_v810_slot_resolver_2026_currency_distinct_matching`. Systemic audit beyond the 2026 program not shown - FT to watch counts on other programs. |
| 280-4 | Red validation clears on typing / after reset | **PASS** | `add_coin_manual_form.dart:178-182` onChanged re-validate; reset `:315-325` clears + setState. Test `p7_v810_manual_form_clears_validation_on_input`. |
| 280-5 | Login icons empty boxes | **PASS (code)** | `web/index.html:73` Material Icons stylesheet. |
| 280-6 | 311 vs 312 one count source | **PASS** | No code change needed: Ask Morgan already uses the shared expandCollection fold (`morgan_chat_context.dart:341-347`). AG read-only audit: 314 docs, 3 set parents, 310x1 + 1x2 = 312; no deletions. FT to confirm Morgan says 312. |
| 280-7 | Console errors (EPN/BetaChecklist 403, news) | **PASS (partial evidence)** | `beta_checklist_service.dart:181-182,341-346` demo/anon/unknown guards. EPN + news guards from V8.9 unchanged. FT to re-check console for main.dart.js Uncaught. |
| Extra | Morgan modal X + guest flag | **PASS** | `morgan_setup_dialog.dart:182-192`; `morgan_prefs.dart:36-41`. |
| Gates | analyze 0 / 566 tests / GEMINI38 / dev-only | **PASS (reported)** | 3 new tests in group 'P7 V8.10 Fixes' in `p7_v8_ux_safety_test.dart`. Not re-run this watch. No live, backend or rules changes in diff. |

## GEMINI38 hygiene
**Improved, still not clean (2 of ~15 blocks wrong).** 13 blocks match source word for word. Wrong:
- Finding 2 claims `:936-947` is an OutlinedButton 'Print Checklist' calling `_showPrintOptions` and `:952-963` is a green ElevatedButton 'Download PDF' calling `_downloadBlankPdf`. Actual: `:933-957` ElevatedButton Print (pink F63366, `_showPrintOptionsDialog`), `:958+` OutlinedButton Download PDF. Those quoted blocks do not exist.
- Finding 3 cites the ConstrainedBox maxWidth 380 chip at `:1541-1555`; that range is the 'Add another' OutlinedButton. The chip is at `:1592`.
Rule applied: independent source wins. Functional PASS stands.

## Next
- Baton stays **GROKCOS_OVER** - AWAITING V8.10 PREVIEW (channel from origin/p7-v8.9 @ 747f7051) + UX Designer + Field Tester re-gate. Stall clock on GROKCOS starts 15:40 ET (2h mark ~17:40).
- FT needs Eric to sign **grokbot** into the V8.10 preview (same as NET-272/280).
- Still no ERIC baton and no deploy YES. Deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.
- AG: Rule 8 WAIT on P7; queued P1 HOLD, P4/P5/P6/P8/P9/P10 Rule 8 WAIT (not stalls).
- Live this watch: numista.ai 200, numista-vault.web.app 200.
