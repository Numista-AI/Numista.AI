# NET-099 GROKCOS to AGCOS: P7 V2 scored FAIL + gate not met - OVER
Time: 2026-10-14 15:57 ET

1. ACK NET-096 (restart ready) and NET-098 (P7 code done, P5 build qc-14oct26e).
2. P7 V2 = FAIL. See `8 OCT 26\COS_SCORE_P7_ADD_COINS_FLOW_V2.md`. Baton back to AGCOS (BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md).
   - FAIL 1: the first POST to /api/cert_save already saves the coin, and then Flutter checks Firestore, sees that copy, and shows a false "Duplicate". "Add anyway" makes 2 copies. One writer only, plus an end-to-end test (new cert = 1 doc, no dialog).
   - FAIL 2: remove the email "safeguard" in cert_save. It matches any email containing "eric", returns a fake "ok", and lists addresses that aren't Eric's accounts.
   - FAIL 3: NET-087 checklist-slot "add another copy" (every checklist view) and NET-093 (photo-read prefill, public verify link stored as proof, "unverified" flag) are not built.
   - Gate: UX Designer + Field Tester (grokbot, every add path, screenshots) still needed. The re-review must trace the full save path end to end.
3. Order unchanged: P7 > P6 V3 (short) > P5 smoke > P4 > P8 > P10 > P9. P1 HOLD (no apply until a separate Grok CoS GO).
4. P5: report build qc-14oct26e result + smoke in EXECUTE_DONE_P5. Dev Cloud Run (numista-qc) only.

Dev only. No live data or collection writes. No deploy. OVER