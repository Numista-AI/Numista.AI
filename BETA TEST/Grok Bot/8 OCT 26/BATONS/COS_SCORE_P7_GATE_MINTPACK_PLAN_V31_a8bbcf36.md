# COS_SCORE | P7 GATE Mint-pack / Upload Invoice Plan v3.1 | a8bbcf36 / 00492-gus

- DTG: 26 Oct 2026 ~3:30 PM ET | Scorer: Grok CoS (handoff watch)
- Input: NET-544, PREVIEW_READY_P7_GATE_MINTPACK_PLAN_V31_a8bbcf36.md, EXECUTE_DONE_P7_GATE_MINTPACK_PLAN_V31.md
- Verdict: PASS-TO-CANARY (preview only). Not a live/main YES.

## Checked in code (git show a8bbcf36, numista_backend/main.py)
- `supersede_batch.set(snap.reference, {"status": "superseded"}, merge=True)` with `superseded_count` log line; no new `.delete()` on review_queue in backend diff.
- Review Hub filter: `(status == 'pending' || status == 'pending_review' || status == 'staged') && status != 'superseded' && status != 'committed'`.
- Indexes changed in numista_backend/firestore.indexes.json (AG reports CICAgNiroIEK / CICAgNjpgYIK READY on studio-9101802118-8c9a8).

## Watch items (FT must prove; not blockers to canary)
1. Proof 6 asked for before/after doc_id match on RE-upload; AG gave one stable hash only. FT: upload 26SQRP twice, confirm still ONE pending Hub row.
2. Supersede errors are caught and only logged as warning (`Error marking review_queue items superseded`) - a silent failure would re-create phantom rows. FT row count is the check.
3. review_hub_screen.dart diff is ~4.4K lines (likely line-ending churn) and contains `HttpAuthClient.delete(` (existing user Dismiss path?). Argon to confirm at next review; no review_queue delete from upload path.
4. Parent receipt field reported as `shipping_fee: 9.95` in run output vs `shipping_amount` in plan - confirm naming.

## Next
NET-545 re-GO Field Tester: 26SQRP canary (x2 upload) -> if PASS, full Invoices folder on FT account. Live/main/traffic OFF. Eric's account untouched.
