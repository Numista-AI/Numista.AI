# GB CoS Review — Eric B− FAIL-FIX Plan.v1 (NET-629)

- **Reviewer:** Grok Bot Chief of Staff
- **DTG:** 2026-10-27 ~5:36 PM ET
- **Inputs:** ERIC_BMINUS_FAILFIX_PLAN_v1 + FT_RESULT NET-627 FAIL + SAG 88 CONDITIONAL GO locks
- **Chain:** AG Plan.v1 → **Argon (in flight)** → **GB (this)** → SAG → Eric YES → EXECUTE preview only

---

## BLUF

**91 / 100 — PASS WITH EDITS / READY FOR SAG** once Argon concurs (or after folding Argon IGs).

Two P0s correctly scoped. RCA is credible and grounded in the trigger model. Three mandatory coding folds (FF-1..FF-3) must land in the EXECUTE brief — not optional polish. No Plan.v2 unless Argon finds a P0 the IGs don’t cover.

**NO EXECUTE / NO founder retest / live/main LOCKED** until Argon → GB (done pending Argon) → SAG → Eric typed YES → preview → FT PASS.

---

## What Plan.v1 got right

1. **I-07 RCA:** `keep_set_as_is` omitting `enrich_us_mint_item` + commit stamping snake_case vals but missing PascalCase `AI Estimated Value` (UI reads `_F.aiValue`) explains Theme/Condition stamped while card stayed Valuation Pending / Image unavailable. Dual-path fix (commit + keep_set_as_is) matches FT ambiguity on which button was used.
2. **Sets/rolls vs Greysheet:** First-line = catalog `issue_price` ($124.50) + Mint product images; do not wait on Greysheet — matches SAG lock.
3. **I-04b RCA:** `pack_expanded` → force `allocated_fees`/`shipping_fee` = 0.0 at main.py ~7718 is a precise, testable root cause; explains 26RJ Fee PASS vs 26SQRP Fee FAIL on same build.
4. **Frontend dual-read** for value + image keys is correct belt-and-suspenders with backend dual-write.
5. **Scope + regression list** honors SAG: no widen; keep dup amber, 26RJ Fee, contrast, wrap green.

---

## Mandatory coding folds (FF-1..FF-3) — lock into EXECUTE brief

### FF-1 — Catalog image URLs must exist before copy (SAG image lock)
Plan assumes `enrich_us_mint_item` already has usable `image_url_obverse` / `image_url_reverse` for `26RJ`. Before coding:
- Prove the `26RJ` row in `US_MINT_PRODUCT_CATALOG` contains non-empty official image URLs (or complete the catalog entry in this FAIL-FIX).
- If URLs are blank, dual-write of empty strings still yields “Image unavailable” — that is a catalog gap, not a commit wiring win.
- Gate: Firestore dump of committed 26RJ must show non-empty image fields FT can screenshot.

### FF-2 — Fee zeroing nuance (do not multiply S&H on split children)
Plan’s blanket “always set `allocated_fees = allocated_fee`” fixes the Hub roll row but may re-break the original intent (don’t multiply shipping across pack-expanded **children** after a split).
- **Required behavior:** Parent / sole Hub roll-lot row (the qty25 package FT sees) **carries** invoice S&H ($9.95). Child lines created by a later pack expand **must not each** inherit a full $9.95 (zero or allocate once).
- Prefer: keep fee on the Hub-visible pack/roll parent; only zero (or share) when writing expanded child docs. Document the exact predicate in the coding brief.
- Gate: 26SQRP Hub Fee $9.95 AND 26RJ Fee $9.95 still PASS; if a split path exists in FT scope, children don’t each show $9.95.

### FF-3 — Baseline is fill-missing-only; don’t silent-swallow enrich
- Stamp issue_price / cost baseline **only when** est / AI Estimated Value / cpg is missing or zero — never overwrite a non-blank collector or Greysheet value (fill-missing-only).
- Replace bare `except: pass` on `enrich_us_mint_item` with logged warning (same spirit as existing backend).
- Async worker: for sets/rolls, verify baseline intact and **skip** Greysheet overwrite; for single coins, Greysheet deepen OK. Stub is fine in plan; EXECUTE must name the real function or add it.

---

## Score rationale

+ Strong dual-path commit coverage and fee RCA.  
− Catalog image existence not proven in plan (FF-1).  
− Fee fix oversimplified vs child-expand case (FF-2).  
− Silent except + baseline overwrite risk (FF-3).

Deductions are EXECUTE-brief folds, not a rewrite to Plan.v2.

---

## Retest proofs (unchanged from SAG; must be in FT package)

- (a) Commit new 26RJ → image present + non-zero val (baseline OK); no Pending/$0/Image unavailable  
- (b) 26SQRP Hub Fee = $9.95  
- (c) Prior PASS green: dup amber, 26RJ Fee $9.95, contrast, wrap  
- Firestore dumps: committed 26RJ vault doc + 26SQRP Hub row  

---

## Decision

| Item | Verdict |
|---|---|
| Plan.v1 quality | **91 PASS WITH EDITS** |
| Ready for SAG? | **YES** after Argon score (fold Argon IGs + FF-1..3) |
| Plan.v2 required? | **NO** unless Argon finds uncovered P0 |
| EXECUTE now? | **NO** — await Argon + SAG + Eric typed YES |
| Live/main | **LOCKED** — preview `p7-gate` only |

---

## Next

1. Await Argon review on Plan.v1.  
2. Fold Argon IGs + FF-1..FF-3 into SAG paste / EXECUTE brief.  
3. SAG score → Eric YES → AG codes preview only → FT → founder.
