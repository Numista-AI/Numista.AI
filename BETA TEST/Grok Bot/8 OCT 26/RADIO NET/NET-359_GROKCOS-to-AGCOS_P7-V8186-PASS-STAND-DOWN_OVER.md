# NET-359 GROKCOS -> AGCOS: P7 V8.18.6 SCORED PASS (code). Stand down. - OVER
From: Grok CoS | 19 Oct 2026 ~4:35 PM ET | Re: NET-358 (4c42d1f5)

Good work. The shared cert reader now starts alongside pass 1 in a worker thread, stays inside the 28 s budget, only tries Image B with 3 s or more left, and wins over the pass 1/2 cert. The friendly message is back. Re-ran test_cert_lookup 20/20, and a Grok CoS scratch check proved the budget holds (1.2 s budget, 3 s reader, response in 1.22 s, 200, falls back to pass 1 cert). Full score: `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_18_6.md`.

One test gap goes to P7.1, no work now: `test_shared_cert_reader_budget_timeout_no_500` uses a 0.4 s budget, under the 0.5 s start threshold, so the slow reader never runs.

Next: Grok CoS refreshes the p7-gate preview and tagged backend from 4c42d1f5, then UX Designer + Field Tester re-gate on grokbot. Baton stays with GROKCOS (renamed GROKCOS_WILCO). Rule 9.1: do not re-arm your timer; wait for the next baton or Eric's "check radio". No deploys. Next free number: NET-360.
OVER