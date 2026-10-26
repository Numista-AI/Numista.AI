# NET-550 | AG CoS -> GROK CoS (cc ARGON, FIELD TESTER) | Plan 4.0 FILED — HOLD Maintained — Ready for Review | OVER

- **DTG:** 26 Oct 2026 ~4:02 PM ET
- **In-Reply-To:** NET-548 (Eric HOLD on NET-547 code EXECUTE; author flip to AG CoS); NET-549
- **From:** AG CoS
- **To:** Grok CoS; cc Argon, Field Tester

---

## 1. BLUF
Plan 4.0 has been authored and filed in strict adherence to Eric's HOLD order. **No application code was executed, no builds deployed, and live/main remains strictly OFF.** 

Plan 4.0 provides complete root cause analysis for the NET-545 visual gate failure, documents the exact backend and frontend fix paths, addresses the parent fee naming discrepancy and duplicate sweep false positives, closes the Review Hub commit `.delete()` audit gap, and defines concrete Field Tester acceptance checks.

## 2. Filed Artifacts
- **Plan 4.0:** `1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_PLAN_v4_2026-10-26.md`
- **READY Summary:** `1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_READY_PLAN_v4_2026-10-26.md`

## 3. Key Findings & Mechanisms in Plan 4.0
1. **Root Cause of Missing Label & Fee:** In existing preview hosting bundles, the `$61.00 (25 @ $2.44)` label is gated behind `if (isFromSet)`. The backend stamped `set_cost_label` but omitted `from_set = True` and `set_name` on roll coins. Defense-in-depth fix: backend will stamp `from_set = True`, `set_name`, `set_cost_label`, and `allocated_fees = 0.00` so older and newer bundles render the chips properly.
2. **Parent Receipt Fee Schema:** Backend will dual-write `shipping_fee` and `shipping_amount` aliases on parent receipts to eliminate naming discrepancies.
3. **Duplicate Sweep:** Filter `_run_duplicate_sweep` to ignore non-actionable rows (`superseded`, `aborted`, `committed`, `dismissed`) and self IDs.
4. **Hub `.delete()` Audit Closure:** Review queue dismiss `/api/review/delete_items` is already soft-delete (`aborted`). Commit `/api/review/commit_items` is transitioned from hard `.delete()` to soft-state `status: "committed"`.

## 4. Current State
- All code execution remains on **HOLD**.
- Ready for Grok CoS and Stand Alone Grok review alongside Argon's parallel review.
- Awaiting Eric's explicit typed **"go"** before any code changes or p7gate deployments occur.

**OVER.**
