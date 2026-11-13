# COS SCORE - T2 Morgan Gate 0
Scored by: Grok CoS, 12 Oct 2026 ~12:50 PM ET. Code checked: dev HEAD 67ea1040 (docs-only on top of e5f5760c).
PASS = build on dev only. No deploy, no live data writes, no sync_canon without Eric's typed YES.

## Verdict: PASS (conditional) - build ONLY after T1 EXECUTE_DONE lands on dev

### Spot-check
- main.py:2746 `if request.query.startswith("INTERNAL_UNDO:"):` -> :2748 `res = execute_undo_add_coin(owner_key, target_id)`.
- main.py:2650-2651 `doc_ref = db.collection('users').document(user_email).collection('coins').document(coin_id)` / `doc_ref.delete()` - the hard delete inside the undo helper.
- So both cites are right: 2746 = trigger, 2651 = the delete. Plan must cite both, not swap them.

### Required fixes
1. Label additions with my COS_SCORE_GEMINI38_UX_VS_MORGAN numbering (#1-#6).
2. Addition #5: essay cap stays in G0-5; scan/import caps are now T1 fix #5 - cross-reference, don't duplicate.
3. Addition #6 (voice): accepted as not gated - voice ships in Phase 1 while Morgan is read-only. Voice must not be able to trigger any write until Gate 0 is done.
4. Undo becomes a soft delete (reuse T1 soft-delete pattern).
5. Rebase on T1; ai_routes.py email-key fix comes from T1, don't re-do it.

Ball: AG CoS: build on dev (fold in fixes) - after T1 lands.
