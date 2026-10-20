# COS SCORE - GreySheet hotfix rev 2 (44f8604d hotfix / 86ee05e0 p7 port)
Scorer: Grok CoS | 20 Oct 2026 16:03 ET | Re: NET-381B, NET-382C, NET-383

## Verdict: PASS (code). Ready for Eric's deploy YES.

## What I checked (git show 44f8604d, verbatim)
- `deal_spotter_service.py` calculate_arbitrage: `target_val = benchmark_val if benchmark_val > 0 else 0.0` (greysheet_bid kwarg fallback gone).
- `deal_spotter_service.py` match_wishlist_items: `benchmark_val = float(item.get("cpgRetail") or item.get("cpg_retail") or 0.0)` then `if benchmark_val <= 0: continue`. No greysheetBid, no 95.0. git grep finds no greysheet or 95.0 left in the file.
- 3 new tests in `test_greysheet_bid_display.py`: bid-only item gives no deal, empty item gives no deal, real cpgRetail=150 gives exactly 1 deal with cpg_retail 150.0 and no greysheet_bid / net_margin. This is the regression guard I asked for.
- `test_deal_spotter.py`: 3 tests moved to CPG inputs. GET /api/wishlist/deals default items in main.py carry cpgRetail (95.0, 125.0), so the endpoint still returns deals.
- p7 port 86ee05e0 diff is identical to the hotfix diff (only index lines differ).
- Exactly 3 files, stray windows/flutter generated files left uncommitted, origin/main untouched at 3c1bacf5. Hotfix branch is main + 3 commits (6370c65c, 1ddb1d1f, 44f8604d), 16 files total vs main.

## Grok re-run
- Hotfix worktree 44f8604d: targeted pytest 10/10. Full tests folder 517 passed, 3 failed (test_missing_images_csv x2, test_usmint_releases_scraper: local data files not in the worktree; untouched by this hotfix).
- P7 worktree 86ee05e0: targeted 10/10. Full tests folder 586 passed, 3 failed (test_missing_images_csv x2; test_identify_timeout cert-routes test = ModuleNotFoundError 'numista_backend' import path when run from the backend folder). None touch deal_spotter.

## Nits (not blocking)
1. `test_deal_spotter.py` line 1 gained a UTF-8 BOM. Python handles it; strip it on next touch.
2. The for-loop after `assert deals == []` in the bid-only test never runs. Harmless.
3. p7v89_build worktree has uncommitted RELEASE_NOTES.md + home_dashboard.dart v8.18.11 release-history entries (generated). Commit or drop before the gate preview build.

## Parked for Eric (not in this hotfix)
- main.py demo deals and match_wishlist_items still make a listing price at 78% of CPG (demo deals, already parked).
- main.py ~10432/10958 still derives `greysheet_bid = cpg_retail * 0.80` when GreySheet has no value and stores it (not displayed). Same "never fake data" family; for Eric's call.
- batch_greysheet scripts' string (already parked).

## Deploy path (only on Eric's typed YES)
Branch from origin/main 3c1bacf5, cherry-pick 6370c65c, 1ddb1d1f, 44f8604d (the hotfix branch is already exactly that). No dev merge.
