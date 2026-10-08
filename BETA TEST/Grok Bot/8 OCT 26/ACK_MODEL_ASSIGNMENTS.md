# ACK: MODEL ASSIGNMENTS (8 Oct 2026 ~15:22 ET)
- **Order:** `BETA TEST\Grok Bot\8 OCT 26\FOR_AG_COS_MODEL_ASSIGNMENTS_UX_MORGAN.md`
- **Receiver:** Antigravity CoS
- **Status:** ACKNOWLEDGED & ASSIGNED.

## Sub-Agent & Model Allocation Matrix:
1. **Morgan Safety ("Gate 0") & REQ_031 Hotfix Plan:**
   - **Model:** Claude Opus 4.6 (Thinking)
   - **Scope:** Proposal-first confirm card pattern, soft delete (30-day trash), server action audit logging, blocking rate & scraper caps, financial data stripping (Privacy Mode), and unprotected write route lockdown.
   - **Deliverables:** `PLAN_V1_REQ031_HOTFIX.md`, `ROUTE_INVENTORY_031.csv`, `PLAN_V1_MORGAN_GATE0.md`.
2. **UX Fixes (Fixes 2, 3, 1, 4, 5 under REQ_032):**
   - **Model:** Claude Sonnet 4.6 (Thinking)
   - **Scope:** Fix 2 (18px+ text / full-width buttons), Fix 3 (PIN screen & masking fix), Fix 1 (checklist rows & count format, following REQ_034/036 data), Fix 4 (6-item menu), Fix 5 (3 big Add Coin options).
   - **Deliverables:** `PLAN_V1_REQ032_UX.md`.
3. **Independent Reviewer:**
   - **Model:** Gemini 3.8 Flash
   - **Scope:** Reviewer only. Must quote exact file:line actually opened. No code writes. Canned agreement rejected.
   - **Deliverables:** `GEMINI38_REVIEW_<track>.md` for each plan.

All work remains on `dev` (baseline `e5f5760c`). No live data writes. No deployment without Eric's explicit typed YES.
