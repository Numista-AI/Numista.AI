# ARGON REVIEW — ERIC_BMINUS_FAILFIX_PLAN_v1 (NET-629 / NET-630)
**DTG:** 27 Oct 2026 ~5:45 PM ET  
**Reviewer:** Argon (read-only; code truth over plan prose)  
**Plan:** `BETA TEST\Grok Bot\8 OCT 26\BATONS\ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md`  
**Baseline SHA:** `68b1ef657af5a7d76b0f099ad821bc9dd4997911` (origin/dev; docs commit filing this plan — code inspected in that tree)  
**Inputs:** FT NET-627 FAIL (`751a4305` preview); SAG 88 CONDITIONAL GO (NET-628 / `SAG_FEEDBACK_NET627_FAILFIX_2026-10-27.md`)  
**Live/main:** LOCKED. NO CODE. NO EXECUTE.

---

## BLUF
**Score: 71 / 100 — CONDITIONAL GO**

Plan correctly scopes the two FT P0s and gets most of I-07 right against real Flutter/FastAPI paths (unlike the earlier hallucinated Live-Mint Plan.v1). **Do not EXECUTE the fee section as written:** it only removes `pack_expanded` zeroing at `main.py:7718-7719` and misses the earlier blanket `allocated_fee = 0.0` at **`main.py:7589-7590`** that fires on any invoice containing 26SQRP. On FT’s 26SQRP-only invoice (USM24086141) that alone keeps Hub Fee at $0.00.

Fold P0 Must-Fix into Plan.v1.1 **or** lock them into the EXECUTE brief before any preview build. Preview only after full cycle + Eric YES.

| # | Claimed root cause | Verdict |
|---|---|---|
| I-07 | keep_set_as_is skips enrich; commit misses PascalCase `AI Estimated Value`; dual-write images; async enrich | **PARTIAL** (keep_set + PascalCase **CONFIRMED**; catalog URLs exist; async underspecified; FT failure path was Commit) |
| I-04b | `pack_expanded` zeros allocated fees | **PARTIAL / incomplete** (`:7718-7719` **CONFIRMED**; `:7589-7590` **missed** — proposed patch insufficient) |

---

## 1. Scorecard vs SAG 88 locks

| SAG 88 lock | In Plan.v1? | Argon note |
|---|---|---|
| Commit re-enrich + issue_price baseline | Yes (§A.2) | Matches gap: commit already re-enriches but omits `AI Estimated Value` |
| Async enrich kick | Claimed (§A.4) | **Vibes** — no signature change, no worker name/file |
| Sets/rolls catalog images first (not Greysheet wait) | Yes (RCA + §A.2/A.3) | Catalog has 26RJ URLs — good |
| 26RJ catalog URLs exist + copy | Implied | **URLs exist** at `us_mint_catalog_service.py:200-202`; fill-missing `:439-441`. Plan should state “confirmed present” and add proof step |
| 26SQRP Fee $9.95 without breaking 26RJ Fee $9.95 | Attempted (§A.1) | **Incomplete** — misses `:7589-7590`; need explicit 26RJ non-regress gate |
| No regress IG-1 dup / contrast / wrap | Listed in §3 | Soft OK — no edits proposed to those paths |

---

## 2. I-07 — Images & baseline valuation (verbatim)

### 2.1 keep_set_as_is skips enrich — **CONFIRMED**
`main.py:3740-3777` copies queue doc → `coins` with **no** `enrich_us_mint_item`, **no** issue_price baseline, **no** image dual-write:

```
3762: set_data = set_snap.to_dict()
3766: committed = {**set_data}
3774: batch.set(coins_ref.document(set_doc_id), committed)
```

Plan §A.3 correctly targets this.

**Wiring note:** FT NET-627 committed via **Commit** (`I-06 PASS: Committed 26RJ only`), i.e. `/api/review/commit`, not Keep-as-Set. keep_set fix is still mandatory (SAG lock / second path) but is **not** the FT-observed failure path.

### 2.2 commit_reviews valuation keys — **CONFIRMED miss of PascalCase**
`main.py:3622-3638`:

```
3624-3625: enrich_us_mint_item(data)
3628: if not data.get('ai_est_value') and not data.get('estValue'):
3629:     cat_p = data.get('issue_price') or ... Cost ...
3635:     data['ai_est_value'] = clean_cat_p
3636:     data['estValue'] = f"${clean_cat_p:.2f}"
3637-3638: valuation_source + enrichment_status = "enriched"
```

**Missing:** `data['AI Estimated Value']` and `data['ai_estimated_value']`.

UI (`my_collection_screen.dart`):

```
71:   static const aiValue = 'AI Estimated Value';
3020-3022: valueText = finalVal > 0 ? fmt.format(finalVal)
           : (m[_F.aiValue]?.toString() ?? '—');
3169: if (valueText == '—' || m['enrichment_status'] == 'pending')
      → 'Valuation Pending'
```

`CoinModel:206` dual-reads `ai_estimated_value ?? AI Estimated Value` — grid card path does **not**; it uses `_F.aiValue` only. Plan §A.2 + §B.1 correctly close this.

