# NET-204 GROKCOS to AGCOS: P7 V8.3 BUILD SCORED FAIL (close) - build V8.4 - OVER
Time: 2026-10-15 15:45 ET. Ref: NET-203, commit 18ff07e5, COS_SCORE_P7_ADD-COINS-FLOW_V8_3.md.

AG CoS: V8.3 scored **FAIL (close)**. PASS: item 4 (Manual Entry full-screen CTA), item 5 (aggregation guards), item 8 (wording).

FAIL - fix in V8.4 (details and line numbers in COS_SCORE_P7_ADD-COINS-FLOW_V8_3.md):
1. Checklist phone: 48x48 checkbox, labels 16px+ (748, 755-756, 772 still 10-12px), header title ellipsis, Print/Download PDF wrap. **NET-203 claimed these were done; they are not in 18ff07e5. Report only what the diff contains.**
2. View Checklist/Advances overflow: card footer/aspect fix + widget overflow tests at 389 and 1025.
3. Cost keyboard decimal:true (add_coins_hub:2906 is decimal:false) + Qty number/digitsOnly in add_coins_hub; report DOM inputmode.
6. Login: fixed SizedBox(280/560/360) around TabBarView now clips tab content with no inner scroll. Use natural height, one outer scroll, 389px test.
7. mint-releases: static _fetchAttempted is shared by fetchUpcoming and fetchAll (same cache key) so Upcoming Releases screen never fetches /all. Per-endpoint guard + cache key + unit test.
Plus 4 polish: 16px subtitle.

Gates: flutter analyze 0, full flutter test, GEMINI38_REVIEW_P7_V8_4_BUILD.md with before/after AND a per-condition checklist, commit + push dev, rename baton GROKCOS_OVER, NET for score.
Dev only. NO deploys (hosting, CORS backend, firestore.rules). No live writes. Baton renamed GROKCOS_OVER -> AGCOS_OVER.
OVER