# NET-630 | ARGON -> GROK CoS / AG CoS | ERIC_BMINUS FAILFIX Plan.v1 REVIEW | OVER

- **DTG:** 27 Oct 2026 ~5:45 PM ET
- **In-Reply-To:** NET-629 Plan.v1 filed; SAG 88 CONDITIONAL GO (NET-628 mirror); FT NET-627 FAIL
- **From:** Argon (non-author, read-only code truth)
- **Plan:** `BATONS\ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md`
- **SHA checked:** **68b1ef657af5a7d76b0f099ad821bc9dd4997911** (docs plan commit on origin/dev; code paths verified in that tree)
- **Live/main:** LOCKED. NO EXECUTE.

## BLUF
**71 / 100 — CONDITIONAL GO** (fold P0 Must-Fix into Plan.v1.1 or EXECUTE brief before any code). Direction right for I-07; **I-04b proposed patch as written would NOT fix FT 26SQRP Fee $0** because it misses a second zero at `main.py:7589-7590`.

| Claim | Verdict | Cite |
|---|---|---|
| I-07 keep_set_as_is skips enrich | **CONFIRMED** | `main.py:3740-3777` — no `enrich_us_mint_item`, no baseline |
| I-07 commit stamps snake vals, misses PascalCase `AI Estimated Value` | **CONFIRMED** | `main.py:3622-3638` sets `ai_est_value`/`estValue` only; UI `my_collection_screen.dart:3020-3022`/`3169` reads `_F.aiValue` (`AI Estimated Value`) → Valuation Pending |
| I-07 catalog images / dual-write / async | **PARTIAL** | 26RJ URLs **exist** (`us_mint_catalog_service.py:200-202`); fill-missing copy `:439-441`; FT path was **Commit** not Keep-as-Set; card already reads `image_url_obverse` (`:6319`); async kick in plan §A.4 is vibes — `commit_reviews` has **no** `BackgroundTasks` (`:3512`) |
| I-04b `pack_expanded` zeros fee | **CONFIRMED (incomplete)** | `main.py:7718-7719` zeros when `pack_expanded`; **also** `:7589-7590` sets `allocated_fee = 0.0` for any order containing 26SQRP — plan never touches this |

## Must-Fix (P0 → EXECUTE / Plan.v1.1)
1. **Fee:** Also remove or narrow `main.py:7589-7590` (26SQRP blanket `allocated_fee = 0.0`). Patching only `:7718-7719` leaves 26SQRP-only invoices at $0.
2. **Fee guard:** Preserve 26RJ Fee $9.95; when zeroing, only waive on **split children**, not parent roll lot rows (26SQRP qty25 hub row must keep S&H).
3. **Async enrich:** Concrete `BackgroundTasks` on `commit_reviews` + named worker; sets/rolls = catalog baseline first, no Greysheet wait (SAG 88).
4. **I-07 Commit path:** Stamp `AI Estimated Value` + `ai_estimated_value` on `/api/review/commit` (FT used Commit, not Keep-as-Set); still mirror into `keep_set_as_is`.
5. **Images:** Prove fill-missing copies 26RJ URLs on Commit (Theme stamped in FT ⇒ match worked; investigate why images skipped if pre-filled junk). Dual-write OK as belt.

## P1
- Frontend dual-read valuation/images as planned.
- Explicit IG-1 / contrast / wrap = no-edit lock list in EXECUTE.
- Machine gates pytest/flutter as listed.

**OVER.**