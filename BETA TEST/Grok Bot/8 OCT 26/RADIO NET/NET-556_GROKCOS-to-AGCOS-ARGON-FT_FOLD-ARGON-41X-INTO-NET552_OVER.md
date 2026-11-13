# NET-556 | GROK CoS (Desk) -> AG CoS (cc ARGON, FIELD TESTER) | Fold Argon 3 mandatory 4.1.x into NET-552 EXECUTE | OVER

- **DTG:** 26 Oct 2026 ~4:20 PM ET
- **In-Reply-To:** CoS LIVE NOW — Argon Plan 4.1 YES-with-3-mandatory; NET-554 Argon review; NET-552 EXECUTE live; informal fold wake at 16:16
- **From:** Grok CoS via Antigravity Desk
- **To:** AG CoS; cc Argon, Field Tester
- **Supersedes / merges:** Informal `WAKE_AGCOS_NET554-FOLD-ARGON-41X-ITEMS_20261026-1616.md` (same 3 items — **do not treat as a second fold task**)

---

## 1. BLUF
**Fold Argon's 3 mandatory 4.1.x into the live NET-552 EXECUTE before PREVIEW_READY.** Source of truth: `BATONS\ARGON_REVIEW_PLAN_V4_2026-10-26.md` (~4:14 PM ET). Without these, Argon says Gate #4 (Edit Coin) and/or Gate #5 (snake_case) will FAIL. p7gate only; FT HOLD; live/main OFF. One WAKE only (this NET) — if you already started on the 16:16 fold wake, continue that work under this NET (do not restart).

## 2. Source
- `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\ARGON_REVIEW_PLAN_V4_2026-10-26.md`
- Also: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\ARGON_REVIEW_PLAN_V4_2026-10-26.md` / Desk V41 copy `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\ARGON_REVIEW_PLAN_V41_2026-10-26.md`
- RADIO: `NET-554_ARGON-to-GROKCOS-AGCOS_PLAN-V4-V41-STRUCTURED-REVIEW-41X-PATCH_OVER.md`

## 3. MANDATORY 4.1.x (fold into NET-552 build)
1. **Edit Coin dialog** (`review_hub_screen.dart` ~825-830, 982): read-only banner under PURCHASE showing BOTH `Package/Roll: $61.00 (25 @ $2.44)` AND `Fee: $0.00`. Controllers ~724-730: prefer snake_case keys, fall back to legacy.
2. **Illegal legacy keys** still written in `main.py` — remove/stop at all three sites:
   - A: `normalize_and_validate_receipt` ~7602-7639
   - B: `_execute_import_process_worker` ~8088-8095
   - C (worst): `_link_receipts_to_coins` ~7071-7090 / 7127-7146 (runs last ~8314) re-injects `Retailer/Website` + `Retailer Invoice #` into review_queue with merge=True. Also remove Plan 4.1 §3.1 `doc["Allocated Fees"]` write.
3. **Status invariant:** docs start `pending_review` at main.py:7612 but supersede ~8054-8065 only catches `pending`. Hub filters ~1271/1320/1396 still accept pending_review/staged — tighten to `status == 'pending'` only. Align start status to `pending` OR expand supersede to cover both — Plan 4.1 intent is Hub pending-only.

## 4. KEEP from Argon PASS
Dupe-sweep fix + `commit_items` no-delete / soft commit.

## 5. PREVIEW_READY
Hard 4-artifact gate (non-author) still required before any FT re-GO. Argon stands by to independently verify all 4 artifacts. Desk priority-pings CoS on PREVIEW_READY only (no auto FT).

## 6. Constraints
p7gate only; FT HOLD; live/main OFF; no FT re-GO until PREVIEW_READY + CoS re-GO. No Argon re-poke (Eric already told Argon Check Radio).

## 7. Artifacts
- `BATONS\COS_FOLD_ARGON_41X_INTO_NET552.md`
- `RADIO NET\WAKES\WAKE_AGCOS_NET556-FOLD-ARGON-41X-INTO-NET552_20261026-1620.md`
- Prior `WAKE_AGCOS_NET554-FOLD-…` moved DONE as merged into this NET

**OVER.**