### 2.3 Images — **PARTIAL**
- Catalog **has** usable URLs for 26RJ (`us_mint_catalog_service.py:200-202` GCS https).
- `enrich_us_mint_item` fill-missing copies `image_url_obverse` / `image_url_reverse` (`:439-441`).
- Collection card already reads `data[_F.imageObverse]` (`:6319`) — same key enrich writes.
- FT: Theme+Condition stamped ⇒ catalog match ran; **images not filled** ⇒ not “missing catalog URLs.” Likely pre-filled junk key blocking fill-missing, wrong commit field persistence, or inspector path — plan’s dual-write to `primary_image_url`/`photo_urls` + UI dual-read (`:6319` today does **not** read `primary_image_url`) is helpful belt-and-suspenders but **does not by itself explain** FT if `image_url_obverse` was empty after enrich.
- **P0 IG:** On Commit of 26RJ, assert vault doc contains non-empty `image_url_obverse` matching catalog; if enrich matched Theme but skipped images, dump pre-enrich field values.

### 2.4 Async kick — **PARTIAL / underspecified**
Plan §A.4 names `_async_post_commit_enrichment` but:
- `commit_reviews` signature today: `async def commit_reviews(request: CommitReviewsRequest, _user: dict = Depends(get_current_user))` (`:3512`) — **no** `BackgroundTasks`.
- No existing `_async_post_commit_enrichment` symbol in `main.py`.
- SAG requires kick on commit with sets/rolls **not waiting** on Greysheet. Plan must specify: add `background_tasks: BackgroundTasks`, enqueue after successful batch, worker skips Greysheet overwrite of catalog baseline for sets/rolls.

---

## 3. I-04b — 26SQRP Fee $0 — **PARTIAL (proposed patch insufficient)**

### 3.1 pack_expanded zero — **CONFIRMED**
After enrich sets `pack_expanded` for pack_quantity>1 (26SQRP has `pack_quantity: 25`):

```
7717: # NET-565: Only pack/roll expansions waive the fee...
7718: doc["allocated_fees"] = 0.0 if doc.get("pack_expanded") else allocated_fee
7719: doc["shipping_fee"] = 0.0 if doc.get("pack_expanded") else allocated_fee
```

Hub reads (`review_hub_screen.dart:2291`):  
`allocated_fees ?? Allocated Fees ?? shipping_fee ?? Fee ?? fee` → shows `$0.00`.

26RJ is not pack_expanded → keeps fee → matches FT (26RJ Fee $9.95 PASS).

### 3.2 Earlier blanket zero — **MISSED BY PLAN (P0)**
```
7589: if is_us_mint_order and any(... == "26SQRP" ... for it in items):
7590:     allocated_fee = 0.0
```

FT invoices: **USM23493262 = 26RJ**, **USM24086141 = 26SQRP** (separate). On the 26SQRP-only import, `:7589-7590` sets `allocated_fee = 0.0` **before** `:7718`. Removing only the pack_expanded ternary still writes `allocated_fees = 0.0`.

**Plan §A.1 proposed diff is therefore incomplete and would fail FT I-04b again.**

### 3.3 Regression risk if naïvely always `allocated_fee`
Always assigning `allocated_fee` on every `pack_expanded` doc may re-apply S&H onto **split children** later. EXECUTE must: keep S&H on **parent roll lot** hub rows; waive only when expanding to individual child coins (or equivalent clear predicate). Do not break 26RJ `$9.95`.

---

## 4. Must-Fix table

### P0 (mandatory IGs before / in EXECUTE)
| ID | Gap | Required action |
|---|---|---|
| P0-1 | Fee root cause incomplete | Also fix/narrow `main.py:7589-7590`; do not ship §A.1 alone |
| P0-2 | Fee split vs lot | Explicit rule: parent roll lot keeps S&H; children waive; 26RJ Fee unchanged |
| P0-3 | Async enrich vibes | `BackgroundTasks` on `commit_reviews` + named worker; catalog-first for sets/rolls |
| P0-4 | I-07 Commit path | Stamp `AI Estimated Value` + `ai_estimated_value` on `/api/review/commit` (FT path); mirror `keep_set_as_is` |
| P0-5 | 26RJ image copy proof | Confirm vault doc gets catalog URLs on Commit; debug fill-missing skip if Theme filled but images empty |

### P1
| ID | Item |
|---|---|
| P1-1 | Frontend dual-read valuation (`:3020-3022`) and images (`primary_image_url` / `photo_urls`) |
| P1-2 | EXECUTE no-touch list: IG-1 dup amber, Theme/Condition fill-missing-only, cream contrast, 20-coin wrap |
| P1-3 | pytest + flutter gates in §4; Firestore dump of committed 26RJ + 26SQRP hub row in FT pack |

---

## 5. Overall verdict
**71 / 100 — CONDITIONAL GO**

Not HOLD for full rewrite: I-07 diagnosis is largely real-code-accurate and SAG locks are mostly named. Not GO: fee patch as written fails the FT case; async kick not executable as specified.

Next: AG folds P0-1…P0-5 into Plan.v1.1 **or** EXECUTE brief locks → GB CoS → SAG → Eric typed YES → preview p7-gate only. **Live/main LOCKED.**

## Hygiene
Temp worktree `%TEMP%\cr_wt_n629` at 68b1ef65; removed after. No git writes, deploys, live POSTs, Eric/AJ executes. No messages sent.

## Deliverables
- Radio: `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\NET-630_ARGON-to-GROKCOS-AGCOS_ERIC-BMINUS-PLAN-V1-REVIEW_OVER.md`
- This file + mirror under `BETA TEST\Grok Bot\27 OCT 26\`