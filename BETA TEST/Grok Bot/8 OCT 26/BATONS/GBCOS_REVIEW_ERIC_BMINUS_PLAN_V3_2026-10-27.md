# GB CoS REVIEW — Eric B− Live Mint Plan.v3 (NET-623 / NET-624, Round 3 of max 4)

- **Reviewer:** Grok Bot Chief of Staff (GB)
- **DTG:** 2026-10-27 ~3:50 PM ET (America/New_York)
- **Inputs:**
  - `ERIC_BMINUS_LIVE_MINT_PLAN_v3_2026-10-27.md` (inherits Plan.v2 I-01..I-16, PM-01..PM-07, FT checklist)
  - `ARGON_REVIEW_ERIC_BMINUS_PLAN_V3_2026-10-27.md` (94/100 GO + IG-1..IG-3)
  - Prior: `GBCOS_REVIEW_ERIC_BMINUS_PLAN_V2_2026-10-27.md` (82 CONDITIONAL GO, GB-1..3)
  - Prior: `SAG_FEEDBACK_PLAN_V2_2026-10-27.md` (81 CONDITIONAL GO, locks a–d)
  - `FT_RETEST_CHECKLIST.md` / `FOUNDER_REVIEW_LOOP.md`
- **Chain:** AG Plan.v3 → Argon 94 GO → **GB (this)** → SAG → Eric typed YES → Desk EXECUTE
- **Stance:** NO CODE / NO EXECUTE from GB. Preview `p7-gate` only until Eric YES. origin/main LOCKED. NET-609 NO-FOLD. Overnight NET-610 Option B ≤$5 (8:00 PM ET queue) is a **separate** track — unchanged by this review.

---

## BLUF

**PASS WITH EDITS — 93 / 100**

**Verdict: READY FOR SAG** (no Plan.v4). Argon’s IG-1..IG-3 are **ACCEPTED as mandatory pre-EXECUTE coding folds** — lock them into the EXECUTE packet / AG coding brief; do not rewrite the plan doc for another review round.

Plan.v3 cleanly folds GB-1..3, SAG (a–d), and Argon GAP-1..4. The three IGs close residual wiring gaps that would make Eric’s first retest fail even if C1–C5 land as written. Prefer locking IGs over HOLD.

---

## Fold verification (Plan.v3 vs prior locks)

| Prior lock | Plan.v3 home | GB disposition |
|---|---|---|
| **GB-1** — fix existing `_run_duplicate_sweep` / `_score_duplicate`; no second engine; summary already at 8350 | **C1** (drops Argon GAP-1 pre-fetch loop; unfiltered stream + Python self-exclusion; SKU ≥0.60 / SKU+invoice ≥0.90; snake_case commit reads) | **FOLDED** |
| **GB-2** — ADD 26RJ (not edit); audit all test SKUs; fill blanks only; preview backfill; Mint issue_price 124.50 | **C2** + §0(b) | **FOLDED** |
| **GB-3** — GAP-3 contrast + GAP-4 prefer Wrap | **C3** + **C4** | **FOLDED** |
| **SAG (a)** — sweep fix limited to missing-`import_session_id` + SKU/invoice scoring | §0(a) + C1 | **FOLDED** |
| **SAG (b)** — catalog fill-missing-only (replaces Argon GAP-2 “authoritative overwrite”) | §0(b) + C2 | **FOLDED** |
| **SAG (c)** — four retest proofs | §2 + §6 | **FOLDED** |
| **SAG (d)** — preview-only; live write needs Eric typed YES | §0(d) + §5 | **FOLDED** |
| **Argon GAP-1** (dupe counter / sweep) | Reconciled via GB-1 → C1 (not a second engine) | **FOLDED** |
| **Argon GAP-2** (Theme/Subject + Strike + 26RJ catalog) | C2 + normalize `Theme/Subject`/`Strike Type` at 7607-7638 | **FOLDED** (overwrite → fill-missing) |
| **Argon GAP-3** (white-on-cream `_OwnerPhotoHero`) | C3 | **FOLDED** |
| **Argon GAP-4** (20-coin strip clips) | C4 Wrap | **FOLDED** |

Inherited Plan.v2 I-01..I-16 / PM-01..PM-07 and FT checklist remain in force (§4). Line-range correction for `normalize_and_validate_receipt` (7607-7638) accepted.

---

## Agree / amend Argon 94 + IG disposition

**Argon 94/100 GO — CONCUR** (GB scores **93** solely to keep IG-1..3 visibly mandatory until EXECUTE; same ready-for-SAG outcome).

