# NET-166 GROK CoS -> AG CoS: P7 V7 preview gate FAIL (CORS), see BATONS\FT_GATE_P7_V7.md
Field Tester (9:58 AM ET): manual entry PASS. Checklist Add Selected Coins FAIL, "Failed to fetch": the backend CORS rules don't allow the preview origin https://numista-vault--p7-v7-gate-o3flke1i.web.app. About 120 blocked calls (add_coins, ui_variant, news/feed, dismissed_news, spot_prices, mint-releases/upcoming). No confirm dialog was seen.
Plan.v1 first, dev only, systemic:
1. Allow the Firebase preview channels in backend CORS with a tight regex (^https://numista-vault--[a-z0-9-]+\.web\.app$ and the default site), NOT a wildcard. Add a test.
2. Explain: Field Tester says LIVE spot_prices is also CORS-blocked. Check it from numista.ai.
3. Firestore runAggregationQuery 403 (rules?).
4. 404 /assets/assets/mint_mark_diagrams/*.png (doubled path).
5. Confirm dialog on Add Selected Coins: expected per V7 or not?
A backend change reaches the live Cloud Run only on Eric's typed YES. P7 stays in my hands until the re-gate.
OVER
