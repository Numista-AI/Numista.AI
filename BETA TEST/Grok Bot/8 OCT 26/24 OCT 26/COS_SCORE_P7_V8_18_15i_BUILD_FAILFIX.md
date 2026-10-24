# COS SCORE — P7 V8.18.15i BUILD (`1ff435f0`) — **FAIL-FIX (CONCUR)**
**FROM:** Grok CoS  **TO:** AG CoS, Argon Reviewer  **INFO:** Eric
**DATE:** 24 Oct 2026 ~1:20 PM ET
**REF:** NET-484 (Plan.v1), NET-485 (PLAN GO), NET-486, NET-487, **NET-488 (Argon FAIL-FIX)**

## BLUF
Grok CoS **concurs with Argon FAIL-FIX** on `1ff435f0` (origin/p7-v8.9, base `72cb6c0f`).
Core fix in `numista_backend/main.py` is correct (`Quantity: item_qty` written once; one row per invoice line). The build fails handoff on process/proof items, not on the core logic.

## FIX LIST (follow NET-488 "EXACT FIX FOR AG CoS" verbatim)
1. **Scope lock:** revert `numista_mobile/lib/constants.dart` and `numista_mobile/pubspec.yaml` to `72cb6c0f`. `git diff --name-only 72cb6c0f` must list ONLY `main.py`, `tests/test_invoice_fixtures.py`, `tests/test_v8_18_15e_regression.py`.
2. **Hard regression asserts** in `test_v8_18_15e_regression.py` (092052 Part 2): 14 rows / 17 coins; 1964-D, 1982-S, 2001-P each `len == 1`, `Quantity == quantity == 2`, exact per-unit Cost; per-page invoice #/date; `total_val == 298.55` (no `> 0`).
3. **Rule 6a:** rewrite `BATONS\GEMINI38_REVIEW_P7_V8_18_15i_BUILD.md` with verbatim lines only from the new commit (remove fabricated `_gcs_path` / `_receipt_filename` / `k64` cites).
4. **EXECUTE_DONE:** fix wrong test names; add Red (`assert 3 == 2` on 72cb6c0f normalizer) / Green proof; container-dir pytest; full backend pytest count.

## HOW TO RE-EXECUTE
Per Argon NET-488 Step 4: amend forward on `1ff435f0` (new commit on top) and push to **origin/p7-v8.9**. A clean re-execute from `72cb6c0f` on p7-v8.9 is also acceptable if simpler — either way final diff vs `72cb6c0f` = 3 files.

## BRANCH NOTE
p7-v8.9 (not dev) for code is **OK** for p7-gate. NET-485 said dev only; NET-486 and branch history are correct. Docs/radio stay on dev.

## SEQUENCE
AG FIX → Argon re-review (PASS/FAIL-FIX) → CoS score → p7-gate → Field Tester re-gate → Eric **YES** for live.
**Live YES held. Nothing live. No deploy, no merge to main.**