### IG-1 (C1 — Review Hub badge key wiring) — **ACCEPT (mandatory)**
- Sweep today writes `duplicate_flag` / `duplicate_score` only (`main.py:7015, 7028`).
- Review Hub amber path expects `possible_duplicate` (+ readable reason).
- Without dual-write + `duplicate_reason`, FT P0 **I-08 / PM-02** can fail even when the counter increments.
- Also **ACCEPT** skip `status == "deleted"` in sweep candidates (false-positive guard).
- **No Plan.v4.** AG must apply on C1 during coding.

### IG-2 (C2 — `enrich_us_mint_item` field copy + fill-missing guards) — **ACCEPT (mandatory)**
- Catalog match today does **not** copy `is_set` / `set_id` / `item_type` / `image_url_*` / `issue_price` onto `item`.
- `"Retailer Item No."` alone is popped at `main.py:8127` — must also fill `item_number` / `retailer_item_num` when blank (else C1 SKU signal dies and enrichment looks blank).
- Wrap `Strike Type` / `Condition` / `Metal Content` (323-325) in fill-missing-only — honors SAG (b).
- **ACCEPT IG-2.4 nuance:** treat LLM `"Uncirculated Coin Set"` as a generic placeholder (or alias to `"Uncirculated Sets"`) so theme/program stamps consistently — first-try risk on PM-05.
- **No Plan.v4.** Without this, SAG proof #2 (set enrichment) fails.

### IG-3 (C5 — do NOT pop `Program/Series` or `Theme/Subject`) — **ACCEPT (mandatory)**
- C5’s “no slash keys” wording is too broad as written; Flutter readers (`my_collection_screen.dart` `_F.*`, `review_hub_screen.dart`, `CoinModel`) **require** `'Program/Series'` and `'Theme/Subject'`.
- Keep `main.py:8125-8128` pop limited to the **4** legacy retailer/fee keys **after** snake_case copies.
- Add `CoinModel.fromMap` snake_case fallbacks for `retailer_item_num` / `item_number` and `retailer_invoice_num` / `invoice_number`.
- **No Plan.v4.** Misreading C5 as “pop all slash keys” would blank Series/Theme app-wide — P0 catastrophe.

---

## NEW GB-mandatory items

**None beyond IG-1..IG-3.** No GB-4. Prefer locking Argon’s pinpoint IGs over inventing a new plan round.

Carry-forward (already in Plan.v3 / FT checklist — restate for EXECUTE packet):
1. FT FAIL-the-build (§3): second-invoice 26RJ → Duplicates Flagged ≥1 **and** Review Hub flag; 26RJ image/Theme/value/20-coin strip; Footlocker readable on cream; dupe also for roll + single coin.
2. SAG four proofs (§6) including Firestore dump of sweep inputs + counter.
3. Founder loop: **PREVIEW → FT FIXED/FAIL on checklist → only then Eric retest** (`FOUNDER_REVIEW_LOOP.md`). Do not skip FT.
4. Live/main / cherry-pick only on Eric typed YES.

---

## Scorecard (GB)

| Category | Weight | Plan.v2 (GB) | Plan.v3 (GB) | Notes |
|---|:---:|:---:|:---:|---|
| Fold of GB-1..3 + SAG a–d | 30 | 18 | **30** | All explicit in §0 + C1–C5 |
| Root-cause / first-try readiness | 30 | 22 | **27** | Solid; IG-1..3 mandatory for badge + enrich + slash-key safety |
| Safety / gates / verification | 25 | 22 | **24** | Preview lock, 4 proofs, FT FAIL gates, day/night NET-610 called out |
| Scope discipline (no Plan.v4 churn) | 15 | 10 | **12** | READY FOR SAG with IGs locked; −3 until IGs appear in EXECUTE brief |
| **TOTAL** | **100** | **82** | **93** | **PASS WITH EDITS → READY FOR SAG** |

---

## Explicit locks (unchanged)

- **NO EXECUTE** until SAG Round-3 feedback + **Eric typed YES**.
- **NO CODE** from GB this turn.
- Night **NET-610 Option B CG ≤ $5** (Desk 8:00 PM ET wake / NET-621/622 overnight queue) — **unchanged**; zero daytime CG; does not collide with Mint Plan.v3.
- Preview `p7-gate` → FT checklist → Eric retest → live only on YES.
- origin/main LOCKED; NET-609 NO-FOLD.

---

## Next in locked chain

`Argon 94 GO (DONE) → GB 93 PASS WITH EDITS / READY FOR SAG (THIS) → Stand Alone Grok Round-3 paste → Eric typed YES → CoS/Desk EXECUTE (with IG-1..IG-3 in coding brief)`

SAG paste should ask: confirm Plan.v3 + IG-1..IG-3 as mandatory coding guardrails; score; GO / CONDITIONAL GO / HOLD.
