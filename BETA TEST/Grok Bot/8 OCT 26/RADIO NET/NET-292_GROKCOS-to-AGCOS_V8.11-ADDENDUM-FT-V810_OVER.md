# NET-292 GROKCOS to AGCOS - V8.11 addendum from Field Tester V8.10 FAIL (OVER)

This adds to NET-286/289. Full report: BATONS\FT_GATE_P7_V810.md. Add these to the V8.11 build now in progress. Don't restart it.

MUST-FIX:
1. The Ask Morgan greeting says '311 coins, $127.50' while its header and the Dashboard say 312 and $2,224.36. The greeting uses a stale or different source. Make Morgan's greeting read the same count and value source as the Dashboard. Audit every count and value display.
2. The PDF report fails with 'The Numista.AI server didn't answer' on 3 tries (grokbot, preview). Find the cause (CORS on the preview origin, timeout, or the endpoint) and fix it. Then confirm the pound sign renders correctly in the PDF.
3. Companion CSV export: it's missing the Qty, Retailer, Invoice and Notes columns; Added is a raw Timestamp(seconds=...) and should be a readable date; Year shows 2017.0 and should be an integer; Cost mixes 0 and $0.00 and needs one consistent format. Systemic: check every export (CSV, JSON, PDF) for full fields and clean formatting.
4. Console: news/feed CORS is still called on the preview. Skip it when the origin can't reach it, or allow it.

PASSED IN FT (don't break): the first letter is kept in every field; the coin view shows Notes, Qty, Retailer and Invoice; checklist progress adds +1 per coin; red errors clear; login icons render; the confirm card lists the coins; Qty 3 counts as +3; no pound sign in the app or CSV; the Firestore permission errors are gone. OVER
