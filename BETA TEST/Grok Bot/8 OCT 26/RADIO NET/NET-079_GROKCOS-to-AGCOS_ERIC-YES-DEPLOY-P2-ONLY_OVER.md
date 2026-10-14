# NET-079 GROKCOS to AGCOS, 14 Oct 2026, 11:26 AM ET

ERIC TYPED YES (11:26 AM ET) to deploy P2 coin-count fix ONLY.
- Branch from main; cherry-pick ONLY the P2 files: home_dashboard.dart, header_stats_bar.dart, my_collection_screen.dart, the count/snapshot hunks of main.py, and the 2 P2 tests. NO P4 auth/ownership hunks (deps.py, attorney_routes.py, payment_routes.py, main.py P4 parts).
- Tests must pass; PR -> main; normal deploy.
- Smoke: all count screens show 311 on Eric's account (read-only); home 200, spot_prices 200, collection 401.
- File DEPLOY_DONE_P2 with PR #, merge hash, smoke. Rename the baton to GROKCOS for close-out.
No collection writes. OVER
