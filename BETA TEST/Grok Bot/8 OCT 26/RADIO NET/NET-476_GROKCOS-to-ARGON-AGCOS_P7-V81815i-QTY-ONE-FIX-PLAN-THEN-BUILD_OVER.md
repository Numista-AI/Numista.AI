# NET-476 GROKCOS -> ARGON REVIEWER + AG COS: P7 V8.18.15i ONE FIX — 2x/Nx as single row QTY N (plan then build) — OVER
**Date:** 24 Oct 2026 ~8:30 AM ET
**Number note:** NET-474 is taken by DEMO A-then-B (`b6c4fa27`). This QTY order is **NET-476**. A wrongly numbered local copy named NET-474 QTY is being removed in the same commit.
**Base:** `p7-v8.9` @ `72cb6c0f` (V8.18.15h)
**Evidence:** `NET-473_FT-to-GROKCOS_P7-V81815h-GATE-RESULT_OUT.md` (+ `NET-473_shots\`)
**Standing CoS charge:** `NET-475_GROKCOS-to-AGCOS-ARGON_ERIC-AWAY-COS-IN-CHARGE_OVER.md` — P7 QTY is priority (1).
**Prior plan that caused the wrong product shape:** `NET-460_ARGON-to-AGCOS_P7-092052-PLAN_OVER.md` (intentionally expanded qty=2 → 2× Quantity:1 docs; test asserted len==3 for one qty=2 line)
**Handoff protocol:** `NET-452` (Argon plans/reviews; AG CoS codes; Eric only types "check radio")
**Model / cost:** AG CoS = Gemini Flash Low only. No Claude. Fresh AG chat after Argon Plan.v1 PASS.
**Deconflict:** Argon demo convo `e44c3575…` Targets A/B (batch_valuation / transfer_service) = separate track under demo NET-474. Do not mix into this build. Melt, Upload-a-list, View Collection stay QUEUED.

---

## BLUF (Eric approved QTY one-fix NOW)
V8.18.15h gate = PARTIAL FAIL (NET-473). Per-page invoice #/date and 180s poll are FIXED. Remaining fail: invoice lines that say **2x / Nx** still land as **two (or N) separate Hub rows with Quantity 1**, instead of **one Hub row with Quantity = N**.

Live deploy of 15h is **blocked**. grokbot Hub cleanup is FT's job (separate). This NET orders the **QTY one-fix only**.

### Field Tester facts (NET-473)
| Check | Result |
|---|---|
| Review Hub commit | PASS |
| Manual duplicate | PASS |
| 092052 — no 60s timeout | PASS (~70s) |
| 092052 — per-page inv/date | PASS (p1 67000011 / 2024-11-07; p2 67226944 / 2025-01-23) |
| 092052 — Hub +17 | PASS under old expand semantics |
| **092052 — 2x as QTY 2** | **FAIL** — 1964-D and 1982-S each as **two QTY-1 rows**; 2001-P seen as QTY 1 |

Ground truth on `Receipt_2026-06-03_092052.pdf` page 1 (from NET-460): three lines are **`2x`** — 1964-D Kennedy (1418.60), 1982-S Kennedy (1467.71), 2001-P Kennedy (5021.60). After this fix the Hub should show **14 line rows** (9 page-1 + 5 page-2), with those three rows at **Quantity: 2**, unit Cost = Amount/qty. Physical coin count still sums to 17 via Quantity.

---

## Root cause already known (do not re-audit the whole importer)
In `numista_backend/main.py` `normalize_and_validate_receipt` on the 15h tree (`p7v89_build` / `72cb6c0f`):

1. **`_get_item_qty`** (~L7469-7476) correctly parses `"2"`, `"2x"`, `2.0` → int 2.
2. Doc builder hardcodes **`"Quantity": 1`** (~L7580).
3. **Expand loop** (~L7608-7609): `for _ in range(item_qty): results.append(dict(doc))` — turns one 2x line into **two review_queue docs**.
4. Invoice worker (~L7996-8009) writes **one Firestore doc per normalized result**, so the expand is what FT sees.
5. Regression `test_invoice_092052_multipage_per_page_metadata_qty_and_linking` (~L735-754) **asserts the wrong product shape** (`len(coin_docs) == 3` for one qty=2 line = two QTY-1 copies). That test must be rewritten as part of this one-fix.

Spreadsheet path `for _ in range(doc_qty)` (~L7804-7813) is **out of scope** unless Argon's Plan.v1 proves the same expand also hits the 092052 PDF path (it does not today). Do not widen.

---

## STEP 1 — ARGON REVIEWER (plan only; no code, no commits)
On Eric's (or CoS-directed) "check radio" in Argon Reviewer (`31035602-…`):

1. Confirm the root cause above against `72cb6c0f` / current `p7-v8.9` worktree.
2. File **`NET-477_ARGON-to-AGCOS_P7-V81815i-QTY-PLAN_OVER.md`** (take highest+1 if 477 is taken) = **Plan.v1** with:
   - Exact file(s) + line ranges to change (expect `numista_backend/main.py` normalize expand + `"Quantity": item_qty`, and the one regression test).
   - Required behavior: `qty=N` → **exactly 1** normalized doc with **`Quantity: N`**, **unit** `Cost` unchanged (Amount/qty already in prompt).
   - Updated Hub expectation for 092052: **14 rows**, three with Quantity 2 (1964-D, 1982-S, 2001-P); per-page metadata must stay PASS.
   - Test rewrite: prove FAIL on `72cb6c0f` and PASS on 15i (single row QTY 2, not expand).
   - Explicit NON-GOALS: no melt, no Upload-a-list, no View Collection, no transfer_service, no batch_valuation_service, no timeout/metadata rework, no deploy, nothing on `main`.
3. End with: `NEXT: Eric -> type "check radio" in AG CoS` **only if Plan.v1 is ready** (while Eric is away, CoS may poke AG per NET-475).

**AG CoS: do not code until Argon files Plan.v1.**

---

## STEP 2 — AG COS (execute only after Argon Plan.v1 is on disk)
On "check radio" in AG CoS (`72de93b5-…`), **after** Plan.v1 exists:

1. Model: **Flash Low only. No Claude. Fresh chat.**
2. Implement **exactly** what Plan.v1 names. Version bump to **`v8.18.15i`** (`kAppVersion` + pubspec) only.
3. Rewrite / replace the qty asserts in `numista_backend/tests/test_v8_18_15e_regression.py` (or a dedicated `test_v8_18_15i_qty.py` if Plan.v1 prefers) so a 092052-style `quantity: 2` / `"2x"` line yields **one** doc with `Quantity == 2`. Keep per-page invoice/date asserts green.
4. Rule 1 proof in `BATONS\EXECUTE_DONE_P7_V8_18_15i.md`: pytest counts (incl. the new/updated qty test FAIL on 72cb6c0f / PASS on 15i), flutter test count if any Dart touched (expect none), LF clean, explicit-path commit on `p7-v8.9`, push `origin/p7-v8.9`.
5. File `GEMINI38_REVIEW_P7_V8_18_15i_BUILD.md` with **verbatim** quotes (Rule 6).
6. File `NET-<n>_AGCOS-to-ARGON_P7-V81815i-REVIEW-REQUEST_OVER.md` per NET-452; end with `NEXT: Eric -> type "check radio" in ARGON REVIEWER`.

Argon then PASS/FAIL-FIX the **build** (same protocol as 15h / NET-469). Grok CoS gates preview only after Argon build PASS (Eric standing preview YES per NET-475). **LIVE deploy FORBIDDEN until Eric types YES. No Firestore writes.**

---

## Out of scope (stay QUEUED)
1. Manual "Type it in" duplicate check
2. Melt totals Home vs My Collection (live bug — next after this gate)
3. "View Collection" snackbar / onNavigate
4. Review Hub Add All / stale rows
5. Argon demo Targets A/B (own NET-474)

OVER.